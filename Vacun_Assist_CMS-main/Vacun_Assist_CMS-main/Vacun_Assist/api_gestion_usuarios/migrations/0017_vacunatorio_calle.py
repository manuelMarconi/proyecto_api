# Generated by Django 4.0.4 on 2022-07-02 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0016_delete_historialvacunacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacunatorio',
            name='calle',
            field=models.CharField(default='1', max_length=20),
        ),
    ]
