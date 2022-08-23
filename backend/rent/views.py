from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from django.contrib.auth.models import User

from .serializers import BikeSerializer, RentSerializer
from .models import Bike
from .services import *
from userprofile.services import charge_wallet, debit_wallet


class BikeListView(APIView):
    def get(self, request):
        """List all bikes."""
        bikes = Bike.objects.all()
        bikes = BikeSerializer(bikes, many=True)
        return Response(bikes.data)

    def post(self, request):
        """Create a new bike."""
        bike = BikeSerializer(data=request.data)
        if bike.is_valid():
            bike.save()
            return Response(bike.data, status.HTTP_201_CREATED)
        return Response(bike.errors, status.HTTP_400_BAD_REQUEST)


class BikeDetailView(APIView):
    def get(self, request, bike_id):
        """Get a bike by bike_id, or 404 if not found."""
        try:
            bike = Bike.objects.get(id=bike_id)
        except Bike.DoesNotExist:
            return Response({'detail': 'Not found'}, status.HTTP_404_NOT_FOUND)
        bike = BikeSerializer(bike)
        return Response(bike.data)

    def put(self, request, bike_id):
        """Change whole bike of bike_id or create new one with bike_id"""
        try:
            bike = Bike.objects.get(id=bike_id)
            bike = BikeSerializer(bike, data=request.data)
            code = status.HTTP_200_OK
        except Bike.DoesNotExist:
            bike = BikeSerializer(data=request.data)
            code = status.HTTP_201_CREATED
        if bike.is_valid():
            bike.save()
            return Response(bike.data, code)
        return Response(bike.errors, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, bike_id):
        """Change partially bike with bike_id"""
        try:
            bike = Bike.objects.get(id=bike_id)
            bike = BikeSerializer(bike, data=request.data, partial=True)
        except Bike.DoesNotExist:
            return Response({'detail': 'Not found'}, status.HTTP_404_NOT_FOUND)
        if bike.is_valid():
            bike.save()
            return Response(bike.data)
        return Response(bike.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, bike_id):
        """Delete bike with bike_id"""
        try:
            bike = Bike.objects.get(id=bike_id)
            bike.delete()
        except Bike.DoesNotExist:
            return Response({'detail': 'Not found'}, status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Deleted'}, status.HTTP_204_NO_CONTENT)


class RentDetailView(APIView):
    def post(self, request):
        '''Start and create rent of bike'''
        user_id = request.data['user_id']
        user = User.objects.select_related('wallet').get(id=user_id)
        bike_id = request.data['bike_id']

        try:
            bike = reserve_bike(bike_id)
            if not charge_wallet(user.wallet, bike.price):
                release_bike_reserve(bike_id)
                raise ParseError('Can`t charge wallet. Not enough money or deactivated')
            rent = RentSerializer(create_rent(bike, user))
            return Response(rent.data)
        except APIException as e:
            return Response({'error': e.detail}, e.status_code)

    def delete(self, request):
        '''Stop rent of bike'''
        user_id = request.data['user_id']
        user = User.objects.select_related('wallet').get(id=user_id)
        rent_id = request.data['rent_id']
        distance = request.data['distance']

        try:
            rent = stop_rent(rent_id, user_id, distance)
            release_bike_reserve(rent.bike.id, distance)
            minutes = calc_minutes_to_refund(rent.created_at, rent.ended_at)
            money = calc_refund_amount(minutes, rent.bike.price)
            if debit_wallet(user.wallet, money):
                return Response(RentSerializer(rent).data)
            raise ParseError(
                'Wallet error, can`t refund extra minutes. Contact administration')
        except APIException as e:
            return Response({'error': e.detail}, e.status_code)
