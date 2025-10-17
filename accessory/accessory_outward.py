


from os import stat
from django.shortcuts import render
from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify 

from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
# from accessory.forms import *
import datetime

from datetime import datetime
from datetime import date
from django.utils import timezone

from django.db.models import Count 


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from accessory.models import *

from django.views.decorators.http import require_http_methods

from django.core.exceptions import ObjectDoesNotExist
import base64 
from django.core.files.base import ContentFile
from django.conf import settings
import hashlib
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models import Max
from django.db import IntegrityError

import json 
from django.db import transaction
import logging
from django.db.models import F, OuterRef, Subquery, Value
from dateutil.parser import parse as parse_date 
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.templatetags.static import static
from django.core.serializers import serialize 
from datetime import timedelta

import uuid 

from openpyxl import load_workbook # excel
from django.core.mail import send_mail


from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required

from django.core.signing import Signer, BadSignature

import requests
from django.db.models.functions import ExtractYear, ExtractMonth


from django.shortcuts import redirect
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from django.middleware.csrf import get_token
from django.conf import settings
from google.auth.transport.requests import AuthorizedSession
import hashlib

from django.utils.text import slugify

from django.core.exceptions import ValidationError

from django.http import HttpResponseBadRequest

from accessory.views import quality
from production_app.models import child_packing_outward_table, child_stiching_outward_table, parent_packing_outward_table, parent_stiching_outward_table
from yarn.views import *
from software_app.models import *
from collections import defaultdict

# `````````````````````````````````````````````````````````````````````



def generate_outward_no():
    last_purchase = parent_accessory_outward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.outward_no:
        match = re.search(r'DO-(\d+)', last_purchase.outward_no) 
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"DO-{next_num:03d}"




def accessory_outward(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter( Q(is_trader=1) | Q(is_supplier=1) | Q(is_stiching=1) | Q(is_ironing=1),status=1)
        product = product_table.objects.filter(status=1)

        return render(request,'outward/outward_list.html',{'party':party,'product':product })
    else:
        return HttpResponseRedirect("/admin")


def accessory_outward_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(
                Q(is_trader=1) | Q(is_supplier=1),
                status=1
            )    
        
        product = product_table.objects.filter(status=1)
        program = accessory_program_table.objects.filter(status=1)
        quality= quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1) 
  
        acc_item = item_table.objects.filter(status=1)
        size= size_table.objects.filter(status=1)  
        uom = uom_table.objects.filter(status=1)
        print('sizes:',size)
        print('prgs:',program)
        out_no = generate_outward_no()
        acc_group = item_group_table.objects.filter(status=1)
        return render(request,'outward/outward_add.html',{'party':party,
                                                          'product':product,
                                                          'program':program ,
                                                          'outward_no':out_no,
                                                          'quality':quality,
                                                          'style':style,
                                                          'uom':uom,
                                                          'size':size,
                                                          'acc_group':acc_group,
                                                          'acc_item':acc_item}) 
    else:
        return HttpResponseRedirect("/admin")




# def get_accessory_items(request):
#     if request.method == 'GET':
#         material_type = request.GET.get('type')  # ✅ Corrected from POST to GET

#         try:
#             # Determine item group filter based on material_type
#             material_type = material_type.upper() if material_type else ""
#             group_mapping = {
#                 'STICHING': ['STICHING', 'STITCHING'],
#                 'PACKING': ['PACKING'],
#                 'SP': ['STICHING', 'PACKING']
#             }

#             item_group_id = 0 
#             group_types = group_mapping.get(material_type)

#             if group_types:
#                 item_group_qs = item_group_table.objects.filter(status=1, group_type__in=group_types)
#                 item_group_obj = item_group_qs
#                 if item_group_obj:
#                     item_group_id = item_group_obj.id

#             print('item-group-id:', item_group_id)

#             items = item_table.objects.filter(item_group_id=item_group_id, status=1)

#             item_group_list = [{'id': item_group_id, 'name': item_group_obj.name}] if item_group_obj else []
#             item_list = [{'id': item.id, 'name': item.name} for item in items]
#             item_ids = [item.id for item in items]

#             sub_values = sub_size_table.objects.filter(status=1, item_id__in=item_ids)

#             quality_ids = sub_values.values_list('quality_id', flat=True).distinct()
#             size_ids = sub_values.values_list('size_id', flat=True).distinct()
#             color_ids = sub_values.values_list('m_color_id', flat=True).distinct()

#             qualities = accessory_quality_table.objects.filter(id__in=quality_ids)
#             sizes = accessory_size_table.objects.filter(id__in=size_ids)
#             colors = color_table.objects.filter(id__in=color_ids)

#             quality_list = [
#                 {'id': q.id, 'name': f"{q.name} - ({q.po_name if q.po_name else '-'})"} for q in qualities
#             ]
#             size_list = [
#                 {'id': s.id, 'name': f"{s.name} - ({s.po_name if s.po_name else '-'})"} for s in sizes
#             ]
#             color_list = [{'id': c.id, 'name': c.name} for c in colors]

#             return JsonResponse({
#                 'success': True,
#                 'item_group': item_group_list,
#                 'item': item_list,
#                 'qualities': quality_list,
#                 'sizes': size_list,
#                 'colors': color_list,
#             })

#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)}, status=500)

#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)



def get_accessory_items(request):
    if request.method == 'GET':
        material_type = request.GET.get('type')  # ✅ Ensure using GET

        try:
            # Normalize material_type
            material_type = material_type.upper() if material_type else ""
            group_mapping = {
                'STICHING': ['STICHING', 'STITCHING'],
                'PACKING': ['PACKING'],
                'SP': ['STICHING', 'PACKING']
            }

            group_types = group_mapping.get(material_type, [])

            # Get all item groups matching the group types
            item_groups = item_group_table.objects.filter(status=1, group_type__in=group_types)

            item_group_list = []
            item_list = []
            item_ids = []

            for group in item_groups:
                item_group_list.append({'id': group.id, 'name': group.name})
                
                # Get items under this group
                items = item_table.objects.filter(item_group_id=group.id, status=1)

                for item in items:
                    item_list.append({'id': item.id, 'name': item.name})
                    item_ids.append(item.id)

            # Now fetch sub-size, quality, size, color for these items
            sub_values = sub_size_table.objects.filter(status=1, item_id__in=item_ids)

            quality_ids = sub_values.values_list('quality_id', flat=True).distinct()
            size_ids = sub_values.values_list('size_id', flat=True).distinct()
            color_ids = sub_values.values_list('m_color_id', flat=True).distinct()

            # Fetch actual names from respective tables
            qualities = accessory_quality_table.objects.filter(id__in=quality_ids)
            sizes = accessory_size_table.objects.filter(id__in=size_ids)
            colors = color_table.objects.filter(id__in=color_ids)

            quality_list = [
                {'id': q.id, 'name': f"{q.name} - ({q.po_name if q.po_name else '-'})"} for q in qualities
            ]
            size_list = [
                {'id': s.id, 'name': f"{s.name} - ({s.po_name if s.po_name else '-'})"} for s in sizes
            ]
            color_list = [{'id': c.id, 'name': c.name} for c in colors]

            return JsonResponse({
                'success': True,
                'item_group': item_group_list,
                'item': item_list,
                'qualities': quality_list,
                'sizes': size_list,
                'colors': color_list,
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)





def get_accessory_item_group(request):
    if request.method == 'GET': 
        # material_type = request.GET.get('type')  # ✅ Ensure using GET

        # try:
        #     # Normalize material_type
        #     material_type = material_type.upper() if material_type else ""
        #     group_mapping = {
        #         'STICHING': ['STICHING', 'STITCHING'],
        #         'PACKING': ['PACKING'],
        #         'SP': ['STICHING', 'PACKING']
        #     }

            # group_types = group_mapping.get(material_type, [])

            # Get all item groups matching the group types
            item_groups = item_group_table.objects.filter(status=1)

            item_group_list = []
            item_list = []
            item_ids = []

            for group in item_groups:
                item_group_list.append({'id': group.id, 'name': group.name})
                
                # Get items under this group
                items = item_table.objects.filter(item_group_id=group.id, status=1)

                for item in items:
                    item_list.append({'id': item.id, 'name': item.name})
                    item_ids.append(item.id)

     
            return JsonResponse({
                'success': True,
                'item_group': item_group_list,
                
            })

        # except Exception as e:
        #     return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

# def get_accessory_items(request):
#     if request.method == 'GET':
#         material_type = request.POST.get('type')
#         # item_group_id = request.GET.get('item_group_id')
 
#         # if not item_group_id:
#         #     return JsonResponse({'success': False, 'message': 'Item Group ID is required'}, status=400)

#         try:
#             # Get all items under this group
#             # item_group = get_object_or_404(item_group_table.objects.filter(status=1,group_type__in=('STICHING','STITCHING')))
#             if material_type="SITCHING":
#                 item_group = item_group_table.objects.filter(status=1,group_type__in=('STICHING','STITCHING'))
#                 if item_group:
#                     item_group_id = item_group.id
#                 else:
#                     item_group_id = 0

#             elif material_type="Packing":
#                 item_group = item_group_table.objects.filter(status=1,group_type__in=('Packing','PACKING'))
#                 if item_group:
#                     item_group_id = item_group.id
#                 else:
#                     item_group_id = 0

#             elif material_type="SP":
#                 item_group = item_group_table.objects.filter(status=1,group_type__in=('STICHING','STITCHING'))
#                 if item_group:
#                     item_group_id = item_group.id
#                 else:
#                     item_group_id = 0
            
#             print('item-group-id:',item_group_id) 
 
#             items = item_table.objects.filter(item_group_id=item_group_id,status=1)
 
#             # Convert items to list of dictionaries
#             item_group_list = [{'id': item_group.id, 'name': item_group.name} for item_group in items]
#             item_list = [{'id': item.id, 'name': item.name} for item in items]
#             item_ids = [item.id for item in items]  # For sub_size filter

#             # Now get sub_size values for these items
#             sub_values = sub_size_table.objects.filter(status=1, item_id__in=item_ids)

#             # Collect unique quality, size, and color IDs
#             quality_ids = sub_values.values_list('quality_id', flat=True).distinct()
#             size_ids = sub_values.values_list('size_id', flat=True).distinct()
#             color_ids = sub_values.values_list('m_color_id', flat=True).distinct()
            
#             # Fetch actual names from respective tables
#             qualities = accessory_quality_table.objects.filter(id__in=quality_ids)
#             sizes = accessory_size_table.objects.filter(id__in=size_ids)
#             colors = color_table.objects.filter(id__in=color_ids)

#             # quality_list = [{'id': q.id, 'name': q.po_name} for q in qualities]
#             # size_list = [{'id': s.id, 'name': s.po_name} for s in sizes]
#             color_list = [{'id': c.id, 'name': c.name} for c in colors]
#             quality_list = [
#                 {
#                     'id': q.id,
#                     'name': f"{q.name} - ({q.po_name if q.po_name else '-'})"
#                 }
#                 for q in qualities
#             ]

#             size_list = [
#                 {
#                     'id': s.id,
#                     'name': f"{s.name} - ({s.po_name if s.po_name else '-'})"
#                 }
#                 for s in sizes
#             ]
#             return JsonResponse({
#                 'success': True,
#                 'item_group':item_group_list,
#                 'items': item_list,
#                 'qualities': quality_list,
#                 'sizes': size_list,
#                 'colors': color_list,
#             })

#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)}, status=500)

#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)




@csrf_exempt  # Optional, recommended to use CSRF token instead
def get_delivery_party_list(request):
    data = []

    if request.method == 'POST':
        material_type = request.POST.get('material_type')

        if material_type == 'stiching': 
            parties = party_table.objects.filter(status=1, is_stiching=1) 
 
        elif material_type == 'sp': 
            parties = party_table.objects.filter(status=1, is_stiching=1)   

        elif material_type == 'packing': 
            parties = party_table.objects.filter(status=1, is_ironing=1) 

        elif material_type == 'dyeing': 
            parties = party_table.objects.filter(status=1, is_fabric=1)

        else:
            parties = party_table.objects.none()

        data = [{"id": p.id, "name": p.name} for p in parties]

    return JsonResponse(data, safe=False)





@csrf_exempt  # Optional, recommended to use CSRF token instead
def get_delivery_party_lists(request):
    data = []

    if request.method == 'POST':
        material_type = request.POST.get('material_type')

        if material_type == 'STITCHING': 
            parties = party_table.objects.filter(status=1, is_stiching=1) 
 
        elif material_type == 'SP': 
            parties = party_table.objects.filter(status=1, is_stiching=1)   

        elif material_type == 'PACKING': 
            parties = party_table.objects.filter(status=1, is_ironing=1) 

        elif material_type == 'DYEING': 
            parties = party_table.objects.filter(status=1, is_fabric=1)

        else:
            parties = party_table.objects.none()

        data = [{"id": p.id, "name": p.name} for p in parties]

    return JsonResponse(data, safe=False)




@csrf_exempt
def get_stiching_list_by_supplier(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')

        if not supplier_id:
            return JsonResponse({'orders': []}) 

        # Filter stitching deliveries by supplier_id
        stiching_orders = parent_stiching_outward_table.objects.filter(party_id=supplier_id,status=1)
        print('st-data:',stiching_orders)

        # Serialize for dropdown
        data = {
            'orders': [
                { 
                    'id': order.id,
                    'outward_no': order.outward_no,
                    'quality_id':order.quality_id,
                    'style_id':order.style_id
                }
                for order in stiching_orders
            ]
        }
        print('orders:',data)

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)




# @csrf_exempt
# def get_stiching_packing_list(request):
#     if request.method == 'POST':
#         supplier_id = request.POST.get('supplier_id')

#         if not supplier_id:
#             return JsonResponse({'orders': []})

#         # Filter stitching deliveries by supplier_id
#         stiching_orders = parent_stiching_outward_table.objects.filter(party_id=supplier_id,status=1)
#         packing = parent_packing_outward_table.objects.filter(party_id=supplier_id,stiching_outward_id=stiching_orders.id,status=1)

#         # Serialize for dropdown
#         data = {
#             'orders': [
#                 {
#                     'id': order.id,
#                     'outward_no': order.outward_no,
#                     'quality_id':order.quality_id,
#                     'style_id':order.style_id
#                 }
#                 for order in stiching_orders
#             ]
#         }
#         print('orders:',data)

#         return JsonResponse(data)

#     return JsonResponse({'error': 'Invalid request'}, status=400)


from django.db.models import Q

@csrf_exempt
def get_stiching_packing_list(request): 
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')

        if not supplier_id:
            return JsonResponse({'orders': []})

        # Fetch stitching orders where the party is active (status=1)
        stiching_orders = parent_stiching_outward_table.objects.filter(party_id=supplier_id,is_packing=1, status=1)
        
        # Fetch packing orders that match the stitching orders' ids
        # packing_orders = parent_packing_outward_table.objects.filter(
        #     party_id=supplier_id,
        #     stiching_outward_id__in=stiching_orders.values('id'),
        #     status=1
        # )  
        
        # # Only include stitching orders where there is a corresponding packing entry
        
        # valid_orders = stiching_orders.filter(id__in=packing_orders.values('stiching_outward_id'))
        
        print('orders:',stiching_orders)
        # Serialize the data for dropdown 
        data = { 
            'orders': [
                {
                    'id': order.id,  
                    'outward_no': order.outward_no,
                    'quality_id': order.quality_id, 
                    'style_id': order.style_id
                }
                for order in stiching_orders
            ]
        }

        print('orders:', data)

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def get_stiching_packing_quality_style_list(request): 
    if request.method == 'POST':
        stiching_id = request.POST.get('stiching_id')
        print('sp-id:',stiching_id)
 
        if not stiching_id: 
            return JsonResponse({'orders': []})

        acc_prg = parent_stiching_outward_table.objects.filter(id=stiching_id, is_packing=1,status=1)

        orders = []
        for order in acc_prg:
            quality = quality_table.objects.filter(status=1, id=order.quality_id).first()
            style = style_table.objects.filter(status=1, id=order.style_id).first()
            if quality and style:
                orders.append({
                    'id': order.id,
                    'quality_id': order.quality_id,
                    'quality_name': quality.name,
                    'style_id': order.style_id,
                    'style_name': style.name,   # Add style name here
                })

        data = {'orders': orders}

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)





from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Sum, Q



from collections import defaultdict 
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_stiching_packing_out_details_test33333(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # === Extract POST Data ===
        program_id = request.POST.get('program_id')
        stitching_id = request.POST.get('stitching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([stitching_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === Check if accessory outward exists for the stitching_id ===
        acc_out = parent_accessory_outward_table.objects.filter(
            stiching_outward_id=stitching_id,
            status=1
        ).first()

        # === If no accessory outward exists, return only stitching outward data ===
        if acc_out is None:
            stitching_data_qs = child_stiching_outward_table.objects.filter(
                tm_id=stitching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values(
                'size_id',
                'quantity',
                'quality_id',
                'style_id',
                'tm_id',
                'status'
            )

            # Optionally map sizes and quality/style names if needed:
            size_ids = [item['size_id'] for item in stitching_data_qs]
            size_map = dict(size_table.objects.filter(id__in=size_ids).values_list('id', 'name'))

            quality_ids = [item['quality_id'] for item in stitching_data_qs]
            quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))

            style_ids = [item['style_id'] for item in stitching_data_qs]
            style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))

            stitching_data = []
            for item in stitching_data_qs:
                stitching_data.append({
                    **item,
                    'size': size_map.get(item['size_id'], ''),
                    'quality': quality_map.get(item['quality_id'], ''),
                    'style': style_map.get(item['style_id'], ''),
                })

            return JsonResponse({
                'data': stitching_data,
                'summary': [],
                'message': 'No accessory outward data found; showing stitching outward only.'
            })

        # === If accessory outward exists, fetch accessory program and stitching outward data ===

        # === Run your existing SQL query to fetch program/accessory data ===
        with connection.cursor() as cursor:
            sql = """
                SELECT  
                    ac.tm_id AS prg_id, 
                    ac.size_id, 
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id, 
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id, 
                    tm.quality_id, 
                    tm.style_id,
                    COALESCE(tx_total.total_st_qty, 0) AS sp_qty,
                    ac.quantity AS prg_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1
                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                        AND tx.tm_id = %s
                        AND tx.quality_id = %s
                        AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id
                WHERE tm.status = 1
                    AND ac.quantity > 0
                    AND ac.status = 1
                    AND tm.quality_id = %s
                    AND tm.style_id = %s
                    AND ac.size_id IN (
                        SELECT DISTINCT size_id 
                        FROM tx_stiching_outward  
                        WHERE status = 1 
                            AND tm_id = %s
                            AND quality_id = %s
                            AND style_id = %s
                    )
                GROUP BY tm.quality_id,
                         tm.style_id,
                         ac.item_id,
                         ac.tm_id,
                         ac.acc_size_id,
                         ac.item_group_id,
                         ac.acc_quality_id,
                         gp.group_type,
                         mx.color_id,
                         ac.uom_id,
                         ac.program_type
            """
            cursor.execute(sql, [
                program_id,
                stitching_id, quality_id, style_id,
                quality_id, style_id,
                stitching_id, quality_id, style_id
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Validate Relevant Size IDs from stitching outward table ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stitching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        # === Mapping Tables ===
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))
        acc_quality_ids = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_ids = {r['group_id'] for r in results if r['group_id']}
        uom_ids = {r['uom_id'] for r in results if r['uom_id']}
        item_ids = {r['item_id'] for r in results if r['item_id']}
        quality_ids = {r['quality_id'] for r in results if r['quality_id']}
        style_ids = {r['style_id'] for r in results if r['style_id']}
        color_ids = {r['color_id'] for r in results if r['color_id']}
        acc_size_ids = {r['acc_size_id'] for r in results if r['acc_size_id']}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Fetch Rec Qty from child_accessory_outward_table ===
        outward_data = child_accessory_outward_table.objects.filter(
            status=1,
            tm_id=acc_out.id,
        ).values(
            'item_id', 'size_id', 'color_id'
        ).annotate(total_rec_qty=Sum('quantity'))

        # Build rec_qty_map keyed by size or color for lookup
        rec_qty_map = {}
        for row in outward_data:
            key_size = (row['item_id'], row['size_id'])
            key_color = (row['item_id'], row['color_id'])

            if row['size_id']:
                rec_qty_map[('SIZE', key_size)] = row['total_rec_qty']
            elif row['color_id']:
                rec_qty_map[('COLOR', key_color)] = row['total_rec_qty']

        # === Build Final Enriched Data ===
        enriched_data = []
        seen_keys = set()

        for row in results:
            if row['size_id'] in valid_size_ids:
                key = (row['item_id'], row['size_id'], row['acc_quality_id'], row['uom_id'])
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                program_type = (row.get('program_type') or '').upper()
                rec_qty = 0

                if program_type == 'SIZE':
                    rec_qty = rec_qty_map.get(('SIZE', (row['item_id'], row['size_id'])), 0)
                elif program_type == 'COLOR':
                    rec_qty = rec_qty_map.get(('COLOR', (row['item_id'], row['color_id'])), 0)
                elif program_type == 'TOTAL QUANTITY':
                    rec_qty = rec_qty_map.get(('TOTAL', (row['item_id'], row['prg_id'])), 0)

                enriched_data.append({
                    **row,
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], ''),
                    'rec_qty': float(rec_qty),
                })

        # === Build Summary ===
        summary_map = defaultdict(lambda: {'program_type': '', 'key_id': None, 'total_qty': 0})

        for row in enriched_data:
            program_type = (row.get('program_type') or '').upper()
            if program_type == 'COLOR':
                key_id = row.get('color_id')
            elif program_type == 'SIZE':
                key_id = row.get('size_id')
            elif program_type == 'TOTAL QUANTITY':
                key_id = row.get('prg_id')
            else:
                continue

            if key_id is None:
                continue

            key = f"{program_type}|{key_id}"
            summary_map[key]['program_type'] = program_type
            summary_map[key]['key_id'] = key_id
            summary_map[key]['total_qty'] = float(row.get('sp_qty') or 0)

        summary_data = list(summary_map.values())

        # === Final Response ===
        return JsonResponse({
            'data': enriched_data,
            'summary': summary_data,
        }) 

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 
 




