from django.contrib import admin

from software_app import views

from .views import *
from django.urls import path, include

urlpatterns = [


    # ``````````views.py`````````````````

 
    # path('', views.signin_admin), 
    # path('signin', views.login), 
    # path('logout',views.logout),
    # path('dashboard', views.dashboard), 

    # path('company',views.company),
    # path('profile',views.profile),
    # path('update_company/',views.update_company, name='update_company'), 
    
    path('party',views.customers), 
    path('party-list/',views.party_list_view),

    path('party-add',views.customer_entry),
    path('party_detail_add/',views.customer_add),
    path('party_details_edit/', views.party_details_edit, name='party_details_edit'),

    path('party_detail_update/',views.party_detail_update), 
    path('party_delete/',views.party_delete),
    path('add_party_photo/',views.add_party_photo),
    path('party_photo_view/',views.party_photo_view),


    # path('', contact_list, name="contact_list"),
    path('add-contact/', views.add_contact, name="add_contact"),
    path('delete-contact/<int:contact_id>/', views.delete_contact, name="delete_contact"),

    path('delete-photo/<int:photo_id>/', views.delete_photo, name="delete_photo"),
    path('edit-photo/<int:photo_id>/', views.edit_photo_remarks, name="edit_photo"),
    path('update-photo/<int:photo_id>/', views.update_photo, name="update_photo"),
    path("update-contact/<int:contact_id>/", views.update_contact, name="update_contact"),


    # uom
    path('uom',views.uom),
    path('uoms/',views.uom_list),
    path('uom-add/',views.uom_add),
    path('uom-edit/',views.uom_edit),
    path('uom-update/',views.uom_update),
    path('uom-delete/',views.uom_delete),

    path('color',views.color),
    path('colors/',views.color_list),
    path('color-add/',views.color_add),
    path('color-edit/',views.color_edit),
    path('color-update/',views.color_update),
    path('color-delete/',views.color_delete),


    path('dia',views.dia),
    path('dia-view/',views.dia_list),
    path('dia-add/',views.dia_add),
    path('dia-edit/',views.dia_edit),
    path('dia-update/',views.dia_update),
    path('dia-delete/',views.delete_dia),

    # gauge
    path('gauge',views.gauge),
    path('gauge-view/',views.gauge_list),
    path('gauge-add/',views.gauge_add),
    path('gauge-edit/',views.gauge_edit),
    path('gauge-update/',views.gauge_update),
    path('gauge-delete/',views.gauge_delete),


    # tex
    path('tex',views.tex),
    path('tex-view/',views.tex_list),
    path('tex-add/',views.tex_add),
    path('tex-edit/',views.tex_edit),
    path('tex-update/',views.tex_update),
    path('tex-delete/',views.tex_delete),

    path('tax',views.tax), 
    path('tax-view/',views.tax_list),
    path('tax-add/',views.tax_add),
    path('tax-edit/',views.tax_edit),
    path('tax-update/',views.tax_update),
    path('tax-delete/',views.tax_delete), 


    path('item-group',views.item_group),
    path('item-group-view/',views.item_group_list), 
    path('item-group-add/',views.item_group_add),
    path('item-group-edit/',views.item_group_edit),
    path('item-group-update/',views.item_group_update),
    path('item-group-delete/',views.item_group_delete), 

    path('mx-item',views.mx_item),
    path('item-view/',views.item_list),
    path('item-add/',views.item_add),
    path('item-edit/',views.item_edit),
    path('item-update/',views.item_update),
    path('item-delete/',views.item_delete), 


    path('count',views.count),
    path('count-list/',views.count_list),
    path('count-add/',views.count_add),
    path('count-edit/',views.count_edit),
    path('count-update/',views.count_update),
    path('count-delete/',views.count_delete),


    path('bag',views.bag),
    path('bag-list/',views.bag_list),
    path('bag-add/',views.bag_add),
    path('bag-edit/',views.bag_edit),
    path('bag-update/',views.bag_update),
    path('bag-delete/',views.bag_delete),


    path('fabric',views.fabric),
    path('fabric-list/',views.fabric_list),
    path('fabric-add/',views.fabric_add),
    path('fabric-edit/',views.fabric_edit),
    path('fabric-update/',views.fabric_update),
    path('fabric-delete/',views.fabric_delete),


    path('fabric-program',views.fabric_program),
    path('fabric_prg-list/',views.fabric_prg_list),
    path('fabric_prg-add/',views.fabric_prg_add),
    path('fabric_prg-edit/',views.fabric_prg_edit),

    path('fabric_prg_dia_edit/',views.fabric_prg_dia_edit),
    path('fabric_dia_list/',views.fabric_dia_list),
    path('dia-edit/',views.fabric_dia_edit),
    path('save-dia-edit/',views.update_dia),
    path('dia-delete/',views.dia_delete),


    path('fabric_prg-update/',views.fabric_prg_update),
    path('fabric_prg-delete/',views.fabric_prg_delete),




    path('yarn-item',views.product),
    path('product-list/',views.product_list),
    path('product-add/',views.product_add),
    path('product-edit/',views.product_edit),
    path('product-update/',views.product_update),
    path('product-delete/',views.product_delete),

    # path('employee',views.employee),
    # path('employee-list/',views.employee_list),
    # path('employee-add/',views.employee_add),
    # path('employee-edit/',views.employee_edit),
    # path('employee-update/',views.employee_update),
    # path('employee-delete/',views.employee_delete), 


    # `````````````` TASK ``````````````````````````````

    path('task',views.task),
    path('task_add/',views.task_add),
    path('task_report/',views.task_report),
    path('task_edit/',views.task_edit),
    path('task_update/',views.task_update),
    path('task_delete/',views.task_delete),
    path('task_followup/',views.task_followup),

    path('get_remarks/',views.get_remarks_list),
    path('followup_add/',views.followup_add),
    path('followup_report/',views.followup_report),

 
    path('task-library',views.task_library),
    path('library_add/',views.library_add),
    path('library_report/',views.library_report),
    path('library_edit/',views.library_edit),
    path('library_update/',views.library_update),
    path('library_delete/',views.library_delete),

    path('remarks_page/',views.remarks_page),
    path('remarks_add/',views.remarks_add),
    path('remarks_report/',views.remarks_report),
    path('remarks_edit/',views.remarks_edit),
    path('remarks_update/',views.remarks_update),
    path('remarks_delete/',views.remarks_delete),


    # ````````package`````````````````

 
    path('package',views.package),
    path('package-add/',views.package_add),  
    path('package-list/',views.package_list),
    # path('package-edit/',views.package_edit), 
    # path('package-delete/',views.package_delete),

    # path('package-size-list/',views.package_size_list),
    # path('package-size-edit/',views.package_size_edit),
    # path('package-size-delete/',views.package_size_delete),
    # path('package-size-update/',views.package_size_update),


    # ``````````````````````````````````````````````
 
    path('company-settings',views.email_settings_page),
    path('email-add/',views.add_email_settings),
    path('email-list/',views.email_list),
    path('email-edit/',views.email_edit),

    path('sms-update/',views.update_sms),



    # ````````````` KNITTING```````````````````````````````````
    # path('knitting',views.knitting_program),
    path('get_fabric_program_lists/',views.get_fabric_lists),
    # path('add-knitting-program/',views.add_knitting),

    # path('knitting-program',views.knitting),
    # path('knitting-program-list/',views.knitting_program_list),
    # path('knitting_detail_delete/',views.knitting_program_delete),

    # path('knitting-details-edit/',views.knitting_program_edit),
    # path('update-knitting-list/',views.tx_knitting_list),
    # path('tx_knitting_detail_edit/',views.tx_knitting_detail_edit),
    # path('delete-knitting/',views.delete_knitting_program),  
    # path('update-knitting-program/',views.update_knitting_program),

    path('get_inward_lists/',views.get_inward_lists), 
    path('get_po_lists/',views.get_po_lists),
    path('get_po_fabric_lists/',views.get_po_fabric_lists),
    # path('get_program_lists/',views.get_program_lists),
    path('get_fabric_details/',views.get_fabric_details),
    # path('get_lot_no/',views.get_lot_no),
    path('get_delivery_details/',views.get_delivery_details),

    path('get_bag_wt/',views.get_bag_wt),
    path('load_knitting_program_detail/',views.load_knitting_program_detail),


    # path('yarn-inward-delete/',views.yarn_inward_delete), 
    # path('get_inward_lists/',views.get_inward_lists),
    # path('get_inward_details/', views.get_inward_details, name='get_inward_details'),

    path('get_po_delivery_details/',views.get_po_delivery_details),

# get_po_fabric_lists

    path('load-purchase-orders/',views.load_po_details),

    path('load_po_details_inward/',views.load_po_details_inward),
    path('load-inward-orders/',views.load_yarn_inward_details),
    # path('get_deliver_to_for_po/', views.get_deliver_to_for_po, name='get_deliver_to_for_po'),
    path('get_deliver_lists/',views.get_deliver_lists),
    path('get_process_deliver_lists/',views.get_process_deliver_lists),


    path('check-lot/',views.check_duplicate_lot_no),

# ````````````yarn outward ``````````````


    # path('yarn-deliver',views.yarn_delivery),
    # path('knitting-deliver',views.knitting_delivery),
    # path('add-knitting-deliver/',views.add_knitting_delivery),


    # path('yarn-knitting-delivery/',views.yarn_delivery_list),
    # path('yarn-deliver-edit/',views.yarn_deliver_edit), 
    # path('yarn_deliver_delete/',views.yarn_deliver_delete), 
    # path('yarn-deliver-lists/',views.tx_yarn_deliver_list),
    # path('delete-yarn-deliver/',views.tx_yarn_deliver_delete),

    # print knitting
    path('knitting-print/',views.knitting_print),

    # path('yarn-deliver-detail-edit/',views.delivered_yarn_edit),
    # path('update-knitting-deliver/',views.update_knitting_delivery),

    path('create-debit-note/',views.create_debit_note),
    path('debit-edit/',views.debit_note),

    path('voucher',views.view_voucher),
    path('voucher-list/',views.voucher_list_view),
    path('voucher-edit/',views.voucher_edit), 

    path('voucher-add',views.voucher),
    path('get_supplier_payable_amount/',views.get_supplier_payable_amount),
    path('add-voucher/',views.add_voucher_details),

    path('production-deliver',views.production_delivery_page),
    path('get-knitting-lists/',views.get_knitting_program_list),
    path('load-knitting-deliver/',views.load_knitting_deliver),


    path('get-supplier-list/',views.get_supplier_list),




    # yarn inward

    path('get-knitting-programs/', views.get_knitting_programs, name='get_knitting_programs'),
    path('get_knitting_details/',views.get_knitting_details),
    path('knit-prg-list/',views.knitting_prg_lists),


    # path('yarn-inward-add',views.yarn_inward), 
    # path('add-yarn-inward/',views.add_yarn_inward),
    # path('yarn-inward',views.yarn_list),
    # path('yarn-inward-view/',views.yarn_inward_list),  
    # path('yarn-details-edit/',views.inward_detail_edit),

    # path('yarn-inward-update-view/',views.update_yarn_inward_list),
    # path('add-or-update-inward-item/',views.add_or_update_inward_item),
    # path('inward-detail-delete/',views.inward_detail_delete),
    # path('inw_detail_edit/',views.inward_details_edit),
    # # path('inw_detail_edit/',views.inward_detail_edit),


    
    
]   