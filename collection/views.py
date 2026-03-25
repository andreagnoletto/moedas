import csv
import json

from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from coinsdb.ai import ask_openai, has_api_key

from .forms import CoinItemForm, DonorForm
from .models import CoinItem, Donor


COINITEM_SORT_FIELDS = {
    "id": "coin_type__pk",
    "moeda": "coin_type__denomination",
    "ano": "coin_type__year",
    "pais": "coin_type__country__name",
    "conservacao": "condition",
    "qtd": "quantity",
    "custo": "cost_brl",
    "valor": "estimated_value_brl",
}


def coinitem_list(request):
    qs = CoinItem.objects.select_related("coin_type__country", "donor")
    condition = request.GET.get("condition", "").strip()
    location = request.GET.get("location", "").strip()
    q = request.GET.get("q", "").strip()
    if condition:
        qs = qs.filter(condition=condition)
    if location:
        qs = qs.filter(location__icontains=location)
    if q:
        qs = qs.filter(coin_type__denomination__icontains=q)

    sort = request.GET.get("sort", "ano").strip()
    desc = sort.startswith("-")
    sort_key = sort.lstrip("-")
    db_field = COINITEM_SORT_FIELDS.get(sort_key, "coin_type__year")
    order = f"-{db_field}" if desc else db_field
    qs = qs.order_by(order)

    total_qty = qs.aggregate(t=Sum("quantity"))["t"] or 0
    total_value = qs.aggregate(t=Sum("estimated_value_brl"))["t"] or 0
    locations = CoinItem.objects.values_list("location", flat=True).distinct().order_by("location")

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page", 1))

    ctx = {
        "items": page,
        "page": page,
        "condition": condition,
        "location": location,
        "q": q,
        "sort": sort,
        "total_qty": total_qty,
        "total_value": total_value,
        "conditions": CoinItem.Condition.choices,
        "locations": locations,
        "has_openai_key": has_api_key(),
    }
    if request.headers.get("HX-Request"):
        return render(request, "collection/coinitem_table.html", ctx)
    return render(request, "collection/coinitem_list.html", ctx)


def coinitem_create(request):
    initial = {}
    coin_type_id = request.GET.get("coin_type")
    if coin_type_id:
        initial["coin_type"] = coin_type_id
    form = CoinItemForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("cointype-list")
    return render(request, "collection/coinitem_form.html", {
        "form": form, "title": "Adicionar à coleção", "back_url": "/catalogo/",
        "has_openai_key": has_api_key(),
    })


def coinitem_edit(request, pk):
    obj = CoinItem.objects.get(pk=pk)
    back_url = request.GET.get("next", request.META.get("HTTP_REFERER", "/colecao/"))
    form = CoinItemForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(request.POST.get("next", "/colecao/"))
    return render(request, "collection/coinitem_form.html", {
        "form": form, "title": f"Editar {obj}", "back_url": back_url,
        "has_openai_key": has_api_key(),
    })


def coinitem_delete(request, pk):
    obj = CoinItem.objects.get(pk=pk)
    back_url = request.GET.get("next", request.META.get("HTTP_REFERER", "/colecao/"))
    if request.method == "POST":
        obj.soft_delete()
        return redirect(request.POST.get("next", "/colecao/"))
    return render(request, "_confirm_delete.html", {"object": obj, "back_url": back_url})


VALUATION_SYSTEM_PROMPT = """Você é um numismata avaliador profissional brasileiro.
Receba uma lista de moedas de uma coleção com denominação, ano, país, material, conservação e quantidade.
Estime o valor de mercado em Reais (R$) de cada item e o total da coleção.

Responda APENAS com JSON válido:
{
  "items": [
    {"denomination": "...", "year": 1994, "condition": "MBC", "qty": 1, "unit_value_brl": 15.00, "reasoning": "Breve justificativa"}
  ],
  "total_brl": 123.45,
  "notes": "Observações gerais sobre a avaliação"
}
Valores em R$ (reais brasileiros). Se não tiver certeza, dê uma faixa e use o valor médio.
"""

SINGLE_VALUATION_PROMPT = """Você é um numismata avaliador profissional brasileiro.
Dada uma moeda com denominação, ano, país, material e conservação, estime o valor de mercado em R$.
Responda APENAS com JSON válido:
{"estimated_value_brl": 15.00, "reasoning": "Breve justificativa da avaliação"}
"""


@require_POST
def estimate_collection_value(request):
    if not has_api_key():
        return JsonResponse({"error": "OPENAI_API_KEY não configurada no .env"}, status=400)

    items = CoinItem.objects.select_related("coin_type__country").order_by("coin_type__year")
    if not items.exists():
        return JsonResponse({"error": "Coleção vazia"}, status=400)

    lines = []
    for item in items:
        ct = item.coin_type
        lines.append(f"- {ct.denomination} ({ct.year}), {ct.country.name}, {ct.material or '?'}, conservação {item.condition}, qtd {item.quantity}")

    prompt = "Avalie esta coleção de moedas:\n" + "\n".join(lines)

    try:
        result = ask_openai(VALUATION_SYSTEM_PROMPT, prompt)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def estimate_item_value(request):
    if not has_api_key():
        return JsonResponse({"error": "OPENAI_API_KEY não configurada no .env"}, status=400)

    data = json.loads(request.body)
    denomination = data.get("denomination", "")
    year = data.get("year", "")
    country = data.get("country", "")
    material = data.get("material", "")
    condition = data.get("condition", "")

    if not denomination or not year:
        return JsonResponse({"error": "Dados insuficientes"}, status=400)

    prompt = f"Moeda: {denomination} ({year}), {country}, {material or '?'}, conservação {condition}"

    try:
        result = ask_openai(SINGLE_VALUATION_PROMPT, prompt)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def export_coinitems(request):
    ids = request.GET.get("ids", "").strip()
    qs = CoinItem.objects.select_related("coin_type__country", "donor").order_by("coin_type__year")
    if ids:
        qs = qs.filter(pk__in=ids.split(","))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="colecao.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "ID Tipo", "Denominação", "Ano", "País", "Material",
        "Conservação", "Quantidade", "Origem", "Doador", "Custo (R$)",
        "Valor Estimado (R$)", "Avaliado em", "Local", "Adquirido em", "Notas",
    ])
    for item in qs:
        ct = item.coin_type
        writer.writerow([
            ct.pk, ct.denomination, ct.year, ct.country.name, ct.material,
            item.condition, item.quantity,
            item.get_origin_display(), item.donor.name if item.donor else "",
            item.cost_brl or "", item.estimated_value_brl or "",
            item.estimated_at or "", item.location, item.acquired_at or "", item.notes,
        ])
    return response


def donor_list(request):
    donors = Donor.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        donors = donors.filter(name__icontains=q)
    ctx = {"donors": donors, "q": q}
    if request.headers.get("HX-Request"):
        return render(request, "collection/donor_table.html", ctx)
    return render(request, "collection/donor_list.html", ctx)


def donor_create(request):
    form = DonorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("donor-list")
    return render(request, "_form.html", {"form": form, "title": "Novo doador", "back_url": "/doadores/"})


def donor_edit(request, pk):
    obj = Donor.objects.get(pk=pk)
    form = DonorForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("donor-list")
    return render(request, "_form.html", {"form": form, "title": f"Editar {obj}", "back_url": "/doadores/"})


def donor_delete(request, pk):
    obj = Donor.objects.get(pk=pk)
    if request.method == "POST":
        obj.soft_delete()
        return redirect("donor-list")
    return render(request, "_confirm_delete.html", {"object": obj, "back_url": "/doadores/"})
