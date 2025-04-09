from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import IssueForm
from .models import Status, Priorities, Types, Severities
from .forms import StatusForm, PrioritiesForm, TypesForm, SeveritiesForm
from .forms import AvatarForm
from .models import Issue, Attachment
from .models import Profile
from .models import Comment

MODEL_FORM_MAP = {
    'status': (Status, StatusForm),
    'priorities': (Priorities, PrioritiesForm),
    'types': (Types, TypesForm),
    'severities': (Severities, SeveritiesForm),
}


@login_required
def issue_list(request):
    form = IssueForm()  # Instancia vacía del formulario
    User = get_user_model()
    users = User.objects.all()  # Lista de usuarios para "Assigned To" y "Created By"
    statuses = Status.objects.all()
    types = Types.objects.all()
    severities = Severities.objects.all()
    priorities = Priorities.objects.all()

    issues = Issue.objects.all()

    # Busqueda por texto
    search_query = request.GET.get('search', '').strip()
    if search_query:
        issues = issues.filter(
            Q(subject__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Filtros individuales
    if request.GET.get('issue_type'):
        issues = issues.filter(issue_type_id=request.GET.get('issue_type'))
    if request.GET.get('severity'):
        issues = issues.filter(severity_id=request.GET.get('severity'))
    if request.GET.get('priority'):
        issues = issues.filter(priority_id=request.GET.get('priority'))
    if request.GET.get('status'):
        issues = issues.filter(status_id=request.GET.get('status'))
    if request.GET.get('assigned_to'):
        issues = issues.filter(assigned_to_id=request.GET.get('assigned_to'))
    if request.GET.get('created_by'):
        issues = issues.filter(created_by_id=request.GET.get('created_by'))

    issues = issues.order_by('-created_at')

    return render(request, './issues/issues_list.html', {
        'issues': issues,
        'form': form,
        'users': users,
        'statuses': statuses,
        'types': types,
        'severities': severities,
        'priorities': priorities,
    })

@login_required
def issue_create(request):
    User = get_user_model()
    users = User.objects.all()

    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()  # Guarda el issue primero para obtener un ID

            # Procesar el archivo adjunto recibido del formulario (solo uno)
            if 'attachments' in request.FILES:
                file = request.FILES['attachments']
                Attachment.objects.create(issue=issue, file=file)

            return redirect('issue_list')

    return redirect('issue_list')





@login_required
def issue_detail(request, issue_id):
    """ Muestra los detalles de un issue específico """
    issue = get_object_or_404(Issue, id=issue_id)

    # Si estás mostrando el pop-up para asignar
    show_assign_form = request.GET.get("show_assign_form") == "1"
    search_query = request.GET.get("q", "")

    # Obtener todos los usuarios o filtrarlos por búsqueda
    users = Profile.objects.all()
    if search_query:
        users = users.filter(username__icontains=search_query)

    context = {
        'issue': issue,
        'show_assign_form': show_assign_form,
        'users': users,
    }

    return render(request, 'issues/issue_detail.html', context)


@login_required
def delete_issue(request, issue_id):
    issue = Issue.objects.get(id=issue_id)
    issue.delete()
    return redirect('issue_list')

@login_required
def update_issue_status(request, issue_id):
    """Actualiza el estado de un issue y redirige a la página de origen."""
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == "POST":
        new_status_id = request.POST.get("status")
        try:
            new_status = Status.objects.get(id=new_status_id)
            issue.status = new_status
            issue.save()
        except Status.DoesNotExist:
            pass  # Manejar el caso donde el estado no exista

    # Obtener la URL de retorno enviada en el formulario
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def update_issue_description(request, issue_id):
    """Actualiza la descripción de un issue y redirige a la página de origen."""
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == "POST":
        new_description = request.POST.get("description")
        if new_description:
            issue.description = new_description
            issue.save()

    # Ontener la URL de retorno enviada en el formaulario
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def add_comment_to_issue(request,issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == "POST":
        comment_text = request.POST.get("comment_text")
        if comment_text:
            comment = issue.comments.create(user=request.user, text=comment_text)
            comment.save()
    return redirect('issue_detail', issue_id=issue_id)

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
def update_issue_metadata(request, issue_id):
    """Actualiza tipo, prioridad y severidad de un issue"""
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == "POST":
        try:
            # Actualizar tipo
            new_type_id = request.POST.get("type")
            if new_type_id:
                new_type = Types.objects.get(id=new_type_id)
                issue.issue_type = new_type

            # Actualizar prioridad
            new_priority_id = request.POST.get("priority")
            if new_priority_id:
                new_priority = Priorities.objects.get(id=new_priority_id)
                issue.priority = new_priority

            # Actualizar severidad
            new_severity_id = request.POST.get("severity")
            if new_severity_id:
                new_severity = Severities.objects.get(id=new_severity_id)
                issue.severity = new_severity

            # Guardar cambios en el modelo Issue
            issue.save()

        except (Types.DoesNotExist, Priorities.DoesNotExist, Severities.DoesNotExist):
            pass  # Manejar errores si no se encuentran valores válidos

    return redirect('issue_list')


@login_required
def issue_bulk_create(request):
    if request.method == "POST":
        issues_text = request.POST.get("issues_text", "").strip()
        if issues_text:
            issues = [
                Issue(
                    subject=line.strip(),
                    description="Bulk created issue",
                    created_by=request.user  # Asigna el usuario creador
                )
                for line in issues_text.split("\n") if line.strip()
            ]
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

def profile(request):
    # Filtra los issues asignados al usuario logueado
    issues = Issue.objects.filter(assigned_to=request.user).order_by('-created_at')
    return render(request, 'BaseProfile.html', {'issues': issues, 'users':{request.user}})

@login_required
def update_bio(request):
    if request.method == 'POST':
        bio_text = request.POST.get('biography', '')
        profile = request.user.profile
        profile.biography = bio_text
        profile.save()
    return redirect('profile')

@login_required
def update_issue_info_title(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        newTitle = request.POST.get('subject')
        if newTitle:
            issue.subject = newTitle
            issue.save()
        return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_delete_comment(request, issue_id, comment_id):
    issue = get_object_or_404(Issue, id=issue_id)
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or issue.created_by == request.user:
        comment.delete()
    return redirect('issue_detail', issue_id=issue_id)


@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile = request.user.profile
        avatar_file = request.FILES['avatar']

        # Guarda en el campo avatar si tienes uno
        profile.avatar.save(avatar_file.name, avatar_file)
        profile.save()

    return redirect('profile')