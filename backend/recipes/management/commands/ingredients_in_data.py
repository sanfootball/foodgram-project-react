import csv

from backend_foodgram.settings import CSV_DIR
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из csv файла в БД.'

    def handle(self, *args, **kwargs):
        with open(
            f'{CSV_DIR}/ingredients.csv',
            newline='',
            encoding='utf-8'
        ) as csv_file:
            rows = csv.reader(csv_file)
            for row in rows:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit)

        self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))

        csv_file.close()
