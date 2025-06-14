from django.contrib import admin
from .models import *

@admin.register(Carro)
class CarroAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'ano', 'valor', 'tipo', 'combustivel')
    list_filter = ('tipo', 'combustivel', 'cambio', 'ipva_pago')
    search_fields = ('marca', 'modelo', 'ano')
    ordering = ('marca', 'modelo')

@admin.register(ImagemCarro)
class ImagemCarroAdmin(admin.ModelAdmin):
    list_display = ('carro', 'foto_url')
    list_filter = ('carro__marca', 'carro__modelo')
    search_fields = ('carro__marca', 'carro__modelo')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone')
    search_fields = ('nome', 'email', 'telefone')
    ordering = ('nome',)

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cpf', 'data_admissao', 'ativo')
    list_filter = ('ativo', 'data_admissao')
    search_fields = ('nome', 'email', 'cpf')
    ordering = ('nome',)

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'carro', 'vendedor', 'cliente', 'data_venda', 'valor_venda', 'forma_pagamento')
    list_filter = ('forma_pagamento', 'data_venda', 'vendedor')
    search_fields = ('carro__marca', 'carro__modelo', 'vendedor__nome', 'cliente__nome')
    date_hierarchy = 'data_venda'

@admin.register(AgendamentoTestDrive)
class AgendamentoTestDriveAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'carro', 'vendedor', 'data_agendamento', 'status')
    list_filter = ('status', 'data_agendamento', 'vendedor')
    search_fields = ('cliente__nome', 'carro__marca', 'carro__modelo', 'vendedor__nome')
    date_hierarchy = 'data_agendamento'