from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from .models import Usuario  # Asegúrate de importar tu modelo Usuario

class CustomUserAdmin(UserAdmin):
    model = Usuario
    list_display = ['rut', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['rut', 'email', 'first_name', 'last_name']
    ordering = ['rut']
    list_filter = ['rol']

# Registra el modelo Usuario
admin.site.register(Usuario, CustomUserAdmin)

# Obtén todos los modelos de la aplicación actual, excluyendo Usuario
app_models = apps.get_models()

# Registra todos los modelos excepto Usuario
for model in app_models:
    if model != Usuario:  # Ignora el modelo Usuario
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass  # Ignora si el modelo ya está registrado
