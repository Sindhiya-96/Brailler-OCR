from ast import NodeVisitor
import os
from types import NoneType
from urllib import response
import PyPDF2
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from PyPDF2 import PdfReader
from PyPDF2 import PdfFileMerger
import pdfplumber
import fitz
import io
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import printer, alphaToBraille, brailleToAlpha
from sys import argv
import camelot
from flask import Flask, request, jsonify,make_response
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
textToBrailleFileList = []
app = Flask(__name__)
CORS(app)

app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'B:/project/pdf2txt/pdfuploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['pdf'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 

def convertBrailleToText(filename):
    file1 = open(filename,encoding="utf8")
    content1 = file1.read()
    print(brailleToAlpha.translate(content1))
    # write to a file and merge


def convertTextToBraille(filename,brailleCount):
    print('inside braille converter::',brailleCount)
    file = open(filename)
    content = file.read()
    opt1= alphaToBraille.translate(content)
    brailleFileName ="brailleop"+str(brailleCount)+".doc"
    with open(brailleFileName,"w",encoding="utf-8") as op:
        op.write(opt1)
        
        #convertToText(brailleFileName)
        textToBrailleFileList.append(brailleFileName)
        op.close()

def extractImage(pageName,fileName):
    pdf_file = fitz.open(pageName) 
    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index] # get the page itself
        image_list = page.get_images()
        
        if image_list: # printing number of images found in this page
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
            
        else:
            print("[!] No images found on page", page_index)
        for image_index, img in enumerate(image_list, start=1):
            
            
            xref = img[0]   # get the XREF of the image

            base_image = pdf_file.extract_image(xref)   # extract the image bytes
            image_bytes = base_image["image"]

            image_ext = base_image["ext"]  # get the image extension

            image = Image.open(io.BytesIO(image_bytes))  

            image.save(open(f"image_{image_index}.{image_ext}", "wb"))   # save it to local disk

            extractedInformation = pytesseract.image_to_string(Image.open("image_"+str(image_index)+".jpeg")) # extracting text from page 

            text= extractedInformation

            file= open(fileName,"a")
            file.write(text)
            file.close()    

def extractText(pageObj,fileName):                     
    outputFile= pageObj.extractText()
    print('Extracted text from page ',outputFile)  
    file= open(fileName,"a")
    file.write("============================")
    file.write("\n")
    file.write(str(outputFile).lower())
    file.close()
                
def extractTable(pageName,fileName):
    tables = camelot.read_pdf(pageName)
    print("Total tables extracted:", tables.n)
    tab= tables.n
    for tab in range(tables.n):
        print("before creation",tab)
        print('TABLE',str(tables[tab].df))
        inp= open(fileName,"w")
        inp.write(str(tables[tab].df))
        inp.close()
                        
               
def mergeTextToBrailleFiles():
    print('LIST::',textToBrailleFileList)
    print('LIST LENGTH::',len(textToBrailleFileList))
    brailleContent = ""
    for names in textToBrailleFileList:
        brailleFile = open(names,encoding="utf8")
        brailleContent += "\n" +"\n"+brailleFile.read()
    with open("Merged.doc","w",encoding="utf-8") as op:
        op.write(brailleContent)
                
def identifyPageType(pageObj,pageName,fileName):
    if '/Font' in pageObj['/Resources']:   #to separate the table from the text
        with pdfplumber.open(pageName) as pdf:
            tbl = pdf.pages[0].extract_table() # reads the table alone from the file
            if type(tbl)==NoneType:
                print("TEXT")
                extractText(pageObj,fileName)
            else:
                print('TABLE::')
                extractTable(pageName,fileName)                           
    elif '/XObject'in pageObj['/Resources']: #for image separation
        print('This page::'+pageName+' IMAGE') 
        extractImage(pageName,fileName)
 
       
def textToBrailleConverter(path):        
    pdf_path=r""+path
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        number_of_pages = pdf.getNumPages()
        print("The no of pages in the pdf:",number_of_pages)


    #-------------------------------------------------------Splitting code-------------------------------------------------------------------
    input_pdf = PdfFileReader(pdf_path)
    pgCount = number_of_pages

    i=0
    while(i < pgCount):
        print('Inside looop::',i)
        fileName="input"+str(i)+".txt"
        print('pgCount looop::',pgCount)
        pageName = 'Page'+str(i)+'.pdf'
        print('PageName',pageName)
        output = PdfFileWriter()
        print('writer object::',input_pdf.getPage(i))
        output.addPage(input_pdf.getPage(i))
        with open(pageName, "wb") as output_stream:
            output.write(output_stream)
        pdfFileObj = open(pageName, 'rb') 
        
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)  # creating a pdf reader object 
        print('Before error::',pdfReader)
        print('pdfReader::',pdfReader.getPage(0))
        
        pageObj = pdfReader.getPage(0)# creating a page object 
        #print('Page Object ',pageObj)
        
        
        print('Page No ',i)  
        identifyPageType(pageObj,pageName,fileName)
        
        # closing the pdf file object 
        pdfFileObj.close() 
        print('Calling convert to braille::fileName::',fileName)
        convertTextToBraille(fileName,i)
        print('Ended for ',i)
        i+=1
    mergeTextToBrailleFiles()
    return 'Merge Done'    


def open_braille(filename):
    file1 = open(filename,encoding="utf8")
    content1 = file1.read()
    print(brailleToAlpha.translate(content1))
 
 
@app.route('/upload', methods=['POST'])
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
        textToBrailleConverter(filePath)
        
    else:
            errors[file.filename] = 'File type is not allowed'
 
    if success:
        return jsonify(
        message='File successfully converted to braille',
        path='B:\\project\\pdf2txt\\Merged.doc',
        filename='Merged.doc'
    )
    else:
        response = jsonify(errors)
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin','*')
        return response 
 
if __name__  == '__main__':
    app.run(debug=True,port=8082)