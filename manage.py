#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    # Logica para criar o admin automaticamente
    # from django.contrib.auth.models import User
    # from your_app.models import Pessoa
    
    # if not User.objects.filter(username='admin').exists():
    #     admin_user = User.objects.create_superuser(
    #         username='admin',
    #         email='admin@escola.com',
    #         password='senhaforte',
    #         first_name='Carlos',
    #         last_name='Administrador'
    #     )
    #     Pessoa.objects.create(
    #         usuario=admin_user,
    #         contato='(11) 9999-8888',
    #         data_prova=timezone.now().date() + timezone.timedelta(days=365)
    #     )
    main()
