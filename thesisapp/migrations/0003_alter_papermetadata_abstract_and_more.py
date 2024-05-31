# Generated by Django 4.2.11 on 2024-04-28 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesisapp', '0002_papermetadata_papermetadataauthors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='papermetadata',
            name='abstract',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papermetadata',
            name='keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papermetadata',
            name='month',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='papermetadata',
            name='year',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='approach',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='critical_concepts',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='domain_task_problem',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='eval_metrics',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='future_work',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='motivations_priorities',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='overview',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='papertou',
            name='results',
            field=models.TextField(blank=True),
        ),
    ]