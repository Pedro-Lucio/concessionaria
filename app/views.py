from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from .models import *
from .forms import AgendamentoTestDriveForm, UserRegistrationForm, UserEditForm
from django.shortcuts import get_object_or_404

class FiltroView(View):
    def get(self, request):
        carros = Carro.objects.all()
        return render(request, 'veiculos/filtro.html', {'carros': carros})


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


class AgendarTestDriveView(LoginRequiredMixin, View):
    def get(self, request, carro_id):
        carro = Carro.objects.get(pk=carro_id)
        form = AgendamentoTestDriveForm(initial={'carro': carro, 'usuario': request.user})
        return render(request, 'agendamento/agendartestdrive.html', {'form': form, 'carro': carro})
    
    def post(self, request, carro_id):
        form = AgendamentoTestDriveForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.usuario = request.user
            agendamento.save()
            return redirect('agendamento_confirmado')
        return render(request, 'agendamento/agendartestdrive.html', {'form': form})


class AgendamentoConfirmadoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'agendamento/agendamentoconfirmado.html')


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


class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'auth/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'auth/register.html', {'form': form})


def custom_logout(request):
    logout(request)
    request.session.flush()  # Limpa completamente a sessão
    return redirect('home')


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