import sys
import json
from flask import Flask, render_template, request
from watson_developer_cloud import ToneAnalyzerV3

app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
	return "<b> hello world </b>"

@app.route('/example', methods=["GET"])
def version():
	return sys.version

@app.route('/tone', methods=["GET"])
def get_tone():
	return render_template("tone.html")

@app.route('/visualrec', methods=["POST"]) #POST of tone
def post_tone():
	u = "d6094380-8c1e-4522-9f9d-97aeadb47356"
	p = "vSAcDfdNZr1r"
	v = "2016-05-19"
	text = request.values['tone'] #from dictionary, textarea name = tone, pull out input words
	t = ToneAnalyzerV3(username=u, password=p, version=v)
	d = t.tone(text)
	
	from IPython import embed; embed() #COOL DEBUGGING TECHNIQUE
	return render_template("tone.html")


app.run(host="0.0.0.0", port=3333, debug=True)

'''

{
  "url": "https://gateway.watsonplatform.net/tone-analyzer/api",
  "username": "d6094380-8c1e-4522-9f9d-97aeadb47356",
  "password": "vSAcDfdNZr1r"
}
'''
