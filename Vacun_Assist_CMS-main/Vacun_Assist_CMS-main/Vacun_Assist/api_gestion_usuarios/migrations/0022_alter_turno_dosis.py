# Generated by Django 4.0.4 on 2022-07-03 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_gestion_usuarios', '0021_turno_dosis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turno',
            name='dosis',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
