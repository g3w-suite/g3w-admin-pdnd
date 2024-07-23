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
    QPDNDProjectDeleteView
)

G3W_SITETREE_I18N_ALIAS.append('qprocessing')

urlpatterns = [

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

    # For reporting layer
    # -------------------
    # path(
    #     'projects/<int:qps_prj_pk>/layers/',
    #     login_required(SimpleProLayersListView.as_view()),
    #     name='simplereporting-project-layer-list'
    # ),
    #
    # path(
    #     'projects/<int:qps_prj_pk>/layers/add/',
    #     login_required(SimpleProLayerAddView.as_view()),
    #     name='simplereporting-project-layer-add'
    # ),
    #
    # path(
    #     'projects/<int:qps_prj_pk>/layers/update/<int:pk>/',
    #     login_required(SimpleProLayerUpdateView.as_view()),
    #     name='simplereporting-project-layer-update'
    # ),
    #
    # path(
    #     'projects/<int:qps_prj_pk>/layers/delete/<int:pk>/',
    #     login_required(SimpleProLayerDeleteView.as_view()),
    #     name='simplereporting-project-layer-delete'
    # ),
]

