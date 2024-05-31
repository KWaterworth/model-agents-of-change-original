from django.db import models

class Person(models.Model):
	name = models.CharField(max_length=100)

class ResearchInstitution(models.Model):
	name = models.CharField(max_length=200)

class PaperMetaData(models.Model):
	title = models.CharField(max_length=250)
	title_emb = models.BinaryField(blank=True, max_length=1000000)
	year = models.IntegerField(blank=True)
	month = models.IntegerField(blank=True)
	abstract = models.TextField(blank=True)
	abstract_emb = models.BinaryField(blank=True, max_length=1000000)
	keywords = models.TextField(blank=True)
	keywords_emb = models.BinaryField(blank=True, max_length=1000000)

class PaperMetaDataAuthors(models.Model):
	metadata = models.ForeignKey(PaperMetaData, on_delete=models.CASCADE)
	author = models.ForeignKey(Person, on_delete=models.CASCADE)

class PaperMetaDataInstitutions(models.Model):
	metadata = models.ForeignKey(PaperMetaData, on_delete=models.CASCADE)
	institution = models.ForeignKey(ResearchInstitution, on_delete=models.CASCADE)

class PaperTOU(models.Model):
	metadata = models.ForeignKey(PaperMetaData, on_delete=models.CASCADE)
	overview = models.TextField(blank=True)
	overview_emb = models.BinaryField(blank=True, max_length=1000000)
	critical_concepts = models.TextField(blank=True)
	critical_concepts_emb = models.BinaryField(blank=True, max_length=1000000)
	domain_task_problem = models.TextField(blank=True)
	domain_task_problem_emb = models.BinaryField(blank=True, max_length=2000000)
	motivations_priorities = models.TextField(blank=True)
	motivations_priorities_emb = models.BinaryField(blank=True, max_length=1000000)
	eval_metrics = models.TextField(blank=True)
	eval_metrics_emb = models.BinaryField(blank=True, max_length=1000000)
	approach = models.TextField(blank=True)
	approach_emb = models.BinaryField(blank=True, max_length=1000000)
	results = models.TextField(blank=True)
	results_emb = models.BinaryField(blank=True, max_length=1000000)
	future_work = models.TextField(blank=True)
	future_work_emb = models.BinaryField(blank=True, max_length=1000000)

class PaperSourceTOU(models.Model):
	title = models.CharField(max_length=250)
	file = models.CharField(max_length=150)
	url = models.CharField(max_length=255)
	tou = models.ForeignKey(PaperTOU, on_delete=models.CASCADE)