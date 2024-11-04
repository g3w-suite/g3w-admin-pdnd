# coding=utf-8
""""
    Base testing module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-12-28'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.files import File
from core.models import G3WSpatialRefSys, Group as CoreGroup
from usersmanage.tests.utils import setup_testing_user, User, Userbackend
from qdjango.utils.data import QgisProject
from qpdnd.models import QPDNDProject, License
import os


CURRENT_PATH = os.path.dirname(__file__)
TEST_BASE_PATH = 'data/'
DATASOURCE_PATH = '{}/{}project_data'.format(CURRENT_PATH, TEST_BASE_PATH)

QGS_PROJECT_FILE = 'projects/test_ogc_api.qgs'
QGS_PROJECT_FILE_NO_WFS_ACTIVED = 'projects/test_ogc_api_no_wfs_actived.qgs'



@override_settings(
    CACHES={
        'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'some',
        }
    },
    DATASOURCE_PATH=DATASOURCE_PATH,
    LANGUAGE_CODE='en',
    LANGUAGES = (
        ('en', 'English'),
    ),
)
class TestQPDNDBase(TestCase):

    fixtures = ['BaseLayer.json',
                'G3WMapControls.json',
                'G3WSpatialRefSys.json',
                'G3WGeneralDataSuite.json',
                'license.json'
                ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        setup_testing_user(cls)

        cls.qgis_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_FILE)
        cls.qgis_file_no_wfs_actived = os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_FILE_NO_WFS_ACTIVED)

        user, created = User.objects.get_or_create(username=settings.QPDND_INTERNAL_USERNAME)
        if created:
            Userbackend(user=user, backend=settings.QPDND_INTERNAL_USERNAME).save()
        else:
            user.userbackend.backend = settings.QPDND_INTERNAL_USERNAME
            user.userbackend.save()

    @classmethod
    def setUp(cls):

        # Main project group
        cls.project_group = CoreGroup(name='QPDND', title='QPDND', header_logo_img='',
                                      srid=G3WSpatialRefSys.objects.get(auth_srid=4326))
        cls.project_group.save()

        # Add projects to DB
        qgis_file = File(open(cls.qgis_file, 'r'))
        cls.project = QgisProject(qgis_file)
        cls.project.title = 'OGC API test project'
        cls.project.group = cls.project_group
        cls.project.save()

        qgis_file = File(open(cls.qgis_file_no_wfs_actived, 'r'))
        cls.project_no_wfs = QgisProject(qgis_file)
        cls.project_no_wfs.title = 'OGC API test project NO WFS ACTIVED'
        cls.project_no_wfs.group = cls.project_group
        cls.project_no_wfs.save()

    def create_form_data(self, uform_data: dict={})-> dict:
        """
        Create form data for forms and views tests
        """

        form_data = {
            'project': self.project.instance,
            'endpoint': 'point',
            'version': '1.0.0',
            'terms_of_service': 'https://smartbear.com/terms-of-use/',
            'contact_author': 'Walter Lorenzetti',
            'contact_email': 'lorenzetti@gis3w.it',
            'contact_url': 'https://gis3w.it',
            'title': 'Title of service',
            'x_summary': 'Brief description',
            'license': '1',
            'pdnd_env': 'test',
            'pdnd_audience': 'test_audience',
            'pdnd_eservice_id': '929ce5a1-2e82-4e37-bdce-c76bfd66407d'

        }

        form_data.update(uform_data)

        return form_data

    def create_qpnd_project(self, udata: dict={}) -> QPDNDProject:
        """
        Create qpdndproject instance
        """

        # Create instance
        data = {
            'project': self.project.instance,
            'endpoint': 'point',
            'version': '1.0.0',
            'terms_of_service': 'https://smartbear.com/terms-of-use/',
            'contact_author': 'Walter Lorenzetti',
            'contact_email': 'lorenzetti@gis3w.it',
            'contact_url': 'https://gis3w.it',
            'title': 'Title of service',
            'x_summary': 'Brief description',
            'license': License.objects.get(pk=3),
            'x_api_id': '0bb5b19c-11e5-4f31-b8a2-6269822b29cc',
            'pdnd_env': 'test',
            'pdnd_audience': 'test_audince',
            'pdnd_eservice_id': '929ce5a1-2e82-4e37-bdce-c76bfd66407d'
        }

        data.update(udata)

        return QPDNDProject.objects.create(**data)
