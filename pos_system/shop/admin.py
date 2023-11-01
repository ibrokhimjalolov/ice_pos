from django.contrib import admin
from . import models


class ProductConsumerPriceInline(admin.StackedInline):
    model = models.ProductConsumerPrice
    extra = 0


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductConsumerPriceInline]
    list_display = ("id", "title", "price", "count_in_box", "stock_quantity")
    ordering = ("title",)
    
    
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
    list_display = ("id", "consumer", "courier", "status", "total_price", "paid_price", "created_at")
    list_filter = ("status", "consumer", "courier")
    
    
@admin.register(models.ConsumerDebt)
class ConsumerDebtAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "consumer", "price", "created_at")
    list_filter = ("consumer",)
    ordering = ("-id",)


@admin.register(models.Courier)
class CourierAdmin(admin.ModelAdmin):
    pass
