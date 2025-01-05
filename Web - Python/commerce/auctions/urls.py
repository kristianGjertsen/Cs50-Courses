from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("your", views.your, name="your"),
    path("bids", views.bids, name="bids"),
    path("comment/<int:list_id>", views.comment, name="comment"),
    path("watchlist/<int:list_id>", views.watchlist, name="watchlist"),
    path("delete/<int:list_id>", views.close, name="close"),
    path("<str:id>", views.listing, name="listing")
]
