from django.contrib import admin

from history.models import CoinTypeContext

from .models import CoinType, Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "iso2", "iso3", "region", "currency")
    search_fields = ("name", "iso2", "iso3")
    list_filter = ("region",)


class CoinTypeContextInline(admin.TabularInline):
    model = CoinTypeContext
    extra = 1


@admin.register(CoinType)
class CoinTypeAdmin(admin.ModelAdmin):
    list_display = ("denomination", "year", "country", "material")
    list_filter = ("country", "year", "material")
    search_fields = ("denomination", "notes")
    inlines = [CoinTypeContextInline]
