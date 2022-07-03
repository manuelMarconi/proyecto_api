# Generated by Django 4.0.4 on 2022-07-03 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0023_usuario_fecha_registro'),
    ]

    operations = [
        migrations.AddField(
            model_name='historialcovid',
            name='fecha_primeradosis',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historialcovid',
            name='fecha_segundadosis',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historialcovid',
            name='vacuna_externa_covid_dosis_1',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='historialcovid',
            name='vacuna_externa_covid_dosis_2',
            field=models.BooleanField(null=True),
        ),
    ]
