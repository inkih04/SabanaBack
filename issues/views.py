from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import IssueForm
from .models import Issue

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
