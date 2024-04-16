'''Adding a machine learning model to our flask app!'''

from sklearn.linear_model import LogisticRegression
import numpy as np
from .models import User
from .twitter import vectorize_tweet

def predict_user(user0_username, user1_username, hypo_tweet_text):
    # Grab the users from the DB
    user0 = User.query.filter(User.username==user0_username).one() 
        # .one() because we don't want it in a list
    user1 = User.query.filter(User.username==user1_username).one()

    # Get the word embeddings from each other
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # Vertically stack the two 2D numpy arrays to make our X matrix
    #   Need square brackets!!!
    X_train = np.vstack([user0_vects, user1_vects])

    # Concatenate our labels of 0 or 1 for each tweet to make y train
    zeros = np.zeros(user0_vects.shape[0])
    ones = np.ones(user1_vects.shape[0])

    y_train = np.concatenate([zeros, ones])

    # Instantiate and fit a logistic regression model
    log_reg = LogisticRegression().fit(X_train, y_train)

    # Vectorize hypothetical tweet text and reshape from 1D to 2D array
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text).reshape(1,-1)
    
    # Predictions originally returned as an array, we index it
    #   so it'll return an integer of 1 or 0
    return log_reg.predict(hypo_tweet_vect)[0]

# Use flask shell to test the code