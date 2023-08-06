from rest_framework.generics import ListAPIView
from . import models as shop_models
from . import serializers as shop_serializers


class ProductListAPIView(ListAPIView):
    queryset = shop_models.Product.objects.all()
    serializer_class = shop_serializers.ProductListSerializer
    
    def get_queryset(self):
        return self.queryset.all()  
    
    def get_serializer_context(self):
        cnt = super().get_serializer_context()
        if "consumer" in self.request.GET:
            consumer_id = self.request.GET.get("consumer")
            cnt["consumer"] = shop_models.Consumer.objects.get(id=consumer_id)
        return cnt
