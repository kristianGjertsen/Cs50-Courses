from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("add", views.add, name="add"),
    path("random", views.random_page, name="random"),
    path("<str:name>", views.site, name="site"),
    path("entries/<str:title>", views.edit, name="edit"),
]
