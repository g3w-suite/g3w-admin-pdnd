# coding=utf-8
"""" QPDND administration modules
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-22'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from qdjango.models import Project, Layer


class QPDNDProject(models.Model):
    """ Projects to expose """

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="%(app_label)s_projects")
    note = models.TextField('Note', null=True, blank=True)

    class Meta:
        verbose_name = 'PDND Project'


GEO_TYPE_VECTOR_LAYER_ALLOWED = [
    'Point',
    'MultiPoint',
    'Point25D',
    'MultiPointZ',
    'PointZ',
    'Polygon',
    'MultiPolygon',
    'Polygon25D',
    'PolygonZ',
    'MultiPolygonZ',
    'LineString',
    'MultiLineString',
    'LineString25D',
    'LineStringZ',
    'MultiLineStringZ',
]

class QPDNDLayer(models.Model):
    """ Layer to expose as endpoint for PDND """

    qpdnd_project = models.ForeignKey(QPDNDProject, on_delete=models.CASCADE, related_name="qpdnd_layer", null=True)

    layer = models.ForeignKey(Layer, on_delete=models.CASCADE, related_name='qpdnd_layer', null=True,
                              help_text=_('Select vector project layer to expose for PDND: '
                                          'only follow geometry types are allowed: ' +
                                          ', '.join(GEO_TYPE_VECTOR_LAYER_ALLOWED)))

    note = models.TextField('Note', null=True, blank=True)

    class Meta:
        verbose_name = 'PDND Layer'

    def clean_fields(self, exclude=None):

        super().clean_fields(exclude=exclude)

        # check for vector layer  only
        if self.layer.geometrytype not in GEO_TYPE_VECTOR_LAYER_ALLOWED:
            raise ValidationError({'layer': _("Layer geometry type is not in allowed type: " +
                                              ", ".join(GEO_TYPE_VECTOR_LAYER_ALLOWED))})

        # check for unique simplreporpoject and layer combination
        current_layers = QPDNDLayer.objects.filter(qpdnd_project=self.qpdnd_project, layer=self.layer)

        if len(current_layers) > 0 and (not hasattr(self, 'pk') or self.pk != current_layers[0].pk):
            raise ValidationError({'layer': _("Only once combination of QPDNDProject and vector layer !")})

    def __str__(self):
        return f"{self.qpdnd_project} - {self.layer}"