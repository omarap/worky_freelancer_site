# Generated by Django 3.1.5 on 2021-02-27 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_project_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='company',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='project',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
