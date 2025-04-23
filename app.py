'''
Created on 

Course work: 
    Flask-basic

@author: Elakia

Source:

'''
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "hello world !!! branch name Update !!! "

if __name__== "__main__":
    
    app.run()
