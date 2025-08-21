from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import asyncio
from asgiref.sync import sync_to_async
from django.db import transaction

from .models import QualityData
from .serializers import (
    QualityDataSerializer, QualityDataListSerializer, 
    QualityDataFilterSerializer, QualityDataStatsSerializer
)
from .services import ExternalQualityAPIService, QualityDataService


class QualityDataListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear datos de calidad
    """
    permission_classes = [IsAuthenticated]  # Cambiado de AllowAny a IsAuthenticated
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QualityDataListSerializer
        return QualityDataSerializer
    
    def get_queryset(self):
        """
        Retorna datos de calidad filtrados por empresa del usuario logueado
        """
        queryset = QualityData.objects.all()
        
        # Filtrar por empresa del usuario logueado
        if self.request.user.is_authenticated and self.request.user.company:
            user_company = self.request.user.company.name
            queryset = queryset.filter(empresa=user_company)
            print(f"🔍 Filtrando por empresa del usuario: {user_company}")
        else:
            # Si el usuario no tiene empresa asignada, no mostrar datos
            queryset = QualityData.objects.none()
            print("⚠️ Usuario sin empresa asignada - no se muestran datos")
        
        # Aplicar filtros adicionales
        empresa = self.request.query_params.get('empresa')
        if empresa:
            queryset = queryset.filter(empresa__icontains=empresa)
        
        # Filtro por contenedor
        contenedor = self.request.query_params.get('contenedor')
        if contenedor:
            queryset = queryset.filter(
                processed_data__additional_info__n_fcl__icontains=contenedor
            )
        
        calidad_general = self.request.query_params.get('calidad_general')
        if calidad_general:
            queryset = queryset.filter(calidad_general=calidad_general)
        
        aprobado = self.request.query_params.get('aprobado')
        if aprobado is not None:
            queryset = queryset.filter(aprobado=aprobado.lower() == 'true')
        
        fecha_desde = self.request.query_params.get('fecha_desde')
        if fecha_desde:
            try:
                fecha_desde = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha_registro__gte=fecha_desde)
            except:
                pass
        
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        if fecha_hasta:
            try:
                fecha_hasta = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha_registro__lte=fecha_hasta)
            except:
                pass
        
        return queryset.order_by('-fecha_registro')
    
    def perform_create(self, serializer):
        """
        Asigna el usuario creador al guardar (si está autenticado)
        """
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()


class QualityDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para ver, actualizar y eliminar datos de calidad específicos
    """
    permission_classes = [IsAuthenticated]  # Cambiado de AllowAny a IsAuthenticated
    serializer_class = QualityDataSerializer
    
    def get_queryset(self):
        """
        Retorna datos de calidad filtrados por empresa del usuario logueado
        """
        queryset = QualityData.objects.all()
        
        # Filtrar por empresa del usuario logueado
        if self.request.user.is_authenticated and self.request.user.company:
            user_company = self.request.user.company.name
            queryset = queryset.filter(empresa=user_company)
        else:
            # Si el usuario no tiene empresa asignada, no mostrar datos
            queryset = QualityData.objects.none()
        
        return queryset


class QualityDataFilterView(generics.ListAPIView):
    """
    Vista para filtrar datos de calidad con parámetros avanzados
    """
    permission_classes = [IsAuthenticated]  # Cambiado de AllowAny a IsAuthenticated
    serializer_class = QualityDataListSerializer
    
    def get_queryset(self):
        """
        Retorna datos de calidad filtrados por empresa del usuario logueado
        """
        queryset = QualityData.objects.all()
        
        # Filtrar por empresa del usuario logueado
        if self.request.user.is_authenticated and self.request.user.company:
            user_company = self.request.user.company.name
            queryset = queryset.filter(empresa=user_company)
        else:
            # Si el usuario no tiene empresa asignada, no mostrar datos
            queryset = QualityData.objects.none()
        
        # Aplicar filtros del serializer
        filter_serializer = QualityDataFilterSerializer(data=self.request.query_params)
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data
            
            if filters.get('empresa'):
                queryset = queryset.filter(empresa__icontains=filters['empresa'])
            
            if filters.get('fecha_desde'):
                queryset = queryset.filter(fecha_registro__gte=filters['fecha_desde'])
            
            if filters.get('fecha_hasta'):
                queryset = queryset.filter(fecha_registro__lte=filters['fecha_hasta'])
            
            if filters.get('calidad_general'):
                queryset = queryset.filter(calidad_general=filters['calidad_general'])
            
            if filters.get('aprobado') is not None:
                queryset = queryset.filter(aprobado=filters['aprobado'])
        
        return queryset.order_by('-fecha_registro')


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Cambiado de AllowAny a IsAuthenticated
def quality_data_stats(request):
    """
    Obtiene estadísticas de datos de calidad filtradas por empresa del usuario
    """
    # Usar la empresa del usuario logueado
    user_company = None
    if request.user.is_authenticated and request.user.company:
        user_company = request.user.company.name
    
    # Usar el servicio de forma síncrona
    stats = QualityDataService.get_quality_stats(user=request.user, empresa=user_company)
    
    serializer = QualityDataStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Cambiado de AllowAny a IsAuthenticated
