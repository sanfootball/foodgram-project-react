import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из csv файла в БД.'

    def handle(self, *args, **kwargs):
        data_path = (
            'C:/Users/Админ/Dev/foodgram-project-react/data/ingredients.csv')
        with open(
            data_path,
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))

        file.close()
