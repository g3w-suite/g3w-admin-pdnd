# coding=utf-8
""""Test for authentication required by PDND
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-09-25'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.urls import reverse
from .base import TestQPDNDBase, CURRENT_PATH, TEST_BASE_PATH
from .pdnd_params import *
import jwt
import datetime
import uuid
import json
import os
import requests

class TestQPDNDModels(TestQPDNDBase):
    """
    Test  Authentication required by PDND
    """

    @classmethod
    def setUp(cls):
        super().setUp()

        cls.voucher_expired = "eyJ0eXAiOiJhdCtqd3QiLCJhbGciOiJSUzI1NiIsInVzZSI6InNpZyIsImtpZCI6ImNkYjUyNTMyLWRkOTQtNDBlZi04MjRkLTljNTViMTBlNmJjOSJ9.eyJhdWQiOiJ0ZXN0X2NhcnRvZ3JhZmljbyIsInN1YiI6IjQ1YTA4N2Y4LTY4MDYtNDNmNi04NDMxLWQxNWZhMWM5OGYwYyIsIm5iZiI6MTcyNzI3MDIxMCwicHVycG9zZUlkIjoiMTRkOTZlMjMtMGIyZC00YTg5LTk3MDYtYTIyNTI5NDJmZjRlIiwiaXNzIjoidWF0LmludGVyb3AucGFnb3BhLml0IiwiZXhwIjoxNzI3MjczODEwLCJpYXQiOjE3MjcyNzAyMTAsImNsaWVudF9pZCI6IjQ1YTA4N2Y4LTY4MDYtNDNmNi04NDMxLWQxNWZhMWM5OGYwYyIsImp0aSI6IjgzMTg0Y2FmLTM4ZDktNDQ2NS1iM2JhLTk5NjhhMTQ5YWRjNSJ9.BuHR2cgr8QiGmOUX1rKyEUtvo4tv35VfQYchNPtQ-cgr7fBu0peBJ8tT0Jti3420oulSipvTiVA6M18A9x705j3cckDSUJIUtSjmMWFXJeKgnYMaS58_HvfjHPmcyFyvc8pqaR2wIZ6YAWuVT3rsQWBRySwoXpUGglANDwJ-0IDEpgLHH8n2lDIzGWuss6wKaP2CXdj36savorddN_lL4hCImKYRwVCrWd8eQNpb633mjGzaCe_q7KqqQNoN8OPZAPTU7H3-VKQ_PMUXRPdZc0VasZMRezt6GJ9YRXh-Yv6iKWvwLdzj4-ln6FjdrYIMFAp-_g7_dAbqRYxiFWZv0Q"


    def _get_client_assertion(self):
        """
        Create a client assertion for get PDND voucher
        """

        issued = datetime.datetime.utcnow()
        delta = datetime.timedelta(minutes=43200)
        expire_in = issued + delta
        jti = uuid.uuid4()

        headers_rsa = {
            "kid": KID,
            "alg": ALG,
            "typ": TYP
        }

        payload = {
            "iss": ISSUER,
            "sub": SUBJECT,
            "aud": AUDIENCE,
            "purposeId": PURPOSEID,
            "jti": str(jti),
            "iat": issued,
            "exp": expire_in
        }

        key_path = os.path.join(CURRENT_PATH, TEST_BASE_PATH, PRIVKEY)
        with open(key_path, "rb") as private_key:
            rsaKey = private_key.read()

        return jwt.encode(payload, rsaKey, algorithm="RS256", headers=headers_rsa)

    def _get_voucher(self):
        """ Request a PDND voucher """

        client_assertion = self._get_client_assertion()

        data = {
            'client_id': ISSUER,
            'client_assertion': client_assertion,
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'grant_type': 'client_credentials',
        }

        response = requests.post(TOKENOAUTH_ENDPOINT, data)

        return json.loads(response.content)["access_token"]

    def test_status(self):
        """ Tets /status endpoint """

        qpdnd_project = self.create_qpnd_project(udata={
            "pdnd_audience": "areepercorsedalfuoco",
            "pdnd_eservice_id": "1fe35bd9-d4be-4e10-a4ed-56f98b10f603"
        })

        # Admin01 can pass
        # ----------------
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        url = reverse('qpdnd-api-ogc', args=[qpdnd_project.endpoint]) + "/status"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": 200, "title": "OK"})
        self.assertEqual(response.headers['Content-Type'], 'application/problem+json')

        self.client.logout()

        qpdnd_project.delete()



    def test_auth(self):
        # Create instance
        qpdnd_project = self.create_qpnd_project(udata={
            "pdnd_audience": "areepercorsedalfuoco",
            "pdnd_eservice_id": "1fe35bd9-d4be-4e10-a4ed-56f98b10f603"
        })
        self.assertTrue(qpdnd_project.pk is not None)

        url = reverse('qpdnd-api-ogc', args=[qpdnd_project.endpoint]) + "/collections"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers['Content-Type'], 'application/problem+json')
        self.assertEqual(json.loads(response.content), {
                'status': 401,
                'title': 'Invalid token (empty)'
            },)

        # Admin01 can pass
        # ----------------
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        # Set authorization header
        # ------------------------

        voucher = self._get_voucher()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + voucher}
        response = self.client.get(url, **headers)

        # The following check can works only if a client is set on PDND !!
        # So activate it if you have set a client on PDND portal.
        # ----------------------------------------------------------------
        self.assertEqual(response.status_code, 200, response.content)

        #self.assertEqual(response.status_code, 401, response.content)
        #self.assertEqual(response.content, b'{"status": 401, "title": "PDND purpose eserviceId verification failed"}')