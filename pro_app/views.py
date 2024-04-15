from rest_framework import generics, status
from django.db import transaction
from rest_framework.response import Response
from .models import CategoryOfProducts, prod_col, ProductDetails, Brand
from .serializers import CategoryOfProductsSerializer, ProdColSerializer, BrandSerializer, ProductDetailsSerializer
from random import randint
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProductListCreateAPIView(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_summary="Get list of products",
        operation_description="Retrieve a list of products optionally filtered by search query and sorted.",
        responses={200: ProductDetailsSerializer(many=True)},
    )
    def get(self, request):
        search_query = request.query_params.get('search', None)
        sort_by = request.query_params.get('sort_by', None)

        if search_query:
            products = ProductDetails.objects.filter(name__icontains=search_query) | ProductDetails.objects.filter(brand__name__icontains=search_query)
        else:
            products = ProductDetails.objects.all()

        if sort_by:
            products = products.order_by(sort_by)

        serializer = ProductDetailsSerializer(products, many=True)

        return Response({"data" : serializer.data,})
    
    @transaction.atomic
    @swagger_auto_schema(
        operation_summary="Create a new product",
        operation_description="Create a new product with category, brand, color, and other details.",
        request_body=ProductDetailsSerializer,
        responses={201: openapi.Response("Product created successfully", ProductDetailsSerializer)},
    )
    def post(self, request):
        data = request.data
        
        category_data = data.get('category', {})
        category_serializer = CategoryOfProductsSerializer(data=category_data)
        
        if category_serializer.is_valid():
            try:
                existing_category = CategoryOfProducts.objects.get(title=category_data['title'])
                category_instance = existing_category
            except CategoryOfProducts.DoesNotExist:
                category_serializer.is_valid(raise_exception=True)
                category_instance = category_serializer.save()
        else:
            return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract brand data from request
        brand_data = data.get('brand', {})
        brand_serializer = BrandSerializer(data=brand_data)
        
        if brand_serializer.is_valid():
            try:
                existing_brand = Brand.objects.get(name=brand_data['name'])
                brand_instance = existing_brand
                brand_message = 'Brand already exists.'
            except Brand.DoesNotExist:
                brand_serializer.is_valid(raise_exception=True)
                brand_instance = brand_serializer.save()
                brand_message = 'New brand created.'
        else:
            return Response(brand_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_data = data.get('product', {})
        product_name = product_data.get('name', '')
        sku_number = product_data.get('sku_number', '')

        if ProductDetails.objects.filter(name=product_name, brand=brand_instance).exists() \
            or ProductDetails.objects.filter(sku_number=sku_number, brand=brand_instance).exists():
            return Response({'message': 'Product with the same name or SKU already exists under this brand.'}, status=status.HTTP_400_BAD_REQUEST)

        color_name = product_data.pop('color', '')  # Remove 'color' key from product_data
        
        try:
            color_instance = prod_col.objects.get(color=color_name)
        except prod_col.DoesNotExist:
            color_serializer = ProdColSerializer(data={'color': color_name})
            if color_serializer.is_valid():
                color_instance = color_serializer.save()
            else:
                return Response(color_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        sku_number = generate_unique_sku(product_data, color_instance)
        
        # Associate color instance with the product
        product_data['brand'] = brand_instance.id
        product_data['category_id'] = category_instance.id
        product_data['color_code'] = color_instance.id
        product_data['sku_number'] = sku_number
        
        product_serializer = ProductDetailsSerializer(data=product_data)
        
        if product_serializer.is_valid():
            product_instance = product_serializer.save()
            brand_name = Brand.objects.get(id=product_instance.brand_id).name
            product_data['brand_name'] = brand_name  # Add brand name to response data
            return Response({'message': 'Product created successfully.', 'brand_message': brand_message, 'product_data': product_data}, status=status.HTTP_201_CREATED)
        else:
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic
    @swagger_auto_schema(
        operation_summary="Update a product",
        operation_description="Update an existing product's details including brand, category, and color.",
        request_body=ProductDetailsSerializer,
        responses={200: openapi.Response("Product updated successfully", ProductDetailsSerializer)},
    )
    def put(self, request, prod_id):
        try:
            product_instance = ProductDetails.objects.get(prod_id=prod_id)
        except ProductDetails.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('product', {})

        brand_data = data.pop('brand', {})
        if brand_data:
            brand_serializer = BrandSerializer(product_instance.brand, data=brand_data, partial=True)
            if brand_serializer.is_valid():
                brand_instance = brand_serializer.save()
            else:
                return Response(brand_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        color_data = data.pop('color', {})
        if color_data:
            color_serializer = ProdColSerializer(product_instance.color_code, data=color_data, partial=True)
            if color_serializer.is_valid():
                color_instance = color_serializer.save()
            else:
                return Response(color_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductDetailsSerializer(product_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="Delete all products",
        operation_description="Delete all products, categories, brands, and colors from the database.",
    )
    def delete(self, request):
            # Delete all products
            ProductDetails.objects.all().delete()
            
            # Delete all categories
            CategoryOfProducts.objects.all().delete()
            
            # Delete all brands
            Brand.objects.all().delete()
            
            # Delete all colors
            prod_col.objects.all().delete()
            
            return Response({"message": "All categories, brands, colors, and products deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
   

def generate_unique_sku(product_data, color_instance):
    """
    Generate unique alphanumeric SKU for the product color combination.
    Example: ProductName-ColorCode-RandomNumber
    """
    product_name = product_data.get('name', '').replace(" ", "-")
    color_code = color_instance.color.replace(" ", "-")
    
    # Generate a random alphanumeric string as part of the SKU
    random_string = ''.join([str(randint(0, 9)) for _ in range(4)])  # Change the range according to your preference
    
    # Combine the product name, color code, and random string to form the SKU
    sku_number = f"{product_name}-{color_code}-{random_string}"
    
    # Check if the generated SKU is unique
    while ProductDetails.objects.filter(sku_number=sku_number).exists():
        # If the SKU already exists, generate a new random string and try again
        random_string = ''.join([str(randint(0, 9)) for _ in range(4)])
        sku_number = f"{product_name}-{color_code}-{random_string}"
    
    return sku_number


class DeleteProductView(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_summary="Delete a product",
        operation_description="Delete a product from the database.",
        responses={204: "No content"},
    )
    def delete(self, request, prod_id):
        try:
            # Filter Basic_Info object by product_id
            basic_info_instance = ProductDetails.objects.filter(prod_id=prod_id).first()
            
            if not basic_info_instance:
                return Response({"message": "Basic_Info with specified product ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            # Delete Basic_Info and associated PriceCost
            basic_info_instance.delete()
            
            return Response({"message": "Basic_Info and associated PriceCost deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except (ProductDetails.DoesNotExist, Brand.DoesNotExist) as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


