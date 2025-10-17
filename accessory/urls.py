
from django.contrib import admin

from accessory import views, accessory_po as acc_po,  accessory_inward as acc_in,accessory_outward as acc_out
from .views import *
from django.urls import path, include

urlpatterns = [


    # ``````````views.py`````````````````
   
    path('item-group',views.item_group),
    
    path('item-group-list/',views.item_group_list),
    path('item-group-add/',views.item_group_add),
    path('item-group-edit/',views.item_group_edit),
    path('item-group-update/',views.item_group_update),
    path('item-group-delete/',views.item_group_delete),



    path('accessory-quality',views.accessory_quality),
    
    path('accessory-quality-list/',views.accessory_quality_list),
    path('accessory-quality-add/',views.accessory_quality_add),
    path('accessory-quality-edit/',views.accessory_quality_edit),
    path('accessory-quality-update/',views.accessory_quality_update),
    path('accessory-quality-delete/',views.accessory_quality_delete),



    path('accessory-size',views.accessory_size),
    
    path('accessory-size-list/',views.accessory_size_list),
    path('accessory-size-add/',views.accessory_size_add),
    path('accessory-size-edit/',views.accessory_size_edit),
    path('accessory-size-update/',views.accessory_size_update),
    path('accessory-size-delete/',views.accessory_size_delete),


    path('accessory-color',views.accessory_color),
    
    path('accessory-color-list/',views.accessory_color_list),
    path('accessory-color-add/',views.accessory_color_add),
    path('accessory-color-edit/',views.accessory_color_edit),
    path('accessory-color-update/',views.accessory_color_update),
    path('accessory-color-delete/',views.accessory_color_delete),



    path('check-duplicate/',views.check_duplicate_item),
    path('item',views.item),
    path('get_size/',views.get_size),
    path('item-list/',views.item_list),
    path('item-add/',views.item_add),
    path('item-edit/',views.item_edit),
    path('item-update/',views.item_update),
    path('item-delete/',views.item_delete), 
 

    path('item-quality-list/',views.item_quality_list),
    path('item-size-list/',views.item_size_list), 

 

    path('edit-quality/', views.edit_quality, name='edit_quality'),
    path('delete-quality/', views.delete_quality, name='delete_quality'),
    path('edit-size/', views.edit_size, name='edit_size'),
    path('delete-size/',views. delete_size, name='delete_size'),
    path("update-quality/", views.update_quality, name="update_quality"),
    path("update-size/", views.update_size, name="update_size"),
    path("update-sizes/", views.update_sizes),
    path("add-quality/", views.add_quality, name="add_quality"),
    path("add-size/", views.add_size, name="add_size"),

        # uom
    path('style',views.style),
    path('style-list/',views.style_list),
    path('style-add/',views.style_add),
    path('style-edit/',views.style_edit),
    path('style-update/',views.style_update),
    path('style-delete/',views.style_delete),


    path('size',views.size),
    path('size-list/',views.size_list),
    path('size-add/',views.size_add),
    path('size-edit/',views.size_edit),
    path('size-update/',views.size_update),
    path('size-delete/',views.size_delete),



    path('group',views.group),
    path('group-list/',views.group_list),
    path('group-add/',views.group_add),
    path('group-edit/',views.group_edit),
    path('group-update/',views.group_update),
    path('group-delete/',views.group_delete),



    path('quality',views.quality),
    path('quality-list/',views.quality_list),
    path('quality-add/',views.quality_add),
    path('quality-edit/',views.quality_edit),
    path('quality-update/',views.quality_update),
    path('quality-delete/',views.quality_delete),




    path('quality-prg',views.quality_program),
    path('quality-prg-add/',views.quality_program_add),  
    path('quality-prg-list/',views.quality_program_list),
    path('quality-prg-edit/',views.quality_prg_edit),
    path('quality-prg-delete/',views.quality_prg_delete),

    path('quality-prg-size-list/',views.quality_prg_size_list),
    path('prg-size-edit/',views.prg_size_edit),
    path('prg-size-delete/',views.prg_size_delete),
    path('prg-size-update/',views.prg_size_update),
    path('check-size-id/',views.check_size_id),


    # `````````` accessory po ``````````````````````````
 
    path('accessory-po',acc_po.accessory_po),
    path('add-po',acc_po.add_po), 
    path('get_acc_item_list/',acc_po.get_item_list), 
    path('get_acc_list/',acc_po.get_acc_value_list),

    path('purchase-order-add/',acc_po.purchase_order_add),
    path('purchase-order-view/',acc_po.purchase_order_view),
    path('po-details-edit/',acc_po.po_details_edit),  
    path('update_po_lists/',acc_po.update_po_lists),  
    path('acc_po_detail_edit/',acc_po.po_detail_edit),  
    path('update-acc-po-item/',acc_po.accessory_po_items_update),
    path('acc_po_detail_delete/',acc_po.po_detail_delete), # child data
    path('accessory-po-detail-delete/',acc_po.accessory_po_detail_delete), # PARENT & child data

    path('accessory-po-details-update/',acc_po.update_accessory_po_details),
    path('print_accessory_po/',acc_po.print_accessory_po),


    # `````````````````````` accessory inward ```````````````````````````````````````````````````````````````````````````



    path('accessory-inward',acc_in.accessory_inward),
    path('accessory-inward-add',acc_in.accessory_inward_add),
    
    path('get_party_lists/',acc_in.get_party_lists),

    path('get_accessory_po_list/',acc_in.get_accessory_po_list),
    path('get_accessory_pos/',acc_in.get_accessory_pos),
    path('get_accesory_po_details/',acc_in.get_accesory_po_details),

    path('get_accessory_do_list/',acc_in.get_accessory_do_list),  ## stiching delivery list 

    path('get_packing_deliver_list/',acc_in.get_packing_delivery_list),

    path('add-accessory-inward/',acc_in.insert_accessory_inward),
    path('accessory-inward-view/',acc_in.accessory_inward_list),  
    path('acc-inward-details-edit/',acc_in.acc_inward_edit),

    path('update_accessory_inward/',acc_in.update_accessory_inward),
    path('accessory-inward-data-update/',acc_in.update_tm_accessory_inward_data),
    # path('delivery',acc_in.accessory_delivery),
    path('acc-inw-print/',acc_in.print_accessory_inward),
    

    # ````````````````````` accessory outward ```````````````````````````````````````````````````````````````````````````


    path('accessory-out',acc_out.accessory_outward),
    path('accessory-outward-add/',acc_out.accessory_outward_add), 

    path('accessory-outward-ajax-report/',acc_out.accessory_outward_report),

    path('get_delivery_party_list/',acc_out.get_delivery_party_list),   
    path('get_stiching_list_by_supplier/',acc_out.get_stiching_list_by_supplier),
    path('get_accessory_program_list/',acc_out.get_accessory_program_list),
    path('get_stiching_out_details/',acc_out.get_stiching_out_details),
    path('get_stiching_out_details_edit/',acc_out.get_stiching_out_details_edit),

    path('get_stiching_out_details_list/',acc_out.get_stiching_out_details_list),
    path('get_stiching_quality_style/',acc_out.get_stiching_quality_style),


    path('get_stiching_packing_list/',acc_out.get_stiching_packing_list), 
    path('get_stiching_packing_quality_style/',acc_out.get_stiching_packing_quality_style_list),
    path('get_stitching_packing_out_details/',acc_out.get_stiching_packing_out_details),

    path('get_packing_list/',acc_out.get_packing_list), 
    path('get_packing_quality_style/',acc_out.get_packing_quality_style), 
    path('get_packing_accessory_program_list/',acc_out.get_packing_accessory_program_list),
    path('get_packing_out_details/',acc_out.get_packing_out_details),  
    path('get_packing_out_details_edit/',acc_out.get_packing_out_details_edit),

    path('get_stiching_packing_out_details_edit/',acc_out.get_stiching_packing_out_details_edit), 

    path('add-accessory-outward/',acc_out.insert_accessory_outward),
    path('update-accessory-outward/',acc_out.update_acc_outward),


    # path('accessory-outward-list/',acc_out.accessory_outward_report),  
    # path('acc-outward-details-edit',acc_out.edit_accessory_outward),
    path('acc-outward-delete/',acc_out.delete_accessory_outward),
    path('acc-outward-details-edit/',acc_out.edit_acc_outward),

    path('get_accessory_items/',acc_out.get_accessory_items),
    path('get_accessory_item_group/',acc_out.get_accessory_item_group),

    path('get_dyeing_out_details_list/',acc_out.get_dyeing_out_details_list),
 
    path('get_quality/',acc_out.get_quality),
 
    path('acc-out-print/',acc_out.accessory_out_print),

] 


