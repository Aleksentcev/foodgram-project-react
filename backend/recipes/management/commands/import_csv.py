from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        for row in DictReader(open('data/ingredients.csv', encoding='UTF-8')):
            name, measurement_unit = row
            ingredient = Ingredient(
                name=name,
                measurement_unit=measurement_unit,
            )
            ingredient.save()
        print('Импорт данных завершен!')
