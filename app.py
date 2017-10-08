import sys, os
import json
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from watson_developer_cloud import VisualRecognitionV3
from werkzeug.utils import secure_filename
import folium
from utils import map_creator


UPLOAD_FOLDER = "temp"
ALLOWED_EXTENSIONS = ["jpg","jpeg","png"]

HOSTNAME = "127.0.0.1"
PORT = 3333

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=["GET"])
def home():
	return "this is the homepage, im gonna prettify it -celine"

# Renders the output of our functions
@app.route('/render', methods=["GET"]) #receives image upload and produces map from foursquare api
def render_results():
		
	# Check if the object has been identified (image has been uploaded)
	if 'objectName' not in request.args:
		return redirect(url_for('upload'))
		
	# Retrieves the object's name
	obj = request.args['objectName']
	
	# Uses Object's Name to Retrieve Foursquare Data
	# ----- TBD ------ #
	m = folium.Map(location=[45.5236, -122.6750])

	# Temporarily Save the Map
	mapPath = os.path.join( app.config['UPLOAD_FOLDER'], "map.html") 
	m.save( mapPath )

	# Render the map
	return render_template("success.html")

# Returns the map file
@app.route("/temp/map.html")
def show_map():
	return send_from_directory(app.config['UPLOAD_FOLDER'], 'map.html')

# File Upload Stuff

# Checks if file is one of the allowed extensions
def allowed_file(filename):
    return '.' in filename and \
    	filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET"])
def upload():
    return render_template("upload.html")

# Checks if the uploaded file can be processed.
# Retrieves the file, analyzes it, and sends results to be rendered.
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
	
	#save the file
	filename = secure_filename(file.filename)
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	file.save(filepath)

	#Send file to Image Recog for identification
	objectName = image_recog(filepath)
	

	# Reroute the User to the results page
	return redirect( url_for('render_results', objectName=objectName))        	


# Identifies the primary object in the Image
# Returns the name of the object
def image_recog(imagefile):

	# Get the Visual Recognition Classifier from Watson
	visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c5666e0f4f55241567cee1f69c0652e7e86d8ffe')
	
	# Retrieve the data 
	image = open( imagefile, "rb")
	imgObject = visual_recognition.classify(images_file=image) #take in image file
	#print json.dumps(imgObject) 
	objectName = imgObject['images'][0]['classifiers'][0]['classes'][0]['class'] #image's class / name
	

	# Remove the file (not needed anymore)
	os.remove( imagefile )

	# Return the Object's name
	return objectName



app.run(host=HOSTNAME, port=PORT, debug=True)

'''

{
  "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "It may take up to 5 minutes for this key to become active",
  "api_key": "c5666e0f4f55241567cee1f69c0652e7e86d8ffe"
}
'''
