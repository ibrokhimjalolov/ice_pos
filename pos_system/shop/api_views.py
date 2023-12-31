from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, RetrieveUpdateAPIView, ListCreateAPIView, GenericAPIView
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q, Sum, Count, F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from . import models as shop_models
from . import serializers as shop_serializers
from . import utils



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


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "created_at": ["gte", "lte", "date__gte", "date__lte"],
        "status": ["exact"],
        "consumer": ["exact"],
        "courier": ["exact"],
    }
    
    def get_serializer_class(self):
        if self.action == "create":
            return shop_serializers.CreateOrderSerializer
        elif self.action == "delivery":
            return shop_serializers.OrderDeliverySerializer
        return shop_serializers.OrderSerializer

    def get_queryset(self):
        return shop_models.Order.objects.all().select_related("consumer", "courier")
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = shop_serializers.OrderSerializer(serializer.instance).data
        utils.send_order_create_notify(serializer.instance)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
    
    def destroy(self, request, *args, **kwargs):
        pass
    
    @action(detail=True, methods=['post'])
    def delivery(self, request, pk):
        order = get_object_or_404(shop_models.Order, status="delivery", pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        data = serializer.data
        order.status = "completed"
        order.delivered_at = timezone.now()
        if data["full_paid"]:
            price = order.total_price - order.paid_price
            order.paid_price = order.total_price
        else:
            price = data["paid_price"]
            order.paid_price = max(order.paid_price + data["paid_price"], order.total_price)
        order.save()
        if price > 0:
            shop_models.ConsumerDebt.objects.create(
                order=order,
                consumer=order.consumer,
                type=1,
                price=price
            )
        return Response(shop_serializers.OrderSerializer(instance=order).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk):
        order = get_object_or_404(shop_models.Order, pk=pk)
        if order.status == "completed":
            return Response({"error": "Allaqachon yakunlangan"}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == "canceled":
            return Response({"error": "Allaqachon bekor qilingan"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = "completed"
        order.save()
        return Response({"success": True}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk):
        order = get_object_or_404(shop_models.Order, pk=pk)
        if order.status == "canceled":
            return Response({"error": "Allaqachon bekor qilingan"}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == "completed" and order.created_at + timedelta(hours=24) < timezone.now():
            return Response({"error": "24 soatdan keyin bekor qilib bo'lmaydi"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = "canceled"
        order.save()
        return Response({"success": True}, status=status.HTTP_200_OK)
    

class ConsumerViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.ConsumerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ("fio", "phone_number", "phone_number2")

    def get_queryset(self):
        return shop_models.Consumer.objects.all().order_by("fio")
    
    def get_serializer_class(self):
        if self.action == "list":
            return shop_serializers.ConsumerListSerializer
        return super().get_serializer_class()



class ConsumerDebtListAPIView(ListAPIView):
    serializer_class = shop_serializers.ConsumerDebtListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ("consumer__fio", "consumer__phone_number", "consumer__phone_number2",)
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


class DebtsViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.ConsumerDebtSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]



class CourierViewSet(viewsets.ModelViewSet):
    serializer_class = shop_serializers.CourierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ("fio", "phone_number", "phone_number2")

    def get_queryset(self):
        return shop_models.Courier.objects.all().order_by("fio")



class MostSoldProductsListAPIView(GenericAPIView):
    pagination_class = None
    filter_backends = tuple()
    FROM_DATE_PARAM = "from_date"
    TO_DATE_PARAM = "to_date"
    DATE_FORMAT = "%Y-%m-%d"
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name=FROM_DATE_PARAM,
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=f"Format {DATE_FORMAT}"
            ),
            openapi.Parameter(
                name=TO_DATE_PARAM,
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description=f"Format {DATE_FORMAT}"
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            from_date = utils.parse_date(request.GET.get(self.FROM_DATE_PARAM), self.DATE_FORMAT)
            to_date = utils.parse_date(request.GET.get(self.TO_DATE_PARAM), self.DATE_FORMAT)
        except ValueError:
            return Response({"error": f"Invalid date format. format={self.DATE_FORMAT}"}, status=status.HTTP_400_BAD_REQUEST)
        subquery_filter = Q(orderproduct__order__status="completed")
        if from_date:
            subquery_filter &= Q(orderproduct__order__created_at__date__gte=from_date)
        if to_date:
            subquery_filter &= Q(orderproduct__order__created_at__date__lte=to_date)
        most_sold_products = shop_models.Product.objects.annotate(
            total_orders=Sum('orderproduct__quantity', filter=subquery_filter)
        ).order_by('-total_orders').filter(total_orders__gt=0).values(
            "id", "title", "price", "count_in_box", "stock_quantity", "total_orders"
        )
        
        results = list(most_sold_products)
        return Response({
            "results": results,
            "results_count": len(results),
            "from_date": from_date,
            "to_date": to_date,
        })



def chek_view(request, pk):
    order = get_object_or_404(shop_models.Order, pk=pk)
    return render(request, "check.html", {"order": order})


class BulkSellRemoveView(GenericAPIView):
    
    @transaction.atomic
    def post(self, request, pk):
        #  dont use signals
        order = get_object_or_404(shop_models.Order, pk=pk, bulk_sell=True, status="delivery")
        rem = {}
        for p_id, q in request.data["data"]:
            rem[p_id] = q
        for p in order.products.all():
            if p.product_id not in rem:
                continue
            if p.quantity < rem[p.product_id]:
                raise ValueError("Invalid quantity")
            shop_models.OrderProduct.objects.filter(id=p.id).update(quantity=F("quantity") - rem[p.product_id])
            shop_models.Product.objects.filter(id=p.product_id).update(stock_quantity=F("stock_quantity") + rem[p.product_id])
            
        total_price = 0
        for p in order.products.all():
            total_price += p.quantity * p.price
        shop_models.Order.objects.filter(id=order.id).update(status="completed", total_price=total_price, paid_price=total_price, delivered_at=timezone.now())
        return Response({"success": True}, status=status.HTTP_200_OK)


class CPPriceListView(GenericAPIView):
    
    def get(self, request, pk):
        consumer = shop_models.Consumer.objects.get(pk=pk)
        prices = {
            p.product_id: p.price
            for p in shop_models.ProductConsumerPrice.objects.filter(consumer=consumer)
        }
        data = []
        for product in shop_models.Product.objects.all().order_by("title"):
            data.append({
                "id": product.id,
                "title": product.title,
                "price": prices.get(product.id),
            })
        return Response(data, status=200)



class CPPriceUpdateView(GenericAPIView):
    
    def post(self, request, pk):
        consumer = shop_models.Consumer.objects.get(pk=pk)
        
        for row in request.data["data"]:
            if row["price"]:
                shop_models.ProductConsumerPrice.objects.update_or_create(
                    consumer=consumer,
                    product_id=row["id"],
                    defaults={"price": row["price"]}
                )
            else:
                shop_models.ProductConsumerPrice.objects.filter(
                    consumer=consumer, product_id=row["id"]
                ).delete()
                
        return Response({"success": True})



class OrderProductsView(GenericAPIView):
    
    def get(self, request, pk):
        order = shop_models.Order.objects.get(pk=pk)
        data = []
        for p in order.products.all().select_related("product"):
            data.append({
                "product_id": p.product.id,
                "title": p.product.title,
                "price": p.price,
                "original_price": p.original_price,
                "quantity": p.quantity,
            })
        return Response(data, status=200)
