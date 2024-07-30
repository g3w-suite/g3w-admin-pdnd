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
from django.http import JsonResponse
from django.urls import reverse
from OWS.views import OWSView, OWSREQUESTHANDLER_CLASSES
from qdjango.ows import OWSRequestHandler
from qpdnd.models import QPDNDProject
from qpdnd.utils import QPDNDAdapter

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
        self.qpdndp = QPDNDProject.objects.get(endpoint=kwargs['endpoint'])

        kwargs.update({
            'group_slug': self.qpdndp.project.group.slug,
            'project_id': self.qpdndp.project.pk,

        })

        # get handler request by project type
        self.OWSRequestHandler = QDPNDOWSRequestHandler

        # Delete endpoint parameter for
        del kwargs['endpoint']

        return super(OWSView, self).dispatch(request, *args, **kwargs)

    def _make_problem_json_response(self, msg:str, status_code:int=500, status='Error') -> JsonResponse:
        """
        Return a JsonResponse with a content-type header set to application/problem+json
        """

        return JsonResponse({
            'status': status,
            'msg': msg
        },
            status=status_code,
            **{'content_type': 'application/problem+json'})

    def get(self, request, *args, **kwargs):

        try:

            # Management fo `/status` response
            if '/wfs3/status' in request.path:
                return self._make_problem_json_response('', status_code=200, status='OK')


            response = self.OWSRequestHandler(request, **kwargs).doRequest()

            # Check for possible problem
            if 400 <= response.status_code <= 499 or 500 <= response.status_code <= 599:
                return self._make_problem_json_response(response.content, response.status_code)

            # Check for api.openapi3 in request.path
            if '/wfs3/api.openapi3' in request.path:
                adapter = QPDNDAdapter(response, self.qpdndp)

                adapter.fix_italian_guidelines_extended()

                adapter.update_response()

                if 'download' in request.GET and request.GET['download'] == '1':
                    adapter.download()

                response = adapter.response

            return response

        except Exception as e:

            return self._make_problem_json_response(str(e), 500)





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