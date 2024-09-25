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


# For PDND request authentication
# -------------------------------

QPDND_ISSUER = {
    'test': "uat.interop.pagopa.it",
    'prod': "interop.pagopa.it"
}

QPDND_WELL_KNOWN_URL = {
    'test': "https://uat.interop.pagopa.it/.well-known/jwks.json",
    'prod': "https://interop.pagopa.it/.well-known/jwks.json"
}