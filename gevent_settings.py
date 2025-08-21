# Configuración de gevent para Django
# Este archivo debe importarse ANTES de cualquier import de Django

import gevent.monkey
gevent.monkey.patch_all()

# Configuraciones específicas para SQLite con gevent
import sqlite3
import threading

# Hacer SQLite thread-safe para gevent
sqlite3.threadsafety = 1

# Configurar el lock global para SQLite
_sqlite_lock = threading.Lock()

def sqlite_connect(*args, **kwargs):
    """Función wrapper para conexiones SQLite thread-safe"""
    with _sqlite_lock:
        return sqlite3.connect(*args, **kwargs)

# Reemplazar la función connect de sqlite3
sqlite3.connect = sqlite_connect
