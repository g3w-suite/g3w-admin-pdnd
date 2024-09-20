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
from qpdnd.forms import QPDNDProjectForm
from qpdnd.models import QPDNDProject
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
        form_data = self.create_form_data()

        form = QPDNDProjectForm(request=self.request, data=form_data)
        self.assertTrue(form.is_valid())
        form.save()

        iu_proj = QPDNDProject.objects.get(project=self.project.instance)
        self.assertEqual(iu_proj.pdnd_env, 'test')
        self.assertEqual(iu_proj.pdnd_audience, 'test_audience')

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







