from django.contrib import admin
from qpdnd.models import (
    QPDNDProject, 
    ANNCSUProject,
    License
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
class ANNCSUProjectAdmin(admin.ModelAdmin):
   list_display = [
       'project',
       'layer'
   ]

