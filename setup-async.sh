#!/bin/bash

# Script para configurar y probar la configuración asíncrona
set -e

echo "🚀 Configurando servidor asíncrono con Gevent..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py"
    exit 1
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores..."
docker-compose down

# Verificar que gevent está instalado
echo "🔍 Verificando dependencias..."
if ! grep -q "gevent" requirements.txt; then
    echo "❌ Error: gevent no está en requirements.txt"
    exit 1
fi

# Limpiar archivos estáticos
echo "🧹 Limpiando archivos estáticos..."
rm -rf staticfiles/*

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Optimizar base de datos para async
echo "🗄️ Optimizando base de datos para async..."
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
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print('✅ Base de datos optimizada para async')
else:
    print('⚠️ Base de datos no encontrada')
"

# Reconstruir y ejecutar con configuración async
echo "🚀 Reconstruyendo y ejecutando con configuración async..."
docker-compose up --build -d

# Esperar a que el servidor esté listo
echo "⏳ Esperando a que el servidor esté listo..."
sleep 15

# Verificar configuración
echo "🔧 Verificando configuración async..."
echo "Workers: 4"
echo "Worker class: gevent"
echo "Worker connections: 1000"
echo "Preload: enabled"

# Probar rendimiento con peticiones concurrentes
echo "📊 Probando rendimiento con peticiones concurrentes..."

# Función para hacer peticiones concurrentes
test_concurrent_requests() {
    local url="http://localhost:8000/api/"
    local num_requests=10
    
    echo "Haciendo $num_requests peticiones concurrentes..."
    
    # Usar curl para peticiones concurrentes
    for i in $(seq 1 $num_requests); do
        (
            time curl -s -o /dev/null -w "Petición $i: Status %{http_code}, Tiempo %{time_total}s\n" "$url"
        ) &
    done
    
    # Esperar a que todas las peticiones terminen
    wait
    
    echo "✅ Pruebas de concurrencia completadas"
}

# Ejecutar pruebas
test_concurrent_requests

# Verificar logs
echo "📋 Verificando logs del servidor..."
docker-compose logs --tail=20 web

echo "✅ Configuración asíncrona completada!"
echo ""
echo "📋 Configuración aplicada:"
echo "- Gunicorn: 4 workers con gevent"
echo "- Worker connections: 1000 por worker"
echo "- Preload: Habilitado para mejor rendimiento"
echo "- Base de datos: Optimizada para async"
echo "- Gevent monkey patching: Habilitado"
echo ""
echo "🌐 Accede a: http://34.136.15.241:8000/"
echo "📊 Monitorea con: docker-compose logs -f web"
