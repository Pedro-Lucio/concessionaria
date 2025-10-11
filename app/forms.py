from django import forms
from django.core.exceptions import ValidationError
from .models import *
from django.utils import timezone

# Perfil extra vinculado ao User
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['telefone']
        labels = {
            'telefone': 'Telefone/Celular',
        }
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(99) 99999-9999'}),
        }


# Para o Usuário editar seus próprios dados básicos (User do Django)
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'exemplo@email.com'}),
        }


