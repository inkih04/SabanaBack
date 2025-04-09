from django import forms
from .models import Issue
from .models import Profile
from .models import Status, Priorities, Types, Severities

class IssueForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(),  # Sin 'multiple'
        required=False
    )

    class Meta:
        model = Issue
        fields = ['subject', 'description', 'status', 'assigned_to', 'issue_type', 'priority', 'severity', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        """widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'issue_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
        }"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].label = "Upload Attachment"


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

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']