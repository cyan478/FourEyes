import json

import sys
import os

from flask import Flask, render_template, request
from watson_developer_cloud import VisualRecognitionV3


app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
	return "this is the homepage, im gonna prettify it -celine"

@app.route('/upload', methods=["POST"]) #user uploads image
def post_image():
	return render_template("uploadimage.html")


# /visualrec -> "visual recommendations"
@app.route('/visualrec', methods=["GET"]) #receives image upload and produces map from foursquare api
def render_results():

	visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c5666e0f4f55241567cee1f69c0652e7e86d8ffe')
	imgObject = visual_recognition.classify(images_file=open("sample-pictures/swing.jpg", "rb")) #take in image file
	#print json.dumps(imgObject) 
	objectName = imgObject['images'][0]['classifiers'][0]['classes'][0]['class'] #image's class / name
	return objectName 




	
	#from IPython import embed; embed() #COOL DEBUGGING TECHNIQUE
	#return render_template("tone.html")





app.run(host="0.0.0.0", port=3333, debug=True)

'''

{
  "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "It may take up to 5 minutes for this key to become active",
  "api_key": "c5666e0f4f55241567cee1f69c0652e7e86d8ffe"
}
'''
