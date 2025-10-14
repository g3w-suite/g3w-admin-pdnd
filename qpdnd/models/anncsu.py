# coding=utf-8
""""
    Models for ANNCSU PDND extension
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-10-10 15:53:19'
__copyright__ = 'Copyright Gis3w'


from django.db import models
from django.core.exceptions import ValidationError


class ANNCSUProject(models.Model):
    """ Projects to expose with ANNCSU PDND extension """

    project = models.OneToOneField('qdjango.Project', on_delete=models.CASCADE, related_name="%(app_label)s_anncsu_projects")

    layer = models.ForeignKey('qdjango.Layer', models.CASCADE, related_name="%(app_label)s_anncsu_layers_related")
    note = models.TextField(blank=True, null=True, help_text="Optional note for the configuration.")

    def clean(self):

        # Ensure that the selected layer belongs to the selected project
        if self.layer.project != self.project:
            raise ValidationError({'layer': 'The selected layer does not belong to the selected project.'})


    def __str__(self):
        return f'ANNCSU PDND Project: {self.project.name}'