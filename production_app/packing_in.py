from cairo import Status
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
from company.models import *
from employee.models import *

from grey_fabric.models import *

from django.utils.timezone import make_aware

from accessory.views import quality, quality_prg_size_list
from production_app.models import parent_packing_outward_table
import yarn 
from yarn.models import * 
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
import datetime

from datetime import datetime
from datetime import date
from django.utils import timezone

from django.db.models import Count


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse


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

from software_app.models import * 
from program_app.models import * 
from production_app.models import * 

from common.utils import *

from software_app.views import fabric_program, getItemNameById, getSupplier, is_ajax, knitting_program


# ``````````````````````````````````````````````   cutting entry ``````````````````````````````````````````


def packing_received(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_ironing=1)
        fabric_program = fabric_program_table.objects.filter(status=1) 
        delivery = parent_packing_outward_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        return render(request,'packing_received/packing_received.html',{'party':party,'fabric_program':fabric_program,'delivery':delivery,'quality':quality,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    



def generate_inward_num_series():
    last_purchase = parent_packing_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_no:
        match = re.search(r'P-(\d+)', last_purchase.inward_no)
        if match:
            next_num = int(match.group(1)) + 1
        else: 
            next_num = 1
    else:
        next_num = 1
 
    return f"P-{next_num:03d}"



def packing_received_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        # party = party_table.objects.filter(status=1,is_stiching=1) 
        party = party_table.objects.filter(status=1).filter(is_stiching=1) | party_table.objects.filter(status=1).filter(is_ironing=1)

        fabric_program = fabric_program_table.objects.filter(status=1) 

        inward_no = generate_inward_num_series()

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        # packing_outward = parent_packing_outward_table.objects.filter(status=1)
        # stitching_outward = parent_stiching_outward_table.objects.filter(status=1,is_packing=1)

        from itertools import chain

        packing_outward = parent_packing_outward_table.objects.filter(status=1).values(
            'id', 'outward_no', 'work_order_no', 'total_quantity'
        )
        for p in packing_outward:
            p['type'] = 'P'  # Packing 

        stitching_outward = parent_stiching_outward_table.objects.filter(status=1, is_packing=1).values(
            'id', 'outward_no', 'work_order_no', 'total_quantity'
        )
        for s in stitching_outward:
            s['type'] = 'SP'  # Stitching for Packing

        combined_outward = list(chain(packing_outward, stitching_outward))

        return render(request,'packing_received/add_packing_received.html',{'party':party,'fabric_program':fabric_program,'inward_no':inward_no,'color':color,
                                                                    "stitching":stitching_outward,'packing_outward':packing_outward,
                                                                  'combined_outward': combined_outward,
                                                                    'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")




from django.http import JsonResponse
from django.db.models import Q
from django.utils.timezone import make_aware, is_naive
from datetime import datetime, date


def packing_received_ajax_report(request):   
    company_id = request.session.get('company_id') 
    print('company_id:', company_id)

    query = Q()

    party = request.POST.get('party', '')
    outward = request.POST.get('outward', '')
    quality = request.POST.get('quality', '')
    style = request.POST.get('style', '') 
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '') 

    # Date filtering
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            if is_naive(start_date):
                start_date = make_aware(start_date)
            if is_naive(end_date):
                end_date = make_aware(end_date)

            date_filter = Q(inward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })
    
    if quality: 
        query &= Q(quality_id=quality)

    if outward: 
        query &= Q(outward_id=outward)   

    if party: 
        query &= Q(party_id=party)

    if style:
        query &= Q(style_id=style) 

    # Query filtered data
    queryset = parent_packing_inward_table.objects.filter(status=1).filter(query)
    child_data_map = child_packing_inward_table.objects.filter(
        tm_id__in=queryset.values_list('id', flat=True),
        status=1
    ).values('tm_id').annotate(
        total_box_pcs=Sum('box_pcs'),
        total_loose_pcs=Sum('loose_pcs'),
        total_seconds_pcs=Sum('seconds_pcs'),
        total_shortage_pcs=Sum('shortage_pcs')
    )

    # Map child data by tm_id
    child_data_dict = {
        item['tm_id']: item for item in child_data_map
    }


    # Pull only required fields (including delivery_from)
    data = list(queryset.order_by('-id').values(
        'id', 'inward_no', 'inward_date', 'work_order_no','party_id',
        'outward_id', 'quality_id', 'style_id', 'total_box','total_pcs','loose_pcs','seconds_pcs','shortage_pcs',
        'is_active', 'delivery_from'
    ))

    # Format results
    formatted = [
        {
            'action': (
                f'<button type="button" onclick="packing_received_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs">'
                f'<i class="feather icon-edit"></i></button> '
                f'<button type="button" onclick="packing_received_delete(\'{item["id"]}\')" class="btn btn-danger btn-xs">'
                f'<i class="feather icon-trash-2"></i></button> '
                f'<button type="button" onclick="packing_received_print(\'{item["id"]}\')" class="btn btn-success btn-xs">'
                f'<i class="feather icon-printer"></i></button>'
            ),
            'id': index + 1, 
            'inward_no': item.get('inward_no') or '-',
            'inward_date': item['inward_date'].strftime('%Y-%m-%d') if isinstance(item.get('inward_date'), date) else '-',
            'work_order_no': item.get('work_order_no') or '-', 
            'out_id': item.get('outward_id') or '-',
 
            'stiching_outward': (
                getStichingDeliveryNoById(parent_stiching_outward_table, item['outward_id'])
                if item.get('delivery_from') == 'STICHING' else '-'
            ),

            'outward': (
                getPackingDeliveryNoById(parent_packing_outward_table, item['outward_id'])
                if item.get('delivery_from') == 'PACKING' else '-'
            ),

            'party': getSupplier(party_table, item['party_id']),
            'quality': getSupplier(quality_table, item['quality_id']),
            'style': getSupplier(style_table, item['style_id']), 
            'total_box': item.get('total_box') or '-',
            'total_pcs': (
                (child_data_dict.get(item['id'], {}).get('total_box_pcs') or 0) +
                (child_data_dict.get(item['id'], {}).get('total_loose_pcs') or 0) +
                (child_data_dict.get(item['id'], {}).get('total_seconds_pcs') or 0) +
                (child_data_dict.get(item['id'], {}).get('total_shortage_pcs') or 0)
            ),
            # 'total_pcs': item.get('total_pcs') or '-',
            'total_loose_pcs': item.get('loose_pcs') or '-',
            'total_seconds_pcs': item.get('seconds_pcs') or '-',
            'total_shortage_pcs': item.get('shortage_pcs') or '-',
            'status': (
                '<span class="badge bg-success">active</span>'
                if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
            )
        }
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})
   
  
   
  


# def packing_received_ajax_report(request):   
#     company_id = request.session['company_id'] 
#     print('company_id:',company_id)
#     # user_type = request.session.get('user_type')
#     # has_access, error_message = check_user_access(user_type, "customer", "read") 

#     # if not has_access:  
#     #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

#     query = Q() 

#     outward = request.POST.get('outward', '')
#     quality = request.POST.get('quality', '')
#     style = request.POST.get('style', '') 
#     start_date = request.POST.get('from_date', '')
#     end_date = request.POST.get('to_date', '') 

#     if start_date and end_date:
#         try:
#             start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
#             end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

#             # Match if either created_on or updated_on falls in range 
#             date_filter = Q(inward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
#             query &= date_filter
#         except ValueError:
#             return JsonResponse({
#                 'data': [],
#                 'message': 'error',
#                 'error_message': 'Invalid date format. Use YYYY-MM-DD.'
#             })
    
#     if quality: 
#             query &= Q(quality_id=quality)

#     if outward: 
#         query &= Q(outward_id=outward)



#     if style:
#             query &= Q(style_id=style) 



#     # Apply filters
#     queryset = parent_packing_inward_table.objects.filter(status=1).filter(query)
#     data = list(queryset.order_by('-id').values())

#     # data = list(parent_packing_inward_table.objects.filter(status=1).order_by('-id').values())
 
#     # formatted = [ 
#     #     {
#     #         'action': '<button type="button" onclick="packing_received_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
#     #                     <button type="button" onclick="packing_received_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
#     #                     <button type="button" onclick="packing_received_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
#     #         'id': index + 1, 
#     #         'inward_no': item['inward_no'] if item['inward_no'] else'-', 
#     #         'inward_date': item['inward_date'] if item['inward_date'] else'-',  
#     #         'work_order_no': item['work_order_no'] if item['work_order_no'] else'-', 
#     #         'stiching_outward':getStichingDeliveryNoById(parent_packing_outward_table, item['outward_id'] ) or '-', 
#     #         'outward':getPackingDeliveryNoById(parent_packing_outward_table, item['outward_id'] ) or '-', 
#     #         'quality':getSupplier(quality_table, item['quality_id'] ),  
#     #         'style':getSupplier(style_table, item['style_id'] ),  
#     #         'total_box': item['total_box'] if item['total_box'] else'-', 
#     #         'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

#     #     } 
#     #     for index, item in enumerate(data)
#     # ]
#     formatted = [ 

#         {
#             'action': '<button type="button" onclick="packing_received_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
#                         <button type="button" onclick="packing_received_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
#                         <button type="button" onclick="packing_received_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'], item['id'], item['id']),
#             'id': index + 1, 
#             'inward_no': item.get('inward_no', '-') or '-', 
#             'inward_date': item.get('inward_date', '-') or '-',  
#             'work_order_no': item.get('work_order_no', '-') or '-', 
#             'out_id': item.get('outward_id', '-') or '-', 
            
#             # This is the fixed conditional logic
#             'stiching_outward': (
#                 getStichingDeliveryNoById(parent_packing_inward_table, item['outward_id']) 
#                 if item.get('delivery_from') == 'stiching' else '-'
#             ), 
             
#             'outward': (
#                 getPackingDeliveryNoById(parent_packing_inward_table, item['outward_id']) 
#                 if item.get('delivery_from') == 'packing' else '-'
#             ), 
            
#             'quality': getSupplier(quality_table, item['quality_id']),  
#             'style': getSupplier(style_table, item['style_id']),  
#             'total_box': item.get('total_box', '-') or '-', 
#             'status': '<span class="badge bg-success">active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>',
#         } 
#         for index, item in enumerate(data)
#         # print('queryset',item['outward_id'])

#     ]
#     print('formate-data:',formatted)



#     return JsonResponse({'data': formatted})  
  



from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def dictfetchall(cursor):
    """Convert cursor results to dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# @csrf_exempt
# def get_packing_delivery_list(request): 
#     prg_id = request.POST.get('prg_id') 

#     if not prg_id: 
#         return JsonResponse({'error': 'Program ID is required'}, status=400) 

#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT 
#                 inward.tm_id,
#                 inward.work_order_no,
#                 inward.quality_id,
#                 inward.style_id,
#                 inward.size_id,
#                 inward.total_in_qty AS already_received_qty,
#                 COALESCE(outward.total_out_qty, 0) AS already_out_qty,
#                 inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
#             FROM (
#                 SELECT 
#                     tx.tm_id,
#                     tx.work_order_no,
#                     tm.quality_id,
#                     tm.style_id,
#                     tx.size_id,
#                     tm.total_pcs AS total_in_qty
#                 FROM tx_packing_inward AS tx
#                 LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
#                 WHERE tx.status = 1 AND tx.tm_id = %s
#             ) AS inward
#             LEFT JOIN (
#                 SELECT 
#                     tp.tm_id,
#                     tp.size_id,
#                     SUM(tp.quantity) AS total_out_qty
#                 FROM tx_packing_outward AS tp
#                 WHERE tp.status = 1
#                 GROUP BY tp.tm_id, tp.size_id
#             ) AS outward
#             ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

#             UNION

#             SELECT 
#                 outward.tm_id,
#                 outward.work_order_no,
#                 outward.quality_id,
#                 outward.style_id,
#                 outward.size_id,
#                 0 AS already_received_qty,
#                 outward.total_out_qty AS already_out_qty,
#                 0 - outward.total_out_qty AS available_qty
#             FROM (
#                 SELECT 
#                     tp.tm_id,
#                     tp.work_order_no,
#                     tp.quality_id,
#                     tp.style_id,
#                     tp.size_id,
#                     SUM(tp.quantity) AS total_out_qty
#                 FROM tx_packing_outward AS tp
#                 WHERE tp.status = 1
#                 GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
#             ) AS outward
#             LEFT JOIN (
#                 SELECT 
#                     tx.tm_id,
#                     tx.size_id
#                 FROM tx_packing_inward AS tx
#                 WHERE tx.status = 1
#             ) AS inward
#             ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
#             WHERE inward.tm_id IS NULL
#         """, [prg_id])
#         result = dictfetchall(cursor)

#     return JsonResponse(result, safe=False)


from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt


from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt



# @csrf_exempt
# def get_packing_delivery_list(request): 
#     prg_id = request.POST.get('prg_id') 

#     if not prg_id: 
#         return JsonResponse({'error': 'Program ID is required'}, status=400) 

