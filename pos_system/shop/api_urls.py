from django.urls import path
from . import api_views

from rest_framework.routers import DefaultRouter

courier_router = DefaultRouter()
courier_router.register('couriers', api_views.CourierViewSet, basename='couriers')

consumer_router = DefaultRouter()
consumer_router.register('consumers', api_views.ConsumerViewSet, basename='consumers')

product_router = DefaultRouter()
product_router.register('products', api_views.ProductViewSet, basename='products')

order_router = DefaultRouter()
order_router.register('orders', api_views.OrderViewSet, basename='orders')

debts_router = DefaultRouter()
debts_router.register('debts', api_views.DebtsViewSet, basename='debts')

urlpatterns = [
    path("consumer-debts/", api_views.ConsumerDebtListAPIView.as_view(), name="consumer-debt-list"),
    path("most-sold-products/", api_views.MostSoldProductsListAPIView.as_view(), name="most-sold-products-list"),
    path("chek/<pk>/", api_views.chek_view, name="chek"),
    path("bulk-sell/<pk>/rem/", api_views.BulkSellRemoveView.as_view(), name="bulk-sell-remove"),
    path("cp-price-list/<pk>/", api_views.CPPriceListView.as_view(), name="cp-price-list"),
    path("cp-price-update/<pk>/", api_views.CPPriceUpdateView.as_view(), name="cp-price-update"),
]

urlpatterns += courier_router.urls + consumer_router.urls + product_router.urls + order_router.urls + debts_router.urls
