# coding=utf-8
""""
Test for models of QPDND plugin
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-09-17'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'


from .base import TestQPDNDBase
from qpdnd.models import (
    QPDNDProject,
    License
)
import copy


class TestQPDNDModels(TestQPDNDBase):
    """
    Test QPDND models
    """

    def test_project(self):

        qpdnd_project = self.create_qpnd_project(udata={
            'license': License.objects.get(pk=2),
        })
        self.assertTrue(qpdnd_project.pk is not None)

        # Check x_api_id not change on update
        x_api_id = qpdnd_project.x_api_id

        qpdnd_project.version = '1.0.1'
        qpdnd_project.save()

        # Reload data from db
        qpdnd_project = QPDNDProject.objects.get(pk=qpdnd_project.pk)

        self.assertEqual(x_api_id, qpdnd_project.x_api_id)

        qpdnd_project.delete()

        # Test set a custom x_api_id
        # --------------------------
        # Create instance
        qpdnd_project = self.create_qpnd_project(udata={
            'x_api_id': 'test_code_api_id'
        })

        self.assertTrue(qpdnd_project.pk is not None)

        self.assertEqual('test_code_api_id', qpdnd_project.x_api_id)

        # Check x_api_id not change on update
        # -----------------------------------
        x_api_id = qpdnd_project.x_api_id

        qpdnd_project.version = '1.0.1'
        qpdnd_project.save()

        # Reload data from db
        qpdnd_project = QPDNDProject.objects.get(pk=qpdnd_project.pk)

        self.assertEqual(x_api_id, qpdnd_project.x_api_id)

        # Test update x_api_id on update
        # ------------------------------
        qpdnd_project.version = '1.0.2'
        qpdnd_project.x_api_id= 'test_for_update_id'
        qpdnd_project.save()

        # Reload data from db
        qpdnd_project = QPDNDProject.objects.get(pk=qpdnd_project.pk)

        self.assertEqual('1.0.2', qpdnd_project.version)
        self.assertEqual('test_for_update_id', qpdnd_project.x_api_id)



