from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, RetrieveUpdateAPIView, ListCreateAPIView
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q, Sum
from rest_framework import status, viewsets
from . import models as shop_models
from . import serializers as shop_serializers



class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title"]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="consumer_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        pass
    
    def get_queryset(self):
        return shop_models.Product.objects.all().order_by("title")
    
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


class OrderListApiView(ListAPIView):
    serializer_class = shop_serializers.OrderSerializer
    
    def get_queryset(self):
        return shop_models.Order.objects.all()
    
    

class ConsumerViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.ConsumerSerializer

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



class CourierViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.CourierSerializer

    def get_queryset(self):
        return shop_models.Courier.objects.all().order_by("fio")
