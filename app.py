from flask import Flask,render_template,url_for,request,flash,redirect,make_response
from dotenv import load_dotenv
from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField,EmailField,PasswordField,SubmitField
from wtforms.validators import Email,EqualTo,InputRequired,Length
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import(
    create_access_token,
    current_user,
    get_jwt_identity,
    JWTManager,
    set_access_cookies,
    jwt_required,
    unset_jwt_cookies
)
import os
import re
load_dotenv()
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
#secret key for csrf protection
app.config['SECRET_KEY']=os.getenv("CSRF_SECRET_KEY")
#ie like a server private stamp
#only server knows it
#sign JWTs
app.config['JWT_SECRET_KEY']=os.getenv("JWT_SECRET_KEY")
#where to look for token
#stored in the cookies
app.config['JWT_TOKEN_LOCATION']=["cookies"]
#name of the cookie that will store access token
app.config['JWT_ACCESS_COOKIE_NAME']="access_token"
#sent cookies over HTTPS-production ,True
app.config['JWT_COOKIE_SECURE']=False #true in production
#csrf protection for JWT
app.config['JWT_COOKIE_CSRF_PROTECT']=False #true in production
#no JS access
app.config['JWT_COOKIE_HTTPONLY']=False #true in production
#jwt expiration
# app.config['JWT_ACCESS_TOKEN_EXPIRES']=timedelta(minutes=10)
#samesite cookie setting
app.config['JWT_COOKIE_SAMESITE']='Lax' #Strict for production
#enable 
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
#initialize app with JWT auth
jwt=JWTManager()
jwt.init_app(app)
# print("DB: ",dbs)
@app.route("/")
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
        #check if username already exists
        user_exists=User.query.filter_by(username=username).first()
        print("Username exists: ",user_exists)
        if user_exists:
            print("Username not available")
            return redirect(url_for("register"))
        #check if email already exists
        email_exists=User.query.filter_by(email=email).first()
        print("Email exists: ",email_exists)
        if email_exists:
            print("Email address not available")
            return redirect(url_for("register"))
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
            print("Invalid username or password")
            return redirect(url_for('login'))
        #create access token
        access_token=create_access_token(identity=str(user.id))
        print("Access token: ",access_token)
        #redirect to dashboard after successful login credentials
        response=make_response(redirect(url_for("dashboard")))
        #set cookies
        set_access_cookies(response,access_token)
        return response
    return render_template("login.html",form=form)
@app.route("/dashboard",methods=["POST","GET"])
@jwt_required()
def dashboard():
    user_id=get_jwt_identity()
    print("User id: ",user_id)
    user=db.session.get(User,int(user_id))
    print("User: ",user)
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html",user=user)
#customize jwt errors
#ie no token provided in the request
@jwt.unauthorized_loader
def missing_token_callback(reason):
    print("Reason: ",reason)
    return redirect(url_for("login"))
#invalid token provided
@jwt.invalid_token_loader
def invalid_token_callback(reason):
    print("Reason: ",reason)
    return redirect(url_for("login"))
#token provided but has expired
@jwt.expired_token_loader
def expired_token_callback(jwt_header,jwt_payload):
    # print("Reason: ",reason)
    print("JWT Header: ",jwt_header)
    print("JWT payload: ",jwt_payload)
    return redirect(url_for("login"))
@app.route("/logout",methods=["POST","GET"])
def logout():
    response=make_response(redirect(url_for("login")))
    #remove jwt cookies
    unset_jwt_cookies(response)
    return response
    
    # return render_template("logout.html")


@app.route('/test',methods=["POST","GET"])
def test():
    response=make_response("Hello world")
    return response
#add notes route
app.route('/create_note',methods=["POST","GET"])
def create_note():
    return render_template("create_note.html")
#update notes route
app.route('/update_note',methods=["POST","GET"])
def update_note():
    return render_template("update_note.html")
#delete note route
app.route('/delete_note',methods=["POST","GET"])
def delete_note():
    return render_template("delete_note.html")
#strong password validator
def strong_passsword(form,field):
    password=field.data
    print("Password: ",password)
    if len(password)<8:
        print("Password must be atleast 8 characters long")
    if not re.search(r"[A-Z]",password):
        print("Password must contain atleast one uppercase letter")
    if not re.search(r"[a-z]",password):
        print("Password must contain atleastone lowercase letter")
    if not re.search(r"\d",password):
        print("Password must contain atleast onedigit")
    if not re.search(r"[!@#%^&*]",password):
        print("Password must contain atleast one special character")

#register form
class RegisterForm(FlaskForm):
    username=StringField("Username",validators=[InputRequired(),Length(min=4)])
    email=EmailField("Email address",validators=[InputRequired(),Email()])
    password=PasswordField("Password",validators=[InputRequired(),strong_passsword])
    confirm_password=PasswordField("Confirm password",validators=[InputRequired(),EqualTo("password",message="Passwords must match")])
    submit=SubmitField("Register")

#login form
class LoginForm(FlaskForm):
    username=StringField("Username",validators=[InputRequired()])
    password=PasswordField("Password",validators=[InputRequired()])
    submit=SubmitField("Login")

#database models
#table for users
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False,unique=True)
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
#table for notes
# class Notes(db.Model):
#     notes_id=db.Column(db.Integer,db.Fo)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        # db.drop_all()
    app.run(debug=True)