from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

# Vista para el login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página principal después de iniciar sesión
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')

# Vista para el registro de usuarios
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirige al login después de registrarse
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige a la página de login después de cerrar sesión

# Vista protegida que requiere estar logueado
@login_required
def home_view(request):
    funcionalidades = [
        {"nombre": "Agendar Cita", "descripcion": "Reserva una cita con un especialista."},
        {"nombre": "Ver Historial", "descripcion": "Accede a tu historial de citas y sesiones."},
        {"nombre": "Chat en Vivo", "descripcion": "Comunícate en tiempo real con un experto."},
    ]
    return render(request, 'accounts/home.html')

