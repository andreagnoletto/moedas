import csv
import json

from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from coinsdb.ai import ask_openai, has_api_key
from collection.models import CoinItem

from .forms import CoinTypeForm
from .models import CoinType, Country


def country_list(request):
    qs = Country.objects.annotate(coin_count=Count("coin_types"))
    q = request.GET.get("q", "").strip()
    region = request.GET.get("region", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)
    if region:
        qs = qs.filter(region=region)

    regions = Country.objects.values_list("region", flat=True).distinct().order_by("region")

    ctx = {"countries": qs, "q": q, "region": region, "regions": regions}
    if request.headers.get("HX-Request"):
        return render(request, "catalog/country_table.html", ctx)
    return render(request, "catalog/country_list.html", ctx)


COINTYPE_SORT_FIELDS = {
    "id": "pk",
    "denominacao": "denomination",
    "ano": "year",
    "pais": "country__name",
    "material": "material",
    "colecao": "item_count",
    "valor": "total_value",
}


def cointype_list(request):
    qs = CoinType.objects.select_related("country").annotate(
        item_count=Sum("items__quantity"),
        total_value=Sum("items__estimated_value_brl"),
    )
    q = request.GET.get("q", "").strip()
    country_id = request.GET.get("country", "").strip()
    material = request.GET.get("material", "").strip()
    if q:
        qs = qs.filter(denomination__icontains=q)
    if country_id:
        qs = qs.filter(country_id=country_id)
    if material:
        qs = qs.filter(material__icontains=material)

    sort = request.GET.get("sort", "ano").strip()
    desc = sort.startswith("-")
    sort_key = sort.lstrip("-")
    db_field = COINTYPE_SORT_FIELDS.get(sort_key, "year")
    order = f"-{db_field}" if desc else db_field
    qs = qs.order_by(order)

    collection_total_qty = sum(ct.item_count or 0 for ct in qs)
    collection_total_value = sum(ct.total_value or 0 for ct in qs)

    countries = Country.objects.filter(coin_types__isnull=False).distinct().order_by("name")
    materials = CoinType.objects.values_list("material", flat=True).distinct().order_by("material")

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page", 1))

    ctx = {
        "cointypes": page, "page": page,
        "q": q, "country_id": country_id, "material": material,
        "countries": countries, "materials": materials, "sort": sort,
        "collection_total_qty": collection_total_qty, "collection_total_value": collection_total_value,
    }
    if request.headers.get("HX-Request"):
        return render(request, "catalog/cointype_table.html", ctx)
    return render(request, "catalog/cointype_list.html", ctx)


def _cointype_form_ctx(form, title):
    return {"form": form, "title": title, "back_url": "/catalogo/", "has_openai_key": has_api_key()}


def cointype_create(request):
    form = CoinTypeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        return redirect(f"/colecao/novo/?coin_type={obj.pk}")
    return render(request, "catalog/cointype_form.html", _cointype_form_ctx(form, "Novo tipo de moeda"))


def cointype_edit(request, pk):
    obj = CoinType.objects.get(pk=pk)
    form = CoinTypeForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("cointype-list")
    return render(request, "catalog/cointype_form.html", _cointype_form_ctx(form, f"Editar {obj}"))


def cointype_delete(request, pk):
    obj = CoinType.objects.get(pk=pk)
    if request.method == "POST":
        obj.soft_delete()
        return redirect("cointype-list")
    return render(request, "_confirm_delete.html", {"object": obj, "back_url": "/catalogo/"})


COINTYPE_SYSTEM_PROMPT = """Você é um especialista em numismática.
Dado uma moeda (denominação, ano, país), preencha os dados técnicos faltantes.
Responda APENAS com JSON válido contendo SOMENTE os campos que você consegue inferir:
{
  "material": "ex: Bronze, Aço Inox, Prata .900",
  "diameter_mm": 25.0,
  "weight_g": 7.5,
  "mintage": 1000000,
  "notes": "Informações relevantes sobre a moeda em português brasileiro"
}
Omita campos que não tiver certeza. Valores numéricos sem aspas.
"""


@require_POST
def cointype_fill_ai(request):
    if not has_api_key():
        return JsonResponse({"error": "OPENAI_API_KEY não configurada no .env"}, status=400)

    data = json.loads(request.body)
    denomination = data.get("denomination", "").strip()
    year = data.get("year", "").strip()
    country_name = data.get("country_name", "").strip()
    if not denomination or not year:
        return JsonResponse({"error": "Preencha ao menos denominação e ano"}, status=400)

    prompt = f"Moeda: {denomination}, Ano: {year}"
    if country_name:
        prompt += f", País: {country_name}"

    try:
        result = ask_openai(COINTYPE_SYSTEM_PROMPT, prompt)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def export_cointypes(request):
    ids = request.GET.get("ids", "").strip()
    qs = CoinType.objects.select_related("country").order_by("year")
    if ids:
        qs = qs.filter(pk__in=ids.split(","))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="catalogo.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Denominação", "Ano", "País", "Material", "Diâmetro mm", "Peso g", "Tiragem", "Notas"])
    for ct in qs:
        writer.writerow([ct.pk, ct.denomination, ct.year, ct.country.name, ct.material,
                         ct.diameter_mm or "", ct.weight_g or "", ct.mintage or "", ct.notes])
    return response
