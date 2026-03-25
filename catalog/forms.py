from django import forms

from .models import CoinType

INPUT_CSS = "rounded-lg border border-gray-200 px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-amber-500"


class CoinTypeForm(forms.ModelForm):
    class Meta:
        model = CoinType
        fields = ["country", "denomination", "year", "material", "diameter_mm", "weight_g", "mintage", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs.update({"class": INPUT_CSS, "rows": 3})
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = INPUT_CSS
            else:
                widget.attrs["class"] = INPUT_CSS
