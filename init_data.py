#!/usr/bin/env python
"""
Script para inicializar el proyecto con datos de ejemplo
Ejecutar después de las migraciones: python init_data.py
"""
import os
import sys
import django
import base64
from datetime import date, datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_backend.settings')
django.setup()

from apps.authentication.models import User, Company, Role
from apps.production.models import Product, Shipment, Inspection, QualityReport, Sample

def create_test_roles():
    """Crear roles de prueba"""
    
    roles_data = [
        {
            'name': 'admin',
            'description': 'Administrador del sistema con acceso completo',
            'permissions': {
                'can_edit_company': True,
                'can_manage_users': True,
                'can_view_reports': True,
                'can_edit_production': True
            },
            'is_active': True
        },
        {
            'name': 'manager',
            'description': 'Gerente con permisos de gestión',
            'permissions': {
                'can_edit_company': False,
                'can_manage_users': True,
                'can_view_reports': True,
                'can_edit_production': True
            },
            'is_active': True
        },
        {
            'name': 'supervisor',
            'description': 'Supervisor de producción',
            'permissions': {
                'can_edit_company': False,
                'can_manage_users': False,
                'can_view_reports': True,
                'can_edit_production': True
            },
            'is_active': True
        },
        {
            'name': 'operator',
            'description': 'Operador del sistema',
            'permissions': {
                'can_edit_company': False,
                'can_manage_users': False,
                'can_view_reports': False,
                'can_edit_production': True
            },
            'is_active': True
        },
        {
            'name': 'viewer',
            'description': 'Visualizador con acceso de solo lectura',
            'permissions': {
                'can_edit_company': False,
                'can_manage_users': False,
                'can_view_reports': True,
                'can_edit_production': False
            },
            'is_active': True
        }
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        if created:
            print(f"✅ Rol creado: {role.display_name}")
        else:
            print(f"⚠️  Rol ya existe: {role.display_name}")


def create_test_companies():
    """Crear empresas de prueba con logos en Base64"""
    
    # Logo simple en Base64 (un cuadrado azul simple)
    simple_logo = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    companies_data = [
        {
            'name': 'SAN LUCAR S.A.',
            'domain': 'sanlucar.com',
            'logo': simple_logo,
            'rubro': 'fruticultura',
            'pais': 'CL',
            'direccion': 'Av. Providencia 1234, Santiago, Chile',
            'telefono': '+56 2 2345 6789',
            'email_contacto': 'contacto@sanlucar.com',
            'website': 'https://www.sanlucar.com',
            'descripcion': 'Empresa líder en producción de arándanos en Chile',
            'activo': True
        },
        {
            'name': 'FRUTAS DEL VALLE',
            'domain': 'frutasdelvalle.com',
            'logo': simple_logo,
            'rubro': 'fruticultura',
            'pais': 'PE',
            'direccion': 'Calle Los Pinos 567, Lima, Perú',
            'telefono': '+51 1 4567 8901',
            'email_contacto': 'info@frutasdelvalle.com',
            'website': 'https://www.frutasdelvalle.com',
            'descripcion': 'Especialistas en frutas tropicales y berries',
            'activo': True
        },
        {
            'name': 'AGROEXPORT S.A.',
            'domain': 'agroexport.com',
            'logo': simple_logo,
            'rubro': 'agricultura',
            'pais': 'CO',
            'direccion': 'Carrera 15 # 45-67, Bogotá, Colombia',
            'telefono': '+57 1 3456 7890',
            'email_contacto': 'ventas@agroexport.com',
            'website': 'https://www.agroexport.com',
            'descripcion': 'Exportadores de productos agrícolas colombianos',
            'activo': True
        }
    ]
    
    for company_data in companies_data:
        company, created = Company.objects.get_or_create(
            domain=company_data['domain'],
            defaults=company_data
        )
        if created:
            print(f"✅ Empresa creada: {company.name}")
        else:
            print(f"⚠️  Empresa ya existe: {company.name}")

def create_test_users():
    """Crear usuarios de prueba asociados a empresas"""
    
    # Obtener empresas existentes
    companies = Company.objects.all()
    
    if not companies.exists():
        print("❌ No hay empresas disponibles. Creando empresas primero...")
        create_test_companies()
        companies = Company.objects.all()
    
    # Obtener roles existentes
    roles = Role.objects.all()
    
    if not roles.exists():
        print("❌ No hay roles disponibles. Creando roles primero...")
        create_test_roles()
        roles = Role.objects.all()
    
    users_data = [
        {
            'email': 'admin@sanlucar.com',
            'username': 'admin_sanlucar',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'company': companies.filter(domain='sanlucar.com').first(),
            'role': roles.filter(name='admin').first(),
            'phone': '+56 9 1234 5678',
            'cargo': 'Gerente de Producción',
            'departamento': 'Producción',
            'is_client': True,
            'is_staff': True,
            'is_superuser': True
        },
        {
            'email': 'maria@frutasdelvalle.com',
            'username': 'maria_frutas',
            'first_name': 'María',
            'last_name': 'González',
            'company': companies.filter(domain='frutasdelvalle.com').first(),
            'role': roles.filter(name='manager').first(),
            'phone': '+51 9 9876 5432',
            'cargo': 'Supervisor de Calidad',
            'departamento': 'Calidad',
            'is_client': True,
            'is_staff': False
        },
        {
            'email': 'carlos@agroexport.com',
            'username': 'carlos_agro',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'company': companies.filter(domain='agroexport.com').first(),
            'role': roles.filter(name='supervisor').first(),
            'phone': '+57 3 1234 5678',
            'cargo': 'Director Comercial',
            'departamento': 'Comercial',
            'is_client': True,
            'is_staff': False
        }
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✅ Usuario creado: {user.full_name} ({user.email})")
        else:
            print(f"⚠️  Usuario ya existe: {user.full_name}")

def create_sample_data():
    print("Creando datos de ejemplo...")
    
    # Crear usuario administrador si no existe
    if not User.objects.filter(email='admin@agrosass.com').exists():
        admin_user = User.objects.create_user(
            email='admin@agrosass.com',
            username='admin',
            first_name='Administrador',
            last_name='Sistema',
            company='AgroSaaS',
            phone='+1234567890',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Usuario administrador creado: {admin_user.email}")
    
    # Crear usuario cliente demo
    if not User.objects.filter(email='cliente@demo.com').exists():
        demo_user = User.objects.create_user(
            email='cliente@demo.com',
            username='cliente_demo',
            first_name='Cliente',
            last_name='Demo',
            company='Empresa Demo S.A.',
            phone='+9876543210',
            password='demo123',
            is_client=True
        )
        print(f"✅ Usuario cliente demo creado: {demo_user.email}")
    else:
        demo_user = User.objects.get(email='cliente@demo.com')
    
    # Crear productos de ejemplo
    products_data = [
        {
            'name': 'Arándanos Frescos',
            'description': 'Arándanos frescos de alta calidad',
            'variety': 'Blue White Blueberries'
        },
        {
            'name': 'Aguacate Hass',
            'description': 'Aguacate Hass para exportación',
            'variety': 'Hass'
        },
        {
            'name': 'Mango Tommy',
            'description': 'Mango Tommy Atkins premium',
            'variety': 'Tommy Atkins'
        }
    ]
    
    created_products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            print(f"✅ Producto creado: {product.name}")
        created_products.append(product)
    
    # Crear embarques de ejemplo
    shipments_data = [
        {
            'reference': '069267/PPX25',
            'product': created_products[0],  # Arándanos
            'shipper': 'FRESAFLOR SDAD. COOP. AND.',
            'consignee': 'Blue White Blueberries Agricul...',
            'transport_type': 'road',
            'location': 'PRESARTCL12x125g',
            'date': date.today() - timedelta(days=2),
            'created_by': demo_user
        },
        {
            'reference': 'AVG001/2025',
            'product': created_products[1],  # Aguacate
            'shipper': 'Productores Unidos S.A.',
            'consignee': 'International Fruits Ltd.',
            'transport_type': 'sea',
            'location': 'Puerto de Veracruz',
            'date': date.today() - timedelta(days=5),
            'created_by': demo_user
        },
        {
            'reference': 'MNG002/2025',
            'product': created_products[2],  # Mango
            'shipper': 'Mango Export Co.',
            'consignee': 'European Fruits Import',
            'transport_type': 'air',
            'location': 'Aeropuerto Internacional',
            'date': date.today() - timedelta(days=1),
            'created_by': demo_user
        }
    ]
    
    created_shipments = []
    for shipment_data in shipments_data:
        shipment, created = Shipment.objects.get_or_create(
            reference=shipment_data['reference'],
            defaults=shipment_data
        )
        if created:
            print(f"✅ Embarque creado: {shipment.reference}")
        created_shipments.append(shipment)
    
    # Crear inspecciones de ejemplo
    inspections_data = [
        {
            'shipment': created_shipments[0],
            'inspection_type': 'grower',
            'status': 'completed',
            'inspection_point': 'Supplier',
            'inspector': 'SanLucar Fruit (Production)',
            'inspection_date': datetime.now() - timedelta(hours=46),
            'notes': 'Inspección del productor completada satisfactoriamente'
        },
        {
            'shipment': created_shipments[0],
            'inspection_type': 'quality',
            'status': 'in_progress',
            'inspection_point': 'Puerto de embarque',
            'inspector': 'Control de Calidad Central',
            'inspection_date': datetime.now() - timedelta(hours=2),
            'notes': 'Inspección de calidad en progreso'
        },
        {
            'shipment': created_shipments[1],
            'inspection_type': 'phytosanitary',
            'status': 'pending',
            'inspection_point': 'Aduana',
            'inspector': 'SENASICA',
            'inspection_date': datetime.now() + timedelta(hours=12),
            'notes': 'Inspección fitosanitaria programada'
        }
    ]
    
    created_inspections = []
    for inspection_data in inspections_data:
        inspection, created = Inspection.objects.get_or_create(
            shipment=inspection_data['shipment'],
            inspection_type=inspection_data['inspection_type'],
            defaults=inspection_data
        )
        if created:
            print(f"✅ Inspección creada: {inspection.inspection_type} - {inspection.shipment.reference}")
        created_inspections.append(inspection)
    
    # Crear reporte de calidad para la primera inspección
    if created_inspections and created_inspections[0].status == 'completed':
        quality_report, created = QualityReport.objects.get_or_create(
            inspection=created_inspections[0],
            defaults={
                'temperature': 2.5,
                'humidity': 85.0,
                'ph_level': 3.2,
                'defects_found': 'Ningún defecto significativo encontrado',
                'overall_quality': 'excellent',
                'approved': True
            }
        )
        if created:
            print(f"✅ Reporte de calidad creado para inspección: {quality_report.inspection}")
    
    # Crear muestras de ejemplo
    if created_inspections:
        samples_data = [
            {
                'inspection': created_inspections[0],
                'sample_id': 'SM001-2025',
                'quantity': 2.5,
                'unit': 'kg',
                'location_taken': 'Contenedor A1-B3',
                'notes': 'Muestra representativa del lote'
            },
            {
                'inspection': created_inspections[0],
                'sample_id': 'SM002-2025',
                'quantity': 1.0,
                'unit': 'kg',
                'location_taken': 'Contenedor A2-C1',
                'notes': 'Muestra de control de calidad'
            }
        ]
        
        for sample_data in samples_data:
            sample, created = Sample.objects.get_or_create(
                sample_id=sample_data['sample_id'],
                defaults=sample_data
            )
            if created:
                print(f"✅ Muestra creada: {sample.sample_id}")
    
    print("\n🎉 Datos de ejemplo creados exitosamente!")
    print("\n📋 Credenciales de acceso:")
    print("Administrador:")
    print("  Email: admin@agrosass.com")
    print("  Password: admin123")
    print("\nCliente Demo:")
    print("  Email: cliente@demo.com")
    print("  Password: demo123")

def main():
    """Función principal para inicializar datos"""
    print("🚀 Iniciando creación de datos de prueba...")
    
    # Crear roles
    print("\n👥 Creando roles...")
    create_test_roles()
    
    # Crear empresas
    print("\n📊 Creando empresas...")
    create_test_companies()
    
    # Crear usuarios
    print("\n👥 Creando usuarios...")
    create_test_users()
    
    print("\n✅ Datos de prueba creados exitosamente!")
    print("\n📋 Resumen:")
    print(f"   - Empresas: {Company.objects.count()}")
    print(f"   - Usuarios: {User.objects.count()}")
    
    # Mostrar información de las empresas
    print("\n🏢 Empresas creadas:")
    for company in Company.objects.all():
        print(f"   - {company.name} ({company.domain}) - {company.get_users_count()} usuarios")

if __name__ == '__main__':
    main()
