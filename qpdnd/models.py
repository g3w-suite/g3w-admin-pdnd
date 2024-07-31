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
import uuid

class License(models.Model):
    """
    Model contain information about licenses
    """

    key = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=400, null=False, blank=False)
    spdx_id = models.CharField(max_length=255, null=False, blank=False)
    url = models.URLField(max_length=1000, null=False, blank=False)
    node_id = models.CharField(max_length=1000, null=True, blank=False)

    def __str__(self):
        return self.name

class QPDNDProject(models.Model):
    """ Projects to expose """

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="%(app_label)s_projects")

    endpoint = models.CharField(max_length=255, null=False, blank=False,
                                help_text=_('Select API endpoint for PDND layer. must be unique'),
                                unique=True, default='')

    version = models.CharField(max_length=255, null=True, blank=False,
                               help_text=_('Indicate a version for the API to expose. I.e.: 1.0.0'),
                               default='1.0.0')

    terms_of_service = models.URLField(max_length=255, null=True, blank=False,
                               help_text=_('Set an url where to find the terms fo service. '
                                           'I.e.: https://smartbear.com/terms-of-use/'))

    contact_author = models.CharField(max_length=400, null=True, blank=False, help_text=_('Author of the service'))
    contact_email = models.EmailField(max_length=400, null=True, blank=False, help_text=_('Email reference'))
    contact_url = models.URLField(max_length=1000, null=True, blank=True, help_text=_('Contact URL reference'))

    title = models.CharField(max_length=400, null=True, blank=False, help_text=_('Title of the service'))
    description = models.TextField(null=True, blank=True, help_text=_('Description of the project'))

    x_summary = models.CharField(max_length=400, null=True, blank=False,
                                 help_text=_('Used to specify a brief, one-liner description of your API: '
                                             'this is very useful for catalog purposes (eg. this can be shown as your '
                                             'API subtitle in catalogs and developer portals)'))

    license = models.ForeignKey(License, on_delete=models.SET_NULL, null=True, blank=True)

    x_api_id = models.CharField(max_length=36, null=True, blank=True)

    note = models.TextField('Note', null=True, blank=True)

    def layers(self):
        """
        Return a list of all layers exposed
        """

        return self.qpdnd_layer.all()

    def save(self, *args, **kwargs):

        # If is in adding state create a new uuid for x_api_d
        if self._state.adding:
            self.x_api_id = uuid.uuid4()
        else:
            current_instance = QPDNDProject.objects.get(pk=self.pk)
            if not current_instance.x_api_id:
                self.x_api_id = uuid.uuid4()
            else:
                self.x_api_id = current_instance.x_api_id

        super().save(*args, **kwargs)

    # TODO: add check i WFS service is active

    class Meta:
        verbose_name = 'PDND Project'
