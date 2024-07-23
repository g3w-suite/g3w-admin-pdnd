# coding=utf-8
"""" QPDND admin views
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
from qpdnd.models import QPDNDProject
from qpdnd.forms import QPDNDProjectForm


class QPDNDProjectsListView(ListView):
    """List view of QPDNDProject instances."""

    template_name = 'qpdnd/projects_list.html'
    model = QPDNDProject

    @method_decorator(permission_required('qpdnd.add_qpdndproject', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QPDNDProjectAddView(G3WRequestViewMixin, CreateView):
    """
    Create view for QPDNDProject instance.
    """
    form_class = QPDNDProjectForm
    template_name = 'qpdnd/project_form.html'
    success_url = reverse_lazy('qpdnd-project-list')

    @method_decorator(permission_required('qpdnd.add_qpdndproject', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

class QPDNDProjectUpdateView(G3WRequestViewMixin, UpdateView):
    """
    Update view for QPDNDProject model instance
    """
    model = QPDNDProject
    form_class = QPDNDProjectForm
    template_name = 'qpdnd/project_form.html'
    success_url = reverse_lazy('qpdnd-project-list')

    @method_decorator(
        permission_required('qpdnd.change_qpdndproject', (QPDNDProject, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QPDNDProjectDeleteView(G3WAjaxDeleteViewMixin, SingleObjectMixin, View):
    """
    Delete QPDNDProject model instance Ajax view
    """
    model = QPDNDProject

    @method_decorator(
        permission_required('qpdnd.delete_qpdndproject', (QPDNDProject, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)