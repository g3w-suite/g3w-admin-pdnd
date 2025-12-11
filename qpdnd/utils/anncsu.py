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
from qpdnd.settings import (
    _ANNCSU_SENDED_STATUS,
    _ANNCSU_ERROR_STATUS
)

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


    def __init__(self, anncsu_project, send_type, process_info=None):
        """ 
        Constructor 
        :param anncsu_project: ANNCSUProject instance
        :param process_info: huey_monitor.ProcessInfo instance
        """

        self.anncsu_project = anncsu_project
        self.send_type = send_type
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
        print(self.send_type)
        features = self.anncsu_project.get_features(self.send_type)

        findex = 0
        while findex < len(features):

            feature = features[findex]               
            # Here would be the logic to send each feature to the PDND API
            try:
                # Inform progress also for not good features
                if self.process_info:
                    self.process_info.update(n=1)

                # Try to check signal interruption(revoked) to exit
                # ==================================================
                if self.task_model:
                
                    # reload from db
                    self.task_model.refresh_from_db()
                    if self.task_model.state.signal_name == signals.SIGNAL_REVOKED:
                        logger.info(f"Task {self.task_model.task_id} revoked. Stopping feature sending.")
                        findex = len(features)
                        break

                self.send_feature(feature)

                # Update results
                self.results['success'] += 1
                qgis_layer.dataProvider().changeAttributeValues({
                    feature.id(): {
                        fmapping[settings.ANNCSU_FIELD_STATO_INVIO]: _ANNCSU_SENDED_STATUS, 
                        fmapping[settings.ANNCSU_FIELD_DATA_INVIO]: send_date,
                        #fmapping[settings.ANNCSU_FIELD_DIRTY]: False
                        }
                    })
                
            except HTTPError as http_err:    
                logger.error(f"HTTP error sending feature ID {feature.id()}: {http_err}")
                
                # Check if it's a specific error that requires waiting (e.g., 429 Too Many Requests or 503)
                # if http_err.response.status_code in [429, 503]:
                #     logger.warning(f"Rate limit or service unavailable error. Waiting until 1 AM next day.")
                    
                #     # Calculate wait time until 1 AM next day
                #     now = datetime.datetime.now()
                #     next_day_1am = (now + datetime.timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
                #     wait_seconds = (next_day_1am - now).total_seconds()
                    
                #     logger.info(f"Waiting {wait_seconds} seconds until {next_day_1am}")
                #     time.sleep(wait_seconds)
                    
                #     # Retry the same feature (don't increment findex)
                #     continue
                
                self._register_error(feature.id(), str(http_err))
                qgis_layer.dataProvider().changeAttributeValues({
                    feature.id(): {
                        fmapping[settings.ANNCSU_FIELD_STATO_INVIO]: _ANNCSU_ERROR_STATUS, 
                        fmapping[settings.ANNCSU_FIELD_DATA_INVIO]: send_date,
                        #fmapping[settings.ANNCSU_FIELD_DIRTY]: True
                        }
                    })
                
                

                continue

            except Exception as e:
                logger.error(f"Error sending feature ID {feature.id()}: {e}")
                self._register_error(feature.id(), str(e))
                qgis_layer.dataProvider().changeAttributeValues({
                    feature.id(): {
                        fmapping[settings.ANNCSU_FIELD_STATO_INVIO]: _ANNCSU_ERROR_STATUS, 
                        fmapping[settings.ANNCSU_FIELD_DATA_INVIO]: send_date,
                        #fmapping[settings.ANNCSU_FIELD_DIRTY]: True
                        }
                    })
                continue

            finally:
                
                # Check if we need to wait after reaching max requests per cycle
                # Examples of how this condition works:
                # If ANNCSU_MAX_REQUESTS_PER_CICLE = 0: condition is False, never waits
                # If ANNCSU_MAX_REQUESTS_PER_CICLE = 100 and findex = 99: (99+1) % 100 = 0, waits
                # If ANNCSU_MAX_REQUESTS_PER_CICLE = 50 and findex = 49: (49+1) % 50 = 0, waits
                if settings.ANNCSU_MAX_REQUESTS_PER_CICLE > 0 and (findex + 1) % settings.ANNCSU_MAX_REQUESTS_PER_CICLE == 0:
                    if settings.ANNCSU_REQUEST_TIME_INTERVAL == 'NEXT_DAY':
                        # Calculate wait time until 1 PM next day
                        now = datetime.datetime.now()
                        next_day_1am = (now + datetime.timedelta(days=1)).replace(hour=1, minute=0, second=0, microsecond=0)
                        wait_seconds = (next_day_1am - now).total_seconds()
                        
                        logger.info(f"Reached {settings.ANNCSU_MAX_REQUESTS_PER_CICLE} requests. Waiting {wait_seconds} seconds until {next_day_1am}")
                        time.sleep(wait_seconds)
                    else:
                        # Wait for specified seconds
                        logger.info(f"Reached {settings.ANNCSU_MAX_REQUESTS_PER_CICLE} requests. Waiting {settings.ANNCSU_REQUEST_TIME_INTERVAL} seconds")
                        time.sleep(settings.ANNCSU_REQUEST_TIME_INTERVAL)


                findex += 1

        return self.results
    
    def send_feature(self, feature):
        """
        Send a single feature to PDND API.
        :param feature: QGIS feature
        """
        # Instance Pydantic mode vor validation
        pdata = self.model(**self._mapping_feature_to_pdnd(feature))

        # Prepare authentication
        # If is set govway_username and govway_password in anncsu_project, use them
        if self.anncsu_project.govway_username and self.anncsu_project.govway_password:
            auth = HTTPBasicAuth(self.anncsu_project.govway_username, self.anncsu_project.govway_password)
        else:       
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

    def __init__(self, anncsu_project, send_type, process_info=None, **kwargs):
        
        super().__init__(anncsu_project, send_type, process_info, **kwargs)

        # Set specific API URL
        self.api_url = self.anncsu_project.govway_api_endpoint

    def _mapping_feature_to_pdnd(self, feature):

        try:
            z = str(feature[settings.ANNCSU_FIELD_QUOTA])
        except:
            z = '0'

        # Cut to max 16 length

        # Truncate coordinates to max 12 characters total (including decimal point)
        # Truncate coordinates ensuring proper decimal precision
        x_str = f"{float(feature[settings.ANNCSU_FIELD_LON]):.8f}"[:12]
        y_str = f"{float(feature[settings.ANNCSU_FIELD_LAT]):.8f}"[:12]
        z_str = z[:12]
        
        toret = {
            'codcom': self.anncsu_project.codice_comune.codice_catastale_del_comune,
            'progr_civico': str(int(feature[settings.ANNCSU_FIELD_PROGR])),
            'coordinate': {
                'x': x_str,
                'y': y_str,
                'z': z_str,
                'metodo': '3'
            }
        }

        return toret
