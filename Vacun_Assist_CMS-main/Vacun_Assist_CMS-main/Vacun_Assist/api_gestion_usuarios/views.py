# Create your views here.
from cgi import MiniFieldStorage
from cgitb import html
from cmath import inf
from email import message
import email
from mmap import PAGESIZE
import re
from typing import ParamSpecArgs
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
#from django.views.generic import View
from django.contrib.auth import login, logout, authenticate
#from django.contrib import messages
from api_gestion_usuarios.forms import FormularioAutenticacion, FormularioModificar, FormularioModificarEstado, FormularioRegistro, FormularioCovid, FormularioFiebreA, FormularioGripe, FormularioAutenticacionVacunador, FormularioEstadoTurno, FormularioRegistroVacunacion, FormularioAutenticacionAdmin, FormularioAgregarVacuna, FormularioNombreVacunador, FormularioEstadoTurnoAdmin, FormularioBuscarUsuario, FormularioBuscarVacunador, FormularioVacunas
from api_gestion_usuarios.models import Codigos, Usuario, Turno, Vacunador, HistorialCovid, HistorialFiebreA, HistorialGripe, Administrador, NombreVacunador, Vacunatorio
import random
from django.core.mail import send_mail
from django.http.response import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date, datetime, timedelta, time

# Create your views here.


############
###DEMO 1###
############
 
def inicio(request):
    ##deberiamos usar un html para la pantalla principal y otro para el inicio del usuario
    if request.user.is_authenticated:
        us=list(Usuario.objects.filter(email=request.user.email))
        if len(us)>0:
            if(tieneTurno(request,"Fiebre amarilla")):
                return render(request, "gestion_usuarios/inicio.html",{"historial":tiene_historial_fiebre_a(request),"turno":1})
            return render(request, "gestion_usuarios/inicio.html",{"historial":tiene_historial_fiebre_a(request),"turno":0})
    return render(request, "gestion_usuarios/inicio.html")


def inicio_vacunador(request):
    if request.user.is_authenticated:
        return render (request, "gestion_vacunador/inicio_vac.html")
    return render(request, "gestion_usuarios/inicio.html")

def inicio_admin(request):
    if request.user.is_authenticated:
        return render (request, "gestion_admin/inicio_admin.html")
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
            

            #Si las contraseñas son distintas O la contraseña es menor a 6 digitos tiene que dar el error
            if infForm['contraseña1'] != infForm['contraseña2'] or len(infForm['contraseña1'])< int(6): #si es menor a 8tambien debe entrar al if
                messages.add_message(request, messages.INFO, 'ERROR contraseña incorrecta!')
                return render(request, "autenticacion/registro.html",{"form":miFormulario})

            
            if (len(infForm['dni'])==8): #verifico que el dni tenga 8 digitos, simulacion de renaper
                
                
                codAleatorio=generarCodigoAleatorio()
                Codigos.objects.create(codigo=codAleatorio)

                #Para guardar la fecha de registro
                dia_actual=datetime.now()
                fecha_reg=date(dia_actual.year, dia_actual.month, dia_actual.day)
                
                Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=infForm['direccion'], email=infForm['email'], contraseña=infForm['contraseña1'], codigo=codAleatorio, fecha_registro=fecha_reg)
                #aca se crea un usuario de tipo User para que se guarde en la base de datos y luego poder autenticar de forma correcta
                user=User.objects.create_user(infForm['email'],infForm['email'],infForm['contraseña1'])
                user.save()
                #Envio de email
                mensaje="Se registro tu informacion en VacunAssist! Tu codigo para iniciar sesion es: "+ str(codAleatorio)
                #send_mail('Registro exitoso',mensaje,'vacun.assist.cms@hotmail.com', [infForm['email']])
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
    fecha_actual = datetime.today() 
    edad = fecha_actual.year - fecha.year - ((fecha_actual.month, fecha_actual.day) < (fecha.month, fecha.day)) 
  
    return edad 

def tieneTurno(request, vacuna_pedido):

    #Busco al dni del usuario de la sesion
    us=list(Usuario.objects.filter(email=request.user.email))

    tieneTurno=False
    #Busco en la lista turnos, los turnos que corresponden al usuario
    #Puede tener hasta tres turnos, o no tener ninguno
    #Si tiene turnos, recorro la lista y busco el turno de "vacuna_pedido", puede ser coronavirus, gripe o fiebre amarilla
    dni=us[int(0)].dni
    turnos=list(Turno.objects.filter(usuario_a_vacunar=dni,vacuna=vacuna_pedido))
    if(len(turnos)>0):
        return True
    return False

def tiene_historial_covid(request):
    #Busco al dni del usuario de la sesion

    us=list(Usuario.objects.filter(email=request.user.email))

    dni=us[int(0)].dni

    #Busco en la lista HistorialCovid, el historial que corresponde al usuario
    historial=list(HistorialCovid.objects.filter(usuario=dni))

    tiene_historial_covid= -1
    if len(historial) != 0:
        cant = historial[int(0)].cantidad_dosis
        if cant == '1':
            tiene_historial_covid= 1
        else:
            if cant == '2':
                tiene_historial_covid= 2
            else: 
                tiene_historial_covid= 0

    return tiene_historial_covid

def tiene_historial_fiebre_a(request):
    #Busco al dni del usuario de la sesion
    us=list(Usuario.objects.filter(email=request.user.email))
    dni=us[int(0)].dni

    #Busco en la lista HistorialCovid, el historial que corresponde al usuario
    historial=list(HistorialFiebreA.objects.filter(usuario=dni))

    #Uso numeros en vez de un booleano porque hay 3 escenarios posibles:
    #Devuelve 0 si no subio nada
    #Devuelve 1 si subio, y marco que ya se vacuno. No puede pedir turno.
    #Devuelve 2 si subio, y marco que no se vacuno. Puede pedir turno
    tiene_historial_fiebre_a=0
    if len(historial) != 0:
        si_o_no=historial[int(0)].si_o_no
        if si_o_no == 'si':
            tiene_historial_fiebre_a=1
        else:
            tiene_historial_fiebre_a=2

    return tiene_historial_fiebre_a

