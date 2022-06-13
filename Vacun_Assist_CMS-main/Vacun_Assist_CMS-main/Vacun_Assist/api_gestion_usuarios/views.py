# Create your views here.
from cgitb import html
from email import message
import email
from mmap import PAGESIZE
import re
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
#from django.views.generic import View
from django.contrib.auth import login, logout, authenticate
#from django.contrib import messages
from api_gestion_usuarios.forms import FormularioAutenticacion, FormularioModificar, FormularioRegistro, FormularioCovid, FormularioFiebreA, FormularioGripe, FormularioAutenticacionVacunador, FormularioEstadoTurno, FormularioRegistroVacunacion
from api_gestion_usuarios.models import Codigos, Usuario, Turno, Vacunador, HistorialCovid, HistorialFiebreA, HistorialGripe
import random
from django.core.mail import send_mail
from django.http.response import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date, datetime, timedelta, time

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
            
            
            if infForm['contraseña1'] != infForm['contraseña2'] and infForm['contraseña1']< int(6): #si es menor a 8tambien debe entrar al if
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
                send_mail('Registro exitoso',mensaje,'vacun.assist.cms@hotmail.com', [infForm['email']])
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
    turnos=list(Turno.objects.filter(usuario_a_vacunar=dni))
    for turno in turnos:
        if turno.vacuna == vacuna_pedido:
            return True

    return tieneTurno

def tiene_historial_covid(request):
    #Busco al dni del usuario de la sesion

    us=list(Usuario.objects.filter(email=request.user.email))

    dni=us[int(0)].dni

    #Busco en la lista HistorialCovid, el historial que corresponde al usuario
    historial=list(HistorialCovid.objects.filter(usuario=dni))

    tiene_historial_covid=False
    if len(historial) != 0:
        tiene_historial_covid=True

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
            us=list(Usuario.objects.filter(email=request.user.email))

            
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
                        dia_actual=datetime.now()
                        fecha_turno = datetime.date(dia_actual+timedelta(days=random.randint(1,7)))
                        hora=random.randint(8,16)
                        hora_turno=time(hour=hora,minute=30)
                        turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado')
                        turno.save()
                        messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                        return redirect('inicio')

                    else:
                        #Menor de 60, sin riesgo
                        #El turno lo asigna manualmente el administrador
                        #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna del coronavirus (El listado no es para esta demo)
                        turno=Turno(vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado='Pendiente')
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
                    turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Coronavirus', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado')
                    turno.save()

                    messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                    return redirect('inicio')
            
      #  return render(request, "cargar_info/info_covid.html")
    else:
        miFormulario=FormularioCovid()
    return render(request, "cargar_info/info_covid.html", {"form": miFormulario})


