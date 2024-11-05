# coding=utf-8
""""
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-30'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.dispatch import receiver
from django.template import loader
from django.db.models.signals import pre_save, post_save
from qdjango.views import (
    QdjangoProjectUpdateView,
    QdjangoProjectListView
)
from core.signals import (
    load_js_modules,
    pre_update_project,
    pre_delete_project
)
from usersmanage.models import User
from .utils.general import get_qpdnd_internal_user
from .models import QPDNDProject


@receiver(load_js_modules)
def get_js_modules(sender, **kwargs):

    return 'qpdnd/js/widget.js'


@receiver(pre_update_project)
def check_project_for_update(sender, **kwargs):
    """
    Check project is going to update.
    """

    if isinstance(sender, QdjangoProjectUpdateView):

        # Check for project
        try:
            qpdnd = QPDNDProject.objects.get(project=kwargs['project'])
            kwargs['qpdnd_id'] = qpdnd.id
            msg = loader.get_template('qpdnd/messages/check_project_update.html')
            return msg.render(kwargs)
        except:
            pass


@receiver(pre_delete_project)
def checkProjectForDelete(sender, **kwargs):
    """
    Check project is going to delete.
    """

    if isinstance(sender, QdjangoProjectListView):

        qpdnd_projects = {q.project: q for q in QPDNDProject.objects.all()}
        projects = kwargs['projects']

        if len(qpdnd_projects.keys()) > 0:
            messages = []
            for project in projects:
                if project in qpdnd_projects.keys():
                    msg = loader.get_template('qpdnd/messages/check_project_delete.html')
                    messages.append({
                        'project': project,
                        'message': msg.render({'qpdnd_id': qpdnd_projects[project].id})})
            if len(messages):
                return messages

@receiver(pre_save, sender=QPDNDProject)
def add_remove_permissions(sender, **kwargs):
    try:
        kwargs['instance']._meta.old_instance = sender.objects.get(pk=kwargs['instance'].pk)
    except:
        pass

@receiver(post_save, sender=QPDNDProject)
def add_remove_permissions(sender, **kwargs):

    # Remove view permission to PDND_INTERNAL_USER if is an update
    # ------------------------------------------------------------
    if hasattr(kwargs['instance']._meta, 'old_instance'):
        kwargs['instance']._meta.old_instance.project.removePermissionsToViewers([get_qpdnd_internal_user().pk])

    # Grant view permission to PDND_INTERNAL_USER
    # -------------------------------------------
    kwargs['instance'].project.addPermissionsToViewers([get_qpdnd_internal_user().pk])