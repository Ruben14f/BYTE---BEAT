# Generated by Django 5.2 on 2025-04-20 03:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart', '0006_alter_cartproduct_quantity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('CREATED', 'Creado'), ('PAYED', 'Pagado'), ('PREPARING', 'Preparando'), ('SHIPPED', 'Enviado'), ('READY_FOR_PICKUP', 'Listo para retirar'), ('DELIVERED', 'Entregado'), ('CANCELED', 'Cancelado')], default='CREATED', max_length=40)),
                ('delivery_method', models.CharField(choices=[('SHIPPING', 'Envío'), ('PICKUP', 'Retiro')], max_length=40)),
                ('envio_total', models.DecimalField(decimal_places=2, default=3990, max_digits=9)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('create_at', models.DateField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.cart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
