from django.apps import AppConfig


class FiordispinoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiordispino'

    def ready(self):
        import fiordispino.signals # load signals at startup