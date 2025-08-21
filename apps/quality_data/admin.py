from django.contrib import admin
from .models import QualityData


@admin.register(QualityData)
class QualityDataAdmin(admin.ModelAdmin):
    """
    Configuración del admin para datos de calidad
    """
    list_display = [
        'empresa', 'fecha_registro', 'temperatura', 'humedad', 'ph',
        'calidad_general', 'aprobado', 'created_at'
    ]
    
    list_filter = [
        'empresa', 'calidad_general', 'aprobado', 'fecha_registro',
        'created_at', 'company'
    ]
    
    search_fields = [
        'empresa', 'defectos_descripcion', 'observaciones',
        'company__name', 'created_by__email'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'empresa_display', 
        'calidad_display', 'aprobado_display'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'empresa_display', 'fecha_registro', 'company')
        }),
        ('Mediciones de Calidad', {
            'fields': ('temperatura', 'humedad', 'ph')
        }),
        ('Calidad del Producto', {
            'fields': ('firmeza', 'solidos_solubles', 'acidez_titulable')
        }),
        ('Defectos', {
            'fields': ('defectos_porcentaje', 'defectos_descripcion')
        }),
        ('Clasificación', {
            'fields': ('calibre', 'color', 'calidad_general', 'calidad_display')
        }),
        ('Aprobación', {
            'fields': ('aprobado', 'aprobado_display', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Datos Originales', {
            'fields': ('processed_data',),
            'classes': ('collapse',)
        }),
    )
    
    def empresa_display(self, obj):
        return obj.empresa_display
    empresa_display.short_description = 'Empresa (Display)'
    
    def calidad_display(self, obj):
        return obj.calidad_display
    calidad_display.short_description = 'Calidad (Display)'
    
    def aprobado_display(self, obj):
        return obj.aprobado_display
    aprobado_display.short_description = 'Aprobado (Display)'
    
    def get_queryset(self, request):
        """
        Optimizar consultas con select_related
        """
        return super().get_queryset(request).select_related('company', 'created_by')
    
    def save_model(self, request, obj, form, change):
        """
        Asignar usuario creador si es un nuevo registro
        """
        if not change:  # Si es un nuevo registro
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
