from django.urls import path
from .views import login_view, register_view, home_view, logout_view, agendar_cita, historial_citas

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('home/', home_view, name='home'),
    path('logout/', logout_view, name='logout'),  # Agregar esta línea
    path('ask-question/', home_view, name='ask_question'),
    path('agendar-cita/', agendar_cita, name='agendar_cita'),
    path('historial-citas/', historial_citas, name='historial_citas'),
]