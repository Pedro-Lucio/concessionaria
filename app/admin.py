from django.contrib import admin
from .models import AgendamentoTestDrive, Venda

@admin.register(AgendamentoTestDrive)
class AgendamentoTestDriveAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_usuario', 'get_carro', 'get_vendedor', 'data_agendamento', 'status')
    list_filter = ('status', 'data_agendamento')
    search_fields = ('usuario__nome', 'carro__marca', 'carro__modelo')
    date_hierarchy = 'data_agendamento'
    
    def get_usuario(self, obj):
        return obj.usuario.nome
    get_usuario.short_description = 'Usuário'
    get_usuario.admin_order_field = 'usuario__nome'
    
    def get_carro(self, obj):
        return f"{obj.carro.marca} {obj.carro.modelo}"
    get_carro.short_description = 'Carro'
    
    def get_vendedor(self, obj):
        return obj.vendedor.nome if obj.vendedor else '-'
    get_vendedor.short_description = 'Vendedor'

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_carro', 'get_vendedor', 'get_usuario', 'data_venda', 'valor_venda', 'forma_pagamento')
    list_filter = ('forma_pagamento', 'data_venda')
    search_fields = ('carro__marca', 'carro__modelo', 'vendedor__nome', 'usuario__nome')
    date_hierarchy = 'data_venda'
    
    def get_carro(self, obj):
        return f"{obj.carro.marca} {obj.carro.modelo}"
    get_carro.short_description = 'Carro'
    
    def get_vendedor(self, obj):
        return obj.vendedor.nome
    get_vendedor.short_description = 'Vendedor'
    
    def get_usuario(self, obj):
        return obj.usuario.nome if obj.usuario else '-'
    get_usuario.short_description = 'Usuário'