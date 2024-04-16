# importing a specific class Flask from a package flask
# render_template is a function, and inside we put the .html file
from flask import Flask, render_template, request

# use . in the flask app file to indicate "look inside the current folder"
from .models import DB, User, Tweet

from .twitter import add_or_update_user

from .predict import predict_user

# create_app factory, to wrap everything under this function
#   so we can get into developer mode with debug mode ON
def create_app():

    # Instantiate our own Flask application
    #   one instance of flask app to create a new flask app
    # or use APP to reflect it's a global variable
    app = Flask(__name__)

    # Database config
    # Tell our app where our database file is gonna live
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    # Allow change to database without error messages popping up
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Register our database with the app
    DB.init_app(app)

    # Decorator
    # tell our app to listen to our browser request for the 
    #   base / route, meaning for the homepage, listen for 
    #   someone accessing our hp
    #   e.g. www.google.com/  <-- the base aka homepage
    @app.route('/') 
    def root():

        users = User.query.all()

        # return f"Welcome to my app called: {my_var}"
        return render_template('base.html', title='Home', users=users) # name on tab
    # what these 3 lines do is when someone visits the homepage
    #   the root() function will be invoked and the user will 
    #   see "Hello, World!" being printed out.

    # # Build another page after the root aka homepage
    # @app.route('/bananas')
    # def bananas():
    #     # return "This is the bananas page"
    #     return render_template('base.html', title='Bananas')
    
    # Create a db.sqlite3 file in the same folder so we can work on it
    @app.route('/reset')
    def reset():
        # drop all database tables
        DB.drop_all()
        # recreate all database tables according to the
        #   indicated schema in models.py
        DB.create_all()
        return render_template('base.html', title='Reset Database')
    
    # Create and insert data into database
    # @app.route('/populate') # add user for the very first time
    # def populate():

    #     add_or_update_user('Austen')
    #     add_or_update_user('NASA')
    #     add_or_update_user('RyanAllred')

    # # #     # We don't need fake users and tweets anymore
    # # #     # # Create 2 users in database
    # # #     # ryan = User(id=1, username='Ryan')
    # # #     # DB.session.add(ryan)
    # # #     # julian = User(id=2, username='Julian')
    # # #     # DB.session.add(julian)

    # # #     # # Create two tweets
    # # #     # tweet1 = Tweet(id=1, text="ryan's tweet text", user=ryan)
    # # #     # DB.session.add(tweet1)
    # # #     # tweet2 = Tweet(id=2, text="julian's tweet text", user=julian)
    # # #     # DB.session.add(tweet2)

    # # #     # Save the changes we just made to the database
    # # #     # commit the database changes
    # # #     # DB.session.commit()

    #     return render_template('base.html', title='Populate Database')
    
    @app.route('/update') # OK with existing users
    def update():
        # Get list of usernames of all users
        users = User.query.all()
        # usernames = []
        # for user in users:
        #     usernames.append(user.username)
        # Instead of above 3 lines, we use list comprehension
        # [user.username for user in users]
        # And we take this list comp and put it in the for loop below

        # Get all the users, then their usernames, then update
        # for username in usernames, where username = [see below]
        for username in [user.username for user in users]:
            add_or_update_user(username)

        return render_template('base.html', title='Users Updated')
    
    # Instead of the /populate route, now we rely on users to supply
    #   us data and here it is:
    # We want the user route to listen to both POST and GET HTTP requests
    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET']) # username based on user's input
    def user(username=None, message=''): # the default will be overriden if we have a username running a GET request

        username = username or request.values['user_name'] # reading data from POST request
        
        # If the try block works, we will skip the exception
        # If something fails, we will get an error message from the Exception
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User "{username}" has been successfully added!'

            # Whether it's POST or GET method, we're grabbing tweets
            tweets = User.query.filter(User.username==username).one().tweets
            # .one() is to grab it as an object instead of a list

        except Exception as e: # e is error message text
            message = f'Error adding {username}: {e}'
            tweets = []
            # if it breaks, it's expecting tweets=tweets, so we still put
            #   something in tweets, an empty list [], that way the
            #   variable tweets is never undefined

        return render_template('user.html', title=username, tweets=tweets, message=message)
        # If we added a user, the message will be 'User so-and-so has been successfully added!'
        # If we just do GET request, the message will just be the default blank

    # The whole purpose of our app - to compare hypothetical text to existing db
    #   and determine who likely has tweeted the text
    # Fill in the route for the left hand side of the homepage
    #   the dropdown menu 1, dropdown menu 2 and Tweet text to predict
    #   Dropdown menu 1 corresponds to the request.values['user0']
    #   Dropdown menu 2 corresponds to the request.values['user1']
    @app.route('/compare', methods=['POST'])
    def compare():

        # write "sorted" to make sure user0 comes first
        user0, user1 = sorted([request.values['user0'], request.values['user1']])
        hypo_tweet_text = request.values['tweet_text']

        if user0 == user1:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)

            # Jump to this if statement if the prediction = 1 (not zero) aka user1
            if prediction: # meaning if prediction exists (as 1, not 0)
                message = f'"{hypo_tweet_text}" is more likely to be said by {user1} than by {user0}.'
            else:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user0} than by {user1}.'
    
        return render_template('prediction.html', title='Prediction', message=message)
        # swap out that block content section in base.html with that in prediction.html

    return app

# populate route didn't work in module 2