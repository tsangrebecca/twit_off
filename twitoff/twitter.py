from os import getenv
import not_tweepy as tweepy
from .models import DB, Tweet, User
import spacy

# Get our API keys from our .env file
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    '''Take a user name and pull that user's data and tweets from the API
    If this user already exists in our database then we will just check 
    to see if there are any new tweets from that user that we don't
    already have and we will add any new tweets to the database.'''

    # try-except-else block to test out this whole code block. all or nothing
    # if something doesn't work, it'll throw us an error message
    # but if it does, then we save the changes
    try: 
    # get the user info from twitter
        twitter_user = TWITTER.get_user(screen_name=username)

        # Check to see if user is already in database
        # Is there a user with the same ID already in the db
        # If we don't already have the user, then we'll create a new one
        # 1st statement to check if the user is already in the db, if false
        #   then check 2nd statement to create a new user name
        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id, username=username)

        # Imaginary if statement to demo the code line above
            # if (age > 20) or (height > 60):
                # get into the if block if either condition is true
                # we only check the 2nd statement if the 1st statement is false

        # Add the user to the database
        # This won't re-add a user if they've already been added
        DB.session.add(db_user)

        # Get the user's tweets
        tweets = twitter_user.timeline(count=200, 
                                    exclude_replies=True, 
                                    include_rts=False, 
                                    tweet_mode='extended',
                                    since_id=db_user.newest_tweet_id)
            # since_id prevents adding the same tweet to the db twice
        
        # Update the newest_tweet_id if there have been new tweets
        #   since the last time this user tweeted
        #   if the tweets is not empty:
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # Add all of the individual tweets to the database
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id, 
                            text=tweet.full_text[:300], 
                            vect=tweet_vector,
                            user_id=db_user.id)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

    except Exception as e:          # e is error message
        print("Error processing {username}: {e}")
        raise e     # raise means entire app is made aware of it
    
    else:
        # Save the changes to the database
        DB.session.commit()

nlp = spacy.load('my_model/')
# Now we have the same tool we used in the flask shell
# give the function some text, it returns a word embedding
def vectorize_tweet(tweet_text):
    return nlp('tweet_text').vector