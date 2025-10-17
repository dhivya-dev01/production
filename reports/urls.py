
from django.contrib import admin

from reports import views

from .views import *
from django.urls import path, include


urlpatterns = [


    path('stock-summary-report/',views.stock_summary_report),
    path('grey-fabric-report',views.grey_fabric_stock_report),
    path('dyed-fabric-report',views.dyed_fabric_stock_report),
    path('lot-wise-report',views.lot_wise_stock_summary_report),
    # path('get-yarn-summary-list/',views.refresh_data),
  
    path('get-yarn-summary-list/', views.refresh_data, name='get_yarn_summary_list'),
    path('get_yarn_out_list/',views.get_yarn_outward_lists), 
 
    path('get-grey-fabric-lot-summary-list/',views.get_grey_fabric_lot_summary_list), 
    path('get_grey_fabric_lot_list/',views.get_grey_fabric_lot_list), 
    path('get_lot_out_list/',views.get_lot_out_list),
    path('get_gf_available_balance/',views.get_gf_available_balance),


    ###dyed fab report//# 

    path('get-dyed-fabric-lot-summary-list/',views.get_dyed_fabric_lot_summary_list),


]