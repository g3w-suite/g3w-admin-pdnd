# coding=utf-8
""""
 Forms for ANNCSU PDND extension
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-10-14 08:54:09'
__copyright__ = 'Copyright Gis3w'


from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm, 
    Select
)
from django.db.models import Q  
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
from qdjango.models import (
    Project
)
from qpdnd.models import (
    ANNCSUProject
)


class ANNCSUProjectForm(G3WFormMixin, G3WRequestFormMixin, ModelForm):
    """
Form for ANNCSUProject model.
    """

    class Meta:
        model = ANNCSUProject
        fields = '__all__'
        widgets = {
            'layer': Select(choices=[])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set value for projects select only project not just in config table
        if self.instance.pk:
            project_ids = [c.project.pk for c in ANNCSUProject.objects.filter(~Q(pk=self.instance.pk))]
        else:
            project_ids = [c.project.pk for c in ANNCSUProject.objects.all()]


        self.fields['project'].queryset = Project.objects.filter(~Q(pk__in=project_ids))


        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-cog'></i> {}</h3>".format(
                                                    _('ANNCSU PDND Project'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Field('project', css_class='select2'),
                                                Field('layer', css_class='select2'),
                                                Field('env_type', css_class='select2'),
                                                Field('codice_comune', css_class='select2'),
                                                'govway_api_endpoint',
                                                Field('note', rows="3"),

                                                css_class='box-body',

                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-6'
                                    ),
                                    css_class='row'
                                )
                            )
        
    def clean_layer(self):
        """
        Check for fields required
        """

        layer = self.cleaned_data['layer']

        # Check required fields
        required_fields = [
            settings.ANNCSU_FIELD_STATO_INVIO,
            settings.ANNCSU_FIELD_DATA_INVIO,
            settings.ANNCSU_FIELD_DIRTY,
            settings.ANNCSU_FIELD_PROGR,
            settings.ANNCSU_FIELD_LAT,
            settings.ANNCSU_FIELD_LON,
            #settings.ANNCSU_FIELD_QUOTA # optional
        ]

        layer_fields = [f.name() for f in layer.qgis_layer.fields()]
        missing_fields = [field for field in required_fields if field not in layer_fields]

        if missing_fields:
            raise ValidationError(
                _("The layer is missing required fields: {}").format(', '.join(missing_fields))
            )

       
        return layer