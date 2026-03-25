from django.db import models

from coinsdb.models import SoftDeleteModel


class Country(models.Model):
    name = models.CharField(max_length=100)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3, unique=True)
    capital = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    currency_name = models.CharField(max_length=100, blank=True)
    currency_symbol = models.CharField(max_length=10, blank=True)
    region = models.CharField(max_length=100, blank=True)
    subregion = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timezones_raw = models.TextField(blank=True)
    wikidata_id = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.iso3})"


class CoinType(SoftDeleteModel):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="coin_types")
    denomination = models.CharField(max_length=100)
    year = models.IntegerField()
    material = models.CharField(max_length=100, blank=True)
    diameter_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    weight_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    mintage = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [("country", "denomination", "year")]
        ordering = ["country", "year", "denomination"]

    def __str__(self):
        return f"{self.denomination} ({self.year}) - {self.country.name}"
