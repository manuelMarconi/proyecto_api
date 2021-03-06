from timeit import default_timer
from django.db import models


# Create your models here.

centros_vacunacion = (
    ("Zona municipalidad", "51 e/ 10  y 11 nro 770"),
    ("Zona cementerio", "138 e/ 73 y 74 nro 2035"),
    ("Zona terminal de omnibus", "3 e/ 41 y 42 nro 480"),
)
nombre_vacunacion = (
    ("Zona municipalidad", "municipalidad_00"),
    ("Zona cementerio", "cementerio_00"),
    ("Zona terminal de omnibus", "terminal_00"),
)

estados_turno = (
    ("Pendiente", "Pendiente"),
    ("Asignado", "Asignado"),
    ("Completo","Completo"),
    ("Incompleto","Incompleto"),
)

class Usuario (models.Model):
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    dni=models.CharField(max_length=8)
    fecha_nacimiento=models.DateField()
    #direccion=models.CharField(max_length=30, choices=centros_vacunacion)
    direccion=models.CharField(max_length=30)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)
    codigo=models.CharField(max_length=4)
    fecha_registro=models.DateField(blank=True, null=True)

    def __str__(self):
        return 'Usuario: %s, %s. DNI: %s. Fecha de nacimiento %s. Vacunatorio: %s. Email: %s' % (self.apellido, self.nombre, self.dni, self.fecha_nacimiento, self.direccion, self.email)

class Turno(models.Model):
    fecha=models.DateField(blank=True, null=True)
    hora=models.TimeField(blank=True, null=True)
    vacuna=models.CharField(max_length=40)
    usuario_a_vacunar=models.CharField(max_length=8)
    nombre_usuario=models.CharField(max_length=50)
    apellido_usuario=models.CharField(max_length=50)
    dosis=models.CharField(max_length=10, blank=True, null=True)
    #vacunatorio=models.CharField(max_length=40, choices=centros_vacunacion)
    vacunatorio=models.CharField(max_length=40)
    estado=models.CharField(max_length=40, choices=estados_turno)
    observaciones=models.CharField(max_length=100, blank=True, null=True, default='Ninguna observación')

    def __str__(self):
        return 'Turno de %s para la vacuna: %s. En el vacunatorio %s, el día %s a la hora %s. Estado: %s' % (self.usuario_a_vacunar, self.vacuna, self.vacunatorio, self.fecha, self.hora, self.estado)


class Codigos(models.Model):
    codigo=models.CharField(max_length=4)
    
    def __str__(self):
        return 'Codigo: %s' % self.codigo

class Vacunador(models.Model):
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    #vacunatorio=models.CharField(max_length=30, choices=centros_vacunacion)
    vacunatorio=models.CharField(max_length=30)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)

    def __str__(self):
        return 'Vacunador: %s, %s. Vacunatorio: %s. Email: %s' % (self.apellido, self.nombre, self.vacunatorio, self.email)

class NombreVacunador(models.Model):
    vacunatorio=models.CharField(max_length=30, choices=centros_vacunacion)
    nuevo_nombre=models.CharField(max_length=30)

class HistorialCovid(models.Model):
    usuario=models.CharField(max_length=8)
    cantidad_dosis=models.CharField(max_length=10)
    nombre_usuario=models.CharField(max_length=50)
    apellido_usuario=models.CharField(max_length=50)
#    vacuna_externa_covid=models.BooleanField(null=True)
    fecha_primeradosis=models.DateField(blank=True, null=True)
    fecha_segundadosis=models.DateField(blank=True, null=True)
    vacuna_externa_covid_dosis_1=models.BooleanField(null=True, blank=True)
    vacuna_externa_covid_dosis_2=models.BooleanField(null=True, blank= True)

    def __str__(self):
        return 'DNI: %s. Cantidad de dosis: %s. Nombre: %s, %s' % (self.usuario, self.cantidad_dosis, self.nombre_usuario, self.apellido_usuario)


class HistorialFiebreA(models.Model):
    fecha_aplicacion_fiebre_a=models.DateField(blank=True, null=True)
    usuario=models.CharField(max_length=8)
    si_o_no=models.CharField(max_length=2, null=True)
    vacuna_externa_fiebre=models.BooleanField(null=True)
    nombre_usuario=models.CharField(max_length=50)
    apellido_usuario=models.CharField(max_length=50)
    
    
    def __str__(self):
        return 'DNI: %s. Fecha: %s. Nombre: %s, %s' % (self.usuario, self.fecha_aplicacion_fiebre_a, self.nombre_usuario, self.apellido_usuario)
 

class HistorialGripe(models.Model):
    fecha_aplicacion_gripe=models.DateField(blank=True, null=True)
    vacuna_externa_gripe=models.BooleanField(null=True)
    usuario=models.CharField(max_length=8)
    nombre_usuario=models.CharField(max_length=50)
    apellido_usuario=models.CharField(max_length=50)

    def __str__(self):
        return 'DNI: %s. Fecha: %s.  Nombre: %s, %s' % (self.usuario, self.fecha_aplicacion_gripe, self.nombre_usuario, self.apellido_usuario)


class Administrador(models.Model):
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)


class Vacunatorio(models.Model):
    nombre=models.CharField(max_length=60)
    direccion=models.CharField(max_length=60)

    def __str__(self):
        return 'Nombre: %s. Direccion: %s' % (self.nombre, self.direccion)
 


