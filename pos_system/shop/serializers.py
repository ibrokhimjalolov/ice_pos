
from rest_framework import serializers
from . import models as shop_models


class ProductListSerializer(serializers.ModelSerializer):
    consumer_price = serializers.SerializerMethodField()
    
    class Meta:
        model = shop_models.Product
        fields = (
            "id",
            "title",
            "price",
            "consumer_price",
        )
        
    def get_consumer_price(self, obj):
        if "consumer" in self.context:
            return obj.get_price_for(self.context["consumer"])
        return obj.price
