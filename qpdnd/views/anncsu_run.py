# coding=utf-8
""""
Anncsu PDND send to API
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-11-19 09:22:24'
__copyright__ = 'Copyright Gis3w'


from django.views.generic import TemplateView
from huey.contrib.djhuey import HUEY
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from huey import signals
from core.utils.qgisapi import count_qgis_features
from qpdnd.models import ANNCSUProject
from qpdnd.settings import (
    _BASE_URL_INFO_TASK, 
    _BASE_URL_KILL_TASK
)



class ANNCSURunView(TemplateView):
    """
    ANNCSU PDND run view.
    """
    template_name = 'qpdnd/anncsu/run.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Get QGIS layewr instance
        ctx['anncsu_project'] = ANNCSUProject.objects.get(pk=kwargs.get('pk'))
        ctx['layer'] = ctx['anncsu_project'].layer
        ctx['qgs_layer'] = ctx['layer'].qgis_layer

        # Feacture count
        ctx['num_features'] = count_qgis_features(ctx['qgs_layer'])

        # Task id
        ctx['BASE_URL_INFO_TASK'] = _BASE_URL_INFO_TASK
        ctx['BASE_URL_KILL_TASK'] = _BASE_URL_KILL_TASK
        if ctx['anncsu_project'].task_id:
            ctx['task_model'] = ctx['anncsu_project'].get_task()

            # Calculate duration
            if ctx['task_model'].update_dt and ctx['task_model'].create_dt:
                delta = ctx['task_model'].update_dt - ctx['task_model'].create_dt
                total_seconds = delta.total_seconds()
                days = int(total_seconds // 86400)
                hours = int((total_seconds % 86400) // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                
                duration_parts = []
                if days > 0:
                    duration_parts.append(f"{days}g")
                if hours > 0:
                    duration_parts.append(f"{hours}h")
                if minutes > 0:
                    duration_parts.append(f"{minutes}m")
                if seconds > 0 or not duration_parts:
                    duration_parts.append(f"{seconds}s")
                
                ctx['task_duration'] = " ".join(duration_parts)

            # Get tasks results
            try:
                ctx['task_results'] = HUEY.result(ctx['anncsu_project'].task_id)
            except TaskException:
                ctx['task_results'] = None
        
        # Task huey signals
        ctx['huey_signals'] = signals

        return ctx
