# Generated by Django 4.0.4 on 2022-06-06 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0008_historialcovid_fecha_primeradosis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='turno',
            name='observaciones',
            field=models.CharField(blank=True, default='Ninguna observación', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='turno',
            name='estado',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='turno',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='turno',
            name='hora',
            field=models.TimeField(blank=True, null=True),
        ),
    ]