from django.urls import path

from . import views

urlpatterns = [
    path("historico/", views.context_list, name="context-list"),
    path("historico/novo/", views.context_create, name="context-create"),
    path("historico/<int:pk>/editar/", views.context_edit, name="context-edit"),
    path("historico/<int:pk>/apagar/", views.context_delete, name="context-delete"),
    path("historico/gerar-ia/", views.generate_ai, name="context-generate-ai"),
]
