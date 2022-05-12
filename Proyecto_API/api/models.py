from django.db import models

# Create your models here.
class Company(models.Model):
	name=models.CharField(max_length=50)
	website=models.URLField(max_length=100)
	foundation=models.PositiveIntegerField()

class UsuarioRandom(models.Model):
	name=models.CharField(max_length=20)
	dni=models.PositiveIntegerField()
	zona=models.CharField(max_length=20)
