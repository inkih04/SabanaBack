from django import forms
from .models import Issue

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'description', 'status', 'assigned_to', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
