from django.db import models

from catalog.models import CoinType, Country
from coinsdb.models import SoftDeleteModel


class HistoricalContext(SoftDeleteModel):
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, related_name="historical_contexts")
    title = models.CharField(max_length=200)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    description = models.TextField()
    sources = models.TextField(blank=True)

    def __str__(self):
        return self.title


class CoinTypeContext(models.Model):
    coin_type = models.ForeignKey(CoinType, on_delete=models.CASCADE, related_name="contexts")
    context = models.ForeignKey(HistoricalContext, on_delete=models.CASCADE, related_name="coin_types")
    relation_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.coin_type} ↔ {self.context}"
