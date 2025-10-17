
from django.contrib import admin

from production_app import stiching_in as s_inw, views,packing_out as p_out, packing_in as p_inw, lp_entry as lp,folding_delivery as fd

from production_app.views import * 
from django.urls import path, include



urlpatterns = [



  # ```````````````````````````````` Stiching Delivery ``````````````````````````````````````
    path('stitching-delivery',views.stiching_delivery),  
    path('stitching-delivery-add/',views.stiching_delivery_add),   
    path('get_cutting_summary_stock/',views.get_cutting_summary_stock), 
    path('get_cutting_summary_stock_lists/',views.get_cutting_summary_stock_lists),
    path('get_cutting_summary_stock_data/',views.get_cutting_summary_stock_data), 
 
    path('get_cutting_summary_update_stock/',views.get_cutting_summary_update_stock),

    path('get_cutting_entry_list/',views.get_cutting_entry_available_list),
    path('get_st_delivery_list/',views.get_st_delivery_available_list),
    path('get_st_folding_available_list/',fd.get_st_folding_delivery_available_list),
    path('get_cutting_entry_available/',views.get_cutting_entry_available), 
    path('get_cutting_entry_quality_style_list/',views.get_cutting_entry_quality_style_list),
    path('get_st_delivery_quality_style_list/',views.get_st_delivery_quality_style_list),
    path('add-stitching-outward/',views.insert_stiching_outward), 
    path('stitching-outward-ajax-report/',views.ajax_report_stiching_outward),
    path('stitching-delivery-edit/',views.stiching_delivery_edit),
    path('stitching-delivery-delete/',views.delete_stiching_delivery),


    # tx-data-list

    path('stitching-delivery-detail-ajax-report/',views.tx_details_list),

    path('get_cutting_stock_modal/',views.get_cutting_stock_modal),
    path('get_stitching_delivery_data/',views.get_stiching_delivery_data),
    path('get_stitching_delivery_summary/',views.get_stitching_delivery_summary),

    path('update-stitching-outward/',views.update_stiching_outward), 
    path('stitching-delivery-print/',views.stiching_delivery_print),
    path('delete_stiching_entry/', views.delete_stiching_entry),

    path('update_stitching_delivery_data/',views.update_stiching_data),
    
    path('stiching-out-master-update/',views.update_master_data), 
    
    # `````````````````````` stiching received ``````````````````````````````


    path('stitching-received',s_inw.stiching_received),  
    path('stitching-received-add/',s_inw.stiching_received_add),   

    path('get_stitching_delivery_list/',s_inw.get_stiching_delivery_list),
    path('get_party_stiching_delivery_list/',s_inw.get_party_stiching_delivery_list),
    path('get-stitching-delivery-details/',s_inw.get_stiching_delivery_details),
    path('get_stitching_delivery_edit_details/',s_inw.get_stiching_delivery_edit_details),

    path('add-stitching-received/',s_inw.insert_stiching_received), 
   
    path('stitching-received-ajax-report/',s_inw.ajax_report_stiching_received),
    path('stitching-received-edit/',s_inw.stiching_received_edit),
    path('stitching-received-delete/',s_inw.delete_stiching_received),

    path('update-stitching-received/',s_inw.update_stiching_received),
    path('stitching-received-print/',s_inw.stiching_received_print),

    path('stiching-received-master-update/',s_inw.update_stitching_received_data),
     # `````````````````````` Packing Delivery ``````````````````````````````


    path('packing-delivery',p_out.packing_delivery),  
    path('packing-delivery-ajax-report/',p_out.packing_delivery_list),

    path('packing-delivery-add/',p_out.packing_delivery_add),   
    path('get_stiching_received_list/',p_out.get_stiching_received_avl_list),
    path('get_stiching_summary_stock/',p_out.get_stiching_summary_stock),
    path('get_stiching_inward_edit_details/',p_out.get_stiching_inward_edit_details),
    path('add-packing-outward/',p_out.insert_packing_outward),

    path('packing-delivery-edit/',p_out.edit_packing_delivery),
    path('packing-delivery-delete/',p_out.delete_packing_delivery),
 
    path('update-packing-outward/',p_out.update_packing_delivery),

    path('packing-delivery-print/',p_out.packing_delivery_print),  
     # `````````````````````` Packing Inward ``````````````````````````````

 
    path('packing-received',p_inw.packing_received),  
    path('packing-received-add/',p_inw.packing_received_add),   

    path('validate-program-style-quality/',p_inw.validate_program_style_quality),
    path('get_packing_delivery_list/',p_inw.get_packing_outward_list),
    path('get_stiching_packing_delivery_list/',p_inw.get_stiching_packing_delivery_list),
    path('get_party_outward_lists/',p_inw.get_party_outward_lists),

    path('get_party_outward_available_lists/',p_inw.get_party_outward_available_lists), 
    path('get-packing-delivery-list/',p_inw.get_packing_delivery_list), 
    path('get-stiching-delivery-data/',p_inw.get_stiching_packing_delivery_data), 
    

 
    # edit screen 


    path('get_packing_delivery_update_list/',p_inw.get_packing_delivery_update_list),
    path('get_stiching_delivery_update_list/',p_inw.get_stiching_delivery_update_list),
    
    path('add-packing-received/',p_inw.insert_packing_received),
    path('packing-received-ajax-report/',p_inw.packing_received_ajax_report),

    path('packing-received-edit/',p_inw.packing_received_edit),
    path('packing-received-detail-ajax-report/',p_inw.packing_received_detail_list),

    path('edit-packing-received/',p_inw.edit_packing_received), 
    path('delete-packing-received/',p_inw.delete_packing_received), #tm table
    path('packing-received-delete/',p_inw.packing_received_delete),  #tx table

    path('update-packing-received/',p_inw.update_packing_received),
    path('check_existing_packing_received/',p_inw.check_existing_packing_received),
    path('packing-received-print/',p_inw.packing_received_print),

    path('packing-received-master-update/',p_inw.update_packing_received_data), 

 
    # `````28-8-2025`````


    path('get-packing-delivery-color-list/',p_inw.get_packing_outward_color_lists),
    path('get-stiching-delivery-color-list/',p_inw.get_stitching_outward_color_lists),
    path('get-existing-loose-pcs/',p_inw.get_existing_loose_pcs),

    # `````````loose pcs entry ```````````````````````````````````


    path('loose-pcs-delivery',lp.loose_pcs_entry),
    path('loose-pcs-entry-add',lp.loose_pcs_entry_add),
    path('add-loose-pcs-entry/',lp.insert_loose_pcs_entry),

    path('get-lp-party-outward-list/',lp.get_lp_party_outward_lists),
    path('get-lp-update-party-outward-list/',lp.get_lp_update_party_delivery_list), 
    path('get-packing-deliver-list/',lp.get_packing_delivery_list),
    path('get-stitching-delivery-list/',lp.get_stitching_delivery_lists),
    path('get-packing-delivery-lists/',lp.get_packing_delivery_lists),
    path('lp-entry-ajax-report/',lp.loose_pcs_entry_report_list), 

    path('lp-entry-delete/',lp.tm_lp_entry_delete),
    path('tx-lp-entry-delete/',lp.tx_lp_entry_delete), 
    path('loose-pcs-entry-print/',lp.lp_entry_print),
    path('loose-pcs-entry-edit/',lp.edit_lp_entry),
    path('lp-entry-data-edit/',lp.loose_pcs_data_edit),
    path('lp-entry-tx-report/',lp.tx_lp_entry_list),

    path('check_existing_loose_pcs_entry/',lp.check_existing_lp_entry),
    path('update-loose-pcs-data/',lp.update_lp_data),




    # ```````````````````` FOLDING DELIVERY ``````````````````

    path('folding-delivery',fd.folding_delivery),
    path('folding-outward-ajax-report/',fd.folding_delivery_report),
    path('get_c_entry_list/',fd.get_cutting_entry_list),

    path('folding-delivery-add',fd.folding_delivery_add),
    path('get_cutting_entry_folding_details/',fd.get_cutting_entry_folding_details),
    path('get_st_delivery_folding_details/',fd.get_st_delivery_folding_details), 
    path('get_cutting_entry_folding_details_update/',fd.get_cutting_entry_folding_details_update), 
    path('get_st_delivery_folding_details_update/',fd.get_st_delivery_folding_details_update),
    path('get_entry_details/',fd.get_entry_details),
    path('get_st_delivery_details/',fd.get_st_delivery_details),

    path('add-folding-outward/',fd.insert_folding_delivery),
    path('folding-delivery-edit/',fd.folding_delivery_edit),
    path('folding-delivery-delete/',fd.delete_folding_delivery),
    path('folding-delivery-print/',fd.folding_delivery_print),    
    path('folding-delivery-update/',fd.update_folding_delivery),    
    path('folding-delivery-master-update/',fd.update_master_folding_delivery),    
 





] 