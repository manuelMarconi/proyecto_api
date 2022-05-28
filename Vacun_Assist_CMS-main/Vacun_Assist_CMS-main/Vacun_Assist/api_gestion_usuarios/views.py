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
from api_gestion_usuarios.forms import FormularioAutenticacion, FormularioRegistro, FormularioCovid, FormularioFiebreA, FormularioGripe
from api_gestion_usuarios.models import Codigos, Usuario, Turno
import random
from django.core.mail import send_mail
from django.http.response import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
import datetime

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
            
            
            if infForm['contraseña1'] != infForm['contraseña2'] and infForm['contraseña1']<8: #si es menor a 8tambien debe entrar al if
                messages.add_message(request, messages.INFO, 'ERROR contraseña incorrecta!')
                return render(request, "autenticacion/registro.html")
            
            
            if (len(infForm['dni'])==8): #verifico que el dni tenga 8 digitos, simulacion de renaper
                
                
                codAleatorio=generarCodigoAleatorio()
                Codigos.objects.create(codigo=codAleatorio)
                
                Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=infForm['direccion'], email=infForm['email'], contraseña=infForm['contraseña1'], codigo=codAleatorio)
                #aca se crea un usuario de tipo User para que se guarde en la base de datos y luego poder autenticar de forma correcta
                user=User.objects.create_user(infForm['email'],infForm['email'],infForm['contraseña1'])
                user.save()
                #Envio de email
                mensaje="Se registro tu informacion en VacunAssist! Tu codigo para iniciar sesion es: "+ str(codAleatorio)
                send_mail('Registro exitoso',mensaje,'vacunassist.cms@gmail.com', [infForm['email']])
                messages.add_message(request, messages.INFO, 'Registro Exitoso')
                login(request, user)
                return redirect('inicio')
            else:
                messages.add_message(request, messages.INFO, 'ERROR dni invalido!')
                return render(request, "autenticacion/registro.html")
        else:
            messages.add_message(request, messages.INFO, 'ERROR formulario invalido!')
            return render(request, "autenticacion/registro.html")    
          #  return redirect('inicio')
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

def generarCodigoAleatorio():
    aux=False
    while aux==False:
        codigo_unico=random.randint(1000,9999)
        usuario=list(Codigos.objects.filter(codigo=codigo_unico))
        if len(usuario)==0:
            aux=True
    return codigo_unico
        

def calcularEdad(fecha): 
    fecha_actual = datetime.datetime.today() 
    edad = fecha_actual.year - fecha.year - ((fecha_actual.month, fecha_actual.day) < (fecha.month, fecha.day)) 
  
    return edad 

def tieneTurno(request, vacuna_pedido):
    #Busco al dni del usuario de la sesion
    us=list(Usuario.objects.filter(id=request.user.id))
    dni=us[int(0)].dni


    #Busco en la lista turnos, los turnos que corresponden al usuario
    #Puede tener hasta tres turnos, o no tener ninguno
    turnos=list(Turno.objects.filter(usuario_a_vacunar=dni))

    tieneTurno=False
    #Si esta vacia la lista entonces no tiene ningun tierno
    if len(us) == 0:
        tieneTurno=False
    else:
        #Si tiene turnos, recorro la lista y busco el turno de "vacuna_pedido", puede ser coronavirus, gripe o fiebre amarilla
        for turno in turnos:
            if turno.vacuna == vacuna_pedido:
                return True

    return tieneTurno




