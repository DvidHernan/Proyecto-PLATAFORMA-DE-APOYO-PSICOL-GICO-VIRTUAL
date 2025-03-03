from openai import OpenAI
import json
import time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings  # Para obtener la API Key
from django.http import JsonResponse
from .models import Conversation, Message, Cita
from django.utils import timezone
from datetime import datetime, timedelta

# Configuración de OpenAI
client = OpenAI(api_key = settings.OPENAI_API_KEY)



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
        {"nombre": "Agendar Cita", "descripcion": "Reserva una cita con un especialista.", "url": 'agendar_cita'},
        {"nombre": "Ver Historial", "descripcion": "Accede a tu historial de citas y sesiones.", "url": 'historial_citas'},
    ]
    assistant_id = "asst_ecntz87UkJE85BVqeeyjei7Z"
    user_name = request.user.username
    
    # Revisamos si ya existe un thread para la sesión actual
    if "thread_id" not in request.session:
        # No existe thread, así que creamos uno nuevo para la sesión actual
        thread = client.beta.threads.create()
        request.session["thread_id"] = thread.id
    else:
        thread_id = request.session["thread_id"]

    # También podemos guardar o relacionar este thread con una conversación en la base de datos
    conversation, created = Conversation.objects.get_or_create(user=request.user, defaults={'thread_id': request.session["thread_id"]})
    if not created and conversation.thread_id != request.session["thread_id"]:
        # Si la conversación ya existe pero el thread_id difiere (por ejemplo, por reinicio de sesión), actualizamos.
        conversation.thread_id = request.session["thread_id"]
        conversation.save()

        message = client.beta.threads.messages.create(
          thread_id=conversation.thread_id,
            role="user",
            content=f"Mi nombre es '{user_name}', llamame así"
        )
   
    assistant_response = None
    if request.method == 'POST' and 'question' in request.POST:
        question = request.POST['question']
        # Guardar el mensaje del usuario en la BD
        Message.objects.create(conversation=conversation, role="user", content=question, timestamp=timezone.now())
        # Recuperar los últimos 10 mensajes para el contexto
        last_messages = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:10]
        messages = [{"role": msg.role, "content": msg.content} for msg in reversed(last_messages)]
        


        message = client.beta.threads.messages.create(
          thread_id=conversation.thread_id,
            role="user",
            content=question
        )
        run = client.beta.threads.runs.create(
            thread_id = conversation.thread_id,
            assistant_id= assistant_id,
        )
        
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=conversation.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(1) 

        # Obtener la respuesta del asistente
        response_messages = client.beta.threads.messages.list(thread_id=conversation.thread_id)
        assistant_response = response_messages.data[0].content[0].text.value.strip()

        # Guardar la respuesta en la BD
        Message.objects.create(conversation=conversation, role="assistant", content=assistant_response, timestamp=timezone.now())

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Verifica si la solicitud es AJAX
            return JsonResponse({'assistant_response': assistant_response})  # Devuelve la respuesta en formato JSON

    return render(request, 'accounts/home.html', {
        'funcionalidades': funcionalidades,
        'assistant_response': assistant_response,
    })

    return redirect('home')  # Redirige a la página principal si no es POST

@login_required
def agendar_cita(request):
    horarios_disponibles = []
    today = timezone.now().date()
    
    # Permitir seleccionar fechas futuras
    if request.method == 'POST':
        fecha_str = request.POST['fecha']
        hora = request.POST['hora']
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        
        if fecha < today:
            return JsonResponse({'error': 'No puedes agendar una cita en el pasado.'})
        
        horario = f"{hora}:00"
        if Cita.objects.filter(fecha=fecha, hora=horario).exists():
            return JsonResponse({'error': 'Este horario ya está reservado.'})
        
        cita = Cita(usuario=request.user, fecha=fecha, hora=hora)
        cita.save()
        return redirect('home')  # Redirige al home después de agendar
    
    # Generamos los horarios disponibles de 9 am a 5 pm para la fecha seleccionada
    for hora in range(9, 17):
        horario = f"{hora}:00"
        if not Cita.objects.filter(fecha=today, hora=horario).exists():
            horarios_disponibles.append(horario)
    
    return render(request, 'accounts/agendar_cita.html', {'horarios_disponibles': horarios_disponibles, 'today': today})


@login_required
def historial_citas(request):
    citas = Cita.objects.filter(usuario=request.user).order_by('fecha', 'hora')
    return render(request, 'accounts/historial_citas.html', {'citas': citas})