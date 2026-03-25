from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def sortable_th(label, field, current_sort, url_name, css="text-left"):
    is_active = current_sort and current_sort.lstrip("-") == field
    is_desc = current_sort and current_sort.startswith("-")
    next_sort = f"-{field}" if is_active and not is_desc else field

    arrow = ""
    if is_active:
        arrow = " ↑" if not is_desc else " ↓"

    active_css = "text-amber-600" if is_active else "text-gray-500"
    url = reverse(url_name)

    return format_html(
        '<th class="px-4 py-3 font-medium {css}">'
        '<a href="{url}?sort={sort}" class="{active} hover:text-amber-600 cursor-pointer" '
        'hx-get="{url}?sort={sort}" hx-target="#results" hx-include="[name=\'q\'],[name=\'country\'],[name=\'material\'],[name=\'condition\'],[name=\'location\']">'
        '{label}{arrow}</a></th>',
        css=css, url=url, sort=next_sort, active=active_css, label=label, arrow=arrow,
    )
