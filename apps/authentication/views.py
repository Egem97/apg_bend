from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import User, Company, Role
from .serializers import (
    UserSerializer, UserListSerializer, LoginSerializer, RegisterSerializer,
    CompanySerializer, CompanyListSerializer, RoleSerializer
)


class IsAdminUser(permissions.BasePermission):
    """Permiso personalizado para verificar si el usuario es administrador"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsAdminOrManager(permissions.BasePermission):
    """Permiso personalizado para verificar si el usuario es admin o manager"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin() or request.user.has_role('manager')
        )


class CompanyListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear empresas"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CompanyListSerializer
        return CompanySerializer

    def get_queryset(self):
        """Filtrar empresas según parámetros de búsqueda"""
        queryset = Company.objects.all()
        
        # Filtros
        name = self.request.query_params.get('name', None)
        rubro = self.request.query_params.get('rubro', None)
        pais = self.request.query_params.get('pais', None)
        activo = self.request.query_params.get('activo', None)
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if rubro:
            queryset = queryset.filter(rubro=rubro)
        if pais:
            queryset = queryset.filter(pais=pais)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset.select_related().prefetch_related('users')

    def perform_create(self, serializer):
        """Crear empresa con validaciones adicionales"""
        serializer.save()


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una empresa específica"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_permissions(self):
        """Permisos específicos según el método HTTP"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Company.objects.select_related().prefetch_related('users')

    def perform_update(self, serializer):
        """Actualizar empresa con validaciones"""
        serializer.save()

    def perform_destroy(self, instance):
        """Eliminar empresa con validaciones"""
        # Verificar si hay usuarios asociados
        if instance.users.exists():
            raise permissions.PermissionDenied(
                "No se puede eliminar una empresa que tiene usuarios asociados."
            )
        instance.delete()


class UserListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear usuarios"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        elif self.request.method == 'POST':
            return RegisterSerializer
        return UserSerializer

    def get_queryset(self):
        """Filtrar usuarios según parámetros de búsqueda"""
        queryset = User.objects.all()
        
        # Filtros
        email = self.request.query_params.get('email', None)
        company_id = self.request.query_params.get('company_id', None)
        is_client = self.request.query_params.get('is_client', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if email:
            queryset = queryset.filter(email__icontains=email)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if is_client is not None:
            queryset = queryset.filter(is_client=is_client.lower() == 'true')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.select_related('company')

    def perform_create(self, serializer):
        """Crear usuario con validaciones adicionales"""
        serializer.save()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un usuario específico"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.select_related('company')

    def perform_update(self, serializer):
        """Actualizar usuario con validaciones"""
        serializer.save()

    def perform_destroy(self, instance):
        """Eliminar usuario con validaciones"""
        # No permitir eliminar superusuarios
        if instance.is_superuser:
            raise permissions.PermissionDenied(
                "No se puede eliminar un superusuario."
            )
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Vista para el login de usuarios"""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Serializar datos del usuario
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Vista para obtener el perfil del usuario autenticado"""
    serializer = UserSerializer(request.user)
    return Response({'user': serializer.data}, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Vista para actualizar el perfil del usuario autenticado"""
    print(f"Recibiendo datos: {request.data}")
    print(f"Archivos: {request.FILES}")
    
    # Combinar datos y archivos
    data = request.data.copy()
    if request.FILES:
        data.update(request.FILES.dict())
    
    serializer = UserSerializer(request.user, data=data, partial=True)
    
    if serializer.is_valid():
        print(f"Datos válidos: {serializer.validated_data}")
        serializer.save()
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    else:
        print(f"Errores de validación: {serializer.errors}")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def company_users(request, company_id):
    """Vista para obtener todos los usuarios de una empresa específica"""
    try:
        company = Company.objects.get(id=company_id)
        users = company.users.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Company.DoesNotExist:
        return Response(
            {'error': 'Empresa no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class RoleListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear roles"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Filtrar roles según parámetros de búsqueda"""
        queryset = Role.objects.all()
        
        # Filtros
        name = self.request.query_params.get('name', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un rol específico"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def company_stats(request, company_id):
    """Vista para obtener estadísticas de una empresa"""
    try:
        company = Company.objects.get(id=company_id)
        
        # Estadísticas básicas
        stats = {
            'id': company.id,
            'name': company.name,
            'domain': company.domain,
            'total_users': company.get_users_count(),
            'active_users': company.users.filter(is_active=True).count(),
            'client_users': company.users.filter(is_client=True).count(),
            'staff_users': company.users.filter(is_staff=True).count(),
            'created_at': company.created_at,
            'updated_at': company.updated_at,
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    except Company.DoesNotExist:
        return Response(
            {'error': 'Empresa no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