def sync_external_quality_data(request):
    """
    Sincroniza datos de calidad desde la API externa para la empresa del usuario
    """
    # Usar la empresa del usuario logueado
    if not request.user.is_authenticated or not request.user.company:
        return Response(
            {'error': 'Usuario debe estar autenticado y tener empresa asignada'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_company = request.user.company.name
    
    try:
        # Crear servicio de API externa
        external_service = ExternalQualityAPIService()
        
        # Sincronizar datos de forma síncrona para la empresa del usuario
        result = external_service.sync_quality_data_for_company(user_company, request.user)
        
        if result['success']:
            return Response({
                'message': result['message'],
                'records_processed': result['records_processed'],
                'records_created': result['records_created'],
                'records_updated': result['records_updated']
            })
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': f'Error durante la sincronización: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Cambiado de AllowAny a IsAuthenticated
def quality_data_dashboard(request):
    """
    Obtiene datos para el dashboard de calidad filtrados por empresa del usuario
    """
    # Usar la empresa del usuario logueado
    user_company = None
    if request.user.is_authenticated and request.user.company:
        user_company = request.user.company.name
    
    # Obtener estadísticas generales de forma síncrona
    stats = QualityDataService.get_quality_stats(user=request.user, empresa=user_company)
    
    # Obtener datos recientes de forma síncrona filtrados por empresa
    recent_data = QualityData.objects.all()
    if user_company:
        recent_data = recent_data.filter(empresa=user_company)
    recent_data = recent_data.order_by('-fecha_registro')[:10]
    recent_data_serializer = QualityDataListSerializer(recent_data, many=True)
    
    # Obtener datos por período (últimos 30 días) de forma síncrona
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_data = QualityData.objects.filter(
        fecha_registro__gte=thirty_days_ago
    )
    if user_company:
        monthly_data = monthly_data.filter(empresa=user_company)
    monthly_data = monthly_data.order_by('-fecha_registro')
    
    monthly_stats = QualityDataService.get_quality_stats(user=request.user, empresa=user_company)
    
    return Response({
        'stats': stats,
        'recent_data': recent_data_serializer.data,
        'monthly_stats': monthly_stats,
        'monthly_data_count': monthly_data.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Cambiado de AllowAny a IsAuthenticated
def quality_data_export(request):
    """
    Exporta datos de calidad en formato CSV filtrados por empresa del usuario
    """
    # Usar la empresa del usuario logueado
    user_company = None
    if request.user.is_authenticated and request.user.company:
        user_company = request.user.company.name
    
    # Obtener queryset filtrado por empresa del usuario
    queryset = QualityData.objects.all()
    if user_company:
        queryset = queryset.filter(empresa=user_company)
    else:
        # Si el usuario no tiene empresa asignada, no mostrar datos
        queryset = QualityData.objects.none()
    
    # Aplicar filtros adicionales
    empresa = request.query_params.get('empresa')
    if empresa:
        queryset = queryset.filter(empresa__icontains=empresa)
    
    fecha_desde = request.query_params.get('fecha_desde')
    if fecha_desde:
        try:
            fecha_desde = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
            queryset = queryset.filter(fecha_registro__gte=fecha_desde)
        except:
            pass
    
    fecha_hasta = request.query_params.get('fecha_hasta')
    if fecha_hasta:
        try:
            fecha_hasta = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
            queryset = queryset.filter(fecha_registro__lte=fecha_hasta)
        except:
            pass
    
    # Serializar datos de forma síncrona
    serializer = QualityDataListSerializer(queryset, many=True)
    
    return Response({
        'data': serializer.data,
        'total_records': queryset.count(),
        'export_date': timezone.now().isoformat()
    })
