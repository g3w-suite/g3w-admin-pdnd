# coding=utf-8
""""
    Test comme for run tasks
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-11-24 15:14:25'
__copyright__ = 'Copyright Gis3w'


from django.core.management.base import BaseCommand, CommandError
from qpdnd.tasks import send_anncsu_pdnd_task

class Command(BaseCommand):
    help = 'Run huey tasks'

    def handle(self, *args, **options):

        # start to import data
        self.stdout.write(self.style.SUCCESS('Start run test Huey task'))

        task = send_anncsu_pdnd_task(1)

        self.stdout.write(self.style.SUCCESS('Task strarted: %s' % task.id))