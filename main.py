'''
Created on 

Course work: 
    Flask-basic

@author: Elakia

Source:

'''
from datetime import datetime
from flask import Flask, render_template, flash, url_for, session, redirect , send_file,Response
import os
import sys
from flask import request
from random import randint
from werkzeug.utils import secure_filename
import logging
import boto3
from botocore.exceptions import ClientError
# from flask.ext.session import Session
import datetime
import shutil
from dotenv import load_dotenv
from boto3 import client

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'log'])


BUCKET         = os.environ.get('BUCKET')
ACCESS_KEY     = os.environ.get('ACCESS_KEY')
SECRET_KEY     = os.environ.get('SECRET_KEY')
DEFAULT_REGION = os.environ.get('DEFAULT_REGION')
IP_ADDRESS     = os.environ.get('IP_ADDRESS')


@app.route('/test', methods=['GET', 'POST'])
def test():
    return 'hello world'


@app.route('/', methods=['GET', 'POST'])
def home():
    
    return render_template('index.html')
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    
    # check if the post request has the file part
    if 'file' not in request.files:        
        result = {
            'result' : 0,    
        }
        return render_template('result.html', result=result)
    
    file = request.files['file']
    print("file")

    if file.filename == '':        
        result = {
            'result' : 0,    
        }

        return render_template('result.html', result=result)
    
    if file and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(filepath)

        print('filepath : ', filepath)
        
        result = {
            'image_location' : filepath
        }

        now=datetime.datetime.now()
        nowtime=str(datetime.datetime.now())
        nowtime=''.join(filter(str.isalnum, nowtime))
        object_name = "featurepreneur/"+str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"/screen_shot_"+nowtime+".png"
        
        

        # Upload the file
        s3_client = boto3.client('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=DEFAULT_REGION)
        response = s3_client.upload_file(filepath, BUCKET, object_name)
        link = 'https://tact-clipboard.s3.amazonaws.com/' + object_name
        
        last_file = get_filename_from_path(object_name)
        
        redirect_url =IP_ADDRESS+"/download_url/"+ last_file
        os.remove(filepath)
        return render_template('result.html',  result = result, filepath = filepath ,link = redirect_url,object_name = object_name)
    
    return render_template('result.html')


@app.route('/download', methods=['POST'])
def download():
    print("hello")
    now=datetime.datetime.now()

    count=0
    s3_resource = boto3.resource('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=DEFAULT_REGION)
    my_bucket = s3_resource.Bucket(BUCKET)
    date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    os.makedirs(date, exist_ok=True)

    objects = my_bucket.objects.filter(Prefix='featurepreneur/'+date+"/")
    for obj in objects:
        path, filename = os.path.split(obj.key)
        output = f"{ date }/{filename}"
        my_bucket.download_file(obj.key, output)
    
    return "abc"

@app.route('/delete', methods=['POST'])
def delete():
    s3_resource = boto3.resource('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=DEFAULT_REGION)
    my_bucket = s3_resource.Bucket('tact-clipboard')
    now=datetime.datetime.now()
    date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
    my_bucket.objects.filter(Prefix="featurepreneur/"+date+"/").delete()
    return "abcd"

def get_filename_from_path(filepath):

    last_file = filepath.rsplit(os.path.sep, 1)[1]
    return last_file


def get_client():
    return client('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=DEFAULT_REGION)



@app.route('/download_url/<object_name>', methods=['GET'])
def download_file(object_name):
    now=datetime.datetime.now()
    filepath="featurepreneur/"+str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"/"+object_name
    s3 = get_client()
    file = s3.get_object(Bucket=BUCKET, Key=filepath)

    return Response(
        file['Body'].read(),
        mimetype='image/png',
        headers={"Content-Disposition": "attachment;filename=image.png"})


if __name__== "__main__":
    
    app.run(
        host    = "0.0.0.0", 
        debug   = True, 
        port    = 3848
    )