from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import Company

User = get_user_model()


class QualityData(models.Model):
    """
    Modelo para almacenar datos de calidad de arándanos obtenidos de la API externa
    """
    # Campos de identificación
    empresa = models.CharField(max_length=200, verbose_name="Empresa")
    fecha_registro = models.DateTimeField(verbose_name="Fecha de Registro")
    
    # Campos de calidad
    temperatura = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Temperatura (°C)"
    )
    humedad = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Humedad (%)"
    )
    ph = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="pH"
    )
    
    # Campos de calidad del producto
    firmeza = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Firmeza"
    )
    solidos_solubles = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Sólidos Solubles (°Brix)"
    )
    acidez_titulable = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Acidez Titulable (%)"
    )
    
    # Campos de defectos
    defectos_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Porcentaje de Defectos"
    )
    defectos_descripcion = models.TextField(
        blank=True, 
        verbose_name="Descripción de Defectos"
    )
    
    # Campos de clasificación
    calibre = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Calibre"
    )
    color = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Color"
    )
    calidad_general = models.CharField(
        max_length=20,
        choices=[
            ('excelente', 'Excelente'),
            ('buena', 'Buena'),
            ('regular', 'Regular'),
            ('mala', 'Mala'),
        ],
        blank=True,
        verbose_name="Calidad General"
    )
    
    # Campos de aprobación
    aprobado = models.BooleanField(
        default=False, 
        verbose_name="Aprobado"
    )
    observaciones = models.TextField(
        blank=True, 
        verbose_name="Observaciones"
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Creado por"
    )
    
    # Relación con la empresa del sistema
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='quality_data',
        null=True,
        blank=True,
        verbose_name="Empresa del Sistema"
    )
    
    # Campo para datos procesados de la API
    processed_data = models.JSONField(
        default=dict, 
        verbose_name="Datos Procesados de la API"
    )

    class Meta:
        verbose_name = "Dato de Calidad"
        verbose_name_plural = "Datos de Calidad"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['empresa']),
            models.Index(fields=['fecha_registro']),
            models.Index(fields=['calidad_general']),
            models.Index(fields=['aprobado']),
        ]

    def __str__(self):
        return f"{self.empresa} - {self.fecha_registro.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        # Intentar asociar con una empresa del sistema si no está asignada
        if not self.company and self.empresa:
            try:
                company = Company.objects.filter(name__icontains=self.empresa).first()
                if company:
                    self.company = company
            except:
                pass
        super().save(*args, **kwargs)

    @property
    def empresa_display(self):
        """Retorna el nombre de la empresa para mostrar"""
        return self.empresa or (self.company.name if self.company else "Sin empresa")

    @property
    def calidad_display(self):
        """Retorna la calidad general para mostrar"""
        return dict(self._meta.get_field('calidad_general').choices).get(
            self.calidad_general, self.calidad_general
        )

    @property
    def aprobado_display(self):
        """Retorna el estado de aprobación para mostrar"""
        return "Sí" if self.aprobado else "No"
