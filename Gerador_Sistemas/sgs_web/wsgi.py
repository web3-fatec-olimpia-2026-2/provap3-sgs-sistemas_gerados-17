"""WSGI da tela do SGS (o runserver usa este application)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sgs_web.settings")
application = get_wsgi_application()