@csrf_exempt
def get_stiching_packing_out_details_tett(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # === Extract POST Data ===
        program_id = request.POST.get('program_id')
        stitching_id = request.POST.get('stitching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([stitching_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === SQL Query to get stitching outward and accessory program data ===
        with connection.cursor() as cursor:
            sql = """
                SELECT  
                    ac.tm_id AS prg_id, 
                    ac.size_id, 
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id, 
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id, 
                    tm.quality_id, 
                    tm.style_id,
                    COALESCE(tx_total.total_st_qty, 0) AS sp_qty,
                    ac.quantity AS prg_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1
                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                        AND tx.tm_id = %s
                        AND tx.quality_id = %s
                        AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id
                WHERE tm.status = 1
                    AND ac.quantity > 0
                    AND ac.status = 1
                    AND tm.quality_id = %s
                    AND tm.style_id = %s
                    AND ac.size_id IN (
                        SELECT DISTINCT size_id 
                        FROM tx_stiching_outward  
                        WHERE status = 1 
                            AND tm_id = %s
                            AND quality_id = %s
                            AND style_id = %s
                    )
                GROUP BY tm.quality_id,
                         tm.style_id,
                         ac.item_id,
                         ac.tm_id,
                         ac.acc_size_id,
                         ac.item_group_id,
                         ac.acc_quality_id,
                         gp.group_type,
                         mx.color_id,
                         ac.uom_id,
                         ac.program_type
            """
            cursor.execute(sql, [
                program_id,
                stitching_id, quality_id, style_id,
                quality_id, style_id,
                stitching_id, quality_id, style_id
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Validate Relevant Size IDs ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stitching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        ) 

        # acc_out = parent_accessory_outward_table.objects.filter(stiching_outward_id=stitching_id,status=1).first()
        # outward = child_accessory_outward_table.objects.filter(status=1,tm_id=acc_out.id)
        # acc_out = parent_accessory_outward_table.objects.filter(stiching_outward_id=stitching_id, status=1).first()

        # === Mapping Tables ===
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))
        acc_quality_ids = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_ids = {r['group_id'] for r in results if r['group_id']}
        uom_ids = {r['uom_id'] for r in results if r['uom_id']}
        item_ids = {r['item_id'] for r in results if r['item_id']}
        quality_ids = {r['quality_id'] for r in results if r['quality_id']}
        style_ids = {r['style_id'] for r in results if r['style_id']}
        color_ids = {r['color_id'] for r in results if r['color_id']}
        acc_size_ids = {r['acc_size_id'] for r in results if r['acc_size_id']}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

      
        acc_out = parent_accessory_outward_table.objects.filter(stiching_outward_id=stitching_id, status=1).first()
        if acc_out is None:
            return JsonResponse({"error": "No accessory outward found for the given stitching id"}, status=404)

        outward_data = child_accessory_outward_table.objects.filter(
            status=1,
            tm_id=acc_out.id,
        ).values(
            'item_id', 'size_id', 'color_id'
        ).annotate(total_rec_qty=Sum('quantity'))



        # === Fetch Rec Qty from tx_accessory_outward ===
        # outward_data = child_accessory_outward_table.objects.filter(
        #     status=1,
        #     tm_id__in=acc_out.id,
        #     # item_id__in=item_ids 
        # ).values(
        #     'item_id', 'size_id', 'color_id'
        # ).annotate(total_rec_qty=Sum('quantity'))
       
        # outward_qty = outward_data 
        # print('out-qty:',outward_qty)


        rec_qty_map = {}
        for row in outward_data: 
            key_size = (row['item_id'], row['size_id'])
            key_color = (row['item_id'], row['color_id'])

            if row['size_id']:
                rec_qty_map[('SIZE', key_size)] = row['total_rec_qty']
            elif row['color_id']:
                rec_qty_map[('COLOR', key_color)] = row['total_rec_qty']
            # else:
            #     rec_qty_map[('TOTAL', key_total)] = row['total_rec_qty']

        # === Build Final Data with Deduplication and rec_qty ===
        enriched_data = [] 
        seen_keys = set()

        for row in results:
            if row['size_id'] in valid_size_ids:
                key = (row['item_id'], row['size_id'], row['acc_quality_id'], row['uom_id'])
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                program_type = (row.get('program_type') or '').upper()
                rec_qty = 0

                if program_type == 'SIZE':
                    rec_qty = rec_qty_map.get(('SIZE', (row['item_id'], row['size_id'])), 0)
                elif program_type == 'COLOR':
                    rec_qty = rec_qty_map.get(('COLOR', (row['item_id'], row['color_id'])), 0)
                elif program_type == 'TOTAL QUANTITY':
                    rec_qty = rec_qty_map.get(('TOTAL', (row['item_id'], row['prg_id'])), 0)

                enriched_data.append({
                    **row,
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['size_id'], ''),
                    'rec_qty': float(rec_qty)
                })

        # === Build Summary ===
        summary_map = defaultdict(lambda: {'program_type': '', 'key_id': None, 'total_qty': 0})
        
        for row in enriched_data:
            program_type = (row.get('program_type') or '').upper()
            if program_type == 'COLOR':
                key_id = row.get('color_id')
            elif program_type == 'SIZE':
                key_id = row.get('size_id')
            elif program_type == 'TOTAL QUANTITY':
                key_id = row.get('prg_id')
            else:
                continue

            if key_id is None:
                continue

            key = f"{program_type}|{key_id}"
            summary_map[key]['program_type'] = program_type
            summary_map[key]['key_id'] = key_id
            summary_map[key]['total_qty'] = float(row.get('sp_qty') or 0)

        summary_data = list(summary_map.values())

        # === Final Response ===
        return JsonResponse({
            'data': enriched_data,
            'summary': summary_data
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection



@csrf_exempt
def get_stiching_packing_out_details(request):
 
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        program_id = request.POST.get('program_id')      # optional
        stitching_id = request.POST.get('stitching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([stitching_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === SQL: fetch accessory program rows + summed outward (sp_qty) for the given stitching instance ===
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id,
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    COALESCE(tx_total.total_st_qty, 0) AS sp_qty,
                    ac.quantity AS prg_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac
                LEFT JOIN tm_accessory_program tm 
                    ON ac.tm_id = tm.id
                LEFT JOIN item_group gp 
                    ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx 
                    ON ac.item_id = mx.item_id AND mx.status = 1
                LEFT JOIN (
                    SELECT
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                        AND tx.tm_id = %s
                        AND tx.quality_id = %s
                        AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id
                WHERE tm.status = 1
                    AND ac.quantity > 0
                    AND ac.status = 1
                    AND tm.quality_id = %s
                    AND tm.style_id = %s
                    AND ac.size_id IN (
                        SELECT DISTINCT size_id
                        FROM tx_stiching_outward
                        WHERE status = 1
                            AND tm_id = %s
                            AND quality_id = %s
                            AND style_id = %s
                    )
                GROUP BY
                    ac.tm_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id,
                    ac.item_group_id,
                    ac.acc_quality_id,
                    gp.group_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    ac.uom_id,
                    ac.program_type
                /* Add comments to explain complex joins and groupings */

            """

            # Build params in the same order as placeholders:
            # tx_total subquery uses (stitching_id, quality_id, style_id)
            # the WHERE tm.quality_id, tm.style_id use (quality_id, style_id)
            # the IN() subquery uses (stitching_id, quality_id, style_id)  

            params = [
                stitching_id, quality_id, style_id,
                quality_id, style_id,
                stitching_id, quality_id, style_id
            ]

            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Validate relevant size IDs from child tx table ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stitching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        # === Prepare mapping dictionaries ===
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))
        acc_quality_ids = {r['acc_quality_id'] for r in results if r.get('acc_quality_id')}
        group_ids = {r['group_id'] for r in results if r.get('group_id')}
        uom_ids = {r['uom_id'] for r in results if r.get('uom_id')}
        item_ids = {r['item_id'] for r in results if r.get('item_id')}
        quality_ids = {r['quality_id'] for r in results if r.get('quality_id')}
        style_ids = {r['style_id'] for r in results if r.get('style_id')}
        color_ids = {r['color_id'] for r in results if r.get('color_id')}
        acc_size_ids = {r['acc_size_id'] for r in results if r.get('acc_size_id')}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Enrich results and deduplicate ===
        enriched_data = []
        seen_keys = set()
        for row in results:
            # ensure size is valid
            if row['size_id'] not in valid_size_ids:
                continue

            # choose a dedupe key (item, size, acc_quality, uom) - you can change as needed
            key = (row.get('item_id'), row.get('size_id'), row.get('acc_quality_id'), row.get('uom_id'))
            if key in seen_keys:
                continue
            seen_keys.add(key)

            enriched_data.append({
                **row,
                'quality': quality_map.get(row.get('quality_id'), ''),
                'style': style_map.get(row.get('style_id'), ''),
                'size': size_map.get(row.get('size_id'), ''),
                'uom': uom_map.get(row.get('uom_id'), ''),
                'color': color_map.get(row.get('color_id'), ''),
                'item': item_map.get(row.get('item_id'), ''),
                'group': group_map.get(row.get('group_id'), ''),
                'acc_quality': acc_quality_map.get(row.get('acc_quality_id'), ''),
                'acc_size': acc_size_map.get(row.get('acc_size_id'), ''),   # use acc_size_id
            })

        # === Build summary (sums per program key) ===
        summary_map = defaultdict(lambda: {'program_type': '', 'key_id': None, 'total_qty': 0.0})

        for row in enriched_data:
            program_type = (row.get('program_type') or '').upper()
            if program_type == 'COLOR':
                key_id = row.get('color_id')
            elif program_type == 'SIZE':
                key_id = row.get('size_id')
            elif program_type == 'TOTAL QUANTITY':
                key_id = row.get('tm_id')  # group by program instance / tm_id
            else:
                # if other program types exist, you may decide how to handle them
                key_id = None

            if key_id is None:
                continue

            map_key = f"{program_type}|{key_id}"
            summary_map[map_key]['program_type'] = program_type
            summary_map[map_key]['key_id'] = key_id
            # sum sp_qty across rows for this key
            summary_map[map_key]['total_qty'] += float(row.get('sp_qty') or 0.0)

        summary_data = list(summary_map.values())

        # === Response ===
        return JsonResponse({
            'data': enriched_data,
            'summary': summary_data
        }, safe=False)

    except Exception as e:
        # return error for debugging — you can hide details in production
        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt
def get_packing_list(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')

        if not supplier_id:
            return JsonResponse({'orders': []})

        # Filter stitching deliveries by supplier_id
        stiching_orders = parent_packing_outward_table.objects.filter(party_id=supplier_id,status=1)

        # Serialize for dropdown
        data = {
            'orders': [
                {
                    'id': order.id,
                    'outward_no': order.outward_no,
                    'quality_id':order.quality_id,
                    'style_id':order.style_id
                }
                for order in stiching_orders
            ]
        }
        print('orders:',data)

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)





def get_packing_accessory_program_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not quality_id and not style_id :
            return JsonResponse({'orders': []})

        # Filter stitching deliveries by supplier_id
        acc_prg = accessory_program_table.objects.filter(quality_id=quality_id,style_id=style_id,status=1)

        # Serialize for dropdown
        data = {
            'orders': [
                {
                    'id': order.id,
                    'accessory_no': order.accessory_no,
                    'quality_id':order.quality_id,
                    'style_id':order.style_id
                }
                for order in acc_prg
            ]
        }
        print('orders:',data)

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from collections import defaultdict
from django.db import connection



@csrf_exempt
def get_packing_out_details(request):
 
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        program_id = request.POST.get('program_id')      # optional
        packing_id = request.POST.get('packing_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([packing_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === SQL: fetch accessory program rows + summed outward (sp_qty) for the given stitching instance ===
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id,
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    COALESCE(tx_total.total_st_qty, 0) AS sp_qty,
                    ac.quantity AS prg_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac
                LEFT JOIN tm_accessory_program tm 
                    ON ac.tm_id = tm.id
                LEFT JOIN item_group gp 
                    ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx 
                    ON ac.item_id = mx.item_id AND mx.status = 1
                LEFT JOIN (
                    SELECT
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_packing_outward tx
                    WHERE tx.status = 1
                        AND tx.tm_id = %s
                        AND tx.quality_id = %s
                        AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id
                WHERE tm.status = 1
                    AND ac.quantity > 0
                    AND ac.status = 1
                    AND tm.quality_id = %s
                    AND tm.style_id = %s
                    AND ac.size_id IN (
                        SELECT DISTINCT size_id
                        FROM tx_packing_outward
                        WHERE status = 1
                            AND tm_id = %s
                            AND quality_id = %s
                            AND style_id = %s
                    )
                GROUP BY
                    ac.tm_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id,
                    ac.item_group_id,
                    ac.acc_quality_id,
                    gp.group_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    ac.uom_id,
                    ac.program_type
                /* Add comments to explain complex joins and groupings */

            """

            # Build params in the same order as placeholders:
            # tx_total subquery uses (packing_id, quality_id, style_id)
            # the WHERE tm.quality_id, tm.style_id use (quality_id, style_id)
            # the IN() subquery uses (packing_id, quality_id, style_id)  

            params = [
                packing_id, quality_id, style_id,
                quality_id, style_id,
                packing_id, quality_id, style_id
            ]

            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Validate relevant size IDs from child tx table ===
        valid_size_ids = set(
            child_packing_outward_table.objects.filter(
                tm_id=packing_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        # === Prepare mapping dictionaries ===
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))
        acc_quality_ids = {r['acc_quality_id'] for r in results if r.get('acc_quality_id')}
        group_ids = {r['group_id'] for r in results if r.get('group_id')}
        uom_ids = {r['uom_id'] for r in results if r.get('uom_id')}
        item_ids = {r['item_id'] for r in results if r.get('item_id')}
        quality_ids = {r['quality_id'] for r in results if r.get('quality_id')}
        style_ids = {r['style_id'] for r in results if r.get('style_id')}
        # color_ids = {r['color_id'] for r in results if r.get('color_id')}

        color_ids = set()
        for r in results:
            color_val = r.get('color_id')
            if color_val:
                if isinstance(color_val, str) and ',' in color_val:
                    color_ids.update(int(c.strip()) for c in color_val.split(',') if c.strip().isdigit())
                else:
                    try:
                        color_ids.add(int(color_val))
                    except (ValueError, TypeError): 
                        pass



        acc_size_ids = {r['acc_size_id'] for r in results if r.get('acc_size_id')}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Enrich results and deduplicate ===
        enriched_data = []
        seen_keys = set()
        for row in results:
            # ensure size is valid
            if row['size_id'] not in valid_size_ids: 
                continue

            # choose a dedupe key (item, size, acc_quality, uom) - you can change as needed
            key = (row.get('item_id'), row.get('size_id'), row.get('acc_quality_id'), row.get('uom_id'))
            if key in seen_keys:
                continue
            seen_keys.add(key)

            enriched_data.append({
                **row,
                'quality': quality_map.get(row.get('quality_id'), ''),
                'style': style_map.get(row.get('style_id'), ''),
                'size': size_map.get(row.get('size_id'), ''),
                'uom': uom_map.get(row.get('uom_id'), ''),
                'color': color_map.get(row.get('color_id'), ''),
                'item': item_map.get(row.get('item_id'), ''),
                'group': group_map.get(row.get('group_id'), ''),
                'acc_quality': acc_quality_map.get(row.get('acc_quality_id'), ''),
                'acc_size': acc_size_map.get(row.get('acc_size_id'), ''),   # use acc_size_id
            })

        # === Build summary (sums per program key) ===
        summary_map = defaultdict(lambda: {'program_type': '', 'key_id': None, 'total_qty': 0.0})

        for row in enriched_data:
            program_type = (row.get('program_type') or '').upper()
            if program_type == 'COLOR':
                key_id = row.get('color_id')
            elif program_type == 'SIZE':
                key_id = row.get('size_id')
            elif program_type == 'TOTAL QUANTITY':
                key_id = row.get('tm_id')  # group by program instance / tm_id
            else:
                # if other program types exist, you may decide how to handle them
                key_id = None

            if key_id is None:
                continue

            map_key = f"{program_type}|{key_id}"
            summary_map[map_key]['program_type'] = program_type
            summary_map[map_key]['key_id'] = key_id
            # sum sp_qty across rows for this key
            summary_map[map_key]['total_qty'] += float(row.get('sp_qty') or 0.0)

        summary_data = list(summary_map.values())

        # === Response ===
        return JsonResponse({ 
            'data': enriched_data,
            'summary': summary_data
        }, safe=False)
 
    except Exception as e:
        # return error for debugging — you can hide details in production
        return JsonResponse({'error': str(e)}, status=500)






@csrf_exempt
def get_packing_out_details_edit(request):
 
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        tm_id = request.POST.get('tm_id')
        program_id = request.POST.get('program_id')      # optional
        packing_id = request.POST.get('packing_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([packing_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === SQL: fetch accessory program rows + summed outward (sp_qty) for the given stitching instance ===
        with connection.cursor() as cursor:
            sql = """

                SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.uom_id AS uom_id, 
                    ac.quantity AS prg_qty,
                    ac.product_pieces,
                    COALESCE(tx_total_stiching.total_st_qty, 0) AS st_qty,
                    COALESCE(tx_total_accessory.total_st_qty, 0) AS already_rec_qty, 
                    ( COALESCE(tx_total_stiching.total_st_qty,0) - COALESCE(tx_total_accessory.total_st_qty, 0)) AS balance_qty,
                    
                    ac.program_type
                    FROM tx_accessory_program ac 
                    LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                    LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                    LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                    LEFT JOIN ( 
                    SELECT 
                        tx.size_id,  
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty 
                    FROM tx_packing_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id =%s
                    --  GROUP BY tx.size_id, tx.tm_id 
                    GROUP BY tx.tm_id
                    ) AS tx_total_stiching ON tx_total_stiching.size_id = ac.size_id

                    LEFT JOIN (
                    SELECT  
                        tx.item_id,
                        tx.item_group_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tm_accessory_outward tma
                    JOIN tx_accessory_outward tx ON tma.id = tx.tm_id 
                    WHERE tx.status = 1 AND tma.packing_outward_id = %s AND tma.id=%s AND tma.status=1 

                    GROUP BY tx.item_id
                    ) AS tx_total_accessory ON tx_total_accessory.item_id = ac.item_id

                    WHERE tm.status = 1
                    AND ac.quantity > 0 
                    AND ac.status = 1
                    AND tm.quality_id = %s
                    AND tm.style_id = %s
                    AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_packing_outward  
                    WHERE status = 1 
                        AND tm_id = %s
                        AND quality_id = %s
                        AND style_id = %s
                    )
                    GROUP BY
                            tm.quality_id,  
                            tm.style_id, 
                            ac.item_id, 
                            ac.tm_id, 
                            ac.item_group_id, 
                            ac.acc_quality_id, 
                            gp.group_type, 
                        --  ac.size_id,  
                        --  ac.acc_size_id,
                        --   mx.color_id,
                        --   ac.quantity, 
                        --    tx_total_stiching.total_st_qty, 
                        --   tx_total_accessory.total_st_qty,  -- Add here in group by if needed
                        --   ac.product_pieces, 
                        --   ac.uom_id, 
                        
                            ac.program_type;
                    


            """

            # Build params in the same order as placeholders:
            # tx_total subquery uses (packing_id, quality_id, style_id)
            # the WHERE tm.quality_id, tm.style_id use (quality_id, style_id)
            # the IN() subquery uses (packing_id, quality_id, style_id)  

            params = [
                program_id,
                packing_id, quality_id, style_id,
                packing_id,tm_id,
                quality_id, style_id,
                packing_id, quality_id, style_id
            ]

            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Validate relevant size IDs from child tx table ===
        valid_size_ids = set(
            child_packing_outward_table.objects.filter(
                tm_id=packing_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )
        
        # === Prepare mapping dictionaries ===
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))
        acc_quality_ids = {r['acc_quality_id'] for r in results if r.get('acc_quality_id')}
        group_ids = {r['group_id'] for r in results if r.get('group_id')}
        uom_ids = {r['uom_id'] for r in results if r.get('uom_id')}
        item_ids = {r['item_id'] for r in results if r.get('item_id')}
        quality_ids = {r['quality_id'] for r in results if r.get('quality_id')}
        style_ids = {r['style_id'] for r in results if r.get('style_id')}
        # color_ids = {r['color_id'] for r in results if r.get('color_id')}

        color_ids = set()
        for r in results:
            color_val = r.get('color_id')
            if color_val:
                if isinstance(color_val, str) and ',' in color_val:
                    color_ids.update(int(c.strip()) for c in color_val.split(',') if c.strip().isdigit())
                else:
                    try:
                        color_ids.add(int(color_val))
                    except (ValueError, TypeError): 
                        pass



        acc_size_ids = {r['acc_size_id'] for r in results if r.get('acc_size_id')}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Enrich results and deduplicate ===
        enriched_data = []
        seen_keys = set()
        for row in results:
            # ensure size is valid
            if row['size_id'] not in valid_size_ids: 
                continue

            # choose a dedupe key (item, size, acc_quality, uom) - you can change as needed
            key = (row.get('item_id'), row.get('size_id'), row.get('acc_quality_id'), row.get('uom_id'))
            if key in seen_keys:
                continue
            seen_keys.add(key)

            enriched_data.append({ 
                **row,
                'quality': quality_map.get(row.get('quality_id'), ''),
                'style': style_map.get(row.get('style_id'), ''),
                'size': size_map.get(row.get('size_id'), ''),
                'uom': uom_map.get(row.get('uom_id'), ''),
                'color': color_map.get(row.get('color_id'), ''),
                'item': item_map.get(row.get('item_id'), ''),
                'group': group_map.get(row.get('group_id'), ''),
                'acc_quality': acc_quality_map.get(row.get('acc_quality_id'), ''),
                'acc_size': acc_size_map.get(row.get('acc_size_id'), ''),   # use acc_size_id
            })

        # === Build summary (sums per program key) ===
        summary_map = defaultdict(lambda: {'program_type': '', 'key_id': None, 'total_qty': 0.0})

        for row in enriched_data:
            program_type = (row.get('program_type') or '').upper()
            if program_type == 'COLOR':
                key_id = row.get('color_id')
            elif program_type == 'SIZE':
                key_id = row.get('size_id')
            elif program_type == 'TOTAL QUANTITY':
                key_id = row.get('tm_id')  # group by program instance / tm_id
            else:
                # if other program types exist, you may decide how to handle them
                key_id = None

            if key_id is None:
                continue

            map_key = f"{program_type}|{key_id}"
            summary_map[map_key]['program_type'] = program_type
            summary_map[map_key]['key_id'] = key_id
            # sum sp_qty across rows for this key
            summary_map[map_key]['total_qty'] += float(row.get('sp_qty') or 0.0)

        summary_data = list(summary_map.values())

        # === Response ===
        return JsonResponse({ 
            'data': enriched_data,
            'summary': summary_data
        }, safe=False)
  
    except Exception as e:
        # return error for debugging — you can hide details in production
        return JsonResponse({'error': str(e)}, status=500)





def get_stiching_quality_style(request):
    if request.method == 'POST':
        stiching_id = request.POST.get('stiching_id')

        if not stiching_id:
            return JsonResponse({'orders': []})

        acc_prg = parent_stiching_outward_table.objects.filter(id=stiching_id, status=1)

        orders = []
        for order in acc_prg:
            quality = quality_table.objects.filter(status=1, id=order.quality_id).first()
            style = style_table.objects.filter(status=1, id=order.style_id).first()
            if quality and style:
                orders.append({
                    'id': order.id,
                    'quality_id': order.quality_id,
                    'quality_name': quality.name,
                    'style_id': order.style_id,
                    'style_name': style.name,   # Add style name here
                })

        data = {'orders': orders}

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)



# def get_stiching_quality_style(request):
#     if request.method == 'POST':
#         stiching_id = request.POST.get('stiching_id')

#         if not stiching_id :
#             return JsonResponse({'orders': []})

#         # Filter stitching deliveries by supplier_id
#         acc_prg = parent_stiching_outward_table.objects.filter(id=stiching_id,status=1)

#         # Serialize for dropdown
#         data = {
#             'orders': [
                
#                 {
#                     'id': order.id,
#                     'quality_id':order.quality_id,
#                     'style_id':order.style_id
#                 }
#                 for order in acc_prg
#             ]
#         }

#         print('orders:',data)

#         return JsonResponse(data)

#     return JsonResponse({'error': 'Invalid request'}, status=400)






def get_packing_quality_style(request):
    if request.method == 'POST':
        packing_id = request.POST.get('packing_id')

        if not packing_id :
            return JsonResponse({'orders': []})

        # Filter stitching deliveries by supplier_id
        acc_prg = parent_packing_outward_table.objects.filter(id=packing_id,status=1)

        orders = [] 
        for order in acc_prg:
            quality = quality_table.objects.filter(status=1, id=order.quality_id).first()
            style = style_table.objects.filter(status=1, id=order.style_id).first()
            if quality and style:
                orders.append({
                    'id': order.id,
                    'quality_id': order.quality_id,
                    'quality_name': quality.name,
                    'style_id': order.style_id,
                    'style_name': style.name,   # Add style name here
                })

        data = {'orders': orders}

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)





# def get_quality(request):
#     if request.method == 'POST':
   
#         orders = [] 
#         # for order in acc_prg: 
#         quality = quality_table.objects.filter(status=1)
#         # style = style_table.objects.filter(status=1, id=order.style_id).first()
#         if quality:
#             orders.append({ 
#                 'quality_id': quality.id,
#                 'quality_name': quality.name,
#                 # 'style_id': order.style_id,
#                 # 'style_name': style.name,   # Add style name here
#             })

#         data = {'orders': orders}

#         return JsonResponse(data)

#     return JsonResponse({'error': 'Invalid request'}, status=400)


 
def get_quality(request):
    if request.method == 'POST':
        qualities = quality_table.objects.filter(status=1)

        orders = []
        for q in qualities: 
            orders.append({
                'quality_id': q.id,
                'quality_name': q.name,
            })

        data = {'orders': orders}
        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)





def get_accessory_program_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not quality_id and not style_id :
            return JsonResponse({'orders': []}) 
 
        # Filter stitching deliveries by supplier_id
        acc_prg = accessory_program_table.objects.filter(quality_id=quality_id,style_id=style_id,status=1)
    
        # Serialize for dropdown
        data = {
            'orders': [



                {
                    'id': order.id,
                    'accessory_no': order.accessory_no,
                    'quality_id':order.quality_id,
                    'style_id':order.style_id
                }
                for order in acc_prg
            ]

        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)



from django.db import connection

# SELECT  
                #     ac.tm_id AS prg_id,
                #     ac.size_id,
                #     ac.item_id,
                #     ac.acc_size_id AS acc_size_id, 
                #     ac.item_group_id AS group_id,
                #     ac.acc_quality_id AS acc_quality_id,
                #     gp.group_type AS item_type,
                #     mx.color_id,
                #     tm.quality_id, 
                #     tm.style_id,
                #     ac.quantity AS prg_qty,
                #     COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                #     ac.product_pieces,
                #     ac.uom_id AS uom_id,
                #     ac.program_type
                # FROM tx_accessory_program ac 
                # LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                # LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                # LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1
                # LEFT JOIN (
                #     SELECT 
                #         tx.size_id,  
                #         tx.tm_id,
                #         SUM(tx.quantity) AS total_st_qty
                #     FROM tx_stiching_outward tx
                #     WHERE tx.status = 1
                #     AND tx.tm_id = %s
                #     AND tx.quality_id = %s
                #     AND tx.style_id = %s
                #     GROUP BY tx.size_id, tx.tm_id
                # ) AS tx_total ON tx_total.size_id = ac.size_id
                # WHERE tm.status = 1
                # AND ac.quantity > 0
                # AND ac.status = 1
                # AND tm.quality_id = %s
                # AND tm.style_id = %s
                # AND gp.group_type = 'Stiching'
                # AND ac.size_id IN (
                #     SELECT DISTINCT size_id 
                #     FROM tx_stiching_outward  
                #     WHERE status = 1 
                #         AND tm_id = %s
                #         AND quality_id = %s 
                #         AND style_id = %s
                # )
                # GROUP BY tm.quality_id, tm.style_id, ac.item_id, ac.size_id, ac.tm_id, ac.acc_size_id,
                #          ac.item_group_id, ac.acc_quality_id, gp.group_type, mx.color_id,
                #          ac.quantity, tx_total.total_st_qty, ac.product_pieces, ac.uom_id, ac.program_type;
  #    SELECT  
            #         ac.tm_id AS prg_id,
            #         ac.size_id,
            #         ac.item_id,
            #         ac.acc_size_id AS acc_size_id, 
            #         ac.item_group_id AS group_id,
            #         ac.acc_quality_id AS acc_quality_id,
            #         gp.group_type AS item_type,
            #         mx.color_id,
            #         tm.quality_id, 
            #         tm.style_id,
            #         ac.quantity AS prg_qty,
            #         COALESCE(tx_total_stiching.total_st_qty, 0) AS st_qty,
            #         COALESCE(tx_total_accessory.total_st_qty, 0) AS already_rec_qty, 
            #         ac.product_pieces,
            #         ac.uom_id AS uom_id,
            #         ac.program_type
            #         FROM tx_accessory_program ac 
            #         LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
            #         LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
            #         LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

            #         LEFT JOIN (
            #         SELECT 
            #             tx.size_id,  
            #             tx.tm_id,
            #             SUM(tx.quantity) AS total_st_qty 
            #         FROM tx_stiching_outward tx
            #         WHERE tx.status = 1
            #         AND tx.tm_id = %s
            #         AND tx.quality_id = %s
            #         AND tx.style_id =%s
            #         GROUP BY tx.size_id, tx.tm_id
            #         ) AS tx_total_stiching ON tx_total_stiching.size_id = ac.size_id

            #         LEFT JOIN (
            #         SELECT  
            #             tx.size_id,  
            #             tx.tm_id,
            #             SUM(tx.quantity) AS total_st_qty
            #         FROM tx_accessory_outward tx
            #         JOIN tm_accessory_outward tma ON tx.tm_id = tma.id AND tma.stiching_outward_id = %s
            #         WHERE tx.status = 1  
            #         GROUP BY tx.tm_id, tx.size_id
            #         ) AS tx_total_accessory ON tx_total_accessory.size_id = ac.size_id

            #         WHERE tm.status = 1
            #         AND ac.quantity > 0
            #         AND ac.status = 1
            #         AND tm.quality_id = %s
            #         AND tm.style_id = %s
            #         AND ac.size_id IN (
            #         SELECT DISTINCT size_id 
            #         FROM tx_stiching_outward  
            #         WHERE status = 1 
            #             AND tm_id = %s
            #             AND quality_id = %s
            #             AND style_id = %s
            #         )
            #         GROUP BY tm.quality_id,  
            #                 tm.style_id, 
            #                 ac.item_id, 
            #                 ac.size_id, 
            #                 ac.tm_id, 
            #                 ac.acc_size_id,
            #                 ac.item_group_id, 
            #                 ac.acc_quality_id, 
            #                 gp.group_type, 
            #                 mx.color_id,
            #                 ac.quantity, 
            #                 tx_total_stiching.total_st_qty, 
            #                 tx_total_accessory.total_st_qty,  -- Add here in group by if needed
            #                 ac.product_pieces, 
            #                 ac.uom_id, 
            #                 ac.program_type;




            
@csrf_exempt
def get_stiching_out_details_edit(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed

    try:
        # === Step 0: Parse POST inputs ===
        tm_id = request.POST.get('tm_id')
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        prg_id = request.POST.get('program_id')

        if not all([tm_id, stiching_id, quality_id, style_id, prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === Step 1: Run raw SQL to get accessory program data ===
        with connection.cursor() as cursor:
            sql = """
            SELECT  
                ac.tm_id AS prg_id,
                ac.size_id,
                ac.item_id,
                ac.acc_size_id AS acc_size_id, 
                ac.item_group_id AS group_id,
                ac.acc_quality_id AS acc_quality_id,
                gp.group_type AS item_type,
                mx.color_id,
                tm.quality_id, 
                tm.style_id,
                ac.uom_id AS uom_id, 
                ac.quantity AS prg_qty,
                ac.product_pieces,
                COALESCE(tx_total_stiching.total_st_qty, 0) AS st_qty,
                COALESCE(tx_total_accessory.total_st_qty, 0) AS already_rec_qty, 
                ( COALESCE(tx_total_stiching.total_st_qty,0) - COALESCE(tx_total_accessory.total_st_qty, 0)) AS balance_qty,
                
                ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                LEFT JOIN ( 
                SELECT 
                    tx.size_id,  
                    tx.tm_id,
                    SUM(tx.quantity) AS total_st_qty 
                FROM tx_stiching_outward tx
                WHERE tx.status = 1
                AND tx.tm_id = %s
                AND tx.quality_id = %s
                AND tx.style_id = %s
                --  GROUP BY tx.size_id, tx.tm_id 
                GROUP BY tx.tm_id
                ) AS tx_total_stiching ON tx_total_stiching.size_id = ac.size_id

                LEFT JOIN (
                SELECT  
                    tx.item_id,
                    tx.item_group_id,
                    SUM(tx.quantity) AS total_st_qty
                FROM tm_accessory_outward tma
                JOIN tx_accessory_outward tx ON tma.id = tx.tm_id 
                WHERE tx.status = 1 AND tma.stiching_outward_id = %s AND tma.id=%s AND tma.status=1 

                GROUP BY tx.item_id
                ) AS tx_total_accessory ON tx_total_accessory.item_id = ac.item_id

                WHERE tm.status = 1
                AND ac.quantity > 0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND ac.size_id IN (
                SELECT DISTINCT size_id 
                FROM tx_stiching_outward  
                WHERE status = 1 
                    AND tm_id = %s
                    AND quality_id = %s
                    AND style_id = %s
                )
                GROUP BY
                            tm.quality_id,  
                        tm.style_id, 
                        ac.item_id, 
                        ac.tm_id, 
                        ac.item_group_id, 
                        ac.acc_quality_id, 
                        gp.group_type, 
                        
                    --  ac.size_id, 
                    --  ac.acc_size_id,
                    --   mx.color_id,
                    --   ac.quantity, 
                    --    tx_total_stiching.total_st_qty, 
                    --   tx_total_accessory.total_st_qty,  -- Add here in group by if needed
                    --   ac.product_pieces, 
                    --   ac.uom_id, 
                    
                        ac.program_type;
                    

            """
            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,
                stiching_id,tm_id,
                quality_id, style_id,
                stiching_id, quality_id, style_id
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Step 2: Lookups ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True)
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results})
        group_ids = parse_ids({r['group_id'] for r in results})
        uom_ids = parse_ids({r['uom_id'] for r in results})
        q_ids = parse_ids({r['quality_id'] for r in results})
        s_ids = parse_ids({r['style_id'] for r in results})
        item_ids = parse_ids({r['item_id'] for r in results})
        acc_size_ids = parse_ids({r['acc_size_id'] for r in results})

        color_ids = set()
        for row in results:
            raw_color = row.get('color_id')
            if isinstance(raw_color, str):
                color_ids.update(int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit())
            elif isinstance(raw_color, int):
                color_ids.add(raw_color)

        # Lookup maps
        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Step 3: Enrich data ===
        enriched_data = []
        for row in results:
            if row['size_id'] not in valid_size_ids:
                continue

            raw_color = row.get('color_id')
            program_type = row.get('program_type')

            if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
                color_id_list = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
                for cid in color_id_list:
                    enriched_data.append({
                        **row,
                        'color_id': cid,
                        'color': color_map.get(cid, ''),
                        'quality': quality_map.get(row['quality_id'], ''),
                        'style': style_map.get(row['style_id'], ''),
                        'size': size_map.get(row['size_id'], ''),
                        'uom': uom_map.get(row['uom_id'], ''),
                        'item': item_map.get(row['item_id'], ''),
                        'group': group_map.get(row['group_id'], ''),
                        'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                        'acc_size': acc_size_map.get(row['acc_size_id'], '')
                    })
            else:
                cid = None
                if isinstance(raw_color, str) and raw_color.strip().isdigit():
                    cid = int(raw_color)
                elif isinstance(raw_color, int):
                    cid = raw_color

                enriched_data.append({
                    **row,
                    'color_id': cid,
                    'color': color_map.get(cid, '') if cid else '',
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')
                })



    # === Step 4: Get quantity from child_stiching_outward_table ===
        outward_data = list(child_stiching_outward_table.objects.filter(
            tm_id=stiching_id,
            quality_id=quality_id,  
            style_id=style_id,
            status=1
        ).values('size_id', 'color_id').annotate(total_qty=Sum('quantity')))

        # Map (size_id, color_id) to quantity
        qty_map = {}
        for rec in outward_data:
            qty_map[(rec['size_id'], rec['color_id'])] = float(rec['total_qty'])

        # Assign quantity to enriched_data
        for row in enriched_data:
            key = (row['size_id'], row.get('color_id'))
            row['child_stiching_qty'] = qty_map.get(key, 0.0)

        # 1. Build a better program_type mapping
        program_type_map = {}
        for row in enriched_data:
            p_type = row['program_type']
            size_id = row['size_id']
            color_id = row.get('color_id')

            if p_type == 'COLOR':
                key = (size_id, color_id)
                key_id = color_id
                key_name = row['color']
            elif p_type == 'SIZE':
                key = (size_id, None)  # Note: force None for color_id in size-based
                key_id = size_id
                key_name = row['size']
            else:
                continue

            # Important: only set if not already set (to avoid overwriting)
            if key not in program_type_map:
                program_type_map[key] = {
                    'program_type': p_type,
                    'key_id': key_id,
                    'key_name': key_name
                }

        # 2. Use mapping + qty_map to generate summary
        summary = defaultdict(lambda: {
            'program_type': '',
            'key_id': None,
            'key_name': '',
            'total_qty': 0.0
        })

        for (size_id, color_id), qty in qty_map.items():
            # First try with exact match (COLOR)
            key = (size_id, color_id)
            p_info = program_type_map.get(key)

            # If not found, try with (size_id, None) — for SIZE
            if not p_info:
                key = (size_id, None)
                p_info = program_type_map.get(key)

            if not p_info:
                continue  # no valid mapping, skip

            p_type = p_info['program_type']
            key_id = p_info['key_id']
            key_name = p_info['key_name']
            summary_key = (p_type, key_id)

            summary[summary_key]['program_type'] = p_type
            summary[summary_key]['key_id'] = key_id
            summary[summary_key]['key_name'] = key_name
            summary[summary_key]['total_qty'] += qty

        # print('end-data:',enriched_data)
        # Final return
        return JsonResponse({
            'data': enriched_data,
            'summary': list(summary.values())
        }, safe=False)


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



#  SELECT
#                     tx.item_id,
#                     prd.name AS item,
#                     tx.size_id,
#                     sz.name AS size,
#                     tx.acc_size_id,
#                     ac.name AS acc_size_name,
#                     tx.item_group_id AS group_id,
#                     grp.name AS group_name, 
#                     tx.acc_quality_id, 
#                     tx.color_id,
#                     clr.name AS color,
#                     tx.quality_id,
#                     qt.name AS quality,
#                     tx.style_id,
#                     st.name AS style,
#                     tx.uom_id,
#                     um.name AS uom,
#                     SUM(CASE WHEN tx.tm_id =1 THEN tx.quantity ELSE 0 END) AS current_outward_qty,
#                     SUM(CASE WHEN tx.tm_id !=1 THEN tx.quantity ELSE 0 END) AS other_outward_qty,

#                     tx.status AS tx_status,
#                     tma.status AS tma_status,
#                     tma.party_id AS tma_party_id

#                 FROM tx_accessory_outward tx
#                 LEFT JOIN tm_accessory_outward tma
#                     ON tma.id = tx.tm_id
#                 LEFT JOIN item prd
#                     ON prd.id = tx.item_id
#                 LEFT JOIN size sz
#                     ON tx.size_id=sz.id
#                 --    ON sz.id = tx.size_id
#                 LEFT JOIN accessory_size ac
#                     ON ac.id = tx.acc_size_id
#                 LEFT JOIN item_group grp
#                     ON grp.id = tx.item_group_id
#                 LEFT JOIN quality qt
#                     ON qt.id = tx.quality_id
#                 LEFT JOIN style st
#                     ON st.id = tx.style_id
#                 LEFT JOIN uom um
#                     ON tx.uom_id =  um.id
#                 LEFT JOIN color clr
#                     ON clr.id = tx.color_id


#                 WHERE
#                     tx.tm_id = 1 
#                     AND (tma.party_id = 82 OR tma.party_id IS NULL)
#                     -- AND tx.status = 1
#                     -- AND tma.status = 1

#                 GROUP BY
#                     tx.item_id, prd.name, tx.size_id, sz.name,
#                     tx.acc_size_id, ac.name, tx.item_group_id, grp.name,
#                     tx.acc_quality_id, tx.color_id, clr.name, tx.quality_id, qt.name,
#                     tx.style_id, st.name, tx.uom_id, um.name,
#                     tx.status, tma.status, tma.party_id;




                    

@csrf_exempt
def get_stiching_packing_out_details_edit(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed

    try:
        # === Step 0: Parse POST inputs ===  
        tm_id= request.POST.get('tm_id')
        party_id = request.POST.get('party_id')


        # stiching_id = request.POST.get('stiching_id')
        # quality_id = request.POST.get('quality_id')
        # style_id = request.POST.get('style_id')
        # prg_id = request.POST.get('program_id')

        # if not all([stiching_id, quality_id, style_id, prg_id]):
        if not all([tm_id, party_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === Step 1: Run raw SQL to get accessory program data ===
        with connection.cursor() as cursor:
            sql = """
             SELECT
                    tx.item_id,
                    prd.name AS item,
                    tx.size_id,
                    sz.name AS size,
                    tx.acc_size_id,
                    ac.name AS acc_size_name,
                    tx.item_group_id AS group_id,
                    grp.name AS group_name, 
                    tx.acc_quality_id, 
                    tx.color_id,
                    clr.name AS color,
                    tx.quality_id,
                    qt.name AS quality,
                    tx.style_id,
                    st.name AS style,
                    tx.uom_id,
                    um.name AS uom,
                    SUM(CASE WHEN tx.tm_id =1 THEN tx.quantity ELSE 0 END) AS current_outward_qty,
                    SUM(CASE WHEN tx.tm_id !=1 THEN tx.quantity ELSE 0 END) AS other_outward_qty,

                    tx.status AS tx_status,
                    tma.status AS tma_status,
                    tma.party_id AS tma_party_id

                FROM tx_accessory_outward tx
                LEFT JOIN tm_accessory_outward tma
                    ON tma.id = tx.tm_id
                LEFT JOIN item prd
                    ON prd.id = tx.item_id
                LEFT JOIN size sz
                    ON tx.size_id=sz.id
                --    ON sz.id = tx.size_id
                LEFT JOIN accessory_size ac
                    ON ac.id = tx.acc_size_id
                LEFT JOIN item_group grp
                    ON grp.id = tx.item_group_id
                LEFT JOIN quality qt
                    ON qt.id = tx.quality_id
                LEFT JOIN style st
                    ON st.id = tx.style_id
                LEFT JOIN uom um
                    ON tx.uom_id =  um.id
                LEFT JOIN color clr
                    ON clr.id = tx.color_id


                WHERE
                    tx.tm_id = 1 
                    AND (tma.party_id = 82 OR tma.party_id IS NULL)
                    -- AND tx.status = 1
                    -- AND tma.status = 1

                GROUP BY
                    tx.item_id, prd.name, tx.size_id, sz.name,
                    tx.acc_size_id, ac.name, tx.item_group_id, grp.name,
                    tx.acc_quality_id, tx.color_id, clr.name, tx.quality_id, qt.name,
                    tx.style_id, st.name, tx.uom_id, um.name,
                    tx.status, tma.status, tma.party_id;
                    

            """
            cursor.execute(sql, [
                tm_id,tm_id, tm_id, party_id
                
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Step 2: Lookups ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True)
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results})
        group_ids = parse_ids({r['group_id'] for r in results})
        uom_ids = parse_ids({r['uom_id'] for r in results})
        q_ids = parse_ids({r['quality_id'] for r in results})
        s_ids = parse_ids({r['style_id'] for r in results})
        item_ids = parse_ids({r['item_id'] for r in results})
        acc_size_ids = parse_ids({r['acc_size_id'] for r in results})

        color_ids = set()
        for row in results:
            raw_color = row.get('color_id')
            if isinstance(raw_color, str):
                color_ids.update(int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit())
            elif isinstance(raw_color, int):
                color_ids.add(raw_color)
 
        # Lookup maps
        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Step 3: Enrich data ===
        enriched_data = []
        for row in results:
            if row['size_id'] not in valid_size_ids:
                continue

            raw_color = row.get('color_id')
            program_type = row.get('program_type')

            if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
                color_id_list = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
                for cid in color_id_list:
                    enriched_data.append({
                        **row,
                        'color_id': cid,
                        'color': color_map.get(cid, ''),
                        'quality': quality_map.get(row['quality_id'], ''),
                        'style': style_map.get(row['style_id'], ''),
                        'size': size_map.get(row['size_id'], ''),
                        'uom': uom_map.get(row['uom_id'], ''),
                        'item': item_map.get(row['item_id'], ''),
                        'group': group_map.get(row['group_id'], ''),
                        'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                        'acc_size': acc_size_map.get(row['acc_size_id'], '')
                    })
            else:
                cid = None
                if isinstance(raw_color, str) and raw_color.strip().isdigit():
                    cid = int(raw_color)
                elif isinstance(raw_color, int):
                    cid = raw_color

                enriched_data.append({
                    **row,
                    'color_id': cid,
                    'color': color_map.get(cid, '') if cid else '',
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')
                })



    # === Step 4: Get quantity from child_stiching_outward_table ===
        outward_data = list(child_stiching_outward_table.objects.filter(
            tm_id=stiching_id,
            quality_id=quality_id,  
            style_id=style_id,
            status=1
        ).values('size_id', 'color_id').annotate(total_qty=Sum('quantity')))

        # Map (size_id, color_id) to quantity
        qty_map = {}
        for rec in outward_data:
            qty_map[(rec['size_id'], rec['color_id'])] = float(rec['total_qty'])

        # Assign quantity to enriched_data
        for row in enriched_data:
            key = (row['size_id'], row.get('color_id'))
            row['child_stiching_qty'] = qty_map.get(key, 0.0)

        # 1. Build a better program_type mapping

        program_type_map = {}
        for row in enriched_data:
            p_type = row['program_type']
            size_id = row['size_id']
            color_id = row.get('color_id')

            if p_type == 'COLOR':
                key = (size_id, color_id)
                key_id = color_id
                key_name = row['color']
            elif p_type == 'SIZE':
                key = (size_id, None)  # Note: force None for color_id in size-based
                key_id = size_id
                key_name = row['size']
            else:
                continue

            # Important: only set if not already set (to avoid overwriting)
            if key not in program_type_map:
                program_type_map[key] = {
                    'program_type': p_type,
                    'key_id': key_id,
                    'key_name': key_name
                }

        # 2. Use mapping + qty_map to generate summary
        summary = defaultdict(lambda: {
            'program_type': '',
            'key_id': None,
            'key_name': '',
            'total_qty': 0.0
        })

        for (size_id, color_id), qty in qty_map.items():
            # First try with exact match (COLOR)
            key = (size_id, color_id)
            p_info = program_type_map.get(key)

            # If not found, try with (size_id, None) — for SIZE
            if not p_info:
                key = (size_id, None)
                p_info = program_type_map.get(key)

            if not p_info:
                continue  # no valid mapping, skip

            p_type = p_info['program_type']
            key_id = p_info['key_id']
            key_name = p_info['key_name']
            summary_key = (p_type, key_id)

            summary[summary_key]['program_type'] = p_type
            summary[summary_key]['key_id'] = key_id
            summary[summary_key]['key_name'] = key_name
            summary[summary_key]['total_qty'] += qty

        # print('end-data:',enriched_data)
        # Final return
        return JsonResponse({
            'data': enriched_data,
            'summary': list(summary.values())
        }, safe=False)


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt
def get_stiching_packing_out_details_edit_7_10(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed

    try:
        # === Step 0: Parse POST inputs ===
        tm_id= request.POST.get('tm_id')
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        prg_id = request.POST.get('program_id')

        if not all([stiching_id, quality_id, style_id, prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === Step 1: Run raw SQL to get accessory program data ===
        with connection.cursor() as cursor:
            sql = """
            SELECT  
                ac.tm_id AS prg_id,
                ac.size_id,
                ac.item_id, 
                ac.acc_size_id AS acc_size_id, 
                ac.item_group_id AS group_id,
                ac.acc_quality_id AS acc_quality_id,
                gp.group_type AS item_type,
                mx.color_id,
                tm.quality_id, 
                tm.style_id,
                ac.uom_id AS uom_id, 
                ac.quantity AS prg_qty,
                ac.product_pieces,
                COALESCE(tx_total_stiching.total_st_qty, 0) AS st_qty,
                COALESCE(tx_total_accessory.total_st_qty, 0) AS already_rec_qty, 
                ( COALESCE(tx_total_stiching.total_st_qty,0) - COALESCE(tx_total_accessory.total_st_qty, 0)) AS balance_qty,
                
                ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                LEFT JOIN ( 
                SELECT 
                    tx.size_id,  
                    tx.tm_id,
                    SUM(tx.quantity) AS total_st_qty 
                FROM tx_stiching_outward tx
                WHERE tx.status = 1
                AND tx.tm_id = %s
                AND tx.quality_id = %s
                AND tx.style_id = %s
                --  GROUP BY tx.size_id, tx.tm_id 
                GROUP BY tx.tm_id
                ) AS tx_total_stiching ON tx_total_stiching.size_id = ac.size_id

                LEFT JOIN (
                SELECT  
                    tx.item_id,
                    tx.item_group_id,
                    SUM(tx.quantity) AS total_st_qty
                FROM tm_accessory_outward tma
                JOIN tx_accessory_outward tx ON tma.id = tx.tm_id 
                WHERE tx.status = 1 AND tma.sp_id = %s AND tma.id= %s AND tma.status=1 

                GROUP BY tx.item_id
                ) AS tx_total_accessory ON tx_total_accessory.item_id = ac.item_id

                WHERE tm.status = 1
                AND ac.quantity > 0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND ac.size_id IN (
                SELECT DISTINCT size_id 
                FROM tx_stiching_outward  
                WHERE status = 1 
                    AND tm_id = %s
                    AND quality_id = %s
                    AND style_id = %s
                )
                GROUP BY
                        tm.quality_id,  
                        tm.style_id, 
                        ac.item_id, 
                        ac.tm_id, 
                        ac.item_group_id, 
                        ac.acc_quality_id, 
                        gp.group_type, 
                        
                      ac.size_id, 
                     ac.acc_size_id,
                    --   mx.color_id,
                    --   ac.quantity, 
                    --    tx_total_stiching.total_st_qty, 
                    --   tx_total_accessory.total_st_qty,  -- Add here in group by if needed
                    --   ac.product_pieces, 
                    --   ac.uom_id, 
                    
                        ac.program_type;
                    

            """
            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,
                stiching_id,tm_id,
                quality_id, style_id,
                stiching_id, quality_id, style_id
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Step 2: Lookups ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True)
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results})
        group_ids = parse_ids({r['group_id'] for r in results})
        uom_ids = parse_ids({r['uom_id'] for r in results})
        q_ids = parse_ids({r['quality_id'] for r in results})
        s_ids = parse_ids({r['style_id'] for r in results})
        item_ids = parse_ids({r['item_id'] for r in results})
        acc_size_ids = parse_ids({r['acc_size_id'] for r in results})

        color_ids = set()
        for row in results:
            raw_color = row.get('color_id')
            if isinstance(raw_color, str):
                color_ids.update(int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit())
            elif isinstance(raw_color, int):
                color_ids.add(raw_color)
 
        # Lookup maps
        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Step 3: Enrich data ===
        enriched_data = []
        for row in results:
            if row['size_id'] not in valid_size_ids:
                continue

            raw_color = row.get('color_id')
            program_type = row.get('program_type')

            if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
                color_id_list = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
                for cid in color_id_list:
                    enriched_data.append({
                        **row,
                        'color_id': cid,
                        'color': color_map.get(cid, ''),
                        'quality': quality_map.get(row['quality_id'], ''),
                        'style': style_map.get(row['style_id'], ''),
                        'size': size_map.get(row['size_id'], ''),
                        'uom': uom_map.get(row['uom_id'], ''),
                        'item': item_map.get(row['item_id'], ''),
                        'group': group_map.get(row['group_id'], ''),
                        'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                        'acc_size': acc_size_map.get(row['acc_size_id'], '')
                    })
            else:
                cid = None
                if isinstance(raw_color, str) and raw_color.strip().isdigit():
                    cid = int(raw_color)
                elif isinstance(raw_color, int):
                    cid = raw_color

                enriched_data.append({
                    **row,
                    'color_id': cid,
                    'color': color_map.get(cid, '') if cid else '',
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')
                })



    # === Step 4: Get quantity from child_stiching_outward_table ===
        outward_data = list(child_stiching_outward_table.objects.filter(
            tm_id=stiching_id,
            quality_id=quality_id,  
            style_id=style_id,
            status=1
        ).values('size_id', 'color_id').annotate(total_qty=Sum('quantity')))

        # Map (size_id, color_id) to quantity
        qty_map = {}
        for rec in outward_data:
            qty_map[(rec['size_id'], rec['color_id'])] = float(rec['total_qty'])

        # Assign quantity to enriched_data
        for row in enriched_data:
            key = (row['size_id'], row.get('color_id'))
            row['child_stiching_qty'] = qty_map.get(key, 0.0)

        # 1. Build a better program_type mapping

        program_type_map = {}
        for row in enriched_data:
            p_type = row['program_type']
            size_id = row['size_id']
            color_id = row.get('color_id')

            if p_type == 'COLOR':
                key = (size_id, color_id)
                key_id = color_id
                key_name = row['color']
            elif p_type == 'SIZE':
                key = (size_id, None)  # Note: force None for color_id in size-based
                key_id = size_id
                key_name = row['size']
            else:
                continue

            # Important: only set if not already set (to avoid overwriting)
            if key not in program_type_map:
                program_type_map[key] = {
                    'program_type': p_type,
                    'key_id': key_id,
                    'key_name': key_name
                }

        # 2. Use mapping + qty_map to generate summary
        summary = defaultdict(lambda: {
            'program_type': '',
            'key_id': None,
            'key_name': '',
            'total_qty': 0.0
        })

        for (size_id, color_id), qty in qty_map.items():
            # First try with exact match (COLOR)
            key = (size_id, color_id)
            p_info = program_type_map.get(key)

            # If not found, try with (size_id, None) — for SIZE
            if not p_info:
                key = (size_id, None)
                p_info = program_type_map.get(key)

            if not p_info:
                continue  # no valid mapping, skip

            p_type = p_info['program_type']
            key_id = p_info['key_id']
            key_name = p_info['key_name']
            summary_key = (p_type, key_id)

            summary[summary_key]['program_type'] = p_type
            summary[summary_key]['key_id'] = key_id
            summary[summary_key]['key_name'] = key_name
            summary[summary_key]['total_qty'] += qty

        # print('end-data:',enriched_data)
        # Final return
        return JsonResponse({
            'data': enriched_data,
            'summary': list(summary.values())
        }, safe=False)


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def get_stiching_out_details(request):
 
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        program_id = request.POST.get('program_id')      # optional
        stitching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([stitching_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === SQL: fetch accessory program rows + summed outward (sp_qty) for the given stitching instance ===
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    ac.tm_id AS prg_id, 
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id,
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    COALESCE(tx_total.total_st_qty, 0) AS sp_qty,
                    ac.quantity AS prg_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac
                LEFT JOIN tm_accessory_program tm 
                    ON ac.tm_id = tm.id
                LEFT JOIN item_group gp 
                    ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx 
                    ON ac.item_id = mx.item_id AND mx.status = 1
                LEFT JOIN (
                    SELECT
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                        AND tx.tm_id = %s
                        AND tx.quality_id = %s
                        AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id
                WHERE tm.status = 1
                    AND ac.quantity > 0
                    AND ac.status = 1
                    AND gp.group_type = 'Stiching'
                    AND tm.quality_id = %s
                    AND tm.style_id = %s
                    AND ac.size_id IN (
                        SELECT DISTINCT size_id
                        FROM tx_stiching_outward
                        WHERE status = 1
                            AND tm_id = %s
                            AND quality_id = %s
                            AND style_id = %s
                    )
                GROUP BY
                    ac.tm_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id,
                    ac.item_group_id,
                    ac.acc_quality_id,
                    gp.group_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    ac.uom_id,
                    ac.program_type
                /* Add comments to explain complex joins and groupings */

            """

            # Build params in the same order as placeholders:
            # tx_total subquery uses (stitching_id, quality_id, style_id)
            # the WHERE tm.quality_id, tm.style_id use (quality_id, style_id)
            # the IN() subquery uses (stitching_id, quality_id, style_id)  

            params = [
                stitching_id, quality_id, style_id,
                quality_id, style_id,
                stitching_id, quality_id, style_id
            ]

            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Validate relevant size IDs from child tx table ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stitching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        # === Prepare mapping dictionaries ===
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))
        acc_quality_ids = {r['acc_quality_id'] for r in results if r.get('acc_quality_id')}
        group_ids = {r['group_id'] for r in results if r.get('group_id')}
        uom_ids = {r['uom_id'] for r in results if r.get('uom_id')}
        item_ids = {r['item_id'] for r in results if r.get('item_id')}
        quality_ids = {r['quality_id'] for r in results if r.get('quality_id')}
        style_ids = {r['style_id'] for r in results if r.get('style_id')}
        # color_ids = {r['color_id'] for r in results if r.get('color_id')}
        acc_size_ids = {r['acc_size_id'] for r in results if r.get('acc_size_id')}

        color_ids = set()
        for r in results:
            color_val = r.get('color_id')
            if color_val:
                if isinstance(color_val, str) and ',' in color_val:
                    color_ids.update(int(c.strip()) for c in color_val.split(',') if c.strip().isdigit())
                else:
                    try:
                        color_ids.add(int(color_val))
                    except (ValueError, TypeError): 
                        pass



        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=quality_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=style_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Enrich results and deduplicate ===
        enriched_data = []
        seen_keys = set()  
        for row in results:
            # ensure size is valid
            if row['size_id'] not in valid_size_ids:
                continue

            # choose a dedupe key (item, size, acc_quality, uom) - you can change as needed
            key = (row.get('item_id'), row.get('size_id'), row.get('acc_quality_id'), row.get('uom_id'))
            if key in seen_keys:
                continue
            seen_keys.add(key)

            enriched_data.append({
                **row,
                'quality': quality_map.get(row.get('quality_id'), ''),
                'style': style_map.get(row.get('style_id'), ''),
                'size': size_map.get(row.get('size_id'), ''),
                'uom': uom_map.get(row.get('uom_id'), ''),
                'color': color_map.get(row.get('color_id'), ''),
                'item': item_map.get(row.get('item_id'), ''),
                'group': group_map.get(row.get('group_id'), ''),
                'acc_quality': acc_quality_map.get(row.get('acc_quality_id'), ''),
                'acc_size': acc_size_map.get(row.get('acc_size_id'), ''),   # use acc_size_id
            })

        # === Build summary (sums per program key) ===
        summary_map = defaultdict(lambda: {'program_type': '', 'key_id': None, 'total_qty': 0.0})

        for row in enriched_data:
            program_type = (row.get('program_type') or '').upper()
            if program_type == 'COLOR':
                key_id = row.get('color_id')
            elif program_type == 'SIZE':
                key_id = row.get('size_id')
            elif program_type == 'TOTAL QUANTITY':
                key_id = row.get('tm_id')  # group by program instance / tm_id
            else:
                # if other program types exist, you may decide how to handle them
                key_id = None

            if key_id is None:
                continue

            map_key = f"{program_type}|{key_id}"
            summary_map[map_key]['program_type'] = program_type
            summary_map[map_key]['key_id'] = key_id
            # sum sp_qty across rows for this key
            summary_map[map_key]['total_qty'] += float(row.get('sp_qty') or 0.0)

        summary_data = list(summary_map.values())

        # === Response ===
        return JsonResponse({
            'data': enriched_data,
            'summary': summary_data
        }, safe=False)


    except Exception as e:
        # return error for debugging — you can hide details in production
        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt
def get_stiching_out_details_4_10(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed

    try:
        # === Step 0: Parse POST inputs ===
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        prg_id = request.POST.get('program_id')

        if not all([stiching_id, quality_id, style_id, prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === Step 1: Run raw SQL to get accessory program data ===
        with connection.cursor() as cursor:
            sql = """
                SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1
                LEFT JOIN (
                    SELECT 
                        tx.size_id,  
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id
                WHERE tm.status = 1
                AND ac.quantity > 0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward  
                    WHERE status = 1 
                        AND tm_id = %s
                        AND quality_id = %s 
                        AND style_id = %s
                )
                GROUP BY tm.quality_id, tm.style_id, ac.item_id, ac.size_id, ac.tm_id, ac.acc_size_id,
                         ac.item_group_id, ac.acc_quality_id, gp.group_type, mx.color_id,
                         ac.quantity, tx_total.total_st_qty, ac.product_pieces, ac.uom_id, ac.program_type;
            """
            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,
                quality_id, style_id,
                stiching_id, quality_id, style_id
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Step 2: Lookups ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True)
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results})
        group_ids = parse_ids({r['group_id'] for r in results})
        uom_ids = parse_ids({r['uom_id'] for r in results})
        q_ids = parse_ids({r['quality_id'] for r in results})
        s_ids = parse_ids({r['style_id'] for r in results})
        item_ids = parse_ids({r['item_id'] for r in results})
        acc_size_ids = parse_ids({r['acc_size_id'] for r in results})

        color_ids = set()
        for row in results:
            raw_color = row.get('color_id')
            if isinstance(raw_color, str):
                color_ids.update(int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit())
            elif isinstance(raw_color, int):
                color_ids.add(raw_color)

        # Lookup maps
        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Step 3: Enrich data ===
        enriched_data = []
        for row in results:
            if row['size_id'] not in valid_size_ids:
                continue

            raw_color = row.get('color_id')
            program_type = row.get('program_type')

            if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
                color_id_list = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
                for cid in color_id_list:
                    enriched_data.append({
                        **row,
                        'color_id': cid,
                        'color': color_map.get(cid, ''),
                        'quality': quality_map.get(row['quality_id'], ''),
                        'style': style_map.get(row['style_id'], ''),
                        'size': size_map.get(row['size_id'], ''),
                        'uom': uom_map.get(row['uom_id'], ''),
                        'item': item_map.get(row['item_id'], ''),
                        'group': group_map.get(row['group_id'], ''),
                        'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                        'acc_size': acc_size_map.get(row['acc_size_id'], '')
                    })
            else:
                cid = None
                if isinstance(raw_color, str) and raw_color.strip().isdigit():
                    cid = int(raw_color)
                elif isinstance(raw_color, int):
                    cid = raw_color

                enriched_data.append({
                    **row,
                    'color_id': cid,
                    'color': color_map.get(cid, '') if cid else '',
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')
                })

        # === Step 4: Get quantity from child_stiching_outward_table ===
        # outward_data = list(child_stiching_outward_table.objects.filter(
        #     tm_id=stiching_id,
        #     quality_id=quality_id,
        #     style_id=style_id,
        #     status=1
        # ).values('size_id', 'color_id').annotate(total_qty=Sum('quantity')))

        # qty_map = {}
        # for rec in outward_data:
        #     qty_map[(rec['size_id'], rec['color_id'])] = float(rec['total_qty'])

        # for row in enriched_data:
        #     key = (row['size_id'], row.get('color_id'))
        #     row['child_stiching_qty'] = qty_map.get(key, 0.0)

        # # === Step 5: Summary by program_type ===
        # summary = defaultdict(lambda: {
        #     'program_type': '',
        #     'key_id': None,
        #     'key_name': '',
        #     'total_qty': 0.0
        # })

        # for row in enriched_data:
        #     p_type = row['program_type']
        #     if p_type == 'COLOR':
        #         key = ('COLOR', row['color_id'])
        #         key_name = row['color']
        #     elif p_type == 'SIZE':
        #         key = ('SIZE', row['size_id'])
        #         key_name = row['size']
        #     else:
        #         continue

        #     summary[key]['program_type'] = p_type
        #     summary[key]['key_id'] = key[1]
        #     summary[key]['key_name'] = key_name
        #     summary[key]['total_qty'] += float(row.get('child_stiching_qty', 0.0))

        # return JsonResponse({
        #     'data': enriched_data,
        #     'summary': list(summary.values())
        # }, safe=False)

    # === Step 4: Get quantity from child_stiching_outward_table ===
        outward_data = list(child_stiching_outward_table.objects.filter(
            tm_id=stiching_id,
            quality_id=quality_id,  
            style_id=style_id,
            status=1
        ).values('size_id', 'color_id').annotate(total_qty=Sum('quantity')))

        # Map (size_id, color_id) to quantity
        qty_map = {}
        for rec in outward_data:
            qty_map[(rec['size_id'], rec['color_id'])] = float(rec['total_qty'])

        # Assign quantity to enriched_data
        for row in enriched_data:
            key = (row['size_id'], row.get('color_id'))
            row['child_stiching_qty'] = qty_map.get(key, 0.0)

        # === Step 5: Summary by program_type ===

        # Build mapping of (size_id, color_id) -> program_type and name
        # program_type_map = {}
        # for row in enriched_data:
        #     key = (row['size_id'], row.get('color_id'))
        #     p_type = row['program_type']
        #     if p_type == 'COLOR':
        #         key_id = row['color_id']
        #         key_name = row['color']
        #     elif p_type == 'SIZE':
        #         key_id = row['size_id']
        #         key_name = row['size']
        #     else:
        #         continue
        #     program_type_map[key] = {
        #         'program_type': p_type,
        #         'key_id': key_id,
        #         'key_name': key_name
        #     }

        # # Now aggregate correctly using qty_map and program_type_map
        # summary = defaultdict(lambda: {
        #     'program_type': '',
        #     'key_id': None,
        #     'key_name': '',
        #     'total_qty': 0.0
        # })

        # for (size_id, color_id), qty in qty_map.items():
        #     key = (size_id, color_id)
        #     p_info = program_type_map.get(key)
        #     if not p_info:
        #         continue

        #     p_type = p_info['program_type']
        #     key_id = p_info['key_id']
        #     key_name = p_info['key_name']
        #     summary_key = (p_type, key_id)

        #     summary[summary_key]['program_type'] = p_type
        #     summary[summary_key]['key_id'] = key_id
        #     summary[summary_key]['key_name'] = key_name
        #     summary[summary_key]['total_qty'] += qty

        # === Step 5: Summary by program_type ===

        # 1. Build a better program_type mapping
        program_type_map = {}
        for row in enriched_data:
            p_type = row['program_type']
            size_id = row['size_id']
            color_id = row.get('color_id')

            if p_type == 'COLOR':
                key = (size_id, color_id)
                key_id = color_id
                key_name = row['color']
            elif p_type == 'SIZE':
                key = (size_id, None)  # Note: force None for color_id in size-based
                key_id = size_id
                key_name = row['size']
            else:
                continue

            # Important: only set if not already set (to avoid overwriting)
            if key not in program_type_map:
                program_type_map[key] = {
                    'program_type': p_type,
                    'key_id': key_id,
                    'key_name': key_name
                }

        # 2. Use mapping + qty_map to generate summary
        summary = defaultdict(lambda: {
            'program_type': '',
            'key_id': None,
            'key_name': '',
            'total_qty': 0.0
        })

        for (size_id, color_id), qty in qty_map.items():
            # First try with exact match (COLOR)
            key = (size_id, color_id)
            p_info = program_type_map.get(key)

            # If not found, try with (size_id, None) — for SIZE
            if not p_info:
                key = (size_id, None)
                p_info = program_type_map.get(key)

            if not p_info:
                continue  # no valid mapping, skip

            p_type = p_info['program_type']
            key_id = p_info['key_id']
            key_name = p_info['key_name']
            summary_key = (p_type, key_id)

            summary[summary_key]['program_type'] = p_type
            summary[summary_key]['key_id'] = key_id
            summary[summary_key]['key_name'] = key_name
            summary[summary_key]['total_qty'] += qty

        # print('end-data:',enriched_data)
        # Final return
        return JsonResponse({
            'data': enriched_data,
            'summary': list(summary.values())
        }, safe=False)


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def get_stiching_out_details_test_(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed

    try:
        # POST parameters
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        prg_id = request.POST.get('program_id')

        if not all([stiching_id, quality_id, style_id, prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === Step 1: Raw SQL query to get data ===
        with connection.cursor() as cursor:
            sql = """
                SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id

                WHERE tm.status = 1
                AND ac.quantity > 0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward  
                    WHERE status = 1 
                        AND tm_id = %s
                        AND quality_id = %s 
                        AND style_id = %s
                )
                GROUP BY tm.quality_id, tm.style_id, ac.item_id, ac.size_id, ac.tm_id, ac.acc_size_id,
                         ac.item_group_id, ac.acc_quality_id, gp.group_type, mx.color_id,
                         ac.quantity, tx_total.total_st_qty, ac.product_pieces, ac.uom_id, ac.program_type;
            """

            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,
                quality_id, style_id,
                stiching_id, quality_id, style_id
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Step 2: Lookup valid sizes and mappings ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True)
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        # Extract IDs for lookups
        acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results})
        group_ids = parse_ids({r['group_id'] for r in results})
        uom_ids = parse_ids({r['uom_id'] for r in results})
        q_ids = parse_ids({r['quality_id'] for r in results})
        s_ids = parse_ids({r['style_id'] for r in results})
        item_ids = parse_ids({r['item_id'] for r in results})
        acc_size_ids = parse_ids({r['acc_size_id'] for r in results})

        color_ids = set()
        for row in results:
            raw_color = row.get('color_id')
            if isinstance(raw_color, str):
                color_ids.update(int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit())
            elif isinstance(raw_color, int):
                color_ids.add(raw_color)

        # Lookup tables
        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

        # === Step 3: Enrich data with lookup names ===
        enriched_data = []
        for row in results:
            if row['size_id'] not in valid_size_ids:
                continue

            raw_color = row.get('color_id')
            program_type = row.get('program_type')

            # Handle multiple color_ids for COLOR program_type
            if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
                color_id_list = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
                for cid in color_id_list:
                    enriched_data.append({
                        **row,
                        'color_id': cid,
                        'color': color_map.get(cid, ''),
                        'quality': quality_map.get(row['quality_id'], ''),
                        'style': style_map.get(row['style_id'], ''),
                        'size': size_map.get(row['size_id'], ''),
                        'uom': uom_map.get(row['uom_id'], ''),
                        'item': item_map.get(row['item_id'], ''),
                        'group': group_map.get(row['group_id'], ''),
                        'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                        'acc_size': acc_size_map.get(row['acc_size_id'], '')
                    })
            else:
                cid = None
                if isinstance(raw_color, str) and raw_color.strip().isdigit():
                    cid = int(raw_color)
                elif isinstance(raw_color, int):
                    cid = raw_color

                enriched_data.append({
                    **row,
                    'color_id': cid,
                    'color': color_map.get(cid, '') if cid else '',
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')
                })

        # === Step 4: Get quantity from child_stiching_outward_table for size and color ===
        size_color_pairs = set()
        for row in enriched_data:
            size_id = row['size_id']
            color_id = row.get('color_id')
            if color_id is not None:
                size_color_pairs.add((size_id, color_id))
            else:
                size_color_pairs.add((size_id, None))

        # Build Q filters
        q_filters = Q(status=1, tm_id=stiching_id, quality_id=quality_id, style_id=style_id)
        q_subfilters = Q()
        for s, c in size_color_pairs:
            if c is not None:
                q_subfilters |= Q(size_id=s, color_id=c)
            else:
                q_subfilters |= Q(size_id=s, color_id__isnull=True)

        q_filters &= q_subfilters

        qty_records = child_stiching_outward_table.objects.filter(q_filters).values('size_id', 'color_id').annotate(total_qty=Sum('quantity'))

        qty_map = {}
        for rec in qty_records:
            key = (rec['size_id'], rec['color_id'])
            qty_map[key] = rec['total_qty']

        # Add child stitching qty into enriched_data
        for row in enriched_data:
            key = (row['size_id'], row.get('color_id'))
            row['child_stiching_qty'] = qty_map.get(key, 0)

        # === Step 5: Summarize based on child stitching quantity and program_type ===
        summary = defaultdict(lambda: {
            'program_type': None,
            'key_id': None,
            'key_name': '',
            'total_qty': 0,
            'details': defaultdict(float)
        })

        for row in enriched_data:
            ptype = row.get('program_type')
            qty = float(row.get('child_stiching_qty') or 0)

            if ptype == 'COLOR':
                cid = row.get('color_id')
                size = row.get('size')
                key = ('COLOR', cid)
                summary[key]['program_type'] = 'COLOR'
                summary[key]['key_id'] = cid
                summary[key]['key_name'] = row.get('color', '')
                summary[key]['total_qty'] += qty
                summary[key]['details'][size] += qty

            elif ptype == 'SIZE':
                sid = row.get('size_id')
                key = ('SIZE', sid)
                summary[key]['program_type'] = 'SIZE'
                summary[key]['key_id'] = sid
                summary[key]['key_name'] = row.get('size', '')
                summary[key]['total_qty'] += qty

            else:
                key = (ptype, None)
                summary[key]['program_type'] = ptype
                summary[key]['key_id'] = None
                summary[key]['key_name'] = ''
                summary[key]['total_qty'] += qty

        # Format summary list
        summary_list = []
        for (ptype, keyid), data in summary.items():
            entry = {
                'program_type': data['program_type'],
                'id': data['key_id'],
                'name': data['key_name'],
                'total_qty': round(data['total_qty'], 2),
            }
            if data['program_type'] == 'COLOR':
                entry['sizes'] = {size: round(qty, 2) for size, qty in data['details'].items()}
            summary_list.append(entry)

        # === Step 6: Return data and summary ===
        return JsonResponse({
            'data': enriched_data,
            'summary': summary_list
        })
 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def get_stiching_out_details_30_tet2(request):
    if request.method != 'POST': 
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed

    try:
        # Get required POST params
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        prg_id = request.POST.get('program_id')

        if not all([stiching_id, quality_id, style_id, prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # === SQL Query ===
        with connection.cursor() as cursor:
            sql = """
                SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id

                LEFT JOIN tx_stiching_inward si ON si.outward_id = tx_total.tm_id 
                                                AND si.size_id = tx_total.size_id
                                                AND si.status = 1

                WHERE tm.status = 1
                AND ac.quantity > 0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward  
                    WHERE status = 1 
                        AND tm_id = %s
                        AND quality_id = %s 
                        AND style_id = %s
                )
                GROUP BY tm.quality_id, tm.style_id, ac.item_id, ac.size_id;
            """

            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,  # For subquery
                quality_id, style_id,               # WHERE filters
                stiching_id, quality_id, style_id   # size_id subquery
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Fetch valid size names ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )
        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        # === Prepare sets for bulk fetching related info ===
        acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results if r['acc_quality_id']})
        group_ids = parse_ids({r['group_id'] for r in results if r['group_id']})
        uom_ids = parse_ids({r['uom_id'] for r in results if r['uom_id']})
        q_ids = parse_ids({r['quality_id'] for r in results if r['quality_id']})
        s_ids = parse_ids({r['style_id'] for r in results if r['style_id']})
        color_ids = parse_ids({r['color_id'] for r in results if r['color_id']})
        item_ids = parse_ids({r['item_id'] for r in results if r['item_id']})
        acc_size_ids = parse_ids({r['acc_size_id'] for r in results if r['acc_size_id']})

        # === Build lookup maps ===
        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))


        # === Enrich final data ===
        # enriched_data = []
        # for row in results:
        #     if row['size_id'] in valid_size_ids:
        #         enriched_data.append({
        #             **row,
        #             'quality': quality_map.get(row['quality_id'], ''),
        #             'style': style_map.get(row['style_id'], ''),
        #             'size': size_map.get(row['size_id'], ''),
        #             'uom': uom_map.get(row['uom_id'], ''),
        #             'color': color_map.get(row['color_id'], ''),  # ✅ Now correctly mapped
        #             'item': item_map.get(row['item_id'], ''),
        #             'group': group_map.get(row['group_id'], ''),
        #             'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
        #             'acc_size': acc_size_map.get(row['acc_size_id'], '')
        #         })



        enriched_data = []

        for row in results:
            if row['size_id'] not in valid_size_ids:
                continue

            raw_color = row.get('color_id')
            program_type = row.get('program_type')

            # Handle multi-color row splitting only if program_type == 'COLOR'
            if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
                color_ids = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
                for cid in color_ids:
                    enriched_data.append({
                        **row,
                        'color_id': cid,
                        'color': color_map.get(cid, ''),
                        'quality': quality_map.get(row['quality_id'], ''),
                        'style': style_map.get(row['style_id'], ''),
                        'size': size_map.get(row['size_id'], ''),
                        'uom': uom_map.get(row['uom_id'], ''),
                        'item': item_map.get(row['item_id'], ''),
                        'group': group_map.get(row['group_id'], ''),
                        'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                        'acc_size': acc_size_map.get(row['acc_size_id'], '')
                    })
            else:
                # Single color or non-COLOR program type
                if isinstance(raw_color, str) and raw_color.strip().isdigit():
                    color_id = int(raw_color)
                elif isinstance(raw_color, int):
                    color_id = raw_color
                else:
                    color_id = None

                enriched_data.append({
                    **row,
                    'color_id': color_id,
                    'color': color_map.get(color_id, '') if color_id else '',
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')
                })

        # Enrich each row
        # enriched_data = []
        # for row in results:
        #     if row['size_id'] in valid_size_ids:
        #         # Handle multi-color case 
        #         color_names = []
        #         raw_color = row.get('color_id') 
        #         if isinstance(raw_color, str):
        #             color_ids = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
        #             color_names = [color_map.get(cid, '') for cid in color_ids if cid in color_map]
        #         elif isinstance(raw_color, int):
        #             color_names = [color_map.get(raw_color, '')]


        #         enriched_data.append({
        #             **row,
        #             'quality': quality_map.get(row['quality_id'], ''),
        #             'style': style_map.get(row['style_id'], ''),
        #             'size': size_map.get(row['size_id'], ''),
        #             'uom': uom_map.get(row['uom_id'], ''),
        #             'color': ', '.join(filter(None, color_names)),  # ✅ Fixed
        #             'item': item_map.get(row['item_id'], ''),
        #             'group': group_map.get(row['group_id'], ''),
        #             'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
        #             'acc_size': acc_size_map.get(row['acc_size_id'], '')
        #         })


        return JsonResponse({'data': enriched_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def get_stiching_out_details_30(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        """

        Parses a set/list of IDs which might be integers or comma-separated strings,
        returning a set of integers.
        """

        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed
    

    try:
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id') 
        prg_id = request.POST.get('program_id')

        print('st-id:', stiching_id, quality_id, style_id)

        if not all([stiching_id, quality_id, style_id,prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        with connection.cursor() as cursor:
            sql = """
               
                SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    -- Balance quantity after subtracting the inward quantity
                    --   COALESCE((tx_total.total_st_qty), 0) - COALESCE((si.quantity), 0) AS balance_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                -- Join to stitching outward to get matching size_ids and total st_qty
                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id

                -- Join to stitching inward to get quantities that have already been processed
                LEFT JOIN tx_stiching_inward si ON si.outward_id = tx_total.tm_id 
                                                AND si.size_id = tx_total.size_id
                                                AND si.status = 1

                -- Exclude records that already exist in tx_stiching_inward
                WHERE tm.status = 1
                AND ac.quantity >0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward  
                    WHERE status = 1 
                        AND tm_id = %s
                        AND quality_id = %s 
                        AND style_id = %s
                )
                GROUP BY  
                    tm.quality_id,
                    tm.style_id,
                    ac.item_id,
                    ac.size_id; 
            """ 

            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,  # For subquery join
                quality_id, style_id,               # For main WHERE filter
                stiching_id, quality_id, style_id   # For size_id IN ()
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Name Mapping & Validation ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        # Extract sets of IDs from query results
        acc_quality_id = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_id = {r['group_id'] for r in results if r['group_id']}
        uom_id = {r['uom_id'] for r in results if r['uom_id']}
        prg_id = {r['prg_id'] for r in results if r['prg_id']}
        q_ids = {r['quality_id'] for r in results if r['quality_id']}
        s_ids = {r['style_id'] for r in results if r['style_id']}
        c_ids = {r['color_id'] for r in results if r['color_id']}
        i_ids = {r['item_id'] for r in results if r['item_id']}
        acc_size = {r['acc_size_id'] for r in results if r['acc_size_id']}

        # Parse all these sets to handle comma-separated strings and convert to int
        acc_quality_id = parse_ids(acc_quality_id)
        group_id = parse_ids(group_id)
        uom_id = parse_ids(uom_id)
        prg_id = parse_ids(prg_id)
        q_ids = parse_ids(q_ids)
        s_ids = parse_ids(s_ids)
        c_ids = parse_ids(c_ids)
        i_ids = parse_ids(i_ids)
        acc_size = parse_ids(acc_size)

        # Fetch color mappings carefully, parsing color_id strings if needed
        color_mappings = sub_size_table.objects.filter(item_id__in=i_ids).values('item_id', 'm_color_id')

        item_color_map = defaultdict(list)
        for entry in color_mappings: 
            color_id = entry['m_color_id']
            if isinstance(color_id, str) and ',' in color_id:
                parsed = [int(cid.strip()) for cid in color_id.split(',') if cid.strip().isdigit()]
            else:
                parsed = [int(color_id)] if str(color_id).isdigit() else []
            item_color_map[entry['item_id']].extend(parsed)

        # Flatten color ids from item_color_map
        all_color_ids = set(cid for cids in item_color_map.values() for cid in cids)

        acc_items = sub_size_table.objects.filter(color_id__in=all_color_ids).values('m_color_id', 'item_id')
        acc_item_map = {entry['m_color_id']: entry['item_id'] for entry in acc_items}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_id).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_id).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_id).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=all_color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size).values_list('id', 'name'))

        enriched_data = []
        for row in results:
            if row['size_id'] in valid_size_ids:
                enriched_data.append({
                    **row, 
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''), 
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''), 
                    'item': item_map.get(row['item_id'], ''), 
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')  # fixed from size_id to acc_size_id
                })

        return JsonResponse({'data': enriched_data})
 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 


@csrf_exempt
def get_stiching_out_details_29_last(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        """

        Parses a set/list of IDs which might be integers or comma-separated strings,
        returning a set of integers.
        """

        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed
    

    try:
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id') 
        prg_id = request.POST.get('program_id')

        print('st-id:', stiching_id, quality_id, style_id)

        if not all([stiching_id, quality_id, style_id,prg_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        with connection.cursor() as cursor:
            sql = """
               SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    -- Balance quantity after subtracting the inward quantity
                    COALESCE((tx_total.total_st_qty), 0) - COALESCE((si.quantity), 0) AS balance_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac 
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                -- Join to stitching outward to get matching size_ids and total st_qty
                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id

                -- Join to stitching inward to get quantities that have already been processed
                LEFT JOIN tx_stiching_inward si ON si.outward_id = tx_total.tm_id 
                                                AND si.size_id = tx_total.size_id
                                                AND si.status = 1

                -- Exclude records that already exist in tx_stiching_inward
                WHERE tm.status = 1
                AND ac.quantity >0
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward  
                    WHERE status = 1 
                        AND tm_id = %s 
                        AND quality_id = %s 
                        AND style_id = %s 
                )
                GROUP BY  
                    tm.quality_id,
                    tm.style_id,
                    ac.item_id,
                    ac.size_id; 
            """ 

            cursor.execute(sql, [
                prg_id,
                stiching_id, quality_id, style_id,  # For subquery join
                quality_id, style_id,               # For main WHERE filter
                stiching_id, quality_id, style_id   # For size_id IN ()
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Name Mapping & Validation ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        # Extract sets of IDs from query results
        acc_quality_id = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_id = {r['group_id'] for r in results if r['group_id']}
        uom_id = {r['uom_id'] for r in results if r['uom_id']}
        prg_id = {r['prg_id'] for r in results if r['prg_id']}
        q_ids = {r['quality_id'] for r in results if r['quality_id']}
        s_ids = {r['style_id'] for r in results if r['style_id']}
        c_ids = {r['color_id'] for r in results if r['color_id']}
        i_ids = {r['item_id'] for r in results if r['item_id']}
        acc_size = {r['acc_size_id'] for r in results if r['acc_size_id']}

        # Parse all these sets to handle comma-separated strings and convert to int
        acc_quality_id = parse_ids(acc_quality_id)
        group_id = parse_ids(group_id)
        uom_id = parse_ids(uom_id)
        prg_id = parse_ids(prg_id)
        q_ids = parse_ids(q_ids)
        s_ids = parse_ids(s_ids)
        c_ids = parse_ids(c_ids)
        i_ids = parse_ids(i_ids)
        acc_size = parse_ids(acc_size)

        # Fetch color mappings carefully, parsing color_id strings if needed
        color_mappings = sub_size_table.objects.filter(item_id__in=i_ids).values('item_id', 'color_id')

        item_color_map = defaultdict(list)
        for entry in color_mappings: 
            color_id = entry['color_id']
            if isinstance(color_id, str) and ',' in color_id:
                parsed = [int(cid.strip()) for cid in color_id.split(',') if cid.strip().isdigit()]
            else:
                parsed = [int(color_id)] if str(color_id).isdigit() else []
            item_color_map[entry['item_id']].extend(parsed)

        # Flatten color ids from item_color_map
        all_color_ids = set(cid for cids in item_color_map.values() for cid in cids)

        acc_items = sub_size_table.objects.filter(color_id__in=all_color_ids).values('color_id', 'item_id')
        acc_item_map = {entry['color_id']: entry['item_id'] for entry in acc_items}

        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_id).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_id).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_id).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=all_color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size).values_list('id', 'name'))

        enriched_data = []
        for row in results:
            if row['size_id'] in valid_size_ids:
                enriched_data.append({
                    **row,
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')  # fixed from size_id to acc_size_id
                })

        return JsonResponse({'data': enriched_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ```````````````````````` update list ``````````````````````````````````````````/


@csrf_exempt
def get_stiching_out_details_list(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    def parse_ids(ids):
        """

        Parses a set/list of IDs which might be integers or comma-separated strings,
        returning a set of integers.
        """

        parsed = set()
        for i in ids:
            if isinstance(i, str) and ',' in i:
                parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
            else:
                if str(i).isdigit():
                    parsed.add(int(i))
        return parsed
    
# SELECT  
            #         ac.tm_id AS prg_id,
            #         ac.size_id,
            #         ac.item_id,
            #         ac.acc_size_id AS acc_size_id, 
            #         ac.item_group_id AS group_id,
            #         ac.acc_quality_id AS acc_quality_id,
            #         gp.group_type AS item_type,
            #         mx.color_id,
            #         tm.quality_id, 
            #         tm.style_id,
            #         ac.quantity AS prg_qty,
            #         COALESCE(tx_total.total_st_qty, 0) AS st_qty,
            #         -- Balance quantity after subtracting the inward quantity
            #         COALESCE((tx_total.total_st_qty), 0) - COALESCE((si.quantity), 0) AS balance_qty,
            #         ac.product_pieces,
            #         ac.uom_id AS uom_id,
            #         ac.program_type
            #     FROM tx_accessory_program ac 
            #     LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
            #     LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
            #     LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

            #     -- Join to stitching outward to get matching size_ids and total st_qty
            #     LEFT JOIN (
            #         SELECT 
            #             tx.size_id, 
            #             tx.tm_id,
            #             SUM(tx.quantity) AS total_st_qty
            #         FROM tx_stiching_outward tx
            #         WHERE tx.status = 1
            #         AND tx.tm_id = %s
            #         AND tx.quality_id = %s
            #         AND tx.style_id = %s
            #         GROUP BY tx.size_id, tx.tm_id
            #     ) AS tx_total ON tx_total.size_id = ac.size_id

            #     -- Join to stitching inward to get quantities that have already been processed
            #     LEFT JOIN tx_stiching_inward si ON si.outward_id = tx_total.tm_id 
            #                                     AND si.size_id = tx_total.size_id
            #                                     AND si.status = 1

            #     -- Exclude records that already exist in tx_stiching_inward
            #     WHERE tm.status = 1
            #     AND ac.quantity >0
            #     AND ac.status = 1
            #     AND tm.quality_id = %s
            #     AND tm.style_id = %s
            #     AND gp.group_type = 'Stiching'
            #     AND ac.size_id IN (
            #         SELECT DISTINCT size_id 
            #         FROM tx_stiching_outward  
            #         WHERE status = 1 
            #             AND tm_id = %s 
            #             AND quality_id = %s 
            #             AND style_id = %s 
            #     )
            #     GROUP BY  
            #         tm.quality_id,
            #         tm.style_id,
            #         ac.item_id,
            #         ac.size_id;
    try:
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id') 
        prg_id = request.POST.get('program_id')
        tm_id = request.POST.get('tm_id')

        print('st-id:', stiching_id, quality_id, style_id)

        if not all([stiching_id, quality_id, style_id,tm_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        with connection.cursor() as cursor:
            sql = """

            SELECT  
                ac.tm_id AS prg_id,
                ac.size_id,
                ac.item_id,
                ac.acc_size_id, 
                ac.item_group_id AS group_id,
                ac.acc_quality_id,
                gp.group_type AS item_type,
                mx.color_id,
                tm.quality_id, 
                tm.style_id,
                ac.quantity AS prg_qty,

                -- Total accessory outward quantity
                COALESCE(ao.total_accessory_qty, 0) AS accessory_out_qty,

                -- Total stitching outward quantity
                COALESCE(so.total_stitching_qty, 0) AS stitching_out_qty,

                -- Total inward quantity
                COALESCE(si.total_inward_qty, 0) AS inward_qty,

                -- Final balance qty calculation
                (COALESCE(ao.total_accessory_qty, 0) + COALESCE(so.total_stitching_qty, 0)) - COALESCE(si.total_inward_qty, 0) AS balance_qty,

                ac.product_pieces,
                ac.uom_id,
                ac.program_type

            FROM tx_accessory_program ac

            LEFT JOIN tm_accessory_program tm ON ac.tm_id = tm.id
            LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
            LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

            -- Accessory outward total
            LEFT JOIN (
                SELECT 
                    tx.size_id,
                    tx.tm_id,
                    SUM(tx.quantity) AS total_accessory_qty
                FROM tx_accessory_outward tx
                WHERE tx.status = 1
                AND tx.tm_id = %s
                AND tx.quality_id = %s
             
                
                GROUP BY tx.size_id, tx.tm_id
            ) AS ao ON ao.size_id = ac.size_id AND ao.tm_id = ac.tm_id

            -- Stitching outward total
            LEFT JOIN (
                SELECT 
                    tx.size_id,
                    tx.tm_id,
                    SUM(tx.quantity) AS total_stitching_qty
                FROM tx_stiching_outward tx
                WHERE tx.status = 1
                AND tx.tm_id = %s
                AND tx.quality_id = %s
                AND tx.style_id = %s
                GROUP BY tx.size_id, tx.tm_id
            ) AS so ON so.size_id = ac.size_id AND so.tm_id = ac.tm_id

            -- Inward quantities against outward
            LEFT JOIN (
                SELECT
                    si.size_id,
                    si.outward_id,
                    SUM(si.quantity) AS total_inward_qty
                FROM tx_stiching_inward si
                WHERE si.status = 1
                GROUP BY si.size_id, si.outward_id
            ) AS si ON si.size_id = ac.size_id AND si.outward_id = ac.tm_id

            WHERE tm.status = 1
            AND ac.quantity > 0
            AND ac.status = 1
            AND tm.quality_id = %s
            AND tm.style_id = %s
            AND gp.group_type = 'Stiching'
            AND ac.size_id IN (
                SELECT DISTINCT size_id 
                FROM tx_stiching_outward  
                WHERE status = 1 
                    AND tm_id = %s
                    AND quality_id = %s
                    AND style_id = %s
            )

            GROUP BY  
                tm.quality_id,
                tm.style_id,
                ac.item_id,
                ac.size_id;

               
            """ 

            # cursor.execute(sql, [
            #     prg_id,tm_id,quality_id,
            #     stiching_id, quality_id, style_id,  # For subquery join
            #     quality_id, style_id,               # For main WHERE filter
            #     stiching_id, quality_id, style_id   # For size_id IN ()
            # ])

            cursor.execute(sql, [
                # prg_id,          # (1) used as tm_id = %s (line 1)
                tm_id,           # (2) tx.tm_id = %s
                quality_id,      # (3) tx.quality_id = %s
                stiching_id,     # (4) tx.tm_id = %s
                quality_id,      # (5) tx.quality_id = %s
                style_id,        # (6) tx.style_id = %s
                quality_id,      # (7) tm.quality_id = %s
                style_id,        # (8) tm.style_id = %s
                stiching_id,     # (9) tm_id = %s (again in IN clause)
                quality_id,      # (10) quality_id = %s
                style_id         # (11) style_id = %s
            ])

            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Name Mapping & Validation ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        # Extract sets of IDs from query results
        acc_quality_id = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_id = {r['group_id'] for r in results if r['group_id']}
        uom_id = {r['uom_id'] for r in results if r['uom_id']}
        prg_id = {r['prg_id'] for r in results if r['prg_id']}
        q_ids = {r['quality_id'] for r in results if r['quality_id']}
        s_ids = {r['style_id'] for r in results if r['style_id']}
        c_ids = {r['color_id'] for r in results if r['color_id']}
        i_ids = {r['item_id'] for r in results if r['item_id']}
        acc_size = {r['acc_size_id'] for r in results if r['acc_size_id']}

        # Parse all these sets to handle comma-separated strings and convert to int
        acc_quality_id = parse_ids(acc_quality_id)
        group_id = parse_ids(group_id)
        uom_id = parse_ids(uom_id)
        prg_id = parse_ids(prg_id)
        q_ids = parse_ids(q_ids)
        s_ids = parse_ids(s_ids)
        c_ids = parse_ids(c_ids)
        i_ids = parse_ids(i_ids)
        acc_size = parse_ids(acc_size)

        # Fetch color mappings carefully, parsing color_id strings if needed
        color_mappings = sub_size_table.objects.filter(item_id__in=i_ids).values('item_id', 'color_id')

        item_color_map = defaultdict(list)
        for entry in color_mappings: 
            color_id = entry['color_id']
            if isinstance(color_id, str) and ',' in color_id:
                parsed = [int(cid.strip()) for cid in color_id.split(',') if cid.strip().isdigit()]
            else:
                parsed = [int(color_id)] if str(color_id).isdigit() else []
            item_color_map[entry['item_id']].extend(parsed)

        # Flatten color ids from item_color_map
        all_color_ids = set(cid for cids in item_color_map.values() for cid in cids)

        acc_items = sub_size_table.objects.filter(color_id__in=all_color_ids).values('color_id', 'item_id')
        acc_item_map = {entry['color_id']: entry['item_id'] for entry in acc_items}


        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_id).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_id).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_id).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=all_color_ids).values_list('id', 'name'))
        item_map = dict(item_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size).values_list('id', 'name'))

        enriched_data = []
        for row in results:
            if row['size_id'] in valid_size_ids:
                enriched_data.append({
                    **row,
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['acc_size_id'], '')  # fixed from size_id to acc_size_id
                })

        return JsonResponse({'data': enriched_data})

    except Exception as e: 
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def get_stiching_out_details_13_9_2025(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        print('st-id:',stiching_id, quality_id, style_id)
        if not all([stiching_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        with connection.cursor() as cursor:
            sql = """
               SELECT  
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.item_group_id AS group_id,
                    ac.acc_quality_id AS acc_quality_id,
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id, 
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    -- Balance quantity after subtracting the inward quantity
                    COALESCE((tx_total.total_st_qty), 0) - COALESCE((si.quantity), 0) AS balance_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = tm.id
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                -- Join to stitching outward to get matching size_ids and total st_qty
                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        tx.tm_id,
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id, tx.tm_id
                ) AS tx_total ON tx_total.size_id = ac.size_id

                -- Join to stitching inward to get quantities that have already been processed
                LEFT JOIN tx_stiching_inward si ON si.outward_id = tx_total.tm_id 
                                                AND si.size_id = tx_total.size_id
                                                AND si.status = 1

                -- Exclude records that already exist in tx_stiching_inward
                WHERE tm.status = 1
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward  
                    WHERE status = 1 
                        AND tm_id = %s 
                        AND quality_id = %s 
                        AND style_id = %s 
                )
                

                GROUP BY  
                    tm.quality_id,
                    tm.style_id,
                    ac.size_id; 

            """ 
            cursor.execute(sql, [
                stiching_id, quality_id, style_id,  # For subquery join
                quality_id, style_id,               # For main WHERE filter
                stiching_id, quality_id, style_id   # For size_id IN ()
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Name Mapping & Validation ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        acc_quality_id = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_id = {r['group_id'] for r in results if r['group_id']}
        uom_id = {r['uom_id'] for r in results if r['uom_id']}
        prg_id = {r['prg_id'] for r in results if r['prg_id']}
        q_ids = {r['quality_id'] for r in results if r['quality_id']}
        s_ids = {r['style_id'] for r in results if r['style_id']}
        c_ids = {r['color_id'] for r in results if r['color_id']}
        i_ids = {r['item_id'] for r in results if r['item_id']}
        acc_size = {r['acc_size_id'] for r in results if r['acc_size_id']}


        # acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
        color_mappings = sub_size_table.objects.filter(item_id__in=i_ids).values('item_id', 'color_id')

        item_color_map = defaultdict(list)
        for entry in color_mappings: 
            color_id = entry['color_id']
            if isinstance(color_id, str) and ',' in color_id:
                parsed = [int(cid.strip()) for cid in color_id.split(',') if cid.strip().isdigit()]
            else:
                parsed = [int(color_id)] if str(color_id).isdigit() else []
            item_color_map[entry['item_id']].extend(parsed)

        acc_items = sub_size_table.objects.filter(color_id__in=set(
            cid for cids in item_color_map.values() for cid in cids
        )).values('color_id', 'item_id')
        acc_item_map = {entry['color_id']: entry['item_id'] for entry in acc_items}



        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_id).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_id).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_id).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_id).values_list('id', 'name'))
        
        # color_name = color_table.objects.filter(id=color_id).values_list('name', flat=True).first() or ''
        acc_item_id = acc_item_map.get(color_id, 0)
        

        item_map = dict(item_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
       
        # Ou
        # acc = sub_accessory_program_table.objects.filter(status=1,tm_id=prg_id,size_id=size_id)
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size).values_list('id', 'name'))


        enriched_data = []
        for row in results:
            if row['size_id'] in valid_size_ids:
                enriched_data.append({
                    **row,
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['size_id'], '')  

                })

        return JsonResponse({'data': enriched_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

 





@csrf_exempt
def get_stiching_out_details_bk_5_8_2025(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        stiching_id = request.POST.get('stiching_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not all([stiching_id, quality_id, style_id]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    ac.tm_id AS prg_id,
                    ac.size_id,
                    ac.item_id,
                    ac.item_group_id AS group_id,
                    ac.acc_size_id AS acc_size_id, 
                    ac.acc_quality_id AS acc_quality_id,  
                    gp.group_type AS item_type,
                    mx.color_id,
                    tm.quality_id,
                    tm.style_id,
                    ac.quantity AS prg_qty,
                    COALESCE(tx_total.total_st_qty, 0) AS st_qty,
                    ac.product_pieces,
                    ac.uom_id AS uom_id,
                    ac.program_type
                FROM tx_accessory_program ac
                LEFT JOIN tm_accessory_program tm ON ac.tm_id = tm.id
                LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
                LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

                -- Join to stitching outward to get matching size_ids and total st_qty

                LEFT JOIN (
                    SELECT 
                        tx.size_id, 
                        SUM(tx.quantity) AS total_st_qty
                    FROM tx_stiching_outward tx
                    WHERE tx.status = 1
                    AND tx.tm_id = %s
                    AND tx.quality_id = %s
                    AND tx.style_id = %s
                    GROUP BY tx.size_id
                ) AS tx_total ON tx_total.size_id = ac.size_id

                WHERE tm.status = 1
                AND ac.status = 1
                AND tm.quality_id = %s
                AND tm.style_id = %s
                AND gp.group_type = 'Stiching'
                AND ac.size_id IN (
                    SELECT DISTINCT size_id 
                    FROM tx_stiching_outward 
                    WHERE status = 1 
                        AND tm_id = %s   
                        AND quality_id = %s
                        AND style_id = %s
                )
                GROUP BY 
                    tm.quality_id,
                    tm.style_id
            """
            cursor.execute(sql, [
                stiching_id, quality_id, style_id,  # For subquery join
                quality_id, style_id,               # For main WHERE filter
                stiching_id, quality_id, style_id   # For size_id IN ()
            ])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # === Name Mapping & Validation ===
        valid_size_ids = set(
            child_stiching_outward_table.objects.filter(
                tm_id=stiching_id,
                quality_id=quality_id,
                style_id=style_id,
                status=1
            ).values_list('size_id', flat=True).distinct()
        )

        size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

        acc_quality_id = {r['acc_quality_id'] for r in results if r['acc_quality_id']}
        group_id = {r['group_id'] for r in results if r['group_id']}
        uom_id = {r['uom_id'] for r in results if r['uom_id']}
        prg_id = {r['prg_id'] for r in results if r['prg_id']}
        q_ids = {r['quality_id'] for r in results if r['quality_id']}
        s_ids = {r['style_id'] for r in results if r['style_id']}
        c_ids = {r['color_id'] for r in results if r['color_id']}
        i_ids = {r['item_id'] for r in results if r['item_id']}
        acc_size = {r['acc_size_id'] for r in results if r['acc_size_id']}


        # acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
        color_mappings = sub_size_table.objects.filter(item_id__in=i_ids).values('item_id', 'color_id')

        item_color_map = defaultdict(list)
        for entry in color_mappings: 
            color_id = entry['color_id']
            if isinstance(color_id, str) and ',' in color_id:
                parsed = [int(cid.strip()) for cid in color_id.split(',') if cid.strip().isdigit()]
            else:
                parsed = [int(color_id)] if str(color_id).isdigit() else []
            item_color_map[entry['item_id']].extend(parsed)

        acc_items = sub_size_table.objects.filter(color_id__in=set(
            cid for cids in item_color_map.values() for cid in cids
        )).values('color_id', 'item_id')
        acc_item_map = {entry['color_id']: entry['item_id'] for entry in acc_items}



        acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_id).values_list('id', 'name'))
        group_map = dict(item_group_table.objects.filter(id__in=group_id).values_list('id', 'name'))
        uom_map = dict(uom_table.objects.filter(id__in=uom_id).values_list('id', 'name'))
        quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
        style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
        color_map = dict(color_table.objects.filter(id__in=color_id).values_list('id', 'name'))
        
        # color_name = color_table.objects.filter(id=color_id).values_list('name', flat=True).first() or ''
        acc_item_id = acc_item_map.get(color_id, 0)
        

        item_map = dict(item_table.objects.filter(id__in=i_ids).values_list('id', 'name'))
       
        # Ou
        # acc = sub_accessory_program_table.objects.filter(status=1,tm_id=prg_id,size_id=size_id)
        acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size).values_list('id', 'name'))


        enriched_data = []
        for row in results:
            if row['size_id'] in valid_size_ids:
                enriched_data.append({
                    **row,
                    'quality': quality_map.get(row['quality_id'], ''),
                    'style': style_map.get(row['style_id'], ''),
                    'size': size_map.get(row['size_id'], ''),
                    'uom': uom_map.get(row['uom_id'], ''),
                    'color': color_map.get(row['color_id'], ''),
                    'item': item_map.get(row['item_id'], ''),
                    'group': group_map.get(row['group_id'], ''),
                    'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
                    'acc_size': acc_size_map.get(row['size_id'], '')  

                })

        return JsonResponse({'data': enriched_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)







# ````````````````````` add function `````````````````````````



@csrf_exempt
def insert_accessory_outward(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    user_id = request.session.get('user_id')  
    company_id = request.session.get('company_id')

    try:
        supplier_id = request.POST.get('supplier_id')
        remarks = request.POST.get('remarks')
        po_list = request.POST.get('po_list', 0)

        outward_date = request.POST.get('outward_date')
        packing_outward_id = request.POST.get('packing_id',0)
 
        stiching_outward_id = request.POST.get('stiching_id',0)
        # sp_id = request.POST.get('sp_id',0)
        sp_id = int(request.POST.get('sp_id', 0) or 0)


        prd_type = request.POST.get('production_type','')
        print('type:',prd_type) 

        dyeing_out_id = request.POST.get('dyeing_outward_id',0) 
        # ✅ Parse chemical data
        chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 
        print('data:',chemical_data)
    
        # Validate material type (must be either 'yarn' or 'grey')   
        material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
        is_production = 1 if material_type == 'production' else 0
        is_dyeing = 1 if material_type == 'dyeing' else 0  
        is_direct =1 if material_type == 'direct' else 0

        # Ensure only one of them is set to 1 
        if is_production + is_dyeing  + is_direct != 1:
            return JsonResponse({'status': 'error', 'message': 'Select either Production or Dyeing !.'}, safe=False)

        # if sp_id > 1:
        #     is_sp=1
        # else:
        #     is_sp=0

        if sp_id > 1:
            is_sp = 1

        else:
            is_sp = 0



 
        # ✅ Generate inward number
        outward_no = generate_outward_no()

        # ✅ Create main inward record
        material_request = parent_accessory_outward_table.objects.create(
            outward_no=outward_no,
            outward_date=outward_date, 
            party_id=supplier_id, 
            production_type = prd_type or "Dyeing",  
            cfyear=2025,    
            po_id=po_list,  
            packing_outward_id = packing_outward_id or 0,
            stiching_outward_id = stiching_outward_id or 0,  
            is_sp = is_sp if is_sp else 0 , 
            sp_id = sp_id,
            is_direct = is_direct if is_direct else 0,
            dyeing_outward_id = dyeing_out_id or 0,
            is_production=is_production,
            is_dyeing=is_dyeing,
            company_id=company_id,
            total_quantity=Decimal('0.00'),
            total_wt=Decimal('0.00'),
            total_amount=Decimal('0.00'),
            remarks=remarks,
            created_by=user_id, 
            created_on=timezone.now() 
        )

        total_quantity = Decimal('0.00')
        total_amount = Decimal('0.00')
        total_wt = Decimal('0.00')

        # ✅ Loop over chemical items
        for chemical in chemical_data:
            item_group_id = chemical.get('item_group_id')
            item_id = chemical.get('item_id')
            quality_id = chemical.get('quality_id')
            size_id = chemical.get('size_id') 
            color_id = chemical.get('color_id')

            acc_size_id = chemical.get('acc_size_id')
            acc_quality_id = chemical.get('acc_quality_id')
            quality_id = chemical.get('quality_id')
            style_id = chemical.get('style_id')
            uom_id = chemical.get('uom_id')
           

            quantity = safe_decimal(chemical.get('quantity'))
            wt = safe_decimal(chemical.get('total_wt'))
            print('wt:',wt)
            rate = safe_decimal(chemical.get('rate'))
            amount = safe_decimal(chemical.get('amount'))

            # ✅ Create sub-inward record 
            child_accessory_outward_table.objects.create(

                tm_id=material_request.id,
                item_group_id=item_group_id,
                item_id=item_id,
                uom_id = uom_id,
                quality_id=quality_id,
                size_id=size_id, 
                acc_size_id = acc_size_id,
                acc_quality_id=acc_quality_id,
                style_id=style_id,
                color_id=color_id,
               
                po_id=po_list,     
                cfyear=2025, 
                company_id=company_id,
                party_id=supplier_id,
                # outward_id=chemical.get('outward_id'),  # one per row here
                quantity=quantity,
                wt=wt,
                rate=rate,
                amount=amount,
                created_by=user_id,
                created_on=timezone.now() 
            )

            total_quantity += quantity
            total_wt += wt
            total_amount += amount
            print('Running total_quantity:', total_quantity)
            print('Running gross_wt:', total_amount)
            print('Total wt:', total_wt)

        # ✅ Update totals 

        parent_accessory_outward_table.objects.filter(id=material_request.id).update(
            total_quantity=total_quantity,
            total_wt=total_wt,
            total_amount=total_amount
        )

        new_no = generate_outward_no()

        return JsonResponse({
            'status': 'success',
            'message': 'Outward added successfully.',
            'outward_no': new_no
        })

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong: {str(e)}'
        })



