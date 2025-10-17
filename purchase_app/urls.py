from django.contrib import admin

from purchase_app import views
# from yarn import views, yarn_inward as yin, yarn_outward_bk as yout
from purchase_app import gf_views
from purchase_app import gcf_views

from .views import *
from .gf_views import *
from .gcf_views import *
from django.urls import path, include 

urlpatterns = [
    # ``````````views.py`````````````````

    # # YARN PO
    # path('yarn-po',views.yarn_po), 
    # path('get_mills/<int:party_id>/', views.get_mills, name='get_mills'),
    # path('yarn-po-report/',views.yarn_po_report),
    # path('yarn-po-add/', views.yarn_po_add),   
    # path('add-yarn-po/',views.insert_yarn_po),
    
    # path('po-print/',views.purchase_print),
    # path('edit-yarn-po/',views.po_detail_edit),
    # path('delete-yarn-po/',views.delete_yarn_po),
   
    # path('yarn-po-details/',views.yarn_po_details),
    # path('ypo-delivery/',views.yarn_po_delivery_list),
    # path('ypo-update/',views.ypo_update),
    # path('get-allowed-bags/', views.get_allowed_bags, name='get_allowed_bags'),
    # # path('add-deliver/',views.add_deliver),
    # path('ypo-delivery-delete/',views.po_detail_delete),

    # YARN INWARD
  
  
    # path('get-knitting-programs/', yin.get_knitting_programs, name='get_knitting_programs'),
    # path('yarn-inward-delete/',yin.yarn_inward_delete),
    # path('yarn-inward-add',yin.yarn_inward),
    # path('add-yarn-inward/',yin.add_yarn_inward),
    # path('yarn-inward',yin.yarn_list),
    # path('yarn-inward-view/',yin.yarn_inward_list),  
    # path('yarn-details-edit/',yin.inward_detail_edit),

    # path('yarn-inward-update-view/',yin.update_yarn_inward_list),
    # path('add-or-update-inward-item/',yin.add_or_update_inward_item),
    # path('inward-detail-delete/',yin.inward_detail_delete),
    # path('inw_detail_edit/',yin.inward_details_edit),

    
    
    

    # # YARN-OUTWARD

    
    # path('yarn-outward',yout.yarn_outward), #list
    # path('yarn-outward-add',yout.yarn_outward_add),  #add-page
    # path('add-yarn-outward/',yout.add_yarn_outward), #add-outward

    # path('yarn-ajax-outward/',yout.yarn_outward_list), 
    # path('edit-yarn-outward/',yout.yarn_outward_edit), 
    # path('delete-yarn-outward/',yout.yarn_outward_delete),

    # path('ajax-yarn-deatil-outward/',yout.tx_yarn_outward_list),
    # path('edit-yarn-outward-detail/',yout.outward_yarn_edit),
    # path('update-yarn-outward/',yout.update_knitting_delivery),
    # path('delete-yarn-outward/',yout.tx_yarn_outward_delete),

    

    
    

    # GREY PURCHASE ORDER 
    path('gf-po',gf_views.purchase_order_gf),
    path('get_do_lists/',gf_views.get_do_lists),
    path('load-delivery-orders/',gf_views.load_delivery_orders),
    path('add-gf-po/',gf_views.add_purchase_order),

    path('gf-po-details-edit/',gf_views.gf_po_details_edit),
    path('gf-po-delete/',gf_views.gf_po_delete),
    

    path('purchase-order-gf',gf_views.gf_po_page),

    path('gf-purchase-order-view/',gf_views.purchase_order_view),
    path('update-gf-po_view/',gf_views.update_gf_po_view),
    path('add_or_update_gf_po_item/',gf_views.add_or_update_gf_po_item),

    path('gf_po_detail_delete/',gf_views.gf_po_detail_delete),
    path('gf_po_detail_edit/',gf_views.gf_po_detail_edit),

 
    # GF Inward

     
    # gf inward
    path('gf-inward',gf_views.gf_list),
    path('get_po_lists/',gf_views.get_po_lists),
    path('get_do_lists/',gf_views.get_do_lists),
    path('get_knitting_deliveries/',gf_views.get_knitting_deliveries),
    path('gf-inward-add',gf_views.grey_fabric_inward),
    path('get_gf_po_lists/',gf_views.get_gf_po_lists),

    path('load-gf-purchase-orders/',gf_views.load_gf_po_details),
    path('add-gf-inward/',gf_views.add_gf_inward),
    path('gf-inward-view/',gf_views.gf_inward_list), 
    path('gf-details-edit/',gf_views.inward_detail_edit),
    path('gf-inward-delete/',gf_views.gf_inward_delete),

    path('gf-inward-update-view/',gf_views.update_gf_inward_list),
    path('add-or-update-gf-inward-item/',gf_views.add_or_update_gf_inward_item),
    path('gf-inward-detail-delete/',gf_views.gf_inward_detail_delete),
    path('gf_inward_detail_edit/',gf_views.gf_inward_edit),

    # GF Delivery

    path('gf-deliver',gf_views.gf_delivery),
    path('get_gf_inward_details/',gf_views.get_gf_inward_details),
    path('dye-prg-list/',gf_views.dye_program_list),
    path('get_gf_delivery_details/',gcf_views.get_gf_delivery_lists),
    path('get_gf_do_lists/',gcf_views.get_gf_do_lists),
    path('get_lot_details/',gf_views.get_lot_details),
    path('gf-delivery-view/',gf_views.gf_delivery_list),
    path('gf-deliver-add',gf_views.gf_delivery_add),
    path('get_gf_delivery_list/',gf_views.get_gf_delivery_list) ,
    path('load-gf-po-orders/',gf_views.load_gf_po_id_list),
    path('load-gf-inward-orders/',gf_views.load_gf_inward_detail),

    path('add-gf-deliver/',gf_views.add_gf_delivery),
    path('gf_deliver-edit/',gf_views.gf_delivery_edit),

    path('gf-delivery-detail-view/',gf_views.gf_delivery_update_view),

    path('add-or-update-gf-delivery-item/',gf_views.add_or_update_gf_delivery_item),
    path('gf-delivery-detail-delete/',gf_views.gf_delivery_detail_delete),
    path('gf_delivery_details_edit/',gf_views.gf_delivery_detail_edit),




 
    # GREY Colored PURCHASE ORDER 
    path('add-gcf-po',gcf_views.purchase_order_gcf),
    path('gcf-po',gcf_views.purchase_order_list),
    path('gcf-purchase-order-view/',gcf_views.purchase_order_view),

    path('gcf-po-details-edit/',gcf_views.gcf_po_details_edit),
    path('gcf-po-delete/',gcf_views.gcf_po_delete),
    path('update-gcf-po_view/',gcf_views.update_gcf_po_view),
    path('add_or_update_gcf_po_item/',gcf_views.add_or_update_gcf_po_item),
 
    path('gcf_po_detail_delete/',gcf_views.gcf_po_detail_delete),
    path('gcf_po_detail_edit/',gcf_views.gcf_po_detail_edit),
    path('gcf-po-add/',gcf_views.add_purchase_order),




    # gcf inward
    path('gcf-inward',gcf_views.gcf_list),
    path('load-gf-delivery-orders/',gcf_views.load_gf_delivery_details),

    path('gcf-inward-add',gcf_views.grey_colored_fabric_inward),
    path('get_lot_product_id/',gcf_views.get_lot_product_id),
    # path('get_gcf_po_lists/',gcf_views.get_gcf_po_lists),

    # path('load-gcf-purchase-orders/',gcf_views.load_gcf_po_details),
    path('add-gcf-inward/',gcf_views.add_gcf_inward),
    path('gcf-inward-view/',gcf_views.gcf_inward_list), 
    path('gcf-details-edit/',gcf_views.gcf_inward_detail_edit), 
    path('gcf-inward-delete/',gcf_views.gcf_inward_delete),

    path('dyed-update-inward/',gcf_views.gcd_parent_inward_update),

    path('gcf-inward-update-view/',gcf_views.update_gcf_inward_list),
    path('add-or-update-gcf-inward-item/',gcf_views.add_or_update_gcf_inward_item),
    # path('gcf-inward-detail-delete/',gcf_views.gcf_inward_detail_delete),
    path('gcf_inward_detail_edit/',gcf_views.gcf_inward_edit),



    path('gcf-deliver',gcf_views.gcf_delivery), 
    path('get_order_through_list/',gcf_views.get_order_through_list),
    path('get_throught_lot_list/',gcf_views.get_through_lot_list),
    path('get_gcf_lot_details/',gcf_views.get_gcf_lot_details),


    path('gcf-delivery-view/',gcf_views.gcf_delivery_list),
    path('gcf-deliver-edit/',gcf_views.gcf_delivery_detail_edit),
    path('gcf-deliver-add',gcf_views.gcf_delivery_add), 
    # path('get_gf_delivery_list/',gf_views.get_gf_delivery_list) ,
    # # path('load-gf-po-orders/',gf_views.load_gf_po_id_list),
    path('load-gcf-delivery-orders/', gcf_views.load_gcf_delivery_details, name='load_gcf_delivery_orders'),

    # path('load-gcf-delivery-orders/',gcf_views.load_gcf_delivery_details),

    path('add-gcf-deliver/',gcf_views.add_gcf_delivery),

    path('gcf-delivery-detail-view/',gcf_views.gcf_delivery_update_view),

    path('add-or-update-gcf-delivery-item/',gcf_views.add_or_update_gcf_delivery_item),
    path('gcf-delivery-detail-delete/',gcf_views.gcf_delivery_detail_delete),
    path('gcf_delivery_details_edit/',gcf_views.gcf_delivery_details_edit),

 
    # Dyeing program


    path('dyeing-program',views.dyeing_program),
    path('dyeing-program-add',views.add_dyeing_program),
    path("get-colors/", views.get_colors_for_fabric, name="get_colors_for_fabric"),

    path("get-fabric-details/", views.get_fabric_details, name="get_fabric_details"),
    path("save-dyeing-program/", views.save_dyeing_program, name="save_dyeing_program"),
    path('dyeing-program-view/',views.dyeing_program_list),
    path('dyeing-program-edit/',views.dyeing_program_edit),  

    path('dyeing-tx-program-view/',views.tx_dyeing_program),

    path('update-dyeing-program/',views.update_dyeing_program),

    path('get-fabric-dias/',views.get_fabric_dias),

    path('add-fabric-rolls/',views.add_fabric_rolls),
    path('dyeing-update/',views.tm_dyeing_update),


#     # cutting program
#     path('cutting-program',views.cutting_program),
#     path('cutting-program-view/',views.cutting_program_view),   
     
#     path('cutting-program-add',views.add_cutting_program),
#     path('get_quality_style_list/',views.get_quality_style_list),
#     path('add-cutting-program/',views.save_cutting_program),
#     path('cutting-program-edit/',views.cutting_program_edit),

#     path('update-cutting-list/',views.tx_cutting_program_list),
#     path('cutting-prg-detail-edit/',views.edit_cutting_prg_detail),

#     path('add_or_update_cutting_program/',views.add_or_update_cutting_program),
#     path('check_existing_cutting_program/',views.check_existing_cutting_program),

#     path('tm-cutting-prg-delete/',views.tm_cutting_prg_delete),
#     path('tx-cutting-prg-delete/',views.tx_cutting_prg_delete),



# # cutting entry
#     path('cutting-entry',views.cutting_entry),
#     path('cutting-entry-view/',views.cutting_entry_view),   
     
#     path('cutting-entry-add',views.add_cutting_entry),
#     path('get_cutting_program_lists/',views.get_cutting_program_lists),
#     path('get_sub_cutting_program/',views.get_sub_cutting_program),

#     path('get_quality_style_list/',views.get_quality_style_list),
#     path('add-cutting-entry/',views.save_cutting_entry),
#     path('cutting-entry-edit/',views.cutting_entry_edit),

#     path('cutting-entry-detail-edit/',views.edit_cutting_entry_detail),

#     path('check_existing_cutting_entry/',views.check_existing_cutting_entry),
#     path('add_or_update_cutting_entry/',views.add_or_update_cutting_entry),

#     path('tx-cutting-entry-list/',views.tx_cutting_entry_list),

#     path('tm-cutting-entry-delete/',views.tm_cutting_entry_delete),
#     path('tx-cutting-entry-delete/',views.tx_cutting_entry_delete),



#     # accessory program

#     path('accessory-program',views.accessory_program),
#     path('accessory-program-view/',views.accessory_program_view),   
#     path('accessory-program-add',views.add_accessory_program),

#     path('get_quality_item_list/',views.get_quality_item_list),

#     path('add-accessory-program/',views.save_accessory_program),







] 