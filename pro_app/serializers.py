from rest_framework import serializers
from .models import CategoryOfProducts, ProductDetails,Brand, prod_col, Country_code, StoreDepotModel, InventoryDEpartmentModel



class CategoryOfProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryOfProducts
        fields = ['id', 'title', 'description']
        
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'description']

class ProdColSerializer(serializers.ModelSerializer):
    class Meta:
        model = prod_col
        fields = ['id', 'color', 'description']

class ProductDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductDetails
        fields = '__all__'
        
   