"""proyecto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# proyecto/urls.py (el archivo de URL de tu proyecto)
from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view, register_view, home_view, logout_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('home/', home_view, name='home'),
    path('logout/', logout_view, name='logout'),  # Agregar esta línea
    path('ask-question/', home_view, name='ask_question'),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls')),
]
