from django.utils import timezone
from botocore.exceptions import ClientError
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from .forms import IssueForm
from .models import Status, Priorities, Types, Severities
from .forms import StatusForm, PrioritiesForm, TypesForm, SeveritiesForm
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
def issue_list(request, attachment_error=None):
    form = IssueForm()
    User = get_user_model()
    users = User.objects.all()
    statuses = Status.objects.all()
    types = Types.objects.all()
    severities = Severities.objects.all()
    priorities = Priorities.objects.all()

    issues = Issue.objects.all()

    search_query = request.GET.get('search', '').strip()
    if search_query:
        issues = issues.filter(
            Q(subject__icontains=search_query) | Q(description__icontains=search_query)
        )

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
        'attachment_error': attachment_error,  # 👉 Pasamos el error aquí
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
            issue.save()

            if 'attachments' in request.FILES:
                file = request.FILES['attachments']
                try:
                    Attachment.objects.create(issue=issue, file=file)
                except ClientError:
                    # En lugar de redirigir, renderiza issue_list con un error
                    return issue_list(request, attachment_error="The bucket is currently disabled. Please try again later.")

            return redirect('issue_list')

    return redirect('issue_list')




@login_required
def issue_detail(request, issue_id):
    """ Muestra los detalles de un issue específico """
    issue = get_object_or_404(Issue, id=issue_id)

    # Si estás mostrando el pop-up para asignar
    show_assign_form = request.GET.get("show_assign_form") == "1"
    search_query = request.GET.get("q", "")
    due_date_form = IssueForm(instance=issue)

    # Obtener la issue anterior ordenada por created_at
    prev_issue = Issue.objects.filter(created_at__lt=issue.created_at).order_by('-created_at').first()

    # Obtener la issue siguiente ordenada por created_at
    next_issue = Issue.objects.filter(created_at__gt=issue.created_at).order_by('created_at').first()

    # Obtener todos los usuarios o filtrarlos por búsqueda
    users = Profile.objects.all()
    statuses = Status.objects.all()
    severities = Severities.objects.all()
    priorities = Priorities.objects.all()
    types = Types.objects.all()
    today = timezone.now().date()


    if search_query:
        users = users.filter(username__icontains=search_query)

    attachments = Attachment.objects.filter(issue=issue)

    # Leer y eliminar el mensaje de error de la sesión si existe
    attachment_error = request.session.pop('attachment_error', None)

    context = {
        'issue': issue,
        'prev_issue': prev_issue,
        'next_issue': next_issue,
        'attachments': attachments,
        'show_assign_form': show_assign_form,
        'users': users,
        'statuses': statuses,
        'attachment_error': attachment_error,  # <-- Añadido aquí
        'due_date_form': due_date_form,
        'severities': severities,
        'priorities': priorities,
        'types': types,
        'today': today,
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


@login_required
def settings_list(request):
    """Muestra la lista de todas las configuraciones."""
    data = {
        'status': Status.objects.all(),
        'priorities': Priorities.objects.all(),
        'types': Types.objects.all(),
        'severities': Severities.objects.all(),
    }
    return render(request, 'settings/settings_list.html', {'data': data})

@login_required
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

@login_required
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


@login_required
def profile(request, username=None):
    # Si no se proporciona un username, mostrar el perfil del usuario actual
    if username is None:
        user = request.user
    else:
        # Obtener el usuario por nombre de usuario o devolver 404 si no existe
        User = get_user_model()
        user = get_object_or_404(User, username=username)

    # Ahora usamos el usuario determinado (user) en lugar de request.user
    assigned_issues = Issue.objects.filter(assigned_to=user).order_by('-created_at')
    total_issues = assigned_issues.count()

    watched_issues_qs = Issue.objects.filter(watchers=user).order_by('-created_at')
    watched_count = watched_issues_qs.count()

    user_comments = Comment.objects.filter(user=user).order_by('-published_at')
    comment_count = user_comments.count()

    view_mode = request.GET.get('view', 'issues')
    attachment_error = request.session.pop('attachment_error', None)

    if view_mode == "watched":
        issues_to_display = watched_issues_qs
    else:
        issues_to_display = assigned_issues

    all_statuses = Status.objects.all().order_by('nombre')

    # Variable para saber si es el perfil del usuario logueado o de otro usuario
    is_own_profile = user == request.user

    context = {
        'profile_user': user,  # Renombramos para evitar conflictos
        'issues': issues_to_display,
        'user_comments': user_comments,
        'total_issues': total_issues,
        'watched_issues': watched_count,
        'comment_count': comment_count,
        'users': {user},
        'view_mode': view_mode,
        'attachment_error': attachment_error,
        'statuses': all_statuses,
        'is_own_profile': is_own_profile,  # Indica si es el perfil propio o no
    }
    return render(request, 'BaseProfile.html', context)




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
def info_issue_upload_attachment(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == 'POST' and request.FILES:
        file = request.FILES.get('file')
        if file:
            try:
                Attachment.objects.create(issue=issue, file=file)
            except ClientError:
                request.session['attachment_error'] = "The bucket is currently disabled. Please try again later."
            except Exception:
                request.session['attachment_error'] = "An unexpected error occurred while uploading the file."

    return redirect('issue_detail', issue_id=issue.id)

@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile = request.user.profile
        avatar_file = request.FILES['avatar']
        try:
            profile.avatar.save(avatar_file.name, avatar_file)
            profile.save()
        except Exception:
            # Guardar en la sesión el mensaje de error para luego mostrarlo en el template
            request.session['attachment_error'] = "The bucket is currently disabled. Please try again later."
    return redirect('profile')


@login_required
def issue_info_delete_attachment(request, issue_id, attachment_id):
    issue = get_object_or_404(Issue, id=issue_id)
    attachment = get_object_or_404(Attachment, id=attachment_id)
    if attachment.issue == issue or issue.created_by == request.user:
        attachment.delete()
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_add_watcher(request,issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.user not in issue.watchers.all():
        issue.watchers.add(request.user)
    return redirect('issue_detail', issue_id=issue_id)


@login_required
def issue_info_remove_watcher(request, issue_id, ):
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, id=user_id)
            issue.watchers.remove(user)
    return redirect('issue_detail', issue_id=issue_id)
@login_required
def issue_info_add_multiple_watchers(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        selected_profile_ids = request.POST.getlist('users') # users es el name del select en el html
        for profile_id in selected_profile_ids:
            profile = get_object_or_404(Profile, pk=profile_id)
            issue.watchers.add(profile.user) # Añadimos el User asociado al Profile
        return redirect('issue_detail', issue_id=issue_id)
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_add_assigned_user(request,issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        selected_profile_ids = request.POST.getlist('users')
        if selected_profile_ids:  # Verifica si se seleccionó al menos un usuario
            profile_id = selected_profile_ids[0]  # Toma el primer usuario seleccionado
            profile = get_object_or_404(Profile, pk=profile_id)
            issue.assigned_to = profile.user  # Asigna el usuario a la issue
            issue.save()
        return redirect('issue_detail', issue_id=issue_id)
    return redirect('issue_detail',issue_id=issue_id)

@login_required
def issue_info_assign_to_current_user(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == "POST":
        issue.assigned_to = request.user
        issue.save()
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_remove_assigned(request,issue_id):
    issue = get_object_or_404(Issue,id=issue_id)
    if request.method=="POST":
        issue.assigned_to = None
        issue.save()
    return redirect('issue_detail',issue_id=issue_id)

@login_required
@login_required
def issue_info_set_due_date(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        due_date_form = IssueForm(request.POST, instance=issue)
        if 'due_date' in request.POST and len(request.POST) == 2: #Verifica si solo se envía due_date y csrf
            if due_date_form['due_date'].errors:
                print(due_date_form.errors)
            else:
                issue.due_date = due_date_form.cleaned_data['due_date']
                issue.save()
        elif due_date_form.is_valid():
            issue.due_date = due_date_form.cleaned_data['due_date']
            issue.save()
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_remove_due_date(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    issue.due_date = None
    issue.save()
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_edit_comment(request, issue_id, comment_id):
    issue = get_object_or_404(Issue, id=issue_id)
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.text = request.POST.get('text')
        comment.save()
        return redirect('issue_detail', issue_id=issue_id)
    return render(request, 'issues/issue_detail.html', {'issue': issue, 'edit_comment_id': comment_id})

@login_required
def issue_info_edit_properties(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        issue.severity = get_object_or_404(Severities, id=request.POST.get('severity'))
        issue.priority = get_object_or_404(Priorities, id=request.POST.get('priority'))
        issue.issue_type = get_object_or_404(Types, id=request.POST.get('issue_type'))
        issue.save()
        return redirect('issue_detail', issue_id=issue_id)
    return redirect('issue_detail', issue_id=issue_id)

@login_required
def issue_info_delete_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        issue.delete()
        return redirect('issue_list')
    return redirect('issue_detail', issue_id=issue_id)


@login_required
def user_directory(request):
    # Obtener todos los usuarios con sus perfiles
    User = get_user_model()
    users = User.objects.all()

    # Procesar la búsqueda si existe
    search_query = request.GET.get('search', '').strip()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(profile__biography__icontains=search_query)
        )

    # Lista para almacenar información de cada usuario
    user_data = []

    for user in users:
        # Contar issues asignados
        assigned_issues_count = Issue.objects.filter(assigned_to=user).count()

        # Contar issues observados
        watched_issues_count = Issue.objects.filter(watchers=user).count()

        # Contar comentarios
        comments_count = Comment.objects.filter(user=user).count()

        # Añadir toda la información a la lista
        user_data.append({
            'user': user,
            'assigned_issues_count': assigned_issues_count,
            'watched_issues_count': watched_issues_count,
            'comments_count': comments_count
        })

    return render(request, 'issues/user_directory.html', {
        'user_data': user_data,
        'search_query': search_query  # Pasar la consulta de búsqueda al template
    })