def cargar_info_covid(request):

    if request.method=="POST":
        miFormulario=FormularioCovid(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que no tenga un turno previo
            tur=tieneTurno(request, 'Coronavirus')
            if tur == True:
                messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de coronavirus') 
                return redirect('inicio')
             
            #Busco la edad del usuario

            us=list(Usuario.objects.filter(id=request.user.id))


            fecha_nac=us[int(0)].fecha_nacimiento
            dni=us[int(0)].dni
            direc=us[int(0)].direccion
            usuario_edad=calcularEdad(fecha_nac)

            cantidad_dosis= int(infForm['cantidad_dosis'])
            paciente_riesgo= infForm['si_o_no']


            if cantidad_dosis == 2:
                messages.add_message(request, messages.ERROR, 'ERROR No puede recibir las vacunas porque tiene todas las dosis correspondientes') 
                #return render(request,"cargar_info/info_covid.html")
                return redirect('inicio')
                #Mensaje: No puede recibir las vacunas porque tiene todas las dosis correspondientes
            
            if usuario_edad < 18:
                messages.add_message(request, messages.ERROR, 'No se puede vacunar. Es menor de edad!') 
                return redirect('inicio')
            else:
                if usuario_edad < 60:

                    if paciente_riesgo == 'si':
                        #Menor de 60, con riesgo
                        #Asigno el turno
                        
                        dia_actual=datetime.datetime.now()
                        fecha_turno = datetime.date(dia_actual.year, dia_actual.month, (dia_actual.day + 1))

                        hora=random.randint(8,16)
                        #minutos=random.randint(00,50)
                        hora_turno= datetime.time(hora,30)



                        turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc)
                        turno.save()

                        messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                        return redirect('inicio')

                    else:
                        #Menor de 60, sin riesgo
                        #El turno lo asigna manualmente el administrador

                        #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna del coronavirus (El listado no es para esta demo)
                        messages.add_message(request, messages.INFO, 'Su pedido de vacuna ha sido procesado, se te enviara un mail proximamente con los datos de tu turno') 
                        return redirect('inicio')
                    
                
                else: 
                    #Mayor de 60
                    #Se asigna un turno

                    #fecha = datetime.date(2021, 7, 22)
                    #hora = datetime.time(21, 15)
                    #hora.isoformat() : '21:15:00'

                    dia_actual=datetime.datetime.now()
                    fecha_turno = datetime.date(dia_actual.year, dia_actual.month, (dia_actual.day + 1))

                    hora=random.randint(8,13)
                    #minutos=random.randint(00,50)
                    hora_turno= datetime.time(hora,20)


                    turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc)
                    turno.save()
                
                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                    return redirect('inicio')
            
      #  return render(request, "cargar_info/info_covid.html")
    else:
        miFormulario=FormularioCovid()
    return render(request, "cargar_info/info_covid.html", {"form": miFormulario})


