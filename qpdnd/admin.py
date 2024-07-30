from django.contrib import admin
from qpdnd.models import (
    QPDNDProject,
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