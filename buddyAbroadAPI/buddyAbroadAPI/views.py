from botocore.exceptions import ClientError
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
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

from buddyAbroadAPI.models import *


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
            boto3.setup_default_session(region_name='us-east-2')
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
        boto3.setup_default_session(region_name='us-east-2')
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
        boto3.setup_default_session(region_name='us-east-2')
        client = boto3.client('cognito-idp')
        try:
            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': request.data['email'],
                    'PASSWORD': request.data['password']
                },
                ClientId=env.str('AWS_CLIENT_ID'),
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

class TripsAPI(generics.ListCreateAPIView):


    test_param = openapi.Parameter('test', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_BOOLEAN)
    trips_response = openapi.Response('response description', TripsSerializers)
    @swagger_auto_schema(method='get',
                         manual_parameters=[test_param],
                         responses={200: trips_response})
    @api_view(['GET'])
    def get(request):
        trips = Trips.objects.all()
        boto3.setup_default_session(region_name='us-east-2')
        client = boto3.client('s3')
        for trip in trips:
            try:
                response = client.generate_presigned_url(ClientMethod='get_object',
                                                            Params={'Bucket' : 'buddy-abroad',
                                                                    'Key':'' + trip.principal_image},
                                                            ExpiresIn=3200)
                trip.principal_image = response
            except ClientError as e:
                return Response(e)

        trips_serializer = TripsSerializers(trips,many=True)
        return Response(trips_serializer.data)



@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'Users': reverse('users', request=request, format=format),
        'Create User':reverse('createUser',request=request, format=format),
        'Confirm Account': reverse('confirm_sign_up', request=request, format=format),
        'Login': reverse('loginAuth', request=request, format=format),
        'documentation':reverse('schema-swagger-ui',request=request,format=format),
        'trips' : reverse('trips',request=request, format=format)
    })
