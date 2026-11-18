from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'description', 'priority']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Тема заявки', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Опишите проблему подробно', 'rows': 4, 'class': 'form-input'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
        }