def cargar_info_fiebre_a(request):

    if request.method=="POST":
        miFormulario=FormularioFiebreA(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que no tenga un turno previo
            tur=tieneTurno(request, 'Fiebre amarilla')
            if tur == True:
                messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de fiebre amarilla') 
                return redirect('inicio')
            #Busco la edad del usuario

            us=list(Usuario.objects.filter(id=request.user.id))


            fecha_nac=us[int(0)].fecha_nacimiento
            dni=us[int(0)].dni
            direc=us[int(0)].direccion
            usuario_edad=calcularEdad(fecha_nac)

            se_aplico=infForm['si_o_no']

      #      if infForm['fecha_aplicacion_fiebre_a'] is not None:
            if se_aplico == 'no':
                if usuario_edad < 60:
                    #Menor de 60
                    #El turno lo asigna el administrador, se manda un "pedido"
                    #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna de la fiebre amarilla(El listado no es para esta demo)

                    messages.add_message(request, messages.INFO, ' Su pedido de vacuna ha sido procesado, se te enviara un mail proximamente con los datos de tu turno!')
                    return redirect('inicio')
                else: 
                    #Mayor de 60
                    #No se puede vacunar 
                    messages.add_message(request, messages.INFO, ' Usted es mayor de 60. No se puede vacunar contra la Fiebre Amarilla!')
                    return redirect('inicio')
                
            else:
                messages.add_message(request, messages.INFO, ' Usted ya se aplico la dosis correspondiente de la vacuna de la Fiebre Amarilla')
                return redirect('inicio')


    else:
        miFormulario=FormularioFiebreA()
    return render(request, "cargar_info/info_fiebre_a.html", {"form": miFormulario})


def cargar_info_gripe(request): 

    if request.method=="POST":
        miFormulario=FormularioGripe(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que no tenga un turno previo
            tur=tieneTurno(request, 'Gripe')
            if tur == True:
                messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de la gripe') 
                return redirect('inicio')

            #Busco la edad del usuario

            
            us=list(Usuario.objects.filter(id=request.user.id))

            fecha_nac=us[int(0)].fecha_nacimiento
            dni=us[int(0)].dni
            direc=us[int(0)].direccion
            usuario_edad=calcularEdad(fecha_nac)

            # falta validar cuando paso menos de 12 meses y pide de nuevo la vacuna
            if infForm['fecha_aplicacion_gripe'] is not None: # que se verifica aca??
                if usuario_edad < 60:
                    #Menor de 60
                    #Asigno turno a 6 meses

                    dia_actual=datetime.datetime.now()
                    fecha_turno = datetime.date(dia_actual.year, (dia_actual.month+6), (dia_actual.day + 1))
                    
                    hora=random.randint(9,16)
                    #minutos=random.randint(00,50)
                    hora_turno= datetime.time(hora,00)

                    #Esto va a depender de los turnos disponibles, tendriamos que acceder a los turnos y buscar una fecha libre dependiendo de cada vacuna

                    turno=Turno(fecha=fecha_turno, hora= hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc)
                    turno.save()

                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                    return redirect('inicio')

                    #Asignar el turno al usuario
                    #Mensaje: Su turno ha sido reservado

                else: 
                    #Mayor de 60
                    #Asigno turno a 3 meses

                    dia_actual=datetime.datetime.now()
                    fecha_turno = datetime.date(dia_actual.year, (dia_actual.month+3), (dia_actual.day + 1))
                    
                    hora=random.randint(8,15)
                    #minutos=random.randint(00,50)
                    hora_turno= datetime.time(hora,15)

                    turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc)
                    turno.save()

                    #Asignar el turno al usuario

                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                    return redirect('inicio')
            else:
                messages.add_message(request, messages.INFO, 'Cargue el formulario') 
                return render(request,"cargar_info/info_gripe.html")  
        
        else:
            messages.add_message(request, messages.INFO, 'Formulario Invalido') 
            return render(request,"cargar_info/info_gripe.html")     
    else:
        miFormulario=FormularioGripe()
    return render(request, "cargar_info/info_gripe.html", {"form": miFormulario})



def modificar_perfil(request):
    if request.method=="POST":
        miFormulario=FormularioRegistro(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios

            #Validar que este el mail en la base de datos
            #Validar contraseña
            #Validar codigo

            us=list(Usuario.objects.filter(email=infForm['email']))
            if len(us)>0:  # NO ENTRA ACA
                usuario=us[0]
                usuario.email=infForm['email']
                usuario.contraseña=infForm['contraseña1']
                usuario.direccion=infForm['direccion']
                usuario.nombre=infForm['nombre']
                usuario.apellido=infForm['apellido']
                usuario.save()
                return redirect('inicio')
            else:
                messages.add_message(request, messages.ERROR, 'ERROR gmail incorrecto')
                return render(request, "gestion_usuarios/modificar_perfil.html")
        else:
              #Si entra, seria el formulario vacio, para que llene los datos
            miFormulario=FormularioAutenticacion()
            return JsonResponse({"Error": "no paso formulario"})
    return render(request, "gestion_usuarios/modificar_perfil.html")

def estatus_turno(request):
    #En el archivo html: si tiene elementos: recorrer la lista, y mostrar datos

    #Esto devuelve DNI del usuario
    us=list(Usuario.objects.filter(id=request.user.id))
    dni=us[int(0)].dni


    #Busco en la lista turnos, los turnos que corresponden al usuario
    #Puede tener hasta tres turnos, o no tener ninguno
    turnos=list(Turno.objects.filter(usuario_a_vacunar=dni))


    return render(request, "gestion_usuarios/estatus_turno.html", {"turnos": turnos, "usuario": us[int(0)]})
