# coding=utf-8
""""
    Models for ANNCSU PDND extension
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-10-10 15:53:19'
__copyright__ = 'Copyright Gis3w'


import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from huey.contrib.djhuey import HUEY
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from core.mixins.models import G3WACLModelMixins
from core.utils.qgisapi import get_qgis_features
from usersmanage.utils import setPermissionUserObject
from usersmanage.models import (
    User, 
    Group as AuthGroup
)
from qpdnd.settings import (
    _ANNCSU_SENDED_STATUS, 
    _ANNCSU_ERROR_STATUS
)
from model_utils import Choices
from qgis.core import (
    QgsSettings, 
    QgsFeatureRequest
)





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



class ANNCSUProject(G3WACLModelMixins, models.Model):
    """ Projects to expose with ANNCSU PDND extension """

    ENV_TYPE = Choices(
        ('prod', _('PRODUCTION')),
        ('test', _('TESTING'))
    )

    API_TYPE = Choices(
        ('aggcoord', 'AGGIORNAMENTO COORDINATE'),
        ('aggacc', 'AGGIORNAMENTO ACCESSI'),
        ('conscom', 'CONSULTAZIONE COMUNI')
    )

    api_type = models.CharField(max_length=10, choices=API_TYPE, default=API_TYPE.aggcoord)

    project = models.ForeignKey('qdjango.Project', on_delete=models.CASCADE, related_name="%(app_label)s_anncsu_projects")

    layer = models.ForeignKey('qdjango.Layer', models.CASCADE, related_name="%(app_label)s_anncsu_layers_related")

    codice_comune  = models.ForeignKey(IstatCodiciUi, help_text=_('Municipality code (ISTAT code).'), on_delete=models.DO_NOTHING, null=True, blank=False)
    
    env_type = models.CharField(max_length=10, choices=ENV_TYPE, default=ENV_TYPE.test)

    govway_api_endpoint = models.URLField(max_length=200, null=True, blank=False, help_text=_('GovWay API endpoint URL'))
    
    note = models.TextField(blank=True, null=True, help_text=_("Optional note for the configuration."))

    task_id = models.CharField(max_length=255, blank=True, null=True, help_text=_('Asynchronous task ID.'))

    ## Add user/password for GOVWAY authentication if needed
    govway_username = models.CharField(max_length=255, blank=True, null=True, help_text=_('GovWay API username'))

    govway_password = models.CharField(max_length=255, blank=True, null=True, help_text=_('GovWay API password'))

    results = models.JSONField(blank=True, null=True, help_text=_('Field to store results of the API call or error messages.'))


    class Meta:
        permissions = (
            ('send_to_pdnd', 'Can send features to PDND API'),
        )

    def get_features(self, send_type=None):
        """
        Get QGIS features from the configured layer.
        :param send_type: optional send type to filter features, can be 'dirty', 'error', 'dirty-error', 'not-sent', 'sent'
        :return: list of QGIS features"""

        qlayer  = self.layer.qgis_layer
        
        if send_type == 'error':
            expression = f"\"{settings.ANNCSU_FIELD_STATO_INVIO}\" = '{_ANNCSU_ERROR_STATUS}'"
        elif send_type == 'sent':
            expression = f"\"{settings.ANNCSU_FIELD_STATO_INVIO}\" = '{_ANNCSU_SENDED_STATUS}'"
        elif send_type == 'dirty':
            expression = f"\"{settings.ANNCSU_FIELD_DIRTY}\" IS True"
        elif send_type == 'dirty-error':
            expression = f"\"{settings.ANNCSU_FIELD_DIRTY}\" IS True OR \"{settings.ANNCSU_FIELD_STATO_INVIO}\" = '{_ANNCSU_ERROR_STATUS}'"
        elif send_type == 'not-sent':
            expression = f"\"{settings.ANNCSU_FIELD_STATO_INVIO}\" IS NULL OR \"{settings.ANNCSU_FIELD_STATO_INVIO}\" <> '{_ANNCSU_SENDED_STATUS}'"
        else:
            expression = 'ALL'

        if expression == 'ALL':
            features = get_qgis_features(qlayer)
        else:
            
            original_subset_string = qlayer.subsetString()

            qfr = QgsFeatureRequest()
            qfr.setFilterExpression(expression)
            features = get_qgis_features(self.layer.qgis_layer, qgis_feature_request=qfr)

            # Restore the original subset string and select no features
            qlayer.selectByIds([])
            qlayer.setSubsetString(original_subset_string)
        
        
        return features
    
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
    
    def get_task_status(self):
        """
        Get the status of the associated task.
        :return: task status or None
        """
        task = self.get_task()
        if task:
             # Get current status
            return task.state.signal_name
        return None
    
    def _permissionsToViewers(self, users_id, mode='add'):
        """
        Add/Remove guardian permissions to Viewers
        """

        for user_id in users_id:
            setPermissionUserObject(User.objects.get(pk=user_id), self,
                                    permissions=['view_anncsuproject', 'send_to_pdnd'], mode=mode)
            
    def _permissions_to_user_groups_viewer(self, groups_id, mode='add'):

        for group_id in groups_id:
            auth_group = AuthGroup.objects.get(pk=group_id)
            setPermissionUserObject(auth_group, self, permissions=['view_anncsuproject', 'send_to_pdnd'], mode=mode)

    
    @property
    def fenv_type(self):
        """Get human readable environment type."""

        return self.ENV_TYPE[self.env_type]

    @property
    def fapi_type(self):
        """Get human readable API type."""

        return self.API_TYPE[self.api_type]

    def clean(self):

        # Ensure that the selected layer belongs to the selected project

        if hasattr(self, 'layer') and self.layer.project != self.project:
            raise ValidationError({'layer': 'The selected layer does not belong to the selected project.'})


    def check_endpoint(self, timeout=10):
        """
        Verify that ``govway_api_endpoint`` is reachable.

        Performs a lightweight HTTP request and returns a dict with:
          - ok (bool): True only on a 2xx/3xx response
          - status_code (int|None)
          - reason (str): HTTP reason phrase or exception message
          - url (str): the endpoint that was probed
          - error (str|None): short error category ('connection', 'timeout',
            'ssl', 'http', 'exception', 'not_configured')
        """

        url = self.govway_api_endpoint
        result = {
            'ok': False,
            'status_code': None,
            'reason': '',
            'url': url,
            'error': None,
        }

        if not url:
            result['error'] = 'not_configured'
            result['reason'] = 'GovWay API endpoint not configured.'
            return result

        auth = None
        if self.govway_username and self.govway_password:
            auth = HTTPBasicAuth(self.govway_username, self.govway_password)

        try:
            # Empty POST: GovWay endpoints typically only accept POST.
            # An empty body will likely return 4xx (bad request) but proves
            # the endpoint is reachable; 5xx / connection errors signal a
            # real problem.
            response = requests.post(
                url,
                auth=auth,
                timeout=timeout,
                allow_redirects=True,
                json={},
            )

            result['status_code'] = response.status_code
            result['reason'] = response.reason or ''
            # Reachable if any response < 500 (4xx means endpoint answered).
            # 401/403 = auth issue, 400/404/422 = bad payload, all "reachable".
            if response.status_code < 500:
                result['ok'] = True
            else:
                result['error'] = 'http'
        except requests.exceptions.SSLError as e:
            result['error'] = 'ssl'
            result['reason'] = str(e)
        except requests.exceptions.ConnectTimeout:
            result['error'] = 'timeout'
            result['reason'] = 'Connection timeout.'
        except requests.exceptions.ReadTimeout:
            result['error'] = 'timeout'
            result['reason'] = 'Read timeout.'
        except requests.exceptions.ConnectionError as e:
            result['error'] = 'connection'
            result['reason'] = str(e)
        except Exception as e:
            result['error'] = 'exception'
            result['reason'] = f'{type(e).__name__}: {e}'

        return result


    def __str__(self):
        return f'ANNCSU PDND Project: {self.project}'