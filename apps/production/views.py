from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from .models import Product, Shipment, Inspection, QualityReport, Sample
from .serializers import (
    ProductSerializer, ShipmentSerializer, ShipmentListSerializer,
    InspectionSerializer, QualityReportSerializer, SampleSerializer
)


# Product Views
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# Shipment Views
class ShipmentListCreateView(generics.ListCreateAPIView):
    queryset = Shipment.objects.select_related('product', 'created_by').prefetch_related('inspections')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShipmentListSerializer
        return ShipmentSerializer


class ShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shipment.objects.select_related('product', 'created_by').prefetch_related('inspections__quality_report', 'inspections__samples')
    serializer_class = ShipmentSerializer


# Inspection Views
class InspectionListCreateView(generics.ListCreateAPIView):
    queryset = Inspection.objects.select_related('shipment__product').prefetch_related('quality_report', 'samples')
    serializer_class = InspectionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        shipment_id = self.request.query_params.get('shipment_id')
        if shipment_id:
            queryset = queryset.filter(shipment_id=shipment_id)
        return queryset


class InspectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inspection.objects.select_related('shipment__product').prefetch_related('quality_report', 'samples')
    serializer_class = InspectionSerializer


# Quality Report Views
class QualityReportListCreateView(generics.ListCreateAPIView):
    queryset = QualityReport.objects.select_related('inspection__shipment')
    serializer_class = QualityReportSerializer


class QualityReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QualityReport.objects.select_related('inspection__shipment')
    serializer_class = QualityReportSerializer


# Sample Views
class SampleListCreateView(generics.ListCreateAPIView):
    queryset = Sample.objects.select_related('inspection__shipment')
    serializer_class = SampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        inspection_id = self.request.query_params.get('inspection_id')
        if inspection_id:
            queryset = queryset.filter(inspection_id=inspection_id)
        return queryset


class SampleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sample.objects.select_related('inspection__shipment')
    serializer_class = SampleSerializer


# Dashboard Statistics
@api_view(['GET'])
def dashboard_stats(request):
    """
    Estadísticas para el dashboard
    """
    stats = {
        'total_shipments': Shipment.objects.count(),
        'total_products': Product.objects.count(),
        'total_inspections': Inspection.objects.count(),
        'pending_inspections': Inspection.objects.filter(status='pending').count(),
        'completed_inspections': Inspection.objects.filter(status='completed').count(),
        'recent_shipments': ShipmentListSerializer(
            Shipment.objects.select_related('product')[:5], 
            many=True
        ).data,
        'inspection_status_breakdown': list(
            Inspection.objects.values('status')
            .annotate(count=Count('status'))
            .order_by('status')
        ),
    }
    
    return Response(stats)