# `````````update acc outward ```````````````````


@csrf_exempt
def update_acc_outward(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    user_id = request.session.get('user_id')  
    company_id = request.session.get('company_id')

    try:
        tm_id = request.POST.get('tm_id')
        supplier_id = request.POST.get('supplier_id')
        remarks = request.POST.get('remarks')
        po_list = request.POST.get('po_list', 0) 

        outward_date = request.POST.get('outward_date')

        prd_type = request.POST.get('production_type','') 
        print('type:',prd_type)

        # ✅ Parse chemical data
        chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
        print('data:',chemical_data)

    
        parent_accessory_outward_table.objects.filter(id=tm_id).update(outward_date=outward_date)
 

        total_quantity = Decimal('0.00')
        total_amount = Decimal('0.00')
        total_wt = Decimal('0.00')

        # ✅ Loop over chemical items
        # for chemical in chemical_data:
        #     item_group_id = chemical.get('item_group_id')
        #     item_id = chemical.get('item_id')
        #     quality_id = chemical.get('quality_id')
        #     # size_id = chemical.get('size_id',0) 
        #     color_id = chemical.get('color_id')

        #     # Fix size_id handling
        #     size_id = chemical.get('size_id')
        #     if size_id in (None, 'null', ''):
        #         size_id = 0
        #     else:
        #         try:
        #             size_id = int(size_id)
        #         except (ValueError, TypeError):
        #             size_id = 0
          
        #     quantity = safe_decimal(chemical.get('quantity'))
        #     wt = safe_decimal(chemical.get('total_wt'))
        #     print('wt:',wt)
        #     rate = safe_decimal(chemical.get('rate')) 
        #     amount = safe_decimal(chemical.get('amount'))

        #     child_accessory_outward_table.objects.filter(tm_id=tm_id,status=1).update(status=0,is_active=0) 

        #     # ✅ Create sub-inward record 
        #     child_accessory_outward_table.objects.create(
        #         tm_id=tm_id,
        #         item_group_id=item_group_id,
        #         item_id=item_id,
        #         quality_id=quality_id,
        #         size_id=size_id, 
        #         color_id=color_id,
               
        #         po_id=po_list,     
        #         cfyear=2025, 
        #         company_id=company_id,
        #         party_id=supplier_id,
        #         # outward_id=chemical.get('outward_id'),  # one per row here
        #         quantity=quantity,
        #         wt=wt,
        #         rate=rate,
        #         amount=amount,
        #         created_by=user_id,
        #         created_on=timezone.now() 
        #     )

        #     total_quantity += quantity
        #     total_wt += wt
        #     total_amount += amount
        #     print('Running total_quantity:', total_quantity)
        #     print('Running gross_wt:', total_amount)
        #     print('Total wt:', total_wt)

        for chemical in chemical_data:
            item_group_id = chemical.get('item_group_id')
            item_id = chemical.get('item_id')
            quality_id = chemical.get('quality_id')
            
            # Fix size_id handling
            size_id = chemical.get('size_id')
            if size_id in (None, 'null', ''):
                size_id = 0
            else:
                try:
                    size_id = int(size_id)
                except (ValueError, TypeError):
                    size_id = 0

            color_id = chemical.get('color_id')

            quantity = safe_decimal(chemical.get('quantity'))
            wt = safe_decimal(chemical.get('total_wt'))
            print('wt:', wt)
            rate = safe_decimal(chemical.get('rate'))
            amount = safe_decimal(chemical.get('amount'))

            child_accessory_outward_table.objects.filter(tm_id=tm_id, status=1).update(status=0, is_active=0)

            child_accessory_outward_table.objects.create(
                tm_id=tm_id,
                item_group_id=item_group_id,
                item_id=item_id,
                quality_id=quality_id,
                size_id=size_id,
                color_id=color_id,
                po_id=po_list,
                cfyear=2025,
                company_id=company_id,
                party_id=supplier_id,
                quantity=quantity,
                wt=wt,
                rate=rate,
                amount=amount,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_quantity += quantity
            total_wt += wt
            total_amount += amount


        # ✅ Update totals 

        parent_accessory_outward_table.objects.filter(id=tm_id).update(
            total_quantity=total_quantity,
            total_wt=total_wt,
            total_amount=total_amount
        )

        new_no = generate_outward_no()

        return JsonResponse({
            'status': 'success',
            'message': 'Outward added successfully.',
            'outward_no': new_no
        })

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong: {str(e)}'
        })