def tiene_historial_gripe(request):
    #Busco al dni del usuario de la sesion
    
    us=list(Usuario.objects.filter(email=request.user.email))
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
        if (miFormulario.is_valid()):
            infForm = miFormulario.cleaned_data

            us=list(Usuario.objects.filter(email=request.user.email))
            dni=us[int(0)].dni
            #Chequeo historial 
            his=tiene_historial_covid(request)
            tur=tieneTurno(request,'Coronavirus') # estado="Asignado"           
            if tur == True:
                messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de Coronavirus') 
                return redirect('inicio')

            if ((his == 2 and infForm['cantidad_dosis']==1) or (his == 1 and infForm['cantidad_dosis']==0) or (his == 2 and infForm['cantidad_dosis']==0)):                    
                messages.add_message(request, messages.ERROR, 'No puede restar dosis') 
                return redirect('inicio')
            else:
                if his == infForm['cantidad_dosis']: #ingresa la misma cantidad que tenia
                    messages.add_message(request, messages.ERROR, 'Sin modificacion') 
                    return redirect('inicio')
            historial=list(HistorialCovid.objects.filter(usuario=dni))
             
            if (his == 0 and infForm['cantidad_dosis']==1):
                historial[int(0)].cantidad_dosis = '1'
                historial = historial[int(0)]
                historial.save()   
                messages.add_message(request, messages.INFO, 'Actualizacion correcta')
                return redirect('inicio') 
                
            if (his == 1 and infForm['cantidad_dosis']== 2):
                historial[int(0)].cantidad_dosis = '2'
                historial = historial[int(0)]
                historial.save()   
                messages.add_message(request, messages.INFO, 'Actualizacion correcta')
                return redirect('inicio') 
                    
            else:        
                fecha_nac=us[int(0)].fecha_nacimiento
                direc=us[int(0)].direccion
                nombre=us[int(0)].nombre
                apellido=us[int(0)].apellido
        
                usuario_edad=calcularEdad(fecha_nac) #Busco la edad del usuario
                cantidad_dosis= int(infForm['cantidad_dosis'])
                paciente_riesgo= infForm['si_o_no']
                    
                if usuario_edad < 18:
                    messages.add_message(request, messages.ERROR, 'No se puede vacunar. Es menor de edad!') 
                    return redirect('inicio')

                #Creo un historial de vacunación, guardo dni del usuario y la cantidad de dosis que ingreso

                historial=HistorialCovid(usuario=dni, cantidad_dosis=cantidad_dosis, nombre_usuario=nombre, apellido_usuario=apellido)
                historial.save()
                if cantidad_dosis == 2:
                    messages.add_message(request, messages.ERROR, 'ERROR No puede recibir mas vacunas de coronavirus porque tiene todas las dosis correspondientes') 
                    return redirect('inicio')

                #El usuario sube "x" dosis aplicadas
                #La dosis que se tiene que aplicar se guarda en la variable para guardarla en el turno (Para los listados)
                dosis_covid= cantidad_dosis +1
                    
                    
                if usuario_edad < 60:

                    if paciente_riesgo == 'si':
                        #Menor de 60, con riesgo
                                #Asigno el turno
                        dia_actual=datetime.now()
                        fecha_turno = datetime.date(dia_actual+timedelta(days=random.randint(1,7)))
                        hora=random.randint(8,16)
                        hora_turno=time(hour=hora,minute=30)
                        turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado',nombre_usuario=nombre, apellido_usuario=apellido, dosis=dosis_covid)
                        turno.save()                        
                        messages.add_message(request, messages.INFO, 'Su turno ha sido reservado. Puede seguirlo en Estatus de turno') 
                        return redirect('inicio')

                    else:
                                #Menor de 60, sin riesgo
                                #El turno lo asigna manualmente el administrador
                                #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna del coronavirus (El listado no es para esta demo)
                        turno=Turno(vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado='Pendiente', nombre_usuario=nombre, apellido_usuario=apellido, dosis=dosis_covid)
                        turno.save()
                        messages.add_message(request, messages.INFO, 'Su pedido de vacuna ha sido procesado, se te enviara un mail proximamente con los datos de tu turno') 
                        return redirect('inicio')
                else: 
                            #Mayor de 60
                            #Se asigna un turno

                            #fecha = datetime.date(2021, 7, 22)
                            #hora = datetime.time(21, 15)
                            #hora.isoformat() : '21:15:00'

                    dia_actual=datetime.now()
                    fecha_turno = datetime.date(dia_actual+timedelta(days=random.randint(1,7)))
                    hora=random.randint(8,16)
                    hora_turno=time(hour=hora,minute=30)
                    turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado', nombre_usuario=nombre, apellido_usuario=apellido, dosis=dosis_covid)                    
                    turno.save()

                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado. Puede seguirlo en Estatus de turno') 
                    return redirect('inicio')
                
      #  return render(request, "cargar_info/info_covid.html")
    else:
        miFormulario=FormularioCovid()
    return render(request, "cargar_info/info_covid.html", {"form": miFormulario})


