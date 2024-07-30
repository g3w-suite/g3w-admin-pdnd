# coding=utf-8
""""
    Urls for API rest service
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-24'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.urls import path, re_path
from .api.views import (
    QPDNDAPIOgcView,
    QPDNDInfoProjectAPIView
)

BASE_URLS = 'qpdnd'

urlpatterns = [
    re_path(
        '^api/ogc/(?P<endpoint>[-_\w\d]+)/wfs3&?',
        QPDNDAPIOgcView.as_view(),
        name='qpdnd-api-ogc'
    ),

    path('api/infoproject/<int:project_id>',
         QPDNDInfoProjectAPIView.as_view(),
         name='qpdnd-api-prj-info'
    )

]