import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open('data/ingredients.csv', encoding='UTF-8') as file:
            for row in csv.reader(file):
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )
            print('Импорт данных завершен!')
