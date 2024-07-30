from django.core.management.base import BaseCommand, CommandError
from qpdnd.models import License
import requests
import json



class Command(BaseCommand):
    help = 'Import licenses data'

    def handle(self, *args, **options):

        # start to import data
        self.stdout.write(self.style.SUCCESS('Start license import from github.'))

        response = requests.get('https://api.github.com/licenses',
                                headers={'Accept': 'application/vnd.github.v3+json'})

        jres = json.loads(response.content)

        for l in jres:
            License.objects.get_or_create(**l)


        self.stdout.write(self.style.SUCCESS('End import.'))
