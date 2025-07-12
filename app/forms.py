from django import forms
from django.core.exceptions import ValidationError
from .models import AgendamentoTestDrive, Usuario
from django.utils import timezone

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']  # Campos editáveis
        # Adicione widgets se necessário
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

class AgendamentoTestDriveForm(forms.ModelForm):
    class Meta:
        model = AgendamentoTestDrive
        fields = ['carro', 'data_agendamento', 'observacoes']
        widgets = {
            'data_agendamento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_data_agendamento(self):
        data = self.cleaned_data.get('data_agendamento')
        if data and data < timezone.now():
            raise ValidationError("A data deve ser futura!")
        return data

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