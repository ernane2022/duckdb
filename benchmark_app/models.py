

# Create your models here.
from django.db import models
import uuid

class SalesRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    sale_date = models.DateTimeField()
    region = models.CharField(max_length=50)
    salesperson = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['category']),
            models.Index(fields=['sale_date']),
            models.Index(fields=['region']),
        ]
        
    def __str__(self):
        return f"{self.product_name} - {self.category}"