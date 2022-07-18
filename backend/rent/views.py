from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import BikeSerializer
from .models import Bike


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
            return Response(bike.data, status.HTTP_200_OK)
        return Response(bike.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, bike_id):
        """Delete bike with bike_id"""
        try:
            bike = Bike.objects.get(id=bike_id)
            bike.delete()
        except Bike.DoesNotExist:
            return Response({'detail': 'Not found'}, status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Deleted'}, status.HTTP_204_NO_CONTENT)