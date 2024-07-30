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
from core.signals import load_js_modules


@receiver(load_js_modules)
def get_js_modules(sender, **kwargs):

    return 'qpdnd/js/widget.js'