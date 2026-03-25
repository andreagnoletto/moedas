from django.urls import path

from . import views

urlpatterns = [
    path("colecao/", views.coinitem_list, name="coinitem-list"),
    path("colecao/novo/", views.coinitem_create, name="coinitem-create"),
    path("colecao/<int:pk>/editar/", views.coinitem_edit, name="coinitem-edit"),
    path("colecao/<int:pk>/apagar/", views.coinitem_delete, name="coinitem-delete"),
    path("colecao/estimar-valor/", views.estimate_collection_value, name="estimate-collection-value"),
    path("colecao/estimar-item/", views.estimate_item_value, name="estimate-item-value"),
    path("colecao/exportar/", views.export_coinitems, name="export-coinitems"),
    path("doadores/", views.donor_list, name="donor-list"),
    path("doadores/novo/", views.donor_create, name="donor-create"),
    path("doadores/<int:pk>/editar/", views.donor_edit, name="donor-edit"),
    path("doadores/<int:pk>/apagar/", views.donor_delete, name="donor-delete"),
]
