import re
from django.shortcuts import render, redirect
#from django.views.generic import View
from django.contrib.auth import login, logout, authenticate
#from django.contrib import messages
from gestion_usuarios.forms import FormularioAutenticacion, FormularioRegistro
from gestion_usuarios.models import Usuario
import random
from django.core.mail import send_mail



# Create your views here.

def inicio(request):
    return render(request, "gestion_usuarios/inicio.html")
    
def registro(request):
    if request.method=="POST":
        miFormulario=FormularioRegistro(request.POST)
    
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Validar si el mail no esta en la base de datos
            #Validar el DNI con el renaper
            #Validar que las contraseñas son iguales 


            us=Usuario.objects.filter(email=infForm['email'])
            if us.__len__ != 0:
                #Si el mail ya esta registrado, error
                pass


            if infForm['contraseña1'] != infForm['contraseña2']:
                pass
            else:
                contra=infForm['contraseña1']   

            #Esto guarda en la base de datos
            #codigo_unico=random.randint(1000,9999) Esto esta mal, seria tener en la base de datos algo para ir chequeando esto
            Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=infForm['direccion'], email=infForm['email'], contraseña=infForm['contraseña1'], codigo='codigo_unico')


            mensaje="Se registro tu informacion en VacunAssist! Tu codigo para iniciar sesion es: %s" %codigo_unico
            send_mail("Registro completo en VacunAssist", mensaje, 'vacunassist.cms@gmail.com', infForm['email'],)

            return redirect('inicio')
            

    else:
        miFormulario=FormularioRegistro()

    
    return render(request, "autenticacion/registro.html", {"form": miFormulario})



def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


def iniciar_sesion(request):
    #Entra una vez que aprieta el boton de enviar
    if request.method=="POST":
        miFormulario=FormularioAutenticacion(request.POST)
    
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios

            #Validar que este el mail en la base de datos
            #Validar contraseña
            #Validar codigo

            #Se podrian chequear todos los campos por separado
            us=Usuario.objects.filter(email=infForm['email'], contraseña=infForm['contraseña'], codigo=infForm['codigo'])
            if us.__len__ == 0:
                #No existen estos datos en la base de datos
                pass  

            """usuario=authenticate(username=infForm['email'], infForm['contraseña'])

            #Si existe el usuario
            if usuario is not None:
                login(request, usuario)
                return redirect('Home')"""
 

    else:
        #Si entra al else, seria el formulario vacio, para que llene los datos
        miFormulario=FormularioAutenticacion()

    
    return render(request, "autenticacion/login.html", {"form": miFormulario})


def cargar_info_covid(request):


    return render(request, "cargar_info/info_covid.html")

def cargar_info_fiebre_a(request):


    return render(request, "cargar_info/info_fiebre_a.html")

def cargar_info_gripe(request): 


    return render(request, "cargar_info/info_gripe.html")


def modificar_perfil(request):
    #No se puede cambiar todos los datos.
    #Seria reemplazar en la base de datos, los datos viejos con los datos nuevos
    return render(request, "gestion_usuarios/modificar_perfil.html")

def estatus_turno(request):
    #En el archivo html: si tiene elementos: recorrer la lista, y mostrar datos

    return render(request, "gestion_usuarios/estatus_turno.html")
