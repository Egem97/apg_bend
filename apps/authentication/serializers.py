from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Company, Role


class CompanySerializer(serializers.ModelSerializer):
    """Serializer para el modelo Company"""
    pais_display = serializers.CharField(read_only=True)
    rubro_display = serializers.CharField(read_only=True)
    users_count = serializers.IntegerField(read_only=True)
    logo_url = serializers.CharField(read_only=True)
    logo_file = serializers.FileField(write_only=True, required=False, help_text="Archivo de imagen para el logo")

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'domain', 'logo', 'logo_url', 'logo_file', 'rubro', 'rubro_display',
            'pais', 'pais_display', 'direccion', 'telefono', 'email_contacto',
            'website', 'descripcion', 'activo', 'created_at', 'updated_at', 'users_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'users_count']

    def validate_logo_file(self, value):
        """Validar archivo de imagen"""
        if value:
            # Verificar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Solo se permiten archivos de imagen (JPEG, PNG, GIF).")
            
            # Verificar tamaño (máximo 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no puede ser mayor a 5MB.")
        
        return value

    def create(self, validated_data):
        """Crear empresa con conversión de imagen a Base64"""
        logo_file = validated_data.pop('logo_file', None)
        
        if logo_file:
            # Convertir imagen a Base64
            import base64
            logo_file.seek(0)
            logo_data = logo_file.read()
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')
            validated_data['logo'] = logo_base64
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Actualizar empresa con conversión de imagen a Base64"""
        logo_file = validated_data.pop('logo_file', None)
        
        if logo_file:
            # Convertir imagen a Base64
            import base64
            logo_file.seek(0)
            logo_data = logo_file.read()
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')
            validated_data['logo'] = logo_base64
        
        return super().update(instance, validated_data)

    def validate_domain(self, value):
        """Validación personalizada para el dominio"""
        if value:
            # Verificar que el dominio no contenga espacios
            if ' ' in value:
                raise serializers.ValidationError("El dominio no puede contener espacios.")
            
            # Verificar que solo contenga caracteres válidos
            valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-')
            if not all(c in valid_chars for c in value):
                raise serializers.ValidationError("El dominio solo puede contener letras, números, puntos y guiones.")
        
        return value

    def validate_logo(self, value):
        """Validación para el logo en Base64"""
        if value:
            try:
                # Verificar que sea un string válido de Base64
                import base64
                base64.b64decode(value)
            except Exception:
                raise serializers.ValidationError("El logo debe estar en formato Base64 válido.")
        
        return value


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar empresas"""
    pais_display = serializers.CharField(read_only=True)
    rubro_display = serializers.CharField(read_only=True)
    users_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'domain', 'rubro', 'rubro_display',
            'pais', 'pais_display', 'activo', 'users_count'
        ]


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Role"""
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'display_name', 'description', 'permissions', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    company = CompanySerializer(read_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    company_name = serializers.CharField(read_only=True)
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    role_name = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    profile_image_url = serializers.CharField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    can_edit_company = serializers.BooleanField(read_only=True)
    can_manage_users = serializers.BooleanField(read_only=True)
    profile_image_file = serializers.FileField(write_only=True, required=False, help_text="Archivo de imagen para el perfil")

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'company', 'company_id', 'company_name', 'role', 'role_id', 'role_name',
            'phone', 'cargo', 'departamento', 'is_client', 'is_active', 'is_staff', 'is_superuser',
            'is_admin', 'can_edit_company', 'can_manage_users',
            'profile_image_url', 'profile_image_file',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_company_id(self, value):
        """Validar que la empresa existe"""
        if value is not None:
            try:
                Company.objects.get(id=value)
            except Company.DoesNotExist:
                raise serializers.ValidationError("La empresa especificada no existe.")
        return value

    def validate_role_id(self, value):
        """Validar que el rol existe"""
        if value is not None:
            try:
                Role.objects.get(id=value)
            except Role.DoesNotExist:
                raise serializers.ValidationError("El rol especificado no existe.")
        return value

    def validate_profile_image_file(self, value):
        """Validar archivo de imagen de perfil"""
        if value:
            # Verificar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Solo se permiten archivos de imagen (JPEG, PNG, GIF).")
            
            # Verificar tamaño (máximo 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no puede ser mayor a 5MB.")
        
        return value

    def update(self, instance, validated_data):
        """Actualizar usuario con validación de empresa y rol"""
        company_id = validated_data.pop('company_id', None)
        role_id = validated_data.pop('role_id', None)
        profile_image_file = validated_data.pop('profile_image_file', None)

        if company_id is not None:
            try:
                company = Company.objects.get(id=company_id)
                instance.company = company
            except Company.DoesNotExist:
                pass

        if role_id is not None:
            try:
                role = Role.objects.get(id=role_id)
                instance.role = role
            except Role.DoesNotExist:
                pass

        if profile_image_file:
            # Convertir imagen a Base64
            import base64
            profile_image_file.seek(0)
            image_data = profile_image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            validated_data['profile_image'] = image_base64

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Personalizar la representación del usuario"""
        data = super().to_representation(instance)
        
        # Agregar los campos booleanos de permisos
        data['is_admin'] = instance.is_admin()
        data['can_edit_company'] = instance.can_edit_company()
        data['can_manage_users'] = instance.can_manage_users()
        
        # Agregar la URL de la imagen de perfil
        data['profile_image_url'] = instance.profile_image_url
        
        return data


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar usuarios"""
    company_name = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'company_name', 'cargo', 'departamento',
            'is_client', 'is_active', 'created_at'
        ]


class LoginSerializer(serializers.Serializer):
    """Serializer para el login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Credenciales inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Debe proporcionar email y contraseña.')

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para el registro de usuarios"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    company_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'password', 'password_confirm',
            'company_id', 'phone', 'cargo', 'departamento', 'is_client'
        ]

    def validate(self, attrs):
        """Validaciones personalizadas"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        # Validar empresa si se proporciona
        company_id = attrs.get('company_id')
        if company_id:
            try:
                Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                raise serializers.ValidationError({"company_id": "La empresa especificada no existe."})
        
        return attrs

    def create(self, validated_data):
        """Crear usuario con empresa asociada"""
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)
        company_id = validated_data.pop('company_id', None)
        
        # Asignar empresa si se proporciona
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                validated_data['company'] = company
            except Company.DoesNotExist:
                pass
        
        # Crear usuario sin username (se generará automáticamente)
        validated_data.pop('username', None)  # Remover username si existe
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
