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
from core.utils.qgisapi import get_qgis_features
from qpdnd.api.models import Accesso

from requests.exceptions import HTTPError
import requests


class ANNCSUPDNDAPI(object):
    """
    ANNCSU PDND API utils class.
    This is a abstract class to be extended for specific PDND data types.
    """

    model = None
    api_url = None
    results = {
        'success': 0,
        'failed': 0
    }


    def __init__(self, anncsu_project, process_info=None):
        """ 
        Constructor 
        :param anncsu_project: ANNCSUProject instance
        :param process_info: huey_monitor.ProcessInfo instance
        """
        print('passato init anncsu')
        self.anncsu_project = anncsu_project
        self.process_info = process_info
        print('pre project anncsu')
        #self.qgs_layer = self.anncsu_project.layer.qgis_layer
        print('fine init anncsu')


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

    def send_features(self):
        """
        Send ANNCSU features to PDND API.
        """

        print('passato send_features')
        
        features = self.anncsu_project.get_features()
        for feature in features:
            
            # Here would be the logic to send each feature to the PDND API
            try:
                # Inform progress also for not good features
                if self.process_info:
                    self.process_info.update(n=1)

                self.send_feature(feature)
                
            except HTTPError as http_err:    
                print(f"HTTP error sending feature ID {feature.id()}: {http_err}")
                continue
            except Exception as e:
                print(f"Error sending feature ID {feature.id()}: {e}")
                continue

        return True
    
    def send_feature(self, feature):
        """
        Send a single feature to PDND API.
        :param feature: QGIS feature
        """
        # Instance Pydantic mode vor validation
        pdata = self.model(**self._mapping_feature_to_pdnd(feature))

        # Prepare authentication
        auth = (settings.ANNCSU_GOVWAY_API_USER, settings.ANNCSU_GOVWAY_API_PASSWORD)

        return {}
        
        # Send POST request with basic authentication
        response = requests.post(
            self.api_url,
            json={
                'richiesta': pdata.model_dump()
            },
            auth=auth
        )
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
                'progr_civico': str(feature['progr_nazionale_ac']),
                'coordinate': {
                    'x': str(feature['longitudine']),
                    'y': str(feature['latitudine']),
                    'z': z,
                    'metodo': '3'
                }
        }

        return toret
