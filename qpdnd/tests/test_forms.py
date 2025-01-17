# coding=utf-8
"""" Test for forms
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-08-16'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.test.client import RequestFactory
from .base import TestQPDNDBase
from qpdnd.forms import QPDNDProjectForm, QPDNDClientSettingForm
from qpdnd.models import QPDNDProject, QPDNDClientSetting
import copy


class TestQPDNDForms(TestQPDNDBase):
    """
    Test QPDND forms module
    """

    @classmethod
    def setUpTestData(cls):
        cls.request = RequestFactory()

    def test_projects(self):


        form = QPDNDProjectForm(request=self.request)
        self.assertFalse(form.is_valid())

        # Test Create
        # -----------
        qpdnd_cs = self.create_qpnd_client_setting()
        form_data = self.create_form_data(uform_data={
            'client_setting': qpdnd_cs
        })

        form = QPDNDProjectForm(request=self.request, data=form_data)
        self.assertTrue(form.is_valid())
        form.save()

        iu_proj = QPDNDProject.objects.get(project=self.project.instance)
        self.assertEqual(iu_proj.contact_author, 'Walter Lorenzetti')
        self.assertEqual(iu_proj.client_setting.pdnd_env, 'test')
        self.assertTrue(iu_proj.client_setting.pdnd_private_key is not None and iu_proj.client_setting.pdnd_private_key != '')

        # Test Update
        # -----------

        initial_form_data = copy.copy(form_data)

        form_data.update({
            'note': 'note test'
        })

        form = QPDNDProjectForm(request=self.request, data=form_data, instance=iu_proj, initial=initial_form_data)
        self.assertTrue(form.is_valid())
        form.save()

        iu_proj.refresh_from_db()
        self.assertEqual(iu_proj.note, 'note test')

        # Test NO WFS ACTIVATED
        # ---------------------
        form_data.update({
            'project': self.project_no_wfs.instance
        })

        form = QPDNDProjectForm(request=self.request, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['project'], ['The project must have almost one vector layer exposed as WFS service!'])


    def test_client_setting(self):

        form = QPDNDClientSettingForm(request=self.request)
        self.assertFalse(form.is_valid())

        # Test Create
        # -----------
        form_data = self.create_client_setting_form_data()

        form = QPDNDClientSettingForm(request=self.request, data=form_data)
        self.assertTrue(form.is_valid())
        form.save()

        cs = QPDNDClientSetting.objects.get(name=form_data['name'])
        self.assertEqual(cs.pdnd_server_issuer, 'c2fc3ed2-a096-4a23-bb2e-47c767fa19d6')
        self.assertEqual(cs.pdnd_api_purpose_verification_url, 'https://api.uat.interop.pagopa.it/1.0/purposes/{purposeId}/agreement')

        # Test Update
        # -----------

        initial_form_data = copy.copy(form_data)

        form_data.update({
            'note': 'note test'
        })

        form = QPDNDClientSettingForm(request=self.request, data=form_data, instance=cs, initial=initial_form_data)
        self.assertTrue(form.is_valid())
        form.save()

        cs.refresh_from_db()
        self.assertEqual(cs.note, 'note test')



