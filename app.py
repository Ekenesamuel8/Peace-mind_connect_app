import os
from flask import Flask, render_template, url_for, redirect, flash, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import input_required, length, ValidationError # data_required
from flask_bcrypt import Bcrypt
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


"""make app instance
db: database instance
app.config:connect the app to the database"""
# Initialize Flask app
app = Flask(__name__)
bcrypt = Bcrypt(app)# to ensure the paasword that is stored in or database is hashed 
# Configure the SQLite database URL and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Initialize SQLAlchemy for database operations
db = SQLAlchemy(app)

# Initialize Flask-Login for user session management

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login" # Set the login view when user is not authenticated

# User loader callback for Flask-Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """table for the database
        id: identity column for the user
        username: the username (db.string: not more than 22 character)
            (nullable:means the username feild must not b empty)
            (unique: means they cannot be duplicate username)
        pasword: same as username
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(22), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Session(db.Model, UserMixin):
    """table for the database
        id: identity column for the user
        username: the username (db.string: not more than 22 character)
            (nullable:means the username feild must not b empty)
            (unique: means they cannot be duplicate username)
        pasword: same as username
    """
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, nullable=False)
    session = db.Column(db.String(50), nullable=False, default=uuid.uuid4)
    created = db.Column(db.DateTime, nullable=True)
    expiry = db.Column(db.DateTime, nullable=True)


class Membershipform(FlaskForm):
    """registration form
        username: 
    """

    username = StringField(validators=[input_required(), length(
        min=4, max=22)], render_kw={"placeholder": "username"})
    
    password = PasswordField(validators=[input_required(), length(
        min=4, max=22)], render_kw={"placeholder": "password"})
    
    submit = SubmitField("Register")

    def validate_username(self, username):
        """to check if user name alredy exist when registering
        """
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError("this username exist already")
        


class loginform(FlaskForm):
    """login form
        username: 
    """

    username = StringField(validators=[input_required(), length(
        min=4, max=22)], render_kw={"placeholder": "username"})
    
    password = PasswordField(validators=[input_required(), length(
        min=4, max=22)], render_kw={"placeholder": "password"})
    
    submit = SubmitField("login")

"""create a route for the app in the web browser
this means, whenever we type the 'lcalhost:5000' in the browser.
it display the content of the function(home)"""

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/consultancy')
def consultancy():
    return render_template('consultancy.html')

@app.route('/about')
@login_required
def about(): 
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/therapy')
def therapy():
    return render_template('therapy.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            sess = Session()
            sess.user = user.id
            db.session.add(sess)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('login unsuccessfull, please check the email or password')    
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Membershipform()

    if form.validate_on_submit():
        flash('Accout Created')
        """hashed_psw: this generate a hash for the real password
        db.session.add(new_user): adds the new_user info in the database table
        db.session.commit: this ensure is been added to the table
        redirect: redirect you to the login page after you register
        """
        hashed_psw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_psw)
        db.session.add(new_user)
        db.session.commit()
        flash("you have successfully registered, please login")
        return redirect(url_for('login'))
    
    #flash("registration unsuccessfull, please check the email or password")
    return render_template('register.html', form=form)
    



if __name__ == "__main__":
     """this will run the app, debug=True means 
     when there any error while running it will indicate
     where is comming from"""

     app.run(debug=True)