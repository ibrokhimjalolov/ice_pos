from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from .utils import send_order_create_notify


class Consumer(models.Model):
    
    class Meta:
        ordering = ("-id",)
        db_table = 'consumer'
        
    fio = models.CharField(max_length=500)
    phone_number = PhoneNumberField(blank=True, null=True)
    phone_number2 = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.fio
    
    def get_total_debts(self):
        qs = ConsumerDebt.objects.filter(consumer=self)
        # total_debt = qs.filter(type=-1).aggregate(total_debt=Sum("price"))["total_debt"] or 0
        total_paid = qs.filter(type=1).aggregate(total_paid=Sum("price"))["total_paid"] or 0
        debt_from_order = Order.objects.filter(~Q(status="canceled"), consumer=self).aggregate(
            total_debt=Sum("total_price"),
            total_paid=Sum("paid_price")
        )
        return total_paid + (debt_from_order["total_paid"] or 0) - (debt_from_order["total_debt"] or 0)


class Courier(models.Model):
    
    class Meta:
        ordering = ("-id",)
        db_table = 'courier'
        
    fio = models.CharField(max_length=500)
    phone_number = PhoneNumberField(blank=True, null=True)
    phone_number2 = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.fio
    
    
class Product(models.Model):
    class Meta:
        ordering = ("-id",)
        db_table = 'product'
    title = models.CharField(max_length=500, unique=True)
    price = models.PositiveIntegerField()
    count_in_box = models.PositiveIntegerField(default=1)
    stock_quantity = models.PositiveBigIntegerField(default=0)
    
    
    def __str__(self) -> str:
        return self.title
    
    
    def get_price_for(self, consumer: Consumer):
        try:
            return self.consumer_prices.get(consumer=consumer).price
        except ProductConsumerPrice.DoesNotExist:
            return self.price
        
    def warehouse_quantity(self):
        return "%s / %s" % (self.stock_quantity, self.count_in_box)



class ProductConsumerPrice(models.Model):
    class Meta:
        ordering = ("-id",)
        db_table = 'product_price_consumer'
        unique_together = ('product', 'consumer')
        
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='consumer_prices')
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT)
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.consumer)
    
    
    
class Order(models.Model):
    class Meta:
        ordering = ("-id",)
        db_table = 'order'
    STATUSES = (
        ("in_process", "Jarayonda"),
        ("delivery", "Yetkazib berish"),
        ("completed", "Yakunlandi"),
        ("canceled", "Bekor qilindi")
    )
    status = models.CharField(max_length=16, default="in_process", choices=STATUSES)
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT, related_name='orders', null=True, blank=True)
    courier = models.ForeignKey(Courier, on_delete=models.PROTECT, null=True, blank=True, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    total_price = models.PositiveIntegerField(default=0, editable=False)
    paid_price = models.PositiveBigIntegerField(default=0)
    
    def __str__(self) -> str:
        return str(self.consumer)


class OrderProduct(models.Model):
    class Meta:
        ordering = ("-id",)
        db_table = 'order_product'
        
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.PositiveIntegerField(editable=False)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self) -> str:
        return str(self.product)


class ConsumerDebt(models.Model):
    class Meta:        
        ordering = ("-id",)
        db_table = "consumer_debt"
        
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', related_name='debts', on_delete=models.PROTECT, null=True)
    consumer = models.ForeignKey('Consumer', related_name='debts', on_delete=models.PROTECT)
    type = models.SmallIntegerField(choices=((-1, -1), (1, 1)))
    price = models.PositiveBigIntegerField()
    
    def __str__(self) -> str:
        return f"{self.consumer} {self.price * self.type}"


@receiver(post_save, sender=Order)
def update_product_stock(sender, instance, created, **kwargs):
    if created:
        for product in instance.products.all():
            Product.objects.filter(id=product.product_id).update(stock_quantity=models.F("stock_quantity") - product.quantity)
    else:
        old_instance = Order.objects.get(id=instance.id)
        if instance.status == "canceled" and old_instance.status != "canceled":
            for product in instance.products.all():
                Product.objects.filter(id=product.product_id).update(stock_quantity=models.F("stock_quantity") - product.quantity)



@receiver(post_save, sender=Order)
def update_product_stock(sender, instance, created, **kwargs):
    if created:
        send_order_create_notify(instance)
