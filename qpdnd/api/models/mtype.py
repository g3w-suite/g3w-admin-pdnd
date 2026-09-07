# coding=utf-8
""""

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2026-02-13 14:51:16'
__copyright__ = 'Copyright Gis3w'


from enum import Enum

# Pydantic models for mtype API
# Tipo di operazione (I: inserimento, R: rimozione, S: sospensione)
class TipoOperazione(Enum):
    I = 'I'
    R = 'R'
    S = 'S'
