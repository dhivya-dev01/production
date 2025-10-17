
from django.contrib import admin
 
from colored_fabric import views,dyed_inward as cin

from .views import *
from django.urls import path, include

urlpatterns = [

    # DYED FABRIC PO
    path('dyed-fabric-po',views.dyed_fabric_po),
    path('dyed-fab-po-add/',views.dyed_fab_po_add),
    path('dyed-prg-list/',views.dyeing_program_list),

    path('add-dyed-fab-po/',views.insert_dyed_fabric_po),
    path('dyed-po-ajax-report/',views.dyed_po_list),

    path('dyed-po-details-edit/',views.dyed_fabric_po_edit),
    path('dyed-fab-po-update/',views.update_dyed_fabric_po),
    path('delete-dyed-fab-po/',views.dyed_fabric_po_delete),   # tm &tx data delete
    path('dyed-fabric-po-print/',views.dyed_fabric_po_print),




    # DYED FABRIC INWARD
    path('dyed-fabric-inward',cin.dyed_fabric_inward),
    path('dyed-fab-inward-add/',cin.dyed_fabric_inward_add),
    path('get_dyed_inward_party_list/',cin.get_dyed_inward_party_list),

    path('dyed-inward-view/',cin.dyed_fabric_inward_ajax_report),

    path('get_dyed_fabric_po_lists/',cin.get_dyed_fabric_po_lists),
    path('get_dyed_po_detail_lists/',cin.get_dyed_po_detail_lists),
    path('get_dyed_inward_po_detail_lists/',cin.get_dyed_inward_po_detail_lists),

    # grey outward lists  
    # 
    path('get_grey_out_lot_lists/',cin.get_grey_out_lot_lists),

    path('get_grey_outward_lists/',cin.get_grey_outward_lists),
    path('get_grey_outward_detail_lists/',cin.get_grey_outward_detail_lists),


    path('add-dyed-fab-inward/',cin.insert_dyed_fabric_inward), 
    path('dyed-fabric-inw-print/',cin.dyed_fab_inward_print),
    path('dyed-fabric-inward-delete/',cin.dyed_fabric_inward_delete), 
    path('dyed-inward-details-edit/',cin.dyed_inward_detail_edit),

    path('get_grey_outward_edit_lists/',cin.get_grey_outward_edit_lists),
    path('get_grey_outward_delivery_lists/',cin.get_grey_outward_delivery_lists), 
    path('get_grey_outward_color_list/',cin.get_grey_outward_color_list),

    path('ajax-report-dyed-fab-inward-details/',cin.update_dyed_fab_inward_list), 
    path('update-dyed-inward-item/',cin.update_dyed_fabric_inward), 



 
]