# importing a specific class Flask from a package flask
# render_template is a function, and inside we put the .html file
from flask import Flask, render_template

# use . in the flask app file to indicate "look inside the current folder"
from .models import DB, User, Tweet

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

    my_var = "Twitoff App"

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

    # Build another page after the root aka homepage
    @app.route('/bananas')
    def bananas():
        # return "This is the bananas page"
        return render_template('base.html', title='Bananas')
    
    # Create a db.sqlite3 file in the same folder so we can work on it
    @app.route('/reset')
    def reset():
        # drop all database tables
        DB.drop_all()
        # recreate all database tables according to the
        #   indicated schema in models.py
        DB.create_all()
        return "database has been reset"
    
    # Create and insert data into database
    @app.route('/populate')
    def populate():
        # Create 2 users in database
        ryan = User(id=1, username='Ryan')
        DB.session.add(ryan)
        julian = User(id=2, username='Julian')
        DB.session.add(julian)

        # Create two tweets
        tweet1 = Tweet(id=1, text="ryan's tweet text", user=ryan)
        DB.session.add(tweet1)
        tweet2 = Tweet(id=2, text="julian's tweet text", user=julian)
        DB.session.add(tweet2)

        # Save the changes we just made to the database
        # commit the database changes
        DB.session.commit()

        return "database has been populated"
    
    return app