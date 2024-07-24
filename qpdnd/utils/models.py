# coding=utf-8
""""
    QPDND utilities for models
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-24'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'


from django.db.models import Q
from qdjango.models import Layer
from qpdnd.models import GEO_TYPE_VECTOR_LAYER_ALLOWED


def allowed_layers_for_reporting(qpdnd_project):
    """
    Return queryset of layer available vector layer to expose:
    only layers with geometry type = GEO_TYPE_VECTOR_LAYER_ALLOWED

    :param qpdnd_project: QPDNDProject model instance
    :return: Qdjango Layer model QuerySet
    """

    return Layer.objects.filter(
            ~Q(pk__in=[l.layer.pk for l in qpdnd_project.layers()]),
            project=qpdnd_project.project,
            geometrytype__in=GEO_TYPE_VECTOR_LAYER_ALLOWED,

        )