# ```````````````````````````````` listing ````````````````````````

def accessory_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(parent_accessory_outward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="acc_inward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="accessory_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="accessory_out_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'outward_date': item['outward_date'] if item['outward_date'] else'-', 
            'outward_no': item['outward_no'] if item['outward_no'] else'-', 
            'po_number':  getPONumberById(parent_accessory_po_table, item['po_id'] ), 
            'party_id':getSupplier(party_table, item['party_id'] ),   
            'total_wt': item['total_wt'] if item['total_wt'] else'-', 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-',  
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 



@csrf_exempt
def accessory_out_print(request): 
    outward_id = request.GET.get('k')
    if not outward_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(outward_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    delivery_data = parent_accessory_outward_table.objects.filter(status=1, id=order_id).first()
    outward = parent_accessory_outward_table.objects.filter(id=order_id, status=1).values(
        'id', 'outward_no', 'outward_date','production_type','party_id','packing_outward_id','stiching_outward_id','sp_id','total_quantity',
        'is_dyeing','is_direct','is_production',
    )

    party_name = get_object_or_404(party_table, id=delivery_data.party_id)
    gstin = party_name.gstin
    mobile = party_name.mobile

    # # Initialize
    delivery_details = [] 
    # dias = set() 
    total_quantity = 0
    # total_out_wt = 0

    delivery_entries_raw = child_accessory_outward_table.objects.filter(
        tm_id=order_id
    ).values('party_id', 'item_group_id','item_id','quality_id',
             'acc_size_id','size_id','acc_quality_id','quality_id','style_id','uom_id','quantity')


    if delivery_entries_raw:
        party_ids = [entry['party_id'] for entry in delivery_entries_raw]
        parties = party_table.objects.filter(id__in=party_ids).values('id', 'name', 'gstin', 'mobile')
        party_map = {p['id']: p for p in parties}

        delivery_entries = [
            { 
                'party_name': party_map.get(entry['party_id'], {}).get('name', 'Unknown'),
                'gstin': party_map.get(entry['party_id'], {}).get('gstin', 'Unknown'),
                'mobile': party_map.get(entry['party_id'], {}).get('mobile', 'Unknown'),
                # 'remarks': entry['remarks']
            } for entry in delivery_entries_raw
        ]
    else: 
        delivery_entries = []


    for out in outward:

        previous_outwards = parent_accessory_outward_table.objects.filter(
            # dyeing_program_id=out['dyeing_program_id'],
              status=1, id__lt=out['id']
        ).values_list('total_quantity', flat=True) 

        pre_qty = sum(previous_outwards) if previous_outwards else '-'

        tx_yarn_entries = child_accessory_outward_table.objects.filter(
            tm_id=out['id'], status=1
        ).values('party_id', 'item_group_id','item_id','quality_id',
             'acc_size_id','size_id','acc_quality_id','quality_id','style_id','uom_id','quantity')
        g_qty = 0
        for tx_yarn in tx_yarn_entries:
            total_quantity += tx_yarn['quantity']

            # total_out_wt += tx_yarn['roll_wt']

            party = get_object_or_404(party_table, id=tx_yarn['party_id'])
            item_group = get_object_or_404(item_group_table, id=tx_yarn['item_group_id'])
            item = get_object_or_404(item_table, id=tx_yarn['item_id'])
            quality = get_object_or_404(quality_table, id=tx_yarn['quality_id'])
            style = get_object_or_404(style_table, id=tx_yarn['style_id'])
            acc_size = get_object_or_404(accessory_size_table, id=tx_yarn['acc_size_id']) 
            size = get_object_or_404(size_table, id=tx_yarn['size_id']) 
            uom = get_object_or_404(uom_table, id=tx_yarn['uom_id']) 
            acc_quality = get_object_or_404(accessory_quality_table, id=tx_yarn['acc_quality_id']) 
            # print('tx-color-data:',tx_yarn['color_id'])

            # fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
            # fabric_name = get_object_or_404(fabric_table, id=fabric.fabric_id).name

            g_qty += tx_yarn['quantity']

            # g_qty = sum(tx_yarn['gross_wt'])

            print('g-wt:',g_qty)
            
            delivery_details.append({
                'party': party.name,
                'item_group': item_group.name, 
                'item': item.name,
                'size': size.name, 
                'acc_size': acc_size.name,
                'acc_quality': acc_quality.name,
                'quality': quality.name,
                'style': style.name or '-', 
                'uom': uom.name,
                'quantity': out['total_quantity'],
                'outward_no': out['outward_no'],
                'outward_date': out['outward_date'],
                
            })
            print('delivery-details:',delivery_details)

    grant_total_quantity = sum(Decimal(item['quantity']) for item in delivery_details)

    remarks = delivery_data.remarks if delivery_data else ''
    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    # context = {
    #     'total_values': delivery_data,
    #     'gstin': gstin, 
    #     'mobile': mobile,
    #     'deilvery_details':delivery_details,
    #     'image_url': image_url,
    #     'remarks': remarks,
    #     'delivery_entries': delivery_entries,
    #     'delivery_data': delivery_data,
    #     'party_name': party_name,
    #     'total_quantity': total_quantity,
    #     'company': company_table.objects.filter(status=1).first(),
    # }

    context = {
        'total_values': delivery_data,
        'gstin': gstin, 
        'mobile': mobile,
        'delivery_details': delivery_details,  # ✅ Fixed here
        'image_url': image_url,
        'remarks': remarks,
        'delivery_entries': delivery_entries,
        'delivery_data': delivery_data,
        'party_name': party_name,
        'total_quantity': grant_total_quantity,
        'company': company_table.objects.filter(status=1).first(),
    }



 
    return render(request, 'outward/accessory_outward_print.html', context)




 

def acc_inward_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'inward/inward_detail_update.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()  
            print('ids:',decoded_id)

        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'inward/inward_detail_update.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer 
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_accessory_inward_table.objects.filter(tm_id=material_id)
       
        # Fetch the parent stock instance
        parent_stock_instance = parent_accessory_inward_table.objects.filter(id=material_id).first()
        print('parent:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'inward/inward_detail_update.html', {'error_message': 'Parent stock not found.'})

       
        # Fetch active products and UOM
        item_group = item_group_table.objects.filter(status=1)
        item = item_table.objects.filter(status=1)
        # supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(
            Q(is_trader=1) | Q(is_supplier=1),
            status=1
        )  
        print('item:',party) 

        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'item_group': item_group,
            'item':item,
            'party': party,
            'supplier': party
        }
        print('cntexrt:',context)
        return render(request, 'inward/inward_detail_update.html', context)

    except Exception as e:
        return render(request, 'inward/inward_detail_update.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



def accessory_outward_report(request):
    company_id = request.session['company_id']
    print('company_id:',company_id) 

    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    print('party:',party)

    # yarn_count = request.POST.get('yarn_count', '')  
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Match if either created_on or updated_on falls in range
            date_filter = Q(outward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })
    
    if party:
            query &= Q(party_id=party)
  
  
    # Apply filters
    # queryset = parent_accessory_outward_table.objects.filter(status=1)
    queryset = parent_accessory_outward_table.objects.filter(query,status=1)
    data = list(queryset.order_by('-id').values())

    # data = list(parent_accessory_outward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="acc_outward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="accessory_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="accessory_outward_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'outward_date': item['outward_date'] if item['outward_date'] else'-', 
            'outward_no': item['outward_no'] if item['outward_no'] else'-', 
            'po_number':  getPONumberById(parent_accessory_po_table, item['po_id'] ),
            'packing_no':  getPONumberById(parent_packing_outward_table, item['packing_outward_id'] ), 
            'stiching_no':  getPONumberById(parent_stiching_outward_table, item['stiching_outward_id'] ), 
            'production_type': item['production_type'],

            'party':getSupplier(party_table, item['party_id'] ),   
            'total_wt': item['total_wt'] if item['total_wt'] else'-',   
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data) 
    ]
    return JsonResponse({'data': formatted}) 
  



