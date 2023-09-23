# Generated by Django 3.2.19 on 2023-09-23 14:07

from django.db import migrations, models
import recipes.utils


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230818_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='Ед. измерения.'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to=recipes.utils.upload_to, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, verbose_name='Цвет тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Имя тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, verbose_name='slug'),
        ),
    ]
