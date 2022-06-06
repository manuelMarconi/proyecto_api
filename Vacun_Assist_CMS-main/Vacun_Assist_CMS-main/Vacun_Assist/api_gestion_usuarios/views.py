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
from api_gestion_usuarios.forms import FormularioAutenticacion, FormularioModificar, FormularioRegistro, FormularioCovid, FormularioFiebreA, FormularioGripe, FormularioAutenticacionVacunador, FormularioEstadoTurno
from api_gestion_usuarios.models import Codigos, Usuario, Turno, Vacunador, HistorialCovid, HistorialFiebreA, HistorialGripe
import random
from django.core.mail import send_mail
from django.http.response import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
import datetime

# prueba carla

# Create your views here.
def inicio(request):
    return render(request, "gestion_usuarios/inicio.html")

def inicio_vacunador(request):
    return render (request, "gestion_vacunador/inicio_vac.html")


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
                return render(request, "autenticacion/registro.html",{"form":miFormulario})

            
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
                return render(request, "autenticacion/registro.html",{"form":miFormulario})
        else:
            messages.add_message(request, messages.INFO, 'ERROR formulario invalido!')
            return render(request, "autenticacion/registro.html",{"form":miFormulario})    
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
                messages.add_message(request, messages.ERROR, 'ERROR usuario y/o contraseña y/o codigo incorrecto')
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

    tieneTurno=False
    #Comprobación innecesaria?? El usuario existe porque esta logueado
    if len(us) == 0:
        tieneTurno=False
    else:
        #Busco en la lista turnos, los turnos que corresponden al usuario
        #Puede tener hasta tres turnos, o no tener ninguno
        #Si tiene turnos, recorro la lista y busco el turno de "vacuna_pedido", puede ser coronavirus, gripe o fiebre amarilla
        dni=us[int(0)].dni
        turnos=list(Turno.objects.filter(usuario_a_vacunar=dni))
        for turno in turnos:
            if turno.vacuna == vacuna_pedido:
                return True

    return tieneTurno

def tiene_historial_covid(request):
    #Busco al dni del usuario de la sesion
    us=list(Usuario.objects.filter(id=request.user.id))
    dni=us[int(0)].dni

    #Busco en la lista HistorialCovid, el historial que corresponde al usuario
    historial=list(HistorialCovid.objects.filter(usuario=dni))

    tiene_historial_covid=False
    if len(historial) != 0:
        tiene_historial_covid=True

    return tiene_historial_covid

def tiene_historial_fiebre_a(request):
    #Busco al dni del usuario de la sesion
    us=list(Usuario.objects.filter(id=request.user.id))
    dni=us[int(0)].dni

    #Busco en la lista HistorialCovid, el historial que corresponde al usuario
    historial=list(HistorialFiebreA.objects.filter(usuario=dni))

    tiene_historial_fiebre_a=False
    if len(historial) != 0:
        tiene_historial_fiebre_a=True

    return tiene_historial_fiebre_a

def tiene_historial_gripe(request):
    #Busco al dni del usuario de la sesion
    us=list(Usuario.objects.filter(id=request.user.id))
    dni=us[int(0)].dni

    #Busco en la lista HistorialCovid, el historial que corresponde al usuario
    historial=list(HistorialGripe.objects.filter(usuario=dni))

    tiene_historial_gripe=False
    if len(historial) != 0:
        tiene_historial_gripe=True

    return tiene_historial_gripe

