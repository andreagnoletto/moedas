import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.models import Country

CSV_PATH = Path("data/csc/countries.csv")

FIELD_MAP = {
    "name": "name",
    "iso2": "iso2",
    "iso3": "iso3",
    "capital": "capital",
    "currency": "currency",
    "currency_name": "currency_name",
    "currency_symbol": "currency_symbol",
    "region": "region",
    "subregion": "subregion",
    "timezones": "timezones_raw",
    "wikiDataId": "wikidata_id",
}


def safe_decimal(value):
    try:
        return Decimal(value) if value else None
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = "Importa países a partir de data/csc/countries.csv"

    def handle(self, *args, **options):
        created = updated = 0
        with open(CSV_PATH, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                defaults = {model_field: row.get(csv_col, "").strip() for csv_col, model_field in FIELD_MAP.items() if csv_col != "iso3"}
                defaults["latitude"] = safe_decimal(row.get("latitude"))
                defaults["longitude"] = safe_decimal(row.get("longitude"))

                _, is_new = Country.objects.update_or_create(
                    iso3=row["iso3"].strip(),
                    defaults=defaults,
                )
                if is_new:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"{created} criados, {updated} atualizados"))
