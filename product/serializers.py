# Django imports
from django.contrib.auth.hashers import make_password

# Rest framework imports
from rest_framework import serializers

# Project imports
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'quantity', 'manufacturer']
