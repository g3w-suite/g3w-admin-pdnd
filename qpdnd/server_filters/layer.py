# coding=utf-8
"""
    Filter WFS3 services with only one layer
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = "lorenzetti@gis3w.it"
__copyright__ = "Copyright Gis3w"
__license__ = "MPL 2.0"

from django.conf import settings
from guardian.shortcuts import get_perms, get_anonymous_user
from qgis.server import QgsAccessControlFilter
from qgis.core import QgsMessageLog, Qgis
from qdjango.apps import QGS_SERVER
from qdjango.models import Layer
from urllib.parse import urlparse, parse_qs


class QPDNDLayerAccessControlFilter(QgsAccessControlFilter):
    """Set only one layer for WFS3 service"""

    def __init__(self, server_iface):
        super().__init__(server_iface)

        self.server_iface = server_iface

    def layerPermissions(self, layer):

        rights = QgsAccessControlFilter.LayerPermissions()

        # Only readable
        rights.canRead = True
        rights.canInsert = False
        rights.canUpdate = False
        rights.canDelete = False
    
        return rights


# Register the filter, keep a reference because of the garbage collector
layer_filter = QPDNDLayerAccessControlFilter(QGS_SERVER.serverInterface())
# Note: this should be the last filter, set the priority to 10000
QGS_SERVER.serverInterface().registerAccessControl(layer_filter, 10100)
