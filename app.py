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
    return "hello world !!! branch 2  "

if __name__== "__main__":
    
    app.run(
        host    = "0.0.0.0", 
        debug   = True, 
        port    = 3848
    )
