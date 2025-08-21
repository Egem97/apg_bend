#!/bin/bash

# Script para preparar el VPS para el despliegue
set -e

echo "🚀 Preparando VPS para despliegue..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Asegúrate de estar en el directorio del proyecto."
    exit 1
fi

# Crear directorios si no existen
echo "📁 Creando directorios..."
mkdir -p media staticfiles

# Verificar si existe la base de datos
if [ ! -f "db.sqlite3" ]; then
    echo "📄 Creando archivo de base de datos..."
    touch db.sqlite3
fi

# Establecer permisos correctos
echo "🔐 Estableciendo permisos..."
chmod 666 db.sqlite3
chmod 755 media staticfiles

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual e instalar dependencias
echo "📦 Instalando dependencias..."
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.authentication.models import Company

User = get_user_model()

# Crear empresa por defecto si no existe
company, created = Company.objects.get_or_create(
    name='Empresa Administradora',
    defaults={
        'domain': 'admin',
        'rubro': 'tecnologia',
        'pais': 'PE',
        'activo': True
    }
)

if created:
    print('✅ Empresa creada:', company.name)
else:
    print('✅ Empresa existente:', company.name)

# Verificar si existe usuario admin
if not User.objects.filter(email='admin@example.com').exists():
    try:
        admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin@example.com',
            first_name='Administrador',
            last_name='Sistema',
            password='admin123',
            company=company,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        print('✅ Superusuario creado: admin@example.com/admin123')
    except Exception as e:
        print('❌ Error al crear superusuario:', str(e))
else:
    print('✅ Superusuario ya existe')
"

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Verificar permisos finales
echo "🔍 Verificando permisos finales..."
ls -la db.sqlite3
ls -la media/
ls -la staticfiles/

echo "✅ VPS preparado correctamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ejecutar: sudo docker-compose up --build -d"
echo "2. Verificar: curl http://localhost:8000/api/"
echo "3. Acceder al admin: http://localhost:8000/admin/"
echo "   Usuario: admin@example.com"
echo "   Contraseña: admin123"
