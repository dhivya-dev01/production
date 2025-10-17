
from django.contrib import admin

from masters import views
from .views import *
from django.urls import path, include

urlpatterns = [


    path('price-list',views.price_lists),
    path('price-list-report/',views.price_list_report),
    path('price-list-add/',views.price_list_add),
    path('price-list-edit/',views.price_list_edit),
    path('price-list-update/',views.price_list_update),
    path('price-list-delete/',views.price_list_delete),


    path('price-list-range',views.price_list_range),
    path('price-list-range-report/',views.price_list_range_report),
    path('price-list-value-add/',views.price_list_range_add),
    path('price-list-value-edit/',views.price_list_range_edit),
    path('price-list-value-update/',views.price_list_range_update),
    path('price-list-value-delete/',views.price_list_range_delete),
    

]