def delete_accessory_outward(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            parent_accessory_outward_table.objects.filter(id=data_id).update(status=0,is_active=0)

            child_accessory_outward_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except parent_accessory_outward_table  & child_accessory_outward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})



def edit_acc_outward(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'outward/acc_outward_update.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()  
            print('ids:',decoded_id)

        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'outward/acc_outward_update.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer 
        material_id = int(decoded_id) 
 
        # Fetch the material instance using 'tm_id'
        material_instance = child_accessory_outward_table.objects.filter(tm_id=material_id)
       
        # Fetch the parent stock instance
        parent_stock_instance = parent_accessory_outward_table.objects.filter(id=material_id).first()
        print('parent:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'outward/acc_outward_update.html', {'error_message': 'Parent stock not found.'})


       
        # Fetch active products and UOM
        item_group = item_group_table.objects.filter(status=1)
        item = item_table.objects.filter(status=1)
        # supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(
            # Q(is_trader=1) | Q(is_supplier=1),
            status=1
        )  
        print('item:',party)
        uom = uom_table.objects.filter(status=1) 
        size = size_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'item_group': item_group,
            'item':item,
            'party': party,
            'supplier': party,
            'size':size,
            'uom':uom,
            'quality':quality,
            'style':style 
        }
        print('cntexrt:',context)
        return render(request, 'outward/acc_outward_update.html', context)

    except Exception as e:
        return render(request, 'outward/acc_outward_update.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.db.models import Sum


# @csrf_exempt
# def get_dyeing_out_details_list(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     try:
#         tm_id = request.POST.get('tm_id')
#         party_id = request.POST.get('party_id')

#         if not tm_id or not party_id:
#             return JsonResponse({"error": "Missing required parameters"}, status=400)

#         child_data = child_accessory_outward_table.objects.filter(status=1,tm_id=tm_id,party_id=party_id)
#         print('sub-datas:',child_data)
#         with connection.cursor() as cursor:
#             sql = """
#                 SELECT
#                     tx.item_id, 
#                     prd.name as item,
#                     tx.size_id,              
#                     sz.name as size_name,  
#                     tx.acc_size_id,
#                     ac.name as acc_size_name,
#                     tx.item_group_id AS group_id,
#                     grp.name as group_name, 
   
#                     tx.acc_quality_id AS acc_quality_id,
                
#                     tx.color_id, 
#                     clr.name as color, 
#                     tx.quality_id,  
#                     qt.name as quality,
#                     tx.style_id,   
#                     st.name as style,
#                     tx.uom_id AS uom_id, 
#                     um.name as uom,
#                     1 AS prg_qty,
#                     1 AS product_pieces,

#                     SUM(CASE WHEN tma.id = %s THEN tx.quantity ELSE 0 END) AS current_outward_qty,
#                     SUM(CASE WHEN tma.id != %s THEN tx.quantity ELSE 0 END) AS other_outward_qty 
#                 FROM tx_accessory_outward tx 
#                 JOIN tm_accessory_outward tma ON tma.id = tx.tm_id
#                 join item prd on tx.item_id = prd.id AND prd.status=1
#                 join size sz on tx.size_id = sz.id AND sz.status=1
#                 join uom um on tx.uom_id = um.id AND um.status=1
#                 join item_group grp on tx.item_group_id = grp.id AND grp.status=1
#                 join style st on tx.style_id = st.id AND st.status=1
#                 join quality qt on tx.quality_id = qt.id AND qt.status=1
#                 join accessory_size ac on tx.acc_size_id = ac.id AND ac.status=1
#                 join color clr on tx.color_id = clr.id AND clr.status=1

#                 WHERE tx.status = 1
#                   AND tma.status = 1 
#                   AND tma.party_id = %s
#                 GROUP BY tx.item_id;  
#             """
#             cursor.execute(sql, [tm_id, tm_id, party_id])
#             columns = [col[0] for col in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()] 

#         # Extract all item_ids to fetch item names and other lookups
#         item_ids = {row['item_id'] for row in results}

#         # Lookup maps
#         item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
#         # Add other lookup maps as needed (e.g., quality, group) if you want to enrich more fields

#         # Enrich results with item names
#         enriched_data = []
#         for row in results:
#             enriched_data.append({
#                 **row,
#                 'item_name': item_map.get(row['item_id'], '') 
#             })

#         return JsonResponse({'data': enriched_data}, safe=False)

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


# SELECT
#                 tx.item_id, prd.name AS item, tx.tm_id, tma.party_id, tx.status AS tx_status, tma.status AS tma_status,
#                 SUM(CASE WHEN tx.tm_id = %s THEN tx.quantity ELSE 0 END) AS current_outward_qty,
#                 SUM(CASE WHEN tx.tm_id != %s THEN tx.quantity ELSE 0 END) AS other_outward_qty
#             FROM tx_accessory_outward tx
#             LEFT JOIN tm_accessory_outward tma ON tma.id = tx.tm_id
#             WHERE (tma.party_id = %s OR tma.party_id IS NULL)
#             GROUP BY tx.item_id, prd.name, tx.tm_id, tma.party_id, tx.status, tma.status;
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
@csrf_exempt
def get_dyeing_out_details_list(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)
    try:
        tm_id = request.POST.get('tm_id')
        party_id = request.POST.get('party_id')
        if not tm_id or not party_id:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        with connection.cursor() as cursor:
            sql = """ 
                SELECT
                    tx.item_id,
                    prd.name AS item,
                    tx.size_id,
                    sz.name AS size,
                    tx.acc_size_id,
                    ac.name AS acc_size_name,
                    tx.item_group_id AS group_id,
                    grp.name AS group_name, 
                    tx.acc_quality_id, 
                    tx.color_id,
                    clr.name AS color,
                    tx.quality_id,
                    qt.name AS quality,
                    tx.style_id,
                    st.name AS style,
                    tx.uom_id,
                    um.name AS uom,
                    SUM(CASE WHEN tx.tm_id =%s THEN tx.quantity ELSE 0 END) AS current_outward_qty,
                    SUM(CASE WHEN tx.tm_id !=%s THEN tx.quantity ELSE 0 END) AS other_outward_qty,

                    tx.status AS tx_status,
                    tma.status AS tma_status,
                    tma.party_id AS tma_party_id

                FROM tx_accessory_outward tx
                LEFT JOIN tm_accessory_outward tma
                    ON tma.id = tx.tm_id
                LEFT JOIN item prd
                    ON prd.id = tx.item_id
                LEFT JOIN size sz
                    ON tx.size_id=sz.id
                --    ON sz.id = tx.size_id
                LEFT JOIN accessory_size ac
                    ON ac.id = tx.acc_size_id
                LEFT JOIN item_group grp
                    ON grp.id = tx.item_group_id
                LEFT JOIN quality qt
                    ON qt.id = tx.quality_id
                LEFT JOIN style st
                    ON st.id = tx.style_id
                LEFT JOIN uom um
                    ON tx.uom_id =  um.id
                LEFT JOIN color clr
                    ON clr.id = tx.color_id


                WHERE
                    tx.tm_id = %s  
                    AND (tma.party_id = %s OR tma.party_id IS NULL)
                    -- AND tx.status = 1
                    -- AND tma.status = 1

                GROUP BY
                    tx.item_id, prd.name, tx.size_id, sz.name,
                    tx.acc_size_id, ac.name, tx.item_group_id, grp.name,
                    tx.acc_quality_id, tx.color_id, clr.name, tx.quality_id, qt.name,
                    tx.style_id, st.name, tx.uom_id, um.name,
                    tx.status, tma.status, tma.party_id;

    
            
            """
            cursor.execute(sql, [tm_id, tm_id,tm_id, party_id])
            columns = [c[0] for c in cursor.description]
            rows = [dict(zip(columns, r)) for r in cursor.fetchall()]

        # If rows is empty, return debug info
        if not rows:
            return JsonResponse({
                "data": [],
                "debug_sql": sql,
                "params": {"tm_id": tm_id, "party_id": party_id},
            })

        return JsonResponse({"data": rows}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



     
# @csrf_exempt
# def get_dyeing_out_details_list(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     def parse_ids(ids):
#         parsed = set()
#         for i in ids:
#             if isinstance(i, str) and ',' in i:
#                 parsed.update(int(x.strip()) for x in i.split(',') if x.strip().isdigit())
#             else:
#                 if str(i).isdigit():
#                     parsed.add(int(i))
#         return parsed

#     try:
#         # === Step 0: Parse POST inputs ===
#         tm_id = request.POST.get('tm_id')
#         party_id = request.POST.get('party_id')
  
#         if not all([tm_id, party_id]):
#             return JsonResponse({"error": "Missing required parameters"}, status=400)

#         # === Step 1: Run raw SQL to get accessory program data ===
#         with connection.cursor() as cursor:
#             sql = """
#             SELECT  
                # ac.tm_id AS prg_id,
                # ac.size_id, 
                # ac.item_id,
                # ac.acc_size_id AS acc_size_id, 
                # ac.item_group_id AS group_id,
                # ac.acc_quality_id AS acc_quality_id,
                # gp.group_type AS item_type,
                # mx.color_id,
                # tm.quality_id, 
                # tm.style_id,
                # ac.uom_id AS uom_id, 
                # ac.quantity AS prg_qty,
                # ac.product_pieces,
#                 COALESCE(tx_total_stiching.total_st_qty, 0) AS st_qty,
#                 COALESCE(tx_total_accessory.total_st_qty, 0) AS already_rec_qty, 
#                 ( COALESCE(tx_total_stiching.total_st_qty,0) - COALESCE(tx_total_accessory.total_st_qty, 0)) AS balance_qty,
                
#                 ac.program_type
#                 FROM tx_accessory_program ac 
#                 LEFT JOIN tm_accessory_program tm ON ac.tm_id = %s
#                 LEFT JOIN item_group gp ON ac.item_group_id = gp.id AND gp.status = 1
#                 LEFT JOIN mx_acc_item_size mx ON ac.item_id = mx.item_id AND mx.status = 1

#                 LEFT JOIN ( 
#                 SELECT 
#                     tx.size_id,  
#                     tx.tm_id,
#                     SUM(tx.quantity) AS total_st_qty 
#                 FROM tx_stiching_outward tx
#                 WHERE tx.status = 1
#                 AND tx.tm_id = %s
#                 AND tx.quality_id = %s
#                 AND tx.style_id = %s
#                 --  GROUP BY tx.size_id, tx.tm_id 
#                 GROUP BY tx.tm_id
#                 ) AS tx_total_stiching ON tx_total_stiching.size_id = ac.size_id

#                 LEFT JOIN (
#                 SELECT  
#                     tx.item_id,
#                     tx.item_group_id,
#                     SUM(tx.quantity) AS total_st_qty
#                 FROM tm_accessory_outward tma
#                 JOIN tx_accessory_outward tx ON tma.id = tx.tm_id 
#                 WHERE tx.status = 1 AND tma.stiching_outward_id = %s AND tma.id=%s AND tma.status=1 

#                 GROUP BY tx.item_id
#                 ) AS tx_total_accessory ON tx_total_accessory.item_id = ac.item_id

#                 WHERE tm.status = 1
#                 AND ac.quantity > 0
#                 AND ac.status = 1
#                 AND tm.quality_id = %s
#                 AND tm.style_id = %s
#                 AND ac.size_id IN (
#                 SELECT DISTINCT size_id 
#                 FROM tx_stiching_outward  
#                 WHERE status = 1 
#                     AND tm_id = %s
#                     AND quality_id = %s
#                     AND style_id = %s
#                 )
#                 GROUP BY
#                             tm.quality_id,  
#                         tm.style_id, 
#                         ac.item_id, 
#                         ac.tm_id, 
#                         ac.item_group_id, 
#                         ac.acc_quality_id, 
#                         gp.group_type, 
                        
#                     --  ac.size_id, 
#                     --  ac.acc_size_id,
#                     --   mx.color_id,
#                     --   ac.quantity, 
#                     --    tx_total_stiching.total_st_qty, 
#                     --   tx_total_accessory.total_st_qty,  -- Add here in group by if needed
#                     --   ac.product_pieces, 
#                     --   ac.uom_id, 
                    
#                         ac.program_type;
                    

#             """
#             cursor.execute(sql, [
#                 prg_id,
#                 stiching_id, quality_id, style_id,
#                 stiching_id,tm_id,
#                 quality_id, style_id,
#                 stiching_id, quality_id, style_id
#             ])
#             columns = [col[0] for col in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]

#         # === Step 2: Lookups ===
#         valid_size_ids = set(
#             child_stiching_outward_table.objects.filter(
#                 tm_id=stiching_id,
#                 quality_id=quality_id,
#                 style_id=style_id,
#                 status=1
#             ).values_list('size_id', flat=True)
#         )

#         size_map = dict(size_table.objects.filter(id__in=valid_size_ids).values_list('id', 'name'))

#         acc_quality_ids = parse_ids({r['acc_quality_id'] for r in results})
#         group_ids = parse_ids({r['group_id'] for r in results})
#         uom_ids = parse_ids({r['uom_id'] for r in results})
#         q_ids = parse_ids({r['quality_id'] for r in results})
#         s_ids = parse_ids({r['style_id'] for r in results})
#         item_ids = parse_ids({r['item_id'] for r in results})
#         acc_size_ids = parse_ids({r['acc_size_id'] for r in results})

#         color_ids = set()
#         for row in results:
#             raw_color = row.get('color_id')
#             if isinstance(raw_color, str):
#                 color_ids.update(int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit())
#             elif isinstance(raw_color, int):
#                 color_ids.add(raw_color)

#         # Lookup maps
#         acc_quality_map = dict(accessory_quality_table.objects.filter(id__in=acc_quality_ids).values_list('id', 'name'))
#         group_map = dict(item_group_table.objects.filter(id__in=group_ids).values_list('id', 'name'))
#         uom_map = dict(uom_table.objects.filter(id__in=uom_ids).values_list('id', 'name'))
#         quality_map = dict(quality_table.objects.filter(id__in=q_ids).values_list('id', 'name'))
#         style_map = dict(style_table.objects.filter(id__in=s_ids).values_list('id', 'name'))
#         color_map = dict(color_table.objects.filter(id__in=color_ids).values_list('id', 'name'))
#         item_map = dict(item_table.objects.filter(id__in=item_ids).values_list('id', 'name'))
#         acc_size_map = dict(accessory_size_table.objects.filter(id__in=acc_size_ids).values_list('id', 'name'))

#         # === Step 3: Enrich data ===
#         enriched_data = []
#         for row in results:
#             if row['size_id'] not in valid_size_ids:
#                 continue

#             raw_color = row.get('color_id')
#             program_type = row.get('program_type')

#             if program_type == 'COLOR' and isinstance(raw_color, str) and ',' in raw_color:
#                 color_id_list = [int(cid.strip()) for cid in raw_color.split(',') if cid.strip().isdigit()]
#                 for cid in color_id_list:
#                     enriched_data.append({
#                         **row,
#                         'color_id': cid,
#                         'color': color_map.get(cid, ''),
#                         'quality': quality_map.get(row['quality_id'], ''),
#                         'style': style_map.get(row['style_id'], ''),
#                         'size': size_map.get(row['size_id'], ''),
#                         'uom': uom_map.get(row['uom_id'], ''),
#                         'item': item_map.get(row['item_id'], ''),
#                         'group': group_map.get(row['group_id'], ''),
#                         'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
#                         'acc_size': acc_size_map.get(row['acc_size_id'], '')
#                     })
#             else:
#                 cid = None
#                 if isinstance(raw_color, str) and raw_color.strip().isdigit():
#                     cid = int(raw_color)
#                 elif isinstance(raw_color, int):
#                     cid = raw_color

#                 enriched_data.append({
#                     **row,
#                     'color_id': cid,
#                     'color': color_map.get(cid, '') if cid else '',
#                     'quality': quality_map.get(row['quality_id'], ''),
#                     'style': style_map.get(row['style_id'], ''),
#                     'size': size_map.get(row['size_id'], ''),
#                     'uom': uom_map.get(row['uom_id'], ''),
#                     'item': item_map.get(row['item_id'], ''),
#                     'group': group_map.get(row['group_id'], ''),
#                     'acc_quality': acc_quality_map.get(row['acc_quality_id'], ''),
#                     'acc_size': acc_size_map.get(row['acc_size_id'], '')
#                 })



#     # === Step 4: Get quantity from child_stiching_outward_table ===
#         outward_data = list(child_stiching_outward_table.objects.filter(
#             tm_id=stiching_id,
#             quality_id=quality_id,  
#             style_id=style_id,
#             status=1
#         ).values('size_id', 'color_id').annotate(total_qty=Sum('quantity')))

#         # Map (size_id, color_id) to quantity
#         qty_map = {}
#         for rec in outward_data:
#             qty_map[(rec['size_id'], rec['color_id'])] = float(rec['total_qty'])

#         # Assign quantity to enriched_data
#         for row in enriched_data:
#             key = (row['size_id'], row.get('color_id'))
#             row['child_stiching_qty'] = qty_map.get(key, 0.0)

#         # 1. Build a better program_type mapping
#         program_type_map = {}
#         for row in enriched_data:
#             p_type = row['program_type']
#             size_id = row['size_id']
#             color_id = row.get('color_id')

#             if p_type == 'COLOR':
#                 key = (size_id, color_id)
#                 key_id = color_id
#                 key_name = row['color']
#             elif p_type == 'SIZE':
#                 key = (size_id, None)  # Note: force None for color_id in size-based
#                 key_id = size_id
#                 key_name = row['size']
#             else:
#                 continue

#             # Important: only set if not already set (to avoid overwriting)
#             if key not in program_type_map:
#                 program_type_map[key] = {
#                     'program_type': p_type,
#                     'key_id': key_id,
#                     'key_name': key_name
#                 }

#         # 2. Use mapping + qty_map to generate summary
#         summary = defaultdict(lambda: {
#             'program_type': '',
#             'key_id': None,
#             'key_name': '',
#             'total_qty': 0.0
#         })

#         for (size_id, color_id), qty in qty_map.items():
#             # First try with exact match (COLOR)
#             key = (size_id, color_id)
#             p_info = program_type_map.get(key)

#             # If not found, try with (size_id, None) — for SIZE
#             if not p_info:
#                 key = (size_id, None)
#                 p_info = program_type_map.get(key)

#             if not p_info:
#                 continue  # no valid mapping, skip

#             p_type = p_info['program_type']
#             key_id = p_info['key_id']
#             key_name = p_info['key_name']
#             summary_key = (p_type, key_id)

#             summary[summary_key]['program_type'] = p_type
#             summary[summary_key]['key_id'] = key_id
#             summary[summary_key]['key_name'] = key_name
#             summary[summary_key]['total_qty'] += qty

#         # print('end-data:',enriched_data)
#         # Final return
#         return JsonResponse({
#             'data': enriched_data,
#             'summary': list(summary.values())
#         }, safe=False)


#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


