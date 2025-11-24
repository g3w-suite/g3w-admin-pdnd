# coding=utf-8
""""
Huey tasks for QPDND plugin
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-11-19 11:53:31'
__copyright__ = 'Copyright Gis3w'

from django.db import close_old_connections
from huey.contrib.djhuey import HUEY
#from huey.contrib.djhuey import db_task
from huey_monitor.tqdm import ProcessInfo
from celery import shared_task, current_task
from celery.utils.log import get_task_logger
from .utils.anncsu import ANNCSUPDND_GestioneCoordinate_API
from .models import ANNCSUProject
from qdjango.apps import  QGS_APPLICATION

from qgis.core import (
    QgsProject, 
    Qgis
)

from functools import wraps
import time

task = HUEY.task

def close_db(fn):
    """Decorator called by db_task() to be used with tasks that may operate
    on the database.

    This implementation is a copy of djhuey implementation but it falls
    back to noop when HUEY.testing is True.

    Set HUEY.testing to True to skip DB connection close.

    """

    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            if not HUEY.immediate and not getattr(HUEY, 'testing', False):
                close_old_connections()
    return inner


def db_task(*args, **kwargs):
    """Decorator to be used with tasks that may operate on the database.

    This implementation is a copy of djhuey implementation but it falls
    back to noop when HUEY.testing is True.

    Set HUEY.testing to True to skip DB connection close.

    """

    def decorator(fn):
        ret = task(*args, **kwargs)(close_db(fn))
        ret.call_local = fn
        return ret
    return decorator


def test_send(anncsu_project_id):

    anncsu_project = ANNCSUProject.objects.get(pk=anncsu_project_id)

   

    qgs_project = QgsProject()
    flags = Qgis.ProjectReadFlags()
    #flags |= Qgis.ProjectReadFlag.DontLoadLayouts
    flags |= Qgis.ProjectReadFlag.DontResolveLayers
    print('arriva')
    qgs_project.read(anncsu_project.project.qgis_file.path, flags)
    #qgs_project.read('/data/www/g3w_suite_data/media/projects/anncsu-la-spezia_anncsu-la-spezia.qgs', flags)
    #qgs_project.read('/data/www/g3w_suite_data/media/projects/processing_qprocessing.qgs', flags)
    print('arriv2')
    qlayer = qgs_project.mapLayers()[anncsu_project.layer.qgs_layer_id]
    print('arriv3')
    print(qlayer.isValid())
    cont = 0
    while not qlayer.isValid() and cont < 20:
        print('pre time')
        time.sleep(0.5)
        QGS_APPLICATION.processEvents()
        print(cont)
        cont += 1

    print(qlayer)

    return {}


@db_task(context=True)
def send_anncsu_pdnd_task(anncsu_project_id, task):
    """
    Task to send ANNCSU PDND data to API.
    """

    #anncsu_project = ANNCSUProject.objects.get(pk=anncsu_project_id)

    # process_info = ProcessInfo(
    #     task,
    #     desc='Send ANNCSU PDND data',
    #     total=len(anncsu_project.get_features())
    # )

    process_info = None

    print('passato tasks')


    # gc = ANNCSUPDND_GestioneCoordinate_API(anncsu_project, process_info)
    
    # gc.send_features()

    res = test_send(anncsu_project_id)

    print('passato dopo tasks')

    return res

@shared_task(name='send_anncsu_pdnd_ceery_task', bind=True)
def send_anncsu_pdnd_ceery_task(self, anncsu_project_id, **kwargs):

    anncsu_project = ANNCSUProject.objects.get(pk=anncsu_project_id)

    print('passato tasks')

    qgs_prj = anncsu_project.project.qgis_project

    #gc = ANNCSUPDND_GestioneCoordinate_API(anncsu_project)
    
    #gc.send_features()

    print('passato dopo tasks')

    return gc

