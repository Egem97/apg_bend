#!/bin/bash

# Script para solucionar permisos de base de datos
set -e

echo "🔧 Solucionando permisos de base de datos..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py"
    exit 1
fi

# Detener contenedores si están ejecutándose
echo "🛑 Deteniendo contenedores..."
docker-compose down 2>/dev/null || true

# Verificar si existe la base de datos
if [ -f "db.sqlite3" ]; then
    echo "📄 Base de datos encontrada, corrigiendo permisos..."
    
    # Hacer backup
    cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup creado"
    
    # Corregir permisos
    chmod 666 db.sqlite3
    chown $USER:$USER db.sqlite3 2>/dev/null || true
    
    echo "✅ Permisos corregidos"
else
    echo "📄 Creando nueva base de datos..."
    touch db.sqlite3
    chmod 666 db.sqlite3
    echo "✅ Base de datos creada con permisos correctos"
fi

# Crear directorios si no existen
mkdir -p media staticfiles
chmod 755 media staticfiles

# Verificar permisos
echo "🔍 Verificando permisos..."
ls -la db.sqlite3
ls -la media/
ls -la staticfiles/

echo "✅ Permisos verificados correctamente"

# Reiniciar contenedores
echo "🚀 Reiniciando contenedores..."
docker-compose up -d

echo "✅ ¡Listo! Prueba acceder a:"
echo "   http://34.136.15.241:8000/admin/"
echo "   Usuario: admin@example.com"
echo "   Contraseña: admin123"
