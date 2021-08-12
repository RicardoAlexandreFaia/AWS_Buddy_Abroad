from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('users/',Test.as_view(),name='users'),
    path('', views.api_root),
]