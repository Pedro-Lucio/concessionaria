from django.contrib import admin
from django.urls import path
from app import views
from django.contrib.auth import views as auth_views
from app.views import *

urlpatterns = [
    # Página inicial (Index)
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    #



    # Perfil do usuário
    # path('perfil/', views.PerfilView.as_view(), name='perfil'),
    # path('editar-perfil/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    # Editar o perfil
    path('perfil/', views.meu_perfil, name='meu_perfil'),






    # Autenticação(Auth)
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),

    # Logout
    path('logout/', logout_view, name='logout'),





    # Página de detalhes do carro
    path('detalhes/<int:pk>/', views.DetalhesView.as_view(), name='detalhes'),
    # Página de comparação de carros
    path('comparar/', views.CompararView.as_view(), name='comparar'),
    # Agendamento
    path('carro/<int:carro_id>/test-drive/', views.agendar_test_drive, name='agendar_test_drive'),
    # Páginas de financiamento
    path('financiamento/<int:carro_id>/', views.financiamento_calculo, name='financiamento'),








    # Página de reciclagem
    path('reciclagem/', views.ReciclagemView.as_view(), name='reciclagem'),








    # Página da tabela consultar FIPE
    path('consultar/', views.ConsultarFIPEView.as_view(), name='consultarfipe'),









    # Urls disponiveis somente para gerente
    
    # Funcionários
    path('funcionario/', FuncionarioListView.as_view(), name='funcionario_lista'),
    path('funcionario/<int:pk>/', FuncionarioDetailView.as_view(), name='funcionario_detalhado'),
    path('funcionario/novo/', views.criar_funcionario, name='criar_funcionario'),
]

