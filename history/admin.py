from django.contrib import admin

from .models import HistoricalContext


@admin.register(HistoricalContext)
class HistoricalContextAdmin(admin.ModelAdmin):
    list_filter = ("country",)
    search_fields = ("title",)