def cargar_info_fiebre_a(request):
    if request.method=="POST":       
            miFormulario=FormularioFiebreA(request.POST)
            
            #Busco al dni del usuario de la sesion
            
            us=list(Usuario.objects.filter(email=request.user.email))
            dni=us[int(0)].dni
            nombre=us[int(0)].nombre
            apellido=us[int(0)].apellido
            
            
            if miFormulario.is_valid():
                infForm=miFormulario.cleaned_data
                
                #si puso no, guarda sin comprobar fecha                
                if request.POST.get('si_o_no') == "no":
                    
                    #compruebo q no existe historial
                    historial=list(HistorialFiebreA.objects.filter(usuario=dni))
                    
                    if len(historial)>0:
                        #si existe solo informa q no modifico la bd
                        messages.add_message(request, messages.INFO, 'Actualización correcta')
                        return redirect('inicio')
                    messages.add_message(request, messages.INFO, 'Informacion guardada')
                    historial=HistorialFiebreA(usuario=dni,si_o_no='no')
                    historial.save()
                    return redirect('inicio')
                #Si puso si, hago una segunda verificacion  
                
                if infForm['si_o_no']=="si": 
                    if infForm['fecha_aplicacion_fiebre_a']>(date.today()):
                        messages.add_message(request, messages.INFO, 'Ingrese una fecha valida') 
                        return render(request,"cargar_info/info_fiebre_a.html")
                    
                    #elimino turno en caso de existir
                    
                    turno=Turno.objects.filter(vacuna="Fiebre amarilla",usuario_a_vacunar=dni, estado="Pendiente", nombre_usuario=nombre, apellido_usuario=apellido)
                    turno.delete()
                    #pregunto si tiene historial. en caso de tenerlo solo modifico.
                    historial=list(HistorialFiebreA.objects.filter(usuario=dni))
                    if len(historial)>0:
                        historial = historial[int(0)]
                        historial.si_o_no = 'si'
                        historial.fecha_aplicacion_fiebre_a = infForm['fecha_aplicacion_fiebre_a']
                        historial.vacuna_externa_fiebre=True
                        historial.save()
                        #retorno
                    
                        messages.add_message(request, messages.INFO, 'Actualización correcta')
                        return redirect('inicio')    
                    historial=HistorialFiebreA.objects.create(fecha_aplicacion_fiebre_a=infForm['fecha_aplicacion_fiebre_a'],usuario=dni,si_o_no=infForm['si_o_no'], nombre_usuario=nombre, apellido_usuario=apellido)
                    historial.save()
                    
                    #retorno
                    
                    messages.add_message(request, messages.INFO, 'Su información a sido guardada')
                    return redirect('inicio')             
            else:
                #Si puso que "si" y no subio una fecha, pide que la ingrese
                    infForm=miFormulario.cleaned_data
                    
                    if infForm['si_o_no']=="si":
                        messages.add_message(request, messages.INFO, 'Ingrese una fecha') 
                        return render(request,"cargar_info/info_fiebre_a.html")
                    
                    if request.POST.get('si_o_no') == "no": 
                    #compruebo q no existe historial
                    
                        historial=list(HistorialFiebreA.objects.filter(usuario=dni))
                    
                        if len(historial)>0:
                            messages.add_message(request, messages.INFO, 'Su información a sido guardada')
                            return redirect('inicio')
                        messages.add_message(request, messages.INFO, 'Su información a sido guardada')
                        historial=HistorialFiebreA(usuario=dni,si_o_no='no')
                        historial.save()
                        return redirect('inicio')      
                    #Si subio una fecha, ya se guarda en el historial
                    #Solo es una aplicación de la vacuna
                    #Agrego vacuna_externa_fiebre, variable booleana para saber si se la dio en Vacun Assist o en otro lado
                    #Si es True, se la dio en otro lado
    else:
        miFormulario=FormularioFiebreA()
    return render(request, "cargar_info/info_fiebre_a.html", {"form": miFormulario})


def sacar_turno_fiebre_amarilla(request):
    if request.method=="POST":
        miFormulario=FormularioFiebreA(request.POST)
        
        #Chequeo que tenga un historial cargado
        his=tiene_historial_fiebre_a(request)
        if his == 0:
            messages.add_message(request, messages.ERROR, 'Por favor, cargue la información correspondiente a la vacuna de la fiebre amarilla') 
            return redirect('inicio')
        
        if his == 1:
            messages.add_message(request, messages.ERROR, 'Usted ya se aplico la dosis corrrespondiente de la vacuna de la fiebre amarilla') 
            return redirect('inicio')
        
        #Chequeo que no tenga un turno previo
        tur=tieneTurno(request, 'Fiebre amarilla')
        if tur == True:
            messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de fiebre amarilla') 
            return redirect('inicio')

        #Busco la edad del usuario
        #Busco por mail porque User y Usuario comparten ID en algunos casos pero no en todos
        #Lo que sabemos que si o si tienen en comun es el mail, (En este sistena, en User, username tambien es el mail)

        us=list(Usuario.objects.filter(email=request.user.email))


        fecha_nac=us[int(0)].fecha_nacimiento
        dni=us[int(0)].dni
        direc=us[int(0)].direccion
        nombre=us[int(0)].nombre
        apellido=us[int(0)].apellido
        usuario_edad=calcularEdad(fecha_nac)


        if request.POST.get('si_o_no') == 'si':
            if usuario_edad < 60:
                #Menor de 60
                #El turno lo asigna el administrador, se manda un "pedido"
                #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna de la fiebre amarilla(El listado no es para esta demo)

                turno=Turno(vacuna='Fiebre amarilla', usuario_a_vacunar=dni, vacunatorio=direc, estado='Pendiente', nombre_usuario=nombre, apellido_usuario=apellido)
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
        #Chequeo que no tenga un historial cargado
        his=tiene_historial_gripe(request)
        if his == True:
            messages.add_message(request, messages.ERROR, 'Usted ya cargo su informacion y tiene un turno para la vacuna de la gripe') 
            return redirect('inicio')
        
        #Chequeo que no tenga un turno previo
        tur=tieneTurno(request, 'Gripe')
        if tur == True:
            messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de la gripe') 
            return redirect('inicio')

        #Busco la edad del usuario
        #Busco al email(unico) del usuario de la sesion
        us=list(Usuario.objects.filter(email=request.user.email))

        fecha_nac=us[int(0)].fecha_nacimiento
        dni=us[int(0)].dni
        nombre=us[int(0)].nombre
        apellido=us[int(0)].apellido
        direc=us[int(0)].direccion
        usuario_edad=calcularEdad(fecha_nac)

        if request.POST.get('si_o_no') == 'no': 
            if usuario_edad < 60:
                #Menor de 60
                #Asigno turno a 6 meses
                dia_actual=datetime.now()
                fecha_turno= dia_actual + timedelta(days=180)
                    
                hora=random.randint(9,16)
                hora_turno= time(hour= hora, minute= 00)
                turno=Turno(fecha=fecha_turno, hora= hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado', nombre_usuario=nombre, apellido_usuario=apellido)
                turno.save()
                messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                return redirect('inicio')

            else: 
                #Mayor de 60
                #Asigno turno a 3 meses
                dia_actual=datetime.now()
                fecha_turno= dia_actual + timedelta(days=90)
                    
                hora=random.randint(8,15)
                hora_turno= time(hour=hora, minute=15)

                turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado',nombre_usuario=nombre, apellido_usuario=apellido)
                turno.save()
                messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                return redirect('inicio')
        else:
            #Si puso que "si", pide que ingrese una fecha
            if request.POST.get('fecha_aplicacion_gripe') is None:
                messages.add_message(request, messages.INFO, 'Si se vacuno para la gripe, ingrese la fecha de la ultima aplicacion')
                return render(request,"cargar_info/info_gripe.html") 

            #una_fecha = '20/04/2019'
            #fecha_dt = datetime.strptime(una_fecha, '%d/%m/%Y')
            #print(fecha_dt)
            dia_apli= datetime.strptime(request.POST.get('fecha_aplicacion_gripe'), '%Y-%m-%d')       
            if dia_apli>(datetime.today()):
                messages.add_message(request, messages.INFO, 'Ingrese una fecha valida') 
                return render(request,"cargar_info/info_gripe.html")
            
            #Segun la edad que tengan, es la diferencia de dias que tiene que esperar para el turno
            #Menor de 60, 6 meses = 180 días
            #Mayor de 60, 3 meses = 90 días
            if usuario_edad < 60:
                dif_mes=180
            else:
                dif_mes=90
            dia_actual=datetime.now()
            fecha_p_turno= dia_actual + timedelta(days=dif_mes)
            dif_dias=fecha_p_turno - dia_apli
            if dif_dias.days > 365:
                #Cumple con el tiempo correspondiente
                hora=random.randint(9,16)
                hora_turno= time(hour= hora, minute= 00)
                turno=Turno(fecha=fecha_p_turno, hora= hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado', nombre_usuario=nombre, apellido_usuario=apellido)
                turno.save()
                messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                return redirect('inicio')
            else:
                #No paso el tiempo correspondiente
                #Agrego vacuna_externa_gripe, variable booleana para saber si se la dio en Vacun Assist o en otro lado
                #Si es True, se la dio en otro lado

                historial=HistorialGripe(usuario=dni, fecha_aplicacion_gripe= request.POST.get('fecha_aplicacion_gripe'), vacuna_externa_gripe= True, nombre_usuario=nombre, apellido_usuario=apellido)
                historial.save()
                messages.add_message(request, messages.ERROR, 'Todavia no paso el tiempo correspondiente para su proxima aplicación de la vacuna') 
                return redirect('inicio')  
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
            contra1=infForm['contraseña1']
            contra2=infForm['contraseña2']
            if (len(contra1) < 6): 
                #si la contraseña es menor a 6 salta mensaje de error
                messages.add_message(request, messages.ERROR, 'La contraseña debe tener minimo 6 caracteres')
                return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})
            else: 
                if (contra1==contra2) and (len(contra1)>= 6):
                    
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
                    messages.add_message(request, messages.ERROR, 'Las contraseñas no coinciden')
                    return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})
        else:
            #aca entra si el usuario deja celdas en blanco o inserta valores no validos
            messages.add_message(request, messages.ERROR, 'Complete todas las casillas')
            
            return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})
    
    return render(request, "gestion_usuarios/modificar_perfil.html",{'form':miFormulario})


