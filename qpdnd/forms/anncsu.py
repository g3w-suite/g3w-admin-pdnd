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
    Select,
    ChoiceField,
    CharField, 
    JSONField,
    Textarea,
    PasswordInput, 
    Form
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
from usersmanage.configs import (
    G3W_VIEWER1, 
    G3W_VIEWER2
)
from usersmanage.forms import G3WACLForm
from usersmanage.models import User
from qdjango.models import (
    Project
)
from qpdnd.models import (
    ANNCSUProject
)

def anncsuCrispyBoxACL(form, **kwargs):
    """
    Build a Crispy object layout element (div) for on AdminLTE2 box structure.
    :param form: Django form instance
    :return: Crispy form layout object
    """

    bgColorCssClass = kwargs.get('bgColorCssClass', 'bg-purple')
    boxCssClass = kwargs.get('boxCssClass', 'col-md-6')
    userFields = [
        Field('viewer_users', css_class='select2 col-md-12', multiple='multiple', style='width:100%;'),
        Field('viewer_user_groups', css_class='select2 col-md-12', multiple='multiple', style='width:100%;'),
    ]

    return Div(
                Div(
                    Div(
                        HTML("<h3 class='box-title'><i class='fa fa-user'></i> {}</h3>".format(_('ACL Users'))),
                        Div(
                            HTML("<button class='btn btn-box-tool' data-widget='collapse'><i class='fa fa-minus'></i></button>"),
                            css_class='box-tools',
                        ),
                        css_class='box-header with-border'
                    ),
                    Div(
                        *userFields,
                        css_class='box-body'
                    ),
                    css_class='box box-solid {} {}'.format(bgColorCssClass, form.checkEmptyInitialsData(*userFields))
                ),
                css_class='{} acl-box'.format(boxCssClass)
            )


class ANNCSUProjecACLForm(G3WACLForm):
    """
    ACL form for ANNCSUProject model.
    """

    viewer_groups = (G3W_VIEWER1, G3W_VIEWER2)


class ANNCSUProjectForm(G3WFormMixin, G3WRequestFormMixin, G3WACLForm, ModelForm):
    """
    Form for ANNCSUProject model.
    """

    viewer_groups = (G3W_VIEWER1, )


    govway_password = CharField(
        label=_("GovWay API Password"),
        required=False,
        strip=False,
        widget=PasswordInput(), #attrs={'autocomplete': 'new-password'}
    )

    class Meta:
        model = ANNCSUProject
        fields = '__all__'
        widgets = {
            'layer': Select(choices=[])
        }

    def __init__(self, *args, **kwargs):

        # set initial users and user groups
        self._init_users(**kwargs)
        self._init_user_groups(**kwargs)

        super().__init__(*args, **kwargs)

        # change ows_user field label
        self.fields['viewer_users'].label = _('User users')

        # Check if ACLBox must added
        # True only if superuser
        self.aclbox = self.request.user.is_superuser


        # set value for projects select only project not just in config table
        if self.instance.pk:
            project_ids = [c.project.pk for c in ANNCSUProject.objects.filter(~Q(pk=self.instance.pk))]
        else:
            project_ids = [c.project.pk for c in ANNCSUProject.objects.all()]


        # self.fields['project'].queryset = Project.objects.filter(~Q(pk__in=project_ids))
        self.fields['project'].queryset = Project.objects.filter()


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
                                                Field('api_type', css_class='select2'),
                                                Field('project', css_class='select2'),
                                                Field('layer', css_class='select2'),
                                                Field('env_type', css_class='select2'),
                                                Field('codice_comune', css_class='select2'),
                                                'govway_api_endpoint',
                                                'govway_username',
                                                'govway_password',
                                                Field('note', rows="3"),

                                                css_class='box-body',

                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-6'
                                    ),
                                    anncsuCrispyBoxACL(self, boxCssClass='col-md-6') if self.aclbox else None,
                                    css_class='row'
                                ),
                            )
        
    def clean_layer(self):
        """
        Check for fields required
        """

        layer = self.cleaned_data['layer']
        api_type = self.cleaned_data.get('api_type')

        # Check required fields
        # Valid for every apit type
        required_fields = [
            settings.ANNCSU_FIELD_STATO_INVIO,
            settings.ANNCSU_FIELD_DATA_INVIO,
            settings.ANNCSU_FIELD_DIRTY,
            settings.ANNCSU_FIELD_PROGR,
            settings.ANNCSU_FIELD_LAT,
            settings.ANNCSU_FIELD_LON,
            #settings.ANNCSU_FIELD_QUOTA # optional
        ]

        # Additional required fields based on API type
        if api_type == 'aggacc':
            required_fields_accessi = [
                settings.ANNCSU_FIELD_SOPPR,
                settings.ANNCSU_FIELD_PROGR_NAZ,
                settings.ANNCSU_FIELD_NUMERO,
                settings.ANNCSU_FIELD_ESPONENTE,
                settings.ANNCSU_FIELD_METRICO,
                settings.ANNCSU_FIELD_SEZ_CENS,
                settings.ANNCSU_FIELD_DT_VAL_AMM,
                settings.ANNCSU_FIELD_ISOLATO,
                settings.ANNCSU_FIELD_SPECIFICITA,
                settings.ANNCSU_FIELD_COD_CIV_COMUNALE
            ]
            required_fields.extend(required_fields_accessi)

        layer_fields = [f.name() for f in layer.qgis_layer.fields()]
        missing_fields = [field for field in required_fields if field not in layer_fields]

        if missing_fields:
            raise ValidationError(
                _("The layer is missing required fields: {}").format(', '.join(missing_fields))
            )

        return layer
    
    def clean_govway_password(self):

        # if password is not changed, keep the old one
        password = self.cleaned_data.get('govway_password')
        if not password and self.instance.pk:
            password = self.instance.govway_password
        
        # If  govway_username is set, password must be set too
        govway_username = self.cleaned_data.get('govway_username')
        if govway_username and not password:
            raise ValidationError(_("GovWay API password is required when username is set."))
        
        # If govway_username is not set, password reset
        if not govway_username and password:
            password = None
        
        return password
    
    def save(self, commit=True):
        self._ACLPolicy()

        return super().save(commit=commit)
    

