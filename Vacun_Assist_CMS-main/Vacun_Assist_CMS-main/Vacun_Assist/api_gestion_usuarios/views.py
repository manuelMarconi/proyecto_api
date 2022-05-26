# Create your views here.
from email import message
import email
import re
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
            
            if len(us) > 0:
                #Si el mail ya esta registrado, error
                datos={'Error':'el email ya se encuentra registrado'}
                return JsonResponse(datos)
            
            #Validar que las contraseñas son iguales 
            if infForm['contraseña1'] != infForm['contraseña2']:
                datos={'Error':'las contraseñas no cohinciden'}
                return JsonResponse(datos)
            else:
                contra=infForm['contraseña1']
            #Validar el DNI con el renaper(pendiente..)
       
            #codigo_unico=random.randint(1000,9999) Esto esta mal, seria tener en la base de datos algo para ir chequeando esto
            
            #Guardar nuevo usuario en la base de datos
            
            Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=infForm['direccion'], email=infForm['email'], contraseña=infForm['contraseña1'], codigo='0000')
            #aca se crea un usuario de tipo User para que se guarde en la base de datos y luego poder autenticar de forma correcta
            user=User.objects.create_user(infForm['email'],infForm['email'],infForm['contraseña1'])
            user.save()
            #Envio de email
            mensaje="Se registro tu informacion en VacunAssist! Tu codigo para iniciar sesion es: 0000" #0000 es parcial
            send_mail('Registro exitoso',mensaje,'vacunassist.cms@gmail.com', [infForm['email']])
            
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
                #autenticate() devuelve un objeto de tipo User, por eso no accedia al if.
                #en la base de datos ademas de guardar un objeto de tipo Usuario, tambien guarda un objeto de tipo User para poder autenticar aca
                user=authenticate(username=username, password=password)
                if user is not None:  #aca es donde no entra
                    login(request, user)
                    return redirect('inicio')
                else:
                    return JsonResponse({'Error':'el usuario no se autentico correctamente'})
            else:
                return JsonResponse({'Error':'Usuario y/o contraseña incorrectos'})
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
