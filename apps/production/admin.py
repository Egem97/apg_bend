from django.contrib import admin
from .models import Product, Shipment, Inspection, QualityReport, Sample


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'variety', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'variety', 'description')


class InspectionInline(admin.TabularInline):
    model = Inspection
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'product', 'shipper', 'consignee', 'transport_type', 'date', 'created_by')
    list_filter = ('transport_type', 'date', 'created_at')
    search_fields = ('reference', 'shipper', 'consignee', 'location')
    inlines = [InspectionInline]
    readonly_fields = ('created_at', 'updated_at')


class QualityReportInline(admin.StackedInline):
    model = QualityReport
    extra = 0


class SampleInline(admin.TabularInline):
    model = Sample
    extra = 0


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'inspection_type', 'status', 'inspector', 'inspection_date')
    list_filter = ('inspection_type', 'status', 'inspection_date')
    search_fields = ('shipment__reference', 'inspector', 'inspection_point')
    inlines = [QualityReportInline, SampleInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QualityReport)
class QualityReportAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'overall_quality', 'approved', 'created_at')
    list_filter = ('overall_quality', 'approved', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'inspection', 'quantity', 'unit', 'location_taken')
    list_filter = ('unit', 'created_at')
    search_fields = ('sample_id', 'inspection__shipment__reference', 'location_taken')
