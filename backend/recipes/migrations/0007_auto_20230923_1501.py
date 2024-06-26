# Generated by Django 3.2.19 on 2023-09-23 15:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20230923_1407'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ['-pub_date', 'name'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Цвет должен быть в формате HEX (например, #FF0000)', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цвет тега'),
        ),
    ]
