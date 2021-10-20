from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import *
import boto3
from environs import Env
# Documentation
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


env = Env()
env.read_env()

from .models import *

class Users(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    name='list_users'

    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'image': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'age': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }
    ))
    @api_view(['POST'])
    def create_user(request):
        # user is created in DataBase
        data={
            'name': request.data['name'],
            'image' : request.data['image'],
            'description' : request.data['description'],
            'age' : request.data['age']
        }
        user = UserSerializer(data=data)

        if user.is_valid():
            user.save() # Save User on DataBase
            boto3.setup_default_session(region_name='eu-west-2')
            client = boto3.client('cognito-idp')
            try:
                response = client.sign_up(
                    ClientId=env.str('AWS_CLIENT_ID'),
                    Username=request.data['email'],
                    Password=request.data['password'],
                    UserAttributes=[
                        {
                            'Name': "name",
                            'Value': request.data['name']
                        },
                        {
                            'Name': "email",
                            'Value': request.data['email']
                        }
                    ]
                )
                return Response(
                    {
                        'MSG' : 'User created!',
                        'response' : response
                    }
                )
            except client.exceptions.InvalidPasswordException:
                return Response('Error:Invalid Password! Password must have length 8 with numbers and special characters')
            except client.exceptions.UsernameExistsException:
                return Response('Error:Username already exists!')
            except client.exceptions.ResourceNotFoundException:
                return Response('Error:Resource Not Found!')
            except client.exceptions.CodeDeliveryFailureException:
                return Response('Error:Code has not delivery!')
        else:
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='int'),
        }
    ))
    @api_view(['POST'])
    def confirm_sign_up(request):
        boto3.setup_default_session(region_name='eu-west-2')
        client = boto3.client('cognito-idp')
        try:
            response = client.confirm_sign_up(
                ClientId=env.str('AWS_CLIENT_ID'),
                Username=request.data['email'],
                ConfirmationCode=request.data['code'],
            )

            return Response({
                'MSG' : 'User Confirmed',
                'response' : response
            })
        except client.exceptions.CodeMismatchException:
            return Response('Error: Code Mismatch!')
        except client.exceptions.ExpiredCodeException:
            return Response('Error: Code has Expired')
        except client.exceptions.UserNotFoundException:
            return Response('Error : User Not Found!')


    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }
    ))
    @api_view(['POST'])
    def login_auth(request):
        boto3.setup_default_session(region_name='eu-west-2')
        client = boto3.client('cognito-idp')
        try:
            response = client.initiate_auth(
                ClientId=env.str('AWS_CLIENT_ID'),
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': request.data['email'],
                    'PASSWORD': request.data['password']
                },
            )
            return Response({
                'MSG': 'User Confirmed',
                'response': response,
            })
        except client.exceptions.UserNotFoundException:
            return Response('Error: User Not Found!')
        except client.exceptions.UserNotConfirmedException:
            return Response('Error: User not confirmed')
        except client.exceptions.NotAuthorizedException:
            return Response('Error: Incorrect username or password!')

class Trips_API(APIView):
    '''
    Trips API Functions
    '''
    queryset = Trips.objects.all()
    serializer_class = TripSerializer

    @api_view(['GET'])
    def get_trip(request,lctn):
        trips = Trips.objects.get(location=lctn)
        trips_srlz = TripSerializer(trips)
        if len(trips_srlz)>0:
            return JsonResponse(trips_srlz.data, safe=False)
        return Response({'msg:No Data!'})

    @api_view(['PUT','DELETE'])
    def update_delete_trip(request,id):
        trip_data = JSONParser().parse(request)
        trip = Trips.objects.get(id=id)
        # Check HTTP Request
        if request.method == 'PUT':
            if id:
                trip_srlz = TripSerializer(trip, data=trip_data)
                if trip_srlz.is_valid():
                    trip_srlz.save()
                    return Response({
                        'msg' : 'Trip Updated!',
                        'data': trip_srlz.data
                    })
            return Response(trip_srlz.errors,status=status.HTTP_400_BAD_REQUEST)
        elif request.method=='DELETE':
            trip.delete()
            return Response({
                'msg': ' Trip Deleted',
            })

    @api_view(['POST'])
    def create_trip(request):
        trip_data = JSONParser().parse(request)
        trip_srlz = TripSerializer(data=trip_data)
        if trip_srlz.is_valid():
            trip_srlz.save()
            return Response({
                'msg': 'Trip Created',
                'data': trip_srlz.data
            })
        return Response(trip_srlz.errors, status=status.HTTP_400_BAD_REQUEST)

class UserTours_API(generics.ListCreateAPIView):
    '''
    Users Trips API
    '''
    queryset = UserTrips.objects.all()
    serializer_class = UserTourSerializer

    @api_view(['GET','PUT','DELETE'])
    def user_tour_id(request,id):
        user_tour_data = JSONParser().parse(request)
        if id:
            if request.method == 'GET':
                user_tour = UserTrips.objects.all().filter(id=id)
                user_tour_ser = UserTourSerializer(user_tour,many=True)
                return Response(user_tour_ser.data)
            elif request.method == 'PUT':
                user_tour = UserTrips.objects.get(id=id)
                user_tour_srlz = UserTourSerializer(user_tour, data=user_tour_data)
                if user_tour_srlz.is_valid():
                    user_tour_srlz.save()
                    return Response({
                        'msg': 'User Trip Updated!',
                        'data': user_tour_srlz.data
                    })
                return Response(user_tour_srlz.errors, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'DELETE':
                user_tour = UserTrips.objects.get(id=id)
                user_tour.delete()
                return Response({
                    'msg': ' User Trip Deleted',
                })


    @api_view(['GET','POST'])
    def user_tours_ops(request):
        user_tour_data = JSONParser().parse(request)
        if request.method == 'POST':
            user_trip_srlz = UserTourSerializer(data=user_tour_data)
            if user_trip_srlz.is_valid():
                user_trip_srlz.save()
                return Response({
                    'msg': 'User Trip Created',
                    'data': user_trip_srlz.data
                })
            return Response(user_trip_srlz.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            user_trips = UserTrips.objects.all()
            user_trips_srlz = UserTourSerializer(user_trips,many=True)
            return Response(user_trips_srlz.data)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'Users': reverse('users', request=request, format=format),
        'Create User':reverse('createUser',request=request, format=format),
        'Confirm Account': reverse('confirm_sign_up', request=request, format=format),
        'Login': reverse('loginAuth', request=request, format=format),
        'documentation':reverse('schema-swagger-ui',request=request,format=format),
        'trips':reverse('trips',request=request,format=format),
        'user_trips':reverse('user_trips',request=request,format=format)
    })
