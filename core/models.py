from django.db import models
from django.contrib.auth.models import PermissionsMixin, Group, Permission, BaseUserManager, AbstractBaseUser

# Manager personalizado
class UsuarioManager(BaseUserManager):
    def create_user(self, rut, password=None, **extra_fields):
        if not rut:
            raise ValueError("El RUT debe ser proporcionado")
        
        user = self.model(rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")
        
        return self.create_user(rut, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROL_CHOICES = [
        (1, 'Paciente'),
        (2, 'Terapeuta'),
        (3, 'Administrador'),
        (4, 'Cliente'),
    ]

    # Elimina el campo username sobrescribiéndolo
    username = None

    # Campos personalizados
    rut = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)
    email = models.EmailField(unique=True)
    rol = models.PositiveIntegerField(choices=ROL_CHOICES)
    institucion = models.ForeignKey('Institucion', on_delete=models.SET_NULL, null=True)

    # Campos necesarios para autenticación de Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    # Definir que el login será por el campo rut
    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['first_name', 'rol', 'email']  # Campos adicionales requeridos

    objects = UsuarioManager()

    def str(self):
        return f"{self.rut}"

    # Mapeo de grupos y permisos
    groups = models.ManyToManyField(
        Group,
        related_name='usuario_set',
        blank=True,
        help_text='Grupo al que pertenece el usuario.',
        verbose_name='grupos'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuario_set',
        blank=True,
        help_text='Permisos específicos del usuario.',
        verbose_name='permisos de usuario'
    )
    
class Institucion(models.Model):
    TIPO_CHOICES = [
        (1, 'Educativa'),
        (2, 'Institucion de salud'),
    ]
    nombre = models.CharField(max_length=100)
    tipo_institucion = models.PositiveIntegerField(choices=TIPO_CHOICES, default=2)
    direccion = models.ForeignKey('Direccion', on_delete=models.SET_NULL, null=True)
    contacto = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Direccion(models.Model):
    nombre_direccion = models.CharField(max_length=100)
    comuna = models.ForeignKey('Comuna', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_direccion


class Comuna(models.Model):
    nombre_comuna = models.CharField(max_length=100)
    ciudad = models.ForeignKey('Ciudad', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_comuna


class Ciudad(models.Model):
    nombre_ciudad = models.CharField(max_length=100)
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_ciudad


class Region(models.Model):
    nombre_region = models.CharField(max_length=100)
    pais = models.ForeignKey('Pais', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_region


class Pais(models.Model):
    nombre_pais = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_pais


class SesionTerapia(models.Model):
    RESULTADO_CHOICES = [
        (1, 'Completa'),
        (2, 'Interrumpida'),
    ]
    contenido = models.ForeignKey('ContenidoTerapia', on_delete=models.CASCADE)
    fecha_sesion = models.DateTimeField()
    duracion = models.PositiveIntegerField()  # en minutos
    resultado = models.PositiveIntegerField(choices=RESULTADO_CHOICES, default=0)
    usuario = models.ManyToManyField(Usuario, through='UsuarioSesion')

    def __str__(self):
        return f"Sesión de Terapia {self.fecha_sesion} - Duración: {self.duracion} mins"


class ContenidoTerapia(models.Model):
    titulo = models.CharField(max_length=100)
    url_contenido = models.URLField()
    descripcion = models.TextField()
    fecha_publicacion = models.DateField()

    def __str__(self):
        return self.titulo


class UsuarioSesion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    sesion = models.ForeignKey(SesionTerapia, on_delete=models.CASCADE)
    rol = models.PositiveIntegerField(choices=Usuario.ROL_CHOICES)

    def __str__(self):
        return f"Usuario {self.usuario} en {self.sesion}"


class SignosVitales(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    sesion = models.ForeignKey(SesionTerapia, on_delete=models.CASCADE)
    frecuencia_cardiaca = models.PositiveIntegerField()  # Pulsaciones por minuto
    fecha_medicion = models.DateTimeField()
    hora_medicion = models.TimeField()

    def __str__(self):
        return f"Signos Vitales de {self.usuario} - Frecuencia: {self.frecuencia_cardiaca} bpm"


class Suscripcion(models.Model):    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado_activo = models.BooleanField(default=True)  # True para activa, False para inactiva

    def __str__(self):
        return f"Suscripción de {self.usuario} - Estado: {'Activa' if self.estado_activo else 'Inactiva'}"


class Room(models.Model):
    terapeuta = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="rooms_as_terapeuta")
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="rooms_as_paciente")

    def __str__(self):
        return f"Sala: {self.nombre} | Terapeuta: {self.terapeuta.rut} - Paciente: {self.paciente.rut}"