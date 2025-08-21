from django.urls import path
from . import views

app_name = 'quality_data'

urlpatterns = [
    # Vistas principales
    path('quality-data/', views.QualityDataListCreateView.as_view(), name='quality-data-list'),
    path('quality-data/<int:pk>/', views.QualityDataDetailView.as_view(), name='quality-data-detail'),
    
    # Vistas de filtrado y búsqueda
    path('quality-data/filter/', views.QualityDataFilterView.as_view(), name='quality-data-filter'),
    
    # Vistas de estadísticas y dashboard
    path('quality-data/stats/', views.quality_data_stats, name='quality-data-stats'),
    path('quality-data/dashboard/', views.quality_data_dashboard, name='quality-data-dashboard'),
    
    # Vistas de sincronización
    path('quality-data/sync/', views.sync_external_quality_data, name='quality-data-sync'),
    
    # Vistas de exportación
    path('quality-data/export/', views.quality_data_export, name='quality-data-export'),
]
