from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.


class CategoryOfProducts(models.Model):
    title = models.CharField(max_length=255, blank = False, null = False)
    description = models.CharField(max_length=255, blank = True)
    
    def __str__(self):
        return self.title

class prod_col(models.Model):
    color = models.CharField(max_length=255, blank = False, null = False)
    description = models.CharField(max_length=255, blank = True)
    
    def __str__(self):
        return self.color
    
class Brand(models.Model):
    name = models.CharField(max_length=255, blank = False, null = False)
    description = models.CharField(max_length=255, blank = True)
    
    def __str__(self):
        return self.name
    
class ProductDetails(models.Model):
    category_id = models.ForeignKey(CategoryOfProducts, on_delete = models.CASCADE, db_index = True)
    prod_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank = False, null = False, db_index = True, help_text = 'Name of product')
    color_code = models.ForeignKey(prod_col, on_delete = models.CASCADE)
    sku_number = models.CharField(max_length = 255, blank = False, null = False)
    description = models.CharField(max_length=255, blank = True)
    review = models.CharField(max_length=255, blank = True, null = True)
    
    def __str__(self):
        return self.name
    
class Country_code(models.Model):
    country_name = models.CharField(max_length=255, blank = False, null = False)
    country_code = models.CharField(max_length=255, blank = False)
    
    def __str__(self):
        return f"{self.country_name} {self.country_code}"




class StoreDepotModel(models.Model):
    store_name = models.CharField(max_length=255, blank = False, null = False)
    address = models.CharField(max_length = 255, blank = False, null = True, help_text = 'enter your address here')
    store_email = models.EmailField(max_length = 255, unique = True, blank = False, null = False, db_index = True)
    Country_code = models.ForeignKey(Country_code, on_delete = models.CASCADE)
    contacts = models.IntegerField(max_length = 255, null = False)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
class InventoryDEpartmentModel(models.Model):
    product_id = models.ForeignKey(ProductDetails, on_delete = models.CASCADE)
    store_id = models.ForeignKey(StoreDepotModel, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    is_available = models.BooleanField(default = True)
    
    
