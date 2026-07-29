from flask import Flask,render_template,url_for,request,flash,redirect
from dotenv import load_dotenv
from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField,EmailField,PasswordField,SubmitField
from wtforms.validators import Email,EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
load_dotenv()
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
#initialize app with local database ie sqlite
db=SQLAlchemy(app)
#initialize app with bcrypt for password hashing
bcrypt=Bcrypt()
bcrypt.init_app(app)
#initialize app to use CSRF protection 
csrf=CSRFProtect()
csrf.init_app(app)
#initialize app to use migrate features ie handle database schema changes
migrate=Migrate()
migrate.init_app(app,db)
# print("DB: ",dbs)
@app.route("/",methods=["POST","GET"])
def home():
    return render_template("home.html")
@app.route("/register",methods=["POST","GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        username=form.username.data
        #check if user exists
        email=form.email.data
        password=form.password.data
        hashed_password=bcrypt.generate_password_hash(password).decode("utf-8")
        #add user to the database
        user=User(username=username,email=email,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html",form=form)
@app.route("/login",methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        #check if username is not available
        user=User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password,password):
            flash("Invalid username or password","warning")
            return redirect(url_for('login'))
    return render_template("login.html",form=form)
@app.route("/dashboard",methods=["POST","GET"])
def dashboard():
    return render_template("dashboard.html")
@app.route("/logout",methods=["POST","GET"])



#register form
class RegisterForm(FlaskForm):
    username=StringField("Username")
    email=EmailField("Email address")
    password=PasswordField("Password")
    confirm_password=PasswordField("Confirm password")
    submit=SubmitField("Register")

#login form
class LoginForm(FlaskForm):
    username=StringField("Username")
    password=PasswordField("Password")
    submit=SubmitField("Login")

#database models
#table for users
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(100))
    password=db.Column(db.String(255))
#table for notes
# class Notes(db.Model):
#     notes_id=db.Column(db.Integer,db.Fo)
def logout():
    return render_template("logout.html")
if __name__=="__main__":
    with app.app_context():
        db.create_all()
        # db.drop_all()
    app.run(debug=True)