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
from django.utils.translation import gettext_lazy as _
from huey.contrib.djhuey import HUEY
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from core.utils.qgisapi import get_qgis_features
from model_utils import Choices
from qgis.core import QgsSettings



class IstatCodiciUi(models.Model):
    codice_regione = models.CharField(max_length=255, blank=True, null=True)
    codice_citta_metropolitana = models.CharField(max_length=255, blank=True, null=True)
    codice_provincia_1 = models.CharField(max_length=255, blank=True, null=True)
    progressivo_del_comune_2 = models.CharField(max_length=255, blank=True, null=True)
    codice_comune_formato_alfanumerico = models.CharField(max_length=255, blank=True, null=True)
    denominazione_in_italiano = models.CharField(max_length=255, blank=True, null=True)
    denominazione_in_tedesco = models.CharField(max_length=255, blank=True, null=True)
    codice_ripartizione_geografica = models.CharField(max_length=255, blank=True, null=True)
    ripartizione_geografica = models.CharField(max_length=255, blank=True, null=True)
    denominazione_regione = models.CharField(max_length=255, blank=True, null=True)
    denominazione_citta_metropolitana = models.CharField(max_length=255, blank=True, null=True)
    denominazione_provincia = models.CharField(max_length=255, blank=True, null=True)
    flag_comune_capoluogo_di_provincia = models.CharField(max_length=255, blank=True, null=True)
    sigla_automobilistica = models.CharField(max_length=255, blank=True, null=True)
    codice_comune_formato_numerico = models.CharField(primary_key=True, max_length=255)
    codice_comune_numerico_con_107_province_dal_2006_al_2009 = models.CharField(max_length=255, blank=True, null=True)
    codice_comune_numerico_con_103_province_dal_1995_al_2005 = models.CharField(max_length=255, blank=True, null=True)
    codice_catastale_del_comune = models.CharField(max_length=255, blank=True, null=True)
    popolazione_legale_2011_09_10_2011 = models.CharField(max_length=255, blank=True, null=True)
    codice_nuts1_2010 = models.CharField(max_length=255, blank=True, null=True)
    codice_nuts2_2010_3 = models.CharField(max_length=255, blank=True, null=True)
    codice_nuts3_2010 = models.CharField(max_length=255, blank=True, null=True)
    codice_nuts1_2006 = models.CharField(max_length=255, blank=True, null=True)
    codice_nuts2_2006_3 = models.CharField(max_length=255, blank=True, null=True)
    codice_nuts3_2006 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.codice_catastale_del_comune} - {self.denominazione_in_italiano}"

    class Meta:
        verbose_name_plural = 'ISTAT Codici UI'
        verbose_name = 'ISTAT Codici UI'

class ANNCSUProject(models.Model):
    """ Projects to expose with ANNCSU PDND extension """

    ENV_TYPE = Choices(
        ('prod', _('PRODUCTION')),
        ('test', _('TESTING'))
    )

    project = models.OneToOneField('qdjango.Project', on_delete=models.CASCADE, related_name="%(app_label)s_anncsu_projects")

    layer = models.ForeignKey('qdjango.Layer', models.CASCADE, related_name="%(app_label)s_anncsu_layers_related")

    codice_comune  = models.ForeignKey(IstatCodiciUi, help_text=_('Municipality code (ISTAT code).'), on_delete=models.DO_NOTHING, null=True, blank=False)
    
    env_type = models.CharField(max_length=10, choices=ENV_TYPE, default=ENV_TYPE.test)

    govway_api_endpoint = models.URLField(max_length=200, null=True, blank=False, help_text=_('GovWay API endpoint URL'))
    
    note = models.TextField(blank=True, null=True, help_text=_("Optional note for the configuration."))

    task_id = models.CharField(max_length=255, blank=True, null=True, help_text=_('Asynchronous task ID.'))

    def get_features(self):
        """
        Get QGIS features from the configured layer.
        :return: list of QGIS features"""
        return get_qgis_features(self.layer.qgis_layer)
    
    def get_task(self):
        """
        Get the associated task.
        :return: task instance or None
        """
        if self.task_id:
             # Get current status
            try:
                result = HUEY.result(self.task_id)
            except TaskException:
                result = None

            return TaskModel.objects.get(task_id=self.task_id)
        return None

    def clean(self):

        # Ensure that the selected layer belongs to the selected project

        if hasattr(self, 'layer') and self.layer.project != self.project:
            raise ValidationError({'layer': 'The selected layer does not belong to the selected project.'})


    def __str__(self):
        return f'ANNCSU PDND Project: {self.project}'