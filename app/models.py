from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



# Usuário
from django.core.validators import RegexValidator

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nome = models.CharField(max_length=100, verbose_name="Nome completo")
    telefone = models.CharField(
        max_length=15,
        verbose_name="Telefone",
        validators=[RegexValidator(r'^\+?\d{10,15}$', "Número de telefone inválido")]
    )
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)

    OCUPACOES = [
        ("cliente", "Cliente"),
        ("funcionario", "Funcionário"),
        ("gerente", "Gerente"),
    ]
    ocupacao = models.CharField(
        max_length=20,
        choices=OCUPACOES,
        default="cliente",
        verbose_name="Ocupação"
    )

    # Campos caso o tipo do usuário for funcionário
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name="CPF")
    data_admissao = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nome or self.user.username

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"














# Carro
class Carro(models.Model):
    MARCA_CHOICES = [
        ('Chevrolet', 'Chevrolet'),
        ('Fiat', 'Fiat'),
        ('Ford', 'Ford'),
        ('Honda', 'Honda'),
        ('Hyundai', 'Hyundai'),
        ('Jeep', 'Jeep'),
        ('Nissan', 'Nissan'),
        ('Peugeot', 'Peugeot'),
        ('Renault', 'Renault'),
        ('Toyota', 'Toyota'),
        ('Volkswagen', 'Volkswagen'),
        ('Audi', 'Audi'),
        ('BMW', 'BMW'),
        ('Mercedes-Benz', 'Mercedes-Benz'),
        ('Outra', 'Outra'),
    ]
    
    COR_CHOICES = [
        ('Branco', 'Branco'),
        ('Preto', 'Preto'),
        ('Prata', 'Prata'),
        ('Cinza', 'Cinza'),
        ('Vermelho', 'Vermelho'),
        ('Azul', 'Azul'),
        ('Verde', 'Verde'),
        ('Amarelo', 'Amarelo'),
        ('Laranja', 'Laranja'),
        ('Marrom', 'Marrom'),
        ('Bege', 'Bege'),
        ('Dourado', 'Dourado'),
        ('Outra', 'Outra'),
    ]
    
    TIPO_CHOICES = [
        ('Hatch', 'Hatch'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Picape', 'Picape'),
        ('Esportivo', 'Esportivo'),
    ]
    
    CAMBIO_CHOICES = [
        ('Manual', 'Manual'),
        ('Automático', 'Automático'),
        ('Automático Sequencial', 'Automático Sequencial'),
        ('CVT', 'CVT'),
    ]
    
    COMBUSTIVEL_CHOICES = [
        ('Gasolina', 'Gasolina'),
        ('Álcool', 'Álcool'),
        ('Flex', 'Flex'),
        ('Diesel', 'Diesel'),
        ('Híbrido', 'Híbrido'),
        ('Elétrico', 'Elétrico'),
    ]
    
    marca = models.CharField(max_length=50, choices=MARCA_CHOICES, verbose_name="Marca")
    cor = models.CharField(max_length=20, choices=COR_CHOICES, verbose_name="Cor")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    ano = models.IntegerField(verbose_name="Ano")
    motor = models.CharField(max_length=30, verbose_name="Motor")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    km = models.IntegerField(verbose_name="Quilometragem")
    cambio = models.CharField(max_length=50, choices=CAMBIO_CHOICES, verbose_name="Câmbio")
    combustivel = models.CharField(max_length=50, choices=COMBUSTIVEL_CHOICES, verbose_name="Combustível")
    ipva_pago = models.BooleanField(verbose_name="IPVA pago")
    consumo_cidade = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Consumo na cidade (km/l)")
    consumo_estrada = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Consumo na estrada (km/l)")

    def __str__(self):
        return f"{self.marca} {self.modelo} {self.ano}"

    class Meta:
        verbose_name = "Carro"
        verbose_name_plural = "Carros"


class ImagemCarro(models.Model):
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, verbose_name="Carro", related_name='imagens')
    foto_url = models.CharField(max_length=255, verbose_name="URL da foto")

    def __str__(self):
        return f"Imagem de {self.carro}"

    class Meta:
        verbose_name = "Imagem de Carro"
        verbose_name_plural = "Imagens de Carros"




















class Venda(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('À vista', 'À vista'),
        ('Financiamento', 'Financiamento'),
        ('Consórcio', 'Consórcio'),
        ('Cartão de crédito', 'Cartão de crédito'),
    ]
    
    carro = models.ForeignKey(
        Carro, 
        on_delete=models.PROTECT, 
        verbose_name="Carro"
    )
    vendedor = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        limit_choices_to={'ocupacao': 'funcionario'},  # só mostra funcionários no admin
        related_name='vendas_realizadas',
        verbose_name="Vendedor"
    )
    cliente = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        limit_choices_to={'ocupacao': 'cliente'},  # só mostra clientes no admin
        related_name='compras',
        verbose_name="Cliente"
    )
    data_venda = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data da venda"
    )
    valor_venda = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Valor da venda"
    )
    forma_pagamento = models.CharField(
        max_length=50, 
        choices=FORMA_PAGAMENTO_CHOICES, 
        verbose_name="Forma de pagamento"
    )
    parcelas = models.IntegerField(
        null=True, blank=True, 
        verbose_name="Parcelas"
    )
    observacoes = models.TextField(
        null=True, blank=True, 
        verbose_name="Observações"
    )

    def __str__(self):
        return f"Venda #{self.id} - {self.carro}"

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"













# Test Drive
class TestDrive(models.Model):
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='test_drives'
    )

    def __str__(self):
        return f"Test Drive - {self.carro} ({self.data} {self.horario}) - {self.usuario.username if self.usuario else 'Sem usuário'}"