def cargar_info_covid(request):

    if request.method=="POST":
        miFormulario=FormularioCovid(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que no tenga un historial cargado
            his=tiene_historial_covid(request)
            if his == True:
                messages.add_message(request, messages.ERROR, 'Usted ya cargo su informacion para la vacuna del coronavirus') 
                return redirect('inicio')

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

            #Creo un historial de vacunación, guardo dni del usuario y la cantidad de dosis que ingreso
            historial=HistorialCovid(usuario=dni, cantidad_dosis=cantidad_dosis)
            historial.save()


            if cantidad_dosis == 2:
                messages.add_message(request, messages.ERROR, 'ERROR No puede recibir las vacunas porque tiene todas las dosis correspondientes') 
                return redirect('inicio')
            
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

                        turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado="Asignado")
                        turno.save()

                        messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                        return redirect('inicio')

                    else:
                        #Menor de 60, sin riesgo
                        #El turno lo asigna manualmente el administrador

                        #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna del coronavirus (El listado no es para esta demo)
                        turno=Turno(vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado="Pendiente")
                        turno.save()
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


                    turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado="Asignado")
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

            us=list(Usuario.objects.filter(id=request.user.id))
            dni=us[int(0)].dni


            if infForm['si_o_no'] == 'no':
                messages.add_message(request, messages.INFO, 'Su información ha sido guardada')
                return redirect('inicio')
                
            else:
                #Si puso que "si" y no subio una fecha, pide que la ingrese
                if infForm['fecha_aplicacion_fiebre_a'] is not None:
                    messages.add_message(request, messages.INFO, 'Cargue el formulario') 
                    return render(request,"cargar_info/info_fiebre_a.html") 

                #Si subio una fecha, ya se guarda en el historial
                #Solo es una aplicación de la vacuna
                historial=HistorialFiebreA(usuario=dni, fecha_aplicacion_fiebre_a= infForm['fecha_aplicacion_fiebre_a'])
                historial.save()

    else:
        miFormulario=FormularioFiebreA()
    return render(request, "cargar_info/info_fiebre_a.html", {"form": miFormulario})


def sacar_turno_fiebre_amarilla(request):
    if request.method=="POST":
        miFormulario=FormularioFiebreA(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que tenga un historial cargado
            his=tiene_historial_fiebre_a(request)
            if his == False:
                messages.add_message(request, messages.ERROR, 'Por favor, cargue la información correspondiente a la vacuna de la fiebre amarilla') 
                return redirect('inicio')

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


            if infForm['si_o_no'] == 'si':
                if usuario_edad < 60:
                    #Menor de 60
                    #El turno lo asigna el administrador, se manda un "pedido"
                    #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna de la fiebre amarilla(El listado no es para esta demo)

                    turno=Turno(vacuna='Fiebre amarilla', usuario_a_vacunar=dni, vacunatorio=direc, estado="Pendiente")
                    turno.save()
                    messages.add_message(request, messages.INFO, ' Su pedido de vacuna ha sido procesado, se te enviara un mail proximamente con los datos de tu turno!')
                    return redirect('inicio')
                else: 
                    #Mayor de 60
                    #No se puede vacunar 

                    messages.add_message(request, messages.INFO, ' Usted es mayor de 60. No se puede vacunar contra la Fiebre Amarilla!')
                    return redirect('inicio')
                
            else:
                #Si selecciono que 'no'
                return redirect('inicio')


    else:
        miFormulario=FormularioFiebreA()
    return render(request, "cargar_info/fiebre_a_turno.html", {"form": miFormulario})


def cargar_info_gripe(request): 

    if request.method=="POST":
        miFormulario=FormularioGripe(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que no tenga un historial cargado
            his=tiene_historial_gripe(request)
            if his == True:
                messages.add_message(request, messages.ERROR, 'Usted ya cargo su informacion para la vacuna de la gripe') 
                return redirect('inicio')


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
            if infForm['si_o_no'] == 'no': 
                if usuario_edad < 60:
                    #Menor de 60
                    #Asigno turno a 6 meses

                    dia_actual=datetime.datetime.now()
                    fecha_turno = datetime.date(dia_actual.year, (dia_actual.month+6), (dia_actual.day + 1))
                    
                    hora=random.randint(9,16)
                    #minutos=random.randint(00,50)
                    hora_turno= datetime.time(hora,00)

                    turno=Turno(fecha=fecha_turno, hora= hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado="Asignado")
                    turno.save()

                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                    return redirect('inicio')

                    #Asignar el turno al usuario

                else: 
                    #Mayor de 60
                    #Asigno turno a 3 meses

                    dia_actual=datetime.datetime.now()
                    fecha_turno = datetime.date(dia_actual.year, (dia_actual.month+3), (dia_actual.day + 1))
                    
                    hora=random.randint(8,15)
                    #minutos=random.randint(00,50)
                    hora_turno= datetime.time(hora,15)

                    turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado="Asignado")
                    turno.save()

                    #Asignar el turno al usuario

                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                    return redirect('inicio')
            else:
                #Si puso que "si", pide que ingrese una fecha
                if infForm['fecha_aplicacion_gripe'] is not None:
                    messages.add_message(request, messages.INFO, 'Cargue el formulario') 
                    return render(request,"cargar_info/info_gripe.html")  

                #Si subio una fecha, se guarda en el historial
                #ACA es donde tendriamos que agregar una validación de la fecha que se ingresa, si pasaron 12 meses se puede vacunar 
                historial=HistorialGripe(usuario=dni, fecha_aplicacion_gripe= infForm['fecha_aplicacion_gripe'])
                historial.save()
        
        else:
            messages.add_message(request, messages.INFO, 'Formulario Invalido') 
            return render(request,"cargar_info/info_gripe.html")     
    else:
        miFormulario=FormularioGripe()
    return render(request, "cargar_info/info_gripe.html", {"form": miFormulario})



def modificar_perfil(request):
    #aca extraemos el objeto Usuario que pertenezca al User con sesion iniciada
    
    usuarioModificar=list(Usuario.objects.filter(email=request.user.get_username()))
    usuarioModificar=usuarioModificar[0]
    
    #guardo los datos del usuario de forma 'key':valor, para luego ponerlos de valor predeterminado en el formulario(pendiente esto ultimo por no poder actualizar el form con estos valores)
    datos={"nombre":usuarioModificar.nombre, "apellido":usuarioModificar.apellido,"direccion":usuarioModificar.direccion, "contraseña1":usuarioModificar.contraseña,"contraseña2":usuarioModificar.contraseña}
    miFormulario=FormularioModificar(datos,auto_id=False)
    #en la variable miformulario, originalmente se encontrarian los datos del usuario, para cuando se haga el get se presenten. En caso de ser post el request, se cambia el miFormulario dentro del if
    if request.method=="POST":
        miFormularioNuevo=FormularioModificar(request.POST)
        if miFormularioNuevo.is_valid():
            infForm=miFormularioNuevo.cleaned_data #Aca se guarda toda la info que se lleno en los formularios
            #Validar igualdad de contraseñas
            if (infForm['contraseña1']==infForm['contraseña2']):
                
                #modificamos al User para no tener problemas en el inicio de sesion 
                
                user=User.objects.filter(username=usuarioModificar.email)
                user=user[0]
                user.set_password(infForm['contraseña1'])
                user.save()
                login(request,user)
                
                #modificamos al Usuario
                
                usuarioModificar.contraseña=infForm['contraseña1']
                usuarioModificar.direccion=infForm['direccion']
                usuarioModificar.nombre=infForm['nombre']
                usuarioModificar.apellido=infForm['apellido']
                usuarioModificar.save()
                messages.add_message(request, messages.SUCCESS, 'Usuario modificado correctamente')
                return redirect('inicio')
            else:
                #si las contraseñas no cohinciden salta mensaje de error
                print('las contraseñas no cohinciden') #esto puede mejorar esteticamente
                return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})
        else:
            #aca entra si el usuario deja celdas en blanco o inserta valores no validos
            print('valores de casilla no validos')#esto puede mejorar esteticamente
            
            return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})
    
    return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})
    
