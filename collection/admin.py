from datetime import date

from django.contrib import admin

from .models import CoinItem, Donor


@admin.action(description="Marcar como avaliado hoje")
def mark_estimated_today(modeladmin, request, queryset):
    queryset.update(estimated_at=date.today())


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "contact")
    search_fields = ("name",)


@admin.register(CoinItem)
class CoinItemAdmin(admin.ModelAdmin):
    list_display = ("coin_type", "condition", "quantity", "origin", "donor", "location", "estimated_value_brl")
    list_filter = ("condition", "origin", "donor", "location")
    actions = [mark_estimated_today]
