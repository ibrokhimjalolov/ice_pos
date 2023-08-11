from django.urls import path
from . import api_views

urlpatterns = [
    path("create-order/", api_views.CreateOrderAPIView.as_view(), name="create-order"),

    path("products/", api_views.ProductListCreateAPIView.as_view(), name="product-list"),
    path("products/search/", api_views.ProductSearchAPIView.as_view(), name="product-search"),
    path("products/<int:pk>/", api_views.ProductDetailUpdateAPIView.as_view(), name="products-detail"),
    
    path("consumers/", api_views.ConsumerListCreateAPIView.as_view(), name="consumer-list"),
    path("consumers/<int:pk>/", api_views.ConsumerDetailUpdateAPIView.as_view(), name="consumer-detail"),
    
    path(("consumer-debts/"), api_views.ConsumerDebtListAPIView.as_view(), name="consumer-debt-list"),
]
