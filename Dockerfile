FROM python:3.12-slim
#Selects the base image for the new image
#"slim" image is a smaller debian based img with python preinstalled
#this provides Python and a minimal OS filesystem to build on


WORKDIR /app
#Sets the working directory inside the container to  /app for all subsequent instructions(COPY,RUN,CMD etc)
#if the directory doesnt exists,it will be created
#this later makes COPY and RUN use /app as their current directory and keep files organized


COPY requirements.txt .
#Copies the file requirements.txt from the build context (local project folder) into the current working directory(/app)
#Copying requirements.txt firrst is a common cache optimization
#if requirements.txt hasnt changed,Docker can reuse the layer that installed dependencies
#rather than reinstalling them


RUN pip install --no-cache-dir -r requirements.txt
#runs the  command inside the image during build to install Python packages listed in the requirements.txt
#using pip --no-cache-dir tells pip not to save package caches inside the image,reducing image size
#it produces a layer with installed dependencies that subsequent image with use


COPY . .
#Copies the rest of the project files from the build context into the container
#working directory(/app)
#placing this after installing requirements leverages Docker's layer caching
#if ony app code changes(not requirements.txt)
#the expensive pip install layer can be reused

EXPOSE 8000
#Documents that the container listens on TCP port 8000 at runtime


CMD ["gunicorn","--bind","0.0.0.0","app:app"]
#Tells Docker what commands to run when a container is started
#CMD -specifies the default command that runs when Docker starts
#"gunicorn"-executable being run
#"--bind"- tells Gunicorn listen on this IP and Port
#0.0.0.0 means acccept connections on port 8000 from any interface
#app:app
#first app-is python file name
#Gunicorn imports app
#second app
#is the Flask application object 
#ie 
#from flask import Flask
#app=Flask(__name__)
#Gunicorn sees:
#app:app
#and does
#from app import app
    
