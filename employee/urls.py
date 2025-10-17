
from django.contrib import admin

from employee import views
from .views import *
from django.urls import path, include

urlpatterns = [


    path('employee',views.employee),
    path('employee-list/',views.employee_list),
    path('employee-add/',views.employee_add),
    path('employee-edit/',views.employee_edit),
    path('employee-update/',views.employee_update),
    path('employee-delete/',views.employee_delete), 


    
]