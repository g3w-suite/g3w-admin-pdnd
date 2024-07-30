# Generated by Django 3.2.25 on 2024-07-26 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qpdnd', '0004_qpdndproject_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='qpdndproject',
            name='terms_of_service',
            field=models.CharField(help_text='Set an url where to find the terms fo service. I.e.: https://smartbear.com/terms-of-use/', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='qpdndproject',
            name='version',
            field=models.CharField(default='1.0.0', help_text='Indicate a version for the API to expose. I.e.: 1.0.0', max_length=255, null=True),
        ),
    ]
