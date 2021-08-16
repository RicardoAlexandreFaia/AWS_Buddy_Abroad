from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import *
import boto3
from environs import Env

env = Env()
env.read_env()

from buddyAbroadAPI.models import Users


class Users(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    name='list_users'

    @api_view(['POST'])
    def create_user(request):
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


    @api_view(['POST'])
    def confirm_sign_up(request):
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


    @api_view(['POST'])
    def login_auth(request):
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




@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'Users': reverse('users', request=request, format=format),
        'Create User':reverse('createUser',request=request, format=format),
        'Confirm Account': reverse('confirm_sign_up', request=request, format=format),
        'Login': reverse('loginAuth', request=request, format=format)
    })
