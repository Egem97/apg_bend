#!/usr/bin/env python3
"""
Script de entrada para Gunicorn con gevent
Importa gevent ANTES de cualquier import de Django
"""

# Importar gevent ANTES que cualquier otra cosa
import gevent.monkey
gevent.monkey.patch_all()

# Configurar SQLite para gevent
import sqlite3
import threading

# Hacer SQLite thread-safe
sqlite3.threadsafety = 1

# Lock global para SQLite
_sqlite_lock = threading.Lock()

def sqlite_connect(*args, **kwargs):
    """Conexión SQLite thread-safe"""
    with _sqlite_lock:
        return sqlite3.connect(*args, **kwargs)

# Reemplazar la función connect
sqlite3.connect = sqlite_connect

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
