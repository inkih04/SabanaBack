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

        # Modificar los campos de selección para tener un valor predeterminado más importante
        for field_name in ['status', 'issue_type', 'priority', 'severity']:
            field = self.fields[field_name]

            # Lógica específica para cada campo
            if field_name == 'status':
                # Buscar el status "New" y ponerlo al principio
                new_status = Status.objects.filter(nombre='New').first()
                if new_status:
                    # Obtener todos los status
                    statuses = list(Status.objects.all())
                    # Eliminar "New" de su posición actual
                    statuses.remove(new_status)
                    # Insertar "New" al principio
                    statuses.insert(0, new_status)
                    # Reconstruir las choices con "New" primero
                    field.choices = [(status.id, status.nombre) for status in statuses]

            elif field_name == 'issue_type':
                # Buscar el type "Bug" y ponerlo al principio
                bug_type = Types.objects.filter(nombre='Bug').first()
                if bug_type:
                    # Obtener todos los types
                    types = list(Types.objects.all())
                    # Eliminar "Bug" de su posición actual
                    types.remove(bug_type)
                    # Insertar "Bug" al principio
                    types.insert(0, bug_type)
                    # Reconstruir las choices con "Bug" primero
                    field.choices = [(t.id, t.nombre) for t in types]

            elif field_name == 'priority':
                # Buscar la prioridad "Medium" y ponerla al principio
                medium_priority = Priorities.objects.filter(nombre='Medium').first()
                if medium_priority:
                    # Obtener todas las prioridades
                    priorities = list(Priorities.objects.all())
                    # Eliminar "Medium" de su posición actual
                    priorities.remove(medium_priority)
                    # Insertar "Medium" al principio
                    priorities.insert(0, medium_priority)
                    # Reconstruir las choices con "Medium" primero
                    field.choices = [(p.id, p.nombre) for p in priorities]

            elif field_name == 'severity':
                # Buscar la severidad "Normal" y ponerla al principio
                normal_severity = Severities.objects.filter(nombre='Normal').first()
                if normal_severity:
                    # Obtener todas las severidades
                    severities = list(Severities.objects.all())
                    # Eliminar "Normal" de su posición actual
                    severities.remove(normal_severity)
                    # Insertar "Normal" al principio
                    severities.insert(0, normal_severity)
                    # Reconstruir las choices con "Normal" primero
                    field.choices = [(s.id, s.nombre) for s in severities]


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
            'color': forms.TextInput(attrs={
                'type': 'color',
                'style': 'font-size: 8px;'
            }),
        }

class TypesForm(forms.ModelForm):
    class Meta:
        model = Types
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={
                'type': 'color',
                'style': 'font-size: 8px;'
            }),
        }

class SeveritiesForm(forms.ModelForm):
    class Meta:
        model = Severities
        fields = ['nombre', 'color']
        widgets = {
            'color': forms.TextInput(attrs={
                'type': 'color',
                'style': 'font-size: 8px;'
            }),
        }

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
