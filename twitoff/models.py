# set up database table

# when we pipenv install, it's flask-sqlalchemy, but when
#   we import it's _
from flask_sqlalchemy import SQLAlchemy

# create a database object from the SQLAlchemy class
DB = SQLAlchemy()

# We need 2 diff tables, one for users one for tweets, so we
#   need 2 diff classes
class User(DB.Model):
    # setting up the schema

    # id column
    id = DB.Column(DB.BigInteger, primary_key=True)

    # username column
    username = DB.Column(DB.String, nullable=False)

    # there is an imaginary tweets list living in this User class
    #   due to the backref line of code we have below

    # repr method, so if I print the object, I can see the value
    def __repr__(self):
        return f"User: {self.username}"

class Tweet(DB.Model):
    # id column
    id = DB.Column(DB.BigInteger, primary_key=True)
    
    # text column
    text = DB.Column(DB.Unicode(300)) # allows emojis
    
    # user_id column (foreign /secondary key)
    #   the 'user.id' refers to above code, the user class id column
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    
    # user column creates a 2-way link btw a user object and a tweet object
    # backref is as if we had added a tweets list to the user class
    # to link the two classes together
    # now I can find the user from a tweet or vice versa
    # lazy parameter --> lazy execution, something not executed until
    #   it's necessary. don't look up anyone's tweet until someone tries
    #   to access it
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return f"Tweet: {self.text}"