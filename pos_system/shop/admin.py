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
    


class OrderProductInline(admin.StackedInline):
    model = models.OrderProduct
    extra = 0

    
    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductInline]
    ordering = ("-id",)
    
    
@admin.register(models.ConsumerDebt)
class ConsumerDebtAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Courier)
class CourierAdmin(admin.ModelAdmin):
    pass
