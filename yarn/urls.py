
from django.contrib import admin

from yarn import views, yarn_inward as yin, yarn_outward as yout

from .views import *
from django.urls import path, include

urlpatterns = [




    # YARN PO
    path('yarn-po',views.yarn_po), 
    
    # path('get_mills/<int:party_id>/', views.get_mills, name='get_mills'),
    path('get_mills/', views.get_mills, name='get_mills'),
    path('get_yarn_mills/', views.get_yarn_mills, name='get_yarn_mills'),
    path('fabric-names/', views.get_fabric_names, name='get_fabric_names'),

    path('yarn-po-report/',views.yarn_po_report),
    path('yarn-po-add/', views.yarn_po_add),   
    path('add-yarn-po/',views.insert_yarn_po), 
    
    # path('po-print/',views.purchase_print),
    path('po-print/',views.print_yarn_po),
    path('edit-yarn-po/',views.po_detail_edit),
    path('delete-yarn-po/',views.delete_yarn_po),
   
    path('delete-yarn-po-outward/',views.yarn_po_outward_delete),
    path('yarn-po-details/',views.yarn_po_details),
    path('ypo-delivery/',views.yarn_po_delivery_list),
    path('ypo-update/',views.ypo_update),
    path('get-allowed-bags/', views.get_allowed_bags, name='get_allowed_bags'),
    path('add-deliver/',views.add_deliver),
    path('ypo-delivery-delete/',views.po_detail_delete),



    # YARN INWARD 
    # path('get_knitting_details/',yin.get_knitting_details),
    # path('knit-prg-list/',views.knitting_prg_lists),
    path('tx_load_po_details_inward/',yin.tx_load_po_details_inward),
    path('get-knitting-programs/', yin.get_knitting_programs, name='get_knitting_programs'),
    path('yarn-inward-delete/',yin.yarn_inward_delete),
    path('yarn-inward-add',yin.yarn_inward),
    path('add-yarn-inward/',yin.add_yarn_inward),
    path('yarn-inward',yin.yarn_list),
    path('yarn-inward-view/',yin.yarn_inward_list),  
    path('yarn-details-edit/',yin.inward_detail_edit),

    path('yarn-inward-update-view/',yin.update_yarn_inward_list),
    path('update-inward-item/',yin.update_inward_item),
    path('inward-detail-delete/',yin.inward_detail_delete),
    path('inw_detail_edit/',yin.inward_details_edit),
    path('yarn-inward-print/',yin.print_yarn_inward),



 
    # YARN-OUTWARD

     
    path('yarn-deliver',yout.yarn_outward), #list
    path('get_lot_no/',yout.get_lot_no),
    path('get_inward_details/', yout.get_inward_details, name='get_inward_details'),
    path('get_program_lists/',yout.get_program_lists),

    path('outward-print/',yout.yarn_outward_print),
    path('yarn-deliver-add',yout.yarn_outward_add),  #add-page
    path('add-yarn-outward/',yout.add_yarn_outward), #add-outward

    path('yarn-ajax-outward/',yout.yarn_outward_list),
    path('edit-yarn-deliver/',yout.yarn_outward_edit), 
    path('delete-yarn-outward/',yout.yarn_outward_delete),

    path('outward-details-update/',yout.tm_outward_details_update),
    path('ajax-yarn-deatil-outward/',yout.tx_yarn_outward_list),
    path('edit-yarn-outward-detail/',yout.outward_yarn_edit),
    path('update-yarn-outward/',yout.update_yarn_outward),
    path('delete-yarn-deliver/',yout.tx_yarn_outward_delete),


]