def estatus_turno(request):
    #En el archivo html: si tiene elementos: recorrer la lista, y mostrar datos

    #Busco al dni del usuario de la sesion
    #Busco por mail porque User y Usuario comparten ID en algunos casos pero no en todos
    #Lo que sabemos que si o si tienen en comun es el mail, (En este sistena, en User, username tambien es el mail)
    
    us=list(Usuario.objects.filter(email=request.user.email))
    dni=us[int(0)].dni
    usuario=us[int(0)]

    #Busco en la lista turnos, los turnos que corresponden al usuario
    #Puede tener hasta tres turnos, o no tener ninguno
    turnos=list(Turno.objects.filter(usuario_a_vacunar=dni))


    return render(request, "gestion_usuarios/estatus_turno.html", {"turnos": turnos, "usuario": usuario})


def mi_perfil(request):
    #Esto muestra los datos del perfil del usuario:
    #Nombre, apellido, dni, email, fecha de nacimiento, vacunatorio

    #Busco al dni del usuario de la sesion
    #Busco por mail porque User y Usuario comparten ID en algunos casos pero no en todos
    #Lo que sabemos que si o si tienen en comun es el mail, (En este sistena, en User, username tambien es el mail)
    
    us=list(Usuario.objects.filter(email=request.user.email))

    #Guardo el usuario en la variable
    usuario=us[int(0)]

    return render(request, "gestion_usuarios/mi_perfil.html", {"usuario": usuario})


def ver_historial(request):
    #Mostrar todos los historiales de vacunacion

    #Busco el dni
    #us=list(Usuario.objects.filter(id=request.user.id))
    #Busco por mail porque User y Usuario comparten ID en algunos casos pero no en todos
    #Lo que sabemos que si o si tienen en comun es el mail, (En este sistena, en User, username tambien es el mail)
    us=list(Usuario.objects.filter(email=request.user.email))


    dni=us[int(0)].dni

    #Busco los 3 historiales
    his_covid=list(HistorialCovid.objects.filter(usuario=dni))
    his_fiebre_a=list(HistorialFiebreA.objects.filter(usuario=dni))
    his_gripe=list(HistorialGripe.objects.filter(usuario=dni))

    return render(request, "gestion_usuarios/historial.html", {"historial_covid": his_covid, "historial_fiebre_a": his_fiebre_a, "historial_gripe": his_gripe})


############
###DEMO 2###
############
    
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
                    return redirect('inicio_vac')

                else: # no entra nunca aca ??
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

def listado_turnos(request): # no se usa, solo se uso para la demo
    #Esto solo muestra un listado de los turnos, no cambia estado ni nada.
    #Dia actual
    dia_actual=datetime.now()
    #Busco ID del vacunador logueado y asi guardo el vacunatorio
    vac=list(Vacunador.objects.filter(email=request.user.email))
    #Busco el vacunatorio del vacunador
    vacunatorio_actual=vac[int(0)].vacunatorio
    #Busco los turnos del vacunatorio y de la fecha actual, de estado= 'Asignado'
    turnos=list(Turno.objects.filter(fecha=dia_actual, vacunatorio=vacunatorio_actual, estado='Asignado'))


    return render(request, "gestion_vacunador/listado_turnos.html", {"turnos": turnos})

def mostrar_turno(request, turno, formulario):
    return render(request, "gestion_vacunador/turno.html", {"turno": turno, "form": formulario})

