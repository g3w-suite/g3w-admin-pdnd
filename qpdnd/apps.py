from django.apps import AppConfig


class QpdndConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qpdnd'

    def ready(self):

        # Load all QGIS server "filter" and "services" plugins,
        # apps can load additional filters and services by
        # registering them directly to QGS_SERVER
        from . import server_filters
        from . import receivers

        # Add default settings for module
        from django.conf import settings
        from qpdnd import settings as qpdnd_settings

        for a in dir(qpdnd_settings):
            if not a.startswith('__') and not hasattr(settings, a):
                setattr(settings, a, getattr(qpdnd_settings, a))
