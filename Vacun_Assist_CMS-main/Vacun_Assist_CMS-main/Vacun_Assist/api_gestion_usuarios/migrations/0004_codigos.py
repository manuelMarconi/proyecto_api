# Generated by Django 4.0.4 on 2022-05-28 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0003_alter_usuario_direccion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Codigos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=4)),
            ],
        ),
    ]
