# Generated by Django 5.2 on 2025-05-02 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orden', '0005_alter_orderaddress_ciudad'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden',
            name='token_ws',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