class ANNCSUCONSCOMForm(G3WFormMixin, Form):


    # service = ChoiceField(
    #     label=_("Request"),
    #     required=True,
    #     choices=(
    #         ('esisteodonimo', '/esisteodonimo'),
    #         ('esisteodonimo/{codcom}/{denom}', '/esisteodonimo/{codcom}/{denom}'),
    #         ('esisteaccesso', '/esisteaccesso'),
    #         ('esisteaccesso/{codcom}/{denom}/{accesso}', '/esisteaccesso/{codcom}/{denom}/{accesso}'),
    #         ('elencoodonimi', '/elencoodonimi'),
    #         ('elencoodonimi/{codcom}/{denomparz}', '/elencoodonimi/{codcom}/{denomparz}'),
    #         ('elencoaccessi', '/elencoaccessi'),
    #         ('elencoaccessi/{codcom}/{denom}/{accparz}', '/elencoaccessi/{codcom}/{denom}/{accparz}'),
    #         ('elencoodonimiprog', '/elencoodonimiprog'),
    #         ('elencoodonimiprog/{codcom}/{denomparz}', '/elencoodonimiprog/{codcom}/{denomparz}'),
    #         ('elencoaccessiprog', '/elencoaccessiprog'),
    #         ('elencoaccessiprog/{prognaz}/{accparz}', '/elencoaccessiprog/{prognaz}/{accparz}'),
    #         ('prognazarea', '/prognazarea'),
    #         ('prognazarea/{prognaz}', '/prognazarea/{prognaz}'),
    #         ('prognazacc', '/prognazacc'),
    #         ('prognazacc/{prognazacc}', '/prognazacc/{prognazacc}'),
    #         ('status', '/status'),
    #     )
    # )

    payload = JSONField(
        label=_("JSON payload"),
        required=True,
        widget=Textarea(attrs={"rows": 10}),
        help_text=_("Inserisci un JSON valido.")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        HTML("<h3 class='box-title'><i class='fa fa-cog'></i> {}</h3>".format(
                            _('ANNCSU Consultazione Comuni'))),
                        css_class='box-header with-border'
                    ),
                    Div(
                        # Field('service', css_class='select2'),
                        Field('payload', rows='10'),
                        css_class='box-body',
                    ),
                    css_class='box box-success'
                ),
                css_class='col-md-12'
            )
        )
