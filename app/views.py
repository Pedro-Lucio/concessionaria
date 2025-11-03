# Import geral
from .models import *
from .forms import *
#

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash

# Enviar notificações ao usuário
from django.contrib import messages

# Para fazer com que o login seja necessário ao utilizar a View
from django.contrib.auth.decorators import login_required

# Utilizados nas views de login e logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# Para datas
from datetime import datetime, date, time, timedelta
from calendar import monthcalendar, monthrange

import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

from django.http import JsonResponse
from django.db.models import Q

from .models import Carro, HistoricoAlteracaoCarro






# Página inicial
class IndexView(View):
    def get(self, request):
        carros = Carro.objects.all()

        if carros.exists():
            preco_min = float(carros.order_by('valor').first().valor)
            preco_max = float(carros.order_by('-valor').first().valor)
        else:
            preco_min, preco_max = 0, 100000

        return render(request, 'index.html', {
            'carros': carros,
            'preco_min': int(preco_min),
            'preco_max': int(preco_max),
        })









# Parte de login e register do Auth
def login_view(request):
    # Se o usuário já estiver autenticado, redirecione para a página inicial
    if request.user.is_authenticated:
        return redirect('index')
    
    error_message = None
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Configurar sessão persistente se "Lembrar-me" estiver marcado
                remember_me = request.POST.get('remember_me') == 'on'
                if not remember_me:
                    # Sessão expira quando o navegador é fechado
                    request.session.set_expiry(0)
                
                # Redirecionar para a próxima página ou página inicial
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
        
        # Se chegou aqui, as credenciais estão inválidas
        error_message = "Usuário ou senha inválidos. Por favor, tente novamente."
    
    context = {
        'form': AuthenticationForm(),
        'error_message': error_message
    }
    return render(request, 'auth/login.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # aqui o signal já vai criar o Usuario vinculado
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()

    return render(request, 'auth/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu da sua conta.")
    return redirect('index')















# Usuário altera os dados do seu perfil
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def meu_perfil(request):
    Usuario = request.user.usuario
    
    if request.method == 'POST':
        perfil_form = PerfilForm(request.POST, instance=Usuario)
        usuario_form = UsuarioForm(request.POST, instance=request.user)
        senha_form = PasswordChangeForm(request.user, request.POST)
        
        if 'salvar_perfil' in request.POST:
            if perfil_form.is_valid() and usuario_form.is_valid():
                perfil_form.save()
                usuario_form.save()
                messages.success(request, "Perfil atualizado com sucesso!")
                return redirect('meu_perfil')
        
        elif 'alterar_senha' in request.POST:
            if senha_form.is_valid():
                user = senha_form.save()
                update_session_auth_hash(request, user)  # mantém logado
                messages.success(request, "Senha alterada com sucesso!")
                return redirect('meu_perfil')
            else:
                messages.error(request, "Corrija os erros no formulário de senha.")
    else:
        perfil_form = PerfilForm(instance=Usuario)
        usuario_form = UsuarioForm(instance=request.user)
        senha_form = PasswordChangeForm(request.user)
    
    context = {
        'perfil_form': perfil_form,
        'usuario_form': usuario_form,
        'senha_form': senha_form,
    }
    return render(request, 'perfil/meu_perfil.html', context)




















# Veículos
class CompararView(View):
    def get(self, request):
        carro1_id = request.GET.get('carro1')
        carro2_id = request.GET.get('carro2')
        
        carro1 = get_object_or_404(Carro, pk=carro1_id) if carro1_id else None
        carro2 = get_object_or_404(Carro, pk=carro2_id) if carro2_id else None
        
        return render(request, 'veiculo/comparar.html', {
            'carro1': carro1,
            'carro2': carro2
        })


class DetalhesView(View):
    # Exibe detalhes de um carro específico.
    def get(self, request, pk):
        carro = get_object_or_404(
            Carro.objects.prefetch_related('imagens'),
            pk=pk
        )
        return render(request, 'veiculo/detalhes.html', {'carro': carro})


def financiamento_calculo(request, carro_id):
    carro = get_object_or_404(Carro, pk=carro_id)
    
    if request.method == 'POST':
        # Processar o formulário de cálculo
        valor_entrada = float(request.POST.get('entrada', 0))
        parcelas = int(request.POST.get('parcelas', 12))
        
        # Cálculo simples (adaptar conforme sua lógica)
        valor_financiado = carro.valor - valor_entrada
        valor_parcela = valor_financiado / parcelas
        
        return render(request, 'financiamento.html', {
            'carro': carro,
            'valor_parcela': valor_parcela,
            'parcelas': parcelas
        })
    
    # GET request - mostrar formulário
    return render(request, 'financiamento.html', {
        'carro': carro,
        'default_parcelas': 12
    })












# Agendar test drive
@login_required
def agendar_test_drive(request, carro_id):
    carro = get_object_or_404(Carro, pk=carro_id)
    hoje = date.today()
    agora = datetime.now().time()

    month = int(request.GET.get('month', hoje.month))
    year = int(request.GET.get('year', hoje.year))

    max_date = hoje + timedelta(days=30)
    if month not in [hoje.month, max_date.month] or year not in [hoje.year, max_date.year]:
        month = hoje.month
        year = hoje.year

    selected_date_str = request.GET.get('data', hoje.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = hoje

    cal = monthcalendar(year, month)
    month_name = datetime(year, month, 1).strftime('%B').capitalize()

    calendario_completo = []
    for week in cal:
        semana = []
        for day in week:
            if day == 0:
                semana.append({'day': 0, 'date': None, 'is_past': False, 'is_weekend': False, 'is_available': False})
            else:
                dia_data = date(year, month, day)
                is_weekend = dia_data.weekday() >= 5
                semana.append({
                    'day': day,
                    'date': dia_data,
                    'is_past': dia_data < hoje,
                    'is_weekend': is_weekend,
                    'is_selected': dia_data == selected_date,
                    'is_available': dia_data >= hoje and not is_weekend
                })
        calendario_completo.append(semana)

    is_weekend_selected = selected_date.weekday() >= 5 if selected_date else False

    horarios_disponiveis = []
    if selected_date >= hoje and not is_weekend_selected:
        horarios_agendados = TestDrive.objects.filter(
            carro=carro,
            data=selected_date
        ).values_list('horario', flat=True)

        for hora in range(8, 18):
            horario = time(hora, 0)
            if (selected_date != hoje or horario > agora) and horario not in horarios_agendados:
                horarios_disponiveis.append(horario)

    show_popup = False
    qr_url = None

    if request.method == 'POST':
        try:
            data = datetime.strptime(request.POST.get('data'), '%Y-%m-%d').date()
            horario = datetime.strptime(request.POST.get('horario'), '%H:%M').time()

            if data < hoje or (data == hoje and horario < agora):
                messages.error(request, "Não é possível agendar no passado")
            elif data.weekday() >= 5:
                messages.error(request, "Só é possível agendar de segunda a sexta")
            elif TestDrive.objects.filter(carro=carro, data=data, horario=horario).exists():
                messages.warning(request, "Horário já reservado")
            else:
                agendamento = TestDrive.objects.create(
                    carro=carro,
                    data=data,
                    horario=horario,
                    usuario=request.user
                )
                # Dados para o QR code
                dados_qr = f"Agendamento: {agendamento.carro.marca} {agendamento.carro.modelo} - {agendamento.data} às {agendamento.horario} - Usuário: {request.user.username}"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={dados_qr}"

                messages.success(request, f"Test drive agendado com sucesso!")
                show_popup = True
        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")

    context = {
        'carro': carro,
        'hoje': hoje,
        'selected_date': selected_date,
        'is_weekend_selected': is_weekend_selected,
        'calendario_completo': calendario_completo,
        'horarios_disponiveis': horarios_disponiveis,
        'current_month': month,
        'current_year': year,
        'month_name': month_name,
        'show_prev': month > hoje.month or year > hoje.year,
        'show_next': (month < max_date.month and year <= max_date.year) or (year < max_date.year),
        'show_popup': show_popup,
        'qr_url': qr_url
    }
    return render(request, 'agendamento/agendar_test_drive.html', context)




# Usuário consegue ver os agendamentos que fez
@login_required
def meus_agendamentos(request):
    hoje = date.today()
    amanha = hoje + timedelta(days=1)

    # buscar apenas os agendamentos do usuário logado
    agendamentos = TestDrive.objects.filter(usuario=request.user).order_by('data', 'horario')

    # cancelar agendamento (POST)
    if request.method == 'POST':
        agendamento_id = request.POST.get('agendamento_id')
        agendamento = get_object_or_404(TestDrive, id=agendamento_id, usuario=request.user)
        
        if agendamento.data >= amanha:  # só pode cancelar até 1 dia antes
            agendamento.delete()
            messages.success(request, "Agendamento cancelado com sucesso.")
        else:
            messages.error(request, "Este agendamento não pode mais ser cancelado.")
        return redirect('meus_agendamentos')

    return render(request, 'agendamento/meus_agendamentos.html', {
        'agendamentos': agendamentos,
        'hoje': hoje,
        'amanha': amanha,
    })









# Reciclagem
class ReciclagemView(View):
    def get(self, request):
        return render(request, 'reciclagem.html')
    










# Consultar FIPE
class ConsultarFIPEView(View):
    def get(self, request):
        return render(request, 'consultarfipe.html')
    










# CHAT
class AssistenteView(View):
    perguntas = [
        {"id": 1, "campo": "marca", "texto": "Você tem alguma marca favorita? (Chevrolet, Ford, Fiat, Toyota, etc.)"},
        {"id": 2, "campo": "tipo", "texto": "Prefere SUV, hatch, sedã, picape ou tanto faz?"},
        {"id": 3, "campo": "cambio", "texto": "Câmbio automático, manual ou tanto faz?"},
        {"id": 4, "campo": "combustivel", "texto": "Gasolina, álcool, flex, diesel ou híbrido?"},
        {"id": 5, "campo": "cor", "texto": "Qual cor você prefere? Preto, branco, prata, vermelho...?"},
        {"id": 6, "campo": "ano", "texto": "Quer um carro mais novo (2019+), mais antigo ou tanto faz?"},
        {"id": 7, "campo": "km", "texto": "Prefere até 50 mil km, até 100 mil km, mais rodado, ou tanto faz?"},
        {"id": 8, "campo": "valor", "texto": "Qual faixa de preço? Até 50 mil, 50 a 100 mil, acima de 100 mil ou tanto faz?"},
        {"id": 9, "campo": "uso", "texto": "Vai usar mais na cidade, na estrada ou em ambos?"},
        {"id": 10, "campo": "tamanho", "texto": "Prefere um carro mais compacto ou espaçoso?"},
        {"id": 11, "campo": "desempenho", "texto": "Prefere economia de combustível ou mais potência?"},
        {"id": 12, "campo": "tecnologia", "texto": "Quer um carro mais simples ou com bastante tecnologia (multimídia, câmera, etc.)?"},
        {"id": 13, "campo": "estilo", "texto": "Prefere um carro mais discreto ou mais chamativo?"},
        {"id": 14, "campo": "manutencao", "texto": "Prefere carros com manutenção mais barata ou tanto faz?"},
        {"id": 15, "campo": "preferencia_final", "texto": "Se tivesse que escolher só um ponto mais importante, seria preço, conforto ou desempenho?"},
    ]

    def get(self, request):
        primeira = self.perguntas[0]
        opcoes = self._get_opcoes(primeira["campo"])
        return JsonResponse({"id": primeira["id"], "pergunta": primeira["texto"], "opcoes": opcoes})

    def post(self, request):
        id = int(request.POST.get("id"))
        resposta = request.POST.get("resposta")

        request.session.setdefault("chat_respostas", {})
        respostas = request.session["chat_respostas"]
        respostas[self.perguntas[id-1]["campo"]] = resposta
        request.session.modified = True

        if id < len(self.perguntas):
            prox = self.perguntas[id]
            opcoes = self._get_opcoes(prox["campo"])
            return JsonResponse({"id": prox["id"], "pergunta": prox["texto"], "opcoes": opcoes})

        carro = self._achar_mais_proximo(respostas)
        return JsonResponse({"final": True, "carro": carro})

    def _get_opcoes(self, campo):
        predefinidas = {
            "marca": ["Chevrolet", "Ford", "Fiat", "Toyota", "Honda", "Volkswagen", "Renault", "Hyundai", "Tanto faz"],
            "tipo": ["SUV", "Hatch", "Sedã", "Picape", "Tanto faz"],
            "cambio": ["Automático", "Manual", "Tanto faz"],
            "combustivel": ["Gasolina", "Álcool", "Flex", "Diesel", "Híbrido", "Tanto faz"],
            "cor": ["Preto", "Branco", "Prata", "Vermelho", "Azul", "Cinza", "Tanto faz"],
            "ano": ["Mais novos (2019+)", "Mais antigos", "Tanto faz"],
            "km": ["Até 50 mil km", "50 a 100 mil km", "Mais de 100 mil km", "Tanto faz"],
            "valor": ["Até 50 mil", "50 a 100 mil", "Acima de 100 mil", "Tanto faz"],
            "uso": ["Cidade", "Estrada", "Ambos"],
            "tamanho": ["Compacto", "Espaçoso"],
            "desempenho": ["Econômico", "Potente"],
            "tecnologia": ["Simples", "Tecnológico"],
            "estilo": ["Discreto", "Chamativo"],
            "manutencao": ["Barata", "Tanto faz"],
            "preferencia_final": ["Preço", "Conforto", "Desempenho"],
        }
        return predefinidas.get(campo, ["Tanto faz"])

    def _achar_mais_proximo(self, respostas):
        carros = Carro.objects.filter(ativo=True)
        melhor_match = None
        melhor_pontuacao = -1

        for carro in carros:
            pontos = 0
            if respostas.get("marca") and respostas["marca"] != "Tanto faz" and carro.marca == respostas["marca"]:
                pontos += 1
            if respostas.get("tipo") and respostas["tipo"] != "Tanto faz" and carro.tipo == respostas["tipo"]:
                pontos += 1
            if respostas.get("cambio") and respostas["cambio"] != "Tanto faz" and carro.cambio == respostas["cambio"]:
                pontos += 1
            if respostas.get("combustivel") and respostas["combustivel"] != "Tanto faz" and carro.combustivel == respostas["combustivel"]:
                pontos += 1
            if respostas.get("cor") and respostas["cor"] != "Tanto faz" and carro.cor == respostas["cor"]:
                pontos += 1

            # Ano
            if respostas.get("ano") == "Mais novos (2019+)" and carro.ano >= 2019:
                pontos += 1
            elif respostas.get("ano") == "Mais antigos" and carro.ano < 2019:
                pontos += 1

            # Km
            if respostas.get("km") == "Até 50 mil km" and carro.km <= 50000:
                pontos += 1
            elif respostas.get("km") == "50 a 100 mil km" and 50000 <= carro.km <= 100000:
                pontos += 1
            elif respostas.get("km") == "Mais de 100 mil km" and carro.km >= 100000:
                pontos += 1

            # Valor
            if respostas.get("valor") == "Até 50 mil" and carro.valor <= 50000:
                pontos += 1
            elif respostas.get("valor") == "50 a 100 mil" and 50000 <= carro.valor <= 100000:
                pontos += 1
            elif respostas.get("valor") == "Acima de 100 mil" and carro.valor >= 100000:
                pontos += 1

            # Demais campos a gente pode ir refinando depois
            if pontos > melhor_pontuacao:
                melhor_match = carro
                melhor_pontuacao = pontos

        if melhor_match:
            return {
                "nome": f"{melhor_match.marca} {melhor_match.modelo} {melhor_match.ano}",
                "valor": f"R$ {melhor_match.valor}",
                "url": f"/detalhes/{melhor_match.id}/",
                "pontos": melhor_pontuacao
            }
        return None




















# Páginas específicas para o funcionário e gerente
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.utils.dateparse import parse_date

# --- Função auxiliar para verificar se é funcionario e gerente ---
def is_funcionario(user):
    return (user.usuario.ocupacao and user.usuario.ocupacao == "funcionario") or (user.is_superuser and user.usuario.ocupacao == "gerente")













# Páginas específicas para o gerente

# --- Função auxiliar para verificar se é gerente ---
# or getattr(user, "usuario", None)
def is_gerente(user):
    return user.is_superuser and user.usuario.ocupacao == "gerente"


# View para criação

# View para criar funcionário
@login_required
@user_passes_test(is_gerente)
def criar_funcionario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        senha = request.POST.get("senha")
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        cpf = request.POST.get("cpf")
        data_admissao = request.POST.get("data_admissao")

        # Verificar se username já existe
        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse nome de usuário já existe.")
            return redirect("criar_funcionario")

        # Criar usuário base
        user = User.objects.create_user(username=username, password=senha)

        # Atualizar dados do modelo Usuario
        usuario = user.usuario  # criado pelo signal
        usuario.nome = nome
        usuario.telefone = telefone
        usuario.email = email
        usuario.ocupacao = "funcionario"
        usuario.cpf = cpf
        usuario.data_admissao = parse_date(data_admissao) if data_admissao else None
        usuario.save()

        messages.success(request, f"Funcionário {nome} cadastrado com sucesso!")
        return redirect("lista_funcionarios")

    return render(request, "paginasGerente/funcionarioCriar.html")




# View para criar veículo

import json
from decimal import Decimal, InvalidOperation
from django.db import transaction

@login_required
@user_passes_test(is_gerente)
def carro_criar(request):
    if request.method == 'POST':
        # ler campos
        marca = request.POST.get('marca', '').strip()
        modelo = request.POST.get('modelo', '').strip()
        ano_raw = request.POST.get('ano', '').strip()
        motor = request.POST.get('motor', '').strip()
        km_raw = request.POST.get('km', '0').strip()
        valor_raw = request.POST.get('valor', '').strip()
        tipo = request.POST.get('tipo', '').strip()
        cambio = request.POST.get('cambio', '').strip()
        combustivel = request.POST.get('combustivel', '').strip()
        cor = request.POST.get('cor', '').strip()
        consumo_cidade_raw = request.POST.get('consumo_cidade', '').strip() or '0'
        consumo_estrada_raw = request.POST.get('consumo_estrada', '').strip() or '0'
        ipva_pago = 'ipva_pago' in request.POST
        ativo = 'ativo' in request.POST

        # valida obrigatórios básicos
        if not (marca and modelo and ano_raw and motor and valor_raw and tipo and cambio and combustivel and cor):
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, 'paginasGerente/carroCriar.html')

        # Normalizadores simples para números que podem vir com '.' como separador de milhar e ',' como decimal
        def normalize_float_string(s):
            s = (s or '').strip()
            if not s:
                return s
            # caso tenha ambos, assumimos que '.' é milhares e ',' é decimal: "49.990,00" -> "49990.00"
            if '.' in s and ',' in s:
                s = s.replace('.', '').replace(',', '.')
            # caso tenha apenas vírgula, converte para ponto: "49,90" -> "49.90"
            elif ',' in s:
                s = s.replace(',', '.')
            # caso tenha apenas pontos (ex: "49990.00") deixamos como está
            return s

        # conversões seguras
        try:
            ano = int(ano_raw)
        except (ValueError, TypeError):
            messages.error(request, "Ano inválido.")
            return render(request, 'paginasGerente/carroCriar.html')

        try:
            # limpar possíveis separadores de milhar no km e converter
            km_clean = km_raw.replace('.', '').replace(',', '') if km_raw is not None else '0'
            km = int(km_clean) if km_clean != '' else 0
        except (ValueError, TypeError):
            messages.error(request, "Quilometragem inválida.")
            return render(request, 'paginasGerente/carroCriar.html')

        try:
            # normaliza valor (aceita "49.990,00", "49990.00", "49990,00", etc.)
            valor_norm = normalize_float_string(valor_raw)
            valor = Decimal(valor_norm)
        except (InvalidOperation, ValueError):
            messages.error(request, "Valor inválido.")
            return render(request, 'paginasGerente/carroCriar.html')

        try:
            consumo_cidade = Decimal(normalize_float_string(consumo_cidade_raw))
            consumo_estrada = Decimal(normalize_float_string(consumo_estrada_raw))
        except (InvalidOperation, ValueError):
            messages.error(request, "Consumo inválido.")
            return render(request, 'paginasGerente/carroCriar.html')

        # obter urls das imagens (form envia várias inputs com name="image_urls")
        image_urls = request.POST.getlist('image_urls')

        # criação atômica: carro + imagens
        try:
            with transaction.atomic():
                carro = Carro.objects.create(
                    marca=marca,
                    modelo=modelo,
                    ano=ano,
                    motor=motor,
                    valor=valor,
                    km=km,
                    tipo=tipo,
                    cambio=cambio,
                    combustivel=combustivel,
                    cor=cor,
                    consumo_cidade=consumo_cidade,
                    consumo_estrada=consumo_estrada,
                    ipva_pago=ipva_pago,
                    ativo=ativo
                )

                # criar imagens válidas (strip e ignorar vazios)
                for u in image_urls:
                    u = (u or '').strip()
                    if u:
                        ImagemCarro.objects.create(carro=carro, foto_url=u)

            messages.success(request, f"Carro {carro.marca} {carro.modelo} cadastrado com sucesso!")
            return redirect('listas')

        except Exception as e:
            # registrar/mostrar erro genérico (poderia logar também)
            messages.error(request, f"Erro ao criar carro: {str(e)}")
            return render(request, 'paginasGerente/carroCriar.html')

    # GET
    return render(request, 'paginasGerente/carroCriar.html')



# Listas
@login_required
@user_passes_test(is_gerente)
def listas_overview(request):
    # POST -> ações (reativar carro)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'reativar':
            carro_id = request.POST.get('carro_id')
            carro = get_object_or_404(Carro, pk=carro_id)
            carro.ativo = True
            carro.save()
            messages.success(request, f'Carro "{carro}" reativado com sucesso.')
            return redirect('listas')   # redirect evita re-submits no F5

    # GET -> mostra listas
    funcionarios = Usuario.objects.filter(ocupacao='funcionario').order_by('-data_admissao', 'nome')
    carros_inativos = Carro.objects.filter(ativo=False).order_by('-ano', 'marca', 'modelo')
    
    # Novo: Histórico de alterações com filtros
    historico_alteracoes = HistoricoAlteracaoCarro.objects.all().select_related('carro', 'usuario')
    
    # Aplicar filtros se existirem
    carro_id = request.GET.get('carro_id')
    usuario_id = request.GET.get('usuario_id')
    campo = request.GET.get('campo')
    
    if carro_id:
        historico_alteracoes = historico_alteracoes.filter(carro_id=carro_id)
    if usuario_id:
        historico_alteracoes = historico_alteracoes.filter(usuario_id=usuario_id)
    if campo:
        historico_alteracoes = historico_alteracoes.filter(campo_alterado=campo)
    
    # Ordenar por data mais recente primeiro
    historico_alteracoes = historico_alteracoes.order_by('-data_alteracao')
    
    # Dados para os filtros
    todos_carros = Carro.objects.all()
    todos_usuarios = User.objects.filter(historicoalteracaocarro__isnull=False).distinct()

    context = {
        'funcionarios': funcionarios,
        'carros_inativos': carros_inativos,
        'historico_alteracoes': historico_alteracoes,
        'todos_carros': todos_carros,
        'todos_usuarios': todos_usuarios,
    }
    return render(request, 'paginasGerente/listas.html', context)







# Registrar venda
from django.contrib import messages
@login_required
@user_passes_test(is_funcionario)
def salvar_venda(request):
    usuario = request.user.usuario  

    if request.method == "POST":
        carro_id = request.POST.get("carro")
        cliente_id = request.POST.get("cliente")

        # 🚨 Validação antes de tentar acessar o banco
        if not carro_id or not cliente_id:
            messages.error(request, "⚠️ Você deve selecionar um carro e um cliente antes de salvar a venda.")
            return redirect("salvar_venda")  # redireciona de volta ao formulário

        carro = get_object_or_404(Carro, pk=carro_id, ativo=True)
        cliente = get_object_or_404(Usuario, pk=cliente_id, ocupacao="cliente")

        valor_venda = carro.valor
        forma_pagamento = request.POST.get("forma_pagamento")
        parcelas = request.POST.get("parcelas") or None
        observacoes = request.POST.get("observacoes")

        venda = Venda.objects.create(
            carro=carro,
            vendedor=usuario,
            cliente=cliente,
            valor_venda=valor_venda,
            forma_pagamento=forma_pagamento,
            parcelas=parcelas,
            observacoes=observacoes,
        )

        if usuario.ocupacao in "gerente, funcionario":
            carro.ativo = False
            carro.save()

        messages.success(request, "✅ Venda registrada com sucesso!")
        return redirect("index")

    carros = Carro.objects.filter(ativo=True)
    clientes = Usuario.objects.filter(ocupacao="cliente")
    return render(request, "paginasGerente/salvarVenda.html", {
        "carros": carros,
        "clientes": clientes,
    })





@login_required
@user_passes_test(is_funcionario)
def editar_carro(request, pk):
    carro = get_object_or_404(Carro, pk=pk)
    
    if request.method == 'POST':
        # Coleta todos os dados do formulário
        marca = request.POST.get('marca', '').strip()
        modelo = request.POST.get('modelo', '').strip()
        ano_raw = request.POST.get('ano', '').strip()
        motor = request.POST.get('motor', '').strip()
        valor_raw = request.POST.get('valor', '').strip()
        km_raw = request.POST.get('km', '').strip()
        cambio = request.POST.get('cambio', '').strip()
        combustivel = request.POST.get('combustivel', '').strip()
        cor = request.POST.get('cor', '').strip()
        consumo_cidade_raw = request.POST.get('consumo_cidade', '').strip()
        consumo_estrada_raw = request.POST.get('consumo_estrada', '').strip()
        ipva_pago = request.POST.get('ipva_pago', 'False')
        
        # Lista para armazenar possíveis erros
        errors = []
        
        # Validação do valor
        valor_raw = valor_raw.replace(',', '.')
        try:
            valor = float(valor_raw) if valor_raw else 0.0
        except ValueError:
            errors.append("O valor deve ser numérico (use ponto ou vírgula).")
        
        # Validação do ano
        try:
            ano = int(ano_raw) if ano_raw else 0
        except ValueError:
            errors.append("O ano deve ser um número inteiro.")
        
        # Validação da quilometragem
        try:
            km = int(km_raw) if km_raw else 0
        except ValueError:
            errors.append("A quilometragem deve ser um número inteiro.")
        
        # Validação do consumo cidade
        consumo_cidade_raw = consumo_cidade_raw.replace(',', '.')
        try:
            consumo_cidade = float(consumo_cidade_raw) if consumo_cidade_raw else 0.0
        except ValueError:
            errors.append("O consumo na cidade deve ser numérico.")
        
        # Validação do consumo estrada
        consumo_estrada_raw = consumo_estrada_raw.replace(',', '.')
        try:
            consumo_estrada = float(consumo_estrada_raw) if consumo_estrada_raw else 0.0
        except ValueError:
            errors.append("O consumo na estrada deve ser numérico.")
        
        # Validação do IPVA pago
        ipva_pago_bool = ipva_pago.lower() == 'true'
        
        # Se houver erros, retorna com mensagens de erro
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'veiculo/editar_carro.html', {'carro': carro})
        
        # Lista para armazenar alterações
        alteracoes = []
        
        # Verifica e registra alterações para cada campo
        campos_para_verificar = [
            ('marca', marca, carro.marca),
            ('modelo', modelo, carro.modelo),
            ('ano', ano, carro.ano),
            ('motor', motor, carro.motor),
            ('valor', valor, float(carro.valor)),
            ('km', km, carro.km),
            ('cambio', cambio, carro.cambio),
            ('combustivel', combustivel, carro.combustivel),
            ('cor', cor, carro.cor),
            ('consumo_cidade', consumo_cidade, float(carro.consumo_cidade)),
            ('consumo_estrada', consumo_estrada, float(carro.consumo_estrada)),
            ('ipva_pago', ipva_pago_bool, carro.ipva_pago),
        ]
        
        for campo_nome, novo_valor, valor_atual in campos_para_verificar:
            if novo_valor != valor_atual:
                alteracoes.append({
                    'campo': campo_nome,
                    'antigo': str(valor_atual),
                    'novo': str(novo_valor)
                })
        
        # Atualiza todos os campos do carro
        carro.marca = marca
        carro.modelo = modelo
        carro.ano = ano
        carro.motor = motor
        carro.valor = valor
        carro.km = km
        carro.cambio = cambio
        carro.combustivel = combustivel
        carro.cor = cor
        carro.consumo_cidade = consumo_cidade
        carro.consumo_estrada = consumo_estrada
        carro.ipva_pago = ipva_pago_bool
        
        carro.save()
        
        # Salva o histórico de alterações
        if alteracoes and request.user.is_authenticated:
            for alteracao in alteracoes:
                HistoricoAlteracaoCarro.objects.create(
                    carro=carro,
                    usuario=request.user,
                    campo_alterado=alteracao['campo'],
                    valor_antigo=alteracao['antigo'],
                    valor_novo=alteracao['novo'],
                    ip_address=get_client_ip(request)
                )
        
        messages.success(request, f"O carro {carro.modelo} foi atualizado com sucesso!")
        if alteracoes:
            messages.info(request, f"Foram realizadas {len(alteracoes)} alteração(s) no carro.")
        
        return redirect('detalhes', pk=carro.pk)
    
    # Se não for POST, renderiza o formulário
    return render(request, 'veiculo/editar_carro.html', {'carro': carro})

def get_client_ip(request):
    """Função auxiliar para obter o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip





# EDITAR FUNCIONARIO
def editar_funcionario(request, pk):
    # Verifica se o usuário está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para acessar esta página.")
        return redirect('login')
    
    # Obtém o usuário a ser editado
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verifica se o usuário é um funcionário (funcionario ou gerente)
    if usuario.ocupacao not in ['funcionario', 'gerente']:
        messages.error(request, "Apenas funcionários podem ser editados nesta página.")
        return redirect('lista_funcionarios')  # Redireciona para lista de funcionários
    
    if request.method == 'POST':
        # Coleta todos os dados do formulário
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        ocupacao = request.POST.get('ocupacao', '').strip()
        kgs_borracha_doados_raw = request.POST.get('kgs_borracha_doados', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        data_admissao_raw = request.POST.get('data_admissao', '').strip()
        ativo = request.POST.get('ativo', 'False')
        username = request.POST.get('username', '').strip()
        
        # Lista para armazenar possíveis erros
        errors = []
        
        # Validação do kgs_borracha_doados
        kgs_borracha_doados_raw = kgs_borracha_doados_raw.replace(',', '.')
        try:
            kgs_borracha_doados = float(kgs_borracha_doados_raw) if kgs_borracha_doados_raw else 0.0
        except ValueError:
            errors.append("Os kgs de borracha doados devem ser numéricos (use ponto ou vírgula).")
        
        # Validação da data de admissão
        data_admissao = None
        if data_admissao_raw:
            try:
                data_admissao = datetime.strptime(data_admissao_raw, '%Y-%m-%d').date()
            except ValueError:
                errors.append("A data de admissão deve estar no formato YYYY-MM-DD.")
        
        # Validação do CPF (opcional, apenas se for preenchido)
        if cpf:
            # Verifica se CPF já existe em outro usuário
            cpf_existente = Usuario.objects.filter(cpf=cpf).exclude(pk=usuario.pk).exists()
            if cpf_existente:
                errors.append("Este CPF já está em uso por outro usuário.")
        
        # Validação do email
        if email and '@' not in email:
            errors.append("E-mail inválido.")
        
        # Validação do username (deve ser único)
        if username:
            user_exists = User.objects.filter(username=username).exclude(pk=usuario.user.pk).exists()
            if user_exists:
                errors.append("Este nome de usuário já está em uso.")
        
        # Validação do ativo
        ativo_bool = ativo.lower() == 'true'
        
        # Se houver erros, retorna com mensagens de erro
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'paginasGerente/editar_funcionario.html', {'usuario': usuario})
        
        # Lista para armazenar alterações
        alteracoes = []
        
        # Verifica e registra alterações para cada campo do Usuario
        campos_para_verificar = [
            ('nome', nome, usuario.nome),
            ('email', email, usuario.email or ''),
            ('telefone', telefone, usuario.telefone),
            ('ocupacao', ocupacao, usuario.ocupacao),
            ('kgs_borracha_doados', kgs_borracha_doados, float(usuario.kgs_borracha_doados)),
            ('cpf', cpf, usuario.cpf or ''),
            ('data_admissao', data_admissao, usuario.data_admissao),
            ('ativo', ativo_bool, usuario.ativo),
        ]
        
        for campo_nome, novo_valor, valor_atual in campos_para_verificar:
            if novo_valor != valor_atual:
                alteracoes.append({
                    'campo': campo_nome,
                    'antigo': str(valor_atual) if valor_atual is not None else '',
                    'novo': str(novo_valor) if novo_valor is not None else ''
                })
        
        # Verifica alterações no username do User relacionado
        if username and username != usuario.user.username:
            alteracoes.append({
                'campo': 'username',
                'antigo': usuario.user.username,
                'novo': username
            })
        
        # Atualiza os campos do Usuario
        usuario.nome = nome
        usuario.email = email if email else None
        usuario.telefone = telefone
        usuario.ocupacao = ocupacao
        usuario.kgs_borracha_doados = kgs_borracha_doados
        usuario.cpf = cpf if cpf else None
        usuario.data_admissao = data_admissao
        usuario.ativo = ativo_bool
        
        # Atualiza o username do User relacionado
        if username:
            usuario.user.username = username
            usuario.user.save()
        
        usuario.save()
        
        messages.success(request, f"O funcionário {usuario.nome} foi atualizado com sucesso!")
        if alteracoes:
            messages.info(request, f"Foram realizadas {len(alteracoes)} alteração(s) no funcionário.")
        
        return redirect('listas')
    
    # Se não for POST, renderiza o formulário
    return render(request, 'paginasGerente/editar_funcionario.html', {'usuario': usuario})




# EDITAR CLIENTE
def editar_cliente(request, pk):
    # Obtém o cliente a ser editado
    cliente = get_object_or_404(Usuario, pk=pk)
    
    # Verifica se o usuário é um cliente
    if cliente.ocupacao != 'cliente':
        messages.error(request, "Apenas clientes podem ser editados nesta página.")
        return redirect('lista_clientes')  # Ou para onde você redireciona
    
    if request.method == 'POST':
        # Coleta apenas os kgs de borracha doados
        kgs_borracha_doados_raw = request.POST.get('kgs_borracha_doados', '').strip()
        
        # Lista para armazenar possíveis erros
        errors = []
        
        # Validação do kgs_borracha_doados
        kgs_borracha_doados_raw = kgs_borracha_doados_raw.replace(',', '.')
        try:
            kgs_borracha_doados = float(kgs_borracha_doados_raw) if kgs_borracha_doados_raw else 0.0
        except ValueError:
            errors.append("Os kgs de borracha doados devem ser numéricos (use ponto ou vírgula).")
        
        # Se houver erros, retorna com mensagens de erro
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'paginasGerente/editar_cliente.html', {'cliente': cliente})
        
        # Verifica se houve alteração
        alteracoes = []
        if kgs_borracha_doados != float(cliente.kgs_borracha_doados):
            alteracoes.append({
                'campo': 'kgs_borracha_doados',
                'antigo': str(cliente.kgs_borracha_doados),
                'novo': str(kgs_borracha_doados)
            })
        
        # Atualiza apenas os kgs de borracha doados
        cliente.kgs_borracha_doados = kgs_borracha_doados
        cliente.save()
        
        messages.success(request, f"Os kgs de borracha doados do cliente {cliente.nome} foram atualizados com sucesso!")
        if alteracoes:
            messages.info(request, f"Valor alterado de {alteracoes[0]['antigo']}kg para {alteracoes[0]['novo']}kg.")
        
        return redirect('listas_overview')  # Ou para onde você redireciona
    
    # Se não for POST, renderiza o formulário
    return render(request, 'paginasGerente/editar_cliente.html', {'cliente': cliente})