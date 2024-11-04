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

        # Add a new user backend type
        from usersmanage.models import USER_BACKEND_TYPES, User, Userbackend
        ubackend = settings.QPDND_INTERNAL_USERBACKEND
        USER_BACKEND_TYPES[ubackend[0]] = ubackend[1]

        # If not exists create new pdnd_internal_user
        try:
            user, created = User.objects.get_or_create(username=settings.QPDND_INTERNAL_USERNAME)
            if created:
                Userbackend(user=user, backend=settings.QPDND_INTERNAL_USERNAME).save()
            else:
                user.userbackend.backend = settings.QPDND_INTERNAL_USERNAME
                user.userbackend.save()
        except Exception as e:
            pass

