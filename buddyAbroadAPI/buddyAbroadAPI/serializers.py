from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('__all__')

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trips
        fields = ('__all__')

class UserTourSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrips
        fields = ('__all__')
'''
class TuristInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuristInfo
        fields = ('__all__')

class TripsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Trips
        fields = ('__all__')

class TripsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripsDetails
        fields = ('__all__')'''
