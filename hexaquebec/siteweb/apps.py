from django.apps import AppConfig


class SitewebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'siteweb'




from django.apps import AppConfig


class StagiairesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stagiaires"
    verbose_name = "Espace stagiaires HexaQuébec"

    def ready(self):
        from . import signals