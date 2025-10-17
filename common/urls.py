from django.contrib import admin

from common import views
from .views import *
from django.urls import path, include

urlpatterns = [


    path('dashboard', views.dashboard), 

]