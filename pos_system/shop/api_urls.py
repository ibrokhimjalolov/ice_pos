from django.urls import path
from . import api_views

urlpatterns = [
    path("create-order/", api_views.CreateOrderAPIView.as_view(), name="create-order"),

    path("product-list/", api_views.ProductListAPIView.as_view(), name="product-list"),
    path("product-detail/<pk>/", api_views.ProductDetailAPIView.as_view(), name="product-detail"),
    
    path("consumer-list/", api_views.ConsumerListAPIView.as_view(), name="consumer-list"),
    path("consumer-detail/<pk>/", api_views.ConsumerDetailAPIView.as_view(), name="consumer-detail"),
    

]
