from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import IssueForm
from .models import Issue


def issue_list(request):
    issues = Issue.objects.all().order_by('-created_at')  # Orden descendente
    return render(request, './issues/issues_list.html', {'issues': issues})


def issue_create(request):
    default_user = User.objects.first()  # Simulación de usuario logueado

    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)  # No guarda aún en la BD
            issue.assigned_to = default_user  # Asigna el usuario por defecto
            issue.save()  # Guarda la issue en la BD
            return redirect('issue_list')  # Redirige a la lista de issues
    else:
        form = IssueForm()  # Si no es POST, crea un formulario vacío

    return render(request, 'issues/issue_create.html', {'form': form})


def delete_issue(request, issue_id):
    issue = Issue.objects.get(id=issue_id)
    issue.delete()
    return redirect('issue_list')