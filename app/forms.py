from django import forms
from .models import AgendamentoTestDrive, Usuario  # Ajuste conforme seus modelos

class AgendamentoTestDriveForm(forms.ModelForm):
    class Meta:
        model = AgendamentoTestDrive
        fields = ['carro', 'data_agendamento', 'observacoes']  # Ajuste os campos

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone', 'senha']  # Ajuste conforme seu modelo Usuario

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']  # Campos editáveis