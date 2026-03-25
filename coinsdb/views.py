from django.db.models import Count, Sum
from django.shortcuts import render

from catalog.models import CoinType, Country
from collection.models import CoinItem


def dashboard(request):
    total_items = CoinItem.objects.aggregate(t=Sum("quantity"))["t"] or 0
    total_value = CoinItem.objects.aggregate(t=Sum("estimated_value_brl"))["t"] or 0

    stats = {
        "countries": Country.objects.count(),
        "coin_types": CoinType.objects.count(),
        "total_items": total_items,
        "total_value": total_value,
    }

    by_condition = (
        CoinItem.objects.values("condition")
        .annotate(total=Sum("quantity"))
        .order_by("-total")
    )
    max_qty = max((c["total"] for c in by_condition), default=1)
    by_condition = [
        {**c, "pct": round(c["total"] / max_qty * 100)} for c in by_condition
    ]

    top_countries = (
        CoinType.objects.values("country__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )

    recent_items = CoinItem.objects.select_related("coin_type__country").order_by("-created_at")[:10]

    return render(request, "dashboard.html", {
        "stats": stats,
        "by_condition": by_condition,
        "top_countries": top_countries,
        "recent_items": recent_items,
    })
