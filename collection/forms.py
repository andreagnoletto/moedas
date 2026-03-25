from django import forms

from .models import CoinItem, Donor

INPUT_CSS = "rounded-lg border border-gray-200 px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-amber-500"


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ["name", "contact", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs.update({"class": INPUT_CSS, "rows": 3})
            else:
                widget.attrs["class"] = INPUT_CSS


class CoinItemForm(forms.ModelForm):
    class Meta:
        model = CoinItem
        fields = ["coin_type", "condition", "quantity", "origin", "donor", "acquired_at", "cost_brl", "estimated_value_brl", "estimated_at", "location", "notes"]
        widgets = {
            "acquired_at": forms.DateInput(attrs={"type": "date"}),
            "estimated_at": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["condition"].help_text = (
            "<strong>BC</strong> — Bem Conservada: desgaste acentuado, detalhes principais ainda visíveis.<br>"
            "<strong>MBC</strong> — Muito Bem Conservada: desgaste moderado, relevos parcialmente preservados.<br>"
            "<strong>SOB</strong> — Soberba: mínimo desgaste, quase todos os detalhes preservados.<br>"
            "<strong>FC</strong> — Flor de Cunho: sem circulação, brilho original, pode ter pequenos defeitos de cunhagem.<br>"
            "<strong>UNC</strong> — Uncirculated: perfeita, sem manuseio, brilho de cunhagem intacto."
        )
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs.update({"class": INPUT_CSS, "rows": 3})
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = INPUT_CSS
            else:
                widget.attrs["class"] = INPUT_CSS
