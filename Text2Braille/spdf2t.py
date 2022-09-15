import glob, sys, fitz
import pytesseract
from PIL import Image
import printer, alphaToBraille
import urllib.request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask import Flask, json, request, jsonify
import os

textToBrailleFileList = []
app = Flask(__name__)
CORS(app)

app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'B:/project/scanned_pdf/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['pdf'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# To get better resolution
zoom_x = 2.0  # horizontal zoom
zoom_y = 2.0  # vertical zoom
mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension



def mergeTextToBrailleFiles():
    print('LIST::',textToBrailleFileList)
    print('LIST LENGTH::',len(textToBrailleFileList))
    brailleContent = ""
    for names in textToBrailleFileList:
        brailleFile = open(names,encoding="utf8")
        brailleContent += "\n" +"\n"+brailleFile.read()
    with open("scanned_Merged.doc","w",encoding="utf-8") as op:
        op.write(brailleContent)   
        
        
         
def open_text(filename,brailleCount):
    pdf_path=r""+filename
    file = open(pdf_path)
    content = file.read()
    opt1= alphaToBraille.translate(content)
    print(alphaToBraille.translate(content))
    brailleFileName ="brailleop"+str(brailleCount)+".doc"
    with open(brailleFileName,"w",encoding="utf-8") as op:
        #op.write("========================["+str(brailleCount)+"]===========================")
        op.write(opt1)
        #convertToText(brailleFileName)
        textToBrailleFileList.append(brailleFileName)
        op.close()
    
   
def scannedPdfToBrailleConverter(filePath) : 
    doc = fitz.open(filePath)  # open document
    for page in doc:  # iterate through the pages
        pix = page.get_pixmap(matrix=mat)  # render page to an image
        pix.save("image_%i.png" % page.number)  # store image as a PNG
        
        extractedInformation = pytesseract.image_to_string(Image.open("image_"+str(page.number)+".png")) # extracting text from page 

        text= extractedInformation


        file= open("input"+str(page.number)+".txt","a")
        file.write("============  [  "+str(page.number)+"   ]  ===========")
        file.write("\n")
        file.write(str(text).lower())
        file.close()
    
    i=0
    while(i <= page.number):
        print("no of pg no::",page.number)
        print('Inside looop::',i)
        fileName="input"+str(i)+".txt"
        print('Calling convert to braille::fileName::',fileName)
        print(i)
        open_text(fileName,i)
        i+=1        
    mergeTextToBrailleFiles()
    
        
@app.route('/uploadScannedText2Braille', methods=['POST'])
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
        scannedPdfToBrailleConverter(filePath)
        
    else:
            errors[file.filename] = 'File type is not allowed'
 
    if success:
        return jsonify(
        message='File successfully converted to braille',
        path='B:\\project\\scanned_pdf\\scanned_Merged.doc',
        filename='scanned_Merged.doc'
    )
    else:
        response = jsonify(errors)
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin','*')
        return response 
 
if __name__  == '__main__':
    app.run(debug=True,port=8083)