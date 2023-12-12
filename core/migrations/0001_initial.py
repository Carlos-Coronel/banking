# Generated by Django 4.2.7 on 2023-12-12 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auditoria',
            fields=[
                ('nro', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('ip', models.GenericIPAddressField()),
                ('servidor', models.CharField(max_length=255)),
                ('evento', models.CharField(choices=[('login', 'Inicio de sesión'), ('transaccion', 'Transacción'), ('retiro', 'Retiro'), ('deposito', 'Deposito')], max_length=20)),
                ('nivel', models.CharField(choices=[('normal', 'Normal'), ('medio', 'Medio'), ('alto', 'Alto')], max_length=20)),
                ('mac', models.CharField(max_length=17)),
                ('origin', models.GenericIPAddressField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
