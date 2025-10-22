# coding=utf-8
""""
    Views for ANNCSU PDND extension
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-10-10 17:20:38'
__copyright__ = 'Copyright Gis3w'


from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import (
    CreateView, 
    ListView, 
    View, 
    UpdateView
)
from django.views.generic.detail import SingleObjectMixin
from guardian.decorators import permission_required
from core.mixins.views import G3WAjaxDeleteViewMixin, G3WRequestViewMixin
from qdjango.models import (
    Project, 
    Layer
)

from qpdnd.models import ANNCSUProject
from qpdnd.forms import ANNCSUProjectForm


class ANNCSUProjectsListView(ListView):
    """
    List ANNCSUProject view.
    """
    model = ANNCSUProject
    template_name = 'qpdnd/anncsu/project_list.html'

    @method_decorator(permission_required('qpdnd.add_anncsuproject', return_403=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

class ANNCSUProjectCreateView(G3WRequestViewMixin, CreateView):
    """ Config create view """

    form_class = ANNCSUProjectForm
    template_name = 'qpdnd/anncsu/project.html'


    @method_decorator(permission_required('qpdnd.add_anncsuproject', return_403=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('qpdnd-anncsu-project-list')
    

class ANNCSUProjectUpdateView(G3WRequestViewMixin, UpdateView):

    form_class = ANNCSUProjectForm
    model = ANNCSUProject
    template_name = 'qpdnd/anncsu/project.html'

    @method_decorator(permission_required('qpdnd.add_anncsuproject', return_403=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('qpdnd-anncsu-project-list')
    

class ANNCSUProjectDeleteView(G3WAjaxDeleteViewMixin, G3WRequestViewMixin, SingleObjectMixin, View):
    '''
    Delete config Ajax view
    '''
    model = ANNCSUProject

    @method_decorator(permission_required('qpdnd.add_anncsuproject', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ANNCSUProjectDeleteView(G3WAjaxDeleteViewMixin, SingleObjectMixin, View):
    """
    Delete ANNCSUProject model instance Ajax view
    """
    model = ANNCSUProject

    @method_decorator(
        permission_required('qpdnd.delete_anncsuproject', (ANNCSUProject, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class LayersConfigView(View):
    """
    Return layers for project
    """

    @method_decorator(permission_required('qpdnd.add_anncsuproject', return_403=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):

        layers = Project.objects.get(pk=self.request.GET['project_id']).layer_set.all()
        try:
            config = ANNCSUProject.objects.get(pk=self.request.GET['config_id'])
        except:
            config = None

        clayers = []
        if config:
            clayers = [config.layer]

        return JsonResponse({
            'layers': [
                {
                    'id': layer.pk,
                    'text': layer.title,
                    'selected': layer in clayers
                } for layer in layers
            ]
        })