from django.urls import path
from . import api_views

urlpatterns = [
    path("product-list/", api_views.ProductListAPIView.as_view(), name="product-list"),
]
