#!/usr/bin/env python3
"""
Script de entrada para Gunicorn con gevent
Importa gevent ANTES de cualquier import de Django
"""

# Importar gevent ANTES que cualquier otra cosa
import gevent.monkey
gevent.monkey.patch_all()

# Importar configuración SQLite thread-safe
import sqlite_gevent

# Ahora importar Django
import os
import django
from django.core.wsgi import get_wsgi_application

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_backend.settings')
django.setup()

# Obtener la aplicación WSGI
application = get_wsgi_application()

if __name__ == "__main__":
    # Para desarrollo local
    from gunicorn.app.wsgiapp import WSGIApplication
    WSGIApplication().run()
