from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Product(models.Model):
    """
    Modelo para productos agrícolas
    """
    name = models.CharField(max_length=100, verbose_name="Nombre del producto")
    description = models.TextField(blank=True, verbose_name="Descripción")
    variety = models.CharField(max_length=50, blank=True, verbose_name="Variedad")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def __str__(self):
        return self.name


class Shipment(models.Model):
    """
    Modelo para embarques/envíos
    """
    TRANSPORT_CHOICES = [
        ('road', 'Transporte terrestre'),
        ('sea', 'Transporte marítimo'),
        ('air', 'Transporte aéreo'),
    ]

    reference = models.CharField(max_length=50, unique=True, verbose_name="Referencia")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    shipper = models.CharField(max_length=100, verbose_name="Expedidor")
    consignee = models.CharField(max_length=100, verbose_name="Consignatario")
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, verbose_name="Tipo de transporte")
    location = models.CharField(max_length=100, verbose_name="Ubicación")
    date = models.DateField(verbose_name="Fecha")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Embarque"
        verbose_name_plural = "Embarques"
        ordering = ['-date']

    def __str__(self):
        return f"{self.reference} - {self.product.name}"


class Inspection(models.Model):
    """
    Modelo para inspecciones de calidad
    """
    INSPECTION_TYPES = [
        ('grower', 'Inspección del productor'),
        ('quality', 'Inspección de calidad'),
        ('phytosanitary', 'Inspección fitosanitaria'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completada'),
        ('rejected', 'Rechazada'),
    ]

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='inspections', verbose_name="Embarque")
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPES, verbose_name="Tipo de inspección")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    inspection_point = models.CharField(max_length=100, verbose_name="Punto de inspección")
    inspector = models.CharField(max_length=100, verbose_name="Inspector")
    inspection_date = models.DateTimeField(verbose_name="Fecha de inspección")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inspección"
        verbose_name_plural = "Inspecciones"
        ordering = ['-inspection_date']

    def __str__(self):
        return f"Inspección {self.get_inspection_type_display()} - {self.shipment.reference}"


class QualityReport(models.Model):
    """
    Modelo para reportes de calidad
    """
    inspection = models.OneToOneField(Inspection, on_delete=models.CASCADE, related_name='quality_report', verbose_name="Inspección")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Temperatura (°C)")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Humedad (%)")
    ph_level = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Nivel de pH")
    defects_found = models.TextField(blank=True, verbose_name="Defectos encontrados")
    overall_quality = models.CharField(max_length=20, choices=[
        ('excellent', 'Excelente'),
        ('good', 'Buena'),
        ('fair', 'Regular'),
        ('poor', 'Mala'),
    ], verbose_name="Calidad general")
    approved = models.BooleanField(default=False, verbose_name="Aprobado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reporte de Calidad"
        verbose_name_plural = "Reportes de Calidad"

    def __str__(self):
        return f"Reporte - {self.inspection}"


class Sample(models.Model):
    """
    Modelo para muestras tomadas durante inspecciones
    """
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='samples', verbose_name="Inspección")
    sample_id = models.CharField(max_length=50, verbose_name="ID de muestra")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")
    unit = models.CharField(max_length=20, default='kg', verbose_name="Unidad")
    location_taken = models.CharField(max_length=100, verbose_name="Ubicación de toma")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Muestra"
        verbose_name_plural = "Muestras"
        ordering = ['sample_id']

    def __str__(self):
        return f"Muestra {self.sample_id} - {self.inspection}"
