# coding=utf-8
""""
    API REST views
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-24'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from OWS.views import OWSView, OWSREQUESTHANDLER_CLASSES
from qdjango.ows import OWSRequestHandler
from qpdnd.models import QPDNDProject

from django.test import Client
import json

class QDPNDOWSRequestHandler(OWSRequestHandler):

    def doRequest(self):
        """ Main proxy method entry """
        q = self.request.GET.copy()
        return self.baseDoRequest(q)


class QPDNDAPIOgcView(OWSView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):

        # Get parameters for OWS:ows-wfs3 url by endpoint url parameter
        qpdndp = QPDNDProject.objects.get(endpoint=kwargs['endpoint'])

        kwargs.update({
            'group_slug': qpdndp.project.group.slug,
            'project_id': qpdndp.project.pk,

        })

        # get handler request by project type
        self.OWSRequestHandler = QDPNDOWSRequestHandler

        # Delete endpoint parameter for
        del kwargs['endpoint']

        return super(OWSView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        # newpath = reverse('OWS:ows-wfs3', kwargs=kwargs)


        # request.path = reverse('OWS:ows-wfs3', kwargs=kwargs)
        return self.OWSRequestHandler(request, **kwargs).doRequest()

    def post(self, request, *args, **kwargs):
        return self.OWSRequestHandler(request, **kwargs).doRequest()




# class QPDNDAPIOgcView(G3WAPIView):
#     """
#     Works as wrapper for G3W-SUITE OWS /wf3 service
#     """
#
#     def get(self, request, *args, **kwargs):
#
#         client = Client()
#         user = User.objects.filter(is_superuser=True).first()
#         client._login(user, 'django.contrib.auth.backends.ModelBackend')
#         response = client.get('/ows/68/qdjango/336/wfs3/collections/buildings/items.json')
#
#
#
#         return Response(json.loads(response.content))