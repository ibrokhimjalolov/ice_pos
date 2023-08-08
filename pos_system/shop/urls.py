from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("products/create/", views.ProductCreate.as_view(), name="product-create"),
    path("products/<pk>/", views.ProductDetail.as_view(), name="product-detail"),
    path("products/", views.ProductList.as_view(), name="products"),
]