def observar_turnos_dia(request):
    #Dia actual
    dia_actual=datetime.now()
    #Busco ID del vacunador logueado y asi guardo el vacunatorio
    vac=list(Vacunador.objects.filter(email=request.user.email))
    #Busco el vacunatorio del vacunador
    vacunatorio_actual=vac[int(0)].vacunatorio
    #Busco los turnos del vacunatorio y de la fecha actual, de estado= 'Asignado'
    turnos=list(Turno.objects.filter(fecha=dia_actual, vacunatorio=vacunatorio_actual, estado='Asignado'))
    
    cant=len(turnos)
    cont=0
    while cont != cant:
        turnos=list(Turno.objects.filter(fecha=dia_actual, vacunatorio=vacunatorio_actual, estado='Asignado'))
        turno=turnos[int(cont)]
        cont=cont+1
        if request.method=="POST":
            miFormulario=FormularioEstadoTurno(request.POST)
            mostrar_turno(request,turno, miFormulario)
            if miFormulario.is_valid():
                infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios
                
                if infForm['estado'] == 'completo':
                    #Turno completo
                    #Cambio el estado del turno
                    tur=list(Turno.objects.filter(id=turno.id))
                    tur=tur[0]
                    tur.estado='Completo'
                    tur.save()
                    #Actualizo el historial de vacunacion dependiendo de la vacuna
                    if turno.vacuna == 'Coronavirus':
                        #Vacuna del coronavirus
                        #Busco el historial de covid del usuario (turno.usuario_a_vacunar)
                        #Se supone que si saco un turno el historial se creo en ese momento. Asumimos que existe
                        hist_covid=list(HistorialCovid.objects.filter(usuario=turno.usuario_a_vacunar))
                        
                        hist_covid=hist_covid[int(0)]
                        #Creo un historial nuevo con los mismos datos que tenia
                        if hist_covid.cantidad_dosis == '0':
                            #Si tiene 0 dosis ingresadas, esta es su primera dosis
                            hist_covid.cantidad_dosis=1
                            hist_covid.fecha_primeradosis=datetime.now()
                            hist_covid.save()
                            
                        else:
                            #Si tiene 1 dosis ingresada esta es su segunda dosis
                            #Si tiene 2 dosis ingresadas no deberia porque aparecer aca. No lo considero como opcion posible.
                            hist_covid.cantidad_dosis=2
                            hist_covid.fecha_segundadosis=datetime.now()
                            hist_covid.save()
                            
                    else:
                        if turno.vacuna == 'Gripe':
                            #Vacuna de la gripe
                            #Actualizar fecha de aplicacion
                            hist_gripe=list(HistorialGripe.objects.filter(usuario=turno.usuario_a_vacunar))
                            hist_gripe=hist_gripe[int(0)]
                            hist_gripe.fecha_aplicacion_gripe=datetime.now()    
                            hist_gripe.save()                        
            
    
                        else:
                            if turno.vacuna == 'Fiebre amarilla':
                                #Vacuna de la fiebre amarilla
                                #Actualizar fecha de aplicacion y si_o_no
                                hist_fiebrea=list(HistorialFiebreA.objects.filter(usuario=turno.usuario_a_vacunar))
                                hist_fiebrea=hist_fiebrea[0]
                                hist_fiebrea.fecha_aplicacion_fiebre_a=datetime.now()    
                                hist_fiebrea.si_o_no='si'
                                hist_fiebrea.save() 
                    
                    return render(request, "gestion_vacunador/listado_turnos.html") #llamaba a turnos_del_dia
                    #si es completo actualizo la pantalla despues de actualizar los datos del historial
                else:
                    #Turno incompleto
                    #Actualizo el estado del turno.
                    tur=list(Turno.objects.filter(id=turno.id))
                    tur=tur[0]
                    tur.estado='Incompleto'
                    tur.save()
                    
                    return render(request, "gestion_vacunador/listado_turnos.html") #llamaba a turnos_del_dia

        else:
            miFormulario=FormularioEstadoTurno()    
        return render(request, "gestion_vacunador/listado_turnos.html", {"turnos": turnos}) #llamaba a turnos_del_dia
   
    
    return render(request, "gestion_vacunador/listado_turnos.html", {"turnos": turnos}) #llamaba a turnos_del_dia


def ver_historial_vac(request):

    #Mostrar todos los historiales de vacunacion

    #Busco el dni
    #us=list(Usuario.objects.filter(id=request.user.id))
    #Busco por mail porque User y Usuario comparten ID en algunos casos pero no en todos
    #Lo que sabemos que si o si tienen en comun es el mail, (En este sistena, en User, username tambien es el mail)
    us=list(Usuario.objects.filter(email=request.user.email))
    dni=us[int(0)].dni
    #Busco los 3 historiales
    his_covid=list(HistorialCovid.objects.filter(usuario=dni))
    his_fiebre_a=list(HistorialFiebreA.objects.filter(usuario=dni))
    his_gripe=list(HistorialGripe.objects.filter(usuario=dni))

    return render(request, "gestion_vacunador/historial_vac.html", {"historial_covid": his_covid, "historial_fiebre_a": his_fiebre_a, "historial_gripe": his_gripe})


def agregar_persona(request):
    if request.method=="POST":
        miFormulario=FormularioRegistroVacunacion(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data
            #Validar si el mail no esta en la base de datos
            us=list(Usuario.objects.filter(email=infForm['email']))
            
            if len(us) > 0: #Si el mail ya esta registrado, mostrar historial y despues agregar vacuna

                messages.add_message(request, messages.INFO, 'Usuario ya registrado')
                return render(request, "gestion_vacunador/ver_historial_vac.html")
                
            
            
            if (len(infForm['dni'])==8): #verifico que el dni tenga 8 digitos, simulacion de renaper
                #Generar contraseña random para el usuario
                contra=str(random.randint(100000,999999))
                
                #Busco el vacunatorio actual y lo inicializo con ese
                vac=list(Vacunador.objects.filter(email=request.user.email))
                vacunatorio=vac[int(0)].vacunatorio
                
                codAleatorio=generarCodigoAleatorio()
                Codigos.objects.create(codigo=codAleatorio)

                #Para guardar la fecha de registro
                dia_actual=datetime.now()
                fecha_reg=date(dia_actual.year, dia_actual.month, dia_actual.day)

                Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=vacunatorio, email=infForm['email'], contraseña=contra, codigo=codAleatorio, fecha_registro= fecha_reg)
                #aca se crea un usuario de tipo User para que se guarde en la base de datos y luego poder autenticar de forma correcta
                user=User.objects.create_user(infForm['email'],infForm['email'],contra)
                user.save()
            #    login(request, user)
                #Envio de email
                

                mensaje="Registro exitoso en VacunAssist! Tu codigo para iniciar sesion es: "+ str(codAleatorio) + " y tu contraseña es: " + str(contra) + ". Le recomendamos cambiar su contraseña." 
                send_mail('Registro exitoso',mensaje,'vacun.assist.cms@hotmail.com', [infForm['email']])
                messages.add_message(request, messages.INFO, 'Registro exitoso en VacunAssist')
                dni=infForm['dni']
                return redirect('inicio_vac')

            else:
                messages.add_message(request, messages.INFO, 'ERROR dni invalido!')
                return render(request, "gestion_vacunador/agregar_persona.html",{"form":miFormulario})
        else:
            messages.add_message(request, messages.INFO, 'ERROR formulario invalido!')
            return render(request, "gestion_vacunador/agregar_persona.html",{"form":miFormulario})   
    else:
        miFormulario=FormularioRegistroVacunacion()
    return render(request, "gestion_vacunador/agregar_persona.html", {"form": miFormulario})

