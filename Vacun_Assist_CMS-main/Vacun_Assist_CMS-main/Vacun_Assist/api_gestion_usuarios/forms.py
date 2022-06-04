from unittest.util import _MAX_LENGTH
from django import forms

centros_vacunacion = (
    ("Zona municipalidad", "51 e/ 10  y 11 nro 770"),
    ("Zona cementerio", "138 e/ 73 y 74 nro 2035"),
    ("Zona terminal de omnibus", "3 e/ 41 y 42 nro 480"),
)

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


