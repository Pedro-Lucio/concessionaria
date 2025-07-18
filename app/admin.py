from django.contrib import admin
from .models import (
    Carro, ImagemCarro, Usuario, 
    Vendedor, Venda, AgendamentoTestDrive
)
from django.utils.html import format_html

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
        'nome', 'email', 'telefone', 
        'total_agendamentos', 'total_compras'
    )
    search_fields = ('nome', 'email', 'telefone')
    list_per_page = 20

    def total_agendamentos(self, obj):
        return obj.agendamentotestdrive_set.count()
    total_agendamentos.short_description = 'Test Drives'

    def total_compras(self, obj):
        return obj.venda_set.count()
    total_compras.short_description = 'Compras'

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'email', 'telefone', 
        'data_admissao', 'status', 
        'total_vendas'
    )
    list_filter = ('ativo', 'data_admissao')
    search_fields = ('nome', 'email', 'cpf')
    date_hierarchy = 'data_admissao'

    def status(self, obj):
        return "Ativo" if obj.ativo else "Inativo"
    status.short_description = 'Status'
    status.admin_order_field = 'ativo'

    def total_vendas(self, obj):
        return obj.venda_set.count()
    total_vendas.short_description = 'Vendas'

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

@admin.register(AgendamentoTestDrive)
class AgendamentoTestDriveAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente_info', 'carro_info', 
        'vendedor_info', 'data_agendamento', 
        'status',  # Campo original para edição
        'status_colorido',  # Versão formatada para visualização
        'dias_restantes'
    )
    list_editable = ('status',)
    list_filter = (
        'status', 'data_agendamento', 
        'vendedor'
    )
    search_fields = (
        'usuario__nome', 'carro__marca', 
        'carro__modelo', 'vendedor__nome'
    )
    date_hierarchy = 'data_agendamento'
    list_editable = ('status',)
    list_select_related = ('usuario', 'carro', 'vendedor')

    def cliente_info(self, obj):
        return obj.usuario.nome
    cliente_info.short_description = 'Cliente'

    def carro_info(self, obj):
        return f"{obj.carro.marca} {obj.carro.modelo}"
    carro_info.short_description = 'Carro'

    def vendedor_info(self, obj):
        return obj.vendedor.nome if obj.vendedor else '-'
    vendedor_info.short_description = 'Vendedor'

    def status_colorido(self, obj):
        colors = {
            'agendado': 'orange',
            'realizado': 'green',
            'cancelado': 'red',
            'remarcado': 'blue'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colorido.short_description = 'Status'

    def dias_restantes(self, obj):
        from django.utils import timezone
        delta = obj.data_agendamento - timezone.now()
        if delta.days > 0:
            return f"Em {delta.days} dias"
        elif delta.days == 0:
            return "Hoje"
        return f"Há {abs(delta.days)} dias"
    dias_restantes.short_description = 'Quando'