#     # 🔹 Step 1: Run SQL query (WITH + UNION + GROUP BY)
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             WITH packing_received_balance_sum AS (
#                 -- LEFT JOIN part
#                 SELECT 
#                     inward.tm_id,
#                     inward.work_order_no, 
#                     inward.quality_id,
#                     inward.style_id, 
#                     inward.size_id,
#                     inward.total_in_qty AS already_received_qty,
#                     COALESCE(outward.total_out_qty, 0) AS already_out_qty,
#                     inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
#                 FROM (
#                     SELECT 
#                         tx.tm_id,
#                         tx.work_order_no,
#                         tm.quality_id,
#                         tm.style_id,
#                         tx.size_id,
#                         tm.total_pcs AS total_in_qty
#                     FROM tx_packing_inward AS tx
#                     LEFT JOIN tm_packing_inward AS tm 
#                            ON tx.tm_id = tm.id
#                     WHERE tx.status = 1 AND tx.outward_id = %s
#                 ) AS inward
#                 LEFT JOIN (
#                     SELECT 
#                         tp.tm_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_packing_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.size_id
#                 ) AS outward
#                 ON inward.tm_id = outward.tm_id 
#                AND inward.size_id = outward.size_id

#                 UNION

#                 -- RIGHT JOIN part for unmatched outward records
#                 SELECT 
#                     outward.tm_id,
#                     outward.work_order_no,
#                     outward.quality_id,
#                     outward.style_id,
#                     outward.size_id,
#                     0 AS already_received_qty,
#                     outward.total_out_qty AS already_out_qty,
#                     (0 - outward.total_out_qty) AS available_qty
#                 FROM (
#                     SELECT 
#                         tp.tm_id,
#                         tp.work_order_no,
#                         tp.quality_id,
#                         tp.style_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_packing_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
#                 ) AS outward
#                 LEFT JOIN (
#                     SELECT 
#                         tx.tm_id,
#                         tx.size_id
#                     FROM tx_packing_inward AS tx
#                     WHERE tx.status = 1
#                 ) AS inward 
#                 ON outward.tm_id = inward.tm_id 
#                AND outward.size_id = inward.size_id
#                 WHERE inward.tm_id IS NULL
#             )
#             -- Final summarized result
#             SELECT  
#                 X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id,
#                 SUM(X.already_received_qty) AS already_received_qty,  
#                 SUM(X.already_out_qty) AS already_out_qty,
#                 SUM(X.already_out_qty)-SUM(X.already_received_qty) AS available_qty
#             FROM packing_received_balance_sum AS X
#             GROUP BY 
#               --  X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id
#         """, [prg_id])
#         result = dictfetchall(cursor)

#     if not result:
#         return JsonResponse([], safe=False)

#     # 🔹 Step 2: Get quality/style for per_box lookup
#     quality_id = result[0]['quality_id']    
#     style_id = result[0]['style_id']

#     quality_prg = quality_program_table.objects.filter(
#         status=1, quality_id=quality_id, style_id=style_id
#     ).first()

#     sub_quality_map = {}
#     if quality_prg:
#         sub_quality_prg = sub_quality_program_table.objects.filter(
#             status=1, tm_id=quality_prg.id
#         ).values('size_id', 'per_box')
#         sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#     # 🔹 Step 3: Build maps for size/color names
#     size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
#     color_map = {c.id: c.name for c in color_table.objects.all()}  # if color_id available

#     # 🔹 Step 4: Merge everything
#     data = []
#     for row in result:
#         data.append({
#             **row,
#             "size_name": size_map.get(row["size_id"], "Unknown"),
#             "color_id": row.get("color_id"),  # will be None if not available
#             "color_name": color_map.get(row.get("color_id"), "Unknown"),
#             "per_box": sub_quality_map.get(row["size_id"], 0)
#         })

#     return JsonResponse(data, safe=False)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection

# Updated Django View
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.db.models import Sum

# @csrf_exempt
# def get_packing_delivery_list(request):
#     if request.method == 'POST':
#         prg_ids_list = request.POST.getlist('prg_ids[]')

#         if not prg_ids_list:
#             return JsonResponse({'error': 'Program IDs are required'}, status=400)
        
#         prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

#         if not prg_ids:
#             return JsonResponse({'error': 'No valid Program IDs provided'}, status=400)

#         # Step 1: Check for quality and style consistency
#         first_item = parent_packing_outward_table.objects.filter(id=prg_ids[0]).first()
#         if not first_item:
#             return JsonResponse({'error': 'Invalid first program ID'}, status=400)

#         base_quality_id = first_item.quality_id
#         base_style_id = first_item.style_id

#         # Check all other selected items against the first one
#         for prg_id in prg_ids[1:]:
#             item = parent_packing_outward_table.objects.filter(id=prg_id).first()
#             if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
#                 # Mismatch detected, return a specific error flag
#                 return JsonResponse({
#                     'quality_mismatch': item.quality_id != base_quality_id if item else True,
#                     'style_mismatch': item.style_id != base_style_id if item else True,
#                     'error': 'Selected outwards have different Quality or Style, cannot load together.'
#                 }, status=200) # Use 200 for a successful response with a business logic error

#         # Step 2: If all items are consistent, proceed with your existing SQL logic
#         # You will need to wrap the IDs for the SQL query
#         in_clause = ','.join(['%s'] * len(prg_ids))
        
#         with connection.cursor() as cursor:
#             # Your existing long SQL query here...
#             sql_query = """
#                    WITH packing_received_balance_sum AS (
#                 SELECT 
#                     inward.tm_id,
#                     inward.work_order_no, 
#                     inward.quality_id,
#                     inward.style_id, 
#                     inward.size_id,
#                     inward.total_in_qty AS already_received_qty,
#                     COALESCE(outward.total_out_qty, 0) AS already_out_qty,
#                     inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
#                 FROM (
#                     SELECT 
#                         tx.tm_id,
#                         tx.work_order_no,
#                         tm.quality_id,
#                         tm.style_id,
#                         tx.size_id,
#                         tm.total_pcs AS total_in_qty
#                     FROM tx_packing_inward AS tx
#                     LEFT JOIN tm_packing_inward AS tm 
#                         ON tx.tm_id = tm.id
#                     WHERE tx.status = 1 AND tx.outward_id IN %s
#                 ) AS inward
#                 LEFT JOIN (
#                     SELECT 
#                         tp.tm_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_packing_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.size_id
#                 ) AS outward
#                 ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

#                 UNION

#                 SELECT 
#                     outward.tm_id,
#                     outward.work_order_no,
#                     outward.quality_id,
#                     outward.style_id,
#                     outward.size_id,
#                     0 AS already_received_qty,
#                     outward.total_out_qty AS already_out_qty,
#                     (0 - outward.total_out_qty) AS available_qty
#                 FROM (
#                     SELECT 
#                         tp.tm_id,
#                         tp.work_order_no,
#                         tp.quality_id,
#                         tp.style_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_packing_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
#                 ) AS outward
#                 LEFT JOIN (
#                     SELECT 
#                         tx.tm_id,
#                         tx.size_id
#                     FROM tx_packing_inward AS tx
#                     WHERE tx.status = 1
#                 ) AS inward 
#                 ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
#                 WHERE inward.tm_id IS NULL
#             )
#             SELECT  
#                 X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id,
#                 SUM(X.already_received_qty) AS already_received_qty,  
#                 SUM(X.already_out_qty) AS already_out_qty,
#                 SUM(X.already_out_qty) - SUM(X.already_received_qty) AS available_qty
#             FROM packing_received_balance_sum AS X
#             GROUP BY 
#                 X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id
#             """
#             cursor.execute(sql_query, prg_ids)
#             result = dictfetchall(cursor)

#         # The rest of your existing code for processing results
#         if not result:
#             return JsonResponse([], safe=False)

#         quality_prg = quality_program_table.objects.filter(
#             status=1, quality_id=base_quality_id, style_id=base_style_id
#         ).first()

#         sub_quality_map = {}
#         if quality_prg:
#             # ... (rest of your existing logic to get sub_quality_prg and total_out) ...
#             sub_quality_prg = sub_quality_program_table.objects.filter(
#                 status=1, tm_id=quality_prg.id
#             ).values('size_id', 'per_box')
#             sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#         size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
#         color_map = {c.id: c.name for c in color_table.objects.all()}

#         data = []
#         for row in result:
#             data.append({
#                 **row,
#                 "size_name": size_map.get(row["size_id"], "Unknown"),
#                 "color_id": row.get("color_id"),
#                 "color_name": color_map.get(row.get("color_id"), "Unknown"),
#                 "per_box": sub_quality_map.get(row["size_id"], 0)
#             })

#         # Add the quality and style info to the response
#         data_to_send = {
#             'quality': {'id': base_quality_id, 'name': quality_table.objects.get(pk=base_quality_id).name},
#             'style': {'id': base_style_id, 'name': style_table.objects.get(pk=base_style_id).name},
#             'sizes': data,
#             'quality_mismatch': False,
#             'style_mismatch': False,
#         }
        
#         return JsonResponse(data_to_send, safe=False)
    
# Django View: Corrected
# ======================
        # WITH packing_received_balance_sum AS (
                #     SELECT 
                #         inward.tm_id,
                #         inward.work_order_no, 
                #         inward.quality_id,
                #         inward.style_id, 
                #         inward.size_id,
                #         inward.total_in_qty AS already_received_qty,
                #         COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                #         inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
                #     FROM (
                #         SELECT 
                #             tx.tm_id,
                #             tx.work_order_no,
                #             tm.quality_id,
                #             tm.style_id,
                #             tx.size_id,
                #             tm.total_pcs AS total_in_qty
                #         FROM tx_packing_inward AS tx
                #         LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                #         WHERE tx.status = 1 AND tx.outward_id IN %s
                #     ) AS inward
                #     LEFT JOIN (
                #         SELECT 
                #             tp.tm_id,
                #             tp.size_id,
                #             SUM(tp.quantity) AS total_out_qty
                #         FROM tx_packing_outward AS tp
                #         WHERE tp.status = 1
                #         GROUP BY tp.tm_id, tp.size_id
                #     ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                #     UNION

                #     SELECT 
                #         outward.tm_id,
                #         outward.work_order_no,
                #         outward.quality_id,
                #         outward.style_id,
                #         outward.size_id,
                #         0 AS already_received_qty,
                #         outward.total_out_qty AS already_out_qty,
                #         (0 - outward.total_out_qty) AS available_qty
                #     FROM (
                #         SELECT 
                #             tp.tm_id,
                #             tp.work_order_no,
                #             tp.quality_id,
                #             tp.style_id,
                #             tp.size_id,
                #             SUM(tp.quantity) AS total_out_qty
                #         FROM tx_packing_outward AS tp
                #         WHERE tp.status = 1
                #         GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                #     ) AS outward
                #     LEFT JOIN (
                #         SELECT 
                #             tx.tm_id,
                #             tx.size_id
                #         FROM tx_packing_inward AS tx
                #         WHERE tx.status = 1
                #     ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                #     WHERE inward.tm_id IS NULL
                # )
                # SELECT 
                #     X.tm_id,
                #     X.work_order_no,
                #     X.quality_id,
                #     X.style_id,
                #     X.size_id,
                #     SUM(X.already_received_qty) AS already_received_qty, 
                #     SUM(X.already_out_qty) AS already_out_qty,
                #     SUM(X.available_qty) AS available_qty
                # FROM packing_received_balance_sum AS X
                # GROUP BY 
                #     X.tm_id,
                #     X.work_order_no,
                #     X.quality_id,
                #     X.style_id,
                #     X.size_id 

# @csrf_exempt
# def get_packing_delivery_list(request):
#     if request.method == 'POST':
#         # Correctly get the list of IDs from the POST data
#         prg_ids_list = request.POST.getlist('prg_id[]')

#         if not prg_ids_list:
#             return JsonResponse({
#                 'error_message': 'Program IDs are required'
#             }, status=400)
        
#         prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

#         if not prg_ids:
#             return JsonResponse({
#                 'error_message': 'No valid Program IDs provided'
#             }, status=400)

#         # Step 1: Check for quality and style consistency
#         first_item = parent_packing_outward_table.objects.filter(id=prg_ids[0]).first()
#         if not first_item:
#             return JsonResponse({
#                 'error_message': 'Invalid first program ID selected.'
#             }, status=400)
 
#         base_quality_id = first_item.quality_id
#         base_style_id = first_item.style_id

#         # Check all other selected items against the first one
#         for prg_id in prg_ids[1:]:
#             item = parent_packing_outward_table.objects.filter(id=prg_id).first()
#             if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
#                 # Mismatch detected, return a specific error flag with a 200 status
#                 return JsonResponse({
#                     'quality_mismatch': True, 
#                     'style_mismatch': True,
#                     # Corrected key from 'error' to 'error_message'
#                     'error_message': 'Selected outwards have different Quality or Style, cannot load together.'
#                 }, status=200)

#         # Step 2: If all items are consistent, proceed with your existing SQL logic
 
        
#             with connection.cursor() as cursor:
#             # Generate placeholders: (%s, %s, %s, ...)
#                 placeholders = ', '.join(['%s'] * len(prg_ids))

#                 sql_query = f"""
#                     WITH packing_received_balance_sum AS (
#                         SELECT 
#                             inward.tm_id,
#                             inward.work_order_no, 
#                             inward.quality_id,
#                             inward.style_id, 
#                             inward.size_id,
#                             inward.total_in_qty AS already_received_qty,
#                             COALESCE(outward.total_out_qty, 0) AS already_out_qty,
#                             COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
#                         FROM (
#                             SELECT 
#                                 tx.tm_id,
#                                 tx.work_order_no,
#                                 tm.quality_id,
#                                 tm.style_id,
#                                 tx.size_id,
#                                 tm.total_pcs AS total_in_qty
#                             FROM tx_packing_inward AS tx
#                             LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
#                             WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
#                         ) AS inward
#                         LEFT JOIN (
#                             SELECT 
#                                 tp.tm_id,
#                                 tp.size_id,
#                                 SUM(tp.quantity) AS total_out_qty
#                             FROM tx_packing_outward AS tp
#                             WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
#                             GROUP BY tp.tm_id, tp.size_id
#                         ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

#                         UNION

#                         SELECT 
#                             outward.tm_id,
#                             outward.work_order_no,
#                             outward.quality_id,
#                             outward.style_id,
#                             outward.size_id,
#                             0 AS already_received_qty,
#                             outward.total_out_qty AS already_out_qty,
#                             (outward.total_out_qty - 0) AS available_qty
#                         FROM (
#                             SELECT 
#                                 tp.tm_id,
#                                 tp.work_order_no,
#                                 tp.quality_id,
#                                 tp.style_id,
#                                 tp.size_id,
#                                 SUM(tp.quantity) AS total_out_qty
#                             FROM tx_packing_outward AS tp
#                             WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
#                             GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
#                         ) AS outward
#                         LEFT JOIN (
#                             SELECT 
#                                 tx.tm_id,
#                                 tx.size_id
#                             FROM tx_packing_inward AS tx
#                             WHERE tx.status = 1
#                         ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
#                         WHERE inward.tm_id IS NULL
#                     )
#                     SELECT 
#                         X.tm_id,
#                         X.work_order_no,
#                         X.quality_id,
#                         X.style_id,
#                         X.size_id,
#                         SUM(X.already_received_qty) AS already_received_qty, 
#                         SUM(X.already_out_qty) AS already_out_qty,
#                         SUM(X.available_qty) AS available_qty
#                     FROM packing_received_balance_sum AS X
#                     GROUP BY 
#                         X.tm_id,
#                         X.work_order_no,
#                         X.quality_id,
#                         X.style_id,
#                         X.size_id
#             """

#             # Since the query has 3 IN clauses, repeat the prg_ids 3 times
#             params = prg_ids * 3
#             cursor.execute(sql_query, params)
#             result = dictfetchall(cursor) 



#             # result = dictfetchall(cursor)

#         if not result:
#             return JsonResponse([], safe=False)

#         quality_prg = quality_program_table.objects.filter(
#             status=1, quality_id=base_quality_id, style_id=base_style_id
#         ).first()

#         sub_quality_map = {}
#         if quality_prg:
#             sub_quality_prg = sub_quality_program_table.objects.filter(
#                 status=1, tm_id=quality_prg.id
#             ).values('size_id', 'per_box')
#             sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#         size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
#         color_map = {c.id: c.name for c in color_table.objects.all()}

#         data = []
#         for row in result:
#             data.append({
#                 **row,
#                 "size_name": size_map.get(row["size_id"], "Unknown"),
#                 "color_id": row.get("color_id"),
#                 "color_name": color_map.get(row.get("color_id"), "Unknown"),
#                 "per_box": sub_quality_map.get(row["size_id"], 0)
#             })

#         data_to_send = {
#             'quality': {'id': base_quality_id, 'name': quality_table.objects.get(pk=base_quality_id).name},
#             'style': {'id': base_style_id, 'name': style_table.objects.get(pk=base_style_id).name},
#             'sizes': data,
#             'quality_mismatch': False,
#             'style_mismatch': False,
#         }
        
#         return JsonResponse(data_to_send, safe=False)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection



@csrf_exempt
def get_packing_delivery_list(request):
    if request.method == 'POST':
        prg_ids_list = request.POST.getlist('prg_id[]')

        if not prg_ids_list:
            return JsonResponse({'error_message': 'Program IDs are required'}, status=400)

        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

        if not prg_ids:
            return JsonResponse({'error_message': 'No valid Program IDs provided'}, status=400)

        # Step 1: Check for quality and style consistency
        first_item = parent_packing_outward_table.objects.filter(id=prg_ids[0]).first()
        if not first_item:
            return JsonResponse({'error_message': 'Invalid first program ID selected.'}, status=400)

        base_quality_id = first_item.quality_id
        base_style_id = first_item.style_id

        for prg_id in prg_ids[1:]:
            item = parent_packing_outward_table.objects.filter(id=prg_id).first()
            if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
                return JsonResponse({
                    'quality_mismatch': True,
                    'style_mismatch': True,
                    'error_message': 'Selected outwards have different Quality or Style, cannot load together.'
                }, status=200)

        # Step 2: Run SQL query
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(prg_ids))
            sql_query = f"""
                WITH packing_received_balance_sum AS (
                    SELECT 
                        inward.tm_id,
                        inward.work_order_no, 
                        inward.quality_id,
                        inward.style_id, 
                        inward.size_id,
                        inward.total_in_qty AS already_received_qty,
                        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                        COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
                    FROM (
                        SELECT 
                            tx.tm_id,
                            tx.work_order_no,
                            tm.quality_id,
                            tm.style_id,
                            tx.size_id,
                            (tx.box_pcs) + (tx.loose_pcs) + (tx.seconds_pcs)+ (tx.shortage_pcs) AS total_in_qty
                        FROM tx_packing_inward AS tx
                        LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                        WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
                    ) AS inward
                    LEFT JOIN (
                        SELECT 
                            tp.tm_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.size_id
                    ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                    UNION

                    SELECT 
                        outward.tm_id,
                        outward.work_order_no,
                        outward.quality_id,
                        outward.style_id,
                        outward.size_id,
                        0 AS already_received_qty,
                        outward.total_out_qty AS already_out_qty,
                        (outward.total_out_qty - 0) AS available_qty
                    FROM (
                        SELECT 
                            tp.tm_id,
                            tp.work_order_no,
                            tp.quality_id,
                            tp.style_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                    ) AS outward
                    LEFT JOIN (
                        SELECT 
                            tx.tm_id,
                            tx.size_id
                        FROM tx_packing_inward AS tx
                        WHERE tx.status = 1
                    ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                    WHERE inward.tm_id IS NULL
                )
                SELECT 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id,
                    SUM(X.already_received_qty) AS already_received_qty, 
                    SUM(X.already_out_qty) AS already_out_qty,
                    SUM(X.available_qty) AS available_qty
                FROM packing_received_balance_sum AS X
                GROUP BY 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id
            """
            params = prg_ids * 3
            cursor.execute(sql_query, params)
            result = dictfetchall(cursor)

        if not result:
            return JsonResponse({'message': 'No data found'}, safe=False)

        # Step 3: Additional lookups
        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=base_quality_id, style_id=base_style_id
        ).first()

        sub_quality_map = {}
        if quality_prg:
            sub_quality_prg = sub_quality_program_table.objects.filter(
                status=1, tm_id=quality_prg.id
            ).values('size_id', 'per_box')
            sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

        size_ids = [r['size_id'] for r in result]
        size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}
        color_map = {c.id: c.name for c in color_table.objects.all()}

        outward_qs = (
            child_packing_outward_table.objects
            .filter(tm_id__in=prg_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))
        )

        delivered_map = {
            (item['tm_id'], item['size_id']): item['total_qty'] or 0
            for item in outward_qs
        }


        # Step 1: Build tm_id to packing_id map
        tm_to_packing_id = {
            obj.id: obj.packing_id
            for obj in parent_lp_entry_table.objects.filter(packing_id__in=prg_ids,is_packing=1, status=1)
        }

        # Step 2: Get child entries
        parent_ids = list(tm_to_packing_id.keys())
        loose_pcs_value = (
            child_lp_entry_table.objects
            .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))  
        )
        print('lp-value:',loose_pcs_value)
        # Step 3: Build correct dictionary
        loose_pcs_qty = {}
        for item in loose_pcs_value:
            tm_id = item['tm_id']
            size_id = item['size_id']
            total_qty = item['total_qty'] or 0

            packing_id = tm_to_packing_id.get(tm_id)
            if packing_id:
                loose_pcs_qty[(packing_id, size_id)] = total_qty



        # Step 4: Build raw data
        raw_data = []
        for row in result:
            key = (row['tm_id'], row['size_id'])
            delivered_pcs = delivered_map.get(key, 0)
            loose_pcs_delivery = loose_pcs_qty.get(key, 0)
            print('raw key:', key, 'loose_pcs:', loose_pcs_qty.get(key, 0))

            raw_data.append({
                "size_id": row["size_id"],
                "size_name": size_map.get(row["size_id"], "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(row["size_id"], 0),
                "already_received_qty": row["already_received_qty"] or 0,
                "already_out_qty": row["already_out_qty"] or 0,
                "available_qty": (row["available_qty"] + loose_pcs_delivery) or 0,
                "delivered_pcs": delivered_pcs + loose_pcs_delivery,
                "loose_pcs_delivery":loose_pcs_delivery
            })
 
        # Step 5: Aggregate by size_id
        aggregated_data = {}
        for item in raw_data:
            size_id = item["size_id"]
            if size_id not in aggregated_data:
                aggregated_data[size_id] = {
                    "size_id": size_id,
                    "size_name": item["size_name"],
                    "color_id": item["color_id"],
                    "color_name": item["color_name"],
                    "per_box": item["per_box"],
                    "already_received_qty": 0,
                    "already_out_qty": 0,
                    "available_qty": 0,
                    "delivered_pcs": 0,
                    "loose_pcs_delivery":0
                }

            aggregated_data[size_id]["already_received_qty"] += item["already_received_qty"]
            aggregated_data[size_id]["already_out_qty"] += item["already_out_qty"]
            aggregated_data[size_id]["available_qty"] += item["available_qty"]
            aggregated_data[size_id]["delivered_pcs"] += item["delivered_pcs"]
            aggregated_data[size_id]["loose_pcs_delivery"] += item["loose_pcs_delivery"]

        # ✅ Filter out entries with available_qty = 0
        final_data = [
            data for data in aggregated_data.values()
            if data["available_qty"] > 0
        ]

        if not final_data:
            return JsonResponse({
                'quality_mismatch': False,
                'style_mismatch': False,
                'message': 'All selected outwards have zero available quantity.',
                'sizes': []
            }, safe=False)

        data_to_send = {
            'quality': {
                'id': base_quality_id,
                'name': quality_table.objects.get(pk=base_quality_id).name
            },
            'style': {
                'id': base_style_id,
                'name': style_table.objects.get(pk=base_style_id).name
            },
            'sizes': final_data,
            'quality_mismatch': False,
            'style_mismatch': False
        }

        return JsonResponse(data_to_send, safe=False)



@csrf_exempt
def get_packing_delivery_list_3_9(request):
    if request.method == 'POST':
        prg_ids_list = request.POST.getlist('prg_id[]')

        if not prg_ids_list:
            return JsonResponse({'error_message': 'Program IDs are required'}, status=400)

        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

        if not prg_ids:
            return JsonResponse({'error_message': 'No valid Program IDs provided'}, status=400)

        # Step 1: Check for quality and style consistency
        first_item = parent_packing_outward_table.objects.filter(id=prg_ids[0]).first()
        if not first_item:
            return JsonResponse({'error_message': 'Invalid first program ID selected.'}, status=400)

        base_quality_id = first_item.quality_id
        base_style_id = first_item.style_id

        for prg_id in prg_ids[1:]:
            item = parent_packing_outward_table.objects.filter(id=prg_id).first()
            if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
                return JsonResponse({
                    'quality_mismatch': True,
                    'style_mismatch': True,
                    'error_message': 'Selected outwards have different Quality or Style, cannot load together.'
                }, status=200)

        # Step 2: Run SQL query
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(prg_ids))
            sql_query = f"""
                WITH packing_received_balance_sum AS (
                    SELECT 
                        inward.tm_id,
                        inward.work_order_no, 
                        inward.quality_id,
                        inward.style_id, 
                        inward.size_id,
                        inward.total_in_qty AS already_received_qty,
                        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                        COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
                    FROM (
                        SELECT 
                            tx.tm_id,
                            tx.work_order_no,
                            tm.quality_id,
                            tm.style_id,
                            tx.size_id,
                            (tx.box_pcs) + (tx.loose_pcs) + (tx.seconds_pcs)+ (tx.shortage_pcs) AS total_in_qty
                        FROM tx_packing_inward AS tx
                        LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                        WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
                    ) AS inward
                    LEFT JOIN (
                        SELECT 
                            tp.tm_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.size_id
                    ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                    UNION

                    SELECT 
                        outward.tm_id,
                        outward.work_order_no,
                        outward.quality_id,
                        outward.style_id,
                        outward.size_id,
                        0 AS already_received_qty,
                        outward.total_out_qty AS already_out_qty,
                        (outward.total_out_qty - 0) AS available_qty
                    FROM (
                        SELECT 
                            tp.tm_id,
                            tp.work_order_no,
                            tp.quality_id,
                            tp.style_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                    ) AS outward
                    LEFT JOIN (
                        SELECT 
                            tx.tm_id,
                            tx.size_id
                        FROM tx_packing_inward AS tx
                        WHERE tx.status = 1
                    ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                    WHERE inward.tm_id IS NULL
                )
                SELECT 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id,
                    SUM(X.already_received_qty) AS already_received_qty, 
                    SUM(X.already_out_qty) AS already_out_qty,
                    SUM(X.available_qty) AS available_qty
                FROM packing_received_balance_sum AS X
                GROUP BY 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id
            """
            params = prg_ids * 3
            cursor.execute(sql_query, params)
            result = dictfetchall(cursor)

        if not result:
            return JsonResponse([], safe=False)

        # Step 3: Additional lookups
        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=base_quality_id, style_id=base_style_id
        ).first()

        sub_quality_map = {}
        if quality_prg:
            sub_quality_prg = sub_quality_program_table.objects.filter(
                status=1, tm_id=quality_prg.id
            ).values('size_id', 'per_box')
            sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

        size_ids = [r['size_id'] for r in result]
        size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}
        color_map = {c.id: c.name for c in color_table.objects.all()}

        # Delivered map (from child table)
        outward_qs = (
            child_packing_outward_table.objects
            .filter(tm_id__in=prg_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))
        )

        delivered_map = {
            (item['tm_id'], item['size_id']): item['total_qty'] or 0
            for item in outward_qs
        }

        # Step 4: Aggregate by size_id
        raw_data = []
        for row in result:
            key = (row['tm_id'], row['size_id'])
            delivered_pcs = delivered_map.get(key, 0)

            raw_data.append({
                "size_id": row["size_id"],
                "size_name": size_map.get(row["size_id"], "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(row["size_id"], 0),
                "already_received_qty": row["already_received_qty"] or 0,
                "already_out_qty": row["already_out_qty"] or 0,
                "available_qty": row["available_qty"] or 0,
                "delivered_pcs": delivered_pcs
            })

        # Now group by size_id
        aggregated_data = {}
        for item in raw_data:
            size_id = item["size_id"]
            if size_id not in aggregated_data:
                aggregated_data[size_id] = {
                    "size_id": size_id,
                    "size_name": item["size_name"],
                    "color_id": item["color_id"],
                    "color_name": item["color_name"],
                    "per_box": item["per_box"],
                    "already_received_qty": 0,
                    "already_out_qty": 0,
                    "available_qty": 0,
                    "delivered_pcs": 0
                }

            aggregated_data[size_id]["already_received_qty"] += item["already_received_qty"]
            aggregated_data[size_id]["already_out_qty"] += item["already_out_qty"]
            aggregated_data[size_id]["available_qty"] += item["available_qty"]
            aggregated_data[size_id]["delivered_pcs"] += item["delivered_pcs"]
            aggregated_data[size_id]["loose_pcs"] += item["loose_pcs"]

        final_data = list(aggregated_data.values())

        data_to_send = {
            'quality': {
                'id': base_quality_id,
                'name': quality_table.objects.get(pk=base_quality_id).name
            },
            'style': {
                'id': base_style_id,
                'name': style_table.objects.get(pk=base_style_id).name
            },
            'sizes': final_data,
            'quality_mismatch': False,
            'style_mismatch': False
        }

        return JsonResponse(data_to_send, safe=False)

@csrf_exempt
def get_packing_delivery_list_last_test_2_9_2025(request):
    if request.method == 'POST':
        prg_ids_list = request.POST.getlist('prg_id[]')

        if not prg_ids_list:
            return JsonResponse({'error_message': 'Program IDs are required'}, status=400)

        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

        if not prg_ids:
            return JsonResponse({'error_message': 'No valid Program IDs provided'}, status=400)

        # Step 1: Check for quality and style consistency
        first_item = parent_packing_outward_table.objects.filter(id=prg_ids[0]).first()
        if not first_item:
            return JsonResponse({'error_message': 'Invalid first program ID selected.'}, status=400)

        base_quality_id = first_item.quality_id
        base_style_id = first_item.style_id

        for prg_id in prg_ids[1:]:
            item = parent_packing_outward_table.objects.filter(id=prg_id).first()
            if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
                return JsonResponse({
                    'quality_mismatch': True,
                    'style_mismatch': True,
                    'error_message': 'Selected outwards have different Quality or Style, cannot load together.'
                }, status=200)

        # Step 2: Run SQL query
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(prg_ids))
            sql_query = f"""
                WITH packing_received_balance_sum AS (
                    SELECT 
                        inward.tm_id,
                        inward.work_order_no, 
                        inward.quality_id,
                        inward.style_id, 
                        inward.size_id,
                        inward.total_in_qty AS already_received_qty,
                        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                        COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
                    FROM (
                        SELECT 
                            tx.tm_id,
                            tx.work_order_no,
                            tm.quality_id,
                            tm.style_id,
                            tx.size_id,
                           --   tm.total_pcs AS total_in_qty
                            (tx.box_pcs) + (tx.loose_pcs) + (tx.seconds_pcs)+ (tx.shortage_pcs) AS total_in_qty
                        FROM tx_packing_inward AS tx
                        LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                        WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
                    ) AS inward
                    LEFT JOIN (
                        SELECT 
                            tp.tm_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.size_id
                    ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                    UNION

                    SELECT 
                        outward.tm_id,
                        outward.work_order_no,
                        outward.quality_id,
                        outward.style_id,
                        outward.size_id,
                        0 AS already_received_qty,
                        outward.total_out_qty AS already_out_qty,
                        (outward.total_out_qty - 0) AS available_qty
                    FROM (
                        SELECT 
                            tp.tm_id,
                            tp.work_order_no,
                            tp.quality_id,
                            tp.style_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                    ) AS outward
                    LEFT JOIN (
                        SELECT 
                            tx.tm_id,
                            tx.size_id
                        FROM tx_packing_inward AS tx
                        WHERE tx.status = 1
                    ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                    WHERE inward.tm_id IS NULL
                )
                SELECT 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id,
                    SUM(X.already_received_qty) AS already_received_qty, 
                    SUM(X.already_out_qty) AS already_out_qty,
                    SUM(X.available_qty) AS available_qty
                FROM packing_received_balance_sum AS X
                GROUP BY 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id
            """
            params = prg_ids * 3
            cursor.execute(sql_query, params)
            result = dictfetchall(cursor)

        if not result:
            return JsonResponse([], safe=False)

        # Step 3: Additional processing
        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=base_quality_id, style_id=base_style_id
        ).first()

        sub_quality_map = {}
        if quality_prg:
            sub_quality_prg = sub_quality_program_table.objects.filter(
                status=1, tm_id=quality_prg.id
            ).values('size_id', 'per_box')
            sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

        size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
        color_map = {c.id: c.name for c in color_table.objects.all()}



        # size_id = result['size_id']

        #     # ✅ Total outward qty for this size_id
        # total_out = (
        #     child_packing_outward_table.objects
        #     .filter(tm_id=prg_ids, size_id__in=[r['size_id'] for r in result], status=1)
        #     .aggregate(total_qty=Sum('quantity'))
        # )
        # total_out_pcs = total_out['total_qty'] or 0

        # if result:
        #     size_id = result[0]['size_id']
        #     total_out = (
        #         child_packing_outward_table.objects
        #         .filter(tm_id__in=prg_ids, size_id=size_id, status=1)
        #         .aggregate(total_qty=Sum('quantity'))
        #     )
        #     total_out_pcs = total_out['total_qty'] or 0
        # else:
        #     total_out_pcs = 0

        # Create lookup for delivered pcs per (tm_id, size_id)

 
        outward_qs = (
            child_packing_outward_table.objects
            .filter(tm_id__in=prg_ids, size_id__in=[r['size_id'] for r in result], status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))
        )

        # Build a dictionary {(tm_id, size_id): total_qty}
        delivered_map = {
            (item['tm_id'], item['size_id']): item['total_qty'] or 0
            for item in outward_qs
        }


        data = [] 
        for row in result:
            key = (row['tm_id'], row['size_id'])
            delivered_pcs = delivered_map.get(key, 0)

            data.append({
                **row,
                "size_name": size_map.get(row["size_id"], "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(row["size_id"], 0),
                "delivered_pcs": delivered_pcs
            })
        print('data:',data)



        # data = []
        # for row in result:
        #     data.append({
        #         **row,
        #         "size_name": size_map.get(row["size_id"], "Unknown"),
        #         "color_id": row.get("color_id"),
        #         "color_name": color_map.get(row.get("color_id"), "Unknown"),
        #         "per_box": sub_quality_map.get(row["size_id"], 0)
        #     })

        data_to_send = {
            'quality': {'id': base_quality_id, 'name': quality_table.objects.get(pk=base_quality_id).name},
            'style': {'id': base_style_id, 'name': style_table.objects.get(pk=base_style_id).name},
            'sizes': data,
            'quality_mismatch': False,
            'style_mismatch': False,
            # 'delivered_pcs':total_out_pcs
        }

        return JsonResponse(data_to_send, safe=False)



@csrf_exempt
def get_packing_delivery_list_test2(request):
    if request.method == 'POST':
        # Correctly get the list of IDs from the POST data
        prg_ids_list = request.POST.getlist('prg_ids[]')

        if not prg_ids_list:
            return JsonResponse({
                'error_message': 'Program IDs are required'
            }, status=400)
        
        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

        if not prg_ids:
            return JsonResponse({
                'error_message': 'No valid Program IDs provided'
            }, status=400)

        # Step 1: Check for quality and style consistency
        first_item = parent_packing_outward_table.objects.filter(id=prg_ids[0]).first()
        if not first_item:
            return JsonResponse({
                'error_message': 'Invalid first program ID selected.'
            }, status=400)

        base_quality_id = first_item.quality_id
        base_style_id = first_item.style_id

        # Check all other selected items against the first one
        for prg_id in prg_ids[1:]:
            item = parent_packing_outward_table.objects.filter(id=prg_id).first()
            if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
                # Mismatch detected, return a specific error flag with a 200 status
                return JsonResponse({
                    'quality_mismatch': True,
                    'style_mismatch': True,
                    'error_message': 'Selected outwards have different Quality or Style, cannot load together.'
                }, status=200)

        # Step 2: If all items are consistent, proceed with your existing SQL logic
        
        with connection.cursor() as cursor:
            sql_query = """
                WITH packing_received_balance_sum AS (
                    SELECT 
                        inward.tm_id,
                        inward.work_order_no, 
                        inward.quality_id,
                        inward.style_id, 
                        inward.size_id,
                        inward.total_in_qty AS already_received_qty,
                        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                        inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
                    FROM (
                        SELECT 
                            tx.tm_id,
                            tx.work_order_no,
                            tm.quality_id,
                            tm.style_id,
                            tx.size_id,
                            tm.total_pcs AS total_in_qty
                        FROM tx_packing_inward AS tx
                        LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                        WHERE tx.status = 1 AND tx.outward_id IN %s
                    ) AS inward
                    LEFT JOIN (
                        SELECT 
                            tp.tm_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1
                        GROUP BY tp.tm_id, tp.size_id
                    ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                    UNION

                    SELECT 
                        outward.tm_id,
                        outward.work_order_no,
                        outward.quality_id,
                        outward.style_id,
                        outward.size_id,
                        0 AS already_received_qty,
                        outward.total_out_qty AS already_out_qty,
                        (0 - outward.total_out_qty) AS available_qty
                    FROM (
                        SELECT 
                            tp.tm_id,
                            tp.work_order_no,
                            tp.quality_id,
                            tp.style_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1
                        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                    ) AS outward
                    LEFT JOIN (
                        SELECT 
                            tx.tm_id,
                            tx.size_id
                        FROM tx_packing_inward AS tx
                        WHERE tx.status = 1
                    ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                    WHERE inward.tm_id IS NULL
                )
                SELECT 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id,
                    SUM(X.already_received_qty) AS already_received_qty, 
                    SUM(X.already_out_qty) AS already_out_qty,
                    SUM(X.available_qty) AS available_qty
                FROM packing_received_balance_sum AS X
                GROUP BY 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id 
            """
            
            # Corrected parameter passing: use `tuple(prg_ids)`
            cursor.execute(sql_query, [tuple(prg_ids)])
            result = dictfetchall(cursor)

        if not result:
            return JsonResponse([], safe=False)

        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=base_quality_id, style_id=base_style_id
        ).first()

        sub_quality_map = {}
        if quality_prg:
            sub_quality_prg = sub_quality_program_table.objects.filter(
                status=1, tm_id=quality_prg.id
            ).values('size_id', 'per_box')
            sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

        size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
        color_map = {c.id: c.name for c in color_table.objects.all()}

        data = []
        for row in result:
            data.append({
                **row,
                "size_name": size_map.get(row["size_id"], "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(row["size_id"], 0)
            })

        data_to_send = {
            'quality': {'id': base_quality_id, 'name': quality_table.objects.get(pk=base_quality_id).name},
            'style': {'id': base_style_id, 'name': style_table.objects.get(pk=base_style_id).name},
            'sizes': data,
            'quality_mismatch': False,
            'style_mismatch': False,
        }
        
        return JsonResponse(data_to_send, safe=False)




# @csrf_exempt
# def get_packing_delivery_list_2_9(request):  
#     prg_ids = request.POST.getlist('prg_id[]')
#     print('received prg_ids:', prg_ids)

#     if not prg_ids:
#         return JsonResponse({'error': 'Program IDs are required'}, status=400)

#     # Convert all to integers (safe check)
#     try:
#         prg_ids = [int(pid) for pid in prg_ids if pid.strip().isdigit()]
#     except ValueError:
#         return JsonResponse({'error': 'Invalid Program IDs'}, status=400) 

#     if not prg_ids:
#         return JsonResponse({'error': 'No valid Program IDs provided'}, status=400)

#     with connection.cursor() as cursor:
#         cursor.execute("""
            # WITH packing_received_balance_sum AS (
            #     SELECT 
            #         inward.tm_id,
            #         inward.work_order_no, 
            #         inward.quality_id,
            #         inward.style_id, 
            #         inward.size_id,
            #         inward.total_in_qty AS already_received_qty,
            #         COALESCE(outward.total_out_qty, 0) AS already_out_qty,
            #         inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
            #     FROM (
            #         SELECT 
            #             tx.tm_id,
            #             tx.work_order_no,
            #             tm.quality_id,
            #             tm.style_id,
            #             tx.size_id,
            #             tm.total_pcs AS total_in_qty
            #         FROM tx_packing_inward AS tx
            #         LEFT JOIN tm_packing_inward AS tm 
            #             ON tx.tm_id = tm.id
            #         WHERE tx.status = 1 AND tx.outward_id IN %s
            #     ) AS inward
            #     LEFT JOIN (
            #         SELECT 
            #             tp.tm_id,
            #             tp.size_id,
            #             SUM(tp.quantity) AS total_out_qty
            #         FROM tx_packing_outward AS tp
            #         WHERE tp.status = 1
            #         GROUP BY tp.tm_id, tp.size_id
            #     ) AS outward
            #     ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

            #     UNION

            #     SELECT 
            #         outward.tm_id,
            #         outward.work_order_no,
            #         outward.quality_id,
            #         outward.style_id,
            #         outward.size_id,
            #         0 AS already_received_qty,
            #         outward.total_out_qty AS already_out_qty,
            #         (0 - outward.total_out_qty) AS available_qty
            #     FROM (
            #         SELECT 
            #             tp.tm_id,
            #             tp.work_order_no,
            #             tp.quality_id,
            #             tp.style_id,
            #             tp.size_id,
            #             SUM(tp.quantity) AS total_out_qty
            #         FROM tx_packing_outward AS tp
            #         WHERE tp.status = 1
            #         GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
            #     ) AS outward
            #     LEFT JOIN (
            #         SELECT 
            #             tx.tm_id,
            #             tx.size_id
            #         FROM tx_packing_inward AS tx
            #         WHERE tx.status = 1
            #     ) AS inward 
            #     ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
            #     WHERE inward.tm_id IS NULL
            # )
            # SELECT  
            #     X.tm_id,
            #     X.work_order_no,
            #     X.quality_id,
            #     X.style_id,
            #     X.size_id,
            #     SUM(X.already_received_qty) AS already_received_qty,  
            #     SUM(X.already_out_qty) AS already_out_qty,
            #     SUM(X.already_out_qty) - SUM(X.already_received_qty) AS available_qty
            # FROM packing_received_balance_sum AS X
            # GROUP BY 
            #     X.tm_id,
            #     X.work_order_no,
            #     X.quality_id,
            #     X.style_id,
            #     X.size_id
#         """, [tuple(prg_ids)]) 

#         result = dictfetchall(cursor)

#     if not result:
#         return JsonResponse([], safe=False)

#     # Use first record to get quality/style (assumes uniform)
#     quality_id = result[0]['quality_id']    
#     style_id = result[0]['style_id']

#     quality_prg = quality_program_table.objects.filter(
#         status=1, quality_id=quality_id, style_id=style_id
#     ).first()

#     sub_quality_map = {}
#     if quality_prg:
#         sub_quality_prg = sub_quality_program_table.objects.filter(
#             status=1, tm_id=quality_prg.id
#         ).values('size_id', 'per_box')
#         sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#     size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
#     color_map = {c.id: c.name for c in color_table.objects.all()}


#     # Access size_id from first result dict
#     size_id = result[0]['size_id']

#     # Filter with __in for list
#     total_out = (
#         child_packing_outward_table.objects 
#         .filter(tm_id__in=prg_ids, size_id=size_id, status=1)
#         .aggregate(total_qty=Sum('quantity'))
#     )




#     # size_id = result['size_id']
#     # print('size-id:',size_id)
#     # # ✅ Total outward qty for this size_id
#     # total_out = (
#     #     child_packing_outward_table.objects
#     #     .filter(tm_id=prg_ids, size_id=size_id, status=1)
#     #     .aggregate(total_qty=Sum('quantity'))
#     # )
#     total_out = total_out['total_qty'] or 0
#     print('total-out-pcs:',total_out)


#     data = []
#     for row in result:
#         data.append({
#             **row,
#             "size_name": size_map.get(row["size_id"], "Unknown"),
#             "color_id": row.get("color_id"),
#             "color_name": color_map.get(row.get("color_id"), "Unknown"),
#             "per_box": sub_quality_map.get(row["size_id"], 0)
#         })

#     return JsonResponse(data, safe=False)

 

@csrf_exempt 
def get_packing_delivery_list_test1(request):  
    prg_ids_raw = request.POST.get('prg_ids')
    print('out-ids:',prg_ids_raw)
    if not prg_ids_raw:
        return JsonResponse({'error': 'Program IDs are required'}, status=400)

    try:
        prg_ids = json.loads(prg_ids_raw)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid format for Program IDs'}, status=400)

    if not prg_ids:
        return JsonResponse({'error': 'No Program IDs provided'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            WITH packing_received_balance_sum AS (
                SELECT 
                    inward.tm_id,
                    inward.work_order_no, 
                    inward.quality_id,
                    inward.style_id, 
                    inward.size_id,
                    inward.total_in_qty AS already_received_qty,
                    COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                    inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
                FROM (
                    SELECT 
                        tx.tm_id,
                        tx.work_order_no,
                        tm.quality_id,
                        tm.style_id,
                        tx.size_id,
                        tm.total_pcs AS total_in_qty
                    FROM tx_packing_inward AS tx
                    LEFT JOIN tm_packing_inward AS tm 
                        ON tx.tm_id = tm.id
                    WHERE tx.status = 1 AND tx.outward_id IN %s
                ) AS inward
                LEFT JOIN (
                    SELECT 
                        tp.tm_id,
                        tp.size_id,
                        SUM(tp.quantity) AS total_out_qty
                    FROM tx_packing_outward AS tp
                    WHERE tp.status = 1
                    GROUP BY tp.tm_id, tp.size_id
                ) AS outward
                ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                UNION

                SELECT 
                    outward.tm_id,
                    outward.work_order_no,
                    outward.quality_id,
                    outward.style_id,
                    outward.size_id,
                    0 AS already_received_qty,
                    outward.total_out_qty AS already_out_qty,
                    (0 - outward.total_out_qty) AS available_qty
                FROM (
                    SELECT 
                        tp.tm_id,
                        tp.work_order_no,
                        tp.quality_id,
                        tp.style_id,
                        tp.size_id,
                        SUM(tp.quantity) AS total_out_qty
                    FROM tx_packing_outward AS tp
                    WHERE tp.status = 1
                    GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                ) AS outward
                LEFT JOIN (
                    SELECT 
                        tx.tm_id,
                        tx.size_id
                    FROM tx_packing_inward AS tx
                    WHERE tx.status = 1
                ) AS inward 
                ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                WHERE inward.tm_id IS NULL
            )
            SELECT  
                X.tm_id,
                X.work_order_no,
                X.quality_id,
                X.style_id,
                X.size_id,
                SUM(X.already_received_qty) AS already_received_qty,  
                SUM(X.already_out_qty) AS already_out_qty,
                SUM(X.already_out_qty) - SUM(X.already_received_qty) AS available_qty
            FROM packing_received_balance_sum AS X
            GROUP BY 
                X.tm_id,
                X.work_order_no,
                X.quality_id,
                X.style_id,
                X.size_id
        """, [tuple(prg_ids)])

        result = dictfetchall(cursor)

    if not result:
        return JsonResponse([], safe=False)

    # Use first record to get quality/style (assumes uniform)
    quality_id = result[0]['quality_id']    
    style_id = result[0]['style_id']

    quality_prg = quality_program_table.objects.filter(
        status=1, quality_id=quality_id, style_id=style_id
    ).first()

    sub_quality_map = {}
    if quality_prg:
        sub_quality_prg = sub_quality_program_table.objects.filter(
            status=1, tm_id=quality_prg.id
        ).values('size_id', 'per_box')
        sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

    size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
    color_map = {c.id: c.name for c in color_table.objects.all()}

    data = []
    for row in result:
        data.append({
            **row,
            "size_name": size_map.get(row["size_id"], "Unknown"),
            "color_id": row.get("color_id"),
            "color_name": color_map.get(row.get("color_id"), "Unknown"),
            "per_box": sub_quality_map.get(row["size_id"], 0)
        })

    return JsonResponse(data, safe=False)


 
@csrf_exempt 
def get_packing_delivery_list_test(request): 
    prg_id = request.POST.get('prg_id') 

    if not prg_id: 
        return JsonResponse({'error': 'Program ID is required'}, status=400) 

    # 🔹 Step 1: Run SQL query for inward vs outward quantities
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                inward.tm_id,
                inward.work_order_no,
                inward.quality_id,
                inward.style_id, 
                inward.size_id,
                inward.total_in_qty AS already_received_qty,
                COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty 
            FROM (
                SELECT 
                    tx.tm_id,
                    tx.work_order_no,
                    tm.quality_id,
                    tm.style_id,
                    tx.size_id,
                    tm.total_pcs AS total_in_qty
                FROM tx_packing_inward AS tx
                LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                WHERE tx.status = 1 AND tx.tm_id = %s
            ) AS inward
            LEFT JOIN (
                SELECT 
                    tp.tm_id,
                    tp.size_id,
                    SUM(tp.quantity) AS total_out_qty
                FROM tx_packing_outward AS tp
                WHERE tp.status = 1
                GROUP BY tp.tm_id, tp.size_id
            ) AS outward
            ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

            UNION

            SELECT 
                outward.tm_id,
                outward.work_order_no,
                outward.quality_id,
                outward.style_id,
                outward.size_id,
                0 AS already_received_qty,
                outward.total_out_qty AS already_out_qty,
                0 - outward.total_out_qty AS available_qty
            FROM (
                SELECT 
                    tp.tm_id,
                    tp.work_order_no,
                    tp.quality_id,
                    tp.style_id,
                    tp.size_id,
                    SUM(tp.quantity) AS total_out_qty
                FROM tx_packing_outward AS tp
                WHERE tp.status = 1
                GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
            ) AS outward
            LEFT JOIN (
                SELECT 
                    tx.tm_id,
                    tx.size_id
                FROM tx_packing_inward AS tx
                WHERE tx.status = 1
            ) AS inward
            ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
            WHERE inward.tm_id IS NULL
        """, [prg_id])
        result = dictfetchall(cursor)

    if not result:
        return JsonResponse([], safe=False)

    # 🔹 Step 2: Get quality/style for per_box lookup
    quality_id = result[0]['quality_id']
    style_id = result[0]['style_id']

    quality_prg = quality_program_table.objects.filter(
        status=1, quality_id=quality_id, style_id=style_id
    ).first()

    sub_quality_map = {}
    if quality_prg:
        sub_quality_prg = sub_quality_program_table.objects.filter(
            status=1, tm_id=quality_prg.id
        ).values('size_id', 'per_box')

        sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

    # 🔹 Step 3: Build maps for size/color names
    size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
    color_map = {c.id: c.name for c in color_table.objects.all()}  # if color_id available

    # 🔹 Step 4: Merge everything
    data = []
    for row in result:
        data.append({
            **row,
            "size_name": size_map.get(row["size_id"], "Unknown"),
            "color_id": row.get("color_id"),  # will be None if not available
            "color_name": color_map.get(row.get("color_id"), "Unknown"),
            "per_box": sub_quality_map.get(row["size_id"], 0)   # ✅ per_box included
        })

    return JsonResponse(data, safe=False)




# @csrf_exempt
# def get_packing_delivery_list(request): 
#     prg_id = request.POST.get('prg_id') 

#     if not prg_id: 
#         return JsonResponse({'error': 'Program ID is required'}, status=400) 

#     program_details = child_packing_outward_table.objects.filter(tm_id=prg_id).values(
#         'size_id', 'color_id', 'quantity', 'quality_id', 'style_id'
#     )
#     print('prg-detail:', list(program_details)) 

#     if not program_details:
#         return JsonResponse([], safe=False)

#     # ✅ Get single quality_id & style_id from first record
#     first_record = program_details[0]
#     quality_id = first_record['quality_id']
#     style_id = first_record['style_id']

#     # ✅ Get quality program
#     quality_prg = quality_program_table.objects.filter(
#         status=1, quality_id=quality_id, style_id=style_id
#     ).first()

#     sub_quality_map = {}
#     if quality_prg:
#         sub_quality_prg = sub_quality_program_table.objects.filter(
#             status=1, tm_id=quality_prg.id
#         ).values('size_id', 'per_box')

#         # ✅ convert size_id to int to match size_table.id
#         sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#         print('sub-size:', sub_quality_map)

#     # ✅ Build maps for size and color names
#     size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[p['size_id'] for p in program_details])}
#     color_map = {c.id: c.name for c in color_table.objects.filter(id__in=[p['color_id'] for p in program_details])}

#     # ✅ Build response with per_box
#     data = [
#         {
#             'size_id': item['size_id'],
#             'size_name': size_map.get(item['size_id'], 'Unknown'),
#             'color_id': item['color_id'],
#             'color_name': color_map.get(item['color_id'], 'Unknown'),
#             'quantity': item['quantity'],
#             'per_box': sub_quality_map.get(item['size_id'], 0)   # ✅ Include per_box
#         }
#         for item in program_details
#     ]

#     return JsonResponse(data, safe=False) 




def get_packing_delivery_list_without_per_box(request): 
    prg_id = request.POST.get('prg_id') 

    if not prg_id:
        return JsonResponse({'error': 'Program ID is required'}, status=400)

    program_details = child_packing_outward_table.objects.filter(tm_id=prg_id).values(
        'size_id', 'color_id', 'quantity','quality_id','style_id'
    )
    print('prg-detail:',program_details) 


    quality_map = {quality.id: quality.name for quality in quality_table.objects.filter(id__in=[p['quality_id'] for p in program_details])}
    style_map = {style.id: style.name for style in style_table.objects.filter(id__in=[p['style_id'] for p in program_details])}
    quality_prg = quality_program_table.objects.filter(
        status=1, quality_id=quality_map.id, style_id=style_map.id
    ).first()

    sub_quality_map = {}
    if quality_prg:
        sub_quality_prg = sub_quality_program_table.objects.filter(
            status=1, tm_id=quality_prg.id
        ).values('size_id', 'per_box')

        # ✅ convert size_id to int to match size_table.id
        sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

        print('sub-size:', sub_quality_map)

    
    size_map = {size.id: size.name for size in size_table.objects.filter(id__in=[p['size_id'] for p in program_details])}
    color_map = {color.id: color.name for color in color_table.objects.filter(id__in=[p['color_id'] for p in program_details])}

    data = [
        {
            'size_id': item['size_id'],
            'size_name': size_map.get(item['size_id'], 'Unknown'),  # Get size name from size_map
            'color_id': item['color_id'],
            'color_name': color_map.get(item['color_id'], 'Unknown'),  # Get color name from color_map
            'quantity': item['quantity']
        }
        for item in program_details
    ]

    return JsonResponse(data, safe=False) 




# stitching & packing 





@csrf_exempt
def get_stiching_packing_delivery_data(request):
    if request.method == 'POST':
        prg_ids_list = request.POST.getlist('prg_id[]')

        if not prg_ids_list:
            return JsonResponse({'error_message': 'Program IDs are required'}, status=400)

        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]

        if not prg_ids:
            return JsonResponse({'error_message': 'No valid Program IDs provided'}, status=400)

        # Step 1: Check for quality and style consistency
        first_item = parent_stiching_outward_table.objects.filter(id=prg_ids[0]).first()
        if not first_item:
            return JsonResponse({'error_message': 'Invalid first program ID selected.'}, status=400)

        base_quality_id = first_item.quality_id
        base_style_id = first_item.style_id

        for prg_id in prg_ids[1:]:
            item = parent_stiching_outward_table.objects.filter(id=prg_id).first()
            if not item or item.quality_id != base_quality_id or item.style_id != base_style_id:
                return JsonResponse({
                    'quality_mismatch': True,
                    'style_mismatch': True,
                    'error_message': 'Selected outwards have different Quality or Style, cannot load together.'
                }, status=200)

        # Step 2: Run SQL query
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(prg_ids))
            sql_query = f"""
                WITH packing_received_balance_sum AS (
                    SELECT 
                        inward.tm_id,
                        inward.work_order_no, 
                        inward.quality_id,
                        inward.style_id, 
                        inward.size_id,
                        inward.total_in_qty AS already_received_qty,
                        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                        COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
                    FROM (
                        SELECT 
                            tx.outward_id AS tm_id,
                            tx.work_order_no,
                            tm.quality_id,
                            tm.style_id,
                            tx.size_id,
                            (tx.box_pcs) + (tx.loose_pcs) + (tx.seconds_pcs)+ (tx.shortage_pcs) AS total_in_qty
                        FROM tx_packing_inward AS tx
                        LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                        WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
                    ) AS inward
                    LEFT JOIN (
                        SELECT 
                            tp.tm_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_stiching_outward AS tp
                        LEFT JOIN tm_stiching_outward AS tm ON tp.tm_id=tm.id
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.size_id
                    ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                    UNION

                    SELECT 
                        outward.tm_id,
                        outward.work_order_no,
                        outward.quality_id,
                        outward.style_id,
                        outward.size_id,
                        0 AS already_received_qty,
                        outward.total_out_qty AS already_out_qty,
                        (outward.total_out_qty - 0) AS available_qty
                    FROM (
                        SELECT 
                            tp.tm_id,
                            tp.work_order_no,
                            tp.quality_id,
                            tp.style_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_stiching_outward AS tp
                        WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                    ) AS outward
                    LEFT JOIN (
                        SELECT 
                            tx.tm_id,
                            tx.size_id
                        FROM tx_packing_inward AS tx
                        WHERE tx.status = 1
                    ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                    WHERE inward.tm_id IS NULL
                )
                SELECT 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id,
                    SUM(X.already_received_qty) AS already_received_qty, 
                    SUM(X.already_out_qty) AS already_out_qty,
                    SUM(X.available_qty) AS available_qty
                FROM packing_received_balance_sum AS X
                GROUP BY 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id
            """
            params = prg_ids * 3
            cursor.execute(sql_query, params)
            result = dictfetchall(cursor)

        if not result:
            return JsonResponse({'message': 'No data found'}, safe=False)

        # Step 3: Additional lookups
        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=base_quality_id, style_id=base_style_id
        ).first()

        sub_quality_map = {}
        if quality_prg:
            sub_quality_prg = sub_quality_program_table.objects.filter(
                status=1, tm_id=quality_prg.id
            ).values('size_id', 'per_box')
            sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

        size_ids = [r['size_id'] for r in result]
        size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}
        color_map = {c.id: c.name for c in color_table.objects.all()}

        outward_qs = (
            child_stiching_outward_table.objects
            .filter(tm_id__in=prg_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))
        )

        delivered_map = {
            (item['tm_id'], item['size_id']): item['total_qty'] or 0
            for item in outward_qs
        }


        # Step 1: Build tm_id to packing_id map
        tm_to_packing_id = {
            obj.id: obj.packing_id
            for obj in parent_lp_entry_table.objects.filter(packing_id__in=prg_ids,is_packing=1, status=1)
        }

        # Step 2: Get child entries
        parent_ids = list(tm_to_packing_id.keys())
        loose_pcs_value = (
            child_lp_entry_table.objects
            .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))  
        )
        print('lp-value:',loose_pcs_value)
        # Step 3: Build correct dictionary
        loose_pcs_qty = {}
        for item in loose_pcs_value:
            tm_id = item['tm_id']
            size_id = item['size_id']
            total_qty = item['total_qty'] or 0

            packing_id = tm_to_packing_id.get(tm_id)
            if packing_id:
                loose_pcs_qty[(packing_id, size_id)] = total_qty



        # Step 4: Build raw data
        raw_data = []
        for row in result:
            key = (row['tm_id'], row['size_id'])
            delivered_pcs = delivered_map.get(key, 0)
            loose_pcs_delivery = loose_pcs_qty.get(key, 0)
            print('raw key:', key, 'loose_pcs:', loose_pcs_qty.get(key, 0))

            raw_data.append({
                "size_id": row["size_id"],
                "size_name": size_map.get(row["size_id"], "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(row["size_id"], 0),
                "already_received_qty": row["already_received_qty"] or 0,
                "already_out_qty": row["already_out_qty"] or 0,
                "available_qty": (row["available_qty"] + loose_pcs_delivery) or 0,
                "delivered_pcs": delivered_pcs + loose_pcs_delivery,
                "loose_pcs_delivery":loose_pcs_delivery
            })
 
        # Step 5: Aggregate by size_id
        aggregated_data = {}
        for item in raw_data:
            size_id = item["size_id"]
            if size_id not in aggregated_data:
                aggregated_data[size_id] = {
                    "size_id": size_id,
                    "size_name": item["size_name"],
                    "color_id": item["color_id"],
                    "color_name": item["color_name"],
                    "per_box": item["per_box"],
                    "already_received_qty": 0,
                    "already_out_qty": 0,
                    "available_qty": 0,
                    "delivered_pcs": 0,
                    "loose_pcs_delivery":0
                }

            aggregated_data[size_id]["already_received_qty"] += item["already_received_qty"]
            aggregated_data[size_id]["already_out_qty"] += item["already_out_qty"]
            aggregated_data[size_id]["available_qty"] += item["available_qty"]
            aggregated_data[size_id]["delivered_pcs"] += item["delivered_pcs"]
            aggregated_data[size_id]["loose_pcs_delivery"] += item["loose_pcs_delivery"]

        # ✅ Filter out entries with available_qty = 0
        final_data = [
            data for data in aggregated_data.values()
            if data["available_qty"] > 0
        ]

        if not final_data:
            return JsonResponse({
                'quality_mismatch': False,
                'style_mismatch': False,
                'message': 'All selected outwards have zero available quantity.',
                'sizes': []
            }, safe=False)

        data_to_send = {
            'quality': {
                'id': base_quality_id,
                'name': quality_table.objects.get(pk=base_quality_id).name
            },
            'style': {
                'id': base_style_id,
                'name': style_table.objects.get(pk=base_style_id).name
            },
            'sizes': final_data,
            'quality_mismatch': False,
            'style_mismatch': False
        }

        return JsonResponse(data_to_send, safe=False)






@csrf_exempt
def get_stiching_packing_delivery_data_bk_4_9(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prg_ids_list = request.POST.getlist('prg_id[]')
    if not prg_ids_list:
        return JsonResponse({'error_message': 'Program IDs are required'}, status=400)

    # Convert to integers safely
    try:
        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]
    except ValueError:
        return JsonResponse({'error_message': 'Invalid Program IDs'}, status=400)

    if not prg_ids:
        return JsonResponse({'error_message': 'No valid Program IDs provided'}, status=400)

    # 🔹 Step 1: Execute SQL query
    with connection.cursor() as cursor:
        placeholders = ','.join(['%s'] * len(prg_ids))
        sql_query = f"""
            WITH packing_received_balance_sum AS (
                SELECT 
                    inward.tm_id,
                    inward.work_order_no,
                    inward.quality_id,
                    inward.style_id,
                    inward.size_id,
                    inward.total_in_qty AS already_received_qty,
                    COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                    COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
                FROM (
                    SELECT 
                        tx.tm_id,
                        tx.work_order_no,
                        tm.quality_id,
                        tm.style_id,
                        tx.size_id,
                        tm.total_pcs AS total_in_qty
                    FROM tx_packing_inward AS tx
                    LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                    WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
                ) AS inward
                LEFT JOIN (
                    SELECT 
                        tp.tm_id,
                        tp.size_id,
                        SUM(tp.quantity) AS total_out_qty
                    FROM tx_stiching_outward AS tp
                    LEFT JOIN tm_stiching_outward AS ts ON tp.tm_id = ts.id
                    WHERE tp.status = 1 AND ts.is_packing = 1 AND ts.id IN ({placeholders})
                    GROUP BY tp.tm_id, tp.size_id
                ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                UNION

                SELECT 
                    outward.tm_id,
                    outward.work_order_no,
                    outward.quality_id,
                    outward.style_id,
                    outward.size_id,
                    0 AS already_received_qty,
                    outward.total_out_qty AS already_out_qty,
                    (outward.total_out_qty - 0) AS available_qty
                FROM (
                    SELECT 
                        tp.tm_id,
                        tp.work_order_no,
                        tp.quality_id,
                        tp.style_id,
                        tp.size_id,
                        SUM(tp.quantity) AS total_out_qty
                    FROM tx_stiching_outward AS tp
                    WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                    GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                ) AS outward
                LEFT JOIN (
                    SELECT 
                        tx.tm_id,
                        tx.size_id
                    FROM tx_packing_inward AS tx
                    WHERE tx.status = 1
                ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                WHERE inward.tm_id IS NULL
            )
            SELECT 
                X.tm_id,
                X.work_order_no,
                X.quality_id,
                X.style_id,
                X.size_id,
                SUM(X.already_received_qty) AS already_received_qty,
                SUM(X.already_out_qty) AS already_out_qty,
                SUM(X.available_qty) AS available_qty
            FROM packing_received_balance_sum AS X
            GROUP BY 
                X.tm_id,
                X.work_order_no,
                X.quality_id,
                X.style_id,
                X.size_id
        """
        params = prg_ids * 3
        cursor.execute(sql_query, params)
        result = dictfetchall(cursor)

    if not result:
        return JsonResponse([], safe=False)

    # 🔹 Step 2: Validate consistency
    base_quality_id = result[0]['quality_id']
    base_style_id = result[0]['style_id']

    for row in result[1:]:
        if row['quality_id'] != base_quality_id or row['style_id'] != base_style_id:
            return JsonResponse({
                'quality_mismatch': True,
                'style_mismatch': True,
                'error_message': 'Selected records have different Quality or Style, cannot load together.'
            }, status=200)

    # 🔹 Step 3: Lookups
    quality = quality_table.objects.filter(pk=base_quality_id).first()
    style = style_table.objects.filter(pk=base_style_id).first()

    quality_prg = quality_program_table.objects.filter(
        status=1, quality_id=base_quality_id, style_id=base_style_id
    ).first()

    sub_quality_map = {}
    if quality_prg:
        sub_quality_qs = sub_quality_program_table.objects.filter(
            status=1, tm_id=quality_prg.id
        ).values('size_id', 'per_box')
        sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_qs}

    size_ids = [r['size_id'] for r in result]
    size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}
    color_map = {c.id: c.name for c in color_table.objects.all()}



    # Step 1: Build tm_id to packing_id map
    # tm_to_packing_id = {
    #     obj.id: obj.packing_id
    #     for obj in parent_lp_entry_table.objects.filter(packing_id__in=prg_ids, is_stitching=1, status=1)
    # }

    # # Step 2: Get child entries (loose pieces) from child_lp_entry_table
    # parent_ids = list(tm_to_packing_id.keys())
    # loose_pcs_value = (
    #     child_lp_entry_table.objects
    #     .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
    #     .values('tm_id', 'size_id')
    #     .annotate(total_qty=Sum('quantity'))
    # )

    # # Step 3: Build correct dictionary with default value handling
    # loose_pcs_qty = {}
    # for item in loose_pcs_value:
    #     tm_id = item['tm_id']
    #     size_id = item['size_id']
    #     total_qty = item['total_qty'] or 0  # Use 0 if total_qty is None or missing

    #     packing_id = tm_to_packing_id.get(tm_id)
    #     if packing_id:
    #         loose_pcs_qty[(packing_id, size_id)] = total_qty

    # # Handle missing values, default to 0
    # for packing_id in tm_to_packing_id.values():
    #     for size_id in size_ids:
    #         if (packing_id, size_id) not in loose_pcs_qty:
    #             loose_pcs_qty[(packing_id, size_id)] = 0


    # # Aggregating data for each size
    # aggregated_data = {}
    # for row in result:
    #     size_id = row['size_id']
    #     total_loose = sum(
    #         qty for (packing_id, s_id), qty in loose_pcs_qty.items() if s_id == size_id
    #     )

    #     if size_id not in aggregated_data:
    #         aggregated_data[size_id] = {
    #             "size_id": size_id,
    #             "size_name": size_map.get(size_id, "Unknown"),
    #             "color_id": row.get("color_id"),
    #             "color_name": color_map.get(row.get("color_id"), "Unknown"),
    #             "per_box": sub_quality_map.get(size_id, 0),
    #             "already_received_qty": 0,
    #             "already_out_qty": 0,
    #             "available_qty": 0,
    #             "loose_pcs_qty": total_loose,
    #             "loose_pcs_delivery": {
    #                 str(packing_id): qty
    #                 for (packing_id, s_id), qty in loose_pcs_qty.items() if s_id == size_id
    #             },
    #         }

    #     # Accumulate totals
    #     aggregated_data[size_id]["already_received_qty"] += row["already_received_qty"] or 0
    #     aggregated_data[size_id]["already_out_qty"] += row["already_out_qty"] or 0
    #     aggregated_data[size_id]["available_qty"] += row["available_qty"] or 0




    # final_data = list(aggregated_data.values())

    # # 🔹 Step 5: Response
    # data_to_send = {
    #     'quality': {
    #         'id': base_quality_id,
    #         'name': quality.name if quality else "Unknown"
    #     },
    #     'style': {
    #         'id': base_style_id,
    #         'name': style.name if style else "Unknown"
    #     },
    #     'sizes': final_data,
    #     'quality_mismatch': False,
    #     'style_mismatch': False
    # }

    # return JsonResponse(data_to_send, safe=False)



    # Step 1: Build tm_id to packing_id map
    tm_to_packing_id = {
        obj.id: obj.packing_id
        for obj in parent_lp_entry_table.objects.filter(packing_id__in=prg_ids, is_stitching=1, status=1)
    }

    # Step 2: Get child entries (loose pieces) from child_lp_entry_table
    parent_ids = list(tm_to_packing_id.keys())
    loose_pcs_value = (
        child_lp_entry_table.objects
        .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
        .values('tm_id', 'size_id')
        .annotate(total_qty=Sum('quantity'))
    )

    # Step 3: Build loose_pcs_qty dictionary with default value handling
    loose_pcs_qty = {}
    for item in loose_pcs_value:
        tm_id = item['tm_id']
        size_id = item['size_id']
        total_qty = item['total_qty'] or 0  # Use 0 if total_qty is None or missing

        packing_id = tm_to_packing_id.get(tm_id)
        if packing_id:
            loose_pcs_qty[(packing_id, size_id)] = total_qty

    # Handle missing values, default to 0 for any missing (packing_id, size_id) pair
    for packing_id in tm_to_packing_id.values():
        for size_id in size_ids:
            if (packing_id, size_id) not in loose_pcs_qty:
                loose_pcs_qty[(packing_id, size_id)] = 0

    # Step 4: Aggregating data for each size with simplified loose_pcs_delivery value
    aggregated_data = {}
    for row in result:
        size_id = row['size_id']

        # Calculate total loose pieces for the current size_id
        total_loose = sum(
            qty for (packing_id, s_id), qty in loose_pcs_qty.items() if s_id == size_id
        )

        if size_id not in aggregated_data:
            aggregated_data[size_id] = {
                "size_id": size_id,
                "size_name": size_map.get(size_id, "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(size_id, 0),
                "already_received_qty": 0,
                "already_out_qty": 0,
                "available_qty": 0,
                "loose_pcs_delivery": total_loose,  # Directly storing the value, no nested dictionary
            }

        # Accumulate totals
        aggregated_data[size_id]["already_received_qty"] += row["already_received_qty"] or 0
        aggregated_data[size_id]["already_out_qty"] += row["already_out_qty"] or 0
        aggregated_data[size_id]["available_qty"] += row["available_qty"] or 0

    # Step 5: Final Data
    final_data = list(aggregated_data.values())

    # Sample data to send
    data_to_send = {
        'quality': {
            'id': base_quality_id,
            'name': quality.name if quality else "Unknown"
        },
        'style': {
            'id': base_style_id,
            'name': style.name if style else "Unknown"
        },
        'sizes': final_data,
        'quality_mismatch': False,
        'style_mismatch': False
    }

    return JsonResponse(data_to_send, safe=False)




@csrf_exempt
def get_stiching_packing_delivery_data_test_1(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    prg_ids_list = request.POST.getlist('prg_id[]')
    if not prg_ids_list:
        return JsonResponse({'error_message': 'Program IDs are required'}, status=400)

    # Convert to integers safely
    try:
        prg_ids = [int(pid) for pid in prg_ids_list if pid.strip().isdigit()]
    except ValueError:
        return JsonResponse({'error_message': 'Invalid Program IDs'}, status=400)

    if not prg_ids:
        return JsonResponse({'error_message': 'No valid Program IDs provided'}, status=400)

    # 🔹 Step 1: Execute SQL query
    with connection.cursor() as cursor:
        placeholders = ','.join(['%s'] * len(prg_ids))
        # sql = f"""
        sql_query = f"""

            WITH packing_received_balance_sum AS (
                SELECT 
                    inward.tm_id,
                    inward.work_order_no,
                    inward.quality_id,
                    inward.style_id,
                    inward.size_id,
                    inward.total_in_qty AS already_received_qty,
                    COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                    COALESCE(outward.total_out_qty, 0) - inward.total_in_qty AS available_qty
                FROM (
                    SELECT 
                        tx.tm_id,
                        tx.work_order_no,
                        tm.quality_id,
                        tm.style_id,
                        tx.size_id,
                        tm.total_pcs AS total_in_qty
                    FROM tx_packing_inward AS tx
                    LEFT JOIN tm_packing_inward AS tm ON tx.tm_id = tm.id
                    WHERE tx.status = 1 AND tx.outward_id IN ({placeholders})
                ) AS inward
                LEFT JOIN (
                    SELECT 
                        tp.tm_id,
                        tp.size_id,
                        SUM(tp.quantity) AS total_out_qty
                    FROM tx_stiching_outward AS tp
                    LEFT JOIN tm_stiching_outward AS ts ON tp.tm_id = ts.id
                    WHERE tp.status = 1 AND ts.is_packing = 1 AND ts.id IN ({placeholders})
                    GROUP BY tp.tm_id, tp.size_id
                ) AS outward ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

                UNION

                SELECT 
                    outward.tm_id,
                    outward.work_order_no,
                    outward.quality_id,
                    outward.style_id,
                    outward.size_id,
                    0 AS already_received_qty,
                    outward.total_out_qty AS already_out_qty,
                    (outward.total_out_qty - 0) AS available_qty
                FROM (
                    SELECT 
                        tp.tm_id,
                        tp.work_order_no,
                        tp.quality_id,
                        tp.style_id,
                        tp.size_id,
                        SUM(tp.quantity) AS total_out_qty
                    FROM tx_stiching_outward AS tp
                    WHERE tp.status = 1 AND tp.tm_id IN ({placeholders})
                    GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                ) AS outward
                LEFT JOIN (
                    SELECT 
                        tx.tm_id,
                        tx.size_id
                    FROM tx_packing_inward AS tx
                    WHERE tx.status = 1
                ) AS inward ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
                WHERE inward.tm_id IS NULL
            )
            SELECT 
                X.tm_id,
                X.work_order_no,
                X.quality_id,
                X.style_id,
                X.size_id,
                SUM(X.already_received_qty) AS already_received_qty,
                SUM(X.already_out_qty) AS already_out_qty,
                SUM(X.available_qty) AS available_qty
            FROM packing_received_balance_sum AS X
            GROUP BY 
                X.tm_id,
                X.work_order_no,
                X.quality_id,
                X.style_id,
                X.size_id
       
        """
        # cursor.execute(sql, prg_ids)
        # result = dictfetchall(cursor)

        params = prg_ids * 3
        cursor.execute(sql_query, params)
        result = dictfetchall(cursor)

    if not result:
        return JsonResponse([], safe=False)

    # 🔹 Step 2: Validate consistency
    base_quality_id = result[0]['quality_id']
    base_style_id = result[0]['style_id']

    for row in result[1:]:
        if row['quality_id'] != base_quality_id or row['style_id'] != base_style_id:
            return JsonResponse({
                'quality_mismatch': True,
                'style_mismatch': True,
                'error_message': 'Selected records have different Quality or Style, cannot load together.'
            }, status=200)

    # 🔹 Step 3: Lookups
    quality = quality_table.objects.filter(pk=base_quality_id).first()
    style = style_table.objects.filter(pk=base_style_id).first()

    quality_prg = quality_program_table.objects.filter(
        status=1, quality_id=base_quality_id, style_id=base_style_id
    ).first()

    sub_quality_map = {}
    if quality_prg:
        sub_quality_qs = sub_quality_program_table.objects.filter(
            status=1, tm_id=quality_prg.id
        ).values('size_id', 'per_box')
        sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_qs}

    size_ids = [r['size_id'] for r in result]
    size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}
    color_map = {c.id: c.name for c in color_table.objects.all()}  # Optional

    # 🔹 Step 4: Format result
    aggregated_data = {}
    for row in result:
        size_id = row['size_id']

        # ````````````````````````````````


        # Step 1: Build tm_id to packing_id map
        tm_to_packing_id = {
            obj.id: obj.packing_id
            for obj in parent_lp_entry_table.objects.filter(packing_id__in=prg_ids,is_stitching=1, status=1)
        }

        # Step 2: Get child entries
        parent_ids = list(tm_to_packing_id.keys())
        loose_pcs_value = (
            child_lp_entry_table.objects
            .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))  
        )
        print('lp-value:',loose_pcs_value)
        # Step 3: Build correct dictionary
        loose_pcs_qty = {}
        for item in loose_pcs_value:
            tm_id = item['tm_id']
            size_id = item['size_id']
            total_qty = item['total_qty'] or 0

            packing_id = tm_to_packing_id.get(tm_id)
            if packing_id:
                loose_pcs_qty[(packing_id, size_id)] = total_qty


        # ````````````````````````````````````````
        if size_id not in aggregated_data:
            total_loose = sum(
                qty for (packing_id, s_id), qty in loose_pcs_qty.items() if s_id == size_id
            )

            aggregated_data[size_id] = {
                "size_id": size_id,
                "size_name": size_map.get(size_id, "Unknown"),
                "color_id": row.get("color_id"),
                "color_name": color_map.get(row.get("color_id"), "Unknown"),
                "per_box": sub_quality_map.get(size_id, 0),
                "already_received_qty": 0,
                "already_out_qty": 0,
                "available_qty": 0,
                "loose_pcs_qty": total_loose,
                "loose_pcs_delivery": {
                    str(packing_id): qty
                    for (packing_id, s_id), qty in loose_pcs_qty.items() if s_id == size_id
                },
            }

        # Accumulate totals
        aggregated_data[size_id]["already_received_qty"] += row["already_received_qty"] or 0
        aggregated_data[size_id]["already_out_qty"] += row["already_out_qty"] or 0
        aggregated_data[size_id]["available_qty"] += row["available_qty"] or 0 


        # if size_id not in aggregated_data:
        #     aggregated_data[size_id] = {
        #         "size_id": size_id,
        #         "size_name": size_map.get(size_id, "Unknown"),
        #         "color_id": row.get("color_id"),
        #         "color_name": color_map.get(row.get("color_id"), "Unknown"),
        #         "per_box": sub_quality_map.get(size_id, 0),
        #         "already_received_qty": 0,
        #         "already_out_qty": 0,
        #         "available_qty": 0,
        #         "loose_pcs_delivery":loose_pcs_qty,
        #     }

        # aggregated_data[size_id]["already_received_qty"] += row["already_received_qty"] or 0
        # aggregated_data[size_id]["already_out_qty"] += row["already_out_qty"] or 0
        # aggregated_data[size_id]["available_qty"] += row["available_qty"] or 0
        # aggregated_data[size_id]["loose_pcs_qty"] += row["loose_pcs_qty"] or 0

    final_data = list(aggregated_data.values())

    # 🔹 Step 5: Response
    data_to_send = {
        'quality': {
            'id': base_quality_id,
            'name': quality.name if quality else "Unknown"
        },
        'style': {
            'id': base_style_id,
            'name': style.name if style else "Unknown"
        },
        'sizes': final_data,
        'quality_mismatch': False,
        'style_mismatch': False
    }

    return JsonResponse(data_to_send, safe=False)




