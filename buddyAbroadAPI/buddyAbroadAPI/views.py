from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import *


from buddyAbroadAPI.models import Users


class Test(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    name='list_users'

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('users', request=request, format=format),
    })
