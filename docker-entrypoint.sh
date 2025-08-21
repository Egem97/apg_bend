#!/bin/bash

# Script de entrada para Docker
set -e

echo "Iniciando aplicación Django..."

# Esperar un momento para que todo esté listo
sleep 2

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe (opcional)
echo "Verificando superusuario..."
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
    print('Empresa creada:', company.name)
else:
    print('Empresa existente:', company.name)

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
        print('Superusuario creado: admin@example.com/admin123')
    except Exception as e:
        print('Error al crear superusuario:', str(e))
else:
    print('Superusuario ya existe')
"

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Aplicación lista para ejecutar!"

# Ejecutar el comando principal
exec "$@"
