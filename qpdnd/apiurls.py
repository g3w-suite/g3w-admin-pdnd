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
from .settings import (
    _BASE_URL_INFO_TASK, 
    _BASE_URL_KILL_TASK,
    _BASE_URL_DOWN_TASK_RESULTS
)
from .api.views import (
    QPDNDAPIOgcView,
    QPDNDInfoProjectAPIView, 
    ANNCSURunAPIView, 
    ANNCSURunInfoTaskView,
    ANNCSURunKillTaskView, 
    ANNCSUDownTaskResultsView
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
    ),

    # Send ANNCSU data to PDND API
    # --------------------------------
    path('api/anncsu/gestionecoordinate/<int:anncsu_project_id>',
         ANNCSURunAPIView.as_view(),
         name='anncsu-api-gestionecoordinate'
    ),
    
    # Use for asyncronous task
    path(f'{_BASE_URL_INFO_TASK}<str:task_id>/',
         ANNCSURunInfoTaskView.as_view(),
         name='anncsu-api-infotask'),

    path(f'{_BASE_URL_KILL_TASK}<str:task_id>/',
         ANNCSURunKillTaskView.as_view(),
         name='anncsu-api-killtask'),

    # Download results
    path(f'{_BASE_URL_DOWN_TASK_RESULTS}<str:task_id>/',
         ANNCSUDownTaskResultsView.as_view(),
         name='anncsu-api-downtaskresults'),

]