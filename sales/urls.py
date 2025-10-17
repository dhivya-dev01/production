
from django.contrib import admin

from sales import views,sales 
from .views import *
from django.urls import path, include

urlpatterns = [


    path('sales-order',views.sales_orders),

    path('add-sales-order',views.add_sales_order),
    path('get_packing_received_list/',views.get_packing_received_lists),
    path('get_packing_inward_list/',views.get_packing_inward_list),

    path('insert-sales-order/',views.insert_sales_order),
    path('sales-order-ajax-report/',views.sales_order_ajax_list),

    path('sales-order-edit/',views.sales_order_edit_value),
    path('get_quality_style_lists/',views.get_quality_style_lists),

    path('get_sales_order_list/',views.get_sales_order_list),

    path('update-sales-order/',views.update_sales_order),  

 

    # `````````````````````````` sales ````````````````````````

    path('sales',sales.sales),

    path('add-sales',sales.add_sales),

    path('sales-ajax-report/',sales.sales_ajax_list),
    path('get_customer_sales_orders/',sales.get_customer_sales_orders),
    path('get_sales_order_data_lists/',sales.get_sales_order_data),
    path('insert-sales/',sales.insert_sales),

] 