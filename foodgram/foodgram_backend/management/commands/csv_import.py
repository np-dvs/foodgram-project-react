from csv import DictReader

from django.core.management import BaseCommand

from foodgram_backend.models import Ingredient

models = {
    Ingredient: 'ingredients.csv'
}


class Command(BaseCommand):

    def handle(self, *args, **options):
        for model, csv_file in models.items():
            with open('data/' + csv_file, encoding='utf-8-sig') as file:
                rows = DictReader(file)
                records = [model(**row) for row in rows]
                model.objects.bulk_create(records)
