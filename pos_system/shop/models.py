from django.db import models
from phonenumber_field.modelfields import PhoneNumberField



class Consumer(models.Model):
    
    class Meta:
        db_table = 'consumer'
        
    fio = models.CharField(max_length=500)
    phone_number = PhoneNumberField(blank=True, null=True)
    phone_number2 = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.fio
    
    
    
class Product(models.Model):
    class Meta:
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
        db_table = 'order'
        
    consumer = models.ForeignKey(Consumer, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0, editable=False)
    paid_price = models.PositiveBigIntegerField(default=0)
    
    def __str__(self) -> str:
        return str(self.consumer)
    

class OrderProduct(models.Model):
    class Meta:
        db_table = 'order_product'
        
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.PositiveIntegerField(editable=False)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self) -> str:
        return str(self.product)


class ConsumerDebt(models.Model):
    class Meta:
        db_table = "consumer_debt"
        
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', related_name='debts', on_delete=models.PROTECT, null=True)
    consumer = models.ForeignKey('Consumer', related_name='debts', on_delete=models.PROTECT)
    type = models.SmallIntegerField(choices=((-1, -1), (1, 1)))
    price = models.PositiveBigIntegerField()
    
    def __str__(self) -> str:
        return f"{self.consumer} {self.price * self.type}"
