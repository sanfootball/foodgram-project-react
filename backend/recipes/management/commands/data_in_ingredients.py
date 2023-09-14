import csv
import sqlite3

from django.core.management import BaseCommand

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Извлечение данных из таблицы
cursor.execute("SELECT * FROM recipes_ingredient;")
data = cursor.fetchall()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open(
            'C:/Users/Админ/Dev/foodgram-project-react/data/ingredients.csv',
            'a',
            newline='',
            encoding='utf-8',
        ) as file:
            writer = csv.writer(file)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(data)


cursor.close()
conn.close()
