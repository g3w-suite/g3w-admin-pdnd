# coding=utf-8
""""
    General utilities
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-11-04'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.conf import settings
from usersmanage.models import User

def get_qpdnd_internal_user():
    """
    Return the qpdnd internal user instance
    """
    try:
        return User.objects.get(username=settings.QPDND_INTERNAL_USERNAME)
    except:
        return None