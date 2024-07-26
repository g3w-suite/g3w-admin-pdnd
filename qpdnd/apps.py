from django.apps import AppConfig


class QpdndConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qpdnd'

    def ready(self):

        # Load all QGIS server "filter" and "services" plugins,
        # apps can load additional filters and services by
        # registering them directly to QGS_SERVER
        from . import server_filters
