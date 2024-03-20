#!/usr/bin/env python3

"""be.py: Description."""
from flask import Flask, request
from flask_restful import Api
from data import Data,get_file
import logging




#logging configuration
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)

"""Models"""

from Segmenter import Segmenter
from backend import  TargerInference


app = Flask(__name__)
api = Api(app)


@app.route('/targer-am', methods=['POST'])
def get_inference_targer():
    if request.method == 'POST':	
        file_obj = request.files['file']
        data = Data(file_obj)
        targer = TargerInference(data)
        return targer.get_argument_structure()

    if request.method == 'GET':
        info = """ This is targer based relation identifier that uses BIO based labling scheme. 
        It takes xIAF as an input to return xIAF as an output. The component can be conected to other AMF modules to create argument mining pipeline."""
        return info



@app.route('/targer-segmenter', methods=['POST', 'GET'])
def ibm_segmenter():    

	if request.method == 'POST':
		file_obj = request.files['file']
		f_name = get_file(file_obj)
		segment = Segmenter()
		result = segment.cascading_anaphora_propositionalizer(f_name)
		return result
	if request.method == 'GET':
		info = "Segmenter is an AMF compononet that segments arguments into propositions.  This is targer based segmenter that uses BIO based labling scheme. It takes xIAF as an input to return xIAF as an output. The component can be conected to propositionUnitizer to create argument mining pipeline."
		return info
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("6000"), debug=False)


