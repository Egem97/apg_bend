"""
Configuración de SQLite para gevent
Este módulo debe importarse ANTES de cualquier import de Django
"""

import sqlite3
import threading
import os
from contextlib import contextmanager

# Lock global para SQLite
_sqlite_lock = threading.RLock()

# Configurar SQLite para ser thread-safe
sqlite3.threadsafety = 1

class ThreadSafeSQLiteConnection:
    """Conexión SQLite thread-safe para gevent"""
    
    def __init__(self, database, **kwargs):
        self.database = database
        self.kwargs = kwargs
        self._connection = None
        self._lock = _sqlite_lock
    
    def __enter__(self):
        with self._lock:
            self._connection = sqlite3.connect(self.database, **self.kwargs)
            # Configurar para mejor rendimiento con gevent
            self._connection.execute('PRAGMA journal_mode=WAL')
            self._connection.execute('PRAGMA synchronous=NORMAL')
            self._connection.execute('PRAGMA cache_size=10000')
            self._connection.execute('PRAGMA temp_store=MEMORY')
            self._connection.execute('PRAGMA locking_mode=EXCLUSIVE')
            return self._connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            with self._lock:
                self._connection.close()

def thread_safe_connect(database, **kwargs):
    """Función thread-safe para conectar a SQLite"""
    # Asegurar que el directorio existe
    db_dir = os.path.dirname(database)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Asegurar permisos de escritura
    if os.path.exists(database):
        try:
            os.chmod(database, 0o666)
        except OSError:
            pass
    
    return ThreadSafeSQLiteConnection(database, **kwargs)

# Reemplazar la función connect de sqlite3
sqlite3.connect = thread_safe_connect

# Función helper para verificar permisos
def ensure_db_permissions(db_path):
    """Asegurar que la base de datos tiene permisos correctos"""
    if os.path.exists(db_path):
        try:
            os.chmod(db_path, 0o666)
            print(f"✅ Permisos establecidos para {db_path}")
        except OSError as e:
            print(f"⚠️ No se pudieron establecer permisos: {e}")
    else:
        # Crear archivo si no existe
        try:
            with open(db_path, 'w') as f:
                pass
            os.chmod(db_path, 0o666)
            print(f"✅ Base de datos creada: {db_path}")
        except OSError as e:
            print(f"❌ Error creando base de datos: {e}")
