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

from django.contrib import admin
from django.urls import path
from app import views
from django.contrib.auth import views as auth_views
from app.views import *

urlpatterns = [
    # Página inicial (Index)
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    

    # Página de detalhes do carro
    path('detalhes/<int:pk>/', views.DetalhesView.as_view(), name='detalhes'),
    

    # Página de comparação de carros
    path('comparar/', views.CompararView.as_view(), name='comparar'),
    

    # Páginas de financiamento
    path('financiamento/<int:carro_id>/', views.financiamento_calculo, name='financiamento'),


    # Vendedores
    path('vendedores/', VendedorListView.as_view(), name='vendedor_lista'),
    path('vendedores/<int:pk>/', VendedorDetailView.as_view(), name='vendedor_detalhado'),
    

    # Perfil do usuário
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('editar-perfil/', views.EditarPerfilView.as_view(), name='editar_perfil'),


    # Página de reciclagem
    path('reciclagem/', views.ReciclagemView.as_view(), name='reciclagem'),


    # Autenticação
    path('login/', LoginView, name='login'),
    path('register/', RegisterView, name='register'),

    # Logout
    path('logout/', LogoutView, name='logout'),

    path('carro/<int:carro_id>/test-drive/', views.agendar_test_drive, name='agendar_test_drive'),
]

