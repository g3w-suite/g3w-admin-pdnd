# coding=utf-8
""""QPDND forms module

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__copyright__ = 'Copyright Gis3w'


from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Div,
    HTML,
    Field,
)
from core.mixins.forms import (
    G3WRequestFormMixin,
    G3WFormMixin
)
from .models import QPDNDProject
import re


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

        fields_info_data = [
            'endpoint',
            'version',
            'contact_author',
            'contact_email',
            'contact_url',
            'title',
            'description',
            'x_summary',
            Field('license', css_class='select2'),
            'terms_of_service',
            Field('note', css_class='wys5'),
        ]

        fields_pdnd = [
            Field('pdnd_env', css_class='select2'),
            'pdnd_audience',
            'pdnd_eservice_id'
        ]

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
                                    Div(
                                        Div(
                                            Div(
                                                Div(
                                                    HTML(
                                                        "<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                            _('Info data'))),
                                                    css_class='box-header with-border'
                                                ),
                                                Div(
                                                    *fields_info_data,
                                                    css_class='box-body',
                                                ),
                                                css_class='box box-success'
                                            ),
                                            css_class='col-md-6'
                                        ),
                                        Div(
                                            Div(
                                                Div(
                                                    HTML(
                                                        "<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                            _('PDND data'))),
                                                    css_class='box-header with-border'
                                                ),
                                                Div(
                                                    *fields_pdnd,
                                                    css_class='box-body',
                                                ),
                                                css_class='box box-success'
                                            ),
                                            css_class='col-md-6'
                                        ),
                                        css_class='row'
                                    ),
                            )

    def clean_version(self, *args, **kwargs):
        version = self.cleaned_data['version']
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z]+[0-9]*)?$'

        if re.match(pattern, version):
            return version
        else:
            raise ValidationError(_("Is not a valid version format!"))

    def clean_project(self):
        """
        Check if WFS for almost one layer is active
        """

        prj = self.cleaned_data['project']
        wfs_active = False
        for l in prj.layer_set.all():
            if l.wfscapabilities:
                wfs_active = True

        if not wfs_active:
            raise ValidationError(_("The project must have almost one vector layer exposed as WFS service!"))
        return prj