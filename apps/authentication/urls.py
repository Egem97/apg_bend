from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Rutas de usuarios
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:id>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Rutas de empresas
    path('companies/', views.CompanyListCreateView.as_view(), name='company_list_create'),
    path('companies/<int:id>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:company_id>/users/', views.company_users, name='company_users'),
    path('companies/<int:company_id>/stats/', views.company_stats, name='company_stats'),
    
    # Rutas de roles
    path('roles/', views.RoleListCreateView.as_view(), name='role_list_create'),
    path('roles/<int:id>/', views.RoleDetailView.as_view(), name='role_detail'),
]
