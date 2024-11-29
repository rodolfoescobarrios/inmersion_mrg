from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Usuario, Institucion, Direccion, Comuna, Ciudad, Region, Pais
from django.core.exceptions import ValidationError


#-----------------Formulario de login -----------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="RUT", max_length=12)
    password = forms.CharField(widget=forms.PasswordInput)
#----------------- fin del login----------------------


#-----------------buscador de usuarios ---------------------
class BuscarUsuarioForm(forms.Form):
    rut = forms.CharField(max_length=12, label='RUT')
#-----------------fin del buscador--------------------------

#---------------- formulario para editar usuario -------------------
class UsuarioUpdateForm(UserChangeForm):
    nueva_contrasena = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(),
        required=False
    )
    confirmacion_contrasena = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(),
        required=False
    )
    antigua_contrasena = forms.CharField(
        label="Contraseña Actual",
        widget=forms.PasswordInput(),
        required=True
    )
    inhabilitar_cuenta = forms.BooleanField(
        label="Inhabilitar cuenta",
        required=False,
        help_text="Desmarcar para inhabilitar la cuenta del usuario."
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'institucion', 'inhabilitar_cuenta', 'nueva_contrasena', 'confirmacion_contrasena', 'antigua_contrasena']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']  # Elimina el campo de contraseña si ya está incluido en UserChangeForm
        self.fields['inhabilitar_cuenta'].initial = not self.instance.is_active  # Establece el valor inicial del campo

        if self.instance.rol == 3:  
            if 'inhabilitar_cuenta' in self.fields:
                self.fields.pop('inhabilitar_cuenta')


    def clean(self):
        cleaned_data = super().clean()
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmacion_contrasena = cleaned_data.get('confirmacion_contrasena')
        antigua_contrasena = cleaned_data.get('antigua_contrasena')

        # Verifica si se proporcionó la contraseña actual
        if not antigua_contrasena:
            raise forms.ValidationError("Debe ingresar la contraseña actual para cambiarla.")

        # Verifica si la contraseña actual es correcta
        if not self.instance.check_password(antigua_contrasena):
            raise forms.ValidationError("La contraseña actual es incorrecta.")

        # Verifica si las nuevas contraseñas coinciden
        if nueva_contrasena and confirmacion_contrasena:
            if nueva_contrasena != confirmacion_contrasena:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        elif nueva_contrasena or confirmacion_contrasena:
            raise forms.ValidationError("Debe ingresar y confirmar la nueva contraseña.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        nueva_contrasena = self.cleaned_data.get('nueva_contrasena')
        inhabilitar_cuenta = self.cleaned_data.get('inhabilitar_cuenta')

        if nueva_contrasena:
            user.set_password(nueva_contrasena)  # Establece la nueva contraseña

        user.is_active = not inhabilitar_cuenta  # Actualiza el estado de la cuenta

        if commit:
            user.save()
        return user

#----------------- fin de la edicion ----------------------

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['rut', 'first_name', 'last_name', 'email', 'rol', 'institucion', 'password1', 'password2']

    def init(self, args, **kwargs):
        super(CustomUserCreationForm, self).init(args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Nombre'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Apellido'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Correo electrónico'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'})


    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not validar_rut(rut):  # Suponiendo que tienes una función validar_rut
            raise ValidationError("El RUT ingresado no es válido.")
        return rut

# ------------- formulario para las instituciones --------------
class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre_pais']

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['nombre_region']

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = ['nombre_ciudad', 'region']

class ComunaForm(forms.ModelForm):
    class Meta:
        model = Comuna
        fields = ['nombre_comuna', 'ciudad']

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre_direccion', 'comuna']

class CustomIntitucionCreationForm(forms.ModelForm):
     class Meta:
        model = Institucion
        fields = ['nombre', 'tipo_institucion', 'direccion', 'contacto']  # Incluye todos los campos que quieras que se puedan editar

# Formulario anidado que incluye todos los formularios necesarios
class FullInstitucionForm(forms.ModelForm):
    pais = forms.ModelChoiceField(queryset=Pais.objects.all(), required=True, label="Pais")
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=True, label="Región")
    ciudad = forms.ModelChoiceField(queryset=Ciudad.objects.all(), required=True, label="Ciudad")
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all(), required=True, label="Comuna")

    # Campo opcional para ingresar una dirección manual
    direccion = forms.CharField(max_length=255, required=False, label="O ingresa una nueva dirección", widget=forms.TextInput())

    class Meta:
        model = Institucion
        fields = ['nombre', 'tipo_institucion', 'contacto']

#--------------------- fin del formulario institucion --------------------------------


#--------------------------validador rut---------------------------------------
def validar_rut(rut):
    # Remover puntos, guiones y otros caracteres no numéricos
    rut = rut.replace(".", "").replace("-", "")
    
    # Verificar que el RUT tenga al menos 9 caracteres (número + dígito verificador)
    if len(rut) < 8:
        print("El RUT es demasiado corto.")
        return False

    # Separar el número del dígito verificador
    rut_numero = rut[:-1]  # Todo menos el último carácter (número)
    digito_verificador = rut[-1].upper()  # El último carácter (dígito)

    # Verificar que el número sea efectivamente un número
    try:
        rut_numero = int(rut_numero)
    except ValueError:
        return False

    # Cálculo del dígito verificador usando el algoritmo del Módulo 11
    multiplicador = 2
    suma = 0

    for numero in reversed(str(rut_numero)):
        suma += int(numero) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    # Obtener el dígito verificador esperado
    resto = 11 - (suma % 11)
    if resto == 11:
        digito_verificador_esperado = "0"
    elif resto == 10:
        digito_verificador_esperado = "K"
    else:
        digito_verificador_esperado = str(resto)

    # Comparar el dígito verificador calculado con el proporcionado
    return digito_verificador == digito_verificador_esperado
#------------------------ fin del validador--------------------------------------