def estatus_turno(request):
    #En el archivo html: si tiene elementos: recorrer la lista, y mostrar datos

    #Esto devuelve ID del usuario
    us=list(Usuario.objects.filter(id=request.user.id))

    if len(us) == 0: #Esta comprobacion no sirve para nada, creo
        messages.add_message(request, messages.INFO, 'Usted no tiene turnos pendientes') 
        return redirect('inicio')
    else:
        dni=us[int(0)].dni
        usuario=us[int(0)]


        #Busco en la lista turnos, los turnos que corresponden al usuario
        #Puede tener hasta tres turnos, o no tener ninguno
        #Agregar comprobacion de estado, los que estan "Completo" o "Incompleto" no deberian aparecer aca. Se podria comprobar directamente en el html, creo
        turnos=list(Turno.objects.filter(usuario_a_vacunar=dni))


    return render(request, "gestion_usuarios/estatus_turno.html", {"turnos": turnos, "usuario": usuario})


def mi_perfil(request):
    #Esto muestra los datos del perfil del usuario:
    #Nombre, apellido, dni, email, fecha de nacimiento, vacunatorio

    #Esto devuelve ID del usuario
    us=list(Usuario.objects.filter(id=request.user.id))

    #Guardo el usuario en la variable
    usuario=us[int(0)]

    return render(request, "gestion_usuarios/mi_perfil.html", {"usuario": usuario})


