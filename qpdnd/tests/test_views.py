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
from .base import TestQPDNDBase
from qpdnd.views import (
    QPDNDProjectDeleteView,
    QPDNDProjectsListView,
    QPDNDProjectAddView,
    QPDNDProjectUpdateView
)
from qpdnd.models import QPDNDProject



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

        data = {
            'project': self.project.instance.pk,
            'endpoint': 'point',
            'version': '1.0.0',
            'terms_of_service': 'https://smartbear.com/terms-of-use/',
            'contact_author': 'Walter Lorenzetti',
            'contact_email': 'lorenzetti@gis3w.it',
            'contact_url': 'https://gis3w.it',
            'title': 'Title of service',
            'x_summary': 'Brief description',
            'license': '2'
        }
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








