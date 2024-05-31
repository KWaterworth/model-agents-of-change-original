import os
import sys
import json
import django
from django.conf import settings
from transformers import BertModel, BertTokenizer
import torch
import pickle

# Set the path to your Django project directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis.settings')

# Add the project directory to the Python path
sys.path.append(PROJECT_DIR)

# Initialize Django
django.setup()

from thesisapp.serializers import PaperMetaDataSerializer, PersonSerializer, ResearchInstitutionSerializer, PaperTOUSerializer, PaperSourceTOUSerializer

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



# Initialize Model
initialize_model()

# Define function to calculate embedding and serialize it for database insertion
def get_embedding(string):
	global model, tokenizer
	inputs = tokenizer(string, return_tensors="pt", max_length=512, truncation=True)
	outputs = model(**inputs)
	embeddings = torch.mean(outputs.last_hidden_state, dim=1)
	serialized_embedding = pickle.dumps(embeddings.detach().numpy())
	# embedding_size_bytes = len(serialized_embedding)
	# print("Size of serialized embedding:", embedding_size_bytes, "bytes")
	return serialized_embedding

# Delete all data in the tables so it can be updated
def delete_all_data():
	PaperSourceTOU.objects.all().delete()
	Person.objects.all().delete()
	ResearchInstitution.objects.all().delete()
	PaperMetaData.objects.all().delete()
	PaperMetaDataAuthors.objects.all().delete()
	PaperMetaDataInstitutions.objects.all().delete()
	PaperTOU.objects.all().delete()

# Call the function to delete all data
delete_all_data()

# Define the path to the JSON file
file_path = os.path.join(settings.BASE_DIR, 'database_management/paperTOUs.json')

# Load JSON data
with open(file_path, 'r', encoding='utf-8') as file:
	json_data = json.load(file)

# Deserialize and add data to the database
for item in json_data:
	# Deserialize PaperMetaData
	metadata_serializer = PaperMetaDataSerializer(data=item['metadata'])
	if metadata_serializer.is_valid():
		# Calculate embeddings for title and abstract
		title_embedding = get_embedding(item['metadata']['title'])
		abstract_embedding = get_embedding(item['metadata']['abstract'])
		keywords_embedding = get_embedding(item['metadata']['keywords'])

		# Save PaperMetaData with embeddings
		metadata_instance = metadata_serializer.save(
			title_emb=title_embedding,
			abstract_emb=abstract_embedding,
			keywords_emb=keywords_embedding
		)

		# Deserialize and add authors
		for author_data in item['metadata']['authors']:
			author_serializer = PersonSerializer(data=author_data)
			if author_serializer.is_valid():
				author_instance = author_serializer.save()
				PaperMetaDataAuthors.objects.create(metadata=metadata_instance, author=author_instance)

		# Deserialize and add institutions
		for institution_data in item['metadata']['institutions']:
			institution_serializer = ResearchInstitutionSerializer(data=institution_data)
			if institution_serializer.is_valid():
				institution_instance = institution_serializer.save()
				PaperMetaDataInstitutions.objects.create(metadata=metadata_instance, institution=institution_instance)

		# Generate and store the embedding
		embedding = get_embedding(item['metadata']['title'])
		metadata_instance.embedding = embedding
		metadata_instance.save()

		# Deserialize and add PaperTOU
		tou_serializer = PaperTOUSerializer(data=item)
		if tou_serializer.is_valid():
			# Calculate embeddings for PaperTOU fields
			overview_embedding = get_embedding(item['overview'])
			critical_concepts_embedding = get_embedding(item['critical_concepts'])
			domain_task_problem_embedding = get_embedding(item['domain_task_problem'])
			motivations_priorities_embedding = get_embedding(item['motivations_priorities'])
			eval_metrics_embedding = get_embedding(item['eval_metrics'])
			approach_embedding = get_embedding(item['approach'])
			results_embedding = get_embedding(item['results'])
			future_work_embedding = get_embedding(item['future_work'])

			# Save PaperTOU with embeddings
			tou_instance = tou_serializer.save(
				metadata=metadata_instance,
				overview_emb=overview_embedding,
				critical_concepts_emb=critical_concepts_embedding,
				domain_task_problem_emb = domain_task_problem_embedding,
				motivations_priorities_emb = motivations_priorities_embedding,
				eval_metrics_emb=eval_metrics_embedding,
				approach_emb=approach_embedding,
				results_emb=results_embedding,
				future_work_emb=future_work_embedding
			)

		# Deserialize and add PaperSourceTOU
		source_tou_serializer = PaperSourceTOUSerializer(data=item)
		if source_tou_serializer.is_valid():
			source_tou_serializer.save(tou_id=tou_serializer.data['id'])

	else:
		print("Error in deserializing PaperMetaData:", metadata_serializer.errors)