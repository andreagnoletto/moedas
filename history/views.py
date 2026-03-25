import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Country
from coinsdb.ai import ask_openai, has_api_key

from .forms import HistoricalContextForm
from .models import HistoricalContext


def context_list(request):
    qs = HistoricalContext.objects.select_related("country")
    country_id = request.GET.get("country", "").strip()
    q = request.GET.get("q", "").strip()
    if country_id:
        qs = qs.filter(country_id=country_id)
    if q:
        qs = qs.filter(title__icontains=q)

    countries = Country.objects.filter(historical_contexts__isnull=False).distinct().order_by("name")

    ctx = {"contexts": qs, "q": q, "country_id": country_id, "countries": countries}
    if request.headers.get("HX-Request"):
        return render(request, "history/context_table.html", ctx)
    return render(request, "history/context_list.html", ctx)


def context_create(request):
    form = HistoricalContextForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("context-list")
    countries = Country.objects.order_by("name")
    return render(request, "history/context_form.html", {
        "form": form, "title": "Novo contexto histórico", "back_url": "/historico/",
        "all_countries": countries, "has_openai_key": has_api_key(),
    })


def context_edit(request, pk):
    obj = HistoricalContext.objects.get(pk=pk)
    form = HistoricalContextForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("context-list")
    return render(request, "_form.html", {"form": form, "title": f"Editar {obj}", "back_url": "/historico/"})


def context_delete(request, pk):
    obj = HistoricalContext.objects.get(pk=pk)
    if request.method == "POST":
        obj.soft_delete()
        return redirect("context-list")
    return render(request, "_confirm_delete.html", {"object": obj, "back_url": "/historico/"})


SYSTEM_PROMPT = """Você é um historiador especializado em numismática.
Dado um tema, gere um resumo cronológico da história monetária relevante para colecionadores.

A descrição DEVE seguir este formato estruturado por períodos:

  Título do Período (ano–ano)
  2-3 frases sobre: padrão monetário vigente, moedas cunhadas, efígies/símbolos,
  reformas monetárias, e o que isso significa para colecionadores.

Exemplo de estilo:
  Período Colonial (até 1822)
  As primeiras moedas vieram de Portugal e utilizavam o Real (Réis). Parte foi cunhada no Brasil, nas primeiras Casas da Moeda.

  Império (1822–1889)
  Mantém-se o sistema de Réis. Moedas traziam Dom Pedro I e Dom Pedro II. Representam a consolidação da identidade nacional.

Inclua de 4 a 8 períodos conforme a complexidade do tema.
Termine com uma frase de conclusão ligando a história às moedas.

Responda APENAS com JSON válido:
{
  "title": "Título (Resumo Cronológico)",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "description": "Texto completo com períodos separados por duas quebras de linha",
  "sources": "Fontes bibliográficas"
}
Use datas aproximadas quando exatas não existirem (ex: início de um século = YYYY-01-01).
Responda em português brasileiro.
"""


@require_POST
def generate_ai(request):
    if not has_api_key():
        return JsonResponse({"error": "OPENAI_API_KEY não configurada no .env"}, status=400)

    data = json.loads(request.body)
    topic = data.get("topic", "").strip()
    country_name = data.get("country_name", "").strip()
    if not topic:
        return JsonResponse({"error": "Informe um tema"}, status=400)

    prompt = topic
    if country_name:
        prompt = f"{topic} — país: {country_name}"

    try:
        result = ask_openai(SYSTEM_PROMPT, prompt)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
