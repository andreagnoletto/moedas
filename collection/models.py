from django.db import models

from catalog.models import CoinType
from coinsdb.models import SoftDeleteModel


class Donor(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)
    contact = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CoinItem(SoftDeleteModel):
    class Condition(models.TextChoices):
        BC = "BC", "Bem Conservada"
        MBC = "MBC", "Muito Bem Conservada"
        SOB = "SOB", "Soberba"
        FC = "FC", "Flor de Cunho"
        UNC = "UNC", "Uncirculated"

    class Origin(models.TextChoices):
        COMPRA = "compra", "Compra"
        DOACAO = "doacao", "Doação"
        TROCA = "troca", "Troca"
        OUTRO = "outro", "Outro"

    coin_type = models.ForeignKey(CoinType, on_delete=models.PROTECT, related_name="items")
    condition = models.CharField(max_length=3, choices=Condition.choices)
    quantity = models.IntegerField(default=1)
    origin = models.CharField(max_length=10, choices=Origin.choices, default=Origin.OUTRO)
    donor = models.ForeignKey(Donor, null=True, blank=True, on_delete=models.SET_NULL, related_name="donated_items")
    acquired_at = models.DateField(null=True, blank=True)
    cost_brl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_value_brl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_at = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.coin_type} - {self.condition}"
