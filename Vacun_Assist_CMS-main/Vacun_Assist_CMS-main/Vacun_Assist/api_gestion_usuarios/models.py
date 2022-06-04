from django.db import models


# Create your models here.

centros_vacunacion = (
    ("Zona municipalidad", "51 e/ 10  y 11 nro 770"),
    ("Zona cementerio", "138 e/ 73 y 74 nro 2035"),
    ("Zona terminal de omnibus", "3 e/ 41 y 42 nro 480"),
)

class Usuario (models.Model):
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    dni=models.CharField(max_length=8)
    fecha_nacimiento=models.DateField()
    direccion=models.CharField(max_length=30, choices=centros_vacunacion)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)
    codigo=models.CharField(max_length=4)

class Turno(models.Model):
    fecha=models.DateField(blank=True, null=True)
    hora=models.TimeField(blank=True, null=True)
    vacuna=models.CharField(max_length=40)
    usuario_a_vacunar=models.CharField(max_length=8)
    #usuario_a_vacunar=models.Usuario() #puede ser un campo de tipo usuario, o un campo de tipo dni 
    vacunatorio=models.CharField(max_length=40)
    estado=models.CharField(max_length=40)
    observaciones=models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return 'Turno de %s para la vacuna: %s. En el vacunatorio %s, el día %s a la hora %s' % (self.usuario_a_vacunar, self.vacuna, self.vacunatorio, self.fecha, self.hora)


class Codigos(models.Model):
    codigo=models.CharField(max_length=4)

class Vacunador(models.Model):
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    vacunatorio=models.CharField(max_length=30, choices=centros_vacunacion)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)


class HistorialCovid(models.Model):
    usuario=models.CharField(max_length=8)
    cantidad_dosis=models.CharField(max_length=10)
    fecha_primeradosis=models.DateField(blank=True, null=True)
    fecha_segundadosis=models.DateField(blank=True, null=True)


class HistorialFiebreA(models.Model):
    fecha_aplicacion_fiebre_a=models.DateField(blank=True, null=True)
    usuario=models.CharField(max_length=8)


class HistorialGripe(models.Model):
    fecha_aplicacion_gripe=models.DateField(blank=True, null=True)
    usuario=models.CharField(max_length=8)






