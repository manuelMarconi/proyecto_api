# Generated by Django 4.0.4 on 2022-06-24 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0010_historialvacunacion_historialfiebrea_si_o_no_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Administrador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('apellido', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('contraseña', models.CharField(max_length=60)),
            ],
        ),
    ]
