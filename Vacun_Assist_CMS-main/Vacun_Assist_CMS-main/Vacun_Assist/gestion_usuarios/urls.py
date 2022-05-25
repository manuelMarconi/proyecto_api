from django.urls import path

from .views import inicio, registro, cerrar_sesion, iniciar_sesion, cargar_info_covid, cargar_info_fiebre_a, cargar_info_gripe, modificar_perfil, estatus_turno

urlpatterns = [
    path('', inicio, name= "inicio"),
    path('inicio', inicio, name= "inicio"),
    #path('registro',registro.as_view(), name="registro"),
    path('registro', registro, name="registro"),
    path('iniciar_sesion', iniciar_sesion, name="iniciar_sesion"),
    path('cerrar_sesion', cerrar_sesion, name="cerrar_sesion"),
    path('covid', cargar_info_covid, name='covid'),
    path('fiebre_a', cargar_info_fiebre_a, name='fiebre_a'),
    path('gripe', cargar_info_gripe, name='gripe'),
    path('modificar_perfil', modificar_perfil, name='modificar_perfil'),
    path('estatus_turno', estatus_turno, name='estatus_turno'),

]
