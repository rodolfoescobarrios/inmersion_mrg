from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import json
from django.db.models import Count

from .models import (
    Usuario,
    Room,
    Institucion,
)

from .forms import (
    CustomUserCreationForm,
    FullInstitucionForm,
    LoginForm,
    UsuarioUpdateForm,
    BuscarUsuarioForm,
)
from .models import Usuario, Direccion

# Decorators to enforce role-based access
def role_required(role_id):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.rol != role_id:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator

paciente_required = role_required(1)
terapeuta_required = role_required(2)
admin_required = role_required(3)
cliente_required = role_required(4)

#--------------------------------------------------Vistas generales-------------------------------------
def home(request):
    return render(request, 'core/home.html')

@login_required
def exit(request):
    logout(request)
    return redirect("home")

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'registration/editarUsuario.html'
    success_url = reverse_lazy('home')


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request_user = self.request.user  # Usuario de la sesión actual
        usuario_actual = self.get_object()  # Usuario que se está editando
        form.rol_usuario = usuario_actual.rol

        # Agrega esto para depurar
        print("Usuario autenticado en la sesión:", self.request.user)
        print("Usuario que se está editando:", usuario_actual)

        return form


#---------------------------------Vistas específicas para el administrador---------------------------------

@login_required
@admin_required
def register(request):
    data = {'form': CustomUserCreationForm()}

    if request.method == "POST":
        user_creation_form = CustomUserCreationForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(
                username=user_creation_form.cleaned_data['rut'],
                password=user_creation_form.cleaned_data['password1']
            )
            login(request, user)
            return redirect("home")

    return render(request, 'registration/register.html', data)


@login_required
@admin_required
def institucion(request):
    if request.method == 'POST':
        full_form = FullInstitucionForm(request.POST)
        
        if full_form.is_valid():
            comuna = full_form.cleaned_data['comuna']
            direccion_texto = full_form.cleaned_data['direccion']
            
            direccion, created = Direccion.objects.get_or_create(
                nombre_direccion=direccion_texto,
                comuna=comuna
            )
            
            institucion = full_form.save(commit=False)
            institucion.direccion = direccion
            institucion.save()
            
            return redirect("institucion")
    else:
        full_form = FullInstitucionForm()
    
    return render(request, 'registration/institucion.html', {'form': full_form})
#----------------------------------------------------------------------------------------------------------------------

#------------------------------------Vistas compartidas entre administrador y cliente----------------------------------
@login_required
def buscarUsuario(request):
    if request.user.rol not in [3, 4, 2]:  # 3: Admin, 4: Cliente
        return redirect('error_page')  # Redirige si no es admin ni cliente

    form = BuscarUsuarioForm(request.POST or None)
    
    if form.is_valid():
        rut = form.cleaned_data['rut']
        usuario = Usuario.objects.filter(rut=rut).first()
        
        if usuario:
            return redirect('editarUsuario', pk=usuario.pk)
        else:
            form.add_error('rut', 'Usuario no encontrado.')
    
    return render(request, 'core/buscadorUsuario.html', {'form': form})
#----------------------------------------------------------------------------------------------------------------------

#---------------------------------------Vistas específicas para terapeutas---------------------------------------------
@login_required
@terapeuta_required
def listarPacientes(request):
    terapeuta = request.user
    if not isinstance(terapeuta, Usuario) or terapeuta.rol != 2:  # Verificar si es terapeuta
        return redirect('error_page')  # Redirigir a una página de error o inicio

    # Obtener la institución del terapeuta
    institucion_id = terapeuta.institucion.id

    # Filtrar pacientes de la misma institución
    pacientes = Usuario.objects.filter(institucion_id=institucion_id, rol=1)  # Asumiendo 1 es el rol de Paciente

    return render(request, 'terapeuta/listarPacientes.html', {'pacientes': pacientes})

def chatPaciente(request, paciente_id):
    paciente = get_object_or_404(Usuario, id=paciente_id, rol=1)  # rol=1 para "Paciente"
    
    # Intenta recuperar la sala, si no existe, créala
    sala, created = Room.objects.get_or_create(terapeuta=request.user, paciente=paciente)
    if created:
        print(f"Se creó una nueva sala con ID {sala.id}")
    else:
        print(f"Se recuperó una sala existente con ID {sala.id}") 
    context = {
        'sala': sala,
        'paciente': paciente,
        'room_id': sala.id,  # Pasamos la ID de la sala creada o encontrada
    }
    return render(request, "terapeuta/chatPaciente.html", context)

@login_required
@terapeuta_required
def metricasChat(request):
    return render(request, "terapeuta/metricasChat.html")

@login_required
@terapeuta_required
def fichaPaciente(request):
    return render(request, "terapeuta/fichaPaciente.html")
#----------------------------------------------------------------------------------------------------------------------

#------------------------------------------Vistas específicas para pacientes-------------------------------------------
@login_required
@paciente_required
def miChat(request):
    sala = Room.objects.filter(paciente=request.user).first()  # Filtrar la sala del paciente actual
    return render(request, "paciente/miChat.html", {'sala': sala, 'room_id': sala.id})
#----------------------------------------------------------------------------------------------------------------------


#-------------------------------------Metricas--------------------------------------------------------------------
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo admins pueden acceder
        if not request.user.is_staff:
            return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtén las métricas
        total_usuarios = Usuario.objects.count()
        usuarios_activos = Usuario.objects.filter(is_active=True).count()
        usuarios_inactivos = Usuario.objects.filter(is_active=False).count()
        total_instituciones = Institucion.objects.count()

        # Obtener el número de usuarios por institución y convertir a JSON
        usuarios_por_institucion = Usuario.objects.values(
            'institucion__nombre'
        ).annotate(
            num_usuarios=Count('institucion')
        ).order_by('-num_usuarios')
        
        # Convertir QuerySet a JSON para el gráfico
        usuarios_por_institucion_json = json.dumps(list(usuarios_por_institucion))

        # Crear el gráfico de usuarios activos e inactivos
        fig, ax = plt.subplots()
        ax.bar(['Activos', 'Inactivos'], [usuarios_activos, usuarios_inactivos], color=['green', 'red'])
        ax.set_title('Usuarios Activos e Inactivos')
        ax.set_xlabel('Estado')
        ax.set_ylabel('Cantidad')

        # Guardar la imagen en formato base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

        # Agregar todos los datos al contexto
        context.update({
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_inactivos': usuarios_inactivos,
            'total_instituciones': total_instituciones,
            'graph_img': graph_img,
            'usuarios_por_institucion_json': usuarios_por_institucion_json
        })

        return context
#----------------------------------------fin de las metricas -----------------------------------------------

