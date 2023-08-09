
from rest_framework import serializers
from . import models as shop_models


class ProductListCreateSerializer(serializers.ModelSerializer):
    consumer_price = serializers.SerializerMethodField()
    
    class Meta:
        model = shop_models.Product
        fields = (
            "id",
            "title",
            "price",
            "count_in_box",
            "stock_quantity",
            "consumer_price",
        )
        read_only_fields = ("id", "stock_quantity", "consumer_price")
        
    def get_consumer_price(self, obj):
        if "consumer" in self.context:
            return obj.get_price_for(self.context["consumer"])
        return obj.price


class CreateOrderProduct(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=shop_models.Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.ModelSerializer):
    products = CreateOrderProduct(many=True)
    
    class Meta:
        model = shop_models.Order
        fields = (
            "id",
            "consumer",
            "created_at",
            "products",
        )
        
    def create(self, validated_data):
        products = validated_data.pop("products")
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
        order.save()
        return order


class ConsumerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = shop_models.Consumer
        fields = (
            "id",
            "fio",
            "phone_number",
            "phone_number2",
        )


class ConsumerListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = shop_models.Consumer
        fields = (
            "id",
            "fio",
            "phone_number",
            "phone_number2",
        )
        read_only_fields = ("id",)
