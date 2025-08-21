#!/bin/bash

# Script para solucionar el error de threading con gevent y SQLite
set -e

echo "🔧 Solucionando error de threading con gevent y SQLite..."

# Detener contenedores
echo "🛑 Deteniendo contenedores..."
docker-compose down

# Verificar que los archivos existen
if [ ! -f "gunicorn_async.py" ]; then
    echo "❌ Error: gunicorn_async.py no encontrado"
    exit 1
fi

# Dar permisos de ejecución
chmod +x gunicorn_async.py

# Limpiar archivos estáticos
echo "🧹 Limpiando archivos estáticos..."
rm -rf staticfiles/*

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Optimizar base de datos para gevent
echo "🗄️ Optimizando base de datos para gevent..."
python manage.py shell -c "
import sqlite3
from django.conf import settings
import os

db_path = settings.DATABASES['default']['NAME']
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA locking_mode=EXCLUSIVE')
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print('✅ Base de datos optimizada para gevent')
else:
    print('⚠️ Base de datos no encontrada')
"

# Reconstruir y ejecutar
echo "🚀 Reconstruyendo y ejecutando con configuración gevent..."
docker-compose up --build -d

# Esperar a que el servidor esté listo
echo "⏳ Esperando a que el servidor esté listo..."
sleep 20

# Verificar que el servidor está funcionando
echo "🔍 Verificando que el servidor está funcionando..."
if curl -f http://localhost:8000/api/ > /dev/null 2>&1; then
    echo "✅ Servidor funcionando correctamente"
else
    echo "❌ Error: Servidor no responde"
    echo "📋 Verificando logs..."
    docker-compose logs --tail=30 web
    exit 1
fi

# Probar el admin
echo "🔐 Probando acceso al admin..."
if curl -f http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Admin accesible"
else
    echo "⚠️ Admin no accesible (puede ser normal si no hay superuser)"
fi

echo "✅ Solución aplicada exitosamente!"
echo ""
echo "📋 Cambios realizados:"
echo "- Monkey patching de gevent al inicio"
echo "- SQLite configurado para thread-safety"
echo "- Workers reducidos a 4 para estabilidad"
echo "- Base de datos optimizada para gevent"
echo ""
echo "🌐 Accede a: http://34.136.15.241:8000/"
echo "📊 Monitorea con: docker-compose logs -f web"
