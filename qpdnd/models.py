# coding=utf-8
"""" QPDND administration modules
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-22'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from qdjango.models import Project, Layer


class QPDNDProject(models.Model):
    """ Projects to expose """

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="%(app_label)s_projects")

    endpoint = models.CharField(max_length=255, null=False, blank=False,
                                help_text=_('Select API endpoint for PDND layer. must be unique'),
                                unique=True, default='')

    note = models.TextField('Note', null=True, blank=True)

    def layers(self):
        """
        Return a list of all layers exposed
        """

        return self.qpdnd_layer.all()



    # TODO: add check i WFS service is active

    class Meta:
        verbose_name = 'PDND Project'


