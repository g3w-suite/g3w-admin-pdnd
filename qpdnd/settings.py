# coding=utf-8
""""
    Default settings variables
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-09-20'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

import os

# Base urls
_BASE_URL_INFO_TASK = 'api/infotask/'
_BASE_URL_KILL_TASK = 'api/killtask/'


#############################################################
# For PDND request authentication
#############################################################

# Activate/deactivate the PDND voucher checker
QPDND_VOUCHER_VALIDATE = True

QPDND_AUTH_HEADER = 'Authorization'

# INTERNAL USER FOR PROJECTS AUTHENTICATION
# -----------------------------------------
QPDND_INTERNAL_USERNAME = 'qpdnd_internal_user'
QPDND_INTERNAL_USERBACKEND = ('qpdnd', 'QPDND')

# FOR TESTING
# -----------
QPDND_TESTING_RUNNING = False
QPDND_TESTING_VOUCHER_EXP = None

# -----------------------------------------------------------------
#  THE FOLLOWING SETTINGS ARE UNSUPPORTED AND SHOULD BE REMOVED
# -----------------------------------------------------------------
# #############################################################
# # These may be ported to the model settings
#
# QPDND_SERVER_KID = {
#     'test': "J_z5sjzZ-7yRxGz0Cz_EtIPSbpLE0d5BJoBNGcsTzz4",
#     'prod': "J_z5sjzZ-7yRxGz0Cz_EtIPSbpLE0d5BJoBNGcsTzz4"
# }
#
# QPDND_ESERVICE_ID = {
#     'test': "929ce5a1-2e82-4e37-bdce-c76bfd66407d",
#     'prod': "929ce5a1-2e82-4e37-bdce-c76bfd66407d"
# }
#
# QPDND_ISSUER = {
#     'test': "uat.interop.pagopa.it",
#     'prod': "interop.pagopa.it"
# }
#
#
# QPDND_SERVER_ISSUER = {
#     'test': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6",
#     'prod': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6"
# }
#
# QPDND_SERVER_SUBJECT = {
#     'test': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6",
#     'prod': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6"
# }
#
# # Path to a RSA256 private key file used by G3WSuite to authenticate itself to PDND
# QPDND_SERVER_PRIVKEY_PATH = {
#     'test': os.getenv('BARI_PDND_PRIV_KEY', '/path/to/privkey.rsa.priv'),
#     'prod': os.getenv('BARI_PDND_PRIV_KEY', '/path/to/privkey.rsa.priv')
# }
#
# #############################################################
# # Generic: should be the same for all services
#
#
# QPDND_WELL_KNOWN_URL = {
#     'test': "https://uat.interop.pagopa.it/.well-known/jwks.json",
#     'prod': "https://interop.pagopa.it/.well-known/jwks.json"
# }
#
# QPDND_API_PURPOSE_VERIFICATION_URL = {
#     'test': "https://api.uat.interop.pagopa.it/1.0/purposes/{purposeId}/agreement",
#     'prod': "https://api.interop.pagopa.it/1.0/purposes/{purposeId}/agreement"
# }
#
# QPDND_API_TOKEN_URL = {
#     'test': "https://auth.uat.interop.pagopa.it/token.oauth2",
#     'prod': "https://auth.interop.pagopa.it/token.oauth2"
# }
#
# QPDN_AUDIENCE = {
#     'test': "auth.uat.interop.pagopa.it/client-assertion",
#     'prod': "auth.interop.pagopa.it/client-assertion"
# }


#############################################################
# For ANNCSU 
#############################################################'

# Private settings for GovWay API access
_ANNCSU_SENDED_STATUS = 'INVIATO'
_ANNCSU_ERROR_STATUS = 'ERRORE'

# GovWay API auth user
ANNCSU_GOVWAY_API_USER = 'your_govway_user'
ANNCSU_GOVWAY_API_PASSWORD = 'your_govway_password'

# ANNCSU FIELDS:

# Internal fields mapping
# -----------------------------
ANNCSU_FIELD_STATO_INVIO = 'anncsu_stato_invio' # varchar
ANNCSU_FIELD_DATA_INVIO = 'anncsu_data_invio' # datetime
ANNCSU_FIELD_DIRTY = 'anncsu_dirty' # boolean

# API - /gestioneaccessi
# -----------------------------

ANNCSU_FIELD_PROGR = 'progressivo'
ANNCSU_FIELD_LAT = 'latitudine'
ANNCSU_FIELD_LON = 'longitudine'
ANNCSU_FIELD_QUOTA = 'quota'

# Max requests per day
ANNCSU_MAX_REQUESTS_PER_CICLE = 2000

# Timeout between requests (seconds)
ANNCSU_REQUEST_TIME_INTERVAL = 60 * 5 # 5 minutes
#ANNCSU_REQUEST_TIME_INTERVAL = 'NEXT_DAY'  # Special value to indicate reset after midnight'

