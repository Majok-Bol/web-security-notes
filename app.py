from flask import Flask,render_template,url_for,request,flash
from dotenv import load_dotenv
from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField,EmailField,PasswordField,SubmitField
from wtforms.validators import Email,EqualTo
from flask_sqlachemy import SQLAlchemy
import os
load_dotenv()
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
db=SQLAlchemy(app)
# print("DB: ",dbs)
@app.route("/")
def hello():
    return 'Hello world'
if __name__=="__main__":
    app.run(debug=True)