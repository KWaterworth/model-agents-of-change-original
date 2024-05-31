import os
import sys
import django

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

# Define a function to list all objects for each model
def list_all_objects(models):
    for model in models:
        print(f"\n\nModel: {model.__name__}\n")
        all_objects = model.objects.all()
        for obj in all_objects:
            print(f"Object ID: {obj.id}")
            for field, value in obj.__dict__.items():
                if not field.startswith('_') and not field.startswith('id'):  # Exclude internal fields and id, since already printed
                    print(f"{field}: \n{value}\n")
            print()

# List all objects for the specified models
list_all_objects([PaperSourceTOU, Person, ResearchInstitution, PaperMetaData, PaperMetaDataAuthors, PaperMetaDataInstitutions, PaperTOU])
