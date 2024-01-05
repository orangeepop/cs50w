from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("add_new_entry", views.add, name="add"),
    path("edit", views.edit, name="edit"),
    path("random", views.random, name="random"),
    path("<str:title>", views.content, name="content"),
]
