from rest_framework import serializers
from .models import *


class TuristInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuristInfo
        fields = ('__all__')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('__all__')

class TripsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Trips
        fields = ('name',
                  'rating',
                  'principal_image',
                  'description',
                  'price',
                  'users')

class TripsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripsDetails
        fields = '__all__'
