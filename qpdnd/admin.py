from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from qpdnd.models import (
    QPDNDProject, 
    ANNCSUProject,
    ANNCSUTaskHistory,
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


class ANNCSUTaskHistoryInline(admin.TabularInline):
    model = ANNCSUTaskHistory
    extra = 0
    can_delete = False
    fields = ['user', 'send_type', 'status', 'started_at', 'ended_at', 'task_id']
    readonly_fields = ['user', 'send_type', 'status', 'started_at', 'ended_at', 'task_id']
    show_change_link = True
    ordering = ('-started_at',)

    def has_add_permission(self, request, obj=None):
        return False


ANNCSUProjectAdmin.inlines = [ANNCSUTaskHistoryInline]


@admin.register(IstatCodiciUi)
class IstatCodiciUiAdmin(admin.ModelAdmin):
   pass


@admin.register(ANNCSUTaskHistory)
class ANNCSUTaskHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'anncsu_project',
        'user',
        'send_type',
        'status',
        'started_at',
        'ended_at',
        'duration',
        'task_id',
    ]
    list_filter = ['status', 'send_type', 'anncsu_project']
    search_fields = ['task_id', 'user__username', 'anncsu_project__project__title']
    raw_id_fields = ['anncsu_project', 'user']
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)
    readonly_fields = [
        'anncsu_project',
        'user',
        'send_type',
        'status',
        'task_id',
        'started_at',
        'ended_at',
        'results',
        'duration',
    ]
    fieldsets = (
        (None, {
            'fields': ('anncsu_project', 'user', 'send_type', 'task_id', 'status'),
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'duration'),
        }),
        ('Result', {
            'fields': ('results',),
        }),
    )

    def duration(self, obj):
        if obj.started_at and obj.ended_at:
            return obj.ended_at - obj.started_at
        return '-'
    duration.short_description = 'Duration'

    def has_add_permission(self, request):
        return False
