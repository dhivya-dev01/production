
from django.contrib import admin

from grey_fabric import views,grey_fab_inward as gin, grey_fab_outward as gout

from grey_fabric.views import * 
from django.urls import path, include

urlpatterns = [



    # GREY FABRIC PO
    path('grey-fab-po',views.grey_fab_po), 

    path('get_mills/', views.get_mills, name='get_mills'),
    path('fabric-names/', views.get_fabric_names, name='get_fabric_names'),
    path('get_knitting_fabric_lists/',views.get_knitting_fabric_details),


    path('grey-fab-po-report/',views.grey_fab_po_report),
    path('grey-fab-po-add/', views.grey_fab_po_add),   
    path('add-grey-fab-po/',views.insert_grey_fab_po), 
    
    # path('po-print/',views.purchase_print),
    path('grey-fabric-po-print/',views.print_grey_fab_po),
    path('edit-grey-fab-po/',views.po_detail_edit),
    path('grey-fab-po-update/',views.grey_fabric_po_update),
    path('get-allowed-roll/',views.get_allowed_roll),
    path('delete-grey-fab-po/',views.delete_grey_fab_po),
   
    path('grey-fab-po-details/',views.grey_fab_po_details),
    path('grey-fab-po-program-report/',views.grey_fabric_po_program_list),
    
    path('gfpo-delivery/',views.grey_fab_po_delivery_list),
    path('gfpo-update/',views.gfpo_update),
    path('add-grey-fab-deliver/',views.add_grey_po_deliver),
    path('gfpo-delivery-delete/',views.po_detail_delete),




#   GREY FABRIC INWARD


    path('grey-fab-inward',gin.grey_fabric_inward),
    path('grey-fab-inward-add',gin.grey_fab_inward_add),
    path('get_party_list/',gin.get_party_list),

    path('get_grey_fabric_po_lists/',gin.get_grey_fabric_po_lists),

    path('grey-fab-po-detail-list/',gin.grey_fabric_po_detail_report),
    path('get_po_knitting_list/',gin.get_po_knitting_list),
    path('get_grey_po_deliver_lists/',gin.get_grey_po_deliver_lists),
    path('tx_load_gf_po_details_inward/',gin.tx_load_gf_po_details_inward),

    path('ajax-report-grey-fab-po-details/',gin.update_grey_fab_inward_list), 
    # get by yarn outward

    path('get_lot_lists/',gin.get_lot_lists), 
    path('get_outward_lists/',gin.get_outward_list),

    path('get_outward_detail_lists/',gin.get_outward_detail_lists),  

    path('get_lot_outward_list/',gin.get_lot_outward_list),
    path('get_yarn_deliver_edit_lists/',gin.get_yarn_deliver_edit_lists),

    path('get_grey_po_deliver_update_lists/',gin.get_grey_po_detail_update_list),
    path('grey-fabric-inward-view/',gin.grey_fabric_inward_lists),
    path('add-grey-fab-inward/',gin.add_grey_fabric_inward),
    path('grey-fabric-inw-print/',gin.grey_fab_inward_print),

    path('grey-fabric-inward-delete/',gin.grey_fabric_inward_delete), 

    path('grey-inward-details-edit/',gin.grey_inward_detail_edit),
  
    path('grey-inw_detail_edit/',gin.sub_inward_detail_edit), 

    path('update-grey-inward-item/',gin.update_grey_fabric_inward),
    path('grey-fabric-inward-detail-delete/',gin.gf_inward_detail_delete),


    # path('grey-fabric-inward-delete/',gin)

    # grey fabric outward

    path('grey-fab-outward',gout.grey_fab_outward), #list
    path('grey-fab-outward-add/',gout.grey_fabric_outward_add),

    path('get-grey-inward-lists/',gout.get_grey_fab_inward),

    path('get_grey_inward_details/',gout.get_grey_fab_inward_detail_list),



    path('get_grey_inward_details_list/',gout.get_grey_inward_details), 
    path('gf-dye-prg-list/',gout.dyeing_program_list),

    path('get_dyed_program_fabrics/',gout.get_dye_program_fabric_list),
    path('get_dyed_program_color/',gout.get_dye_program_colors_list),


    path('add-grey-outward/',gout.insert_grey_fab_outward),
    path('grey-fab-ajax-outward/',gout.grey_fab_outward_ajax_report),
 
    path('edit-grey-outward/',gout.grey_fab_outward_edit),
    path('grey-outward-print/',gout.grey_fab_outward_print),

    path('delete-grey-fab-outward/',gout.grey_fab_outward_delete),



    path('ajax-report-grey-fab-outward-details/',gout.outward_detail_lists),
    path('gf-out-delivery-report/',gout.gf_delivery_details_list),
    path('edit-grey-fab-delivery/',gout.gf_delivery_details_edit),
    path('gfdelivery_update/',gout.gfdelivery_update),

    path('dyeing-prg-update-gf-outward/',gout.dyeing_program_list_update_gf),
    path('update-grey-outward/',gout.update_grey_outward),
]