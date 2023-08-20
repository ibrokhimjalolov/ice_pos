from django.urls import path
from . import api_views

from rest_framework.routers import DefaultRouter

courier_urls = DefaultRouter()
courier_urls.register('couriers', api_views.CourierViewSet, basename='couriers')


consumer_urls = DefaultRouter()
consumer_urls.register('consumers', api_views.ConsumerViewSet, basename='consumers')

product_urls = DefaultRouter()
product_urls.register('products', api_views.ProductViewSet, basename='products')

urlpatterns = [
    path("orders/create/", api_views.CreateOrderAPIView.as_view(), name="order-create"),
    path("orders/", api_views.OrderListApiView.as_view(), name="order-list"),
    path(("consumer-debts/"), api_views.ConsumerDebtListAPIView.as_view(), name="consumer-debt-list"),

]

urlpatterns += courier_urls.urls + consumer_urls.urls + product_urls.urls