def cargar_info_fiebre_a(request):
    if request.method=="POST":
        his=tiene_historial_fiebre_a(request)
        #1 y 2 indican que subio informacion, sin importar que subio
        if his == 1 or his==2: #siempre chequea esto ponga que si o ponga que no
            messages.add_message(request, messages.ERROR, 'Usted ya cargo su informacion para la vacuna de la fiebre amarilla') 
            return redirect('inicio')
        miFormulario=FormularioFiebreA(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data

            #Chequeo que no tenga un turno previo
            tur=tieneTurno(request, 'Fiebre amarilla')            
            if tur == True:
                messages.add_message(request, messages.ERROR, 'Usted ya tiene un turno pendiente para la vacuna de fiebre amarilla') 
                return redirect('inicio')   

        #Busco al dni del usuario de la sesion
        us=list(Usuario.objects.filter(email=request.user.email))
        dni=us[int(0)].dni
        if request.POST.get('si_o_no') == "no":
            messages.add_message(request, messages.INFO, 'Su información ha sido guardada')
            historial=HistorialFiebreA(usuario=dni,si_o_no='no')
            historial.save()
            return redirect('inicio')                
        else:
            #Si puso que "si" y no subio una fecha, pide que la ingrese
            if miFormulario.is_valid():
                infForm=miFormulario.cleaned_data
                if infForm['fecha_aplicacion_fiebre_a']>(date.today()):
                    messages.add_message(request, messages.INFO, 'Ingrese una fecha valida') 
                    return render(request,"cargar_info/info_fiebre_a.html") 
                #Si subio una fecha, ya se guarda en el historial
                #Solo es una aplicación de la vacuna
                historial=HistorialFiebreA(usuario=dni, fecha_aplicacion_fiebre_a= infForm['fecha_aplicacion_fiebre_a'],si_o_no='si')
                historial.save()
                messages.add_message(request, messages.INFO, 'Su información ha sido guardada')
                return redirect('inicio')
            else:
                messages.add_message(request, messages.INFO, 'Ingrese una fecha') 
                return render(request,"cargar_info/info_fiebre_a.html")
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
        usuario_edad=calcularEdad(fecha_nac)

        if request.POST.get('si_o_no') == 'si':
            if usuario_edad < 60:
                #Menor de 60
                #El turno lo asigna el administrador, se manda un "pedido"
                #Se agrega a la lista para el administrador, Listado de personas que solicitaron la vacuna de la fiebre amarilla(El listado no es para esta demo)

                turno=Turno(vacuna='Fiebre amarilla', usuario_a_vacunar=dni, vacunatorio=direc, estado='Pendiente')
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
            messages.add_message(request, messages.ERROR, 'Usted ya cargo su informacion para la vacuna de la gripe') 
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
                turno=Turno(fecha=fecha_turno, hora= hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado')
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

                turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado')
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
                turno=Turno(fecha=fecha_p_turno, hora= hora_turno, vacuna='Gripe', usuario_a_vacunar=dni, vacunatorio=direc, estado='Asignado')
                turno.save()
                messages.add_message(request, messages.INFO, 'Su turno ha sido reservado.') 
                return redirect('inicio')
            else:
                #No paso el tiempo correspondiente
                historial=HistorialGripe(usuario=dni, fecha_aplicacion_gripe= request.POST.get('fecha_aplicacion_gripe'))
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



def observar_turnos_dia(request):
    #Dia actual
    dia_actual=datetime.now()

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
                
                hoy=datetime.now()
                #actualizo el estado del turno a completo
                #Se agregan las "Observaciones" al turno, si es que hay
                
                #Actualizo el historial del usuario
                #No seria con infForm, seria con la informacion del Turno que se marca
                #La cantidad de dosis depende de las dosis que tenia el usuario antes. Si es 0 o 1, se le suma 1. Si es 2 queda igual
                if infForm['vacuna']  == "Coronavirus":
                    #Vacuna del coronavirus
                    historial_covid=HistorialCovid(usuario=infForm['dni'], cantidad_dosis=0, fecha_primeradosis=hoy.date)
                    historial_covid.save()
                    #Si esta es la primera dosis, se le da turno para la segunda, y se actualiza la cantidad de dosis en el historial
                    #Si es la segunda dosis, se actualiza el historial con "2" dosis
                else:
                    if infForm['vacuna']  == "Gripe":
                        #Vacuna de la gripe
                        historial_gripe=HistorialGripe(usuario=infForm['dni'], fecha_aplicacion_gripe=hoy.date)
                        historial_gripe.save()
                    else:
                        #Vacuna de la fiebre amarilla
                        historial_fiebre=HistorialFiebreA(usuario=infForm['dni'], fecha_aplicacion_fiebre_a=hoy.date, si_o_no='Si')
                        historial_fiebre.save()
                #Si no tiene datos, creo un historial dependiendo la vacuna
                #Si tiene datos (ej gripe, fecha de ultima aplicacion), los actualizo
                
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
    if request.method=="POST":
        miFormulario=FormularioRegistroVacunacion(request.POST)
        if miFormulario.is_valid():
            infForm=miFormulario.cleaned_data
            #Validar si el mail no esta en la base de datos
            us=list(Usuario.objects.filter(email=infForm['email']))
            
            if len(us) > 0: #Si el mail ya esta registrado, error
                messages.add_message(request, messages.INFO, 'ERROR el email ya se encuentra registrado!')
                return render(request, "gestion_vacunador/agregar_persona.html")
            
            
            if (len(infForm['dni'])==8): #verifico que el dni tenga 8 digitos, simulacion de renaper
                #Generar contraseña random para el usuario
                contra=str(random.randint(100000,999999))
                
                #Busco el vacunatorio actual y lo inicializo con ese
                vac=list(Vacunador.objects.filter(email=request.user.email))
                vacunatorio=vac[int(0)].vacunatorio
                
                codAleatorio=generarCodigoAleatorio()
                Codigos.objects.create(codigo=codAleatorio)
                
                Usuario.objects.create(nombre=infForm['nombre'], apellido=infForm['apellido'], dni=infForm['dni'], fecha_nacimiento=infForm['fecha_nacimiento'], direccion=vacunatorio, email=infForm['email'], contraseña=contra, codigo=codAleatorio)
                #aca se crea un usuario de tipo User para que se guarde en la base de datos y luego poder autenticar de forma correcta
                user=User.objects.create_user(infForm['email'],infForm['email'],contra)
                user.save()
                
                #Aca se saca el turno correspondiente a "vacuna"
                
                ahora = datetime.now()
                #Si uso directamente now.date() y now.time() da error y no guarda nada
                hora_turno= time(hour= ahora.hour, minute= ahora.minute)
                fecha_turno= date(year=ahora.year, month=ahora.month, day= ahora.day )    
                
                hora_turno= time(hour= ahora.hour, minute= ahora.minute)
                
                #if infForm['observaciones'] is not None:
                #    obs=str(infForm['observaciones'])
                turno=Turno(fecha=fecha_turno, hora=hora_turno, vacuna=infForm['vacuna'], usuario_a_vacunar=infForm['dni'], vacunatorio=vacunatorio, estado='Completo')
                turno.save()
                #Turno.objects.create(fecha=hoy.date, hora=hoy.time, vacuna=infForm['vacuna'], usuario_a_vacunar=infForm['dni'], vacunatorio=vacunatorio, estado="Completo", observaciones="Nada")
                #Prueba
                
                #Aca se actualiza el historial del usuario, dependiendo de la vacuna
                
                if infForm['vacuna']  == "Coronavirus":
                    #Vacuna del coronavirus
                    #Depende de las dosis ingresadas, se guarda la fecha de HOY como primera o segunda dosis
                    if infForm['nro_dosis'] == 1:
                        historial_covid=HistorialCovid(usuario=infForm['dni'], cantidad_dosis=infForm['nro_dosis'], fecha_primeradosis=fecha_turno)
                        historial_covid.save()
                        #Se le da el turno de la segunda dosis de aca a "X" meses
                        
                        dia_actual=datetime.now()
                        fecha_turno_2= dia_actual + timedelta(days=90)
                        hora=random.randint(8,15)
                        hora_turno_2= time(hour=hora, minute=45)
                        
                        turno=Turno(fecha=fecha_turno_2, hora=hora_turno_2, vacuna=infForm['vacuna'], usuario_a_vacunar=infForm['dni'], vacunatorio=vacunatorio, estado='Asignado')
                        turno.save()
                        
                    else:
                        historial_covid=HistorialCovid(usuario=infForm['dni'], cantidad_dosis=infForm['nro_dosis'], fecha_segundadosis=fecha_turno)
                        historial_covid.save()
                else:
                    if infForm['vacuna']  == "Gripe":
                        #Vacuna de la gripe
                        historial_gripe=HistorialGripe(usuario=infForm['dni'], fecha_aplicacion_gripe=fecha_turno)
                        historial_gripe.save()
                    else:
                        #Vacuna de la fiebre amarilla
                        historial_fiebre=HistorialFiebreA(usuario=infForm['dni'], fecha_aplicacion_fiebre_a=fecha_turno, si_o_no='si')
                        historial_fiebre.save()
                
                #Envio de email
                mensaje="Se registro tu informacion en VacunAssist! Tu codigo para iniciar sesion es: "+ str(codAleatorio) + " Y su contraseña es: " + str(contra) + ". Le recomendamos cambiar su contraseña." 
                send_mail('Registro exitoso',mensaje,'vacun.assist.cms@hotmail.com', [infForm['email']])
                messages.add_message(request, messages.INFO, 'Se registro el usuario y su turno')
                return render (request, "gestion_vacunador/inicio_vac.html")
            else:
                messages.add_message(request, messages.INFO, 'ERROR dni invalido!')
                return render(request, "gestion_vacunador/agregar_persona.html",{"form":miFormulario})
        else:
            messages.add_message(request, messages.INFO, 'ERROR formulario invalido!')
            return render(request, "gestion_vacunador/agregar_persona.html",{"form":miFormulario})   
    else:
        miFormulario=FormularioRegistroVacunacion()
    return render(request, "gestion_vacunador/agregar_persona.html", {"form": miFormulario})




