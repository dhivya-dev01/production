from django.contrib import admin

from program_app import program, cutting_prg as cp,folding_prg as fp


from django.urls import path, include

urlpatterns = [

    # knitting  program 

    path('knitting',program.knitting_program), 
    # path('get_fabric_program_lists/',program.get_fabric_lists), 
    path('add-knitting-program/',program.add_knitting),

    path('knitting-program',program.knitting),
    path('knitting-program-list/',program.knitting_program_list),
    path('knitting_detail_delete/',program.knitting_program_delete), 
    path('knitting-details-edit/',program.knitting_program_edit),
    path('knitting-program-print/',program.program_print),  


    path('update-knitting-list/',program.tx_knitting_list),

    path('knitting-details-update/',program.tm_knitting_details_update),
    path('tx_knitting_detail_edit/',program.tx_knitting_detail_edit), 
    path('delete-knitting/',program.delete_knitting_program),
    path('update-knitting-program/',program.update_knitting_program),



  
  
    # Dyeing program


    path('dyeing-program',program.dyeing_program),  
    path('dyeing-program-add',program.add_dyeing_program),

    path('get_lot_fabric_list/',program.get_lot_fabric_list),
    path('get-lot-details/',program.get_outward_lot_no_details),
    path('get_fabric_dia_list/',program.get_fabric_dia_list),
    path('add-dyeing-program/',program.insert_dyeing_program),

    path("get-colors/", program.get_colors_for_fabric, name="get_colors_for_fabric"),

    path("get-fabric-details/", program.get_fabric_details, name="get_fabric_details"),
    path("save-dyeing-program/", program.save_dyeing_program, name="save_dyeing_program"),
    path('dyeing-program-view/',program.dyeing_program_list),

    path('dyeing-program-print/',program.dyeing_program_print),
    path('dyeing-program-edit/',program.dyeing_program_edit),  

    path('dyeing-tx-program-view/',program.tx_dyeing_program),
    path('ajax-dyeing-program-deatil/',program.dyeing_program_detail_ajax_report),
    path('update_sub_dyeing_program/', program.update_sub_dyeing_program),
    path('dyeing_program_delete/',program.dyeing_program_delete),
    path('dyeing-details-update/',program.update_dyeing_master),

    
    path('update-dyeing-program/',program.update_dyeing_program),

    path('get-fabric-dias/',program.get_fabric_dias),

    path('add-fabric-rolls/',program.add_fabric_rolls), 
    # path('dyeing-update/',program.tm_dyeing_update), 


    #```````````````````````````````````` cutting program ``````````````````````````````
    path('cutting-program',cp.cutting_program),
    path('cutting-program-view/',cp.cutting_prg_view),    
     
    path('cutting-program-add',cp.add_cutting_program),
    path('get_quality_fabric_list/',cp.get_quality_fabric_list),

    path('add-cutting-program/',cp.save_cutting_program),
    path('cutting-program-edit/',cp.cutting_program_edit),

    path('update-cutting-list/',cp.tx_cutting_program_list),
    path('cutting-prg-detail-edit/',cp.edit_cutting_prg_detail),

    path('update-cutting-program/',cp.update_cutting_program),
    path('check_existing_cutting_program/',cp.check_existing_cutting_program),

    path('delete-cutting-prg/',cp.tm_cutting_prg_delete),
    path('tx-cutting-prg-delete/',cp.tx_cutting_prg_delete),

    path('get_quality_style_list/',cp.get_quality_style_list),
    path('cutting-program-print/',cp.cutting_program_print),
    path('cutting-prg-details-update/',cp.cutting_program_update),
    path('get-material-instance/', cp.get_material_instance, name='get_material_instance'),

# 14-03-2025
    path('get_size_list/', program.get_size_list, name='get_size_list'),
    path('get_color_list/',program.get_color_list),
    path('get_color_lists/',program.get_color_lists),
    path('get_quality_size_list/',program.get_quality_size_list),

   
   
    # accessory program

    path('accessory-program',program.accessory_program),
    path('accessory-program-add',program.add_accessory_program),
    path('accessory-program-view/',program.accessory_program_view),   
    path('accessory-program-edit/',program.accessory_program_edit),
    path('update-acc-ratio-list/',program.update_acc_ratio_view),
    path('edit-acc-ratio/',program.edit_acc_ratio_settings),
    path('acc-ratio-update/',program.acc_ratio_update),
    path('update-size/', program.update_size, name='update_size'),  # Map to the update_size view

    path('update_save_color_selection/',program.update_save_color_selection),
    path('tx-acc-delete/',program.tx_acc_ratio_delete),
    path('tm-acc-delete/',program.tm_acc_ratio_delete),

    path('tx-acc-edit/',program.tx_acc_ratio_edit),
    path('update-quantity/',program.update_quantity),

    path('get_quality_item_list/',program.get_quality_item_list),

    path('get_style_based_sizes/',program.get_style_based_sizes), 
    path('add-accessory-program/',program.save_accessory_program),


    path('get_acc_quality_item_list/',program.get_acc_quality_item_list),
    path('get_acc_size_list/',program.get_acc_size_list),
    path('get_acc_quality_list/',program.get_acc_quality_list), 
    path('get_acc_item_size_list/',program.get_acc_item_size_list),



    # ```````````````` FOLDING ``````````````````````````````````````



    path('folding-program',fp.folding_program),
    path('folding-program-add',fp.folding_program_add), 
    path('folding-program-ajax-report/',fp.folding_program_report),
    path('folding-program-edit/',fp.folding_program_edit),
    path('folding-prg-delete/',fp.delete_folding_program),



    path('add-folding-program/',fp.insert_folding_program), 
    path('update-folding-program/',fp.update_folding_program), 

]