from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import IssueForm
from .models import Issue
from .models import Status, Priorities, Types, Severities
from .forms import StatusForm, PrioritiesForm, TypesForm, SeveritiesForm

MODEL_FORM_MAP = {
    'status': (Status, StatusForm),
    'priorities': (Priorities, PrioritiesForm),
    'types': (Types, TypesForm),
    'severities': (Severities, SeveritiesForm),
}

@login_required
def issue_list(request):
    issues = Issue.objects.all().order_by('-created_at')
    form = IssueForm()  # Instancia vacía del formulario
    User = get_user_model()
    users = User.objects.all()  # Lista de usuarios para el campo "Assigned To"

    return render(request, './issues/issues_list.html', {'issues': issues, 'form': form, 'users': users})


@login_required
def issue_create(request):
    User = get_user_model()  # Obtiene el modelo de usuario
    users = User.objects.all()  # Obtiene todos los usuarios disponibles

    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)  # No guarda aún en la BD
            issue.save()  # Guarda la issue en la BD
            return redirect('issue_list')  # Redirige a la lista de issues
    else:
        form = IssueForm()  # Formulario vacío

    return render(request, 'issues/issue_create.html', {'form': form, 'users': users})

@login_required
def issue_detail(request, issue_id):
    """ Muestra los detalles de un issue específico """
    issue = get_object_or_404(Issue, id=issue_id)
    return render(request, 'issues/issue_detail.html', {'issue': issue})


@login_required
def delete_issue(request, issue_id):
    issue = Issue.objects.get(id=issue_id)
    issue.delete()
    return redirect('issue_list')

@login_required
def update_issue_status(request, issue_id):
    """ Actualiza el estado de un issue basado en la selección del usuario """
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Issue.STATUS_CHOICES):  # Verificar que el estado es válido
            issue.status = new_status
            issue.save()

    return redirect('issue_list')  # Redirige a la lista de issues


@login_required
def update_issue_assignee(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == 'POST':
        assigned_to_id = request.POST.get("assigned_to")
        if assigned_to_id:
            try:
                user = get_user_model().objects.get(id=assigned_to_id)
                issue.assigned_to = user
            except get_user_model().DoesNotExist:
                issue.assigned_to = None
        else:
            issue.assigned_to = None  # Desasignar si el valor está vacío

        issue.save()

    return redirect('issue_list')


@login_required
def issue_bulk_create(request):
    if request.method == "POST":
        issues_text = request.POST.get("issues_text", "").strip()
        if issues_text:
            issues = [Issue(subject=line.strip(), description="Bulk created issue")
                      for line in issues_text.split("\n") if line.strip()]
            Issue.objects.bulk_create(issues)
            return redirect('issue_list')
    return redirect('issue_list')  # Redirigir a la lista de issues


def login(request):
    return render(request, 'issues/custom_login.html')

def settings_list(request):
    """Muestra la lista de todas las configuraciones."""
    data = {
        'status': Status.objects.all(),
        'priorities': Priorities.objects.all(),
        'types': Types.objects.all(),
        'severities': Severities.objects.all(),
    }
    return render(request, 'settings/settings_list.html', {'data': data})


def settings_edit(request, model_name, pk=None):
    """Añade o edita un objeto de configuración."""
    model_data = MODEL_FORM_MAP.get(model_name)
    if not model_data:
        return redirect('settings_list')  # Redirige si el modelo no es válido

    model, form_class = model_data
    instance = get_object_or_404(model, pk=pk) if pk else None

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            # Generar automáticamente el slug si es necesario (solo para Status)
            if model_name == 'status' and not obj.slug:
                from django.utils.text import slugify
                obj.slug = slugify(obj.nombre)
            obj.save()
            return redirect('settings_list')
    else:
        form = form_class(instance=instance)

    return render(request, 'settings/settings_form.html', {'form': form})


def settings_delete(request, model_name, pk):
    """Elimina un objeto de configuración."""
    model_data = MODEL_FORM_MAP.get(model_name)  # Obtiene el modelo y formulario correspondiente
    if not model_data:
        return redirect('settings_list')  # Redirige si el modelo no es válido

    model, _ = model_data  # Solo necesitamos el modelo, no el formulario
    instance = get_object_or_404(model, pk=pk)  # Obtiene la instancia del objeto a eliminar

    if request.method == 'POST':
        instance.delete()  # Elimina el objeto de la base de datos
        return redirect('settings_list')  # Redirige a la lista de configuraciones

    return render(request, 'settings/settings_confirm_delete.html', {'instance': instance})