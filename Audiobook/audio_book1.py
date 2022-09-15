
import pyttsx3
import pdfplumber
import PyPDF2
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask import Flask, json, request, jsonify



app = Flask(__name__)
CORS(app)

app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'B:/project/Audiobook/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['pdf'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def audio(path):
      

      pdfFileObj = open(path, 'rb')

      
      pdfReader = PyPDF2.PdfFileReader(pdfFileObj)    # creating a pdf reader object
      pages = pdfReader.numPages    #Get the number of pages

      with pdfplumber.open(path) as pdf:
      
          for i in range(0, pages): #Loop through the number of pages
            page = pdf.pages[i]
            text = page.extract_text()
            print(text)
            
            speaker = pyttsx3.init()
            voices= speaker.getProperty('voices')
            speaker.setProperty("rate", 170)
            speaker.setProperty('voice',voices[1].id) # assigning female voice 
            speaker.say(text)
            speaker.save_to_file(text, "output"+str(i)+".mp3")  #save the audio as mp3 file
            speaker.runAndWait()
            speaker.stop()



       
#audio(path="B:\project\Audiobook/the_brothers_grimm_fairy_tales.pdf")

@app.route('/uploadTextToAudio', methods=['POST'])
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
        audio(filePath)
        
    else:
            errors[file.filename] = 'File type is not allowed'
 
    if success:
        return jsonify(
        message='File successfully converted to Audio',
        path='B:\\project\\Audiobook\\output.mp3',
        filename='output.mp3'
    )
    else:
        response = jsonify(errors)
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin','*')
        return response 
 
if __name__  == '__main__':
    app.run(debug=True,port=8087)