from django.apps import AppConfig


class MayaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maya'

    def ready(self):
        import maya.signals
