# coding=utf-8
""""QPDND views for vector layers

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__copyright__ = 'Copyright Gis3w'

from django.views.generic import \
    ListView, \
    CreateView, \
    UpdateView, \
    View
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from guardian.decorators import permission_required
from core.mixins.views import (
    G3WRequestViewMixin,
    G3WAjaxDeleteViewMixin
)
from qpdnd.models import (
    QPDNDProject,
    QPDNDLayer
)
from qpdnd.forms import QPDNDLayerForm


class QPDNDLayersListView(ListView):
    """List projects layers view."""

    template_name = 'qpdnd/layers_list.html'
    model = QPDNDLayer

    def get_queryset(self):
        return QPDNDLayer.objects.filter(qpdnd_project_id=self.kwargs['qps_prj_pk'])

    @method_decorator(
        permission_required(
            'qpdnd.change_qpdndproject',
            (QPDNDProject, 'pk', 'qps_prj_pk'),
            return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Add QpsProject instance pk
        ctx['qpdnd_project_id'] = self.kwargs['qps_prj_pk']

        return ctx


class QPDNDLayerMixinView(object):

    def get_context_data(self, **kwargs):
        ctx = ctx = super().get_context_data(**kwargs)

        # Add QpsProject instance pk
        ctx['update'] = False

        return ctx

    def get_form_kwargs(self):
        fkwargs = super().get_form_kwargs()

        # Add QpsTimeseriesProject instance
        fkwargs['qpdnd_project'] = QPDNDProject.objects.get(pk=self.kwargs['qps_prj_pk'])

        return fkwargs

    def get_success_url(self):

        return reverse_lazy('qpdnd-project-layer-list', args=[self.kwargs['qps_prj_pk']])


class QPDNDLayerAddView(QPDNDLayerMixinView, G3WRequestViewMixin, CreateView):
    """
    Create view for qps_timeseries project layer
    """
    form_class = QPDNDLayerForm
    template_name = 'qpdnd/layer_form.html'

    @method_decorator(
        permission_required(
            'qpdnd.change_qpdndproject',
            (QPDNDProject, 'pk', 'qps_prj_pk'),
            return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QPDNDLayerUpdateView(QPDNDLayerMixinView, G3WRequestViewMixin, UpdateView):
    """
    Update view for project layer
    """
    model = QPDNDLayer
    form_class = QPDNDLayerForm
    template_name = 'qpdnd/layer_form.html'

    @method_decorator(
        permission_required(
            'qpdnd.change_qpdndproject',
            (QPDNDProject, 'pk', 'qps_prj_pk'),
            return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QPDNDLayerDeleteView(QPDNDLayerMixinView, G3WAjaxDeleteViewMixin, SingleObjectMixin, View):
    """
    Delete project layer Ajax view
    """
    model = QPDNDLayer

    @method_decorator(
        permission_required(
            'qpdnd.change_qpdndproject',
            (QPDNDProject, 'pk', 'qps_prj_pk'),
            return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

