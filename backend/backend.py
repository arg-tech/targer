#!/usr/bin/env python3

"""be.py: Description."""
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask_restful import Api, Resource, reqparse
from flask import make_response
from nltk.tokenize import sent_tokenize, word_tokenize
import random
import json
from flask import jsonify
import json
import logging
import re
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
#app.json_encoder = LazyJSONEncoder


# Initialize Prometheus metrics
#metrics = PrometheusMetrics(app)

# group by endpoint rather than path
metrics = PrometheusMetrics(app)

@app.route('/collection/:collection_id/item/:item_id')
@metrics.counter(
    'cnt_collection', 'Number of invocations per collection', labels={
        'collection': lambda: request.view_args['collection_id'],
        'status': lambda resp: resp.status_code
    })
def get_item_from_collection(collection_id, item_id):
    pass




#logging configuration
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)

"""Models"""

from Model import Model
from Segmenter import Segmenter
#from ModelNewES import ModelNewES
#from ModelNewWD import ModelNewWD


#modelNewES = ModelNewES()

#modelNewWD = ModelNewWD()

modelIBM = Model("IBM.h5")
#modelIBM = Model("debela-arg/segmenter")
#We must call this cause of a keras bug
#https://github.com/keras-team/keras/issues/2397
modelIBM.label("Therefore fixed punishment will")

'''modelCombo = Model("COMBO.h5")
# # We must call this cause of a keras bug
# # https://github.com/keras-team/keras/issues/2397
modelCombo.label("Therefore fixed punishment will")

modelES = Model("ES.h5")
# We must call this cause of a keras bug
# https://github.com/keras-team/keras/issues/2397
modelES.label("Therefore fixed punishment will")

modelWD = Model("WD.h5")
# # We must call this cause of a keras bug
# # https://github.com/keras-team/keras/issues/2397
modelWD.label("Therefore fixed punishment will")

modelES_dep = Model("ES_dep.h5")
# # We must call this cause of a keras bug
# # https://github.com/keras-team/keras/issues/2397
modelES_dep.label("Therefore fixed punishment will")

modelWD_dep = Model("WD_dep.h5")
# # We must call this cause of a keras bug
# # https://github.com/keras-team/keras/issues/2397
modelWD_dep.label("Therefore fixed punishment will")'''

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)



#metrics = PrometheusMetrics(app)

class ClassifyIBM(Resource):
    def post(self):
       """
       Classifies input text to argument structure (IBM model, fasttext - big dataset)
       ---
       consumes:
         - text/plain
       parameters:
         - in: body
           name: text
           type: string
           required: true
           description: Text to classify
           example: Quebecan independence is justified. In the special episode in Japan, his system is restored by a doctor who wishes to use his independence for her selfish reasons.
       responses:
         200:
           description: A list of tagged tokens annotated with labels
           schema:
             id: argument-structure
             properties:
               argument-structure:
                 type: string
                 description: JSON-List
                 default: No input text set
        """
       inputtext = "request.get_data().decode('UTF-8')"
       result = modelIBM.label_with_probs(inputtext)
       response = make_response(jsonify(result))
       response.headers['content-type'] = 'application/json'
       return response



def get_file(file_obj):
    f_name = file_obj.filename    
    file_obj.save(f_name)
    file = open(f_name,'r')
    return f_name

def get_argument_relation(labeling_output):
    """ post processing
    it takes the output of targer seqeunce labling and returns:
    a: segements based on BIO labling scheme
    b: argument relation between a pair of proposition - it is based on a rather simple assumption 
    that if one of the proposition is a premise wheile the other is the claim,
    an argument relation is introduced between the two"""
    
    props = {}
    for prop in labeling_output:
        segment = []
        prop_type = ""
        for token in prop:
            if token['label'] in ['P-B', 'P-I']:
                segment.append(token['token'])
                prop_type = "premise"
            elif token['label'] in ['C-B', 'C-I']:
                segment.append(token['token'])
                prop_type = "Claim"
        props[' '.join(segment)] = prop_type
    print(props.keys())
    #logging.info('keys: {}'.format(props.keys()))
    prop_list = list(props.keys())
    if len(prop_list)>1:
      p1 = prop_list[0]
      p1_type = props[p1]
      p2 = prop_list[1]
      p2_type = props[p2]
      #logging.info('the two categories: {} {}'.format(p1_type, p2_type))
      return p1_type!=p2_type
    else:
      return False


