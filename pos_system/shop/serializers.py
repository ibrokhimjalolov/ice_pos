
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from django.db import transaction
from . import models as shop_models


class ConsumerListSerializer(serializers.ModelSerializer):
    depts = serializers.SerializerMethodField()
    
    def get_depts(self, obj: shop_models.Consumer):
        return obj.get_total_debts()

    class Meta:
        model = shop_models.Consumer
        fields = (
            "id",
            "fio",
            "phone_number",
            "phone_number2",
            "depts",
            "created_at",
        )


class ConsumerSerializer(serializers.ModelSerializer):
    depts = serializers.SerializerMethodField()
    
    def get_depts(self, obj: shop_models.Consumer):
        return obj.get_total_debts()

    class Meta:
        model = shop_models.Consumer
        fields = (
            "id",
            "fio",
            "phone_number",
            "phone_number2",
            "debts",
            "created_at",
        )
        extra_kwargs = {
            "debts": {"read_only": True},
        }


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = shop_models.Courier
        fields = (
            "id",
            "fio",
            "phone_number",
            "phone_number2",
        )
        

class ProductSerializer(serializers.ModelSerializer):
    consumer_price = serializers.SerializerMethodField()
    
    class Meta:
        model = shop_models.Product
        fields = (
            "id",
            "title",
            "price",
            "consumer_price",
            "count_in_box",
            "stock_quantity",
        )
        read_only_fields = ("id", "stock_quantity")
    
    def get_consumer_price(self, obj):
        if "consumer" in self.context:
            return obj.get_price_for(self.context["consumer"])
        return obj.price


class CreateOrderProduct(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=shop_models.Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.ModelSerializer):
    products = CreateOrderProduct(many=True)
    full_paid = serializers.BooleanField(required=True)
    price_paid = serializers.IntegerField(required=False)
    
    class Meta:
        model = shop_models.Order
        fields = (
            "id",
            "courier",
            "consumer",
            "created_at",
            "products",
            "full_paid",
            "price_paid",
        )
        
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs["full_paid"]:
            if not isinstance(attrs.get("price_paid", None), int):
                raise ValidationError({"price_paid": "required!"}, code="required")
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        products = validated_data.pop("products")
        full_paid = validated_data.pop("full_paid")
        price_paid = validated_data.pop("price_paid", None)
        if "courier" in validated_data and validated_data["courier"]:
            validated_data["status"] = "delivery"
        order = shop_models.Order.objects.create(**validated_data)
        total_price = 0
        for product in products:
            product_obj = product["product"]
            quantity = product["quantity"]
            price = product_obj.get_price_for(order.consumer)
            total_price += price * quantity
            shop_models.OrderProduct.objects.create(
                order=order,
                product=product_obj,
                price=price,
                quantity=quantity,
            )
        order.total_price = total_price
        if order.paid_price > order.total_price:
            raise ValidationError({"price_paid": "gte total_price"}, code="greater_then_total_price")
        
        if full_paid:
            order.paid_price = total_price
            order.status = "completed"
        else:
            if not order.consumer:
                raise ValidationError({"consumer": "required when full_paid is false"}, code="consumer_required")
            order.paid_price = price_paid
            debt_price = total_price - price_paid
            shop_models.ConsumerDebt.objects.create(
                consumer=order.consumer,
                order=order,
                price=debt_price,
                type=-1
            )
        order.save()
        return order


   
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = shop_models.OrderProduct
        fields = ("product", "quantity", "price")
     

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)
    courier = CourierSerializer()
    consumer = ConsumerSerializer()
    
    class Meta:
        model = shop_models.Order
        fields = (
            "id",
            "status",
            "courier",
            "consumer",
            "created_at",
            "delivered_at",
            "products",
            "total_price",
            "paid_price",
        )



class ConsumerDebtListSerializer(serializers.ModelSerializer):
    consumer = ConsumerSerializer()
    order = OrderSerializer()
    
    
    class Meta:
        model = shop_models.ConsumerDebt
        fields = (
            "id",
            "consumer",
            "order",
            "price",
            "type",
            "created_at",
        )


class OrderDeliverySerializer(serializers.Serializer):
    paid_price = serializers.IntegerField(required=True, allow_null=False)
    full_paid = serializers.BooleanField(required=True, allow_null=False)
