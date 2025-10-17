
from django.contrib import admin

from user_auth import views
from .views import *
from django.urls import path, include

urlpatterns = [





    path('', views.signin_admin), 
    path('signin', views.login), 
    # path('login',views.login),
    path('logout',views.logout),

    

]