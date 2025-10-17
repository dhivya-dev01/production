
from django.contrib import admin

from cutting_entry import views

from cutting_entry.views import * 
from django.urls import path, include

urlpatterns = [



  # ```````````````````````````````` cutting entry ``````````````````````````````````````
    path('cutting-entry',views.cutting_entry),  
    path('cutting-entry-view/',views.cutting_entry_view),   
    path('cutting-entry-add',views.add_cutting_entry),
    path('get_quality_style_fabrics_list/',views.get_quality_style_fabrics_list),

    path('get_cutting_program_list/',views.get_cutting_program_list),
    path('add-cutting-entry/',views.insert_cutting_entry),

    path('cutting-entry-edit/',views.cutting_entry_edit),
    path('cutting-entry-detail-edit/',views.edit_cutting_entry_detail),

    path('cutting-entry-ajax-report/',views.tx_cutting_entry_list),
    path('get_cutting_program_lists/',views.get_cutting_program_lists),
    path('get_sub_cutting_program/',views.get_sub_cutting_program), 
    


    path('check_existing_cutting_entry/',views.check_existing_cutting_entry),
    path('update-cutting-entry-details/',views.update_cutting_values),

    # path('tx-cutting-entry-list/',views.tx_cutting_entry_list),

    path('cutting-entry-delete/',views.tm_cutting_entry_delete), 
    path('tx-cutting-entry-delete/',views.tx_cutting_entry_delete),
    path('cutting-entry-abstract-print/',views.cutting_entry_abstract_print),
    path('cutting-entry-print/',views.cutting_entry_print),
    path('cutting-entry-qrcode-print/',views.cutting_qr_code_print),
    path('cutting/barcode-detail/',views.cutting_barcode_detail, name='cutting_barcode_detail'),

    path('update-cutting-entry-summary/',views.update_cutting_summary),

    path('cutting-entry-tm-update/',views.cutting_entry_tm_update),


]