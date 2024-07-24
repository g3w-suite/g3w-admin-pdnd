# coding=utf-8
""""QPDND forms module

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__copyright__ = 'Copyright Gis3w'


from django.conf import settings
from django.forms.models import ModelForm
from django.forms import (
    CharField,
    HiddenInput
)
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Div,
    HTML,
    Row,
    Field,
    Hidden
)
from usersmanage.utils import (
    crispyBoxACL,
    userHasGroups
)
from usersmanage.configs import G3W_EDITOR1
from core.mixins.forms import (
    G3WRequestFormMixin,
    G3WFormMixin
)
from .models import (
    QPDNDProject,
    QPDNDLayer
)

from .utils import allowed_layers_for_reporting


class QPDNDProjectForm(G3WFormMixin, G3WRequestFormMixin, ModelForm):
    """
    Form for QPDNDProject model.
    """
    class Meta:
        model = QPDNDProject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields = [
            Field('project', css_class='select2'),
        ]

        fields.append(Field('note', css_class='wys5'))

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Project'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                *fields,
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-12'
                                    ),
                                    css_class='row'
                                ),
                            )


class QPDNDLayerForm(G3WFormMixin, G3WRequestFormMixin, ModelForm):
    """
    Form for QPDNDLayer model.
    """

    class Meta:
        model = QPDNDLayer
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        self.qpdnd_project_instance = kwargs['qpdnd_project']
        del (kwargs['qpdnd_project'])

        super().__init__(*args, **kwargs)

        # build queryset for reporting vector layer
        self.fields['layer'].queryset = allowed_layers_for_reporting(self.qpdnd_project_instance)

        self.initial['qpdnd_project'] = self.qpdnd_project_instance

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Vector layer to expose'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Field('qpdnd_project', type='hidden'),
                                                'layer',
                                                Field('note', css_class='wys5'),
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-12'
                                    ),
                                    css_class='row'
                                ),
                            )