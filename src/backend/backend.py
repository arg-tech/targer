#!/usr/bin/env python3

"""be.py: Description."""
import logging
#logging configuration
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.DEBUG)

"""Models"""
from Model import Model
from data import AIF

class TargerInference:
    def __init__(self,data):
        self.data = data
        self.modelIBM = Model("IBM.h5")
        self.AIF = AIF()
    def get_argument_structure(self,):
        """Retrieve the argument structure from the input data."""
        data = self.get_json_data()
        if not data:
            return "Invalid input"       
        x_aif = data.get_aif(format='xAIF')
        aif = x_aif.get('AIF', {})
        if not self.is_valid_aif(aif):
            return "Invalid json-aif"
        propositions_id_pairs = self.get_propositions_id_pairs(aif)
        self.update_node_edge_with_relations(propositions_id_pairs, aif)
        return x_aif

    def get_json_data(self,):
        """Retrieve JSON data from the file."""      
        return self.data if self.data.is_valid_json() else None

    def is_valid_aif(self, aif):
        """Check if the AIF data is valid."""
        return 'nodes' in aif and 'edges' in aif

    def get_propositions_id_pairs(self, aif):
        """Extract proposition ID pairs from the AIF data."""
        propositions_id_pairs = {}
        for node in aif.get('nodes', []):
            if node.get('type') == "I":
                proposition = node.get('text', '').strip()
                if proposition:
                    node_id = node.get('nodeID')
                    propositions_id_pairs[node_id] = proposition
        return propositions_id_pairs
    
    def update_node_edge_with_relations(self, propositions_id_pairs, aif):
        """
        Update the nodes and edges in the AIF structure to reflect the new relations between propositions.
        """
        checked_pairs = set()
        for prop1_node_id, prop1 in propositions_id_pairs.items():
            for prop2_node_id, prop2 in propositions_id_pairs.items():
                if prop1_node_id != prop2_node_id:
                    pair1 = (prop1_node_id, prop2_node_id)
                    pair2 = (prop2_node_id, prop1_node_id)
                    if pair1 not in checked_pairs and pair2 not in checked_pairs:
                        checked_pairs.add(pair1)
                        checked_pairs.add(pair2)
                        prediction = self.ibm_am_label(prop1+" "+prop2)
                        self.AIF.create_entry(aif['nodes'], aif['edges'], prediction, prop1_node_id, prop2_node_id)
    


    def get_argument_relation(self, labeling_output):
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


    def ibm_am_label(self,inputtext):
      
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
        result = self.modelIBM.label_with_probs(inputtext)
        #logging.info('total label: {}'.format(result))
        argument_relation = self.get_argument_relation(result)
        #logging.info('argument_relation: {}'.format(argument_relation))
        arg_rel2 = "None"
        if  argument_relation:
            arg_rel2="RA"
        else:
            arg_rel2="None"

        return arg_rel2











