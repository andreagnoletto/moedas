from django.urls import path

from . import views

urlpatterns = [
    path("paises/", views.country_list, name="country-list"),
    path("catalogo/", views.cointype_list, name="cointype-list"),
    path("catalogo/novo/", views.cointype_create, name="cointype-create"),
    path("catalogo/<int:pk>/editar/", views.cointype_edit, name="cointype-edit"),
    path("catalogo/<int:pk>/apagar/", views.cointype_delete, name="cointype-delete"),
    path("catalogo/preencher-ia/", views.cointype_fill_ai, name="cointype-fill-ai"),
    path("catalogo/exportar/", views.export_cointypes, name="export-cointypes"),
]
