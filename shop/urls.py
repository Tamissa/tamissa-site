from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("request/<slug:artwork_slug>/<str:artwork_title>/", views.request_purchase, name="request_purchase"),
    path("request/success/", views.request_purchase_success, name="request_purchase_success"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<slug:artwork_slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<slug:artwork_slug>/", views.remove_from_cart, name="remove_from_cart"),
]