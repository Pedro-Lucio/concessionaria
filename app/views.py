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
        carros = Carro.objects.all()
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
                "url": f"/carros/{melhor_match.id}/",
                "pontos": melhor_pontuacao
            }
        return None


















# Páginas específicas para o gerente

from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.utils.dateparse import parse_date

# --- Função auxiliar para verificar se é gerente ---
def is_gerente(user):
    return user.is_superuser or getattr(user, "usuario", None) and user.usuario.ocupacao == "gerente"


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


# Lista de funcionários
@method_decorator([login_required, user_passes_test(is_gerente)], name="dispatch")
class FuncionarioListView(ListView):
    model = Usuario
    template_name = 'paginasGerente/funcionarioLista.html'
    context_object_name = 'funcionarios'

    def get_queryset(self):
        return Usuario.objects.filter(ocupacao='funcionario')


# Detalhe de funcionário
@method_decorator([login_required, user_passes_test(is_gerente)], name="dispatch")
class FuncionarioDetailView(DetailView):
    model = Usuario
    template_name = 'paginasGerente/funcionarioDetalhado.html'
    context_object_name = 'funcionario'

    def get_queryset(self):
        return Usuario.objects.filter(ocupacao='funcionario')
