
from django.contrib import admin

from user_roles import views

from .views import *
from django.urls import path, include

urlpatterns = [



    path('user_roles',views.user_roles),

    path('get_roles/',views.get_roles),
    path('view_roles/',views.view_roles),
    path('add_roles/',views.add_roles),
    path('privileges_update/',views.privileges_update),
    path('edit_roles/',views.edit_roles),
    path('update_roles/',views.update_roles),
    path('duplicate_add/',views.duplicate_add),
    path('role_duplicate/',views.role_duplicate),
    path('delete_roles/',views.delete_roles), 
    path('refresh_privileges/',views.refresh_privileges),


]