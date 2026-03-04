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
from pydantic import ValidationError
from core.utils.qgisapi import get_qgis_features
from qpdnd.api.models import (
    AccessoGestioneCoordinate, 
    AccessoAggiornamentiAccessi,
    RichiestaGestioneCoordinate,
    RichiestaAggiornamentoAccessi, 
    Coordinate,
    TipoOperazione
)

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

logger = logging.getLogger('qpdnd.anncsu')


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
            'errors': {},
            'results': {}
        }

    def _is_numeric_string(self, value):
        """
        Check if a string value is numeric (integer or float).
        :param value: String value to check
        :return: True if numeric, False otherwise
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _get_coordinates(self, feature):

        try:
            z = str(feature[settings.ANNCSU_FIELD_QUOTA])
            
            # Validate that z is numeric
            if not self._is_numeric_string(z):
                raise ValueError(f"Field {settings.ANNCSU_FIELD_QUOTA} must be numeric, got: {z}")
            
        except:
            z = '0'

        # Cut to max 16 length

        # Truncate coordinates to max 12 characters total (including decimal point)
        # Truncate coordinates ensuring proper decimal precision
        try:
            x_str = f"{float(feature[settings.ANNCSU_FIELD_LON]):.8f}"[:12]
            y_str = f"{float(feature[settings.ANNCSU_FIELD_LAT]):.8f}"[:12]
            z_str = z[:12]
        except Exception as e:
            raise ValueError(f"Invalid coordinate values: lat={feature[settings.ANNCSU_FIELD_LAT]}, lon={feature[settings.ANNCSU_FIELD_LON]}, quota={z}. Exception: {e}")   

        return Coordinate(**{
                'x': x_str,
                'y': y_str,
                'z': z_str,
                'metodo': '3'
            })


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

    def _register_success(self, feature_id, success_msg):
        """
        Register a success for a feature.
        :param feature_id: ID of the feature
        :param success_msg: Success message
        """
        self.results['success'] += 1
        self.results['results'][feature_id] = success_msg

    def _layer_fields_mapping(self, qgis_layer):
        """
        Get the mapping of layer fields tby index fiels.
        :return: dict with field mappings
        """
        mapping = {}
        for qgis_field in qgis_layer.fields():
                mapping[qgis_field.name()] = qgis_layer.fields().indexFromName(qgis_field.name())
        return mapping
    
    def _fields_to_update(self, feature, res,fmapping=None):
        """
        Get the fields to update in QGIS layer after sending to API.
        :param res: API response
        :return: dict with field names and values to update
        """
        return {}

    def send_features(self):
        """
        Send ANNCSU features to PDND API.
        """

        # Get fields mapping
        qgis_layer = self.anncsu_project.layer.qgis_layer
        fmapping = self._layer_fields_mapping(qgis_layer)
        send_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

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

                res = self.send_feature(feature)

                logger.debug(f"Feature ID {feature.id()} sent successfully. Response: {res}")

                # Update fields in QGIS layer to mark as sent
                # first specific for ANNCSU API TYPE
                ftoupdate = self._fields_to_update(feature, res, fmapping)
                ftoupdate.update({
                        fmapping[settings.ANNCSU_FIELD_STATO_INVIO]: _ANNCSU_SENDED_STATUS, 
                        fmapping[settings.ANNCSU_FIELD_DATA_INVIO]: send_date,
                        fmapping[settings.ANNCSU_FIELD_DIRTY]: False
                    })

                qgis_layer.dataProvider().changeAttributeValues({
                    feature.id(): ftoupdate
                    })
                
                # Update results
                self._register_success(feature.id(), res)
                
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
                
                self._register_error(feature.id(), f"Status code: {http_err.response.status_code}: {http_err.response.text}")
                qgis_layer.dataProvider().changeAttributeValues({
                    feature.id(): {
                        fmapping[settings.ANNCSU_FIELD_STATO_INVIO]: _ANNCSU_ERROR_STATUS, 
                        fmapping[settings.ANNCSU_FIELD_DATA_INVIO]: send_date,
                        fmapping[settings.ANNCSU_FIELD_DIRTY]: True
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
                        fmapping[settings.ANNCSU_FIELD_DIRTY]: True
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

        tosend = {
            'richiesta': pdata.model_dump(mode='json', exclude_none=True)
        }

        logger.debug(f"[ANNCSU] Data to send - {tosend}")
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=tosend,
            auth=auth
        )

        logger.debug(f"[ANNCSU] PDND response- {response.json()}")
        response.raise_for_status()
        
        
        return response.json()



class ANNCSUPDND_GestioneCoordinate_API(ANNCSUPDNDAPI):
    """
    ANNCSU PDND Gestione Coordinate API utils class.
    """

    model = RichiestaGestioneCoordinate

    def __init__(self, anncsu_project, send_type, process_info=None, **kwargs):
        
        super().__init__(anncsu_project, send_type, process_info, **kwargs)

        # Set specific API URL
        self.api_url = self.anncsu_project.govway_api_endpoint

    def _mapping_feature_to_pdnd(self, feature):
        
        accesso_data = {
            'codcom': self.anncsu_project.codice_comune.codice_catastale_del_comune,
            'progr_civico': str(int(feature[settings.ANNCSU_FIELD_PROGR])),
            'coordinate': self._get_coordinates(feature)
        }

        return {
            "accesso": AccessoGestioneCoordinate(**accesso_data)
        }


class ANNCSUPDND_AggiornamentoAccessi_API(ANNCSUPDNDAPI):
    """
    ANNCSU PDND Aggiornamento Accessi API utils class.
    """

    model = RichiestaAggiornamentoAccessi

    def __init__(self, anncsu_project, send_type, process_info=None, **kwargs):
        
        super().__init__(anncsu_project, send_type, process_info, **kwargs)

        # Set specific API URL
        self.api_url = self.anncsu_project.govway_api_endpoint

    def _get_operazione_civico(self, feature):
        """
        Get the operation for civico based on specific fields in feature.
        If not present, default to 'R'.
        """
        # Example logic to determine operation type
        # This should be replaced with actual logic based on feature attributes

        # If ANNCSU_FIELD_PROGR empty -> Insert
        if not feature[settings.ANNCSU_FIELD_PROGR]:
            return TipoOperazione.I  # Insert
        elif feature[settings.ANNCSU_FIELD_SOPPR]:
            return TipoOperazione.S  # Suppress
        elif feature[settings.ANNCSU_FIELD_DIRTY]:
            return TipoOperazione.R  # Update (default)
        
    def _fields_to_update(self, feature, res, fmapping=None):

        toret = super()._fields_to_update(feature, res, fmapping)

        operazione_civico = self._get_operazione_civico(feature)

        # Upate progr_civico only for I operation, for R and S it should not be updated
        if operazione_civico == TipoOperazione.I:
            toret.update({
                fmapping[settings.ANNCSU_FIELD_PROGR]: res['dati'][0].get('progr_civico'),
            })

        return toret

        
        
    def _to_NULL_to_empty_string(self, value):
        """
        Convert None or NULL values to empty string, to avoid issues with API validation.
        """
        value_str = str(value)
        if value_str == 'NULL':
            return ''
        
        return value_str

    def _mapping_feature_to_pdnd(self, feature):

        # Get the operation for civico, if not present default to 'R'
        operazione_civico = self._get_operazione_civico(feature)

        richiesta = {
            'codcom': self.anncsu_project.codice_comune.codice_catastale_del_comune,
            'progr_nazionale': str(int(feature[settings.ANNCSU_FIELD_PROGR_NAZ]))
        }

        # Formats the data according to the API requirements, including conditional fields based on operation type
        # data_valid_amm is mandatory for API
        data_valid_amm = feature[settings.ANNCSU_FIELD_DT_VAL_AMM]
        if not isinstance(data_valid_amm, str):
            data_valid_amm = data_valid_amm.toString('dd/MM/yyyy')
            
        

        # Create Accesso
        accesso_data = {
            'operazione_civico': operazione_civico,           
            'codice_civico_comunale': self._to_NULL_to_empty_string(feature[settings.ANNCSU_FIELD_COD_CIV_COMUNALE]),
            'metrico': self._to_NULL_to_empty_string(feature[settings.ANNCSU_FIELD_METRICO]),
            'sezione_censimento': self._to_NULL_to_empty_string(feature[settings.ANNCSU_FIELD_SEZ_CENS]),
            'coordinate': self._get_coordinates(feature),
            'data_valid_amm': data_valid_amm,
            'isolato': self._to_NULL_to_empty_string(feature[settings.ANNCSU_FIELD_ISOLATO]),
        } 

        try:

            # Case I: remove progr_civico if TipoOperanzione.I, 
            # because it will be generated by API and returned in response, 
            # so we need to update it in QGIS layer with the value returned by API
            accesso_data['progr_civico'] = str(int(feature[settings.ANNCSU_FIELD_PROGR]))
        except:
            pass
            
        
        if operazione_civico != TipoOperazione.S:

            accesso_data['numero'] = str(feature[settings.ANNCSU_FIELD_NUMERO])
            accesso_data['esponente'] = self._to_NULL_to_empty_string(str(feature[settings.ANNCSU_FIELD_ESPONENTE]))
            if str(feature[settings.ANNCSU_FIELD_SPECIFICITA]) != 'NULL':
                accesso_data['specificita'] = str(feature[settings.ANNCSU_FIELD_SPECIFICITA])

        if operazione_civico == TipoOperazione.S:
            accesso_data['numero'] = None
            accesso_data['metrico'] = None
            accesso_data['sezione_censimento'] = None
            accesso_data['isolato'] = None
            accesso_data['codice_civico_comunale'] = None
        
        richiesta['accesso'] = AccessoAggiornamentiAccessi(**accesso_data)

        return richiesta
    

    
# Mapping of API types to their corresponding classes
# ---------------------------------------------------
MAP_API_CLASS = {
    'aggcoord': ANNCSUPDND_GestioneCoordinate_API,
    'aggacc': ANNCSUPDND_AggiornamentoAccessi_API
}