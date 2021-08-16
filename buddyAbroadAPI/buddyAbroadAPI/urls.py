from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('users/',Users.as_view(),name='users'),
    path('createUser/',Users.create_user,name='createUser'),
    path('confirmAccount/',Users.confirm_sign_up,name='confirm_sign_up'),
    path('login/',Users.login_auth,name='loginAuth'),
    path('', views.api_root),
]