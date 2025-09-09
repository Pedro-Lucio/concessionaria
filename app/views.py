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

















# Lista de funcionários (usuários com ocupação = 'funcionario')
class FuncionarioListView(ListView):
    model = Usuario
    template_name = 'funcionario/lista.html'
    context_object_name = 'funcionarios'

    def get_queryset(self):
        return Usuario.objects.filter(ocupacao='funcionario')


# Detalhe de um funcionário específico
class FuncionarioDetailView(DetailView):
    model = Usuario
    template_name = 'funcionario/detalhado.html'
    context_object_name = 'funcionario'

    def get_queryset(self):
        return Usuario.objects.filter(ocupacao='funcionario')


# Gerente cria funcionário
@login_required
def criar_funcionario(request):
    if not request.user.is_superuser and request.user.usuario.ocupacao != "gerente":
        return redirect("home")  # só gerente pode criar funcionário

    if request.method == "POST":
        username = request.POST["username"]
        senha = request.POST["senha"]
        nome = request.POST["nome"]
        telefone = request.POST["telefone"]

        user = User.objects.create_user(username=username, password=senha)

        # o signal já criou um Usuario como cliente
        usuario = user.usuario
        usuario.nome = nome
        usuario.telefone = telefone
        usuario.ocupacao = "funcionario"
        usuario.save()

        return redirect("lista_funcionarios")

    return render(request, "usuarios/criar_funcionario.html")












# Veículos
class CompararView(View):
    def get(self, request):
        # Lógica para comparar carros (poderia receber IDs via GET)
        carro1_id = request.GET.get('carro1')
        carro2_id = request.GET.get('carro2')
        
        carro1 = Carro.objects.get(pk=carro1_id) if carro1_id else None
        carro2 = Carro.objects.get(pk=carro2_id) if carro2_id else None
        
        return render(request, 'veiculo/comparar.html', {'carro1': carro1, 'carro2': carro2})


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
    
    # Controle de navegação entre meses
    month = int(request.GET.get('month', hoje.month))
    year = int(request.GET.get('year', hoje.year))
    
    # Limita navegação ao mês atual e próximo
    max_date = hoje + timedelta(days=30)
    if month not in [hoje.month, max_date.month] or year not in [hoje.year, max_date.year]:
        month = hoje.month
        year = hoje.year
    
    # Data selecionada
    selected_date_str = request.GET.get('data', hoje.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = hoje
    
    # Configuração do calendário
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
    
    # Flag para mostrar popup
    show_popup = False

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
                TestDrive.objects.create(
                    carro=carro,
                    data=data,
                    horario=horario,
                    usuario=request.user
                )
                messages.success(request, f"Test drive agendado para {data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}")
                show_popup = True  # dispara o popup
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
        'show_popup': show_popup
    }
    return render(request, 'agendamento/agendar_test_drive.html', context)













# Reciclagem
class ReciclagemView(View):
    def get(self, request):
        return render(request, 'reciclagem.html')
    










# Consultar FIPE
class ConsultarFIPEView(View):
    def get(self, request):
        return render(request, 'consultarfipe.html')