# Generated by Django 4.0.4 on 2022-06-03 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0006_vacunador_apellido_vacunador_contraseña_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialCovid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=8)),
                ('cantidad_dosis', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='HistorialFiebreA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_aplicacion_fiebre_a', models.DateField(blank=True, null=True)),
                ('usuario', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='HistorialGripe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_aplicacion_gripe', models.DateField(blank=True, null=True)),
                ('usuario', models.CharField(max_length=8)),
            ],
        ),
        migrations.AlterField(
            model_name='turno',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Asignado', 'Asignado'), ('Completo', 'Completo'), ('Incompleto', 'Incompleto')], max_length=40),
        ),
        migrations.AlterField(
            model_name='turno',
            name='fecha',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='turno',
            name='hora',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='vacunador',
            name='apellido',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='vacunador',
            name='contraseña',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='vacunador',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='vacunador',
            name='nombre',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='vacunador',
            name='vacunatorio',
            field=models.CharField(choices=[('Zona municipalidad', '51 e/ 10  y 11 nro 770'), ('Zona cementerio', '138 e/ 73 y 74 nro 2035'), ('Zona terminal de omnibus', '3 e/ 41 y 42 nro 480')], max_length=30),
        ),
    ]