from rest_framework import serializers
from .models import Product, Shipment, Inspection, QualityReport, Sample


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'


class QualityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityReport
        fields = '__all__'


class InspectionSerializer(serializers.ModelSerializer):
    quality_report = QualityReportSerializer(read_only=True)
    samples = SampleSerializer(many=True, read_only=True)
    inspection_type_display = serializers.CharField(source='get_inspection_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Inspection
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    inspections = InspectionSerializer(many=True, read_only=True)
    transport_type_display = serializers.CharField(source='get_transport_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ('created_by',)

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ShipmentListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de embarques"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    transport_type_display = serializers.CharField(source='get_transport_type_display', read_only=True)
    inspections_count = serializers.IntegerField(source='inspections.count', read_only=True)
    
    class Meta:
        model = Shipment
        fields = ['id', 'reference', 'product_name', 'shipper', 'consignee', 
                 'transport_type_display', 'location', 'date', 'inspections_count']
