# coding=utf-8
"""" QPDND utilities
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-26'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.conf import settings
from django.http import HttpResponse
from qpdnd.models import QPDNDProject
import json
import re


class QPDNDAdapter():
    """
    Class for fix OpenAPI QGIS response to Italian Guidelines
    """

    def __init__(self, response: HttpResponse, qdnd_project: QPDNDProject):
        self.response = response
        self.jcontent = json.loads(response.content)
        self.qdnd_project = qdnd_project

    def _update_structure(self, path: str, dtu: dict, mode: str='upd') -> None:
        """
        Update the content of self.jcontent dict at the specific `path`
        I.e. Given #/info/version `path` the self.jcontent['info']['version'] will be updated with `dtu` dict.
        """

        if not path.startswith('#'):
            raise Exception('Path must start with #!')

        if mode not in ('del', 'upd'):
            raise Exception('Mode must be `del`(delete) or `upd`(update)!')

        startdictpath = path[2:].split('/')
        if mode == 'del':
            dictpath = startdictpath[0:-1]
        else:
            dictpath = startdictpath

        node = None
        for lev in dictpath:
            if not node:
                node = self.jcontent[lev]
            else:
                node = node[lev]

        # Delete the property and return
        if mode == 'del':
            del(node[startdictpath[-1:][0]])
        else:

            # Update the content
            if type(node) == dict:
                node.update(dtu)
            elif type(node) == list:
                mode.append(dtu)
            else:
                raise Exception('Nod type not supported, only `dict` or `list`!')



    def fix_italian_guidelines_extended(self):
        """
        Fix italian guidelines extended requirements
        """

        # Fix single part fo the schema
        self._fix_info()
        self._fix_components()
        self._fix_servers()
        self._fix_paths()
        self._fix_status()

    def _fix_https(self, doc):
        """
        Change http to https when the debug statsu is active
        """

        pattern = r'^http://'
        replacement = 'https://'

        # Usa re.sub per sostituire "http" con "https"
        fixed_doc = re.sub(pattern, replacement, doc)
        return fixed_doc

    def _fix_status(self):
        """
        Fix italian guidelines extended requirements add `/status` path
        """
        self.jcontent['paths'].update({
            "/status": {
                "get": {
                    "description": "Give the status of the service",
                    "operationId": "getStatus",
                    "responses": {
                        "200": {
                            "content": {
                                "application/problem+json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/root"
                                    }
                                },
                            },
                            "description": "Return the health status of the API"
                        },
                        "default": {
                            "content": {
                                "application/problem+json": {
                                    "schema": {
                                        "type": "string"
                                    }
                                },

                            },
                            "description": "An error occurred."
                        }
                    },
                    "summary": "Service status",
                    "tags": [
                        "Capabilities"
                    ]
                }
            }
        })



    def _fix_paths(self):
        """
        Fix italian guidelines extended requirements for `paths` section
        """


        # For every path fix the response fo default exception
        paths = self.jcontent['paths']
        for path, dpath in paths.items():

            # Explore 'get'
            if 'get' in dpath:
                def_res = dpath['get']['responses']['default']
                tochange = None
                for k, v in def_res['content'].items():
                    if k == 'application/json' and v['schema']['$ref'] == '#/components/schemas/exception':
                        tochange = k
                del (def_res['content'][tochange])
                def_res['content'].update({
                    'application/problem+json': v
                })

                # Delete text/html response
                if 'text/html' in def_res['content']:
                    del (def_res['content']['text/html'])

                # Fix parameters for integer|float
                if 'parameters' in dpath['get']:
                    for param in dpath['get']['parameters']:
                        if 'schema' in param:
                            if 'type' in param['schema'] and param['schema']['type'] in ('integer', 'numeric', 'number'):
                                param['schema'].update({
                                    'format': 'int32' if param['schema']['type'] == 'integer' else 'float',
                                })


            # ---------------------------------------------------
            # Delete other http methods: post, put, patch, delete
            # ---------------------------------------------------
            for m in ('post', 'put', 'patch', 'delete'):
                if m in dpath:
                    del (dpath[m])

    def _fix_servers(self):
        """
        Fix italian guidelines extended requirements for `servers` section
        """

        # For development
        if settings.DEBUG:
            self.jcontent['servers'][0]['url'] = self._fix_https(self.jcontent['servers'][0]['url'])

        self.jcontent['servers'][0].update({'description': 'Production server'})

    def _fix_components(self):
        """
        Fix italian guidelines extended requirements for `components` section
        """

        # Fix type number
        self._update_structure('#/components/parameters/bbox/schema/items', {'format': 'float'})
        self._update_structure('#/components/parameters/limit/schema', {'format': 'int32'})
        self._update_structure('#/components/parameters/offset/schema', {'format': 'int32'})
        self._update_structure('#/components/schemas/extent/properties/spatial/items',
                               {'format': 'float'})
        self._update_structure('#/components/schemas/featureGeoJSON/properties/id',
                               {"oneOf": [
                                            {"type": "string"},
                                            {"type": "integer", 'format': 'int32'}
                                         ]
                                    })
        self._update_structure('#/components/schemas/featureCollectionGeoJSON/properties/numberMatched',
                               {'format': 'int32'})
        self._update_structure('#/components/schemas/featureCollectionGeoJSON/properties/numberReturned',
                               {'format': 'int32'})

        # Fix example
        self._update_structure('#/components/schemas/collectionInfo/properties/relations',
                               {'example': {'id': 'label'}})
        self._update_structure('#/components/schemas/extent/properties/temporal/properties/interval/items/items',
                               {'example': '2011-11-11T12:22:11Z'})

        # TODO: check the correct position of trs i.e. form pygeoapi
        # Remove `trs`
        self._update_structure('#/components/schemas/extent/properties/temporal/properties/interval/items/items/trs',
                               {},
                               'del')

    def _fix_info(self):
        """
        Fix italian guidelines extended requirements for `info` section
        """

        # Fix #/info/x-summary
        self._update_structure('#/info', {
            'x-summary': self.qdnd_project.x_summary
        })

        # Fix #/info/version
        self._update_structure('#/info', {
            'version': self.qdnd_project.version
        })

        # Fix #/info/termsOfService
        # Only for Italian Guidelines Extended
        if self.qdnd_project.terms_of_service:
            self._update_structure('#/info', {
                'termsOfService': self.qdnd_project.terms_of_service
            })

        self._update_structure('#/info', {
            'title': self.qdnd_project.title
        })

        self._update_structure('#/info', {
            'description': self.qdnd_project.description
        })

        self._update_structure('#/info/contact', {
            'name': self.qdnd_project.contact_author
        })

        self._update_structure('#/info/contact', {
            'email': self.qdnd_project.contact_email
        })

        self._update_structure('#/info/contact', {
            'url': self.qdnd_project.contact_url
        })

        self._update_structure('#/info/license', {
            'name': self.qdnd_project.license.name,
            'url': self.qdnd_project.license.url
        })

        self._update_structure('#/info', {
            'x-api-id': self.qdnd_project.x_api_id,

        })

    def update_response(self):
        """
        Update the current response (self.response) with the new content and headers
        """

        self.response.content = json.dumps(self.jcontent, indent=2)

        self.response.headers['Content-Length'] = len(self.response.content)

    def download(self):
        """
        Set `Content-Disposition` for download of OpenAPI schema
        """

        # Build name: add endpoint
        filename = f'{self.qdnd_project.endpoint}.api.openapi3.json'
        self.response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'




