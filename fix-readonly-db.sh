#!/bin/bash

# Script para solucionar el error "attempt to write a readonly database"
set -e

echo "🔧 Solucionando error de base de datos readonly..."

# Detener contenedores
echo "🛑 Deteniendo contenedores..."
docker-compose down

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py"
    exit 1
fi

# Verificar permisos de la base de datos
echo "🔍 Verificando permisos de la base de datos..."
if [ -f "db.sqlite3" ]; then
    echo "📄 Base de datos encontrada, verificando permisos..."
    ls -la db.sqlite3
    
    # Hacer backup
    echo "💾 Creando backup..."
    cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
    
    # Establecer permisos correctos
    echo "🔐 Estableciendo permisos de escritura..."
    chmod 666 db.sqlite3
    chown $USER:$USER db.sqlite3 2>/dev/null || true
    
    echo "✅ Permisos establecidos"
else
    echo "📄 Creando nueva base de datos..."
    touch db.sqlite3
    chmod 666 db.sqlite3
    chown $USER:$USER db.sqlite3 2>/dev/null || true
fi

# Verificar directorios
echo "📁 Verificando directorios..."
mkdir -p media staticfiles
chmod 755 media staticfiles
chown $USER:$USER media staticfiles 2>/dev/null || true

# Limpiar archivos estáticos
echo "🧹 Limpiando archivos estáticos..."
rm -rf staticfiles/*

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Verificar que los archivos de configuración existen
echo "🔍 Verificando archivos de configuración..."
if [ ! -f "sqlite_gevent.py" ]; then
    echo "❌ Error: sqlite_gevent.py no encontrado"
    exit 1
fi

if [ ! -f "gunicorn_async.py" ]; then
    echo "❌ Error: gunicorn_async.py no encontrado"
    exit 1
fi

# Dar permisos de ejecución
chmod +x gunicorn_async.py

# Optimizar base de datos
echo "🗄️ Optimizando base de datos..."
python manage.py shell -c "
import os
from django.conf import settings

db_path = str(settings.DATABASES['default']['NAME'])
print(f'Base de datos: {db_path}')

if os.path.exists(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA locking_mode=EXCLUSIVE')
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print('✅ Base de datos optimizada')
else:
    print('⚠️ Base de datos no encontrada')
"

# Reconstruir y ejecutar
echo "🚀 Reconstruyendo y ejecutando..."
docker-compose up --build -d

# Esperar a que el servidor esté listo
echo "⏳ Esperando a que el servidor esté listo..."
sleep 25

# Verificar que el servidor está funcionando
echo "🔍 Verificando que el servidor está funcionando..."
for i in {1..5}; do
    if curl -f http://localhost:8000/api/ > /dev/null 2>&1; then
        echo "✅ Servidor funcionando correctamente"
        break
    else
        echo "⏳ Intento $i/5 - Esperando..."
        sleep 5
    fi
done

# Verificar logs si hay problemas
if ! curl -f http://localhost:8000/api/ > /dev/null 2>&1; then
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
echo "- Permisos de escritura establecidos en db.sqlite3"
echo "- Configuración SQLite thread-safe para gevent"
echo "- Base de datos optimizada con WAL mode"
echo "- Directorios media y staticfiles configurados"
echo ""
echo "🌐 Accede a: http://34.136.15.241:8000/"
echo "📊 Monitorea con: docker-compose logs -f web"
echo ""
echo "🔧 Si persiste el error, ejecuta:"
echo "   sudo chown -R \$USER:\$USER ."
echo "   chmod 666 db.sqlite3"
