from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from qpdnd.models import (
    QPDNDProject, 
    ANNCSUProject,
    License, 
    IstatCodiciUi
)

@admin.register(QPDNDProject)
class QPDNDProjectAdmin(admin.ModelAdmin):
   list_display = [
       'project',
       'endpoint'
   ]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
   pass

@admin.register(ANNCSUProject)
class ANNCSUProjectAdmin(GuardedModelAdmin):
   list_display = [
       'project',
       'layer',
       'env_type',
   ]

@admin.register(IstatCodiciUi)
class IstatCodiciUiAdmin(admin.ModelAdmin):
   pass
