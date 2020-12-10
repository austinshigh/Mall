from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("cart", views.cart, name="cart"),
    path("categories", views.categories, name="categories"),
    path("checkout", views.checkout, name="checkout"),
    path("review/<int:listing_id>", views.review, name="review"),
    path("category/<int:category_id>", views.category, name="category"),
    path("received", views.checkout, name="received"),

    # API Routes
    path("change-quant/<int:listing_id>", views.change_quant, name="change-quant"),
    path("feedback", views.feedback, name="feedback")
]
