from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import UserSerializer


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all users.
        """
        users = User.objects.all()
        users = UserSerializer(users, many=True)
        return Response(users.data)

    def post(self, request):
        """
        Create a user.
        """
        data = {
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'password': request.data.get('password')
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
