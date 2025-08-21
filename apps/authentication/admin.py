from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, Company, Role


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'rubro', 'pais', 'activo', 'users_count', 'created_at']
    list_filter = ['rubro', 'pais', 'activo', 'created_at']
    search_fields = ['name', 'domain', 'email_contacto']
    readonly_fields = ['created_at', 'updated_at', 'users_count']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'domain', 'rubro', 'pais')
        }),
        ('Información de Contacto', {
            'fields': ('email_contacto', 'telefono', 'website', 'direccion')
        }),
        ('Logo', {
            'fields': ('logo',),
            'description': 'Sube el logo en formato Base64. Puedes usar herramientas online para convertir imágenes a Base64.'
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'activo')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def users_count(self, obj):
        """Muestra el número de usuarios asociados a la empresa"""
        count = obj.get_users_count()
        return format_html('<span style="color: {};">{}</span>', 
                          'green' if count > 0 else 'red', count)
    users_count.short_description = 'Usuarios'

    def get_queryset(self, request):
        """Optimizar consultas con select_related y prefetch_related"""
        return super().get_queryset(request).prefetch_related('users')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description')
        }),
        ('Permisos', {
            'fields': ('permissions',),
            'description': 'Configurar permisos específicos del rol (formato JSON)'
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'full_name', 'company_name', 'role_name', 'is_client', 'is_active', 'created_at']
    list_filter = ['is_client', 'is_active', 'company', 'role', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone', 'cargo', 'departamento')
        }),
        ('Empresa y Rol', {
            'fields': ('company', 'role', 'is_client')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'company', 'role', 'is_client'),
        }),
    )
    
    ordering = ['email']
    
    def company_name(self, obj):
        """Muestra el nombre de la empresa del usuario"""
        return obj.company_name or 'Sin empresa'
    company_name.short_description = 'Empresa'
    
    def role_name(self, obj):
        """Muestra el nombre del rol del usuario"""
        return obj.role_name or 'Sin rol'
    role_name.short_description = 'Rol'
    
    def full_name(self, obj):
        """Muestra el nombre completo del usuario"""
        return obj.full_name
    full_name.short_description = 'Nombre Completo'
