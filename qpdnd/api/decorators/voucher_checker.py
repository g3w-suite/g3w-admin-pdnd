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
import datetime
import uuid


def _get_server_client_assertion(audience, client_id, issuer, subject, private_key_path):
    """
    Create a client assertion (where G3WSuite is the client) to get PDND a voucher
    """

    issued = datetime.datetime.utcnow()
    delta = datetime.timedelta(minutes=120)
    expire_in = issued + delta
    jti = uuid.uuid4()

    headers_rsa = {
        "kid": client_id,
        "alg": "RS256",
        "typ": "JWT"
    }

    payload = {
        "iss": issuer,
        "sub": subject,
        "aud": audience,
        #"purposeId": PURPOSEID,  # Not needed for server assertion
        "jti": str(jti),
        "iat": issued,
        "exp": expire_in
    }

    key_path = private_key_path
    with open(key_path, "rb") as private_key:
        rsaKey = private_key.read()

    return jwt.encode(payload, rsaKey, algorithm="RS256", headers=headers_rsa)


def _get_voucher(url, client_id, client_assertion):
    """
    Make a POST request to PDND
    """

    # Note: client_id is the ISSUER, not KID!!!
    data = {
        'client_id': client_id,
        'client_assertion': client_assertion,
        'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'grant_type': 'client_credentials'
    }

    return requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})


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


        # Verify that the purposeId in the token is authorized by calling PDND API
        purpose_id = None
        try:
            purpose_id = payload.get('purposeId')
        except Exception as e:
            return JsonResponse({
                'status': 'Error',
                'msg': 'Invalid token (missing purposeId)'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        # Get the voucher from the PDND API
        server_assertion = _get_server_client_assertion(
            settings.QPDN_AUDIENCE[qpdndp.pdnd_env],
            settings.QPDND_SERVER_KID[qpdndp.pdnd_env],
            settings.QPDND_SERVER_ISSUER[qpdndp.pdnd_env],
            settings.QPDND_SERVER_SUBJECT[qpdndp.pdnd_env],
            settings.QPDND_SERVER_PRIVKEY_PATH[qpdndp.pdnd_env])

        server_result = _get_voucher(settings.QPDND_API_TOKEN_URL[qpdndp.pdnd_env], settings.QPDND_SERVER_ISSUER[qpdndp.pdnd_env], server_assertion)

        if server_result.status_code != 200:
            return JsonResponse({
                'status': 'Error',
                'msg': 'PDND voucher request failed'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        server_access_token = server_result.json()['access_token']
        purpose_verification_url = settings.QPDND_API_PURPOSE_VERIFICATION_URL[qpdndp.pdnd_env].format(purposeId=purpose_id)
        purpose_verification_response = requests.get(purpose_verification_url, headers={settings.QPDND_AUTH_HEADER: 'Bearer ' + server_access_token})

        if purpose_verification_response.status_code != 200:
            return JsonResponse({
                'status': 'Error',
                'msg': 'PDND purpose request verification failed'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        purpose_verification_response_json = purpose_verification_response.json()
        state = purpose_verification_response_json.get('state', False)
        if state != 'ACTIVE':
            return JsonResponse({
                'status': 'Error',
                'msg': 'PDND purpose state verification failed'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        eserviceId = purpose_verification_response_json.get('eserviceId', False)
        if not eserviceId or not eserviceId == qpdndp.pdnd_eservice_id:
            return JsonResponse({
                'status': 'Error',
                'msg': 'PDND purpose eserviceId verification failed'
            },
                status=401,
                **{'content_type': 'application/problem+json'})

        # All checks passed, call the view
        return func(request, *args, **kwargs)

    return _wrapped_view
