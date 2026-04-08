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
    ANNCSUProjectsListView, 
    ANNCSUProjectCreateView, 
    ANNCSUProjectUpdateView, 
    ANNCSUProjectDeleteView,
    LayersConfigView, 
    ANNCSURunView
)

G3W_SITETREE_I18N_ALIAS.append('qpdnd')

urlpatterns = [

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

    path(
        'anncsu/projects/update/<int:pk>/', 
        login_required(ANNCSUProjectUpdateView.as_view()),
        name='qpdnd-anncsu-project-update'
    ),

    path(
        'anncsu/projects/delete/<int:pk>/', 
        login_required(ANNCSUProjectDeleteView.as_view()),
        name='qpdnd-anncsu-project-delete'
        ),

    # Path to get layers list of a project
    path(
        'jx/config/project_layers/', 
        login_required(LayersConfigView.as_view()),
        name='qpdnd-project-layers'),

    # To Run and reports page
    path(
        'anncsu/projects/run/<int:pk>/', 
        login_required(ANNCSURunView.as_view()),
        name='qpdnd-anncsu-project-run'),
]

