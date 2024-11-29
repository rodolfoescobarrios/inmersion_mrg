"""
URL configuration for inmersion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.urls import path
from django.contrib import admin
from core.views import (
    home, exit, register,
    institucion, CustomLoginView,
    UsuarioUpdateView, buscarUsuario,
    listarPacientes, chatPaciente, miChat,
    AdminDashboardView, metricasChat,
    fichaPaciente,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('logout/', exit, name="exit"),
    path("register/", register, name='register'),
    path("institucion/", institucion, name='institucion'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('usuario/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='editarUsuario'),
    path('buscadorUsuario/', buscarUsuario, name='buscadorUsuario'),
    path('pacientes/', listarPacientes, name='listarPacientes'),
    path('terapeuta/chat/<int:paciente_id>/', chatPaciente, name='chatPaciente'),
    path('paciente/chat/', miChat, name='miChat'),
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('terapeuta/metricasChat', metricasChat, name='metricasChat'),
    path('terapeuta/fichaPaciente', fichaPaciente, name='fichaPaciente'),
    
]
