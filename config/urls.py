"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from app import views
from django.contrib.auth import views as auth_views
from app.views import VendedorListView, VendedorDetailView

urlpatterns = [
    # Página inicial (Filtro)
    path('', views.FiltroView.as_view(), name='home'),
    
    # Página de comparação
    path('comparar/', views.CompararView.as_view(), name='comparar'),
    
    # Página de detalhes do carro
    path('detalhes/<int:pk>/', views.DetalhesView.as_view(), name='detalhes'),
    
    # Páginas de agendamento
    path('agendar-test-drive/<int:carro_id>/', views.AgendarTestDriveView.as_view(), name='agendar_test_drive'),
    path('agendamento-confirmado/', views.AgendamentoConfirmadoView.as_view(), name='agendamento_confirmado'),
    
    # Páginas de financiamento
    path('financiamento/<int:carro_id>/', views.financiamento_calculo, name='financiamento'),
    
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='Login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Perfil do usuário
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('editar-perfil/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    
    path('vendedores/', VendedorListView.as_view(), name='vendedor_list'),
    path('vendedores/<int:pk>/', VendedorDetailView.as_view(), name='vendedor_detail'),
    
    # API para filtros (se necessário)
    path('api/carros/', views.CarrosAPIView.as_view(), name='api_carros'),
]