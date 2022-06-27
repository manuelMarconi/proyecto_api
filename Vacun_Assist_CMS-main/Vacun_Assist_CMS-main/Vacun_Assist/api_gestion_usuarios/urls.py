from django.urls import path

from .views import agregar_persona, iniciar_sesion_vacunador, inicio, observar_turnos_dia, registro, cerrar_sesion, iniciar_sesion, cargar_info_covid, cargar_info_fiebre_a, cargar_info_gripe, modificar_perfil, estatus_turno, sacar_turno_fiebre_amarilla, ver_historial, iniciar_sesion_vacunador, ver_historial, sacar_turno_fiebre_amarilla, observar_turnos_dia, agregar_persona, mi_perfil, inicio_vacunador, mi_perfil_vacunador, listado_turnos, mostrar_turno, inicio_admin, informe_cantidad_persona, informe_covid, informe_fiebre_a, informe_personas_registradas, ver_historial_admin, modificar_nombre_vacunatorio, asignar_turno_covid, asignar_turno_fiebre_a, inicio_administrador, agregar_vacuna, ver_historial_vac

urlpatterns = [
    ###
    #DEMO 1
    ###
    path('', inicio, name= "inicio"),
    path('inicio', inicio, name= "inicio"),
    #path('registro',registro.as_view(), name="registro"),
    path('registrarse', registro, name="registro"),
    path('iniciar_sesion', iniciar_sesion, name="iniciar_sesion"),
    path('cerrar_sesion', cerrar_sesion, name="cerrar_sesion"),
    path('covid', cargar_info_covid, name='covid'),
    path('fiebre_a', cargar_info_fiebre_a, name='fiebre_a'),
    path('gripe', cargar_info_gripe, name='gripe'),
    path('modificar_perfil', modificar_perfil, name='modificar_perfil'),
    path('estatus_turno', estatus_turno, name='estatus_turno'),
    ###
    #DEMO 2
    ###
    path('inicio_vacunador', iniciar_sesion_vacunador, name='inicio_vacunador'),
    path('inicio_vac', inicio_vacunador, name='inicio_vac'),
    path('historial',ver_historial , name='historial'),
    path('ver_historial_vac',ver_historial_vac , name='ver_historial_vac'),
    path('turno_fiebre_a', sacar_turno_fiebre_amarilla, name='turno_fiebre_a'),
    path('turnos_dia', observar_turnos_dia, name='turnos_dia'),
    path('mostrar_turno', mostrar_turno, name='mostrar_turno'),
 #   path('turnos_dia', listado_turnos, name='turnos_dia'),
 #   path('marcar_turno', marcar_turno, name='marcar_turno'),
    path('agregar_persona',agregar_persona, name='agregar_persona'),
    path('agregar_vacuna',agregar_vacuna, name='agregar_vacuna'),
    path('mi_perfil', mi_perfil, name='mi_perfil'),

    path('mi_perfil_vacunador', mi_perfil_vacunador, name='mi_perfil_vacunador'),
    ###
    #DEMO 3
    ###
    path('inicio_administrador', inicio_administrador ,name='inicio_administrador'),
    path('inicio_admin', inicio_admin ,name='inicio_admin'),
    path('informe_cant_persona', informe_cantidad_persona,name='informe_cant_persona'),
    path('informe_covid', informe_covid,name='informe_covid'),
    path('informe_fiebre', informe_fiebre_a ,name='informe_fiebre'),
    path('info_personas', informe_personas_registradas,name='info_personas'),
    path('historial_admin', ver_historial_admin ,name='historial_admin'),
    path('mod_nombre', modificar_nombre_vacunatorio,name='mod_nombre'),
    path('asignar_turno_covid', asignar_turno_covid ,name='asignar_turno_covid'),
    path('asignar_turno_fiebre', asignar_turno_fiebre_a ,name='asignar_turno_fiebre'),

]