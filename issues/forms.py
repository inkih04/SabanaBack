from django import forms
from .models import Issue
from .models import Profile

class IssueForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=forms.ClearableFileInput(),  # Sin 'multiple'
        required=False
    )

    class Meta:
        model = Issue
        fields = ['subject', 'description', 'status', 'assigned_to', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].label = "Upload Attachment"


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']