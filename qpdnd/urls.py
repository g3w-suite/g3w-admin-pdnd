# coding=utf-8
"""" Qpdnd urls
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-22'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'


from django.urls import path
from django.contrib.auth.decorators import login_required
from base.urls import G3W_SITETREE_I18N_ALIAS

from qpdnd.views import (
    QPDNDProjectsListView,
    QPDNDProjectAddView,
    QPDNDProjectUpdateView,
    QPDNDProjectDeleteView,
    QPDNDClientSettingListView,
    QPDNDClientSettingAddView,
    QPDNDClientSettingUpdateView,
    QPDNDClientSettingDeleteView,
    ANNCSUProjectsListView, 
    ANNCSUProjectCreateView, 
    LayersConfigView
)

G3W_SITETREE_I18N_ALIAS.append('qpdnd')

urlpatterns = [

    # For client settings
    # -------------------
    path(
        'client_settings/',
        login_required(QPDNDClientSettingListView.as_view()),
        name='qpdnd-client-setting-list'
    ),

    path(
        'client_settings/add/',
        login_required(QPDNDClientSettingAddView.as_view()),
        name='qpdnd-client-setting-add'
    ),

    path(
        'client_settings/update/<int:pk>/',
        login_required(QPDNDClientSettingUpdateView.as_view()),
        name='qpdnd-client-setting-update'
    ),

    path(
        'client_settings/delete/<int:pk>/',
        login_required(QPDNDClientSettingDeleteView.as_view()),
        name='qpdnd-client-setting-delete'
    ),

    # For projects
    # ------------
    path(
        'projects/',
        login_required(QPDNDProjectsListView.as_view()),
        name='qpdnd-project-list'
    ),

    path(
        'projects/add/',
        login_required(QPDNDProjectAddView.as_view()),
        name='qpdnd-project-add'
    ),

    path(
        'projects/update/<int:pk>/',
        login_required(QPDNDProjectUpdateView.as_view()),
        name='qpdnd-project-update'
    ),

    path(
        'projects/delete/<int:pk>/',
        login_required(QPDNDProjectDeleteView.as_view()),
        name='qpdnd-project-delete'
    ),

    # For ANNCSU projects
    # -------------------
    path(
        'anncsu/projects/', 
        login_required(ANNCSUProjectsListView.as_view()), 
        name='qpdnd-anncsu-project-list'
    ),

    path(
        'anncsu/projects/add/', 
        login_required(ANNCSUProjectCreateView.as_view()), 
        name='qpdnd-anncsu-project-add'
    ),

    # path(
    #     'anncsu/projects/update/<int:pk>/', 
    #     login_required(IntercadConfigUpdateView.as_view()),
    #     name='intercad-config-update'
    # ),

    # path(
    #     'anncsu/projects/delete/<int:pk>/', 
    #     login_required(IntercadConfigDeleteView.as_view()),
    #     name='intercad-config-delete'),

    # Path to get layers list of a project
    path(
        'jx/config/project_layers/', 
        login_required(LayersConfigView.as_view()),
        name='qpdnd-project-layers'),
]

