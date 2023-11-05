
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from django.db import transaction
from . import models as shop_models


class ConsumerListSerializer(serializers.ModelSerializer):
    debts = serializers.SerializerMethodField()
    
    def get_debts(self, obj: shop_models.Consumer):
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


class ConsumerShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = shop_models.Consumer
        fields = (
            "id",
            "fio",
            "phone_number",
            "phone_number2",
            "created_at",
        )

        
class ConsumerSerializer(serializers.ModelSerializer):
    debts = serializers.SerializerMethodField()
    
    def get_debts(self, obj: shop_models.Consumer):
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
        read_only_fields = ("id",)
    
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
    original_price = serializers.IntegerField(required=False, read_only=True)
    
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
            "original_price",
            "bulk_sell",
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
        bulk_sell = validated_data.get("bulk_sell", False)
        if "courier" in validated_data and validated_data["courier"]:
            validated_data["status"] = "delivery"
        order = shop_models.Order.objects.create(**validated_data)
        total_price = 0
        original_price = 0
        for product in products:
            product_obj = product["product"]
            quantity = product["quantity"]
            if quantity > product_obj.stock_quantity:
                raise ValidationError({"products": f"Maxsulot miqdori yetarli emas: {product_obj.stock_quantity}"}, code="stock_quantity")
            price = product_obj.get_price_for(order.consumer)
            org_price = product_obj.price
            original_price += org_price * quantity
            total_price += price * quantity
            shop_models.OrderProduct.objects.create(
                order=order,
                product=product_obj,
                price=price,
                original_price=org_price,
                quantity=quantity,
            )
        order.total_price = total_price
        order.original_price = original_price
        if order.paid_price > order.total_price:
            raise ValidationError({"price_paid": "To'langan summa buyurtma narxidan oshmasligi kerak"}, code="price_paid")
        
        if full_paid:
            order.paid_price = order.total_price
            order.status = "completed"
        elif not bulk_sell:
            order.status = "completed"
            if not order.consumer:
                # consumer is required when full_paid is false
                raise ValidationError({"consumer": "Buyurtma beruvchi tanlanmagan"}, code="consumer")
            order.paid_price = price_paid
        
        if bulk_sell:
            order.status = "delivery"
        order.save()
        return order


   
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = shop_models.OrderProduct
        fields = ("product", "quantity", "price", "original_price")
     

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    
    def get_products(self, obj):
        return OrderProductSerializer(obj.products.all().select_related("product"), many=True).data
    
    status = serializers.CharField(source="get_status_display")
    
    courier = CourierSerializer()
    consumer = ConsumerShortSerializer()
    
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
            "bulk_sell",
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


class ConsumerDebtSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = ("id", "consumer", "price")
        model = shop_models.ConsumerDebt

    def create(self, validated_data):
        consumer = validated_data["consumer"]
        price = validated_data["price"]
        self.instance = shop_models.ConsumerDebt.objects.create(
            consumer=consumer,
            price=price,
            type=1,
        )
        return self.instance
