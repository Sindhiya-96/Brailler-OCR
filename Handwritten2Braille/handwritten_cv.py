import cv2
import pytesseract
from PIL import Image
from textblob import TextBlob
import printer, alphaToBraille
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask import Flask, json, request, jsonify
import os


app = Flask(__name__)
CORS(app)

app.secret_key = "caircocoders-ednalan"
 
UPLOAD_FOLDER = 'B:/project/handwritten/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#im = cv2.imread('img2.png') 
#contours_text()

def open_text(filename):
    file = open(filename)
    content = file.read()
    opt1= alphaToBraille.translate(content)
    print(alphaToBraille.translate(content))
    brailleFileName ="handop.doc"
    with open(brailleFileName,"w",encoding="utf-8") as op:
        op.write(opt1)
        op.close()



# preprocessing
# gray scale
def gray(img):
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(r"img_gray.png",img)
    return img

# blur
def blur(img) :
    img_blur = cv2.GaussianBlur(img,(5,5),0)
    cv2.imwrite(r"img_blur.png",img)    
    return img_blur

# threshold
def threshold(img,im):
    #pixels with value below 100 are turned black (0) and those with higher value are turned white (255)
    img = cv2.threshold(img, 100, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)[1]    
    cv2.imwrite(r"img_threshold.png",img)
    # configurations
    config = ('-l eng --oem 1 --psm 3')
    # pytessercat
    text = pytesseract.image_to_string(im, config=config)
    # print text
    text = text.split('\n')

    mystring =' '.join(map(str,text))

    text1=mystring.split()
    print(text1)
    crt = " "
    finalText =" "
    for x in text1:
   
        voc=x.lower()
        finalText=finalText+" "+ voc
        b = TextBlob(finalText)
        crt= b.correct()
    print(crt)
     
    file1 = open("input.doc","w")
    file1.write(str(crt).lower())
    file1.close() 
    fileName="B:\project\handwritten\input.doc"
    open_text(fileName)       
       
    
    
# Finding contours 
"""im_gray = gray(im)
im_blur = blur(im_gray)
im_thresh = threshold(im_blur)

contours,_ = cv2.findContours(im_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) """

# text detection
"""def contours_text(orig, img, contours):
    for cnt in contours: 
        x, y, w, h = cv2.boundingRect(cnt) 

        # Drawing a rectangle on copied image 
        rect = cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 255, 255), 2) 
        
        cv2.imshow('cnt',rect)
        cv2.waitKey()

        # Cropping the text block for giving input to OCR 
        cropped = orig[y:y + h, x:x + w] 

        # Apply OCR on the cropped image 
        config = ('-l eng --oem 1 --psm 3')
        text = pytesseract.image_to_string(cropped, config=config) 

        print(text)"""
 

@app.route('/uploadHandwrittenToBraille', methods=['POST'])
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
        im = cv2.imread(filePath) 
        im_gray = gray(im)
        im_blur = blur(im_gray)
        im_thresh = threshold(im_blur,im)
        
    else:
            errors[file.filename] = 'File type is not allowed'
 
    if success:
        return jsonify(
        message='File successfully converted to braille',
        path='B:\\project\\handwritten\\handop.doc',
        filename='handop.doc'
    )
    else:
        response = jsonify(errors)
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin','*')
        return response 
 
if __name__  == '__main__':
    app.run(debug=True,port=8086) 
