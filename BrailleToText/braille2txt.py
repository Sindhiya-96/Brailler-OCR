import printer, alphaToBraille, brailleToAlpha


from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask import Flask, json, request, jsonify
import os


app = Flask(__name__)
CORS(app)

app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'B:/project/Braille_conv/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['doc','docx'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        
    
def open_braille(filename):
    file1 = open(filename,encoding="utf8")
    content1 = file1.read()
    opt1= brailleToAlpha.translate(content1)
    print(brailleToAlpha.translate(content1))
    brailleFileName ="brailleop.doc"
    with open(brailleFileName,"w",encoding="utf-8") as op:
        op.write(opt1)
        op.close()
        
        
def brailletoTextConverter(path): 
    pdf_path=r""+path     
    open_braille(pdf_path)

 
@app.route('/uploadBrailleToText', methods=['POST'])
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
        brailletoTextConverter(filePath)
        
    else:
            errors[file.filename] = 'File type is not allowed'
 
    if success:
        return jsonify(
        message='File successfully converted to braille',
        path='B:\\project\\Braille_conv\\brailleop.doc',
        filename='brailleop.doc'
    )
    else:
        response = jsonify(errors)
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin','*')
        return response 
 
if __name__  == '__main__':
    app.run(debug=True,port=8085)