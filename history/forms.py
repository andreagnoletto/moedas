from django import forms

from .models import HistoricalContext

INPUT_CSS = "rounded-lg border border-gray-200 px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-amber-500"


class HistoricalContextForm(forms.ModelForm):
    class Meta:
        model = HistoricalContext
        fields = ["country", "title", "period_start", "period_end", "description", "sources"]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs.update({"class": INPUT_CSS, "rows": 3})
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = INPUT_CSS
            else:
                widget.attrs["class"] = INPUT_CSS
