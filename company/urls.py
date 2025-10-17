
from django.contrib import admin

from company import views

from .views import *
from django.urls import path

urlpatterns = [ 

    path('company',views.company),
    path('profile',views.profile),
    path('update_company/',views.update_company, name='update_company'),
    

]