from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Products
    path('products/', views.ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Shipments
    path('shipments/', views.ShipmentListCreateView.as_view(), name='shipment_list_create'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    
    # Inspections
    path('inspections/', views.InspectionListCreateView.as_view(), name='inspection_list_create'),
    path('inspections/<int:pk>/', views.InspectionDetailView.as_view(), name='inspection_detail'),
    
    # Quality Reports
    path('quality-reports/', views.QualityReportListCreateView.as_view(), name='quality_report_list_create'),
    path('quality-reports/<int:pk>/', views.QualityReportDetailView.as_view(), name='quality_report_detail'),
    
    # Samples
    path('samples/', views.SampleListCreateView.as_view(), name='sample_list_create'),
    path('samples/<int:pk>/', views.SampleDetailView.as_view(), name='sample_detail'),
]
