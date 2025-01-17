# coding=utf-8
"""" QPDND admin views fro client settings models
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-23'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

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
from qpdnd.models import QPDNDClientSetting
from qpdnd.forms import QPDNDClientSettingForm


class QPDNDClientSettingListView(ListView):
    """List view of QPDNDClientSetting instances."""

    template_name = 'qpdnd/client_settings_list.html'
    model = QPDNDClientSetting

    @method_decorator(permission_required('qpdnd.add_QPDNDClientSetting', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QPDNDClientSettingMixin(object):

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['info_project_url'] = '/qpdnd/api/infoproject/'

        ctx['form_state'] = 'insert' if isinstance(self, CreateView) else 'update'
        return ctx


class QPDNDClientSettingAddView(QPDNDClientSettingMixin, G3WRequestViewMixin, CreateView):
    """
    Create view for QPDNDClientSetting instance.
    """
    form_class = QPDNDClientSettingForm
    template_name = 'qpdnd/project_form.html'
    success_url = reverse_lazy('qpdnd-client-setting-list')

    @method_decorator(permission_required('qpdnd.add_QPDNDClientSetting', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class QPDNDClientSettingUpdateView(QPDNDClientSettingMixin, G3WRequestViewMixin, UpdateView):
    """
    Update view for QPDNDClientSetting model instance
    """
    model = QPDNDClientSetting
    form_class = QPDNDClientSettingForm
    template_name = 'qpdnd/client_setting_form.html'
    success_url = reverse_lazy('qpdnd-client-setting-list')

    @method_decorator(
        permission_required('qpdnd.change_QPDNDClientSetting', (QPDNDClientSetting, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QPDNDClientSettingDeleteView(G3WAjaxDeleteViewMixin, SingleObjectMixin, View):
    """
    Delete QPDNDClientSetting model instance Ajax view
    """
    model = QPDNDClientSetting

    @method_decorator(
        permission_required('qpdnd.delete_QPDNDClientSetting', (QPDNDClientSetting, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)