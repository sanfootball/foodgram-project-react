import csv

from backend_foodgram.settings import CSV_DIR
from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка тегов из csv файла'

    def handle(self, *args, **kwargs):
        with open(
            f'{CSV_DIR}/tags.csv',
            'r',
            newline='',
            encoding='utf-8'
        ) as csv_file:
            rows = csv.reader(csv_file)
            for row in rows:
                name, slug = row
                Tag.objects.get_or_create(
                    name=name,
                    slug=slug)

        self.stdout.write(self.style.SUCCESS('Все теги загружены!'))

        csv_file.close()
