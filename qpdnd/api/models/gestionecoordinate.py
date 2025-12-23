# coding=utf-8
""""
Pydantic models for gestionecoordinate API
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-11-18 17:28:05'
__copyright__ = 'Copyright Gis3w'


from pydantic import (
    BaseModel, 
    field_validator
)

from .coordinate import Coordinate

import re

class Accesso(BaseModel):
    codcom: str
    progr_civico: str
    coordinate: Coordinate

    @field_validator("codcom")
    def validate_codcom(cls, value):
        pattern = r"^[A-Za-z][0-9]{3}$"
        if not re.match(pattern, value):
            raise ValueError("codcom deve essere nel formato: 1 carattere alfanumerico + 3 cifre (es. B432)")
        return value

    @field_validator("progr_civico")
    def validate_prog_civico(cls, value):
        try:
            int(value)
        except ValueError:
            raise ValueError("prog_civico deve essere un valore numerico rappresentato come stringa")
        return value