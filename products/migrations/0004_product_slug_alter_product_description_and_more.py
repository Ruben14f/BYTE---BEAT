# Generated by Django 5.2 on 2025-04-13 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_brand_description_remove_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default='', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='main_image',
            field=models.ImageField(blank=True, default='', upload_to='products/images/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