def ver_historial(request):
    #Mostrar todos los historiales de vacunacion

    #Busco el dni
    us=list(Usuario.objects.filter(id=request.user.id))
    dni=us[int(0)].dni

    #Busco los 3 historiales
    his_covid=list(HistorialCovid.objects.filter(usuario=dni))
    his_fiebre_a=list(HistorialFiebreA.objects.filter(usuario=dni))
    his_gripe=list(HistorialGripe.objects.filter(usuario=dni))

    return render(request, "gestion_usuarios/historial.html", {"historial_covid": his_covid, "historial_fiebre_a": his_fiebre_a, "historial_gripe": his_gripe})
    
def iniciar_sesion_vacunador(request):
    if request.method=="POST":
        miFormulario=FormularioAutenticacionVacunador(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios

            #Se podrian chequear todos los campos por separado
            vac=list(Vacunador.objects.filter(email=infForm['email'], contraseña=infForm['contraseña']))
            
            #utilice una lista(q siempre tiene long o 0 o 1) por que de la forma anterior no entraba al if correctamente, se puede cambiar para solo extraer un objeto.
            if len(vac)>0:
                username=infForm['email']
                password=infForm['contraseña'] 
             
                user=authenticate(username=username, password=password)
                if user is not None:  
             
                    messages.add_message(request, messages.INFO, 'Inicio de sesion Exitoso')
                    login(request, user)
                    #return redirect('inicio_vacunador')
                    return render (request, "gestion_vacunador/inicio_vac.html")

                else:
                    messages.add_message(request, messages.ERROR, 'ERROR el usuario no se encuentra autenticado') 
                    return render(request, "autenticacion/login_vacunador.html")          
            else:
                messages.add_message(request, messages.ERROR, 'ERROR usuario y/o contraseña incorrecto')
                return render(request, "autenticacion/login_vacunador.html")
    else:
        #Si entra al else, seria el formulario vacio, para que llene los datos
        miFormulario=FormularioAutenticacionVacunador()

    
    return render(request, "autenticacion/login_vacunador.html", {"form": miFormulario})
    
def mi_perfil_vacunador(request):
    #Esto muestra los datos del perfil del vacunador:
    #Nombre, apellido, email, vacunatorio

    #Esto devuelve ID del vacunador
    #vac=list(Vacunador.objects.filter(id=request.user.id))
    #Lo hago con el mail, porque el ID del vacunador User y el vacunador Vacunador(tabla) no es el mismo
    vac=list(Vacunador.objects.filter(email=request.user.email))

    #Guardo el vacunador en la variable
    vacunador=vac[int(0)]

    return render(request, "gestion_vacunador/mi_perfil_vacunador.html", {"vacunador": vacunador})




def observar_turnos_dia(request):
    #Dia actual
    dia_actual=datetime.datetime.today()

    #Busco ID del vacunador logueado y asi guardo el vacunatorio
    #vac=list(Vacunador.objects.filter(id=request.user.id))
    #Lo hago con el mail, porque el ID del vacunador User y el vacunador Vacunador(tabla) no es el mismo
    vac=list(Vacunador.objects.filter(email=request.user.email))

    #Busco el vacunatorio del vacunador
    vacunatorio_actual=vac[int(0)].vacunatorio

    #Busco los turnos del vacunatorio y de la fecha actual
    turnos=list(Turno.objects.filter(fecha=dia_actual, vacunatorio=vacunatorio_actual))


    return render(request, "gestion_vacunador/turnos_del_dia.html", {"turnos": turnos})


def marcar_turno(request):

    if request.method=="POST":
        miFormulario=FormularioEstadoTurno(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios

            estado= infForm['estado']

            if estado == "completo":
                #actualizo el estado del turno a completo
                #Se agregan las "Observaciones" al turno, si es que hay
                #Como busco el turno? 
                pass
            else:
                #actualizo el estado del turno a incompleto
                #Se agregan las "Observaciones" al turno, si es que hay
                pass

            
    else:
        #Si entra al else, seria el formulario vacio, para que llene los datos
        miFormulario=FormularioEstadoTurno()

    
    return render(request, "gestion_vacunador/marcar_turno.html", {"form": miFormulario})


def agregar_persona(request):
    return render(request, "gestion_vacunador/agregar_persona.html")