def agregar_vacuna(request):
    if request.method=="POST":
        miFormulario=FormularioAgregarVacuna(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data
            #Aca se saca el turno correspondiente a "vacuna"
                
            ahora = datetime.now()
            #Si uso directamente now.date() y now.time() da error y no guarda nada
            hora_turno= time(hour= ahora.hour, minute= ahora.minute)
            fecha_turno= date(year=ahora.year, month=ahora.month, day= ahora.day )    
            
            hora_turno= time(hour= ahora.hour, minute= ahora.minute)
            #Busco el vacunatorio actual y lo inicializo con ese
        #    vac=list(Vacunador.objects.filter(email=request.user.get_username()))
            vac=list(Vacunador.objects.filter(email=request.user.email ))
            vacunatorio=vac[int(0)].vacunatorio
    
            us=list(Usuario.objects.filter(dni=infForm['dni']))
            dni=us[int(0)].dni  
            nombre=us[int(0)].nombre
            apellido=us[int(0)].apellido

            #Si cant_dosis tiene informacion, es una vacuna del coronavirus. 
            #Segun la cantidad de dosis que subio, se cambia el valor
            if infForm['vacuna'] == 'Coronavirus':
                turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna=infForm['vacuna'], usuario_a_vacunar=dni, vacunatorio=vacunatorio, estado='Completo', nombre_usuario=nombre, apellido_usuario=apellido, dosis=infForm['nro_dosis'])
                turno.save()
            else:
                turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna=infForm['vacuna'], usuario_a_vacunar=dni, vacunatorio=vacunatorio, estado='Completo', nombre_usuario=nombre, apellido_usuario=apellido)
                turno.save()
                
            #Aca se actualiza el historial del usuario, dependiendo de la vacuna
                


            if infForm['vacuna']  == "Coronavirus":
                #Vacuna del coronavirus
                #Depende de las dosis ingresadas, se guarda la fecha de HOY como primera o segunda dosis
                if infForm['nro_dosis'] == '1':
                    historial_covid=HistorialCovid(usuario=infForm['dni'], cantidad_dosis=infForm['nro_dosis'], nombre_usuario=nombre, apellido_usuario=apellido)
                    historial_covid.save()
                    #Se le da el turno de la segunda dosis de aca a "X" meses
                    
                    dia_actual=datetime.now()
                    fecha_turno_2= dia_actual + timedelta(days=90) # 3 meses
                    hora=random.randint(8,15)
                    hora_turno_2= time(hour=hora, minute=45)
                    
                    turno=Turno(fecha=fecha_turno_2, hora=hora_turno_2, vacuna=infForm['vacuna'], usuario_a_vacunar=infForm['dni'], vacunatorio=vacunatorio, estado='Asignado', nombre_usuario=nombre, apellido_usuario=apellido, dosis='2')
                    turno.save()
                        
                else:
                    historial_covid=HistorialCovid(usuario=infForm['dni'], cantidad_dosis=infForm['nro_dosis'], nombre_usuario=nombre, apellido_usuario=apellido)
                    historial_covid.save()
            else:
                if infForm['vacuna']  == "Gripe": #Vacuna de la gripe
                    historial_gripe=HistorialGripe(usuario=infForm['dni'], fecha_aplicacion_gripe=fecha_turno, nombre_usuario=nombre, apellido_usuario=apellido)
                    historial_gripe.save()
                else:
                    #Vacuna de la fiebre amarilla
                    historial_fiebre=HistorialFiebreA(usuario=infForm['dni'], fecha_aplicacion_fiebre_a=fecha_turno, si_o_no='si', nombre_usuario=nombre, apellido_usuario=apellido)
                    historial_fiebre.save()
            # luego de actualizar el historial, redirigo a inicio_vac
            messages.add_message(request, messages.INFO, 'Se guardo la informacion de la vacuna aplicada')
            return render(request, "gestion_vacunador/inicio_vac.html")
    
    else:
        miFormulario=FormularioAgregarVacuna()
    return render(request, "gestion_vacunador/agregar_vacuna.html", {"form": miFormulario})

############
###DEMO 3###
############


