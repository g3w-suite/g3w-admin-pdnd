# coding=utf-8
""""
Utils classes and functions for ANNCSU PDND
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-11-19 12:44:23'
__copyright__ = 'Copyright Gis3w'

from django.conf import settings
from huey import signals
from huey_monitor.models import TaskModel
from core.utils.qgisapi import get_qgis_features
from qpdnd.api.models import Accesso

from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import requests
import datetime
import time


import logging

logger = logging.getLogger('qdpnd.anncsu')


class ANNCSUPDNDAPI(object):
    """
    ANNCSU PDND API utils class.
    This is a abstract class to be extended for specific PDND data types.
    """

    model = None
    api_url = None


    def __init__(self, anncsu_project, process_info=None):
        """ 
        Constructor 
        :param anncsu_project: ANNCSUProject instance
        :param process_info: huey_monitor.ProcessInfo instance
        """

        self.anncsu_project = anncsu_project
        self.process_info = process_info

        # Set TaskModel if exists
        self.task_model = None
        if self.process_info:
            self.task_model = TaskModel.objects.get(task_id=self.process_info.task.id)

        # Reset results
        self.results = {
            'success': 0,
            'failed': 0,
            'errors': {}
        }


    def _mapping_feature_to_pdnd(self, feature):
        """
        Map QGIS feature to PDND data structure.
        :param feature: QGIS feature
        :return: dict with mapped data
        """
        # Here would be the mapping logic
        #---------------------------
        # To implement in subclasses
        #---------------------------
        data = {
            # 'field1': feature['qgis_field1'],
            # 'field2': feature['qgis_field2'],
        }
        return data
    
    def _register_error(self, feature_id, error_msg):
        """
        Register an error for a feature.
        :param feature_id: ID of the feature
        :param error_msg: Error message
        """
        self.results['failed'] += 1
        self.results['errors'][feature_id] = error_msg

    def _layer_fields_mapping(self, qgis_layer):
        """
        Get the mapping of layer fields tby index fiels.
        :return: dict with field mappings
        """
        mapping = {}
        for qgis_field in qgis_layer.fields():
                mapping[qgis_field.name()] = qgis_layer.fields().indexFromName(qgis_field.name())
        return mapping

    def send_features(self):
        """
        Send ANNCSU features to PDND API.
        """

        # Get fields mapping
        qgis_layer = self.anncsu_project.layer.qgis_layer
        fmapping = self._layer_fields_mapping(qgis_layer)
        send_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        features = self.anncsu_project.get_features()
        for feature in features:
            
            # Here would be the logic to send each feature to the PDND API
            try:
                # Inform progress also for not good features
                if self.process_info:
                    self.process_info.update(n=1)

                # Try to check signal interruption(revoked) to exit
                if self.task_model:
                
                    # reload from db
                    self.task_model.refresh_from_db()
                    if self.task_model.state.signal_name == signals.SIGNAL_REVOKED:
                        logger.info(f"Task {self.task_model.task_id} revoked. Stopping feature sending.")
                        break

                self.send_feature(feature)

                # Update results
                self.results['success'] += 1
                qgis_layer.dataProvider().changeAttributeValues({feature.id(): {fmapping['stato_invio']: 'INVIATO', fmapping['data_invio']: send_date}})
                
            except HTTPError as http_err:    
                logger.error(f"HTTP error sending feature ID {feature.id()}: {http_err}")
                self._register_error(feature.id(), str(http_err))
                qgis_layer.dataProvider().changeAttributeValues({feature.id(): {fmapping['stato_invio']: 'ERRORE', fmapping['data_invio']: send_date}})
                continue
            except Exception as e:
                logger.error(f"Error sending feature ID {feature.id()}: {e}")
                self._register_error(feature.id(), str(e))
                qgis_layer.dataProvider().changeAttributeValues({feature.id(): {fmapping['stato_invio']: 'ERRORE', fmapping['data_invio']: send_date}})
                continue

        return self.results
    
    def send_feature(self, feature):
        """
        Send a single feature to PDND API.
        :param feature: QGIS feature
        """
        # Instance Pydantic mode vor validation
        pdata = self.model(**self._mapping_feature_to_pdnd(feature))

        # Prepare authentication
        auth = HTTPBasicAuth(settings.ANNCSU_GOVWAY_API_USER, settings.ANNCSU_GOVWAY_API_PASSWORD)


        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Send POST request with basic authentication
        data = {
                'richiesta': {
                    'accesso': pdata.dict()
                }
            }
        
        time.sleep(3)  # To avoid overwhelming the API
        
        return data
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            auth=auth
        )
        logger.debug(f"[ANNCSU gestioneaccessi] - {response.json()}")
        response.raise_for_status()
        
        
        return response.json()



class ANNCSUPDND_GestioneCoordinate_API(ANNCSUPDNDAPI):
    """
    ANNCSU PDND Gestione Coordinate API utils class.
    """

    model = Accesso

    def __init__(self, anncsu_project, process_info=None):
        
        super().__init__(anncsu_project, process_info)

        # Set specific API URL
        self.api_url = self.anncsu_project.govway_api_endpoint

    def _mapping_feature_to_pdnd(self, feature):

        try:
            z = feature['quota']
        except:
            z = '0'

        toret = {
                'codcom': self.anncsu_project.codice_comune.codice_catastale_del_comune,
                'progr_civico': str(int(feature['indirizzario_id'])),
                'coordinate': {
                    'x': str(feature['longitudine']),
                    'y': str(feature['latitudine']),
                    'z': z,
                    'metodo': '3'
                }
        }

        return toret