def ibm_am_label(inputtext):
  
    """
    Classifies input text to argument structure (IBM model, fasttext - big dataset)
    ---
    consumes:
      - text/plain
    parameters:
      - in: body
        name: text
        type: string
        required: true
        description: Text to classify
        example: Quebecan independence is justified. In the special episode in Japan, his system is restored by a doctor who wishes to use his independence for her selfish reasons.
    responses:
      200:
        description: A list of tagged tokens annotated with labels
        schema:
          id: argument-structure
          properties:
            argument-structure:
              type: string
              description: JSON-List
              default: No input text set
    """
    #inputtext = "This is sample text."

    result = modelIBM.label_with_probs(inputtext)
    #logging.info('total label: {}'.format(result))
    argument_relation = get_argument_relation(result)
    #logging.info('argument_relation: {}'.format(argument_relation))
    arg_rel2 = "None"
    if  argument_relation:
        arg_rel2="RA"
    else:
        arg_rel2="None"
    #logging.info('arg_rel2: {}'.format(arg_rel2))
    #response = make_response(jsonify(result))
    return arg_rel2



def is_json(file: str) -> bool:		
  ''' check if the file is valid json
  '''

  try:
    with open(file, 'r') as file:
            content = file.read()
    logging.debug(content)
    content = re.sub(r"(\w+)'(\w+)", r'\1"\2', content)  # handle apostrophes inside words

    content = json.dumps(content)
    #print(content)
    parsed_content = json.loads(content)
    
  except ValueError as e:			
    return False

  return True

def nodes_counter(nodeset: list):
	return len([entry for entry in nodeset])

def get_next_max_id(nodes, n_type):
    """
    This function takes a list of nodes and returns the maximum node ID.

    Arguments:
    - nodes (List[Dict]): a list of nodes, where each node is a dictionary containing a node ID

    Returns:
    - (int): the maximum node ID in the list of nodes
    """
    # Initialize a variable to store the maximum node ID found so far
    max_id  = 0
    lef_n_id, right_n_id = 0, ""
  
    if isinstance(nodes[0][n_type],str):
      if "_" in nodes[0][n_type]:
          
          #logging.debug('with hyphen')       
          # Loop through each node in the list of nodes
          for node in nodes:
              # Check if the current node ID is greater than the current maximum
              #logging.debug(node)
              temp_id = node[n_type]
              if "_" in temp_id:
                  nodeid_parsed = temp_id.split("_")
                  lef_n_id, right_n_id = int(nodeid_parsed[0]), nodeid_parsed[1]
                  if lef_n_id > max_id:
                      max_id = lef_n_id
          #logging.debug(str(int(max_id)+1)+"_"+str(right_n_id))
          return str(int(max_id)+1)+"_"+str(right_n_id)
      else:
        for node in nodes:
            # Check if the current node ID is greater than the current maximum
            temp_id = int(node[n_type])     
            if temp_id > max_id:
                # If it is, update the maximum to the current node ID
                max_id = temp_id   
        # Return the maximum node ID found
        return str(max_id+1)

    elif isinstance(nodes[0][n_type],int):	
      for node in nodes:
          # Check if the current node ID is greater than the current maximum
          temp_id = node[n_type]     
          if temp_id > max_id:
              # If it is, update the maximum to the current node ID
              max_id = temp_id   
      # Return the maximum node ID found
      return max_id+1