def inicio_administrador(request):
    if request.method=="POST":
        miFormulario=FormularioAutenticacionAdmin(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios

            #Se podrian chequear todos los campos por separado
            admin=list(Administrador.objects.filter(email=infForm['email'], contraseña=infForm['contraseña']))
            
            #utilice una lista(q siempre tiene long o 0 o 1) por que de la forma anterior no entraba al if correctamente, se puede cambiar para solo extraer un objeto.
            if len(admin)>0:
                username=infForm['email']
                password=infForm['contraseña'] 
             
                user=authenticate(username=username, password=password)
                if user is not None:  
             
                    messages.add_message(request, messages.INFO, 'Inicio de sesion Exitoso')
                    login(request, user)
                    return redirect('inicio_admin')

                else: # no entra nunca aca ??
                    messages.add_message(request, messages.ERROR, 'ERROR el usuario no se encuentra autenticado') 
                    return render(request, "gestion_admin/inicio_admin.html")          
            else:
                messages.add_message(request, messages.ERROR, 'ERROR usuario y/o contraseña incorrecto')
                return render(request, "autenticacion/login_admin.html")
    else:
        #Si entra al else, seria el formulario vacio, para que llene los datos
        miFormulario=FormularioAutenticacionAdmin()

    return render(request, "autenticacion/login_admin.html", {"form": miFormulario})

def informe_cantidad_persona(request):
    #Listado:
    #Se vacunaron "x" cantidad de personas:
    #Mostrar si o si: DNI y vacunatorio
    #Podemos mostrar para que quede mejor: Nombre y apellido, fecha de nacimiento
    
    if request.method=="POST":
        miFormulario=FormularioVacunas(request.POST)  

        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios        
            vac=infForm["vacuna"]
            turnos=list(Turno.objects.filter(vacuna=vac, estado='Completo'))
            return render(request, "gestion_admin/personas_vacuna.html",{"turnos":turnos})
        else:
            messages.add_message(request, messages.INFO, 'Formulario invalido') 

    return render(request, "gestion_admin/informe_registro.html")
    


def informe_personas_registradas(request): 
    #Personas que se registraron
    #Filtrar por DNI, vacunatorio.
     
    if request.method=="POST":
        miFormulario=FormularioBuscarVacunador(request.POST)  

        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios        
            vac= infForm["direccion"]
            personas=list(Usuario.objects.filter(direccion=vac))
            return render(request, "gestion_admin/personas_reg.html",{"personas":personas} )
        else:
            messages.add_message(request, messages.INFO, 'Formulario invalido') 

    return render(request, "gestion_admin/informe_cant_personas.html")


def ver_historial_admin(request):  # HECHO
    #El admin ve el historial de vacunacion de un usuario
    #Se busca por DNI, busca los 3 historiales (o los que tenga) y muestra

    if request.method=="POST":
        miFormulario=FormularioBuscarUsuario(request.POST)  

        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios        
            dni= infForm["dni"]
     
            #Busco los 3 historiales
            his_covid=list(HistorialCovid.objects.filter(usuario=dni))
            his_fiebre_a=list(HistorialFiebreA.objects.filter(usuario=dni))
            his_gripe=list(HistorialGripe.objects.filter(usuario=dni))

            return render(request, "gestion_admin/historial_usu.html", {"historial_covid": his_covid, "historial_fiebre_a": his_fiebre_a, "historial_gripe": his_gripe})
        else:
            messages.add_message(request, messages.INFO, 'Formulario invalido') 

    return render(request, "gestion_admin/historial_admin.html")


def modificar_nombre_vacunatorio(request):
    #Modifica el nombre del vacunatorio
    #Esto ?? 
    #Idea: armar modelo "Vacunatorio" con nombre y direccion 

    vacunatorios_lista=Vacunatorio.objects.filter()
    if request.method=="POST":
        miFormulario=FormularioNombreVacunador(request.POST)  

        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios
   #         nombre = infForm["direccion"]
   #         nombreVac=list(NombreVacunador.objects.filter(vacunatorio=nombre))
   #         nombreVac[int(0)].nuevo_nombre = infForm["nuevo_nombre"]
   #         nombreVac.save()

            #Obtengo la info del formulario
            nombre_nuevo = infForm['nombre']    
            vacunatorio_nuevo = infForm['nombre_actual']

            #Busco en tabla "Vacunatorio" el vacunatorio a cambiar
            #Guardo el nuevo nombre
            vac=list(Vacunatorio.objects.filter(nombre=vacunatorio_nuevo))
            while (len(vac) == int(0)):
                messages.add_message(request, messages.INFO, 'Nombre incorrecto')    
                return render(request, "gestion_admin/modificar_nombre.html",{"vacunatorios":vacunatorios_lista})
            vac=vac[int(0)]
            vac.nombre=nombre_nuevo
            vac.save()

            #Cambio en la tabla Usuario, el nombre del nuevo vacunatorio
            usuarios=list(Usuario.objects.filter(direccion=vacunatorio_nuevo))

            cont=0
            for us in usuarios:
                us=usuarios[cont]
                cont=cont+1
                us.direccion=nombre_nuevo
                us.save()
                

            #Cambio en la tabla Turno, en nombre del vacunatorio
            turnos=list(Turno.objects.filter(vacunatorio=vacunatorio_nuevo))

            cont=0
            for tur in turnos:
                tur=turnos[cont]
                cont=cont+1
                tur.vacunatorio=nombre_nuevo
                tur.save()

            #Cambio en la tabla del Vacunadaor, el nombre del vacunatorio

            vacunadores=list(Vacunador.objects.filter(vacunatorio=vacunatorio_nuevo))

            cont=0
            for vac in vacunadores:
                vac=vacunadores[cont]
                cont=cont+1
                vac.vacunatorio=nombre_nuevo
                vac.save()


            messages.add_message(request, messages.INFO, 'Actualizacion correcta de nombre')    
            return render(request, "gestion_admin/modificar_nombre.html",{"vacunatorios":vacunatorios_lista})
        else:
            messages.add_message(request, messages.INFO, 'Formulario invalido') 
    return render(request, "gestion_admin/modificar_nombre.html", {"vacunatorios":vacunatorios_lista})


def asignar_turno_covid(request):
    #Listado de gente que pidio vacuna covid 
    # + opcion de asignar turno (cambiar el estado del turno existente y asignarle una fecha)
    # + ver historial de la persona para "aceptar" y "rechazar" el pedido del turno
    turnos=list(Turno.objects.filter(estado='Pendiente', vacuna="Fiebre Amarilla"))
   
    cant=len(turnos)
    cont=0
   
    while cont != cant:
        turnos=list(Turno.objects.filter(estado='Pendiente', vacuna="Fiebre Amarilla"))
        turno=turnos[int(cont)]
        cont=cont+1
        if request.method=="POST":  
            miFormulario=FormularioEstadoTurnoAdmin(request.POST)
            mostrar_turno(request,turno, miFormulario)
            if miFormulario.is_valid():
                infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios
                
                if infForm['estado'] == 'asignar':
                    #Turno completo
                    #Cambio el estado del turno
                    tur=list(Turno.objects.filter(id=turno.id))
                    tur=tur[0]
                    fecha_turno = infForm["fecha_aplicacion"] 
                    hora=random.randint(8,16)
                    tur.fecha=fecha_turno
                    tur.hora=hora
                    tur.estado='Asignado'
                    tur.save()
                   
                else:
                    #Turno rechazado
                    #Actualizo el estado del turno.
                    tur=list(Turno.objects.filter(id=turno.id))
                    tur=tur[0]
                    tur.estado='Incompleto'
                    tur.save()
        else:
            messages.add_message(request, messages.ERROR, 'Invalido')
            return render(request, "gestion_admin/asignar_covid.html") 
    else:
        messages.add_message(request, messages.ERROR, 'Sin turnos!!')
    return render(request, "gestion_admin/asignar_covid.html")

def asignar_turno_covid_2(request):
     #El admin ve el historial de vacunaciones pendientes
    
    turnos=list(Turno.objects.filter(vacuna="Coronavirus", estado="Pendiente"))
    if request.method=="POST":  
        miFormulario=FormularioModificarEstado(request.POST)
        if miFormulario.is_valid():
            ##extraigo datos para luego modificar
            infForm=miFormulario.cleaned_data
            turnoMod=list(Turno.objects.filter(vacuna="Coronavirus", estado="Pendiente",usuario_a_vacunar=infForm['dni']))
            turnoMod=turnoMod[0]
            if (infForm['estado']=="Incompleto"): #EN CASO DE SER INCOMPLETO ELIMINO EL TURNO
                Turno.objects.filter(vacuna="Coronavirus", estado="Pendiente",usuario_a_vacunar=infForm['dni']).delete()
                turnos=list(Turno.objects.filter(vacuna="Coronavirus", estado="Pendiente"))
                usuario=list(Usuario.objects.filter(dni=infForm['dni']))
                email=usuario[0].email
                #Mando mail al usuario
                mensaje="Su pedido de vacuna ha sido rechazado." 
                send_mail('Turno rechazado',mensaje,'vacun.assist.cms@hotmail.com', [email])
                return render(request, "gestion_admin/asignar_covid.html",{"turnos": turnos})
            usuario=list(Usuario.objects.filter(dni=infForm['dni']))
            email=usuario[0].email
            #Mando mail al usuario
            mensaje="Su pedido de vacuna ha sido aceptado! Ingrese a su cuenta en VacunAssist para ver los detalles del turno" 
            send_mail('Turno asignado',mensaje,'vacun.assist.cms@hotmail.com', [email])
            turnoMod.estado=infForm['estado']
            turnoMod.save()
            
            #actualizo los turnos a mostrar
            turnos=list(Turno.objects.filter(vacuna="Coronavirus", estado="Pendiente"))
            return render(request, "gestion_admin/asignar_covid.html",{"turnos": turnos})
    return render(request, "gestion_admin/asignar_covid.html",{"turnos": turnos})

def asignar_turno_fiebre_a_2(request):
     #El admin ve el historial de vacunaciones pendientes
    
    turnos=list(Turno.objects.filter(vacuna="Fiebre amarilla", estado="Pendiente"))
    if request.method=="POST":  
        miFormulario=FormularioModificarEstado(request.POST)
        if miFormulario.is_valid():
            ##extraigo datos para luego modificar
            infForm=miFormulario.cleaned_data
            turnoMod=list(Turno.objects.filter(vacuna="Fiebre amarilla", estado="Pendiente",usuario_a_vacunar=infForm['dni']))
            turnoMod=turnoMod[0]
            if (infForm['estado']=="Incompleto"): #EN CASO DE SER INCOMPLETO ELIMINO EL TURNO
                Turno.objects.filter(vacuna="Fiebre amarilla", estado="Pendiente",usuario_a_vacunar=infForm['dni']).delete()
                turnos=list(Turno.objects.filter(vacuna="Fiebre amarilla", estado="Pendiente"))
                
                usuario=list(Usuario.objects.filter(dni=infForm['dni']))
                email=usuario[0].email
                #Mando mail al usuario
                mensaje="Su pedido de vacuna ha sido rechazado." 
                send_mail('Turno rechazado',mensaje,'vacun.assist.cms@hotmail.com', [email])
                
                return render(request, "gestion_admin/asignar_fiebre.html",{"turnos": turnos})
            usuario=list(Usuario.objects.filter(dni=infForm['dni']))
            email=usuario[0].email
            #Mando mail al usuario
            mensaje="Su pedido de vacuna ha sido aceptado! Ingrese a su cuenta en VacunAssist para ver los detalles del turno" 
            send_mail('Turno asignado',mensaje,'vacun.assist.cms@hotmail.com', [email])
            turnoMod.estado=infForm['estado']
            turnoMod.save()
            
            #actualizo los turnos a mostrar
            turnos=list(Turno.objects.filter(vacuna="Fiebre amarilla", estado="Pendiente"))
            return render(request, "gestion_admin/asignar_fiebre.html",{"turnos": turnos})
    return render(request, "gestion_admin/asignar_fiebre.html",{"turnos": turnos})



def marcar_turno_covid_2(request):   
    return render(request, "gestion_admin/marcar_turno_covid.html")

def asignar_turno_fiebre_a(request):
    #Listado de gente que pidio vacuna de la fiebre amarilla 
    # + opcion de asignar turno (cambiar el estado del turno existente y asignarle una fecha)
    # + ver historial de la persona para "aceptar" y "rechazar" el pedido del turno

    turnos=list(Turno.objects.filter(estado='Pendiente', vacuna="Fiebre Amarilla"))
    
    cant=len(turnos)
    cont=0
    while cont != cant:
        turnos=list(Turno.objects.filter(estado='Pendiente',vacuna="Fiebre Amarilla"))
        turno=turnos[int(cont)]
        cont=cont+1
        if request.method=="POST":
            miFormulario=FormularioEstadoTurnoAdmin(request.POST)
            mostrar_turno(request,turno, miFormulario)
            if miFormulario.is_valid():
                infForm=miFormulario.cleaned_data #Aca se guarda toda la info que se lleno en los formularios
                
                if infForm['estado'] == 'asignar':
                    #Turno completo
                    #Cambio el estado del turno
                    tur=list(Turno.objects.filter(id=turno.id))
                    tur=tur[0]
                    tur.estado='Asignado'
                    tur.save()
                  
                    return render(request,"gestion_admin/asignar_fiebre.html") 
                else:
                    #Turno incompleto
                    #Actualizo el estado del turno.
                    tur=list(Turno.objects.filter(id=turno.id))
                    tur=tur[0]
                    tur.estado='Asignado'
                    tur.save()
                    
                    return render(request, "gestion_admin/asignar_fiebre.html") #llamaba a turnos_del_dia

        else:
            miFormulario=FormularioEstadoTurnoAdmin()    
        return render(request,"gestion_admin/asignar_fiebre.html", {"turnos": turnos}) #llamaba a turnos_del_dia
    
    return render(request, "gestion_admin/asignar_fiebre.html")


def informe_covid(request): #NO SE USA
    #Listado:
    #Personas que pidieron la vacuna de covid

    turnos=list(Turno.objects.filter(vacuna='Coronavirus'))
    return render(request, "gestion_admin/informe_covid.html",{"turnos":turnos} )

def informe_fiebre_a(request): #  
    #Listado:
    #Personas que pidieron la vacuna de la fiebre amarilla

    turnos=list(Turno.objects.filter(vacuna='Fiebre Amarilla'))
    return render(request, "gestion_admin/informe_fiebre_a.html",{"turnos":turnos})