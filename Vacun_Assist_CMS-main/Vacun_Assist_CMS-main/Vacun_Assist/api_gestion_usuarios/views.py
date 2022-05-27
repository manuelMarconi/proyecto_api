# Create your views here.
from cgitb import html
from email import message
import email
import re
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
#from django.views.generic import View
from django.contrib.auth import login, logout, authenticate
#from django.contrib import messages
from api_gestion_usuarios.forms import FormularioAutenticacion, FormularioRegistro
from api_gestion_usuarios.models import Usuario
import random
from django.core.mail import send_mail
from django.http.response import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def inicio(request):
    return render(request, "gestion_usuarios/inicio.html")

@method_decorator(csrf_exempt)    
def registro(request):
    if request.method=="POST":
        miFormulario=FormularioRegistro(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data
             
            #Validar si el mail no esta en la base de datos
            us=list(Usuario.objects.filter(email=infForm['email']))
            
            if len(us) > 0: #Si el mail ya esta registrado, error
                messages.add_message(request, messages.INFO, 'ERROR el email ya se encuentra registrado!')
                return render(request, "autenticacion/registro.html")
            #Validar que las contraseñas son iguales 
            if infForm['contraseña1'] != infForm['contraseña2'] and infForm['contraseña1']>7: #valido q sea mayor a 7
                messages.add_message(request, messages.INFO, 'ERROR contraseña incorrecta!')
                return render(request, "autenticacion/registro.html")

            #Validar el DNI con el renaper(pendiente..)
            #codigo_unico=random.randint(1000,9999) #Esto esta mal, seria tener en la base de datos algo para ir chequeando esto
    
            if  (infForm['dni'] == int(8)): #verifico que el dni tenga 8 digitos
                Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=infForm['direccion'], email=infForm['email'], contraseña=infForm['contraseña1'], codigo='0000')
                #aca se crea un usuario de tipo User para que se guarde en la base de datos y luego poder autenticar de forma correcta
                user=User.objects.create_user(infForm['email'],infForm['email'],infForm['contraseña1'])
                user.save()
                #Envio de email
                mensaje="Se registro tu informacion en VacunAssist! Tu codigo para iniciar sesion es: 0000" #0000 es parcial
                send_mail('Registro exitoso',mensaje,'vacunassist.cms@gmail.com', [infForm['email']])
                

            else:
                messages.add_message(request, messages.INFO, 'ERROR dni invalido!')
                return render(request, "autenticacion/registro.html")
            
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
            us=list(Usuario.objects.filter(email=infForm['email'], contraseña=infForm['contraseña'], codigo=infForm['codigo']))
            
            #utilice una lista(q siempre tiene long o 0 o 1) por que de la forma anterior no entraba al if correctamente, se puede cambiar para solo extraer un objeto.
            if len(us)>0:
                username=infForm['email']
                password=infForm['contraseña']
             
                user=authenticate(username=username, password=password)
                if user is not None:  
             
                    messages.add_message(request, messages.INFO, 'Inicio de sesion Exitoso')
                    login(request, user)
                    return redirect('inicio')
                else:
                    messages.add_message(request, messages.ERROR, 'ERROR el usuario no se encuentra autenticado') 
                    return render(request, "autenticacion/login.html")          
            else:
                messages.add_message(request, messages.ERROR, 'ERROR usuario y/o contrasenia y/o codigo incorrecto')
                return render(request, "autenticacion/login.html")
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
    if request.method=="POST":
        miFormulario=FormularioAutenticacion(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios

            #Validar que este el mail en la base de datos
            #Validar contraseña
            #Validar codigo

            us=list(Usuario.objects.filter(email=infForm['email']))
            
            if len(us)>0:  # NO ENTRA ACA
                username=infForm['email']
                password=infForm['contraseña']
                dni=infForm['dni']
                if  (dni != 8):
                    messages.add_message(request, messages.INFO, 'ERROR dni invalido!')
                    return render(request, "gestion_usuarios/modificar_perfil.html")

                Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=infForm['direccion'], email=infForm['email'], contraseña=infForm['contraseña1'], codigo='0000')
                return redirect('inicio')
            else:
                messages.add_message(request, messages.ERROR, 'ERROR gmail incorrecto')
                return render(request, "gestion_usuarios/modificar_perfil.html")
        else:
              #Si entra, seria el formulario vacio, para que llene los datos
            miFormulario=FormularioAutenticacion()

    return render(request, "gestion_usuarios/modificar_perfil.html")

def estatus_turno(request):
    #En el archivo html: si tiene elementos: recorrer la lista, y mostrar datos

    return render(request, "gestion_usuarios/estatus_turno.html")