@csrf_exempt
def get_stiching_packing_delivery_data_3_9_2025(request): 
    # prg_id = request.POST.get('prg_id') 
    prg_id = request.POST.getlist('prg_id[]')
    print('received prg_id:', prg_id)

    if not prg_id:
        return JsonResponse({'error': 'Program IDs are required'}, status=400)

    # Convert all to integers (safe check)
    try:
        prg_id = [int(pid) for pid in prg_id if pid.strip().isdigit()]
    except ValueError:
        return JsonResponse({'error': 'Invalid Program IDs'}, status=400) 

    if not prg_id:
        return JsonResponse({'error': 'No valid Program IDs provided'}, status=400)


    # if not prg_id: 
    #     return JsonResponse({'error': 'Program ID is required'}, status=400) 

    # 🔹 Step 1: Run SQL query (WITH + UNION + GROUP BY)
    with connection.cursor() as cursor:
        cursor.execute("""

WITH packing_received_balance_sum AS (
    -- LEFT JOIN part
    SELECT 
        inward.tm_id,
        inward.work_order_no,
        inward.quality_id,
        inward.style_id, 
        inward.size_id,
        inward.outward_id,
        inward.total_in_qty AS already_received_qty,
        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
        inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
    FROM (
        SELECT 
            tx.tm_id,
            tx.work_order_no,
            tx.outward_id,
            tm.quality_id,
            tm.style_id,
            tx.size_id,
            tm.total_pcs AS total_in_qty
        FROM tx_packing_inward AS tx
        LEFT JOIN tm_packing_inward AS tm 
            ON tx.tm_id = tm.id
        WHERE tx.status = 1 AND tx.outward_id = %s
    ) AS inward
    LEFT JOIN (
        SELECT 
            tp.tm_id,
            tp.size_id,
            SUM(tp.quantity) AS total_out_qty
        FROM tx_stiching_outward AS tp
        LEFT JOIN tm_stiching_outward AS ts ON tp.tm_id = ts.id
        WHERE tp.status = 1 AND ts.is_packing = 1
        GROUP BY tp.tm_id, tp.size_id
    ) AS outward
    ON inward.tm_id = outward.tm_id AND inward.size_id = outward.size_id

    UNION

    -- RIGHT JOIN part for unmatched outward records
    SELECT 
        outward.tm_id,
        outward.work_order_no,
        outward.quality_id,
        outward.style_id,
        outward.size_id,
        NULL AS outward_id,  -- outward_id is unknown here
        0 AS already_received_qty,
        outward.total_out_qty AS already_out_qty,
        (0 - outward.total_out_qty) AS available_qty
    FROM (
        SELECT 
            tp.tm_id,
            tp.work_order_no,
            tp.quality_id,
            tp.style_id,
            tp.size_id,
            SUM(tp.quantity) AS total_out_qty
        FROM tx_stiching_outward AS tp
        WHERE tp.status = 1
        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
    ) AS outward
    LEFT JOIN (
        SELECT 
            tx.tm_id,
            tx.size_id
        FROM tx_packing_inward AS tx
        WHERE tx.status = 1
    ) AS inward 
    ON outward.tm_id = inward.tm_id AND outward.size_id = inward.size_id
    WHERE inward.tm_id IS NULL
)

-- Final summarized result
SELECT 
    X.tm_id AS outward_id,
    X.tm_id,
    X.work_order_no,
    X.quality_id,
    X.style_id,
    X.size_id,
    SUM(X.already_received_qty) AS already_received_qty, 
    SUM(X.already_out_qty) AS already_out_qty,
    SUM(X.already_out_qty) - SUM(X.already_received_qty) AS available_qty
FROM packing_received_balance_sum AS X
GROUP BY 
    X.outward_id,
 --   X.tm_id,
    X.work_order_no,
    X.quality_id,
    X.style_id,
    X.size_id

          
        """, [prg_id])
        result = dictfetchall(cursor)

    if not result:
        return JsonResponse([], safe=False)

    # 🔹 Step 2: Get quality/style for per_box lookup
    quality_id = result[0]['quality_id']
    style_id = result[0]['style_id']

    quality_prg = quality_program_table.objects.filter(
        status=1, quality_id=quality_id, style_id=style_id
    ).first()

    sub_quality_map = {}
    if quality_prg:
        sub_quality_prg = sub_quality_program_table.objects.filter(
            status=1, tm_id=quality_prg.id
        ).values('size_id', 'per_box')
        sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

    # 🔹 Step 3: Build maps for size/color names
    size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
    color_map = {c.id: c.name for c in color_table.objects.all()}  # if color_id available

    # 🔹 Step 4: Merge everything
    data = []
    for row in result:
        data.append({
            **row,
            "size_name": size_map.get(row["size_id"], "Unknown"),
            "color_id": row.get("color_id"),  # will be None if not available
            "color_name": color_map.get(row.get("color_id"), "Unknown"),
            "per_box": sub_quality_map.get(row["size_id"], 0)
        })

    return JsonResponse(data, safe=False)



