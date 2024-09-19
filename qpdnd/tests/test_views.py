# coding=utf-8
"""" Test for views
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-08-29'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.urls import reverse
from guardian.shortcuts import assign_perm

from .base import (
    TestQPDNDBase,
    CURRENT_PATH,
    TEST_BASE_PATH
)
from qpdnd.views import (
    QPDNDProjectDeleteView,
    QPDNDProjectsListView,
    QPDNDProjectAddView,
    QPDNDProjectUpdateView
)
from qpdnd.models import QPDNDProject, License
import json
import os



class TestQPDNDViews(TestQPDNDBase):
    """
    Test qpdnd views module
    """


    def test_projects(self):

        url = reverse('qpdnd-project-add')

        # Login required
        res = self.client.post(url,data={})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(f'/en/login/?next={url}' in res.headers['Location'])

        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        data = self.create_form_data(uform_data={
            'project': self.project.instance.pk,
            'license': '2'
        })

        res = self.client.post(url, data=data)

        # Check redirect after save to page list
        self.assertEqual(res.status_code, 302)

        self.assertEqual(QPDNDProject.objects.count(), 1)

        # Test update
        url = reverse('qpdnd-project-update', kwargs={'pk': QPDNDProject.objects.all()[0].pk})

        data.update({
            'version': '1.0.1',
        })

        res = self.client.post(url, data=data)

        # Check redirect after save to page list
        self.assertEqual(res.status_code, 302)

        self.assertEqual(QPDNDProject.objects.count(), 1)

        # Test delete
        url = reverse('qpdnd-project-delete', kwargs={'pk': QPDNDProject.objects.all()[0].pk})

        res = self.client.post(url, data={'project': self.project.instance.pk})

        # Check redirect after save to page list
        self.assertEqual(res.status_code, 200)

        self.assertEqual(QPDNDProject.objects.count(), 0)

        self.client.logout()

    def test_ocg_api(self):
        """
        Test for wrapper QGIS server ogc api
        """

        # Create instance
        qpdnd_project = self.create_qpnd_project()
        self.assertTrue(qpdnd_project.pk is not None)

        # To avoid auto generation of z_api_id
        # qpdnd_project.x_api_id = '0bb5b19c-11e5-4f31-b8a2-6269822b29cc'
        # qpdnd_project.save()

        # Test OGC API endpoint
        # -------------------------------------------

        # Test Landing Page
        url = reverse('qpdnd-api-ogc', args=[qpdnd_project.endpoint])

        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        # / (landing page)
        #-----------------
        response = self.client.get(f'{url}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        to_compare = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'openapi/open.api.landingpage.json')
        with open(to_compare, 'r') as f:
            to_compare_json = f.read()

        # Compare only `links` because timestamp change on every request
        to_compare_dict = json.loads(to_compare_json)
        self.assertEqual(to_compare_dict['links'], json.loads(response.content)['links'])

        # /api.openapi3
        # -------------
        response = self.client.get(f'{url}/api.openapi3')
        self.assertEqual(response.headers['Content-Type'], 'application/vnd.oai.openapi+json;version=3.0')

        to_compare = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'openapi/open.api.schema.json')
        with open(to_compare, 'r') as f:
            to_compare_json = f.read()

        to_compare_dict = json.loads(to_compare_json)
        self.assertEqual(to_compare_dict, json.loads(response.content))


        self.client.logout()

    def test_download_openapi_schema(self):
        """
        Test download view for openapi schema
        """

        # Create instance
        qpdnd_project = self.create_qpnd_project()
        self.assertTrue(qpdnd_project.pk is not None)

        url = reverse('qpdnd-api-ogc', args=[qpdnd_project.endpoint])
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        response = self.client.get(f'{url}/api.openapi3')
        self.assertFalse('Content-Disposition' in response.headers)

        response = self.client.get(f'{url}/api.openapi3?download=0')
        self.assertFalse('Content-Disposition' in response.headers)

        response = self.client.get(f'{url}/api.openapi3?download=1')
        self.assertTrue('Content-Disposition' in response.headers)
        self.assertEqual(response.headers['Content-Disposition'], f'attachment; filename="{qpdnd_project.endpoint}.api.openapi3.json"')
        self.assertEqual(response.headers['Content-Type'], 'application/vnd.oai.openapi+json;version=3.0')

        to_compare = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'openapi/open.api.schema.json')
        with open(to_compare, 'r') as f:
            to_compare_json = f.read()

        to_compare_dict = json.loads(to_compare_json)
        self.assertEqual(to_compare_dict, json.loads(response.content))

        # Download only for /api.openapi3
        response = self.client.get(f'{url}')
        self.assertFalse('Content-Disposition' in response.headers)

        self.client.logout()

    def test_projectinfo_api(self):
        """
        Test project info api
        """

        # TODO: add test for permissions

        url = reverse('qpdnd-api-prj-info', args=[self.project.instance.pk])

        # Test not login user
        # -------------------
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test user logged without permission
        # -----------------------------------
        self.client.login(username=self.test_editor1.username, password=self.test_editor1.username)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test user logged with permission
        # --------------------------------
        assign_perm('change_project', self.test_editor1, self.project.instance)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        # Test as admin01
        # ---------------
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.headers['Content-Type'], 'application/json')

        to_compare = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'projectinfo/response.json')
        with open(to_compare, 'r') as f:
            to_compare_json = f.read()

        to_compare_dict = json.loads(to_compare_json)
        self.assertEqual(to_compare_dict, json.loads(response.content))

        self.client.logout()









