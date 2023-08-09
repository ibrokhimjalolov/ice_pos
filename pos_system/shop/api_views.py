from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, RetrieveUpdateAPIView, ListCreateAPIView
from . import models as shop_models
from . import serializers as shop_serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter



class ProductListCreateAPIView(ListCreateAPIView):
    """
    ?consumer=123 oziga mos narxi olish uchun
    """

    queryset = shop_models.Product.objects.all().order_by("title")
    serializer_class = shop_serializers.ProductListCreateSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ["title"]
    
    def get_queryset(self):
        return self.queryset.all()  
    
    def get_serializer_context(self):
        cnt = super().get_serializer_context()
        if "consumer" in self.request.GET:
            consumer_id = self.request.GET.get("consumer")
            cnt["consumer"] = shop_models.Consumer.objects.get(id=consumer_id)
        return cnt


class ProductDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = shop_models.Product.objects.all()
    serializer_class = shop_serializers.ProductListCreateSerializer
    
    def get_queryset(self):
        return self.queryset.all()  
    
    def get_serializer_context(self):
        cnt = super().get_serializer_context()
        if "consumer" in self.request.GET:
            consumer_id = self.request.GET.get("consumer")
            cnt["consumer"] = shop_models.Consumer.objects.get(id=consumer_id)
        return cnt


class CreateOrderAPIView(CreateAPIView):
    serializer_class = shop_serializers.CreateOrderSerializer



class ConsumerListCreateAPIView(ListCreateAPIView):
    queryset = shop_models.Consumer.objects.all().order_by("fio")
    serializer_class = shop_serializers.ConsumerListCreateSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ["fio"]
    
    def get_queryset(self):
        return self.queryset.all()



class ConsumerDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = shop_models.Consumer.objects.all().order_by("fio")
    serializer_class = shop_serializers.ConsumerListCreateSerializer
    
    def get_queryset(self):
        return self.queryset.all()
