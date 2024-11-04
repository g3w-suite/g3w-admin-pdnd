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


#############################################################
# For PDND request authentication
#############################################################


#############################################################
# These may be ported to the model settings

QPDND_SERVER_KID = {
    'test': "J_z5sjzZ-7yRxGz0Cz_EtIPSbpLE0d5BJoBNGcsTzz4",
    'prod': "J_z5sjzZ-7yRxGz0Cz_EtIPSbpLE0d5BJoBNGcsTzz4"
}

QPDND_ESERVICE_ID = {
    'test': "929ce5a1-2e82-4e37-bdce-c76bfd66407d",
    'prod': "929ce5a1-2e82-4e37-bdce-c76bfd66407d"
}

QPDND_ISSUER = {
    'test': "uat.interop.pagopa.it",
    'prod': "interop.pagopa.it"
}


QPDND_SERVER_ISSUER = {
    'test': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6",
    'prod': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6"
}

QPDND_SERVER_SUBJECT = {
    'test': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6",
    'prod': "c2fc3ed2-a096-4a23-bb2e-47c767fa19d6"
}

# Path to a RSA256 private key file used by G3WSuite to authenticate itself to PDND
QPDND_SERVER_PRIVKEY_PATH = {
    'test': os.getenv('BARI_PDND_PRIV_KEY', '/path/to/privkey.rsa.priv'),
    'prod': os.getenv('BARI_PDND_PRIV_KEY', '/path/to/privkey.rsa.priv')
}

#############################################################
# Generic: should be the same for all services


QPDND_WELL_KNOWN_URL = {
    'test': "https://uat.interop.pagopa.it/.well-known/jwks.json",
    'prod': "https://interop.pagopa.it/.well-known/jwks.json"
}

QPDND_AUTH_HEADER = 'Authorization'

QPDND_API_PURPOSE_VERIFICATION_URL = {
    'test': "https://api.uat.interop.pagopa.it/1.0/purposes/{purposeId}/agreement",
    'prod': "https://api.interop.pagopa.it/1.0/purposes/{purposeId}/agreement"
}

QPDND_API_TOKEN_URL = {
    'test': "https://auth.uat.interop.pagopa.it/token.oauth2",
    'prod': "https://auth.interop.pagopa.it/token.oauth2"
}

QPDN_AUDIENCE = {
    'test': "auth.uat.interop.pagopa.it/client-assertion",
    'prod': "auth.interop.pagopa.it/client-assertion"
}

# INTERNAL USER FOR PROJECTS AUTHENTICATION
# -----------------------------------------
QPDND_INTERNAL_USERNAME = 'qpdnd_internal_user'
QPDND_INTERNAL_USERBACKEND = ('qpdnd', 'QPDND')

