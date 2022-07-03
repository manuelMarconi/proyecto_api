from unittest.util import _MAX_LENGTH
from django import forms

centros_vacunacion = (
    ("Zona municipalidad", "51 e/ 10  y 11 nro 770"),
    ("Zona cementerio", "138 e/ 73 y 74 nro 2035"),
    ("Zona terminal de omnibus", "3 e/ 41 y 42 nro 480"),
)
nombre_vacunacion = (
    ("Zona municipalidad", "municipalidad_00"),
    ("Zona cementerio", "cementerio_00"),
    ("Zona terminal de omnibus", "terminal_00"),
)
diccNombre ={
    "Zona municipalidad": "municipalidad_00",
    "Zona cementerio": "cementerio_00",
    "Zona terminal de omnibus": "terminal_00",
}


class FormularioRegistro(forms.Form):

    nombre=forms.CharField(max_length=30)
    apellido=forms.CharField(max_length=30)
    dni=forms.CharField(max_length=8)
    fecha_nacimiento=forms.DateField()
    #direccion=forms.CharField(max_length=30)
    direccion=forms.ChoiceField(choices = centros_vacunacion, widget=forms.widgets.Select())
    email=forms.EmailField()
    contraseña1=forms.CharField(max_length=30)
    contraseña2=forms.CharField(max_length=30)

class FormularioBuscarUsuario(forms.Form):
    dni=forms.CharField(max_length=8)

class FormularioBuscarVacunador(forms.Form):
    direccion=forms.ChoiceField(choices = centros_vacunacion, widget=forms.widgets.Select())

class FormularioModificar(forms.Form):

    nombre=forms.CharField(max_length=30)
    apellido=forms.CharField(max_length=30)
    direccion=forms.ChoiceField(choices = centros_vacunacion, widget=forms.widgets.Select())
    contraseña1=forms.CharField(max_length=30)
    contraseña2=forms.CharField(max_length=30)

class FormularioAutenticacion(forms.Form):
    email=forms.EmailField()
    contraseña=forms.CharField(max_length=30)
    codigo=forms.CharField(max_length=4)


class FormularioAutenticacionVacunador(forms.Form):
    email=forms.EmailField()
    contraseña=forms.CharField(max_length=30)


class FormularioCovid(forms.Form):
    #Cantidad de dosis aplicadas    
    cantidad_dosis=forms.IntegerField(max_value=2,min_value=0)
    si_o_no=forms.CharField(max_length=10)
#   fecha_primeradosis=forms.DateField(initial=forms.DateField.bound_data)
#    fecha_segundadosis=forms.DateField(initial=forms.DateField.bound_data)

class FormularioFiebreA(forms.Form):
    #En que año se aplico
    fecha_aplicacion_fiebre_a=forms.DateField()
    si_o_no=forms.CharField(max_length=10)


class FormularioGripe(forms.Form):
    #Fecha de la ultima aplicacion
    fecha_aplicacion_gripe=forms.DateField()
    si_o_no=forms.CharField(max_length=10)

class FormularioEstadoTurno(forms.Form):
    estado=forms.CharField(max_length=30)
    observaciones=forms.Textarea()

class FormularioEstadoTurnoAdmin(forms.Form):
    estado=forms.CharField(max_length=30)
    observaciones=forms.Textarea() 
    fecha_aplicacion=forms.DateField()

class FormularioRegistroVacunacion(forms.Form):
    nombre=forms.CharField(max_length=30)
    apellido=forms.CharField(max_length=30)
    dni=forms.CharField(max_length=8)
    fecha_nacimiento=forms.DateField()
    email=forms.EmailField()
    

class FormularioAgregarVacuna(forms.Form):
    vacuna=forms.CharField(max_length=40)
    nro_dosis=forms.CharField(max_length=10)
    observaciones=forms.Textarea()
    dni=forms.CharField(max_length=8)
    
class FormularioAutenticacionAdmin(forms.Form):
    email=forms.EmailField()
    contraseña=forms.CharField(max_length=30)

class FormularioNombreVacunador(forms.Form):
    direccion=forms.ChoiceField(choices = nombre_vacunacion, widget=forms.widgets.Select())
    nombre=forms.CharField(max_length=30) 
    nombre_actual=forms.CharField(max_length=30) 
#    nuevo_nombre=forms.CharField(max_length=30)

class FormularioVacunas(forms.Form):
    vacuna=forms.CharField(max_length=30)
    