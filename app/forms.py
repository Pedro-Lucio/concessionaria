from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario
from django.utils import timezone

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']  # Campos editáveis
        # Adicione widgets se necessário
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirme a senha")

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password2'):
            raise ValidationError("As senhas não coincidem!")
        return cleaned_data