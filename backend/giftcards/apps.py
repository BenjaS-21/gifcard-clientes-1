from django.apps import AppConfig


class GiftcardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'giftcards'

    def ready(self):
        # Precargar el dashboard al arrancar el servidor (no en migrate, shell, etc.).
        # Con el recargador de runserver, sólo en el proceso que atiende (RUN_MAIN).
        import os
        import sys
        import threading
        if 'runserver' in sys.argv and (os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv):
            from . import dashboard
            threading.Timer(3, dashboard.warm_up).start()
