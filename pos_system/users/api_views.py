from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from . import serializers


class UserDetail(APIView):
    """
    API endpoint that returns the user's details.
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)
