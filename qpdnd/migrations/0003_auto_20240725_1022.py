# Generated by Django 3.2.25 on 2024-07-25 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qpdnd', '0002_qpdndlayer_endpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='qpdndproject',
            name='endpoint',
            field=models.CharField(default='', help_text='Select API endpoint for PDND layer. must be unique', max_length=255, unique=True),
        ),
        migrations.DeleteModel(
            name='QPDNDLayer',
        ),
    ]
