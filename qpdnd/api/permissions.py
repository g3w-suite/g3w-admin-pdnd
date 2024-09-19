# coding=utf-8
""""
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-09-19'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from rest_framework.permissions import BasePermission
from qdjango.models import Project


class ProjectEditPermission(BasePermission):
    """
    Allows access only to users have edit permission on project
    """

    def has_permission(self, request, view):

        func, args, kwargs = request.resolver_match

        project = Project.objects.get(pk=kwargs['project_id'])
        return request.user.has_perm('qdjango.change_project', project)