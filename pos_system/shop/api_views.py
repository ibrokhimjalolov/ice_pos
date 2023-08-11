from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, RetrieveUpdateAPIView, ListCreateAPIView
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q, Sum
from . import models as shop_models
from . import serializers as shop_serializers



class ProductListCreateAPIView(ListCreateAPIView):
    queryset = shop_models.Product.objects.all().order_by("title")
    serializer_class = shop_serializers.ProductListCreateSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ["title"]
    
    def get_queryset(self):
        return self.queryset.all()  


class ProductDetailUpdateAPIView(RetrieveUpdateAPIView):
    queryset = shop_models.Product.objects.all()
    serializer_class = shop_serializers.ProductListCreateSerializer
    
    def get_queryset(self):
        return self.queryset.all()  



class ProductSearchAPIView(ListAPIView):
    queryset = shop_models.Product.objects.all()
    serializer_class = shop_serializers.ProductSearchSerializer
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="consumer_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
        ]
    )

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.order_by("title")

    def get_serializer_context(self):
        cnt = super().get_serializer_context()
        if "consumer_id" in self.request.GET:
            consumer_id = self.request.GET.get("consumer_id")
            try:
                cnt["consumer"] = shop_models.Consumer.objects.get(id=int(consumer_id))
            except ValueError:
                pass
        return cnt


class CreateOrderAPIView(CreateAPIView):
    serializer_class = shop_serializers.CreateOrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = shop_serializers.OrderSerializer(serializer.instance).data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)



class ConsumerListCreateAPIView(ListCreateAPIView):
    serializer_class = shop_serializers.ConsumerListCreateSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ["fio"]
    
    def get_queryset(self):
        return shop_models.Consumer.objects.all().order_by("fio")



class ConsumerDetailUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = shop_serializers.ConsumerListCreateSerializer
    
    def get_queryset(self):
        return shop_models.Consumer.objects.all().order_by("fio")



class ConsumerDebtListAPIView(ListAPIView):
    serializer_class = shop_serializers.ConsumerDebtListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "consumer": ["exact"],
        "type": ["exact"],
    }

    def get_queryset(self):
        return shop_models.ConsumerDebt.objects.all().order_by("-created_at")
    
    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        qs = self.filter_queryset(self.get_queryset())
        response.data["total_debt"] = qs.filter(type=1).aggregate(total_debt=Sum("price"))["total_debt"] or 0
        response.data["total_paid"] = qs.filter(type=-1).aggregate(total_paid=Sum("price"))["total_paid"] or 0
        return response
