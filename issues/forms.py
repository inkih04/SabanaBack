from django import forms
from .models import Issue
from .models import Status, Priorities, Types, Severities


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'description', 'status', 'assigned_to', 'issue_type', 'priority', 'severity']
        """widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'issue_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
        }"""

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class PrioritiesForm(forms.ModelForm):
    class Meta:
        model = Priorities
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class TypesForm(forms.ModelForm):
    class Meta:
        model = Types
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class SeveritiesForm(forms.ModelForm):
    class Meta:
        model = Severities
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
