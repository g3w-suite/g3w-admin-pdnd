# coding=utf-8
""""Checks for a valid JWS token in the request authorization header.

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2024-09-16'
__copyright__ = 'Copyright 2024, Gis3w'

from django.http import JsonResponse
from django.conf import settings
from qpdnd.models import QPDNDProject
import json
import jwt
import requests


def pdnd_voucher_required(func):
    """
    Decorator for views that checks that the user has a valid JWS token.
    """

    def _wrapped_view(request, *args, **kwargs):

        # If user is superuser, skip the check
        if request.user.is_superuser:
            return func(request, *args, **kwargs)

        # Get parameters for OWS:ows-wfs3 url by endpoint url parameter
        qpdndp = QPDNDProject.objects.get(endpoint=kwargs['endpoint'])

        # Extract the JWS token from the request authorization:bearer header
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]

        if not token:
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (empty)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        try:
            header = jwt.get_unverified_header(token)
        except Exception as e:
            return JsonResponse({
                'status': 'Error',
                'msg': str(e)
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        if not header.get('typ', '') == 'at+jwt':
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (wrong type)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        alg = header.get('alg', '')
        # NOTE: only RS256 is supported?
        if not alg == 'RS256':
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (unsupported algorithm)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        if not header.get('use', '') == 'sig':
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (invalid use)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        kid = header.get('kid', '')
        if not kid:
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (empty kid)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        # Get the public key from the well-known endpoint
        # TODO: this should be cached!
        well_known_response = requests.get(settings.QPDND_WELL_KNOWN_URL[qpdndp.pdnd_env])

        # Search for kid in the json response
        public_key = None
        for key in well_known_response.json().get('keys', []):
            if key.get('kid', '') == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                break

        if not public_key:
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (kid not found in .well-known)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})


        # Decode and validate the JWS token
        try:
            payload = jwt.decode(token, public_key,
                                 algorithms=[alg],
                                 audience=qpdndp.pdnd_audience,
                                 issuer=settings.QPDND_ISSUER[qpdndp.pdnd_env])
        except Exception as e:
            return JsonResponse({
                'status': 'Error',
                'msg': str(e)
            },
                status=401,
                **{'content_type': 'application/problem+json'})


        return func(request, *args, **kwargs)

    return _wrapped_view
