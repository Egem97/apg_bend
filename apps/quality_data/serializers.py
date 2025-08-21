from rest_framework import serializers
from .models import QualityData


class QualityDataSerializer(serializers.ModelSerializer):
    """
    Serializer para datos de calidad
    """
    empresa_display = serializers.ReadOnlyField()
    calidad_display = serializers.ReadOnlyField()
    aprobado_display = serializers.ReadOnlyField()
    company_name = serializers.ReadOnlyField(source='company.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.full_name')
    
    # Campos adicionales desde processed_data
    destino = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    presentacion = serializers.SerializerMethodField()
    tipo_producto = serializers.SerializerMethodField()
    trazabilidad = serializers.SerializerMethodField()
    peso_muestra = serializers.SerializerMethodField()
    total_exportable = serializers.SerializerMethodField()
    total_no_exportable = serializers.SerializerMethodField()
    evaluador = serializers.SerializerMethodField()
    fundo = serializers.SerializerMethodField()
    linea = serializers.SerializerMethodField()
    turno = serializers.SerializerMethodField()
    semana = serializers.SerializerMethodField()

    class Meta:
        model = QualityData
        fields = [
            'id', 'empresa', 'empresa_display', 'fecha_registro',
            'temperatura', 'humedad', 'ph',
            'firmeza', 'solidos_solubles', 'acidez_titulable',
            'defectos_porcentaje', 'defectos_descripcion',
            'calibre', 'color', 'calidad_general', 'calidad_display',
            'aprobado', 'aprobado_display', 'observaciones',
            'company', 'company_name', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'processed_data',
            # Campos adicionales
            'destino', 'variedad', 'presentacion', 'tipo_producto',
            'trazabilidad', 'peso_muestra', 'total_exportable',
            'total_no_exportable', 'evaluador', 'fundo', 'linea',
            'turno', 'semana'
        ]
        read_only_fields = [
            'id', 'empresa_display', 'calidad_display', 'aprobado_display',
            'company_name', 'created_by_name', 'created_at', 'updated_at',
            'destino', 'variedad', 'presentacion', 'tipo_producto',
            'trazabilidad', 'peso_muestra', 'total_exportable',
            'total_no_exportable', 'evaluador', 'fundo', 'linea',
            'turno', 'semana'
        ]
    
    def get_destino(self, obj):
        """Obtiene el destino desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('destino')
        return None
    
    def get_variedad(self, obj):
        """Obtiene la variedad desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('variedad')
        return None
    
    def get_presentacion(self, obj):
        """Obtiene la presentación desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('presentacion')
        return None
    
    def get_tipo_producto(self, obj):
        """Obtiene el tipo de producto desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('tipo_producto')
        return None
    
    def get_trazabilidad(self, obj):
        """Obtiene la trazabilidad desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('trazabilidad')
        return None
    
    def get_peso_muestra(self, obj):
        """Obtiene el peso de muestra desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('peso_muestra')
        return None
    
    def get_total_exportable(self, obj):
        """Obtiene el total exportable desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('total_exportable')
        return None
    
    def get_total_no_exportable(self, obj):
        """Obtiene el total no exportable desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('total_no_exportable')
        return None
    
    def get_evaluador(self, obj):
        """Obtiene el evaluador desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('evaluador')
        return None
    
    def get_fundo(self, obj):
        """Obtiene el fundo desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('fundo')
        return None
    
    def get_linea(self, obj):
        """Obtiene la línea desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('linea')
        return None
    
    def get_turno(self, obj):
        """Obtiene el turno desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('turno')
        return None
    
    def get_semana(self, obj):
        """Obtiene la semana desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('semana')
        return None


class QualityDataListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listas de datos de calidad
    """
    empresa_display = serializers.ReadOnlyField()
    calidad_display = serializers.ReadOnlyField()
    aprobado_display = serializers.ReadOnlyField()
    
    # Campos adicionales importantes
    total_exportable = serializers.SerializerMethodField()
    variedad = serializers.SerializerMethodField()
    destino = serializers.SerializerMethodField()
    contenedor = serializers.SerializerMethodField()  # Campo para contenedor
    
    # Campos adicionales para la información solicitada
    evaluador = serializers.SerializerMethodField()
    fecha_mp = serializers.SerializerMethodField()
    fecha_proceso = serializers.SerializerMethodField()
    productor = serializers.SerializerMethodField()
    tipo_producto = serializers.SerializerMethodField()
    fundo = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()
    presentacion = serializers.SerializerMethodField()

    class Meta:
        model = QualityData
        fields = [
            'id', 'empresa', 'empresa_display', 'fecha_registro',
            'temperatura', 'humedad', 'ph',
            'firmeza', 'solidos_solubles', 'acidez_titulable',
            'defectos_porcentaje', 'calidad_general', 'calidad_display',
            'aprobado', 'aprobado_display', 'created_at',
            # Campos adicionales
            'total_exportable', 'variedad', 'destino', 'contenedor',
            'evaluador', 'fecha_mp', 'fecha_proceso', 'productor',
            'tipo_producto', 'fundo', 'hora', 'presentacion'
        ]
    
    def get_total_exportable(self, obj):
        """Obtiene el total exportable desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('total_exportable')
        return None
    
    def get_variedad(self, obj):
        """Obtiene la variedad desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('variedad')
        return None
    
    def get_destino(self, obj):
        """Obtiene el destino desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('destino')
        return None

    def get_contenedor(self, obj):
        """Obtiene el contenedor (N° FCL) desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('n_fcl')
        return None
    
    def get_evaluador(self, obj):
        """Obtiene el evaluador desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('evaluador')
        return None
    
    def get_fecha_mp(self, obj):
        """Obtiene la fecha de MP desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('fecha_mp')
        return None
    
    def get_fecha_proceso(self, obj):
        """Obtiene la fecha de proceso desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('fecha_proceso')
        return None
    
    def get_productor(self, obj):
        """Obtiene el productor desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('productor')
        return None
    
    def get_tipo_producto(self, obj):
        """Obtiene el tipo de producto desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('tipo_producto')
        return None
    
    def get_fundo(self, obj):
        """Obtiene el fundo desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('fundo')
        return None
    
    def get_hora(self, obj):
        """Obtiene la hora desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('hora')
        return None
    
    def get_presentacion(self, obj):
        """Obtiene la presentación desde processed_data"""
        if obj.processed_data and 'additional_info' in obj.processed_data:
            return obj.processed_data['additional_info'].get('presentacion')
        return None


class QualityDataFilterSerializer(serializers.Serializer):
    """
    Serializer para filtros de datos de calidad
    """
    empresa = serializers.CharField(required=False, help_text="Filtrar por empresa")
    fecha_desde = serializers.DateTimeField(required=False, help_text="Fecha desde")
    fecha_hasta = serializers.DateTimeField(required=False, help_text="Fecha hasta")
    calidad_general = serializers.ChoiceField(
        choices=QualityData._meta.get_field('calidad_general').choices,
        required=False,
        help_text="Filtrar por calidad general"
    )
    aprobado = serializers.BooleanField(required=False, help_text="Filtrar por estado de aprobación")
    limit = serializers.IntegerField(required=False, min_value=1, max_value=1000, help_text="Límite de registros")
    offset = serializers.IntegerField(required=False, min_value=0, help_text="Desplazamiento")


class QualityDataStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de datos de calidad
    """
    total_registros = serializers.IntegerField()
    registros_aprobados = serializers.IntegerField()
    registros_rechazados = serializers.IntegerField()
    promedio_temperatura = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    promedio_humedad = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    promedio_ph = serializers.DecimalField(max_digits=4, decimal_places=2, allow_null=True)
    calidad_breakdown = serializers.DictField()
    empresas_count = serializers.IntegerField()
