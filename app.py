from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import input_required, length, ValidationError
from flask_bcrypt import Bcrypt


"""make app instance
db: database instance
app.config:connect the app to the database"""

app = Flask(__name__)
bcrypt = Bcrypt(app)# to ensure the paasword that is stored in or database is encrypt with hash 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1258@localhost/ekenetest'
app.config['SECRET_KEY'] = 'ascretekey'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


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

class Membershipform(FlaskForm):
    """registration form
        username: 
    """

    username = StringField(validators=[input_required(), length(
        min=4, max=22)], render_kw={"placeholder": "username"})
    
    password = PasswordField(validators=[input_required(), length(
        min=4, max=22)], render_kw={"placeholder": "password"})
    
    submit = SubmitField("Register")

    def comfirm_username(self, username):
        """to check if user name alredy exist when registering
        """
        already_exist = User.query.filter_by(username=username.data).first()

        if already_exist:
            raise ValidationError(
            "this username exist already")
        


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

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
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
        """hashed_psw: this generate a hash for the real password
        db.session.add(new_user): adds the new_user info in the database table
        db.session.commit: this ensure is been added to the table
        redirect: redirect you to the login page after you register
        """
        hashed_psw = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_psw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



if __name__ == "__main__":
     """this will run the app, debug=True means 
     when there any error while running it will indicate
     where is comming from"""

     app.run(debug=True)