# Padrão
from django.shortcuts import render, redirect
from .models import *
from django.views import View
from django.shortcuts import get_object_or_404
#
from django.contrib import messages
from .models import Carro, TestDrive
from datetime import datetime, date, time, timedelta
from calendar import monthcalendar, monthrange
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

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
    
    # Prepara os dias do calendário (todos visíveis)
    calendario_completo = []
    for week in cal:
        semana = []
        for day in week:
            if day == 0:
                semana.append({'day': 0, 'date': None, 'is_past': False, 'is_weekend': False, 'is_available': False})
            else:
                dia_data = date(year, month, day)
                is_weekend = dia_data.weekday() >= 5  # 5=sábado, 6=domingo
                semana.append({
                    'day': day,
                    'date': dia_data,
                    'is_past': dia_data < hoje,
                    'is_weekend': is_weekend,
                    'is_selected': dia_data == selected_date,
                    'is_available': dia_data >= hoje and not is_weekend
                })
        calendario_completo.append(semana)
    
    # Verifica se a data selecionada é fim de semana
    is_weekend_selected = selected_date.weekday() >= 5 if selected_date else False
    
    # Horários disponíveis (apenas para dias úteis futuros)
    horarios_disponiveis = []
    if selected_date >= hoje and not is_weekend_selected:
        horarios_agendados = TestDrive.objects.filter(
            carro=carro,
            data=selected_date
        ).values_list('horario', flat=True)
        
        for hora in range(8, 18):  # 8h às 17h
            horario = time(hora, 0)
            if (selected_date != hoje or horario > agora) and horario not in horarios_agendados:
                horarios_disponiveis.append(horario)
    
    # Processamento do POST
    if request.method == 'POST':
        try:
            data = datetime.strptime(request.POST.get('data'), '%Y-%m-%d').date()
            horario = datetime.strptime(request.POST.get('horario'), '%H:%M').time()
            
            if data < hoje or (data == hoje and horario < agora):
                messages.error(request, "Não é possível agendar no passado")
                return redirect('agendar_test_drive', carro_id=carro_id)
                
            if data.weekday() >= 5:  # Fim de semana
                messages.error(request, "Só é possível agendar de segunda a sexta")
                return redirect('agendar_test_drive', carro_id=carro_id)
                
            if TestDrive.objects.filter(carro=carro, data=data, horario=horario).exists():
                messages.warning(request, "Horário já reservado")
                return redirect('agendar_test_drive', carro_id=carro_id)
            
            TestDrive.objects.create(carro=carro, data=data, horario=horario)
            messages.success(request, f"Agendado para {data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}")
            return redirect('detalhes', pk=carro_id)
            
        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")
            return redirect('agendar_test_drive', carro_id=carro_id)
    
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
    }
    return render(request, 'agendar_test_drive.html', context)

# Enviar notificações ao usuário
from django.contrib import messages

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Formulários
from .forms import UserRegistrationForm, UserEditForm

# Para fazer com que o login seja necessário ao utilizar a View
from django.contrib.auth.decorators import login_required

# Utilizados nas views de login e logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class IndexView(View):
    def get(self, request):
        carros = Carro.objects.all()
        return render(request, 'index.html', {'carros': carros})


class CompararView(View):
    def get(self, request):
        # Lógica para comparar carros (poderia receber IDs via GET)
        carro1_id = request.GET.get('carro1')
        carro2_id = request.GET.get('carro2')
        
        carro1 = Carro.objects.get(pk=carro1_id) if carro1_id else None
        carro2 = Carro.objects.get(pk=carro2_id) if carro2_id else None
        
        return render(request, 'veiculos/comparar.html', {'carro1': carro1, 'carro2': carro2})


class DetalhesView(View):
    # Exibe detalhes de um carro específico.
    def get(self, request, pk):
        carro = get_object_or_404(
            Carro.objects.prefetch_related('imagens'),
            pk=pk
        )
        return render(request, 'veiculos/detalhes.html', {'carro': carro})


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


class PerfilView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'perfil/overview.html', {'user': request.user})


class EditarPerfilView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserEditForm(instance=request.user)
        return render(request, 'perfil/editarPerfil.html', {'form': form})
    
    def post(self, request):
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
        return render(request, 'perfil/editarPerfil.html', {'form': form})


class ReciclagemView(View):
    def get(self, request):
        return render(request, 'reciclagem.html')


class VendedorListView(ListView):
    model = Vendedor
    template_name = 'vendedores/lista.html'
    context_object_name = 'vendedores'  # Nome mais intuitivo para o template


class VendedorDetailView(DetailView):
    model = Vendedor
    template_name = 'vendedores/detalhado.html'
    context_object_name = 'vendedor'  # Nome mais claro no template







# Login e register do Auth
def RegisterView(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'auth/register.html', context)



def LoginView(request):
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



# class RegisterView(View):
#     def get(self, request):
#         form = UserRegistrationForm()
#         return render(request, 'auth/register.html', {'form': form})
    
#     def post(self, request):
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#         return render(request, 'auth/register.html', {'form': form})



@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, "Você saiu da sua conta.")
    return redirect('index')