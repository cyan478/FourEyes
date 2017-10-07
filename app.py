import sys, os
import json
from flask import Flask, render_template, request, url_for, redirect
from watson_developer_cloud import ToneAnalyzerV3
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = ["jpg","jpeg","png"]


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=["GET"])
def home():
	return "this is the homepage, im gonna prettify it -celine"

# /visualrec -> "visual recommendations"
@app.route('/visualrec', methods=["GET"]) #receives image upload and produces map from foursquare api
def render_results():

	visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c5666e0f4f55241567cee1f69c0652e7e86d8ffe')
	imgObject = visual_recognition.classify(images_file=open("sample-pictures/swing.jpg", "rb")) #take in image file
	#print json.dumps(imgObject) 
	objectName = imgObject['images'][0]['classifiers'][0]['classes'][0]['class'] #image's class / name
	return objectName 


# File Upload Stuff

# Checks if file is one of the allowed extensions
def allowed_file(filename):
        return '.' in filename and \
                filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET"])
def upload():
        return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():

        #check if there is a file
        if 'file' not in request.files:
                flash("File Not Found")
                return redirect(url_for('upload')) # Refinement Suggestion: Send JSON to Client instead

        #retrieve file
        file = request.files['file']

        #check that it is a file
        if not file:
                print("Not A File")
                return redirect(url_for('upload')) # Refinement Suggestion: Send JSON to Client instead
        
        #check that the file has a name 
        if file.filename == '':
                print("No Selectec File")
                return redirect(url_for('upload')) # Refinement Suggestion: Send JSON to Client instead
        
        
        #check that file is allowed
        if not allowed_file( file.filename ) :
                print("File Extension not Allowed")
                return redirect(url_for('upload')) # Refinement Suggestion: Send JSON to Client instead

        #Upload File and Store it
        filename = secure_filename( file.filename ) 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('success_upload'))

@app.route("/success", methods=["GET"])
def success_upload():
        return render_template("success.html")


app.run(host="0.0.0.0", port=3333, debug=True)

'''

{
  "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "It may take up to 5 minutes for this key to become active",
  "api_key": "c5666e0f4f55241567cee1f69c0652e7e86d8ffe"
}
'''
