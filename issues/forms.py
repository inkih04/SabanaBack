from django import forms
from .models import Issue
from .models import Status, Priorities, Types, Severities


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'description', 'status', 'assigned_to']

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['nombre', 'color']  # Excluye 'slug' porque se genera automáticamente


class PrioritiesForm(forms.ModelForm):
    class Meta:
        model = Priorities
        fields = ['nombre', 'color']


class TypesForm(forms.ModelForm):
    class Meta:
        model = Types
        fields = ['nombre', 'color']


class SeveritiesForm(forms.ModelForm):
    class Meta:
        model = Severities
        fields = ['nombre', 'color']
