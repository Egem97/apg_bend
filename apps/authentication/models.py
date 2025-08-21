import base64
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import os


class Company(models.Model):
    """
    Company model for managing client companies in the agricultural production system
    """
    RUBRO_CHOICES = [
        ('agricultura', 'Agricultura'),
        ('fruticultura', 'Fruticultura'),
        ('horticultura', 'Horticultura'),
        ('viticultura', 'Viticultura'),
        ('ganaderia', 'Ganadería'),
        ('avicultura', 'Avicultura'),
        ('porcicultura', 'Porcicultura'),
        ('acuicultura', 'Acuicultura'),
        ('apicultura', 'Apicultura'),
        ('otros', 'Otros'),
    ]

    PAIS_CHOICES = [
        ('AR', 'Argentina'),
        ('BR', 'Brasil'),
        ('CL', 'Chile'),
        ('CO', 'Colombia'),
        ('EC', 'Ecuador'),
        ('PE', 'Perú'),
        ('UY', 'Uruguay'),
        ('VE', 'Venezuela'),
        ('MX', 'México'),
        ('US', 'Estados Unidos'),
        ('CA', 'Canadá'),
        ('ES', 'España'),
        ('FR', 'Francia'),
        ('DE', 'Alemania'),
        ('IT', 'Italia'),
        ('NL', 'Países Bajos'),
        ('GB', 'Reino Unido'),
        ('AU', 'Australia'),
        ('NZ', 'Nueva Zelanda'),
        ('CN', 'China'),
        ('JP', 'Japón'),
        ('KR', 'Corea del Sur'),
        ('IN', 'India'),
        ('ZA', 'Sudáfrica'),
        ('OT', 'Otros'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    domain = models.CharField(max_length=100, unique=True, verbose_name="Dominio")
    logo = models.TextField(blank=True, null=True, verbose_name="Logo (Base64)")
    rubro = models.CharField(max_length=50, choices=RUBRO_CHOICES, verbose_name="Rubro")
    pais = models.CharField(max_length=2, choices=PAIS_CHOICES, verbose_name="País")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email_contacto = models.EmailField(blank=True, verbose_name="Email de Contacto")
    website = models.URLField(blank=True, verbose_name="Sitio Web")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        db_table = 'auth_company'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.domain})"

    def clean(self):
        """Validación personalizada del modelo"""
        if self.domain:
            # Validar que el dominio no contenga espacios ni caracteres especiales
            if ' ' in self.domain or not self.domain.replace('.', '').replace('-', '').isalnum():
                raise ValidationError({
                    'domain': 'El dominio debe contener solo letras, números, puntos y guiones.'
                })

    def save(self, *args, **kwargs):
        """Override save para validaciones adicionales"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def logo_url(self):
        """Retorna la URL del logo para el frontend"""
        if self.logo:
            return f"data:image/png;base64,{self.logo}"
        return None

    @property
    def pais_display(self):
        """Retorna el nombre del país"""
        return dict(self.PAIS_CHOICES).get(self.pais, self.pais)

    @property
    def rubro_display(self):
        """Retorna el nombre del rubro"""
        return dict(self.RUBRO_CHOICES).get(self.rubro, self.rubro)

    def get_users_count(self):
        """Retorna el número de usuarios asociados a esta empresa"""
        return self.users.count()


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crear usuario normal"""
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        
        # Generar username automáticamente si no se proporciona
        if 'username' not in extra_fields or not extra_fields['username']:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            # Verificar que el username sea único
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crear superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    """
    Role model for user permissions in the system
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('operator', 'Operador'),
        ('viewer', 'Visualizador'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name="Nombre del Rol")
    description = models.TextField(blank=True, verbose_name="Descripción")
    permissions = models.JSONField(default=dict, verbose_name="Permisos")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        db_table = 'auth_role'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()

    @property
    def display_name(self):
        """Retorna el nombre legible del rol"""
        return self.get_name_display()


class User(AbstractUser):
    """
    Custom User model for the agricultural production system
    """
    # Hacer el username opcional y único
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, 
        blank=True,
        verbose_name="Empresa"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rol"
    )
    phone = models.CharField(max_length=20, blank=True)
    is_client = models.BooleanField(default=True)
    cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    departamento = models.CharField(max_length=100, blank=True, verbose_name="Departamento")
    profile_image = models.TextField(blank=True, null=True, help_text="Imagen de perfil en Base64")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def company_name(self):
        """Retorna el nombre de la empresa del usuario"""
        return self.company.name if self.company else None

    @property
    def profile_image_url(self):
        """Retorna la URL de la imagen de perfil para el frontend"""
        if self.profile_image:
            return f"data:image/png;base64,{self.profile_image}"
        return None

    @property
    def role_name(self):
        """Retorna el nombre del rol del usuario"""
        return self.role.display_name if self.role else None

    def has_role(self, role_name):
        """Verifica si el usuario tiene un rol específico"""
        return self.role and self.role.name == role_name

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.has_role('admin') or self.is_superuser

    def can_edit_company(self):
        """Verifica si el usuario puede editar empresas"""
        return self.is_admin()

    def can_manage_users(self):
        """Verifica si el usuario puede gestionar usuarios"""
        return self.is_admin() or self.has_role('manager')

    def save(self, *args, **kwargs):
        """Override save para generar username automáticamente si no existe"""
        if not self.username:
            # Generar username basado en el email
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            # Verificar que el username sea único
            while User.objects.filter(username=username).exclude(id=self.id).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
        
        super().save(*args, **kwargs)
