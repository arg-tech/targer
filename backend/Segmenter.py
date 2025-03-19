
import re
from flask import json
from typing import Dict, List
import logging
logging.basicConfig(datefmt='%H:%M:%S',
                    level=logging.INFO)




class Segmenter():
	def __init__(self, modelIBM) -> None:
		self.modelIBM = modelIBM
		self.nodeID_speaker = {}
		
	def is_json(self, file: str) -> bool:		
		''' check if the file is valid json
		'''

		try:
			with open(file, 'r') as file:
					content = file.read()
			
			#content = re.sub(r"(\w+)'(\w+)", r'\1"\2', content)  # handle apostrophes inside words

			content = json.dumps(content)
			#print(content)
			logging.debug(content)
			parsed_content = json.loads(content)
			
		except ValueError as e:			
			return False

		return True


	def is_json2(self, file: str) -> bool:
		''' check if the file is valid json
		'''
		try:
			# Open the file and read its content
			content = open(file).read()
			#logging.debug("Original content: %s", content)

			# Replace single quotes with double quotes
			#content = content.replace("'", '"')
			#logging.debug("after replacement content: %s", content)

			# Try to load the JSON from the modified content
			json.loads(json.dumps(content))


		except ValueError as e:
			return False

		return True


	def parse_inp(self, path):
		data=open(path).read()+"\n"
		first_names, last_names,texts = [],[],[]
		propositions = re.findall(r'([A-Za-z ]+): (.+\n)', data)

		for proposition in propositions:
			first_last_names = proposition[0].split()
			if len(first_last_names)>1:
				first_names.append(first_last_names[0])
				last_names.append(first_last_names[1])
			else:
				first_names.append(first_last_names[0])
				last_names.append("None")
			texts.append(proposition[1].replace("\n",""))
		return first_names,last_names,texts  

	def get_next_max_id(self, nodes, n_type):

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
		if len(nodes) == 0:
			return 0
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

	def delete_original_entries(
		self, 
		Lnode_id, 
		Inode_id_text, 
		json_dict
		):

		Inode_id = Lnode_id
		for node in json_dict['nodes']: 
			if node.get('type') == 'I' and  node.get('text') == Inode_id_text:
				Inode_id = node.get('nodeID')


		edited_nodes = [node for node in json_dict['nodes'] if  node.get('nodeID') not  in [Lnode_id, Inode_id]]

		edited_locutions = [node for node in json_dict['locutions'] if node.get('nodeID') not in [Lnode_id, Inode_id]]

		edited_edges = [node for node in json_dict['edges'] if not (node.get('fromID') == Lnode_id or node.get('toID') == Lnode_id or node.get('fromID') == Inode_id or node.get('toID') == Inode_id) ]

		json_dict['nodes'] = edited_nodes
		json_dict['edges'] = edited_edges
		json_dict['locutions'] = edited_locutions		
		return(json_dict)
	
	def get_inode(self, edges, n_id):
		for entry in edges:
			if n_id == entry['fromID']:
				ya_node_id = entry['toID']
				for entry2 in edges:
					if ya_node_id == entry2['fromID']:
						inode_id = entry2['toID']
						return(inode_id, ya_node_id)
		return None, None

	def remove_entries(self, node_id, L_nodes, edges, locutions):
		"""
		This function removes entries associated with a specific node ID from a JSON dictionary.

		Arguments:
		- node_id (int): the node ID to remove from the JSON dictionary
		- json_dict (Dict): the JSON dictionary to edit

		Returns:
		- (Dict): the edited JSON dictionary with entries associated with the specified node ID removed
		"""
		# Remove nodes with the specified node ID
		in_id, yn_id = self.get_inode(edges, node_id)
		edited_nodes = [node for node in L_nodes if node.get('nodeID') != node_id]
		edited_nodes = [node for node in edited_nodes if node.get('nodeID') != in_id]

		# Remove locutions with the specified node ID
		edited_locutions = [node for node in locutions if node.get('nodeID') != node_id]

		# Remove edges with the specified node ID
		edited_edges = [node for node in edges if not (node.get('fromID') == node_id or node.get('toID') == node_id)]
		edited_edges = [node for node in edited_edges if not (node.get('fromID') == in_id or node.get('toID') == in_id)]
		edited_nodes = [node for node in edited_nodes if node.get('nodeID') != yn_id]
		# Return the edited JSON dictionary
		return edited_nodes, edited_edges, edited_locutions
	
	def is_json_aif_dialog(self, node_list: list) -> bool:
		''' check if json_aif is dialog
		'''

		for nodes_entry in node_list:					
			if nodes_entry['type'] == "L":
				return True
		return False

	def _get_segments(self, input_text):
		return re.split("[.!?]",input_text)
	def get_speaker(self, 
		node_id: int, 
		locutions: List[Dict[str, int]], 
		participants: List[Dict[str, str]]
		) -> str:
		"""
		This function takes a node ID, a list of locutions, and a list of participants, and returns the name of the participant who spoke the locution with the given node ID, or "None" if the node ID is not found.

		Arguments:
		- node_id (int): the node ID to search for
		- locutions (List[Dict]): a list of locutions, where each locution is a dictionary containing a node ID and a person ID
		- participants (List[Dict]): a list of participants, where each participant is a dictionary containing a participant ID, a first name, and a last name

		Returns:
		- (str): the name of the participant who spoke the locution with the given node ID, or "None" if the node ID is not found
		"""

		
		# Loop through each locution and extract the person ID and node ID
		for locution in locutions:
			personID = locution['personID']
			nodeID = locution['nodeID']
			
			# Loop through each participant and check if their participant ID matches the person ID from the locution
			for participant in participants:
				if participant["participantID"] == personID:
					# If there is a match, add the participant's name to the nodeID_speaker dictionary with the node ID as the key
					firstname = participant["firstname"]
					surname = participant["surname"]
					self.nodeID_speaker[nodeID] = (firstname+" "+surname,personID)
					
		# Check if the given node ID is in the nodeID_speaker dictionary and return the corresponding speaker name, or "None" if the node ID is not found
		if node_id in self.nodeID_speaker:
			return self.nodeID_speaker[node_id]
		else:
			return ("None","None")

	def ibm_segmenter(self, input_text):

		
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


		result = self.modelIBM.label_with_probs(input_text)
		segments = self.get_segments(result)
		#response = make_response(jsonify(result))
		return segments

	def get_segments(self, labeling_output):
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
		return props

	def _add_entry(
		self, 
		L_nodes, 
		locutions, 
		old_locutions, 
		edges,
		participants, 
		id_counter, 
		n_id,
		text_with_span,
		propositions_all ,
		propositions_id,
		prop,
		dialog,
		count_L_nodes
		):
		'''id_counter = id_counter+1
		l_node_id = id_counter
		
		speaker = ""
		for entry_locutions in old_locutions:
			l_id = entry_locutions['nodeID']
			if n_id == l_id:
				speaker = entry_locutions['personID']

		L_nodes.append({'text': prop, 'type':'L','nodeID': l_node_id})
		count_L_nodes=count_L_nodes+1			
		locution_id = l_node_id+1			
		locutions.append({'personID': speaker, 'nodeID': l_node_id})
		count_L_nodes=count_L_nodes+1			
		i_id=locution_id+1						
		L_nodes.append({'text': prop, 'type':'I','nodeID': i_id})	
		count_L_nodes=count_L_nodes+1
		y_id=i_id+1			
		L_nodes.append({'text': 'Default Illocuting', 'type':'YA','nodeID': y_id})	
		count_L_nodes=count_L_nodes+1	
		edge_id=y_id+1
		edges.append({'toID': y_id, 'fromID':l_node_id,'edgeID': edge_id})
		count_L_nodes=count_L_nodes+1
		edge_id=edge_id+1
		edges.append({'toID': i_id, 'fromID':y_id,'edgeID': edge_id})
		count_L_nodes=count_L_nodes+1'''

		speaker = ""
		speaker_id = None
		
		if participants:
			speaker, speaker_id = self.get_speaker(
				n_id, 
				locutions, 
				participants
				)
			first_name_last_name = speaker.split()
			first_n, last_n = first_name_last_name[0], first_name_last_name[1]
			if last_n=="None":
				speaker = first_n
			else:
				speaker = first_n+" " + last_n
		else:
			first_n, last_n  = "None", "None"

		
		l_node_id = self.get_next_max_id(L_nodes, 'nodeID')
		L_nodes.append({'text': prop, 'type':'L','nodeID': l_node_id})		
		locutions.append({'personID': speaker_id, 'nodeID': l_node_id})
		participants.append(
			{
			"participantID": speaker_id,
			"firstname": first_n,
			"surname": last_n
			}
			)
		p_id += 1
		i_id = self.get_next_max_id(L_nodes, 'nodeID')			
		L_nodes.append({'text': prop, 'type':'I','nodeID': i_id})

		y_id = self.get_next_max_id(L_nodes, 'nodeID')	
		L_nodes.append({'text': 'Default Illocuting', 'type':'YA','nodeID': y_id})	

		edge_id = self.get_next_max_id(edges, 'edgeID')	
		edges.append({'toID': y_id, 'fromID':l_node_id,'edgeID': edge_id})
		edge_id = self.get_next_max_id(edges, 'edgeID')	
		edges.append({'toID': i_id, 'fromID':y_id,'edgeID': edge_id})

		if prop not in propositions_all:
			propositions_all.append(prop)
			propositions_id.update({prop:i_id})
		id_counter = edge_id+1
		text_with_span = text_with_span+" "+str(speaker)+" "+"<span class=\"highlighted\" id=\""+str(l_node_id)+"\">"+prop+"</span>.<br><br>"



		return 	(
			L_nodes,
			locutions, 
			old_locutions,
			edges,
			participants,
			id_counter, 
			n_id,
			text_with_span,
			propositions_all,
			propositions_id,
			prop,
			count_L_nodes
			)
	def convert_single_to_double_quotes(self, data):
		# Replace single quotes with double quotes safely
		data = data.replace("'", '"')

		# Validate and ensure correct JSON formatting
		try:
			parsed_json = json.loads(data)
			return json.dumps(parsed_json, indent=4)  # Pretty-print JSON
		except json.JSONDecodeError:
			print("Warning: Attempting alternative parsing...")
			try:
				parsed_json = eval(data)  # Converts Python-style dict to valid JSON
				return json.dumps(parsed_json, indent=4)
			except Exception as e:
				raise ValueError("Invalid JSON or Python dictionary format:")

	def cascading_anaphora_propositionalizer(self, path):       
		if path.endswith("json"):
			is_json_file=self.is_json(path)                     
			if is_json_file: 
				data = open(path).read()   
				#data = self.convert_single_to_double_quotes(data)  # Convert single to double quotes 
				#data = re.sub(r"(\w+)'(\w+)", r'\1"\2', data)  # handle apostrophes inside words

				#data = json.dumps(data)
				#print(content)
				#parsed_content = json.loads(content)
                        
				extended_json_aif = eval(data)
				json_aif = json_dict = extended_json_aif['AIF']
				
				
				if 'nodes' in json_dict and 'locutions' in json_dict and 'edges' in json_dict:	
			
					participants = json_dict.get("participants")               
					locutions = json_dict.get("locutions")
					edges = json_dict.get("edges")
					old_edges = edges.copy()
					nodes = json_dict.get("nodes") 
					old_nodes = nodes.copy()                   
					for nodes_entry in old_nodes:                        
						type = nodes_entry['type']
						node_id = nodes_entry['nodeID']
						if type == "L":  
							props = []  
							#l_node_text = nodes_entry['text'].replace("\n","")
							speaker_id = None
							if participants:
								_, speaker_id = self.get_speaker(node_id, locutions, participants)
							
							props = self.ibm_segmenter(nodes_entry['text'])

							if len(props) > 1:
								for prop in props:
									n_id = self.get_next_max_id(nodes, 'nodeID')
									#logging.debug('fthe id is {n_id}', n_id)
									nodes.append({'text': prop, 'type':'L','nodeID': n_id})
									locutions.append({'personID': speaker_id, 'nodeID': n_id})
									y_n_id = self.get_next_max_id(nodes, 'nodeID')
									nodes.append({'text': 'Default Illocuting', 'type':'YA','nodeID': y_n_id})	
									edge_id = self.get_next_max_id(edges, 'edgeID')
									edges.append({'toID': y_n_id, 'fromID':node_id,'edgeID': edge_id})
									edge_id = self.get_next_max_id(edges, 'edgeID')
									edges.append({'toID': n_id, 'fromID':y_n_id,'edgeID': edge_id})              
								nodes, edges, locutions  = self.remove_entries(node_id, nodes, edges, locutions)
					json_aif.update( {'nodes' : nodes} )
					json_aif.update( {'edges' : edges} )
					json_aif.update( {'locutions' : locutions} )            
					extended_json_aif['AIF'] = json_aif
					return json.dumps(extended_json_aif)
				else:
					return("Invalid json-aif")
		else:
			extended_json_aif = {}
			json_aif={}
			OVA = {}
			text_with_span=""
			L_nodes=[]
			edges=[]
			schemefulfillments = []
			descriptorfulfillments = []
			participants = []
			locutions=[]
			first_names, last_names,texts = self.parse_inp(path)
			j = 0
			for first_n, last_n,text in zip(first_names, last_names,texts):
				props = []
				if last_n=="None":
					speaker_names = first_n
				else:
					speaker_names = first_n+" " + last_n				
					props = self.ibm_segmenter(text)
				for prop in props:
					L_nodes.append({'text': prop, 'type':'L','nodeID': j})                         
					locutions.append(
						{"nodeID": str(j),  
						"personID": j
						})

					participants.append(
						{
						"participantID": j,
						"firstname": first_n,
						"surname": last_n
						})
					text_with_span=text_with_span+" "+speaker_names+" "+"<span class=\"highlighted\" id=\""+str(j)+"\">"+prop+"</span>.<br><br>"
					j=j+1
				json_aif.update( {'nodes' : L_nodes} )
				json_aif.update( {'edges' : edges} )
				json_aif.update( {'locutions' : locutions} )
				json_aif.update( {'schemefulfillments' : schemefulfillments} )
				json_aif.update( {'descriptorfulfillments' : descriptorfulfillments} )
				json_aif.update( {'participants' : participants} )
				extended_json_aif['AIF'] = json_aif
				extended_json_aif['OVA'] = OVA
				extended_json_aif['text'] = text_with_span      

			return json.dumps(extended_json_aif)

		
	def _segmenter_default(self, path: str):
		is_json_file=self.is_json(path)

		if is_json_file:
			data = open(path).read()		
			extended_json_aif = eval(data)
			json_dict = extended_json_aif['AIF']
			dialog = extended_json_aif.get('dialog')
			if not dialog:
				dialog = False
			text_with_span_old = ""

			if 'text' in extended_json_aif:
				text_with_span_old = extended_json_aif['text']
			text_with_span=""
			if 'nodes' in json_dict and 'locutions' in json_dict and 'edges' in json_dict:

				nodes = json_dict['nodes']
				L_nodes = nodes.copy()
				locutions = json_dict['locutions']
				edges = json_dict['edges']
				old_locutions = json_dict['locutions']
				schemefulfillments = json_dict.get('schemefulfillments')
				descriptorfulfillments = json_dict.get('descriptorfulfillments')
				participants = json_dict.get("participants")	

				#logging.info('participants: {}'.format(participants))
				if not participants:
					participants = []
			
				id_counter = 0				
				count_L_nodes = 0
				propositions_all = []
				propositions_id =  {}

				for nodes_entry in nodes:
					speaker = ""
					n_id = nodes_entry['nodeID']
					node_text = nodes_entry['text']
					type = nodes_entry['type']
					propositions = []	

					if type == "L":
						propositions = self.ibm_segmenter(nodes_entry['text'])
						propositions = [p.strip() for p in propositions if len(p.strip())>1]

						#logging.info('propositions: {}'.format(propositions))

						if len(propositions) > 0:
							for prop in propositions:
								prop = prop.strip()							
								if prop != "":
									#logging.info('prop: {}'.format(prop))	
									(
										L_nodes,
										locutions,
										old_locutions,
										edges,
										participants,
										id_counter, 
										n_id,
										text_with_span,
										propositions_all,
										propositions_id,
										prop,
										count_L_nodes
										) = self._add_entry(
										L_nodes,
										locutions, 
										old_locutions, 
										edges, 
										participants,
										id_counter, 
										n_id,
										text_with_span,
										propositions_all,
										propositions_id,
										prop,
										dialog,
										count_L_nodes
										)				

							L_nodes, edges, locutions  = self.remove_entries(n_id, L_nodes, edges, locutions)

				json_dict['nodes'] = L_nodes
				json_dict['edges']= edges 
				json_dict['locutions'] = locutions
				json_dict.update( {'schemefulfillments' : schemefulfillments} )
				json_dict.update( {'descriptorfulfillments' : descriptorfulfillments} )
				json_dict.update( {'participants' : participants} )

				extended_json_aif['AIF'] = json_dict
				
				extended_json_aif['text'] = text_with_span

				if text_with_span_old:
					extended_json_aif.update({'text': text_with_span_old})
				else:
					extended_json_aif.update({'text': text_with_span})
				return json.dumps(extended_json_aif)
			else:
				return("Invalid json-aif")
		else:
			return("Invalid input")
	






  
