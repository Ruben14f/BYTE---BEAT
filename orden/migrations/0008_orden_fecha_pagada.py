# Generated by Django 5.2 on 2025-05-02 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orden', '0007_ordenproducto'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden',
            name='fecha_pagada',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
