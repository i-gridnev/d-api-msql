from rest_framework import serializers
from .models import Bike, Rent

class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ['id', 'name', 'code', 'price', 'mileage', 'is_rented', 'is_active']


class RentSerializer(serializers.ModelSerializer):
    bike = BikeSerializer(read_only=True)
    class Meta:
        model = Rent
        fields = ['id', 'bike','created_at', 'ended_at']