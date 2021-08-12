from rest_framework import serializers
from .models import *

class TuristInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuristInfo
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):
    info = TuristInfoSerializer(many=False,read_only=True)
    
    class Meta:
        model = Users
        fields = ('name','image','age','info','info')