# @csrf_exempt
# def get_stiching_packing_delivery_data(request): 
#     prg_id = request.POST.get('prg_id') 

#     if not prg_id: 
#         return JsonResponse({'error': 'Program ID is required'}, status=400) 

#     # 🔹 Step 1: Run SQL query (WITH + UNION + GROUP BY)
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             WITH packing_received_balance_sum AS (
#                 -- LEFT JOIN part
#                 SELECT 
#                     inward.tm_id,
#                     inward.work_order_no,
#                     inward.quality_id,
#                     inward.style_id, 
#                     inward.size_id,
#                     inward.total_in_qty AS already_received_qty,
#                     COALESCE(outward.total_out_qty, 0) AS already_out_qty,
#                     inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
#                 FROM (
#                     SELECT 
#                         tx.tm_id,
#                         tx.work_order_no,
#                         tm.quality_id,
#                         tm.style_id,
#                         tx.size_id,
#                         tm.total_pcs AS total_in_qty
#                     FROM tx_packing_inward AS tx
#                     LEFT JOIN tm_packing_inward AS tm 
#                         ON tx.tm_id = tm.id
#                     WHERE tx.status = 1 AND tx.outward_id = %s
#                 ) AS inward
#                 LEFT JOIN (
#                     SELECT 
#                         tp.tm_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_stiching_outward AS tp
#                     LEFT JOIN tm_stiching_outward AS ts ON tp.tm_id = ts.id
#                     WHERE tp.status = 1 AND ts.is_packing=1
#                     GROUP BY tp.tm_id, tp.size_id
#                 ) AS outward
#                 ON inward.tm_id = outward.tm_id 
#             AND inward.size_id = outward.size_id

#                 UNION

#                 -- RIGHT JOIN part for unmatched outward records
#                 SELECT 
#                     outward.tm_id,
#                     outward.work_order_no,
#                     outward.quality_id,
#                     outward.style_id,
#                     outward.size_id,
#                     0 AS already_received_qty,
#                     outward.total_out_qty AS already_out_qty,
#                     (0 - outward.total_out_qty) AS available_qty
#                 FROM (
#                     SELECT 
#                         tp.tm_id,
#                         tp.work_order_no,
#                         tp.quality_id,
#                         tp.style_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_stiching_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
#                 ) AS outward
#                 LEFT JOIN (
#                     SELECT 
#                         tx.tm_id,
#                         tx.size_id
#                     FROM tx_packing_inward AS tx
#                     WHERE tx.status = 1
#                 ) AS inward 
#                 ON outward.tm_id = inward.tm_id 
#             AND outward.size_id = inward.size_id
#                 WHERE inward.tm_id IS NULL
#             )
#             -- Final summarized result
#             SELECT 
#                 X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id,
#                 SUM(X.already_received_qty) AS already_received_qty, 
#                 SUM(X.already_out_qty) AS already_out_qty,
#                 SUM(X.already_out_qty)-SUM(X.already_received_qty) AS available_qty
#             FROM packing_received_balance_sum AS X
#             GROUP BY 
#             --  X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id
#         """, [prg_id])
#         result = dictfetchall(cursor)

#     if not result:
#         return JsonResponse([], safe=False)

#     # 🔹 Step 2: Get quality/style for per_box lookup
#     quality_id = result[0]['quality_id']
#     style_id = result[0]['style_id']

#     quality_prg = quality_program_table.objects.filter(
#         status=1, quality_id=quality_id, style_id=style_id
#     ).first()

#     sub_quality_map = {}
#     if quality_prg:
#         sub_quality_prg = sub_quality_program_table.objects.filter(
#             status=1, tm_id=quality_prg.id
#         ).values('size_id', 'per_box')
#         sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#     # 🔹 Step 3: Build maps for size/color names
#     size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
#     color_map = {c.id: c.name for c in color_table.objects.all()}  # if color_id available

#     # 🔹 Step 4: Merge everything
#     data = []
#     for row in result:
#         data.append({
#             **row,
#             "size_name": size_map.get(row["size_id"], "Unknown"),
#             "color_id": row.get("color_id"),  # will be None if not available
#             "color_name": color_map.get(row.get("color_id"), "Unknown"),
#             "per_box": sub_quality_map.get(row["size_id"], 0)
#         })

#     return JsonResponse(data, safe=False)




def get_stiching_packing_delivery_data_without_per_box(request):
    prg_id = request.POST.get('prg_id')

    if not prg_id:
        return JsonResponse({'error': 'Program ID is required'}, status=400)

    program_details = child_stiching_outward_table.objects.filter(tm_id=prg_id,status=1).values(
        'size_id', 'color_id', 'quantity'
    )
    print('prg-detail:',program_details)

    size_map = {size.id: size.name for size in size_table.objects.filter(id__in=[p['size_id'] for p in program_details])}
    color_map = {color.id: color.name for color in color_table.objects.filter(id__in=[p['color_id'] for p in program_details])}

    data = [
        {
            'size_id': item['size_id'],
            'size_name': size_map.get(item['size_id'], 'Unknown'),  # Get size name from size_map
            'color_id': item['color_id'],
            'color_name': color_map.get(item['color_id'], 'Unknown'),  # Get color name from color_map
            'quantity': item['quantity']
        }
        for item in program_details
    ]

    return JsonResponse(data, safe=False) 

 
# ``````````````````````````


from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def get_packing_delivery_update_list(request):
#     prg_id = request.POST.get('prg_id')
#     tm_id = request.POST.get('tm_id')
#     print('packing-ids:', prg_id, tm_id)

#     if not prg_id or not tm_id:
#         return JsonResponse({'error': 'Program ID and TM ID are required'}, status=400)

#     try:
        # with connection.cursor() as cursor:
        #     cursor.execute("""
                # WITH packing_received_balance_sum AS (
                #     -- LEFT JOIN part
                #     SELECT 
                #         inward.tm_id,
                #         inward.work_order_no, 
                #         inward.quality_id,
                #         inward.style_id, 
                #         inward.size_id,
                #         inward.total_in_qty AS already_received_qty,
                #         COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                #         inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
                #     FROM (
                #         SELECT 
                #             tx.tm_id,
                #             tx.work_order_no,
                #             tm.quality_id,
                #             tm.style_id,
                #             tx.size_id,
                #             tm.total_pcs AS total_in_qty
                #         FROM tx_packing_inward AS tx
                #         LEFT JOIN tm_packing_inward AS tm 
                #                ON tx.tm_id = tm.id
                #         WHERE tx.status = 1 AND tx.outward_id = %s AND tx.tm_id = %s
                #     ) AS inward
                #     LEFT JOIN (
                #         SELECT 
                #             tp.tm_id,
                #             tp.size_id,
                #             SUM(tp.quantity) AS total_out_qty
                #         FROM tx_packing_outward AS tp
                #         WHERE tp.status = 1
                #         GROUP BY tp.tm_id, tp.size_id
                #     ) AS outward
                #     ON inward.tm_id = outward.tm_id 
                #    AND inward.size_id = outward.size_id

                #     UNION

                #     -- RIGHT JOIN part for unmatched outward records
                #     SELECT 
                #         outward.tm_id,
                #         outward.work_order_no,
                #         outward.quality_id,
                #         outward.style_id,
                #         outward.size_id,
                #         0 AS already_received_qty,
                #         outward.total_out_qty AS already_out_qty,
                #         (0 - outward.total_out_qty) AS available_qty
                #     FROM (
                #         SELECT 
                #             tp.tm_id,
                #             tp.work_order_no,
                #             tp.quality_id,
                #             tp.style_id,
                #             tp.size_id,
                #             SUM(tp.quantity) AS total_out_qty
                #         FROM tx_packing_outward AS tp
                #         WHERE tp.status = 1
                #         GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                #     ) AS outward
                #     LEFT JOIN (
                #         SELECT 
                #             tx.tm_id,
                #             tx.size_id
                #         FROM tx_packing_inward AS tx
                #         WHERE tx.status = 1
                #     ) AS inward 
                #     ON outward.tm_id = inward.tm_id 
                #    AND outward.size_id = inward.size_id
                #     WHERE inward.tm_id IS NULL
                # )
                # -- Final summarized result
                # SELECT  
                #     X.tm_id,
                #     X.work_order_no,
                #     X.quality_id,
                #     X.style_id,
                #     X.size_id,
                #     SUM(X.already_received_qty) AS already_received_qty,  
                #     SUM(X.already_out_qty) AS already_out_qty,
                #     SUM(X.already_received_qty) - SUM(X.already_out_qty) AS available_qty
                # FROM packing_received_balance_sum AS X
                # GROUP BY 
                #     X.tm_id,
                #     X.work_order_no,
                #     X.quality_id,
                #     X.style_id,
                #     X.size_id
#             """, [prg_id, tm_id])

#             rows = cursor.fetchall()

#         # map sizes
#         size_ids = [r[4] for r in rows]
#         size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}

#         data = []
#         for row in rows:
#             data.append({
#                 "tm_id": row[0],
#                 "work_order_no": row[1],
#                 "quality_id": row[2],
#                 "style_id": row[3],
#                 "size_id": row[4],
#                 "size_name": size_map.get(row[4], "Unknown"),
#                 "already_received_qty": float(row[5]),
#                 "already_out_qty": float(row[6]),
#                 "available_qty": float(row[7]),
#             })

#         return JsonResponse(data, safe=False)

#     except Exception as e:
#         print("Error in get_packing_delivery_update_list:", e)
#         return JsonResponse({'error': str(e)}, status=500)



# @csrf_exempt
# def get_packing_delivery_update_list(request): 
#     prg_id = request.POST.get('prg_id') 
#     tm_id = request.POST.get('tm_id') 

#     if not prg_id and not tm_id: 
#         return JsonResponse({'error': 'Outward ID and tm Id is required'}, status=400) 

#     # 🔹 Step 1: Run SQL query (WITH + UNION + GROUP BY)
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             WITH packing_received_balance_sum AS (
#                 -- LEFT JOIN part
#                 SELECT 
#                     inward.tm_id,
#                     inward.work_order_no, 
#                     inward.quality_id,
#                     inward.style_id, 
#                     inward.size_id,
#                     inward.total_in_qty AS already_received_qty,
#                     COALESCE(outward.total_out_qty, 0) AS already_out_qty,
#                     inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
#                 FROM (
#                     SELECT 
#                         tx.tm_id,
#                         tx.work_order_no,
#                         tm.quality_id,
#                         tm.style_id,
#                         tx.size_id,
#                         tm.total_pcs AS total_in_qty
#                     FROM tx_packing_inward AS tx
#                     LEFT JOIN tm_packing_inward AS tm 
#                            ON tx.tm_id = tm.id
#                     WHERE tx.status = 1 AND tx.outward_id = %s AND tx.tm_id=%s
#                 ) AS inward
#                 LEFT JOIN (
#                     SELECT 
#                         tp.tm_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_packing_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.size_id
#                 ) AS outward
#                 ON inward.tm_id = outward.tm_id 
#                AND inward.size_id = outward.size_id

#                 UNION

#                 -- RIGHT JOIN part for unmatched outward records
#                 SELECT 
#                     outward.tm_id,
#                     outward.work_order_no,
#                     outward.quality_id,
#                     outward.style_id,
#                     outward.size_id,
#                     0 AS already_received_qty,
#                     outward.total_out_qty AS already_out_qty,
#                     (0 - outward.total_out_qty) AS available_qty
#                 FROM (
#                     SELECT 
#                         tp.tm_id,
#                         tp.work_order_no,
#                         tp.quality_id,
#                         tp.style_id,
#                         tp.size_id,
#                         SUM(tp.quantity) AS total_out_qty
#                     FROM tx_packing_outward AS tp
#                     WHERE tp.status = 1
#                     GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
#                 ) AS outward
#                 LEFT JOIN (
#                     SELECT 
#                         tx.tm_id,
#                         tx.size_id
#                     FROM tx_packing_inward AS tx
#                     WHERE tx.status = 1
#                 ) AS inward 
#                 ON outward.tm_id = inward.tm_id 
#                AND outward.size_id = inward.size_id
#                 WHERE inward.tm_id IS NULL
#             )
#             -- Final summarized result
#             SELECT  
#                 X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id,
#                 SUM(X.already_received_qty) AS already_received_qty,  
#                 SUM(X.already_out_qty) AS already_out_qty,
#                 SUM(X.already_out_qty)-SUM(X.already_received_qty) AS available_qty
#             FROM packing_received_balance_sum AS X
#             GROUP BY 
#               --  X.tm_id,
#                 X.work_order_no,
#                 X.quality_id,
#                 X.style_id,
#                 X.size_id
#         """, [prg_id,tm_id])
#         result = dictfetchall(cursor)

#     if not result:
#         return JsonResponse([], safe=False)

#     # 🔹 Step 2: Get quality/style for per_box lookup
#     quality_id = result[0]['quality_id']    
#     style_id = result[0]['style_id']

#     quality_prg = quality_program_table.objects.filter(
#         status=1, quality_id=quality_id, style_id=style_id
#     ).first()

#     sub_quality_map = {}
#     if quality_prg:
#         sub_quality_prg = sub_quality_program_table.objects.filter(
#             status=1, tm_id=quality_prg.id
#         ).values('size_id', 'per_box')
#         sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

#     # 🔹 Step 3: Build maps for size/color names
#     size_map = {s.id: s.name for s in size_table.objects.filter(id__in=[r['size_id'] for r in result])}
#     color_map = {c.id: c.name for c in color_table.objects.all()}  # if color_id available

#     # 🔹 Step 4: Merge everything
#     data = []
#     for row in result:
#         data.append({
#             **row,
#             "size_name": size_map.get(row["size_id"], "Unknown"),
#             "color_id": row.get("color_id"),  # will be None if not available
#             "color_name": color_map.get(row.get("color_id"), "Unknown"),
#             "per_box": sub_quality_map.get(row["size_id"], 0)
#         })

#     return JsonResponse(data, safe=False)



@csrf_exempt
def get_packing_delivery_update_list_tet__29(request):
    prg_id = request.POST.get('prg_id')
    tm_id = request.POST.get('tm_id')
    print('packing-ids:', prg_id, tm_id)

    if not prg_id or not tm_id:
        return JsonResponse({'error': 'Program ID and TM ID are required'}, status=400)

    try:
        # Fetch box details from ORM
        program_details = list(child_packing_inward_table.objects.filter(
            tm_id=tm_id, outward_id=prg_id, status=1
        ).values('size_id', 'box_pcs', 'pcs_per_box', 'box', 'loose_pcs', 'seconds_pcs', 'shortage_pcs'))

        size_ids = [p['size_id'] for p in program_details]
        size_map = {s.id: s.name for s in size_table.objects.filter(id__in=size_ids)}

        # Fetch available qty from raw SQL
        with connection.cursor() as cursor:
            cursor.execute(""" 
                           
                           WITH packing_received_balance_sum AS (
                    -- LEFT JOIN part
                    SELECT 
                        inward.tm_id,
                        inward.work_order_no, 
                        inward.quality_id,
                        inward.style_id, 
                        inward.size_id,
                        inward.total_in_qty AS already_received_qty,
                        COALESCE(outward.total_out_qty, 0) AS already_out_qty,
                        inward.total_in_qty - COALESCE(outward.total_out_qty, 0) AS available_qty
                    FROM (
                        SELECT 
                            tx.tm_id,
                            tx.work_order_no,
                            tm.quality_id,
                            tm.style_id,
                            tx.size_id,
                            tm.total_pcs AS total_in_qty
                        FROM tx_packing_inward AS tx
                        LEFT JOIN tm_packing_inward AS tm 
                               ON tx.tm_id = tm.id
                        WHERE tx.status = 1 AND tx.outward_id = %s AND tx.tm_id = %s
                    ) AS inward
                    LEFT JOIN (
                        SELECT 
                            tp.tm_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1
                        GROUP BY tp.tm_id, tp.size_id
                    ) AS outward
                    ON inward.tm_id = outward.tm_id 
                   AND inward.size_id = outward.size_id

                    UNION

                    -- RIGHT JOIN part for unmatched outward records
                    SELECT 
                        outward.tm_id,
                        outward.work_order_no,
                        outward.quality_id,
                        outward.style_id,
                        outward.size_id,
                        0 AS already_received_qty,
                        outward.total_out_qty AS already_out_qty,
                        (0 - outward.total_out_qty) AS available_qty
                    FROM (
                        SELECT 
                            tp.tm_id,
                            tp.work_order_no,
                            tp.quality_id,
                            tp.style_id,
                            tp.size_id,
                            SUM(tp.quantity) AS total_out_qty
                        FROM tx_packing_outward AS tp
                        WHERE tp.status = 1
                        GROUP BY tp.tm_id, tp.work_order_no, tp.quality_id, tp.style_id, tp.size_id
                    ) AS outward
                    LEFT JOIN (
                        SELECT 
                            tx.tm_id,
                            tx.size_id
                        FROM tx_packing_inward AS tx
                        WHERE tx.status = 1
                    ) AS inward 
                    ON outward.tm_id = inward.tm_id 
                   AND outward.size_id = inward.size_id
                    WHERE inward.tm_id IS NULL
                )
                -- Final summarized result
                SELECT  
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id,
                    SUM(X.already_received_qty) AS already_received_qty,  
                    SUM(X.already_out_qty) AS already_out_qty,
                    SUM(X.already_received_qty) - SUM(X.already_out_qty) AS available_qty
                FROM packing_received_balance_sum AS X
                GROUP BY 
                    X.tm_id,
                    X.work_order_no,
                    X.quality_id,
                    X.style_id,
                    X.size_id
                           

                           
                -- your big SQL goes here
            """, [prg_id, tm_id])
            rows = cursor.fetchall()

        # Build a map for available qty by size_id
        availability_map = {}
        for row in rows:
            size_id = row[4]  # size_id index
            available_qty = row[7]  # available_qty index
            availability_map[size_id] = available_qty

        # Combine both datasets
        result = []
        for item in program_details:
            size_id = item['size_id']
            result.append({
                'size_id': size_id,
                'size_name': size_map.get(size_id, 'Unknown'),
                'box': item.get('box'),
                'per_box': item.get('pcs_per_box'),
                'box_pcs': item.get('box_pcs'),
                'loose_pcs': item.get('loose_pcs'),
                'seconds_pcs': item.get('seconds_pcs'),
                'shortage_pcs': item.get('shortage_pcs'),
                'available_qty': availability_map.get(size_id, 0)
            })

        return JsonResponse(result, safe=False)

    except Exception as e:
        print(f"❌ Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def get_packing_delivery_update_list(request):
    prg_id = request.POST.get('prg_id')
    tm_id = request.POST.get('tm_id')
    print('packing-ids:', prg_id, tm_id)

    if not prg_id or not tm_id:
        return JsonResponse({'error': 'Program ID and TM ID are required'}, status=400)

    try:
        prg_id_int = int(prg_id)

        # Get inward program details
        program_details = list(
            child_packing_inward_table.objects.filter(
                tm_id=tm_id, outward_id=prg_id_int, status=1
            ).values('size_id', 'box_pcs', 'pcs_per_box', 'box',
                     'loose_pcs', 'seconds_pcs', 'shortage_pcs')
        )

        if not program_details:
            return JsonResponse([], safe=False)

        size_ids = [p['size_id'] for p in program_details]
        size_map = {
            size.id: size.name for size in size_table.objects.filter(id__in=size_ids)
        }

        # ✅ Build tm_id → packing_id map only once
        tm_to_packing_id = {
            obj.id: obj.packing_id
            for obj in parent_lp_entry_table.objects.filter(packing_id=prg_id_int, status=1)
        }

        parent_ids = list(tm_to_packing_id.keys())

        # ✅ Get loose pcs values only once
        loose_pcs_value = (
            child_lp_entry_table.objects
            .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))  
        )

        # ✅ Build dictionary for loose delivery
        loose_pcs_qty = {}
        for item in loose_pcs_value:
            child_tm_id = item['tm_id']
            size_id = item['size_id']
            total_qty = item['total_qty'] or 0

            packing_id = tm_to_packing_id.get(child_tm_id)
            if packing_id:
                loose_pcs_qty[(packing_id, size_id)] = total_qty

        # ✅ Prepare final data
        data = []
        for item in program_details:
            size_id = item['size_id']

            total_out = (
                child_packing_outward_table.objects
                .filter(tm_id=prg_id_int, size_id=size_id, status=1)
                .aggregate(total_qty=Sum('quantity'))
            )
            total_out_pcs = total_out['total_qty'] or 0

            # Already received (excluding current tm_id)
            tx_program_details = (
                child_packing_inward_table.objects
                .filter(outward_id=prg_id_int, size_id=size_id, status=1)
                .exclude(tm_id=tm_id)
                .aggregate(
                    total_box_pcs=Sum('box_pcs'),
                    total_loose_pcs=Sum('loose_pcs'),
                    total_seconds_pcs=Sum('seconds_pcs'),
                    total_shortage_pcs=Sum('shortage_pcs'),
                )
            )

            box_pcs = tx_program_details['total_box_pcs'] or 0
            loose_pcs = tx_program_details['total_loose_pcs'] or 0
            seconds_pcs = tx_program_details['total_seconds_pcs'] or 0
            shortage_pcs = tx_program_details['total_shortage_pcs'] or 0
            total_inw_pcs = box_pcs + loose_pcs + seconds_pcs + shortage_pcs

            current_inward_qs = child_packing_inward_table.objects.filter(
                outward_id=prg_id_int, tm_id=tm_id, size_id=size_id, status=1
            )

            current_inward = current_inward_qs.aggregate(
                total_box=Sum('box'),
                total_box_pcs=Sum('box_pcs'),
                total_loose_pcs=Sum('loose_pcs'),
                total_seconds_pcs=Sum('seconds_pcs'),
                total_shortage_pcs=Sum('shortage_pcs'),
            )

            per_box = current_inward_qs.values_list('pcs_per_box', flat=True).first() or 0

            current_box = (current_inward['total_box'] or 0) * per_box
            current_box_pcs = current_inward['total_box_pcs'] or 0
            current_loose_pcs = current_inward['total_loose_pcs'] or 0
            current_seconds_pcs = current_inward['total_seconds_pcs'] or 0
            current_shortage_pcs = current_inward['total_shortage_pcs'] or 0

            total_current_inw = current_box + current_loose_pcs + current_seconds_pcs + current_shortage_pcs
            available_qty = total_out_pcs - total_current_inw

            data.append({
                'size_id': size_id,
                'size_name': size_map.get(size_id, 'Unknown'),
                'box': item['box'],
                'per_box': item['pcs_per_box'], 
                'box_pcs': item['box_pcs'],
                'loose_pcs': item['loose_pcs'],
                'seconds_pcs': item['seconds_pcs'],
                'shortage_pcs': item['shortage_pcs'],
                'already_rec': total_inw_pcs,
                'delivered_pcs': total_out_pcs,
                'available_pcs': available_qty,
                'loose_pcs_delivery': loose_pcs_qty.get((prg_id_int, size_id), 0)
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def get_stiching_delivery_update_list(request):
    prg_id = request.POST.get('prg_id')
    tm_id = request.POST.get('tm_id')
    print('packing-ids:', prg_id, tm_id)

    if not prg_id or not tm_id:
        return JsonResponse({'error': 'Program ID and TM ID are required'}, status=400)

    try:
        prg_id_int = int(prg_id)

        # Get inward program details
        program_details = list(
            child_packing_inward_table.objects.filter(
                tm_id=tm_id, outward_id=prg_id_int, status=1
            ).values('size_id', 'box_pcs', 'pcs_per_box', 'box',
                     'loose_pcs', 'seconds_pcs', 'shortage_pcs')
        )

        if not program_details:
            return JsonResponse([], safe=False)

        size_ids = [p['size_id'] for p in program_details]
        size_map = {
            size.id: size.name for size in size_table.objects.filter(id__in=size_ids)
        }

        # ✅ Build tm_id → packing_id map only once
        tm_to_packing_id = {
            obj.id: obj.packing_id
            for obj in parent_lp_entry_table.objects.filter(packing_id=prg_id_int, status=1)
        }

        parent_ids = list(tm_to_packing_id.keys())

        # ✅ Get loose pcs values only once
        loose_pcs_value = (
            child_lp_entry_table.objects
            .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
            .values('tm_id', 'size_id')
            .annotate(total_qty=Sum('quantity'))  
        )

        # ✅ Build dictionary for loose delivery
        loose_pcs_qty = {}
        for item in loose_pcs_value:
            child_tm_id = item['tm_id']
            size_id = item['size_id']
            total_qty = item['total_qty'] or 0

            packing_id = tm_to_packing_id.get(child_tm_id)
            if packing_id:
                loose_pcs_qty[(packing_id, size_id)] = total_qty

        # ✅ Prepare final data
        data = []
        for item in program_details:
            size_id = item['size_id']

            total_out = (
                child_stiching_outward_table.objects
                .filter(tm_id=prg_id_int, size_id=size_id, status=1)
                .aggregate(total_qty=Sum('quantity'))
            )
            total_out_pcs = total_out['total_qty'] or 0

            # Already received (excluding current tm_id)
            tx_program_details = (
                child_packing_inward_table.objects
                .filter(outward_id=prg_id_int, size_id=size_id, status=1)
                .exclude(tm_id=tm_id)
                .aggregate(
                    total_box_pcs=Sum('box_pcs'),
                    total_loose_pcs=Sum('loose_pcs'),
                    total_seconds_pcs=Sum('seconds_pcs'),
                    total_shortage_pcs=Sum('shortage_pcs'),
                )
            )

            box_pcs = tx_program_details['total_box_pcs'] or 0
            loose_pcs = tx_program_details['total_loose_pcs'] or 0
            seconds_pcs = tx_program_details['total_seconds_pcs'] or 0
            shortage_pcs = tx_program_details['total_shortage_pcs'] or 0
            total_inw_pcs = box_pcs + loose_pcs + seconds_pcs + shortage_pcs

            current_inward_qs = child_packing_inward_table.objects.filter(
                outward_id=prg_id_int, tm_id=tm_id, size_id=size_id, status=1
            )

            current_inward = current_inward_qs.aggregate(
                total_box=Sum('box'),
                total_box_pcs=Sum('box_pcs'),
                total_loose_pcs=Sum('loose_pcs'),
                total_seconds_pcs=Sum('seconds_pcs'),
                total_shortage_pcs=Sum('shortage_pcs'),
            )

            per_box = current_inward_qs.values_list('pcs_per_box', flat=True).first() or 0

            current_box = (current_inward['total_box'] or 0) * per_box
            current_box_pcs = current_inward['total_box_pcs'] or 0
            current_loose_pcs = current_inward['total_loose_pcs'] or 0
            current_seconds_pcs = current_inward['total_seconds_pcs'] or 0
            current_shortage_pcs = current_inward['total_shortage_pcs'] or 0

            total_current_inw = current_box + current_loose_pcs + current_seconds_pcs + current_shortage_pcs
            available_qty = total_out_pcs - total_current_inw

            data.append({
                'size_id': size_id,
                'size_name': size_map.get(size_id, 'Unknown'),
                'box': item['box'],
                'per_box': item['pcs_per_box'], 
                'box_pcs': item['box_pcs'],
                'loose_pcs': item['loose_pcs'],
                'seconds_pcs': item['seconds_pcs'],
                'shortage_pcs': item['shortage_pcs'],
                'already_rec': total_inw_pcs,
                'delivered_pcs': total_out_pcs,
                'available_pcs': available_qty,
                'loose_pcs_delivery': loose_pcs_qty.get((prg_id_int, size_id), 0)
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def get_packing_delivery_update_list_3_9(request):
    prg_id = request.POST.get('prg_id')
    tm_id = request.POST.get('tm_id')
    print('packing-ids:', prg_id, tm_id)

    if not prg_id or not tm_id:
        return JsonResponse({'error': 'Program ID and TM ID are required'}, status=400)

    try:
        # Get inward program details (multiple rows possible)
        program_details = list(
            child_packing_inward_table.objects.filter(
                tm_id=tm_id, outward_id=prg_id, status=1
            ).values('size_id', 'box_pcs', 'pcs_per_box', 'box',
                     'loose_pcs', 'seconds_pcs', 'shortage_pcs')
        )

        if not program_details:
            return JsonResponse([], safe=False)

        # Collect size_ids (and later color_ids if needed)
        size_ids = [p['size_id'] for p in program_details]

        # Map sizes
        size_map = {
            size.id: size.name for size in size_table.objects.filter(id__in=size_ids)
        }
        
        data = []
        for item in program_details:
            size_id = item['size_id']

            # ✅ Total outward qty for this size_id
            total_out = (
                child_packing_outward_table.objects
                .filter(tm_id=prg_id, size_id=size_id, status=1)
                .aggregate(total_qty=Sum('quantity'))
            )
            total_out_pcs = total_out['total_qty'] or 0


            # Step 1: Build tm_id to packing_id map
            tm_to_packing_id = {
                obj.id: obj.packing_id
                for obj in parent_lp_entry_table.objects.filter(packing_id__in=prg_id, status=1)
            }

            # Step 2: Get child entries
            parent_ids = list(tm_to_packing_id.keys())
            loose_pcs_value = (
                child_lp_entry_table.objects
                .filter(tm_id__in=parent_ids, size_id__in=size_ids, status=1)
                .values('tm_id', 'size_id')
                .annotate(total_qty=Sum('quantity'))  
            )
            print('lp-value:',loose_pcs_value)
            # Step 3: Build correct dictionary
            loose_pcs_qty = {}
            for item in loose_pcs_value:
                tm_id = item['tm_id']
                size_id = item['size_id']
                total_qty = item['total_qty'] or 0

                packing_id = tm_to_packing_id.get(tm_id)
                if packing_id:
                    loose_pcs_qty[(packing_id, size_id)] = total_qty





            # ✅ Already received (exclude current tm_id)
            tx_program_details = (
                child_packing_inward_table.objects
                .filter(outward_id=prg_id,tm_id=tm_id, size_id=size_id, status=1)
                .exclude(tm_id=tm_id)
                .aggregate(
                    total_box_pcs=Sum('box_pcs'),
                    total_loose_pcs=Sum('loose_pcs'),
                    total_seconds_pcs=Sum('seconds_pcs'),
                    total_shortage_pcs=Sum('shortage_pcs'),
                )
            )

            box_pcs = tx_program_details['total_box_pcs'] or 0
            loose_pcs = tx_program_details['total_loose_pcs'] or 0
            seconds_pcs = tx_program_details['total_seconds_pcs'] or 0
            shortage_pcs = tx_program_details['total_shortage_pcs'] or 0

            total_inw_pcs = box_pcs + loose_pcs + seconds_pcs + shortage_pcs

       
            from django.db.models import F

            current_inward_qs = child_packing_inward_table.objects.filter(
                outward_id=prg_id, tm_id=tm_id, size_id=size_id, status=1
            )

            current_inward = current_inward_qs.aggregate(
                total_box=Sum('box'),
                total_box_pcs=Sum('box_pcs'),
                total_loose_pcs=Sum('loose_pcs'),
                total_seconds_pcs=Sum('seconds_pcs'),
                total_shortage_pcs=Sum('shortage_pcs'),
            )

            per_box = current_inward_qs.values_list('pcs_per_box', flat=True).first() or 0


            # per_box = current_inward_qs.values_list('pcs_per_box', flat=True).first() or 0


            current_box = (current_inward['total_box'] or 0) * per_box
            current_box_pcs = current_inward['total_box_pcs'] or 0
            current_loose_pcs = current_inward['total_loose_pcs'] or 0
            current_seconds_pcs = current_inward['total_seconds_pcs'] or 0
            current_shortage_pcs = current_inward['total_shortage_pcs'] or 0

            total_current_inw = current_box + current_loose_pcs + current_seconds_pcs + current_shortage_pcs



            available_qty = total_out_pcs - total_current_inw
            data.append({
                'size_id': size_id,
                'size_name': size_map.get(size_id, 'Unknown'),
                'box': item['box'],
                'per_box': item['pcs_per_box'],
                'box_pcs': item['box_pcs'],
                'loose_pcs': item['loose_pcs'],
                'seconds_pcs': item['seconds_pcs'],
                'shortage_pcs': item['shortage_pcs'],
                'already_rec': total_inw_pcs,
                'delivered_pcs': total_out_pcs,
                'available_pcs':available_qty,
                'loose_pcs_delivery':loose_pcs_qty
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt
# def get_packing_delivery_update_list(request):
#     prg_id = request.POST.get('prg_id')
#     tm_id = request.POST.get('tm_id')  # 👈 Extract this too
#     print('packing-ids:',prg_id,tm_id)
#     if not prg_id or not tm_id:  
#         return JsonResponse({'error': 'Program ID and TM ID are required'}, status=400)

#     try:
      
 
#         program_details = child_packing_inward_table.objects.filter(
#             tm_id=tm_id,outward_id=prg_id ,status=1 # 👈 filter by tm_id, not just prg_id
#         ).values('size_id', 'box_pcs','pcs_per_box','box','loose_pcs','seconds_pcs','shortage_pcs')


#         total_out =(
#             child_packing_outward_table.objects
#             .filter(tm_id=prg_id,size_id=program_details['size_id'],color_id=program_details['color_id'], status=1)

#             .aggregate(
#                 total_qty=Sum('quantity'),
#             )
#         )

#         total_quantity = total_out['total_qty'] or 0

#         total_out_pcs = total_quantity



#         tx_program_details = (
#             child_packing_inward_table.objects
#             .filter(outward_id=prg_id,size_id=program_details['size_id'],color_id=program_details['color_id'], status=1)
#             .exclude(tm_id=tm_id)   # ✅ exclude same tm_id
#             .aggregate(
#                 total_box_pcs=Sum('box_pcs'),
#                 total_loose_pcs=Sum('loose_pcs'),
#                 total_seconds_pcs=Sum('seconds_pcs'),
#                 total_shortage_pcs=Sum('shortage_pcs'),
#             )
#         )

#         box_pcs = tx_program_details['total_box_pcs'] or 0
#         loose_pcs = tx_program_details['total_loose_pcs'] or 0
#         seconds_pcs = tx_program_details['total_seconds_pcs'] or 0
#         shortage_pcs = tx_program_details['total_shortage_pcs'] or 0

#         total_inw_pcs = box_pcs + loose_pcs + seconds_pcs + shortage_pcs



#         size_map = {
#             size.id: size.name for size in size_table.objects.filter(
#                 id__in=[p['size_id'] for p in program_details]
#             )
#         }

#         # color_map = {
#         #     color.id: color.name for color in color_table.objects.filter(
#         #         id__in=[p['color_id'] for p in program_details]
#         #     )
#         # }
 


#         data = [ 
#             {
#                 'size_id': item['size_id'],
#                 'size_name': size_map.get(item['size_id'], 'Unknown'),
#                 # 'color_id': item['color_id'],
#                 # 'color_name': color_map.get(item['color_id'], 'Unknown'),
#                 'box': item['box'],
#                 'per_box': item['pcs_per_box'],
#                 'box_pcs': item['box_pcs'],
#                 'loose_pcs': item['loose_pcs'],  
#                 'seconds_pcs': item['seconds_pcs'],
#                 'shortage_pcs': item['shortage_pcs'],
#                 'already_rec':total_inw_pcs,
#                 'delivered_pcs':total_out_pcs   
#             }
#             for item in program_details
#         ]

#         return JsonResponse(data, safe=False)

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)



# get_party_outward_lists 

from itertools import chain
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def get_existing_loose_pcs(request):
#     size_id = request.POST.get('size_id')

#     tm_id = request.POST.get('tm_id')

#     if not all([size_id, tm_id]):
#         return JsonResponse({'status': 'error', 'message': 'Missing params'})

#     try:
#         loose = child_packing_inward_loose_pcs_table.objects.filter(
#             size_id=size_id,tm_id=tm_id

#         ).values('quantity','color_id')

#         color = color_table.objects.filter(status=1,id=loose['color_id']).first()
#         if loose:
#             return JsonResponse({'status': 'ok', 'color_id': loose['color_id'],'quantity': loose['quantity'],'color_name':color.name})
#         else:
#             return JsonResponse({'status': 'ok', 'quantity': 0})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)})
@csrf_exempt
def get_existing_loose_pcs(request):
    size_id = request.POST.get('size_id')
    tm_id = request.POST.get('tm_id')

    if not all([size_id, tm_id]):
        return JsonResponse({'status': 'error', 'message': 'Missing params'})

    try:
        loose_qs = child_packing_inward_loose_pcs_table.objects.filter(
            size_id=size_id,
            tm_id=tm_id,status=1    
        ).values('quantity', 'color_id','size_id')

        data = []
        for entry in loose_qs:
            color = color_table.objects.filter(status=1, id=entry['color_id']).first()
            color_name = color.name if color else 'Unknown'
            data.append({
                'size_id': entry['size_id'],
                'color_id': entry['color_id'],
                'quantity': entry['quantity'],
                'color_name': color_name
            })

        return JsonResponse({'status': 'ok', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



@csrf_exempt 
def get_party_outward_lists(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    party_id = request.POST.get('party_id')
    print('party-id:', party_id)

    if not party_id:
        return JsonResponse({'error': 'Party ID is required'}, status=400)

    try:
        # Packing outward

        packing_outward = parent_packing_outward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity')

        for p in packing_outward:
            p['type'] = 'P' 

        # Stitching outward 

        stitching_outward = parent_stiching_outward_table.objects.filter(
            party_id=party_id, is_packing=1, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity')

        for s in stitching_outward:
            s['type'] = 'SP'


        packing_inward = parent_packing_inward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'inward_no', 'work_order_no')



        # Combine both lists
        combined_outward = list(chain(packing_outward, stitching_outward))
        print('details:',combined_outward) 
        if not combined_outward:
            return JsonResponse({'error': 'Outward not found for the given party ID'}, status=404)

        return JsonResponse({'outward': combined_outward})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 



@csrf_exempt 
def get_party_outward_available_lists(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    party_id = request.POST.get('party_id')
    print('party-id:', party_id)

    if not party_id:
        return JsonResponse({'error': 'Party ID is required'}, status=400)

    try:
        # Packing outward

        packing_outward = parent_packing_outward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity')

        for p in packing_outward:
            p['type'] = 'P' 

        # Stitching outward 

        stitching_outward = parent_stiching_outward_table.objects.filter(
            party_id=party_id, is_packing=1, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity')

        for s in stitching_outward:
            s['type'] = 'SP'


        packing_inward = parent_packing_inward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'inward_no', 'work_order_no')



        # Combine both lists
        combined_outward = list(chain(packing_outward, stitching_outward))
        print('details:',combined_outward) 
        if not combined_outward:
            return JsonResponse({'error': 'Outward not found for the given party ID'}, status=404)

        return JsonResponse({'outward': combined_outward})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 


# @csrf_exempt
# def get_party_outward_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=400)

#     party_id = request.POST.get('party_id')
#     print('party-id:', party_id)

#     if not party_id:
#         return JsonResponse({'error': 'Party ID is required'}, status=400)

#     try:

#         # program_value = get_object_or_404(parent_packing_outward_table, id=party_id)

#         # First: Try from Packing
#         outward = parent_packing_outward_table.objects.filter(party_id=party_id,status=1).values(
#             'id', 'outward_no', 'work_order_no', 'total_quantity'
#         )

#         if outward:
#             outward['type'] = 'P'

#         else:
#             # Second: Try from Stitching for Packing
#             outward = parent_stiching_outward_table.objects.filter(party_id=party_id, is_packing=1,status=1).values(
#                 'id', 'outward_no', 'work_order_no', 'total_quantity'
#             )


#             if outward:
#                 outward['type'] = 'SP'
#             else:
#                 return JsonResponse({'error': 'Outward not found for the given party ID'}, status=404)

#         # ✅ Return Single Outward
#         response_data = {
#             'outward': {
#                 'id': outward['id'],
#                 'outward_no': outward['outward_no'],
#                 'work_order_no': outward['work_order_no'],
#                 'total_quantity': outward['total_quantity'],
#                 'type': outward['type'],
#             }
#         }
 
#         return JsonResponse(response_data)


#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

@csrf_exempt
def get_packing_outward_list(request):
    if request.method == 'POST':
        # Accept prg_ids as a list from POST
        prg_ids = request.POST.getlist('prg_ids[]')
        print('Incoming prg_ids:', prg_ids)

        if not prg_ids:
            return JsonResponse({'error': 'Program ID(s) required'}, status=400)

        try:
            prg_ids = [int(pid) for pid in prg_ids if str(pid).isdigit()]
            if not prg_ids:
                return JsonResponse({'error': 'Invalid Program ID(s) provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error parsing Program IDs: {str(e)}'}, status=400)

        try:
            # Fetch all program records
            programs = parent_packing_outward_table.objects.filter(id__in=prg_ids)

            if programs.count() != len(prg_ids):
                return JsonResponse({'error': 'Some Program IDs not found'}, status=404)

            # Check that all have the same quality_id and style_id
            quality_ids = set(p.quality_id for p in programs)
            style_ids = set(p.style_id for p in programs)

            if len(quality_ids) > 1 or len(style_ids) > 1:
                return JsonResponse({
                    'error': 'Selected outwards have different Quality or Style, cannot load together.'
                }, status=400)

            # Since all same, pick first for details
            program_value = programs.first()
            party = get_object_or_404(party_table, id=program_value.party_id)
            quality = get_object_or_404(quality_table, id=program_value.quality_id)
            style = get_object_or_404(style_table, id=program_value.style_id)

            quality_prg = quality_program_table.objects.filter( 
                status=1, quality_id=quality.id, style_id=style.id
            ).first()

            sub_quality_map = {}
            if quality_prg:
                sub_quality_prg = sub_quality_program_table.objects.filter(
                    status=1, tm_id=quality_prg.id
                ).values('size_id', 'per_box')
                sub_quality_map = {int(sq['size_id']): sq['per_box'] for sq in sub_quality_prg}

            # Aggregate child packing outward data from all selected programs
            tx_prg_list = child_packing_outward_table.objects.filter(tm_id__in=prg_ids)

            size_ids = set()
            for tx_prg in tx_prg_list:
                raw_value = tx_prg.size_id
                if isinstance(raw_value, str):
                    size_ids.update(int(sid.strip()) for sid in raw_value.split(',') if sid.strip().isdigit())
                elif isinstance(raw_value, int):
                    size_ids.add(raw_value)

            size_qs = size_table.objects.filter(id__in=size_ids)
            size_id_list = [
                {'id': s.id, 'name': s.name, 'per_box': sub_quality_map.get(s.id, 0)}
                for s in size_qs
            ]

            color_ids = set()
            for tx_prg in tx_prg_list:
                raw_value = tx_prg.color_id
                if isinstance(raw_value, str):
                    color_ids.update(int(cid.strip()) for cid in raw_value.split(',') if cid.strip().isdigit())
                elif isinstance(raw_value, int):
                    color_ids.add(raw_value)

            color_qs = color_table.objects.filter(id__in=color_ids)
            color_id_list = [{'id': c.id, 'name': c.name} for c in color_qs]

            fabric_qs = fabric_program_table.objects.filter(id=program_value.fabric_id)
            fabric_id_list = [{'id': f.id, 'name': f.name} for f in fabric_qs]

            response_data = {
                'quality': {'id': quality.id, 'name': quality.name},
                'style': {'id': style.id, 'name': style.name},
                'party': {'id': party.id, 'name': party.name},
                'sizes': size_id_list,
                'colors': color_id_list,
                'fabrics': fabric_id_list,
                'items': list(tx_prg_list.values()),  # optionally return raw child details for frontend processing
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)





@csrf_exempt
def get_stiching_packing_delivery_list(request): 
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    # Get list of program IDs from form data
    prg_id_list = request.POST.getlist('prg_ids[]')
    print('Received prg_ids:', prg_id_list)

    if not prg_id_list:
        return JsonResponse({'error': 'Program IDs are required'}, status=400)

    # Convert all to integers safely
    try:
        prg_ids = [int(pid) for pid in prg_id_list if pid.strip().isdigit()]
    except ValueError:
        return JsonResponse({'error': 'Invalid Program IDs'}, status=400) 

    if not prg_ids:
        return JsonResponse({'error': 'No valid Program IDs provided'}, status=400)

    try:
        # For now, use the first valid ID (adjust if you need to support multiple)
        program_value = get_object_or_404(parent_stiching_outward_table, id=prg_ids[0], is_packing=1)
        party = get_object_or_404(party_table, id=program_value.party_id)
        quality = get_object_or_404(quality_table, id=program_value.quality_id)
        style = get_object_or_404(style_table, id=program_value.style_id)
        parent_fabric_id = program_value.fabric_id

        # Fetch all child records for all program IDs
        tx_prg_list = child_stiching_outward_table.objects.filter(tm_id__in=prg_ids)

        # Parse size IDs
        size_ids = set()
        for tx_prg in tx_prg_list:
            raw_value = tx_prg.size_id
            if isinstance(raw_value, str):
                size_ids.update(int(sid.strip()) for sid in raw_value.split(',') if sid.strip().isdigit())
            elif isinstance(raw_value, int):
                size_ids.add(raw_value)

        size_qs = size_table.objects.filter(id__in=size_ids)
        size_id_list = [{'id': s.id, 'name': s.name} for s in size_qs]

        # Parse color IDs
        color_ids = set()
        for tx_prg in tx_prg_list:
            raw_value = tx_prg.color_id
            if isinstance(raw_value, str):
                color_ids.update(int(cid.strip()) for cid in raw_value.split(',') if cid.strip().isdigit())
            elif isinstance(raw_value, int):
                color_ids.add(raw_value)

        color_qs = color_table.objects.filter(id__in=color_ids)
        color_id_list = [{'id': c.id, 'name': c.name} for c in color_qs]

        # Get fabric data
        fabric_qs = fabric_program_table.objects.filter(id=parent_fabric_id)
        fabric_id_list = [{'id': f.id, 'name': f.name} for f in fabric_qs]

        # Construct response
        response_data = {
            'quality': {'id': quality.id, 'name': quality.name},
            'style': {'id': style.id, 'name': style.name},
            'party': {'id': party.id, 'name': party.name},
            'sizes': size_id_list,
            'colors': color_id_list,
            'fabrics': fabric_id_list,
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)






@csrf_exempt
def validate_program_style_quality(request):
    if request.method == 'POST':
        try:
            programs = json.loads(request.POST.get('programs', '[]'))
            # programs is a list of dicts with 'id' and 'type'
            print('Programs:', programs)
        except Exception as e:
            return JsonResponse({'status': False, 'message': 'Invalid input data'})

        if not programs:
            return JsonResponse({'status': False, 'message': 'No programs selected'})

        # Separate IDs by type
        packing_ids = [p['id'] for p in programs if p['type'] == 'P']
        stitching_ids = [p['id'] for p in programs if p['type'] == 'SP']

        all_programs = []

        if packing_ids:
            packing_programs = parent_packing_outward_table.objects.filter(id__in=packing_ids)
            all_programs.extend(list(packing_programs))

        if stitching_ids:
            stitching_programs = parent_stiching_outward_table.objects.filter(id__in=stitching_ids)
            all_programs.extend(list(stitching_programs))

        found_ids = {p.id for p in all_programs}
        missing_ids = set(p['id'] for p in programs) - found_ids

        if missing_ids:
            return JsonResponse({
                'status': False,
                'message': f"Some programs not found: {', '.join(map(str, missing_ids))}"
            })

        # If only one program, no need to check consistency
        if len(all_programs) == 1:
            p = all_programs[0]
            return JsonResponse({
                'status': True,
                'style_id': p.style_id,
                'quality_id': p.quality_id,
                'inward_type': getattr(p, 'type', 'P')
            })

        # For multiple, check consistency
        style_ids = set(p.style_id for p in all_programs)
        quality_ids = set(p.quality_id for p in all_programs)
        types = set(getattr(p, 'type', 'P') for p in all_programs) 

        if len(style_ids) > 1 or len(quality_ids) > 1:
            return JsonResponse({
                'status': False,
                'message': 'Selected programs have different Style or Quality. Cannot proceed.'
            })

        if len(types) > 1:
            return JsonResponse({
                'status': False,
                'message': 'Selected programs have mixed types (P / SP). Please select same type.'
            })

        return JsonResponse({
            'status': True,
            'style_id': list(style_ids)[0],
            'quality_id': list(quality_ids)[0],
            'inward_type': list(types)[0]
        })

    return JsonResponse({'status': False, 'message': 'Invalid request method'})



@csrf_exempt
def validate_program_style_quality_test2(request):
    if request.method == 'POST':
        try:
            prg_ids = list(map(int, json.loads(request.POST.get('prg_ids', '[]'))))
            print('outId:', prg_ids)
        except:
            return JsonResponse({'status': False, 'message': 'Invalid input data'})

        if not prg_ids:
            return JsonResponse({'status': False, 'message': 'No programs selected'})

        packing_programs = parent_packing_outward_table.objects.filter(id__in=prg_ids)
        stiching_programs = parent_stiching_outward_table.objects.filter(id__in=prg_ids)

        all_programs = list(packing_programs) + list(stiching_programs)

        found_ids = {p.id for p in all_programs}
        missing_ids = set(prg_ids) - found_ids

        # if missing_ids: 
        #     return JsonResponse({ 
        #         'status': False,
        #         'message': f'Some programs not found: {', '.join(map(str, missing_ids))}'
        #     })


        if missing_ids:   
            return JsonResponse({
                'status': False,
                'message': f"Some programs not found: {', '.join(map(str, missing_ids))}"
            })



        style_ids = set(p.style_id for p in all_programs)
        quality_ids = set(p.quality_id for p in all_programs)
        types = set(getattr(p, 'type', 'P') for p in all_programs)

        if len(style_ids) > 1 or len(quality_ids) > 1:
            return JsonResponse({
                'status': False,
                'message': 'Selected programs have different Style or Quality. Cannot proceed.'
            })

        if len(types) > 1:
            return JsonResponse({
                'status': False,
                'message': 'Selected programs have mixed types (P / SP). Please select same type.'
            })

        return JsonResponse({
            'status': True,
            'style_id': list(style_ids)[0],
            'quality_id': list(quality_ids)[0],
            'inward_type': list(types)[0]
        })

    return JsonResponse({'status': False, 'message': 'Invalid request method'})



@csrf_exempt
def insert_packing_received(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try: 
            # Extracting Data from Request  
            prg_id = request.POST.get('prg_id')
            fabric_id = request.POST.get('fab_id')
            print('fab-id:',fabric_id)

            remarks = request.POST.get('remarks')  
            deliver_from = request.POST.get('delivery_from') 
            print('deliver-from:',deliver_from)
            quality_id = request.POST.get('quality_id') 
            style_id = request.POST.get('style_id')  
            dc_no = request.POST.get('dc_no')
            dc_date = request.POST.get('dc_date')
            received_date = request.POST.get('inward_date')
            received_date = request.POST.get('inward_date')
            received_data = json.loads(request.POST.get('cutting_data', '[]'))
            loose_pcs_data = json.loads(request.POST.get('loose_pcs_data', '[]'))
            work_order_no = request.POST.get('work_order_no') 
            party_id = request.POST.get('party_id') 
            print('Chemical Data:', received_data)  

            def clean_amount(amount): 
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()  

 
            inward_no = generate_inward_num_series()
            
            # Create Parent Entry (gf_inward_table)
            material_request = parent_packing_inward_table.objects.create(
                inward_no = inward_no.upper(),
                inward_date=received_date, 
                dc_no =dc_no,
                dc_date = dc_date,
                outward_id = prg_id,
                party_id = party_id,
                delivery_from = deliver_from, 
                # prg_quantity = 0,
                fabric_id = fabric_id,
                work_order_no = work_order_no,
                quality_id=quality_id, 
                style_id=style_id,
                company_id=company_id,
                cfyear = 2025, 
              
                total_box=request.POST.get('total_box'),
                total_pcs=request.POST.get('delivered_pcs'),
                per_box=request.POST.get('per_box',0),
                loose_pcs=request.POST.get('loose_pcs',0),
                seconds_pcs=request.POST.get('seconds_pcs',0),
                shortage_pcs=request.POST.get('shortage_pcs',0),
                
                # box_pcs=request.POST.get('box_pcs',0),
              
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            ) 
            print('m-req:',material_request)

            po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for cutting in received_data:
                print("Processing cutting Data:", cutting)
 
                po_id = cutting.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later

                sub_entry = child_packing_inward_table.objects.create(
                    work_order_no = work_order_no,
                    tm_id=material_request.id,  
                    outward_id = prg_id,
                    size_id=cutting.get('size_id'),  
                    box=cutting.get('box'),
                    pcs_per_box=cutting.get('pcs_per_box'),
                    box_pcs=cutting.get('box_pcs'),
                    loose_pcs=cutting.get('loose_pcs'),
                    seconds_pcs=cutting.get('seconds_pcs'),
                    shortage_pcs=cutting.get('shortage'), 
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025, 
                # ) 

                )
                print('sub:',sub_entry)



            # for pcs in loose_pcs_data:
            #     print("Processing pcs Data:", pcs)
 



            #     sub_loose_pcs = child_packing_inward_loose_pcs_table.objects.create(
            #         work_order_no = work_order_no,
            #         tm_id=material_request.id,  
            #         outward_id = prg_id,
            #         size_id=pcs.get('size_id'),  
            #         quantity=pcs.get('quantity'),
            #         color_id=pcs.get('color_id'),
            #         party_id=party_id,
                   
            #         created_by=user_id,
            #         created_on=timezone.now(),
            #         company_id=company_id,
            #         cfyear=2025, 
            #     # ) 

            #     )
            #     print('sub_pcs:',sub_loose_pcs)

            for key, pcs in loose_pcs_data.items():
                print("Processing pcs Data:", pcs)

                sub_loose_pcs = child_packing_inward_loose_pcs_table.objects.create(
                    work_order_no=work_order_no,
                    tm_id=material_request.id,
                    outward_id=prg_id,
                    size_id=pcs.get('size_id'),
                    quantity=pcs.get('quantity'),
                    color_id=pcs.get('color_id'),
                    # party_id=party_id,
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,
                )
                print('sub_pcs:', sub_loose_pcs)



            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'packing_received/add_packing_received.html')

 

from django.db import connection

 
def packing_received_edit(request):
    try:  
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'packing_received/update_packing_received.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'packing_received/update_packing_received.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_packing_inward_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            size_id = request.POST.get('size_id')  # Adjust as per your input structure
            box = request.POST.get('box')  # Adjust as per your input structure
            wt = request.POST.get('wt')  # Adjust as per your input structure
           
            # Ensure valid data before saving
            if size_id :
                material_instance = child_packing_inward_table.objects.create(
                    tm_id=material_id,
                    size_id=size_id, 
                    box=box,
                    wt=wt,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'packing_received/update_packing_received.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = parent_packing_inward_table.objects.filter(id=material_id).first()
    
        # Fetch active products and UOM
        # party = party_table.objects.filter(status=1)
        

        party = party_table.objects.filter(status=1).filter(is_stiching=1) | party_table.objects.filter(status=1).filter(is_ironing=1)

        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        packing_delivery = parent_packing_outward_table.objects.filter(status=1)
        from itertools import chain

        packing_outward = parent_packing_outward_table.objects.filter(status=1).values(
            'id', 'outward_no', 'work_order_no', 'total_quantity'
        )
        for p in packing_outward:
            p['type'] = 'P'  # Packing 

        stitching_outward = parent_stiching_outward_table.objects.filter(status=1, is_packing=1).values(
            'id', 'outward_no', 'work_order_no', 'total_quantity'
        )
        for s in stitching_outward:
            s['type'] = 'SP'  # Stitching for Packing

        combined_outward = list(chain(packing_outward, stitching_outward))
        # ✅ Lot-wise available quantity query
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    inward.lot_no,
                    inward.total_wt AS inw_wt,
                    COALESCE(inward.total_wt, 0) - COALESCE(cutting.total_cutting_wt, 0) AS available_wt
                FROM (
                    SELECT 
                        tx.lot_no, 
                        MAX(tm.total_wt) AS total_wt
                    FROM tx_dyed_fab_inward AS tx
                    LEFT JOIN tm_dyed_fab_inward AS tm ON tx.tm_id = tm.id
                    WHERE tx.status = 1
                    GROUP BY tx.lot_no
                ) AS inward
                LEFT JOIN (
                    SELECT 
                        lot_no, 
                        SUM(wt) AS total_cutting_wt
                    FROM tx_cutting_entry
                    WHERE status = 1
                    GROUP BY lot_no
                ) AS cutting ON inward.lot_no = cutting.lot_no
            """)
            lot_rows = cursor.fetchall()

        # ✅ Filter only lots with available weight > 0
        lot_no = [
            {'lot_no': row[0], 'total_wt': row[1], 'available_wt': row[2]}
            for row in lot_rows if row[2] > 0
        ]
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance, 
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            'size':size,
            'quality':quality,
            'style':style,
            'lot_no':lot_no, 
            'packing_delivery':packing_delivery,
            'combined_outward':combined_outward,
            
        }
        return render(request, 'packing_received/update_packing_received.html', context)

    except Exception as e:
        return render(request, 'packing_received/update_packing_received.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


def packing_received_detail_list(request):
    tm_id = request.POST.get('id')

    # Fetch child data 
    child_qs = child_packing_inward_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')

    if child_qs.exists():
        # Calculate total quantity and total weight from child table
        total_box = child_qs.aggregate(Sum('box'))['box__sum'] or 0

        # Fetch master cutting entry
        parent_data = parent_packing_inward_table.objects.filter(id=tm_id).first()

        if not parent_data:
            return JsonResponse({'message': 'error', 'error_message': 'Cutting Entry not found in parent table'})

        # Convert child queryset to list
        child_data = list(child_qs.values())

        # Format child table data
        formatted_data = [
            {
                'action': f'<button type="button" onclick="packing_received_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '
                          f'<button type="button" onclick="packing_received_delete(\'{item["id"]}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>',
                'id': index + 1,
                'size': getSupplier(size_table, item['size_id']),
                'box': item['box'] if item['box'] else '-',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            }
            for index, item in enumerate(child_data)
        ]

        # Prepare master values for summary
        summary_data = {
            'total_box': total_box,
            'delivered_pcs': parent_data.total_pcs,
            'loose_pcs': parent_data.loose_pcs,
            'seconds_pcs': parent_data.seconds_pcs,
            'shortage_pcs': parent_data.shortage_pcs,
            'balance_pcs': parent_data.balance_pcs,
            'per_box': parent_data.per_box,
       
        }

        return JsonResponse({
            'data': formatted_data,
            **summary_data
        })

    else:
        return JsonResponse({'message': 'error', 'error_message': 'No cutting program data found for this TM ID'})




def edit_packing_received(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = child_packing_inward_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  



def packing_received_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting
            child_packing_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except child_packing_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'}) 
    

 

def delete_packing_received(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            parent_packing_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)

            child_packing_inward_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except parent_packing_inward_table  & child_packing_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})




def check_existing_packing_received(request): 
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        size_id = request.POST.get('size_id')

        # Check if a record with the same tm_id, size_id, and color_id exists
        existing_entry = child_packing_inward_table.objects.filter(
            tm_id=tm_id, size_id=size_id
        ).first()

        if existing_entry:
            return JsonResponse({'exists': True, 'existing_id': existing_entry.id})
        else:
            return JsonResponse({'exists': False})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_packing_received_bk_datatable(request):
    if request.method == 'POST':
        master_id = request.POST.get('id')  # The ID of the row (if updating)
        tm_id = request.POST.get('tm_id')   # The transaction master ID
        size_id = request.POST.get('size_id')
        box = request.POST.get('box')
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        fabric_id = request.POST.get('fabric_id')

        print('tm-id:', tm_id) 

        # Validate required fields
        if not tm_id or not size_id or not box:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Check if the same tm_id, size_id, and color_id already exist
            existing_item = child_packing_inward_table.objects.filter(
                tm_id=tm_id,
                size_id=size_id,
            ).first()

            if existing_item:
                # Update existing entry
                existing_item.box = box
             
                existing_item.save()
                
                updated_totals = update_values(tm_id)  # Update totals
                return JsonResponse({'success': True, 'updated': True, **updated_totals})

            else:
                # Create a new row if no existing entry
                child_item = child_packing_inward_table.objects.create(
                    tm_id=tm_id,
                    size_id=size_id,
                    box=box,
                    status=1, 
                    is_active=1,
                    company_id=company_id,
                    cfyear = 2025,
                    
                )
                updated_totals = update_values(tm_id)  # Update totals
                return JsonResponse({'success': True, 'created': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


 

def update_values(tm):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given tm
        tx = child_packing_inward_table.objects.filter(tm_id=tm, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_box = tx.aggregate(Sum('box'))['box__sum'] or Decimal('0')

        # Update values in parent_po_table 
        parent_packing_inward_table.objects.filter(id=tm).update(
            total_box=total_box,
 
        )

        # Return updated values for frontend update
        return {
            'total_box': total_box,
   
        }

    except Exception as e: 
        return {'error': str(e)}





from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
import base64
import json


# @csrf_exempt
# def packing_received_print(request):
#     po_id = request.GET.get('k') 
#     if not po_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     try:
#         order_id = int(base64.b64decode(po_id))  # Decode the order ID from base64
#         print('ord-id:', order_id)
#     except Exception:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)

#     try:
#         # Fetching the main order details
#         total_values = get_object_or_404(parent_packing_inward_table, id=order_id)
#         print('quality', total_values.quality_id)

#         # Fetching child records and related objects
#         prg_details = child_packing_inward_table.objects.filter(tm_id=order_id).select_related(
#             'size', 'color', 'fabric_id', 'quality_id', 'style_id'
#         ).values('id', 'box', 'size_id', 'loose_pcs', 'seconds_pcs', 'shortage_pcs')

#         # Prepare lists and counters for aggregation
#         combined_details = []
#         total_quantity = Decimal('0.000')

#         # Iterate through prg_details and calculate the total pcs dynamically
#         # for prg_detail in prg_details:
#         #     product = prg_detail.get('fabric_id')
#         #     quality = prg_detail.get('quality_id')
#         #     style = prg_detail.get('style_id')
#         #     size = prg_detail.get('size')

#         #     # Ensure no None values for calculation
#         #     box = prg_detail.get('box', 0) or 0
#         #     loose_pcs = prg_detail.get('loose_pcs', 0) or 0
#         #     seconds_pcs = prg_detail.get('seconds_pcs', 0) or 0
#         #     shortage_pcs = prg_detail.get('shortage_pcs', 0) or 0

#         #     # Calculate total pcs
#         #     total_pcs = (box * 12) + loose_pcs + seconds_pcs + shortage_pcs

#         #     # Add total quantity to the overall total
#         #     total_quantity += total_pcs
#         #     quality_name = quality_table.objects.filter(status=1, id=quality).first()
#         #     style_name = style_table.objects.filter(status=1, id=style).first()
#         #     size_name = size_table.objects.filter(status=1, id=size).first()

#         #     # Add details for the row
#         #     combined_details.append({
#         #         'style': style_name.name if style_name else 'Unknown',
#         #         'quality': quality_name.name if quality_name else 'Unknown',
#         #         'size': size_name.name if size_name else 'Unknown',
#         #         'box': box,
#         #         'loose_pcs': loose_pcs,
#         #         'seconds_pcs': seconds_pcs,
#         #         'shortage_pcs': shortage_pcs,
#         #         'total_pcs': total_pcs,
#         #     })


#         # Iterate through prg_details and calculate the total pcs dynamically
#         for prg_detail in prg_details:
#             product = prg_detail.get('fabric_id')
#             quality = prg_detail.get('quality_id')
#             style = prg_detail.get('style_id')
#             size = prg_detail.get('size')

#             # Ensure no None values for calculation
#             box = prg_detail.get('box', 0) or 0
#             loose_pcs = prg_detail.get('loose_pcs', 0) or 0
#             seconds_pcs = prg_detail.get('seconds_pcs', 0) or 0
#             shortage_pcs = prg_detail.get('shortage_pcs', 0) or 0

#             # Calculate total pcs
#             total_pcs = (box * 12) + loose_pcs + seconds_pcs + shortage_pcs

#             # Add total quantity to the overall total
#             total_quantity += total_pcs
#             quality_name = quality_table.objects.filter(status=1, id=quality).first()
#             style_name = style_table.objects.filter(status=1, id=style).first()
#             size_name = size_table.objects.filter(status=1, id=size).first()

#             print(f"Size: {size_name.name if size_name else 'Unknown'}, Box: {box}, Total pcs: {total_pcs}")

#             # Add details for the row
#             combined_details.append({
#                 'style': style_name.name if style_name else 'Unknown',
#                 'quality': quality_name.name if quality_name else 'Unknown',
#                 'size': size_name.name if size_name else 'Unknown',
#                 'box': box,
#                 'loose_pcs': loose_pcs,
#                 'seconds_pcs': seconds_pcs,
#                 'shortage_pcs': shortage_pcs,
#                 'total_pcs': total_pcs,
#             })

#         # Print combined details to see if size is populated
#         print("Combined Details:", combined_details)


#         # Collect unique size values in sorted order
#         sizes = sorted(set(item['size'] for item in combined_details))

#         # Group data by size
#         # group_map = defaultdict(lambda: {'size_data': {}})
#         # for item in combined_details:
#         #     key = item['size']  # Group by size only, or you can include other factors like fabric or quality
#         #     group_map[key]['size_data'][item['size']] = {
#         #         'box': item['box'],
#         #         'loose_pcs': item['loose_pcs'],
#         #         'seconds_pcs': item['seconds_pcs'],
#         #         'shortage_pcs': item['shortage_pcs'],
#         #         'total_pcs': item['total_pcs'],
#         #     }

#         # Group data by size (You can also group by other keys like 'fabric' if needed)
#         group_map = defaultdict(lambda: {'size_data': {}})
#         for item in combined_details:
#             key = item['size']  # Group by size
#             group_map[key]['size_data'][item['size']] = {
#                 'box': item['box'],
#                 'loose_pcs': item['loose_pcs'],
#                 'seconds_pcs': item['seconds_pcs'],
#                 'shortage_pcs': item['shortage_pcs'],
#                 'total_pcs': item['total_pcs'],
#             }

#         # Debug print for group_map to see the structure
#         print("Group Map:", dict(group_map))




#         # Prepare grouped data for rendering
#         grouped_data = []
#         for val in group_map.values():  
#             val['size_data_list'] = [ 
#                 val['size_data'].get(size, {'box': 0, 'loose_pcs': 0, 'seconds_pcs': 0, 'shortage_pcs': 0, 'total_pcs': 0}) for size in sizes
#             ]
#             val['row_total'] = sum(entry['total_pcs'] for entry in val['size_data_list'] if entry['total_pcs'])
#             grouped_data.append(val)

#         # Calculate the grand total
#         grand_total = sum(val['row_total'] for val in grouped_data)

#         # Size-wise total calculation
#         size_totals = {size: {'quantity': 0} for size in sizes}
#         for item in combined_details:
#             size_totals[item['size']]['quantity'] += item['total_pcs']

#         size_totals_list = [size_totals[size] for size in sizes]
#         total_columns = 2 + len(sizes) * 2  # Box and Loose Pcs, plus columns for each size

#         # Collecting the context for the template
#         context = {
#             'total_values': total_values,
#             'sizes': sizes, 
#             'grouped_data': grouped_data,
#             'dia_totals_list': size_totals_list,
#             'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
#             'total_columns': total_columns,
#             'company': company_table.objects.filter(status=1).first(),
#             'style': style_name.name if style_name else 'Unknown',
#             'quality': quality_name.name if quality_name else 'Unknown',
#             'size': size_name.name if size_name else 'Unknown',
#             'grand_total': grand_total,
#             'combined_details': combined_details  
#         }

#         return render(request, 'packing_received/packing_received_print.html', context)

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)




from collections import defaultdict
import base64
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Assumed models
# from yourapp.models import parent_packing_inward_table, child_packing_inward_table, party_table, fabric_program_table, fabric_table, quality_table, style_table, size_table, company_table



@csrf_exempt
def packing_received_print(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id).decode('utf-8'))
    except (ValueError, base64.binascii.Error):
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_packing_inward_table, id=order_id)
    party = get_object_or_404(party_table, id=total_values.party_id)

    try:
        product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        quality = get_object_or_404(quality_table, id=total_values.quality_id)
        style = get_object_or_404(style_table, id=total_values.style_id)
    except (fabric_program_table.DoesNotExist, fabric_table.DoesNotExist,
            quality_table.DoesNotExist, style_table.DoesNotExist):
        return JsonResponse({'error': 'Related master data not found'}, status=404)

    prg_details = child_packing_inward_table.objects.filter(
        tm_id=order_id, status=1
    ).values(
        'size_id'
    ).annotate(
        total_box=Sum('box'),
        total_loose_pcs=Sum('loose_pcs'),
        box_pcs=Sum('box_pcs'),
        pcs_per_box=Max('pcs_per_box'),  # 👈 safer than Sum
        total_seconds_pcs=Sum('seconds_pcs'),
        total_shortage_pcs=Sum('shortage_pcs')
    ).order_by('size_id')

    combined_details = []

    for prg_detail in prg_details:
        size = get_object_or_404(size_table, id=prg_detail['size_id'])

        quantity = prg_detail['total_box'] or 0
        box_pcs = prg_detail['box_pcs'] or 0
        pcs_per_box = prg_detail['pcs_per_box'] or 0
        loose_pcs = prg_detail['total_loose_pcs'] or 0
        seconds_pcs = prg_detail['total_seconds_pcs'] or 0
        shortage_pcs = prg_detail['total_shortage_pcs'] or 0

        # ✅ Correct formula
        total_pcs = (quantity * pcs_per_box) + loose_pcs +seconds_pcs +shortage_pcs

        combined_details.append({
            'size': size.name,
            'quantity': quantity,
            'box_pcs': box_pcs,
            'pcs_per_box': pcs_per_box,
            'loose_pcs': loose_pcs,
            'seconds_pcs': seconds_pcs,
            'shortage_pcs': shortage_pcs,
            'total_pcs': total_pcs,
        })

    # ✅ Totals (outside loop)
    total_boxes = sum(c['quantity'] for c in combined_details)
    total_box_pcs = sum(c['box_pcs'] for c in combined_details)
    loose_pcs_total = sum(c['loose_pcs'] for c in combined_details)
    seconds_pcs_total = sum(c['seconds_pcs'] for c in combined_details)
    shortage_pcs_total = sum(c['shortage_pcs'] for c in combined_details)
    grand_total_pcs = sum(c['total_pcs'] for c in combined_details)

    context = {
        'total_values': total_values,
        'party_name': party.name,
        'gstin': party.gstin,
        'mobile': party.mobile,
        'quality': quality.name,
        'style': style.name,
        'combined_details': combined_details,
        "total_boxes": total_boxes,
        "total_box_pcs": total_box_pcs,
        "loose_pcs_total": loose_pcs_total,
        "seconds_pcs_total": seconds_pcs_total,
        "shortage_pcs_total": shortage_pcs_total,
        "grand_total_pcs": grand_total_pcs,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'company': company_table.objects.filter(status=1).first(),
    }

    return render(request, 'packing_received/packing_received_print.html', context)




@csrf_exempt
def packing_received_print_bk_22(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id).decode('utf-8'))
    except (ValueError, base64.binascii.Error):
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_packing_inward_table, id=order_id)
    
    party = get_object_or_404(party_table, id=total_values.party_id)
    
    try:
        product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        quality = get_object_or_404(quality_table, id=total_values.quality_id)
        style = get_object_or_404(style_table, id=total_values.style_id)
    except (fabric_program_table.DoesNotExist, fabric_table.DoesNotExist, quality_table.DoesNotExist, style_table.DoesNotExist):
        return JsonResponse({'error': 'Related master data not found'}, status=404)

    prg_details = child_packing_inward_table.objects.filter(tm_id=order_id,status=1).values(
        'size_id'
    ).annotate(
        total_box=Sum('box'),
        total_loose_pcs=Sum('loose_pcs'),
        box_pcs=Sum('box_pcs'),
        pcs_per_box=Sum('pcs_per_box'),
        total_seconds_pcs=Sum('seconds_pcs'),
        total_shortage_pcs=Sum('shortage_pcs') 
    ).order_by('size_id') 

    print('prg-detail:',prg_details)
    combined_details = []
    
    for prg_detail in prg_details:
        size = get_object_or_404(size_table, id=prg_detail['size_id'])
        
        box_pcs = prg_detail['box_pcs'] or 0
        pcs_per_box = prg_detail['pcs_per_box'] or 0
        quantity = prg_detail['total_box'] or 0 
        print('qty-box:',quantity)
        loose_pcs = prg_detail['total_loose_pcs'] or 0
        seconds_pcs = prg_detail['total_seconds_pcs'] or 0
        shortage_pcs = prg_detail['total_shortage_pcs'] or 0

        total_pcs = (quantity * 10) + loose_pcs
 
        combined_details.append({
            'size': size.name,
            'quantity': quantity,
            'box_pcs':box_pcs,
            'pcs_per_box':pcs_per_box,
            'loose_pcs': loose_pcs,
            'seconds_pcs': seconds_pcs,
            'shortage_pcs': shortage_pcs,  
            'total_pcs': total_pcs,
        })

        total_boxes = sum(c.quantity for c in combined_details)
        total_box_pcs = sum(c.box_pcs for c in combined_details)
        loose_pcs_total = sum(c.loose_pcs for c in combined_details)
        seconds_pcs_total = sum(c.seconds_pcs for c in combined_details)
        shortage_pcs_total = sum(c.shortage_pcs for c in combined_details)
        grand_total_pcs = sum(c.total_pcs for c in combined_details)


    context = {
        'total_values': total_values,
        'party_name': party.name,
        'gstin': party.gstin,
        'mobile': party.mobile,
        'quality': quality.name,
        'style': style.name,
        'combined_details': combined_details,
        # 'total_boxes': total_values.total_box,
        # 'loose_pcs_total': total_values.loose_pcs,
        # 'seconds_pcs_total': total_values.seconds_pcs,
        # 'shortage_pcs_total': total_values.shortage_pcs,
        # 'grand_total_pcs': total_values.total_pcs,
        "total_boxes": total_boxes,
        "total_box_pcs": total_box_pcs,
        "loose_pcs_total": loose_pcs_total,
        "seconds_pcs_total": seconds_pcs_total,
        "shortage_pcs_total": shortage_pcs_total,
        "grand_total_pcs": grand_total_pcs,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'company': company_table.objects.filter(status=1).first(),
    }

    return render(request, 'packing_received/packing_received_print.html', context)

# from collections import defaultdict

# @csrf_exempt
# def packing_received_print(request):
#     po_id = request.GET.get('k') 
#     if not po_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     try:
#         order_id = int(base64.b64decode(po_id)) 
#         print('ord-id:',order_id)
#     except Exception:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)

#     total_values = get_object_or_404(parent_packing_inward_table, id=order_id)
#     print('quality',total_values.quality_id)

#     party = get_object_or_404(party_table, id=total_values.party_id)
#     party_name = party.name
#     gstin = party.gstin
#     mobile = party.mobile



#     prg_details = child_packing_inward_table.objects.filter(tm_id=order_id).values(
#         'id', 'box', 'size_id','loose_pcs','seconds_pcs', 'shortage_pcs'
#     )
   
#     combined_details = []
#     total_quantity = 0 
 
#     for prg_detail in prg_details:
#         product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
#         fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
#         quality = get_object_or_404(quality_table, id=total_values.quality_id)
#         style = get_object_or_404(style_table, id=total_values.style_id)



#         size = get_object_or_404(size_table, id=prg_detail['size_id'])
#         # color = get_object_or_404(color_table, id=prg_detail['color_id'])

     
#         # quantity = prg_detail['box']
#         # loose_pcs = prg_detail['loose_pcs']
#         # seconds_pcs = prg_detail['seconds_pcs']
#         # shortage_pcs = prg_detail['shortage_pcs']
#         # # total_pcs = 0 #prg_detail['total_pcs']
#         # total_pcs = (quantity * 12) + loose_pcs + seconds_pcs + shortage_pcs

#         quantity = prg_detail['box'] or 0
#         loose_pcs = prg_detail['loose_pcs'] or 0
#         seconds_pcs = prg_detail['seconds_pcs'] or 0
#         shortage_pcs = prg_detail['shortage_pcs'] or 0

#         # Now calculate total_pcs safely
#         total_pcs = (quantity * 12) + loose_pcs + seconds_pcs + shortage_pcs



#         total_quantity += quantity

#         combined_details.append({
#             'fabric': fabric_obj.name,
#             'style': style.name,
#             'quality': quality.name,
#             # 'color': color.name,
#             'size': size.name, 
#             'quantity': quantity,
#             'loose_pcs':loose_pcs,
#             'seconds_pcs':seconds_pcs,
#             'shortage_pcs':shortage_pcs,
#             'total_pcs':total_pcs,
#         })

#     # Collect unique dia values in sorted order
#     sizes = sorted(set(item['size'] for item in combined_details))

#     # Group data by fabric + color
#     group_map = defaultdict(lambda: {'size_data': {}})
#     grouped_data = []

#     for item in combined_details:
#         key = (item['fabric'], item['size'])
#         group_map[key]['fabric'] = item['fabric']
#         group_map[key]['size_data'][item['size']] = {
#             'quantity': item['quantity'],
#             'loose_pcs': item['loose_pcs'],
#             'seconds_pcs': item['seconds_pcs'],
#             'shortage_pcs': item['shortage_pcs'],
#             'total_pcs': total_pcs,
#         }

    

#     for val in group_map.values():
#     # Prebuild size_data_list to avoid dynamic dict access in template
#         val['size_data_list'] = [
#             val['size_data'].get(size, {'quantity': ''}) for size in sizes
#         ]

#         # Compute row total
#         val['row_total'] = sum(entry['quantity'] for entry in val['size_data_list'] if entry['quantity'])

#         grouped_data.append(val)
#         grand_total = sum(val['row_total'] for val in grouped_data) 
 
 
#     # size-wise total (dict) and list (for template)
#     size_totals = {size: {'quantity': 0} for size in sizes} 
#     for item in combined_details:
#         size_totals[item['size']]['quantity'] += item['quantity']

#     size_totals_list = [size_totals[size] for size in sizes]
#     total_columns = 2 + len(sizes) * 2

#     context = {

#         'total_values': total_values,
#         'sizes': sizes,
#         'party_name':party_name,
#         'gstin':gstin,
#         'mobile':mobile,
#         'grouped_data': grouped_data,
#         'dia_totals_list': size_totals_list,
#         'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
#         'total_columns':total_columns,
#         'company':company_table.objects.filter(status=1).first(),
#         'fabric': fabric_obj.name,
#         'style': style.name, 
#         'quality': quality.name,
#         'size': size.name,
#         'grand_total':grand_total,
#         'combined_details':combined_details,
#         'loose_pcs_total':total_values.loose_pcs,
#         'seconds_pcs_total':total_values.seconds_pcs,
#         'shortage_pcs_total':total_values.shortage_pcs,
#         'total_boxes':total_values.total_box,
#         'total_pcs':total_values.total_pcs,
 
#     }

#     return render(request, 'packing_received/packing_received_print.html', context)





from decimal import Decimal
from django.http import JsonResponse
from django.utils import timezone
import json
from .models import parent_packing_inward_table, child_packing_inward_table

@csrf_exempt
def update_packing_received(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')

            # Retrieve data from the POST request
            master_id = request.POST.get('tm_id')
            # inward_date = request.POST.get('inward_date')

            # dc_no = request.POST.get('dc_no')
            # dc_date = request.POST.get('dc_date')
            remarks = request.POST.get('remarks')
            work_order_no = request.POST.get('work_order_no')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            fabric_id = request.POST.get('fabric_id')
            outward_id = request.POST.get('delivery_id')


            # Validation checks
            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            chemical_data = request.POST.get('received_data')
            loose_pcs_data = json.loads(request.POST.get('loose_pcs_data', '[]'))

            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'})

            # Parse table data
            table_data = json.loads(chemical_data)
            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Step 1: Update master table entry
            material_request = parent_packing_inward_table.objects.filter(id=master_id).first()
            if not material_request:
                return JsonResponse({'success': False, 'error_message': 'Invalid master ID'})

            # material_request.inward_date = inward_date
            # material_request.dc_no = dc_no, 
            # material_request.dc_date = dc_date,
            material_request.remarks = remarks
            material_request.updated_by = user_id
            material_request.updated_on = timezone.now()

            # Step 2: Delete existing child entries (set status and is_active)
            child_packing_inward_table.objects.filter(tm_id=master_id).update(status=0, is_active=0)
            child_packing_inward_loose_pcs_table.objects.filter(tm_id=master_id).update(status=0, is_active=0)

            total_qty = Decimal('0.000')  # Sum up quantities for the master table

            # Step 3: Insert updated child entries
            for row in table_data:
                quantity = safe_decimal(row.get('quantity', 0))
                total_qty += quantity  # Sum total quantity

                # Create a new child entry
                print('per-box:',row.get('pcs_per_box'))
                child_packing_inward_table.objects.create(
                    tm_id=material_request.id,
                    work_order_no=work_order_no, 
                    quality_id=quality_id, 
                    style_id=style_id,
                    outward_id=material_request.outward_id, 
                    size_id=row.get('size_id'), 
                    box=row.get('box'), 
                    box_pcs=row.get('box_pcs'),
                    pcs_per_box=row.get('pcs_per_box'),
                    loose_pcs=row.get('loose_pcs'),
                    seconds_pcs=row.get('seconds_pcs'),
                    shortage_pcs=row.get('shortage'),
                    created_by=user_id,
                    created_on=timezone.now(), 
                    company_id=company_id,
                    cfyear=2025,  # This could be dynamic if needed
                    updated_by=user_id,
                    updated_on=timezone.now()
                ) 


                for key, pcs in loose_pcs_data.items():
                    print("Processing pcs Data:", pcs)

                    sub_loose_pcs = child_packing_inward_loose_pcs_table.objects.create(
                        work_order_no=work_order_no,
                        tm_id=material_request.id,
                        outward_id=material_request.outward_id,
                        size_id=pcs.get('size_id'), 
                        quantity=pcs.get('quantity'),
                        color_id=pcs.get('color_id'),
                        created_by=user_id,
                        created_on=timezone.now(),
                        company_id=company_id,
                        cfyear=2025,
                    )
                    print('sub_pcs:', sub_loose_pcs)





            # Step 4: Update master total quantity and other fields
            material_request.total_box = request.POST.get('total_box')
            material_request.total_pcs = request.POST.get('delivered_pcs')
            material_request.per_box = request.POST.get('per_box', 0)
            material_request.loose_pcs = request.POST.get('loose_pcs', 0)
            material_request.seconds_pcs = request.POST.get('seconds_pcs', 0)
            material_request.shortage_pcs = request.POST.get('shortage_pcs', 0)
            material_request.balance_pcs = request.POST.get('balance_pcs', 0)
            

            # Save master table
            material_request.save()

            return JsonResponse({'success': True, 'message': 'Updated successfully!'})

        except Exception as e:
            # Handle errors and send response
            return JsonResponse({'success': False, 'error_message': str(e)})

    # Return an error if method is not POST
    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_packing_received_data(request):
    if request.method == 'POST':
        inward_date_str = request.POST.get('inward_date')
        dc_date_str = request.POST.get('dc_date')
        tm_id = request.POST.get('tm_id')
        remarks = request.POST.get('remarks')
        dc_no = request.POST.get('dc_no')

         
        # is_packing_raw = request.POST.get('is_packing')  # This will be '1' or '0' based on the checkbox state

            # Convert '1' -> 1 and '0' -> 0
        # is_packing = 1 if is_packing_raw == '1' else 0

        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = parent_packing_inward_table.objects.get(id=tm_id)
         
            parent_item.remarks= remarks
            parent_item.dc_no= dc_no

            if inward_date_str:
                inward_date = datetime.strptime(inward_date_str, '%Y-%m-%d').date()
                parent_item.inward_date = inward_date

            if dc_date_str:
                dc_date = datetime.strptime(dc_date_str, '%Y-%m-%d').date()
                parent_item.dc_date = dc_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except parent_packing_inward_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




@csrf_exempt
def update_packing_received_bk_16_8_25(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')

            master_id = request.POST.get('tm_id')
            inward_date = request.POST.get('inward_date')
            remarks = request.POST.get('remarks')
            work_order_no = request.POST.get('work_order_no')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            fabric_id = request.POST.get('fabric_id')
            outward_id = request.POST.get('delivery_id')

            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            chemical_data = request.POST.get('received_data')
            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'})

            table_data = json.loads(chemical_data)
            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Step 1: Update master table entry
            material_request = parent_packing_inward_table.objects.filter(id=master_id).first()
            if not material_request:
                return JsonResponse({'success': False, 'error_message': 'Invalid master ID'})

            material_request.inward_date = inward_date
            material_request.remarks = remarks
            # material_request.quality_id = quality_id
            # material_request.fabric_id=fabric_id
            # material_request.style_id = style_id
            material_request.updated_by = user_id 
            material_request.updated_on = timezone.now()

            # Step 2: Delete existing child entries
            child_packing_inward_table.objects.filter(tm_id=master_id).update(status=0,is_active=0)

            total_qty = Decimal('0.000')

            # Step 3: Insert updated child entries
            for row in table_data:
                quantity = safe_decimal(row.get('quantity', 0))
                total_qty += quantity

                child_packing_inward_table.objects.create(
                    tm_id=material_request.id,

                    work_order_no=work_order_no,
                    quality_id=quality_id,
                    style_id=style_id,
                    outward_id=outward_id,
                    size_id=row.get('size_id'),
                    box=row.get('box'),
                    loose_pcs=row.get('loose_pcs'),
                    seconds_pcs=row.get('seconds_pcs'),
                    shortage_pcs=row.get('shortage_pcs'),
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,
                    updated_by=user_id,
                    updated_on=timezone.now()
                )

            # Step 4: Update master total quantity 
            # material_request.total_pcs = total_qty

            material_request.total_box=request.POST.get('total_box')
            material_request.total_pcs=request.POST.get('delivered_pcs')
            material_request.per_box=request.POST.get('per_box',0)
            material_request.loose_pcs=request.POST.get('loose_pcs',0)
            material_request.seconds_pcs=request.POST.get('seconds_pcs',0)
            material_request.shortage_pcs=request.POST.get('shortage_pcs',0)
            material_request.balance_pcs=request.POST.get('balance_pcs',0)
            material_request.save()

          
            return JsonResponse({'success': True, 'message': 'Updated successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# @csrf_exempt
# @require_POST 
# def get_packing_delivery_color_lists(request):
#     prg_id = request.POST.get('prg_id')
#     if not prg_id:
#         return JsonResponse({'error': 'prg_id missing'}, status=400)

#     queryset = child_packing_outward_table.objects.filter(staus=1, tm_id=prg_id)
#     data = list(queryset.values('size_id', 'size_name', 'color_id', 'color_name', 'available_qty'))

#     quality_list = quality_table.objects.filter(status=1).values_list("id","name")
#     style_list = style_table.objects.filter(status=1).values_list("id","name")
#     color_list = color_table.objects.filter(status=1).values_list("id","name")
#     size_list = size_table.objects.filter(status=1).values_list("id","name")
#     # Example placeholders for related data:
#     quality = {'id': 5, 'name': 'Quality A'}
#     style = {'id': 8, 'name': 'Style X'}

#     return JsonResponse({
#         'data': data,
#         'quality': quality,
#         'style': style,
#     })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def get_packing_outward_color_lists(request):
    prg_ids = request.POST.getlist('prg_id[]')
    print('Received prg_ids:', prg_ids)

    if not prg_ids:
        return JsonResponse({'error': 'prg_id missing'}, status=400)

    # Ensure prg_ids are integers
    try:
        prg_ids = [int(pid) for pid in prg_ids] 
    except ValueError:
        return JsonResponse({'error': 'Invalid prg_id values'}, status=400)

    # Query child_packing_outward_table with the list of prg_ids
    queryset = child_packing_outward_table.objects.filter(status=1, tm_id__in=prg_ids)
    data = list(queryset.values('size_id', 'color_id', 'quantity'))

    # Extract unique IDs for related lookups
    quality_ids = queryset.values_list('quality_id', flat=True).distinct()
    style_ids = queryset.values_list('style_id', flat=True).distinct()
    color_ids = queryset.values_list('color_id', flat=True).distinct()
    size_ids = queryset.values_list('size_id', flat=True).distinct()

    # Query related tables using those IDs
    quality_list = list(quality_table.objects.filter(status=1, id__in=quality_ids).values('id', 'name'))
    style_list = list(style_table.objects.filter(status=1, id__in=style_ids).values('id', 'name'))
    color_list = list(color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name'))
    size_list = list(size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name'))

    return JsonResponse({
        'data': data,
        'quality_list': quality_list,
        'style_list': style_list,
        'color_list': color_list,
        'size_list': size_list,
    })





@csrf_exempt
@require_POST 
def get_stitching_outward_color_lists(request):
    # prg_id = request.POST.get('prg_id')
    # if not prg_id:
    #     return JsonResponse({'error': 'prg_id missing'}, status=400)


    prg_ids = request.POST.getlist('prg_id[]')
    print('Received prg_ids:', prg_ids)

    if not prg_ids:
        return JsonResponse({'error': 'prg_id missing'}, status=400)

    # Ensure prg_ids are integers
    try:
        prg_ids = [int(pid) for pid in prg_ids] 
    except ValueError:
        return JsonResponse({'error': 'Invalid prg_id values'}, status=400)
    

    queryset = child_stiching_outward_table.objects.filter(status=1, tm_id__in=prg_ids)
    data = list(queryset.values('size_id', 'color_id', 'quantity')) 

    # Extract unique IDs for related lookups
    quality_ids = queryset.values_list('quality_id', flat=True).distinct()
    style_ids = queryset.values_list('style_id', flat=True).distinct()
    color_ids = queryset.values_list('color_id', flat=True).distinct()
    size_ids = queryset.values_list('size_id', flat=True).distinct()

    # Query related tables using those IDs
    quality_list = list(quality_table.objects.filter(status=1, id__in=quality_ids).values('id', 'name'))
    style_list = list(style_table.objects.filter(status=1, id__in=style_ids).values('id', 'name'))
    color_list = list(color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name'))
    size_list = list(size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name'))

    return JsonResponse({
        'data': data,
        'quality_list': quality_list,
        'style_list': style_list,
        'color_list': color_list,
        'size_list': size_list,
    })

