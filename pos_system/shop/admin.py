from django.contrib import admin
from . import models


class ProductConsumerPriceInline(admin.StackedInline):
    model = models.ProductConsumerPrice
    extra = 0


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductConsumerPriceInline]
    
    
@admin.register(models.Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    inlines = [ProductConsumerPriceInline]