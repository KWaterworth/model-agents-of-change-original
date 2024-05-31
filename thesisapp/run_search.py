from transformers import BertModel, BertTokenizer
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
import json
import django
import pickle
from django.conf import settings

# Set the path to your Django project directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis.settings')

# Add the project directory to the Python path
sys.path.append(PROJECT_DIR)

# Initialize Django
django.setup()

# Import Django models
from thesisapp.models import PaperSourceTOU, Person, ResearchInstitution, PaperMetaData, PaperMetaDataAuthors, PaperMetaDataInstitutions, PaperTOU


#####################################################
###   Initialize the model and CUDA if available
#####################################################

# Initialize Model and Tokenizer as global variables
model = None
tokenizer = None

def initialize_model():
	global model, tokenizer
	# Check if CUDA is available
	if torch.cuda.is_available():
		device = torch.device("cuda")
		print("Using GPU:", torch.cuda.get_device_name(0))
	else:
		device = torch.device("cpu")
		print("CUDA is not available. Using CPU.")

	# Load SciBERT tokenizer
	tokenizer = BertTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')

	# Load pre-trained SciBERT model
	# Construct the full path to the model directory using BASE_DIR
	model_dir = os.path.join(settings.BASE_DIR, 'thesisapp', 'large_models', 'scibert')
	model = BertModel.from_pretrained(model_dir).to(device)

#####################################################
###   Basic Functions
#####################################################

# Get embedding from a string of text
def get_embedding(string):
	global model, tokenizer
	inputs = tokenizer(string, return_tensors="pt", max_length=512, truncation=True)
	outputs = model(**inputs)
	embeddings = torch.mean(outputs.last_hidden_state, dim=1)
	return embeddings.detach().numpy()

#####################################################
###   Database Queries and Cosine Similarity
#####################################################

def compareTOUs(query):
	global model, tokenizer
	# Initialize Model
	initialize_model()

	# Can eventually outsource some of this stuff to other functions, 
	# because will want to leave room for taking top percentage and sending back to ASP answer set...

	# Calculate the embedding of the query
	emb_query = get_embedding(query)
	
	# Define a dictionary to hold paper info, max cosine similarity score, and the component which was highest
	dict_paper_cos = []
	
	# Retrieve the TOUs for all the papers
	all_papertou = PaperTOU.objects.all()
	for paper in all_papertou:
		# Define the components of the TOU that will be used for comparison		
		tou_components = {
			"Title" : paper.metadata.title, 
			"Abstract" : paper.metadata.abstract, 
			"Keywords" : paper.metadata.keywords, 
			"Overview" : paper.overview, 
			"Critical Concepts" : paper.critical_concepts, 
			"Domain / Task / Problem" : paper.domain_task_problem, 
			"Motivations / Priorities" : paper.motivations_priorities, 
			"Evaluation Metrics" : paper.eval_metrics, 
			"Approach" : paper.approach, 
			"Results" : paper.results, 
			"Future Work" : paper.future_work
		}
		# Load embedding data
		tou_embeddings = {
			"Title" : pickle.loads(paper.metadata.title_emb),
			"Abstract" : pickle.loads(paper.metadata.abstract_emb), 
			"Keywords" : pickle.loads(paper.metadata.keywords_emb), 
			"Overview" : pickle.loads(paper.overview_emb), 
			"Critical Concepts" : pickle.loads(paper.critical_concepts_emb), 
			"Domain / Task / Problem" : pickle.loads(paper.domain_task_problem_emb), 
			"Motivations / Priorities" : pickle.loads(paper.motivations_priorities_emb), 
			"Evaluation Metrics" : pickle.loads(paper.eval_metrics_emb), 
			"Approach" : pickle.loads(paper.approach_emb), 
			"Results" : pickle.loads(paper.results_emb), 
			"Future Work" : pickle.loads(paper.future_work_emb)
		}

		# Create dictionary to store the cosine similarity values for each component of the TOU
		tou_cosine_sim = {}
		
		# Calculate cosine similarity between the query and each component of the TOU
		for key, value in tou_components.items():
			# Set cosine_sim to zero, in case the item is empty
			cosine_sim = 0
			# Make sure there is data in the field to compare to, else ignore
			if value != "":
				# Get cosine similarity to query from the embedding of the TOU component
				cosine_sim = cosine_similarity(tou_embeddings[key], emb_query)[0][0]
			# Store the value in the cosine_sim dictionary
			tou_cosine_sim[key] = cosine_sim
		
		# Find the key-value pair with the maximum value
		max_pair = max(tou_cosine_sim.items(), key=lambda x: x[1])

		# Max_pair is a tuple containing the key and value of the maximum cosine similarity
		max_key, max_val = max_pair
		
		# Make a JSON item that holds the max key and value, and then the full set of TOU items in order
		paper_dict = {}
		paper_dict["max_key"] = max_key
		paper_dict["max_val"] = float(max_val)
		paper_dict["tou"] = tou_components
		
		for key, value in tou_cosine_sim.items():
			paper_dict[key] = float(value)
		
		dict_paper_cos.append(paper_dict)
	
	# Return all the paperTOUs in order of cosine similarity with context
	# Include the maximum TOU component and cos score, and all components in order of TOU, with cos scores
	return json.dumps(dict_paper_cos)