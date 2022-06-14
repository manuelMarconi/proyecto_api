from django.urls import path

from .views import agregar_persona, iniciar_sesion_vacunador, inicio, observar_turnos_dia, registro, cerrar_sesion, iniciar_sesion, cargar_info_covid, cargar_info_fiebre_a, cargar_info_gripe, modificar_perfil, estatus_turno, sacar_turno_fiebre_amarilla, ver_historial, iniciar_sesion_vacunador, ver_historial, sacar_turno_fiebre_amarilla, observar_turnos_dia, agregar_persona, mi_perfil, inicio_vacunador, mi_perfil_vacunador, listado_turnos

urlpatterns = [
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
    path('inicio_vacunador', iniciar_sesion_vacunador, name='inicio_vacunador'),
    path('historial',ver_historial , name='historial'),
    path('turno_fiebre_a', sacar_turno_fiebre_amarilla, name='turno_fiebre_a'),
    #path('turnos_dia', observar_turnos_dia, name='turnos_dia'),
    path('turnos_dia', listado_turnos, name='turnos_dia'),
 #   path('marcar_turno', marcar_turno, name='marcar_turno'),
    path('agregar_persona',agregar_persona, name='agregar_persona'),
    path('mi_perfil', mi_perfil, name='mi_perfil'),
    path('inicio_vac', inicio_vacunador, name='inicio_vac'),
    path('mi_perfil_vacunador', mi_perfil_vacunador, name='mi_perfil_vacunador'),

]