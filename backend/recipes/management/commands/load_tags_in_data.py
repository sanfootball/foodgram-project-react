import csv

from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка тегов из csv файла'

    def handle(self, *args, **kwargs):
        data_path = (
            'C:/Users/Админ/Dev/foodgram-project-react/data/tags.csv')
        Tag.objects.all().delete()
        with open(
            data_path,
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Tag.objects.bulk_create(
                Tag(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS('Все теги загружены!'))

        file.close()
