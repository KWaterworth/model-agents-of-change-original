from rest_framework import serializers
from .models import Person, ResearchInstitution, PaperMetaData, PaperMetaDataAuthors, PaperMetaDataInstitutions, PaperTOU, PaperSourceTOU

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name']

class ResearchInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchInstitution
        fields = ['id', 'name']

class PaperMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperMetaData
        fields = ['id', 'title', 'year', 'month', 'abstract', 'keywords']

class PaperMetaDataAuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperMetaDataAuthors
        fields = ['id', 'metadata', 'author']

class PaperMetaDataInstitutionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperMetaDataInstitutions
        fields = ['id', 'metadata', 'institution']

class PaperTOUSerializer(serializers.ModelSerializer):
    metadata = PaperMetaDataSerializer()

    class Meta:
        model = PaperTOU
        fields = ['id', 'metadata', 'overview', 'critical_concepts', 'domain_task_problem', 'motivations_priorities', 'eval_metrics', 'approach', 'results', 'future_work']

class PaperSourceTOUSerializer(serializers.ModelSerializer):
    tou = PaperTOUSerializer()

    class Meta:
        model = PaperSourceTOU
        fields = ['id', 'title', 'file', 'url', 'tou']