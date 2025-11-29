from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    # Alteração feita para lógica de Gerente x Cliente
    def ready(self):
        import app.signals