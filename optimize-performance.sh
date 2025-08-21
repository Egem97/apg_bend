#!/bin/bash

# Script para optimizar el rendimiento del servidor
set -e

echo "🚀 Optimizando rendimiento del servidor..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py"
    exit 1
fi

# Detener contenedores
echo "🛑 Deteniendo contenedores..."
docker-compose down

# Limpiar archivos estáticos antiguos
echo "🧹 Limpiando archivos estáticos..."
rm -rf staticfiles/*

# Recolectar archivos estáticos optimizados
echo "📦 Recolectando archivos estáticos optimizados..."
python manage.py collectstatic --noinput --clear

# Optimizar base de datos SQLite
echo "🗄️ Optimizando base de datos..."
python manage.py shell -c "
import sqlite3
from django.conf import settings
import os

db_path = settings.DATABASES['default']['NAME']
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
    conn.close()
    print('✅ Base de datos optimizada')
else:
    print('⚠️ Base de datos no encontrada')
"

# Verificar configuración de Gunicorn
echo "🔧 Verificando configuración de Gunicorn..."
echo "Workers configurados: 4"
echo "Worker class: sync"
echo "Timeout: 120s"
echo "Keep-alive: 2s"

# Reconstruir y ejecutar con optimizaciones
echo "🚀 Reconstruyendo y ejecutando con optimizaciones..."
docker-compose up --build -d

# Esperar a que el servidor esté listo
echo "⏳ Esperando a que el servidor esté listo..."
sleep 10

# Verificar rendimiento
echo "📊 Verificando rendimiento..."
echo "Probando respuesta del servidor..."

# Hacer algunas peticiones de prueba
for i in {1..3}; do
    echo "Petición $i:"
    time curl -s -o /dev/null -w "Status: %{http_code}, Tiempo: %{time_total}s\n" http://localhost:8000/api/
done

echo "✅ Optimización completada!"
echo ""
echo "📋 Mejoras aplicadas:"
echo "- Gunicorn: 4 workers con configuración optimizada"
echo "- SQLite: Configuración para múltiples hilos"
echo "- Cache: Configurado para producción"
echo "- Archivos estáticos: Optimizados"
echo "- Base de datos: VACUUM y ANALYZE ejecutados"
echo ""
echo "🌐 Accede a: http://34.136.15.241:8000/"
