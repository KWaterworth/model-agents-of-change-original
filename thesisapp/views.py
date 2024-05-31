from django.shortcuts import render
from .models import PaperSourceTOU
from django.http import JsonResponse
import clingo
import json
import subprocess
import os
import re
from django.core.serializers import serialize
from .run_search import *

def index(request):
	return render(request, 'index.html')

def search_view(request):
	if request.method == 'GET' and 'question' in request.GET:
		# Get question from the AJAX request
		question = request.GET['question']
		# This is the meta model for now, get the results back here from embedding model-agent and send to ASP model-agent
		# In the future, this can have certain other functions, self evaluate, to tell when it's done, and can decide to do other functions on the set based on the results of a feedback loop from a neural network which learns when to send it to white hat, red hat, etc...

		# Send the TOU to embedding model-agent and get results back
		embedding_results = compareTOUs(question)
		
		# Split the question into terms for the ASP program
		split_question = question.split()
		
		asp_question_string = ""
		
		for word in split_question:
			# Make sure not an empty string
			if re.sub(r'[^a-z0-9]', '', word.lower()) != "":
				asp_question_string += "keyword(" + re.sub(r'[^a-z0-9]', '', word.lower()) + ").\n"
		
		asp_files = ["asp_files/rules.lp"]
		
		results = json.loads(embedding_results)	
		for paper in results:
			# Reset the ASP program string for each new paper
			asp_program_string = ""

			# Split the title and abstract into words
			split_title = paper["tou"]["Title"].split()
			split_abstract = paper["tou"]["Abstract"].split()
			
			for word in split_title:
				# Make sure not an empty string
				if re.sub(r'[^a-z]', '', word.lower()) != "":
					asp_program_string += "metadata_title_word(" + re.sub(r'[^a-z]', '', word.lower()) + ").\n"
			
			for word in split_abstract:
				# Make sure not an empty string
				if re.sub(r'[^a-z0-9]', '', word.lower()) != "":
					asp_program_string += "metadata_abstract_word(" + re.sub(r'[^a-z0-9]', '', word.lower()) + ").\n"

			# Add the question string to the data from each paper
			asp_program_string = asp_question_string + asp_program_string
			asp_results = solve_problem(asp_files, asp_program_string)
			asp_score = int(asp_results[0].replace("score", "").replace("(", "").replace(")", ""))

			# Pull maximum semantic embedding value for calculation
			sem_emb = paper["max_val"]

			# Calculate total ranking number for later sorting
			total_ranking = 2.0 * 10 * sem_emb + 0.2 * asp_score
			paper["total_ranking"] = total_ranking
		
		sorted_results = sorted(results, key=lambda x: x['total_ranking'], reverse = True)
		return JsonResponse({'question': question, 'results': sorted_results})
	else:
		return JsonResponse({'error': 'Invalid request'})

# Runs ASP program and returns string of answer sets
def solve_problem(asp_files, asp_program_string):
	# Get the current directory and then change it to local
	current_directory = os.getcwd()
	script_dir = os.path.dirname(os.path.abspath(__file__))
	os.chdir(script_dir)	
	
	# Check whether they open - only used in debug
	for asp_file in asp_files:
		try:
			with open(asp_file):
				# print(f"File found : {asp_file}")
				pass  # File exists, do nothing
		except FileNotFoundError:
			print(f"File not found: {asp_file}")
	
	# Create a Control object
	ctl = clingo.Control()

	# Load the .lp files
	for asp_file in asp_files:
		ctl.load(asp_file)
	ctl.add("base", [], asp_program_string)

	# Ground the program
	ctl.ground([("base", [])])

	# Solve and save results as string
	models = []
	with ctl.solve(yield_=True) as handle:
		for model in handle:
			models.append(str(model))
	
	# Change the directory back
	os.chdir(current_directory)
	return models