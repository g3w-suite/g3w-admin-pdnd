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
from rest_framework.response import Response
from OWS.views import OWSView
from qdjango.ows import OWSRequestHandler
from qdjango.models import Project
from core.api.base.views import G3WAPIView
from qpdnd.models import QPDNDProject
from qpdnd.utils.pdnd import QPDNDAdapter
from .permissions import ProjectEditPermission
from .decorators.voucher_checker import pdnd_voucher_required
from qgis.server import QgsServerProjectUtils

from django.test import Client
import json

class QDPNDOWSRequestHandler(OWSRequestHandler):

    def doRequest(self):
        """ Main proxy method entry """
        q = self.request.GET.copy()
        return self.baseDoRequest(q)


class QPDNDAPIOgcView(OWSView):
    """
    A wrapper view for QGIS server OCG WFS3 endpoint.
    """


    @method_decorator(csrf_exempt)
    @method_decorator(pdnd_voucher_required)
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

    def _make_problem_json_response(self, msg:str, status_code:int=500) -> JsonResponse:
        """
        Return a JsonResponse with a content-type header set to application/problem+json
        """

        return JsonResponse({
            'status': status_code,
            'title': msg
        },
            status=status_code,
            **{'content_type': 'application/problem+json'})

    def get(self, request, *args, **kwargs):

        try:

            # Management fo `/status` response
            # https://italia.github.io/api-oas-checker/rulesets/spectral-modi.html
            # 'paths-status'
            # You must define a /status path that can be used to health-check the API. Using this path avoids the
            # arbitrary usage of a server URL for health-check scope.
            # The /status endpoint should return a application/problem+json response containing a successful status code
            # if the service is working correctly.
            # The service provider is free to define the implementation logic for this path.
            if '/wfs3/status' in request.path:
                return self._make_problem_json_response('OK', status_code=200)


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


class QPDNDInfoProjectAPIView(G3WAPIView):

    permission_classes = [
        ProjectEditPermission
    ]

    def get(self, request, *args, **kwargs):

        prj = Project.objects.get(pk=kwargs['project_id'])
        qprj = prj.qgis_project

        toret = {}
        # Get OCG Server capabilitites properties:
        for service_property in [
            'Title',
            'Abstract',
            'OnlineResource',
            'ContactMail',
            'ContactPerson',

        ]:
            toret.update({
              service_property: getattr(
                QgsServerProjectUtils, f'owsService{service_property}')(qprj)
            })

        self.results.results.update(toret)
        return Response(self.results.results)
