# issues/forms.py
from django import forms
from .models import Issue

class IssueForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(),  # Sin 'multiple'
        required=False
    )

    class Meta:
        model = Issue
        fields = ['subject', 'description', 'status', 'assigned_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].label = "Upload Attachment"