@app.route('/targer-am', methods=['POST'])
@metrics.counter('targer_am_requests_total', 'Total number of requests to /targer-am')
def get_inference_targer():
  if request.method == 'POST':	
    file_obj = request.files['file']
    path = get_file(file_obj)
    is_json_file = is_json(path)
    if is_json_file: 
      data=open(path).read()+"\n"	    
      extended_json_aif = json.loads(data)
      json_dict = extended_json_aif['AIF']
      #edges = []

      if 'nodes' in json_dict and 'locutions' in json_dict and 'edges' in json_dict:
        json_aif={}	
        edges= json_dict['edges']
        nodes=json_dict['nodes']
        old_nodes = nodes.copy()
        locutions = json_dict['locutions']
        schemefulfillments = json_dict.get('schemefulfillments')
        descriptorfulfillments = json_dict.get('descriptorfulfillments')
        participants = json_dict.get("participants")



        propositions_all=[]
        propositions_id={}
        for nodes_entry in old_nodes:
          node_type=nodes_entry['type']
          original_node_id = nodes_entry['nodeID']
          if node_type=="I":
            proposition = nodes_entry['text']				
            proposition=proposition.strip()					
            if proposition!="":
              if proposition not in propositions_all:
                propositions_all.append(proposition)
                propositions_id.update({original_node_id:proposition})


        #props1, props2, index1, index2 =[], [], 0, 0
        connected_propositions = []
        for index1, prop1 in propositions_id.items():          
          for  index2, prop2 in propositions_id.items():
            if index1!=index2 and (str(index1)+'and'+str(index2) not in connected_propositions or str(index2)+'and'+str(index1) not in connected_propositions):
              connected_propositions.append(str(index1)+'and'+str(index2))
              connected_propositions.append(str(index2)+'and'+str(index1))
              p1p2 = prop1+" "+prop2
              #logging.info('both propositions: {}'.format(p1p2))
              result = ibm_am_label(p1p2)
              #logging.info('relation type: {}'.format(result))

              if result == "RA":
                node_id = get_next_max_id(nodes, 'nodeID')
                edge_id = get_next_max_id(edges, 'edgeID')
                nodes.append({'text': 'Default Inference', 'type':'RA','nodeID': node_id})					
                edges.append({'fromID': index1, 'toID': node_id,'edgeID':edge_id})
                #logging.info('list of edges: {}'.format(edges))
                edge_id = get_next_max_id(edges, 'edgeID')
                edges.append({'fromID': node_id, 'toID': index2,'edgeID':edge_id})
              
              if result=="CA":	
                node_id = get_next_max_id(nodes, 'nodeID')
                edge_id = get_next_max_id(edges, 'edgeID')
                nodes.append({'text': 'Default Conflict', 'type':'CA','nodeID': node_id})				
                edges.append({'fromID': index1, 'toID': node_id,'edgeID':edge_id})
                edge_id = get_next_max_id(edges, 'edgeID')
                edges.append({'fromID': node_id, 'toID': index2,'edgeID':edge_id})


        json_aif.update( {'nodes' : nodes} )
        json_aif.update( {'edges' : edges} )
        json_aif.update( {'locutions' : locutions} )
        json_aif.update( {'schemefulfillments' : schemefulfillments} )
        json_aif.update( {'descriptorfulfillments' : descriptorfulfillments}),
        json_aif.update( {'participants' : participants} )
        extended_json_aif['AIF'] = json_aif	

        return json.dumps(extended_json_aif)

      else:
        return("Invalid json-aif")
    else:
      return("Invalid input")


@app.route('/targer-segmenter', methods=['POST', 'GET'])
@metrics.counter('targer_segmenter_requests_total', 'Total number of requests to /targer-segmenter')
def ibm_segmenter():    

	if request.method == 'POST':
		file_obj = request.files['file']
		f_name = get_file(file_obj)
		segment = Segmenter(modelIBM)
		result = segment.cascading_anaphora_propositionalizer(f_name)
		return result
	if request.method == 'GET':
		info = "Segmenter is an AMF compononet that segments arguments into propositions.  This is targer based segmenter that uses BIO based labling scheme. It takes xIAF as an input to return xIAF as an output. The component can be conected to propositionUnitizer to create argument mining pipeline."
		return info
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("6000"), debug=False)


