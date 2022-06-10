from django.db import models


# Create your models here.

centros_vacunacion = (
    ("Zona municipalidad", "51 e/ 10  y 11 nro 770"),
    ("Zona cementerio", "138 e/ 73 y 74 nro 2035"),
    ("Zona terminal de omnibus", "3 e/ 41 y 42 nro 480"),
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
    direccion=models.CharField(max_length=30, choices=centros_vacunacion)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)
    codigo=models.CharField(max_length=4)

    def __str__(self):
        return 'Usuario: %s, %s. DNI: %s. Fecha de nacimiento %s. Vacunatorio: %s. Email: %s' % (self.apellido, self.nombre, self.dni, self.fecha_nacimiento, self.direccion, self.email)

class Turno(models.Model):
    fecha=models.DateField(blank=True, null=True)
    hora=models.TimeField(blank=True, null=True)
    vacuna=models.CharField(max_length=40)
    usuario_a_vacunar=models.CharField(max_length=8)
    #usuario_a_vacunar=models.Usuario() #puede ser un campo de tipo usuario, o un campo de tipo dni 
    vacunatorio=models.CharField(max_length=40, choices=centros_vacunacion)
    estado=models.CharField(max_length=40, choices=estados_turno)
    observaciones=models.CharField(max_length=100, blank=True, null=True, default='Ninguna observación')

    def __str__(self):
        return 'Turno de %s para la vacuna: %s. En el vacunatorio %s, el día %s a la hora %s. Estado: %s' % (self.usuario_a_vacunar, self.vacuna, self.vacunatorio, self.fecha, self.hora, self.estado)


class Codigos(models.Model):
    codigo=models.CharField(max_length=4)

class Vacunador(models.Model):
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    vacunatorio=models.CharField(max_length=30, choices=centros_vacunacion)
    email=models.EmailField()
    contraseña=models.CharField(max_length=60)

    def __str__(self):
        return 'Vacunador: %s, %s. Vacunatorio: %s. Email: %s' % (self.apellido, self.nombre, self.vacunatorio, self.email)


class HistorialCovid(models.Model):
    usuario=models.CharField(max_length=8)
    cantidad_dosis=models.CharField(max_length=10)
    fecha_primeradosis=models.DateField(blank=True, null=True)
    fecha_segundadosis=models.DateField(blank=True, null=True)

    def __str__(self):
        return 'DNI: %s. Cantidad de dosis: %s. Primera dosis: %s. Segunda dosis: %s' % (self.usuario, self.cantidad_dosis, self.fecha_primeradosis, self.fecha_segundadosis)


class HistorialFiebreA(models.Model):
    fecha_aplicacion_fiebre_a=models.DateField(blank=True, null=True)
    usuario=models.CharField(max_length=8)
    si_o_no=models.CharField(max_length=2, null=True)
    
    def __str__(self):
        return 'DNI: %s. Fecha: %s' % (self.usuario, self.fecha_aplicacion_fiebre_a)
 

class HistorialGripe(models.Model):
    fecha_aplicacion_gripe=models.DateField(blank=True, null=True)
    usuario=models.CharField(max_length=8)

    def __str__(self):
        return 'DNI: %s. Fecha: %s' % (self.usuario, self.fecha_aplicacion_gripe)


#Otra opción: historial unificado

class HistorialVacunacion(models.Model):
    usuario=models.CharField(max_length=8)
    vacuna=models.CharField(max_length=20)
    cantidad_dosis_covid=models.CharField(max_length=10, blank=True, null=True)
    fecha_primeradosis_covid=models.DateField(blank=True, null=True)
    fecha_segundadosis_covid=models.DateField(blank=True, null=True)
    fecha_aplicacion_fiebre_a=models.DateField(blank=True, null=True)
    fecha_aplicacion_gripe=models.DateField(blank=True, null=True)


