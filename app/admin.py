from django.contrib import admin
from .models import (
    Carro, ImagemCarro, Usuario, Venda
)
from django.utils.html import format_html
from .models import TestDrive

# ========== CARRO E IMAGENS ==========
class ImagemCarroInline(admin.TabularInline):
    model = ImagemCarro
    extra = 1
    fields = ('foto_url', 'imagem_preview')
    readonly_fields = ('imagem_preview',)

    def imagem_preview(self, obj):
        if obj.foto_url:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.foto_url)
        return "-"
    imagem_preview.short_description = "Pré-visualização"

@admin.register(Carro)
class CarroAdmin(admin.ModelAdmin):
    list_display = (
        'modelo', 'marca', 'ano', 'tipo', 
        'valor_formatado', 'km', 'combustivel', 
        'ipva_status'
    )
    list_filter = (
        'marca', 'tipo', 'combustivel', 
        'cambio', 'ipva_pago'
    )
    search_fields = (
        'marca', 'modelo', 'ano', 'cor'
    )
    inlines = [ImagemCarroInline]
    ordering = ('-ano', 'marca', 'modelo')
    list_per_page = 20

    def valor_formatado(self, obj):
        return f"R$ {obj.valor:,.2f}"
    valor_formatado.short_description = 'Valor'
    valor_formatado.admin_order_field = 'valor'

    def ipva_status(self, obj):
        return "Pago" if obj.ipva_pago else "Pendente"
    ipva_status.short_description = 'IPVA'

@admin.register(ImagemCarro)
class ImagemCarroAdmin(admin.ModelAdmin):
    list_display = ('carro', 'imagem_preview')
    list_select_related = ('carro',)
    search_fields = ('carro__marca', 'carro__modelo')

    def imagem_preview(self, obj):
        if obj.foto_url:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.foto_url)
        return "-"
    imagem_preview.short_description = "Imagem"

# ========== USUÁRIOS E VENDEDORES ==========
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'nome_completo', 'email_usuario', 'telefone',
        'ocupacao', 'total_agendamentos', 'total_compras'
    )
    search_fields = ('nome', 'telefone', 'user__username', 'user__email')
    list_filter = ('ocupacao',)
    list_per_page = 20

    def nome_completo(self, obj):
        return obj.nome or obj.user.get_full_name() or obj.user.username
    nome_completo.short_description = 'Nome'

    def email_usuario(self, obj):
        return obj.email or obj.user.email
    email_usuario.short_description = 'E-mail'

    def total_agendamentos(self, obj):
        return obj.testdrive_set.count()
    total_agendamentos.short_description = 'Test Drives'

    def total_compras(self, obj):
        return obj.venda_set.count()
    total_compras.short_description = 'Compras'


# ========== VENDAS E AGENDAMENTOS ==========
class VendaInline(admin.TabularInline):
    model = Venda
    extra = 0
    fields = ('carro', 'valor_venda', 'data_venda')
    readonly_fields = ('data_venda',)
    show_change_link = True

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'carro_info', 'vendedor_info', 
        'cliente_info', 'data_venda', 
        'valor_formatado', 'forma_pagamento', 
        'parcelas_info'
    )
    list_filter = (
        'forma_pagamento', 'data_venda', 
        'vendedor'
    )
    search_fields = (
        'carro__marca', 'carro__modelo',
        'vendedor__nome', 'usuario__nome'
    )
    date_hierarchy = 'data_venda'
    list_select_related = ('carro', 'vendedor', 'usuario')

    def carro_info(self, obj):
        return f"{obj.carro.marca} {obj.carro.modelo}"
    carro_info.short_description = 'Carro'
    carro_info.admin_order_field = 'carro__modelo'

    def vendedor_info(self, obj):
        return obj.vendedor.nome
    vendedor_info.short_description = 'Vendedor'

    def cliente_info(self, obj):
        return obj.usuario.nome if obj.usuario else '-'
    cliente_info.short_description = 'Cliente'

    def valor_formatado(self, obj):
        return f"R$ {obj.valor_venda:,.2f}"
    valor_formatado.short_description = 'Valor'

    def parcelas_info(self, obj):
        return f"{obj.parcelas}x" if obj.parcelas else 'À vista'
    parcelas_info.short_description = 'Parcelas'

@admin.register(TestDrive)
class TestDriveAdmin(admin.ModelAdmin):
    list_display = ('carro', 'data', 'horario', 'criado_em')
    search_fields = ('carro__marca', 'carro__modelo')
    list_filter = ('data',)