import pytesseract

import shutil

import os

import random
import urllib.request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask import Flask, json, request, jsonify

from PIL import Image
import printer, alphaToBraille
app = Flask(__name__)
CORS(app)

app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'B:/project/img2txt/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def open_text(filename):
    file = open(filename)
    content = file.read()
    opt1= alphaToBraille.translate(content)
    print(alphaToBraille.translate(content))
    brailleFileName ="brailleop.doc"
    with open(brailleFileName,"w",encoding="utf-8") as op:
        op.write(opt1)
        op.close()


def imgtoText(filePath):

    extractedInformation = pytesseract.image_to_string(Image.open(filePath))

    text= extractedInformation

    file1 = open("input.txt","w")
    file1.write(str(text).lower())
    file1.close()


    fileName="input.txt"
    open_text(fileName)

        
@app.route('/uploadImageText2Braille', methods=['POST'])
def upload_file():
    print('REQUEST::', request.files['file'])
    
    file = request.files['file']
    #args = request.args
    #name = args.get('name')
    print('FILENAME::',file.filename) 
    errors = {}
    success = False
       
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filePath=UPLOAD_FOLDER+"/"+filename
        success = True
        imgtoText(filePath)
        
    else:
            errors[file.filename] = 'File type is not allowed'
 
    if success:
        return jsonify(
        message='File successfully converted to braille',
        path='B:\\project\\img2txt\\brailleop.doc',
        filename='brailleop.doc'
    )
    else:
        response = jsonify(errors)
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin','*')
        return response 
 
if __name__  == '__main__':
    app.run(debug=True,port=8084)