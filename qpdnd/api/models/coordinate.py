# coding=utf-8
""""

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-12-23 14:02:37'
__copyright__ = 'Copyright Gis3w'


from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints


class Coordinate(BaseModel):
    x: Annotated[str, StringConstraints(max_length=12)] | None = Field(
        None,
        description='Coordinata X, obbligatoria se viene valorizzata Y. (Valori ammessi in Italia 6.0 ≤ x ≤ 18.0)',
        example='13.1022000',
    )
    y: Annotated[str, StringConstraints(max_length=12)] | None = Field(
        None,
        description='Coordinata Y, obbligatoria se viene valorizzata X. (Valori ammessi in Italia 36.0 ≤ y ≤ 47.0)',
        example='41.8847600',
    )
    z: Annotated[str, StringConstraints(max_length=7)] | None = Field(
        None,
        description='Quota, da non valorizzare in assenza di X e Y, espressa in metri',
        example='150',
    )
    metodo: Annotated[str, StringConstraints(max_length=1)] | None = Field(
        None,
        description='Metodo di rilevazione, da non valorizzare in assenza di X e Y',
        example='3',
    )