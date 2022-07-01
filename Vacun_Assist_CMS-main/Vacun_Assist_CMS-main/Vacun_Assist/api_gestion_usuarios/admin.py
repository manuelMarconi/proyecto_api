from django.contrib import admin
from api_gestion_usuarios.models import Usuario, Turno, Vacunador, Codigos, HistorialGripe, HistorialFiebreA, HistorialCovid, Administrador, NombreVacunador, Vacunatorio

# Register your models here.


admin.site.register(Usuario)
admin.site.register(Turno)
admin.site.register(Vacunador)
admin.site.register(Codigos)
admin.site.register(HistorialCovid)
admin.site.register(HistorialFiebreA)
admin.site.register(HistorialGripe)
admin.site.register(Administrador)
admin.site.register(NombreVacunador)
admin.site.register(Vacunatorio)


