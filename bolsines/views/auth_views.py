"""Login con legajo, logout y dashboard."""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..models import Empleado


def login_view(request: HttpRequest) -> HttpResponse:
    """Muestra el login y autentica al empleado por legajo + contraseña."""
    if request.user.is_authenticated:
        return redirect('seguimiento')

    error = None
    legajo = ''
    if request.method == 'POST':
        legajo = request.POST.get('legajo', '').strip()
        password = request.POST.get('password', '')
        empleado = Empleado.objects.select_related('user').filter(legajo=legajo, activo=True).first()
        # Se acepta el legajo; si no hay empleado con ese legajo, se prueba como username (p. ej. el admin).
        username = empleado.user.username if empleado else legajo
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or 'seguimiento')
        error = 'Legajo o contraseña incorrectos'

    return render(request, 'login.html', {'error': error, 'legajo': legajo})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Cierra la sesión y vuelve al login."""
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Inicio: accesos a las pantallas del sistema."""
    return render(request, 'dashboard.html', {'nav_activo': 'inicio'})
