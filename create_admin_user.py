#!/usr/bin/env python3
"""
Script para crear el usuario admin si no existe
Este script verifica si existe el usuario admin y lo crea si es necesario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import Company

User = get_user_model()

def create_admin_user():
    """Crear usuario admin si no existe"""
    email = "admin@example.com"
    password = "admin123"
    
    # Verificar si el usuario ya existe
    if User.objects.filter(email=email).exists():
        print(f"✅ Usuario admin ya existe: {email}")
        return True
    
    # Crear empresa por defecto si no existe
    company, created = Company.objects.get_or_create(
        name="Empresa Administradora",
        defaults={
            'domain': 'admin',
            'rubro': 'tecnologia',
            'pais': 'PE',
            'activo': True
        }
    )
    
    if created:
        print(f"✅ Empresa creada: {company.name}")
    else:
        print(f"✅ Empresa existente: {company.name}")
    
    # Crear usuario admin
    try:
        admin_user = User.objects.create_user(
            email=email,
            username=email,  # Usar email como username
            first_name="Administrador",
            last_name="Sistema",
            password=password,
            company=company,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print(f"✅ Usuario admin creado exitosamente:")
        print(f"   Email: {admin_user.email}")
        print(f"   Contraseña: {password}")
        print(f"   Empresa: {admin_user.company.name}")
        print(f"   Es superusuario: {admin_user.is_superuser}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear usuario admin: {e}")
        return False

def verify_admin_user():
    """Verificar que el usuario admin existe y tiene los permisos correctos"""
    email = "admin@example.com"
    
    try:
        user = User.objects.get(email=email)
        print(f"✅ Usuario admin verificado:")
        print(f"   Email: {user.email}")
        print(f"   Nombre: {user.get_full_name()}")
        print(f"   Empresa: {user.company.name if user.company else 'Sin empresa'}")
        print(f"   Es superusuario: {user.is_superuser}")
        print(f"   Es staff: {user.is_staff}")
        print(f"   Está activo: {user.is_active}")
        
        # Verificar que puede autenticarse
        from django.contrib.auth import authenticate
        auth_user = authenticate(username=email, password="admin123")
        if auth_user:
            print(f"   ✅ Autenticación exitosa")
        else:
            print(f"   ❌ Error en autenticación")
            
        return True
        
    except User.DoesNotExist:
        print(f"❌ Usuario admin no existe: {email}")
        return False
    except Exception as e:
        print(f"❌ Error al verificar usuario: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 Verificando y creando usuario admin...")
    print("=" * 50)
    
    # Verificar si existe
    if not verify_admin_user():
        print("\n🛠️ Creando usuario admin...")
        if create_admin_user():
            print("\n✅ Verificación final:")
            verify_admin_user()
        else:
            print("❌ No se pudo crear el usuario admin")
            return False
    
    print("\n" + "=" * 50)
    print("✅ Usuario admin listo para usar")
    print("📧 Email: admin@example.com")
    print("🔑 Contraseña: admin123")
    print("\n🌐 Puedes usar estas credenciales en los scripts de prueba")
    
    return True

if __name__ == "__main__":
    main()
