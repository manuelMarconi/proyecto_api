# Generated by Django 4.0.4 on 2022-07-05 02:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0026_historialcovid_fecha_primeradosis_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historialcovid',
            name='fecha_primeradosis',
        ),
        migrations.RemoveField(
            model_name='historialcovid',
            name='fecha_segundadosis',
        ),
        migrations.RemoveField(
            model_name='historialcovid',
            name='vacuna_externa_covid_dosis_1',
        ),
        migrations.RemoveField(
            model_name='historialcovid',
            name='vacuna_externa_covid_dosis_2',
        ),
    ]
