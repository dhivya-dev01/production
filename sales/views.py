import re
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify
from jwt import decode

from accessory.models import *
from accessory.views import getDiaByIds
from software_app.models import *
from yarn.models import *
from user_auth.models import *
from user_roles.models import *
from program_app.models import *
from company.models import *
from employee.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
from software_app.forms import *
import datetime
from django.db import connection

from datetime import datetime 
from datetime import date 
from django.utils import timezone 

from django.db.models import Count


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from software_app.models import *

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
from common.utils import *
from production_app.models import *
from accessory.models import *
from sales.models import *
# ``````````````````````````````````````*************************``````````````````````````````````````````````````````````
# Create your views here.


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 




def sales_orders(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'sales_order/sales_order_list.html')
    else:
        return HttpResponseRedirect("/signin")
 



def generate_sales_order_no():
    last_purchase = parent_sales_order_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.order_no:
        match = re.search(r'DO-(\d+)', last_purchase.order_no)
        if match:
            next_num = int(match.group(1)) + 1
        else: 
            next_num = 1
    else: 
        next_num = 1
 
    return f"DO-{next_num:03d}"


def add_sales_order(request): 
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        sales_order_no = generate_sales_order_no()
        party = party_table.objects.filter(status=1,is_ironing=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        return render(request,'sales_order/add_sales_order.html',
                      {'order_no':sales_order_no,
                       'party':party,
                       'quality':quality,
                       'style':style,
                       }
                    )
    else:
        return HttpResponseRedirect("/signin")
 


@csrf_exempt 
def get_packing_received_lists(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    party_id = request.POST.get('customer_id')
    print('party-id:', party_id)

    if not party_id:
        return JsonResponse({'error': 'Party ID is required'}, status=400)

    try:
        # Packing Inward

        packing_inward = parent_packing_inward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'inward_no', 'work_order_no', 'total_pcs','total_box')

    
        print('packing-data:',packing_inward)

        # Combine both lists
        # combined_outward = list(chain(packing_inward, stitching_outward))
        # print('details:',packing_inward) 
        if not packing_inward:
            return JsonResponse({'error': 'Inward not found for the given party ID'}, status=404)

        # return JsonResponse({'outward': packing_inward})
        return JsonResponse({'inward': list(packing_inward)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 


# def get_packing_inward_list(request):
#     packing_list_id = request.GET.get('packing_list_id')

#     if not packing_list_id:
#         return JsonResponse({'status': 'error', 'message': 'Missing packing list ID'})

#     size = size_table.objects.filter(status=1,id=data['size_id'])
#     data = list(child_packing_inward_table.objects.filter(tm_id=packing_list_id)
#                 .values('size_id', 'box', 'pcs_per_box', 'box_pcs'))

#     return JsonResponse({'status': 'success', 'data': data})



from django.http import JsonResponse



def get_packing_inward_list(request):
    packing_list_id = request.GET.get('packing_list_id')
    party_id = request.GET.get('party_id')

    if not packing_list_id:
        return JsonResponse({'status': 'error', 'message': 'Missing packing list ID'})

    try:
        # Fetch inward data first
        inward_data = child_packing_inward_table.objects.filter(tm_id=packing_list_id)
        party = party_table.objects.filter(status=1, id=party_id).first()
        inward = parent_packing_inward_table.objects.filter(status=1, id=packing_list_id).first()

        if not party or not inward:
            return JsonResponse({'status': 'error', 'message': 'Party or Inward not found'})

        # Get the related price list
        price = price_list_table.objects.filter(status=1, id=party.price_list_id).first()
        if not price:
            return JsonResponse({'status': 'error', 'message': 'Price list not found'})

        data = []
        for item in inward_data:
            size_name = (
                size_table.objects.filter(id=item.size_id, status=1)
                .values_list('name', flat=True)
                .first()
            )

            # Get rate value
            rate_value = (
                price_list_range_table.objects.filter(
                    quality_id=inward.quality_id,
                    style_id=inward.style_id,
                    size_id=item.size_id,
                    price_list_id=price.id,
                    status=1
                )
                .values_list('rate', flat=True)
                .first()
            )

            data.append({
                'size_id': item.size_id,
                'size_name': size_name or '',
                'box_qty': item.box,
                'pcs_per_box': item.pcs_per_box,
                'box_pcs': item.box_pcs,
                'rate': rate_value or 0,
                'total_pcs': item.box_pcs or 0,
            })

        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})




def get_quality_style_lists(request):
    quality_id = request.GET.get('quality_id')
    style_id = request.GET.get('style_id')
    party_id = request.GET.get('party_id')
    print('ids:',quality_id,style_id,party_id) 

    if not quality_id:
        return JsonResponse({'status': 'error', 'message': 'Missing quality_id'})

    try:
        # ✅ Fetch inward data
        inward_data = child_packing_inward_table.objects.filter(tm_id=quality_id) 
        party = party_table.objects.filter(status=1, id=party_id).first()
        inward = parent_packing_inward_table.objects.filter(status=1, id=quality_id).first()
        # print('inw:',inward)
        # if not party or not inward:
        #     return JsonResponse({'status': 'error', 'message': 'Party or Inward not found'})

        # ✅ Get related price list
        price = price_list_table.objects.filter(status=1, id=party.price_list_id).first()
        if not price:
            return JsonResponse({'status': 'error', 'message': 'Price list not found'})

        # ✅ Run your availability SQL query
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    k.quality_id,
                    k.style_id,
                    k.size_id,
                    COALESCE(pi.total_inward_pcs, 0) AS total_inward_pcs,
                    COALESCE(so.total_sold_pcs, 0) AS total_sold_pcs,
                    (COALESCE(pi.total_inward_pcs, 0) - COALESCE(so.total_sold_pcs, 0)) AS available_pcs
                FROM (
                    SELECT DISTINCT
                        ti.quality_id,
                        ti.style_id,
                        tx.size_id
                    FROM tx_packing_inward AS tx
                    LEFT JOIN tm_packing_inward AS ti ON tx.tm_id = ti.id AND ti.status = 1
                    WHERE tx.status = 1
                    UNION
                    SELECT DISTINCT
                        ts.quality_id,
                        ts.style_id,
                        ts.size_id
                    FROM tx_sales_order AS ts
                    LEFT JOIN tm_sales_order AS tms ON ts.tm_id = tms.id AND tms.status = 1
                    WHERE ts.status = 1
                ) AS k
                LEFT JOIN (
                    SELECT 
                        ti.quality_id,
                        ti.style_id,
                        tx.size_id,
                        SUM(tx.box_pcs) AS total_inward_pcs
                    FROM tx_packing_inward AS tx
                    LEFT JOIN tm_packing_inward AS ti ON tx.tm_id = ti.id AND ti.status = 1
                    WHERE tx.status = 1
                    GROUP BY ti.quality_id, ti.style_id, tx.size_id
                ) AS pi
                    ON k.quality_id = pi.quality_id
                    AND k.style_id = pi.style_id
                    AND k.size_id = pi.size_id
                LEFT JOIN (
                    SELECT 
                        ts.quality_id,
                        ts.style_id,
                        ts.size_id,
                        SUM(ts.box_pcs) AS total_sold_pcs
                    FROM tx_sales_order AS ts
                    LEFT JOIN tm_sales_order AS tms ON ts.tm_id = tms.id AND tms.status = 1
                    WHERE ts.status = 1
                    GROUP BY ts.quality_id, ts.style_id, ts.size_id
                ) AS so
                    ON k.quality_id = so.quality_id
                    AND k.style_id = so.style_id 
                    AND k.size_id = so.size_id
                WHERE k.quality_id = %s AND k.style_id = %s
            """, [quality_id, style_id])

            availability_results = cursor.fetchall()
            print('avl-pcs:',availability_results)

        # ✅ Build a dict for quick lookup by size_id
        availability_map = {}
        for row in availability_results:
            _, _, size_id, total_inward_pcs, total_sold_pcs, available_pcs = row
            availability_map[size_id] = {
                'inward_pcs': total_inward_pcs or 0,
                'sold_pcs': total_sold_pcs or 0,
                'available_pcs': available_pcs or 0,
            }
 
        data = []
        all_size_ids = set(list(availability_map.keys()) + list(inward_data.values_list('size_id', flat=True)))

        for size_id in all_size_ids:
            size_name = size_table.objects.filter(id=size_id, status=1).values_list('name', flat=True).first()
            available = availability_map.get(size_id, {'available_pcs': 0})

            # Get inward data if exists
            inward_item = next((x for x in inward_data if x.size_id == size_id), None)

            box_qty = inward_item.box if inward_item else 0
            pcs_per_box = inward_item.pcs_per_box if inward_item else 0
            box_pcs = inward_item.box_pcs if inward_item else 0

            rate_value = price_list_range_table.objects.filter(
                quality_id=quality_id,
                style_id=style_id,
                size_id=size_id,
                price_list_id=price.id,
                status=1
            ).values_list('rate', flat=True).first()
            
            quality_prg = quality_program_table.objects.filter(status=1,quality_id=quality_id,style_id=style_id).first()

            size = sub_quality_program_table.objects.filter(status=1,tm_id=quality_prg.id,size_id=size_id).first()
            per_box =  size.per_box

            quality = quality_table.objects.filter(status=1, id=quality_id).first()
            style = style_table.objects.filter(status=1, id=style_id).first()

            data.append({
                'size_id': size_id,
                'size_name': size_name or '',
                'box_qty': box_qty,
                'pcs_per_box': per_box,
                'box_pcs': box_pcs,
                'rate': rate_value or 0,
                'total_pcs': box_pcs,
                'available_pcs': available['available_pcs'],
                'quality_id':quality_id,
                'style_id':style_id,
                'quality':quality.name,
                'style':style.name
            })



        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})




def get_sales_order_list(request):
    tm_id = request.GET.get('tm_id')
    party_id = request.GET.get('party_id')

    if not tm_id:
        return JsonResponse({'status': 'error', 'message': 'Missing packing list ID'})

    try:
        # Fetch parent record (inward)
        inward = parent_sales_order_table.objects.filter(status=1, id=tm_id).first()
        party = party_table.objects.filter(status=1, id=party_id).first()

        if not party or not inward:
            return JsonResponse({'status': 'error', 'message': 'Party or Inward not found'})

        # Fetch related quality and style names
        

        # Get the related price list
        price = price_list_table.objects.filter(status=1, id=party.price_list_id).first()
        if not price:
            return JsonResponse({'status': 'error', 'message': 'Price list not found'})

        # Fetch all child rows for the selected tm_id
        inward_data = child_sales_order_table.objects.filter(tm_id=tm_id)

        data = []
        for item in inward_data:
            # Get size name
            size_name = (
                size_table.objects.filter(id=item.size_id, status=1)
                .values_list('name', flat=True)
                .first()
            )
            quality = quality_table.objects.filter(status=1, id=item.quality_id).first()
            style = style_table.objects.filter(status=1, id=item.style_id).first()
            # Get rate from price list range
            rate_value = (
                price_list_range_table.objects.filter(
                    quality_id=item.quality_id,
                    style_id=item.style_id,
                    size_id=item.size_id,
                    price_list_id=price.id,
                    status=1
                )
                .values_list('rate', flat=True)
                .first()
            )

            # Compose row
            data.append({
                'size_id': item.size_id,
                'size_name': size_name or '',
                'box_qty': item.box,
                'pcs_per_box': item.pcs_per_box,
                'box_pcs': item.box_pcs,
                'rate': rate_value or 0,
                'total_pcs': item.box_pcs or 0,
                'quality_id': item.quality_id,
                'style_id': item.style_id,
                'quality': quality.name if quality else '',
                'style': style.name if style else '' 
            })

        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# def get_sales_order_list(request):
#     tm_id = request.GET.get('tm_id')
#     party_id = request.GET.get('party_id')

#     if not tm_id:
#         return JsonResponse({'status': 'error', 'message': 'Missing packing list ID'})

#     try:
#         # Fetch inward data first
#         inward_data = child_sales_order_table.objects.filter(tm_id=tm_id)
#         party = party_table.objects.filter(status=1, id=party_id).first()
#         inward = parent_sales_order_table.objects.filter(status=1, id=tm_id).first()

#         if not party or not inward:
#             return JsonResponse({'status': 'error', 'message': 'Party or Inward not found'})

#         # Get the related price list
#         price = price_list_table.objects.filter(status=1, id=party.price_list_id).first()
#         if not price:
#             return JsonResponse({'status': 'error', 'message': 'Price list not found'})

#         data = []
#         for item in inward_data:
#             size_name = (
#                 size_table.objects.filter(id=item.size_id, status=1)
#                 .values_list('name', flat=True)
#                 .first()
#             )

#             # Get rate value
#             rate_value = (
#                 price_list_range_table.objects.filter(
#                     quality_id=inward.quality_id,
#                     style_id=inward.style_id,
#                     size_id=item.size_id,
#                     price_list_id=price.id,
#                     status=1
#                 )
#                 .values_list('rate', flat=True)
#                 .first()
#             )
           
#             data.append({
#                 'size_id': item.size_id,
#                 'size_name': size_name or '',
#                 'box_qty': item.box,
#                 'pcs_per_box': item.pcs_per_box,
#                 'box_pcs': item.box_pcs,
#                 'rate': rate_value or 0,
#                 'total_pcs': item.box_pcs or 0,
          
#             })

#         return JsonResponse({'status': 'success', 'data': data})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)})



from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def insert_sales_order(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            # Extract data from request
            order_date = request.POST.get('order_date')
            party_id = request.POST.get('customer_id')
            remarks = request.POST.get('remarks')
            price_list = request.POST.get('price_list')
            packing_id = request.POST.get('packing_list')
            work_order_no = request.POST.get('work_order_no')

            # Parse order data JSON
            data = json.loads(request.POST.get('order-data', '[]'))
            print('🔹 Raw Order Data:', data)

            # Generate Sales Order Number
            inward_no = generate_sales_order_no()

            # Create Parent Entry
            parent_entry = parent_sales_order_table.objects.create(
                order_no=inward_no.upper(),
                order_date=order_date,
                packing_received_id=packing_id,
                party_id=party_id,
                work_order_no=work_order_no,
                company_id=company_id,
                cfyear=2025,
                total_box=request.POST.get('sub_total'),
                total_pcs=request.POST.get('total_pcs'),
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )
            print('✅ Parent entry created:', parent_entry)

            # Create Child Entries — only for valid size_id (>0)
            for order in data:
                try:
                    size_id_raw = order.get('size_id')
                    size_id = int(size_id_raw) if size_id_raw not in (None, '', 'null') else 0

                    # 🚫 Skip invalid or missing size_id
                    if size_id <= 0:
                        print(f"⚠️ Skipped invalid size_id: {size_id_raw}")
                        continue

                    # Insert child record
                    sub_entry = child_sales_order_table.objects.create(
                        work_order_no=work_order_no,
                        tm_id=parent_entry.id,
                        packing_received_id=packing_id,
                        size_id=size_id,
                        quality_id=order.get('quality_id'),
                        style_id=order.get('style_id'),
                        box=order.get('box') or 0,
                        pcs_per_box=order.get('pcs_per_box') or 0,
                        box_pcs=order.get('total_pcs') or 0,
                        rate=order.get('rate') or 0,
                        amount=order.get('amount') or 0,
                        created_by=user_id,
                        created_on=timezone.now(),
                        company_id=company_id,
                        cfyear=2025,
                    )
                    print('   ✅ Child entry created:', sub_entry)

                except Exception as child_err:
                    print(f"❌ Error inserting child record: {child_err}")
                    continue

            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f"❌ Main Error: {e}")
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'sales_order/add_sales_order.html')


# @csrf_exempt
# def insert_sales_order(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')  # Prevent KeyErrors
#         company_id = request.session.get('company_id')

#         try: 
#             # Extracting Data from Request  
#             order_date = request.POST.get('order_date')
#             party_id = request.POST.get('customer_id')

#             remarks = request.POST.get('remarks')  
#             price_list = request.POST.get('price_list') 

#             packing_id = request.POST.get('packing_list') 

#             # style_id = request.POST.get('style_id')   
#             # dc_no = request.POST.get('dc_no')
#             # dc_date = request.POST.get('dc_date') 
#             # received_date = request.POST.get('inward_date')
#             # received_date = request.POST.get('inward_date')

  
#             data = json.loads(request.POST.get('order-data', '[]'))

#             work_order_no = request.POST.get('work_order_no') 

#             print('Chemical Data:', data)  

#             def clean_amount(amount): 
#                 """Remove currency symbols and commas from amount values."""
#                 return amount.replace('₹', '').replace(',', '').strip()  

 
#             inward_no = generate_sales_order_no()
            
#             # Create Parent Entry (gf_inward_table)
#             material_request = parent_sales_order_table.objects.create(
#                 order_no = inward_no.upper(),
#                 order_date=order_date,   
                
#                 packing_received_id = packing_id, 
#                 party_id = party_id,
#                 # prg_quantity = 0,
#                 work_order_no = work_order_no, 
#                 # quality_id=quality_id, 
#                 # style_id=style_id, 
#                 company_id=company_id,  
#                 cfyear = 2025,  
              
#                 total_box=request.POST.get('sub_total'),
#                 total_pcs=request.POST.get('total_pcs'),
                      
#                 remarks=remarks, 
#                 created_by=user_id,
#                 created_on=timezone.now()
#             ) 
#             print('m-req:',material_request)

#             po_ids = set()  # Store unique PO IDs to update later

#             # Create Sub Table Entries
#             for order in data:
#                 print("Processing order Data:", order)
 
#                 po_id = order.get('tm_id')  # Get PO ID
#                 po_ids.add(po_id)  # Store for updating later
 
#                 sub_entry = child_sales_order_table.objects.create(
#                     work_order_no = work_order_no,
#                     tm_id=material_request.id,  
#                     packing_received_id = packing_id,
#                     size_id=order.get('size_id'),  
#                     quality_id=order.get('quality_id'),  
#                     style_id=order.get('style_id'),  
#                     box=order.get('box'),
#                     pcs_per_box=order.get('pcs_per_box'), 
#                     box_pcs=order.get('total_pcs'),

#                     rate = order.get('rate'),
#                     amount = order.get('amount') ,

#                     created_by=user_id,
#                     created_on=timezone.now(), 
#                     company_id=company_id,
#                     cfyear=2025, 

#                 )
#                 print('sub:',sub_entry)


#             # Return a success response
#             return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

#         except Exception as e:
#             print(f" Error: {e}")  # Log error
#             return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

#     return render(request, 'packing_received/add_packing_received.html')


 
def getSupplier(tbl, supplier_id):
    try: 
        party = tbl.objects.get(id=supplier_id).name 
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party



# def sales_order_ajax_list(request):
#     tm_id = request.POST.get('id')

#     # Fetch child data 
#     child_qs = child_sales_order_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')

#     if child_qs.exists():
#         # Calculate total quantity and total weight from child table
#         total_box = child_qs.aggregate(Sum('box'))['box__sum'] or 0

#         # Fetch master cutting entry
#         parent_data = parent_sales_order_table.objects.filter(id=tm_id).first()

#         if not parent_data:
#             return JsonResponse({'message': 'error', 'error_message': 'Cutting Entry not found in parent table'})

#         # Convert child queryset to list
#         child_data = list(child_qs.values())
#         print('child-data:',child_data)

 

#         formatted_data = [ 
#             {
#                 'action': f'<button type="button" onclick="packing_received_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '
#                         f'<button type="button" onclick="packing_received_delete(\'{item["id"]}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>',
#                 'id': index + 1,
#                 'order_no': parent_data.order_no if hasattr(parent_data, 'order_no') else '-',
#                 'order_date': parent_data.order_date.strftime('%d-%m-%Y') if hasattr(parent_data, 'order_date') else '-',
#                 'party': getSupplier(party_table, parent_data.party_id),
#                 'work_order_no': item['work_order_no'],
#                 'packing_received': getInward_entryNoById(parent_packing_inward_table, item['packing_received_id']),
#                 'total_box': item['box'] or 0,   # ✅ Correct field name
#                 'total_pcs': item['pcs'] or 0,   # ✅ Adjust if your child table uses another field
#                 'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
#             }
#             for index, item in enumerate(child_data)
#         ]




#         # Prepare master values for summary
#         summary_data = {
#             'total_box': total_box,
#             'delivered_pcs': parent_data.total_pcs,
          
       
#         }

#         return JsonResponse({
#             'data': formatted_data,
#             **summary_data
#         }) 

#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'No cutting program data found for this TM ID'})


from django.utils.timezone import make_aware, is_naive

def sales_order_ajax_list(request):   
    company_id = request.session.get('company_id') 
    print('company_id:', company_id)

    query = Q()

    party = request.POST.get('party', '')
    packing = request.POST.get('packing', '')
    # quality = request.POST.get('quality', '')
    # style = request.POST.get('style', '') 
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
    
   
    if packing: 
        query &= Q(packing_received_id=packing)   

    if party:
        query &= Q(party_id=party)

   
    # Query filtered data
    queryset = parent_sales_order_table.objects.filter(status=1).filter(query)
    child_data_map = child_sales_order_table.objects.filter(

        tm_id__in=queryset.values_list('id', flat=True),
        status=1

    ).values('tm_id').annotate(

        total_box_pcs=Sum('box_pcs'), 
        # total_loose_pcs=Sum('loose_pcs'),
        # total_seconds_pcs=Sum('seconds_pcs'),
        # total_shortage_pcs=Sum('shortage_pcs')

    )

    # Map child data by tm_id
    child_data_dict = {
        item['tm_id']: item for item in child_data_map
    }


    # Pull only required fields (including delivery_from)
    data = list(queryset.order_by('-id').values(
        'id', 'order_no', 'order_date', 'work_order_no','party_id',
        'packing_received_id', 'total_box','total_pcs',
        'is_active','status'
    ))

    # Format results 
    formatted = [ 
        {
            'action': (
                f'<button type="button" onclick="sales_order_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs">'
                f'<i class="feather icon-edit"></i></button> '
                f'<button type="button" onclick="sales_order_delete(\'{item["id"]}\')" class="btn btn-danger btn-xs">'
                f'<i class="feather icon-trash-2"></i></button> '
                f'<button type="button" onclick="sales_order_print(\'{item["id"]}\')" class="btn btn-success btn-xs">'
                f'<i class="feather icon-printer"></i></button>'
            ),
            'id': index + 1, 
            'order_no': item.get('order_no') or '-',
            'order_date': item['order_date'].strftime('%Y-%m-%d') if isinstance(item.get('order_date'), date) else '-',
            'work_order_no': item.get('work_order_no') or '-', 
            # 'packing_received': item.get('packing_received_id') or '-',
            
         

            'packing_received': (
                getInward_entryNoById(parent_packing_inward_table, item['packing_received_id'])),

            'party': getSupplier(party_table, item['party_id']),
            # 'quality': getSupplier(quality_table, item['quality_id']),
            # 'style': getSupplier(style_table, item['style_id']), 
            'total_box': item.get('total_box') or '-',
            'total_pcs':item.get('total_pcs') or '-',
            # 'total_pcs': (
            #     (child_data_dict.get(item['id'], {}).get('total_box_pcs') or 0) +
            #     (child_data_dict.get(item['id'], {}).get('total_loose_pcs') or 0) +
            #     (child_data_dict.get(item['id'], {}).get('total_seconds_pcs') or 0) +
            #     (child_data_dict.get(item['id'], {}).get('total_shortage_pcs') or 0)
            # ),
            # 'total_pcs': item.get('total_pcs') or '-',

            # 'total_loose_pcs': item.get('loose_pcs') or '-',
            # 'total_seconds_pcs': item.get('seconds_pcs') or '-',
            # 'total_shortage_pcs': item.get('shortage_pcs') or '-',
            'status': (
                '<span class="badge bg-success">active</span>'
                if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
            )
        }
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})
   
  

   
def sales_order_edit_value(request):
    try:  
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        # if not encoded_id:
        #     return render(request, 'sales_order/update_sales_order.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        # try: 
        decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        #     print('decoded-id:',decoded_id)
        # except (ValueError, TypeError, base64.binascii.Error):
        #     return render(request, 'sales_order/update_sales_order.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
 
        # Fetch the material instance using 'tm_id'
        material_instance = child_sales_order_table.objects.filter(tm_id=material_id).first()
      
        # Fetch the parent stock instance 
        parent_stock_instance = parent_sales_order_table.objects.filter(id=material_id).first()
        print('order:',parent_stock_instance.order_no) 
    
        # Fetch active products and UOM 
        # party = party_table.objects.filter(status=1) 
        

        party = party_table.objects.filter(status=1).filter(is_stiching=1) | party_table.objects.filter(status=1).filter(is_ironing=1)

        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1)  
        style = style_table.objects.filter(status=1)
        packing_received = parent_packing_inward_table.objects.filter(status=1)


     
        print('parent-data:',parent_stock_instance)
        context = {  
            'material': material_instance, 
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            'size':size,
            'quality':quality,
            'style':style,
            # 'lot_no':lot_no, 
            'packing_received':packing_received,
            # 'combined_outward':combined_outward, 
            
        }
        return render(request, 'sales_order/update_sales_order.html', context)

    except Exception as e:
        return render(request, 'sales_order/update_sales_order.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

import json



@csrf_exempt
def update_sales_order(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')
            tm_id = request.POST.get('tm_id')

            data = json.loads(request.POST.get('order-data', '[]')) 
            print('🔹 Received order data:', data)

            parent = parent_sales_order_table.objects.filter(id=tm_id, status=1).first()
            if not parent:
                return JsonResponse({'status': 'no', 'message': 'Parent sales order not found.'})

            # Delete existing child rows
            child_sales_order_table.objects.filter(tm_id=tm_id).delete()

            total_pcs = 0
            total_amount = 0

            for row in data:
                total_pcs += float(row.get('total_pcs', 0) or 0)
                total_amount += float(row.get('amount', 0) or 0)

                child_sales_order_table.objects.create(
                    tm_id=parent.id,
                    quality_id=row.get('quality_id'),
                    style_id=row.get('style_id'),
                    size_id=row.get('size_id'),
                    box=row.get('box', 0),
                    pcs_per_box=row.get('pcs_per_box', 0),
                    box_pcs=row.get('total_pcs', 0),
                    rate=row.get('rate', 0),
                    amount=row.get('amount', 0),
                    company_id=company_id,
                    created_by=user_id,
                    created_on=timezone.now(),
                    cfyear=2025
                )

            parent.total_pcs = total_pcs
            parent.total_box = 0
            parent.sub_total = total_amount
            parent.updated_on = timezone.now()
            parent.save()

            return JsonResponse({'status': 'success', 'message': 'Sales order updated successfully!'})

        except Exception as e:
            print(f"❌ Error: {e}")
            return JsonResponse({'status': 'no', 'message': str(e)})

    return render(request, 'packing_received/add_packing_received.html')




# @csrf_exempt 
# def update_sales_order(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')
#         company_id = request.session.get('company_id')

#         try:
#             # Extract basic info
#             tm_id = request.POST.get('tm_id')
#             order_date = request.POST.get('order_date')
#             party_id = request.POST.get('customer_id')
#             remarks = request.POST.get('remarks')
#             price_list = request.POST.get('price_list')
#             packing_id = request.POST.get('packing_list')
#             work_order_no = request.POST.get('work_order_no')

#             # Parse table data (JSON string)
#             data = json.loads(request.POST.get('order-data', '[]'))
#             print('🔹 Received order data:', data)

#             # Fetch the parent record safely
#             try:
#                 material_request = parent_sales_order_table.objects.get(id=tm_id, status=1)
#             except parent_sales_order_table.DoesNotExist:
#                 return JsonResponse({'status': 'no', 'message': 'Parent sales order not found.'}, safe=False)

#             # ✅ Update parent table fields
#             material_request.order_date = order_date
#             material_request.party_id = party_id
#             material_request.remarks = remarks
#             material_request.price_list = price_list
#             material_request.updated_by = user_id
#             material_request.updated_on = timezone.now()
#             material_request.save()

#             # ✅ Delete old child entries (to replace with new)
#             child_sales_order_table.objects.filter(tm_id=tm_id).delete()

#             total_pieces = 0

#             # ✅ Create new child entries
#             for order in data:
#                 print("Processing order Data:", order)

#                 total_pcs = float(order.get('total_pcs', 0) or 0)
#                 rate = float(order.get('rate', 0) or 0)
#                 amount = float(order.get('amount', 0) or 0)

#                 child_sales_order_table.objects.create(
#                     work_order_no=work_order_no,
#                     tm_id=material_request.id,
#                     packing_received_id=packing_id,
#                     size_id=order.get('size_id'),
#                     quality_id=order.get('quality_id'),
#                     style_id=order.get('style_id'),
#                     box=order.get('box', 0),
#                     pcs_per_box=order.get('pcs_per_box', 0),
#                     box_pcs=total_pcs,
#                     rate=rate,
#                     amount=amount,
#                     created_by=user_id,
#                     created_on=timezone.now(),
#                     company_id=company_id,
#                     cfyear=2025
#                 )

#                 total_pieces += total_pcs

#             # ✅ Update totals in parent
#             material_request.total_pcs = total_pieces
#             material_request.total_box = 0
#             material_request.save()

#             return JsonResponse({'status': 'success', 'message': 'Sales order updated successfully!'})

#         except Exception as e:
#             print(f"❌ Error: {e}")
#             return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

#     # fallback for GET
#     return render(request, 'packing_received/add_packing_received.html')



# @csrf_exempt
# def update_sales_order(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')  # Prevent KeyErrors
#         company_id = request.session.get('company_id')

#         try: 
#             # Extracting Data from Request  
#             tm_id =request.POST.get('tm_id')
#             order_date = request.POST.get('order_date')
#             party_id = request.POST.get('customer_id')

#             remarks = request.POST.get('remarks')  
#             price_list = request.POST.get('price_list') 

#             packing_id = request.POST.get('packing_list') 

#             data = json.loads(request.POST.get('order-data', '[]'))

#             work_order_no = request.POST.get('work_order_no') 

#             print('Chemical Data:', data)  

    
            
#             material_request = parent_sales_order_table.objects.filter(status=1,id=tm_id)
#             material_request.order_date =order_date
           
#             total_pieces = 0
#             po_ids = set()  # Store unique PO IDs to update later
 
#             # Create Sub Table Entries
#             for order in data: 
#                 print("Processing order Data:", order)
 
#                 po_id = order.get('tm_id')  # Get PO ID
#                 po_ids.add(po_id)  # Store for updating later
 
#                 sub_entry = child_sales_order_table.objects.create(
#                     work_order_no = work_order_no,
#                     tm_id=material_request.id,  
#                     packing_received_id = packing_id,
#                     size_id=order.get('size_id'),  
#                     quality_id=order.get('quality_id'),  
#                     style_id=order.get('style_id'),  
#                     box=order.get('box'),
#                     pcs_per_box=order.get('pcs_per_box'), 
#                     box_pcs=order.get('total_pcs'),

#                     rate = order.get('rate'),
#                     amount = order.get('amount') ,

#                     created_by=user_id,
#                     created_on=timezone.now(), 
#                     company_id=company_id,
#                     cfyear=2025, 

#                 )
#                 print('sub:',sub_entry)

#                 total_pieces += order.get('total_pcs')

#             material_request.total_pcs =total_pieces
#             material_request.total_box =0
#             # Return a success response
#             return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

#         except Exception as e:
#             print(f" Error: {e}")  # Log error
#             return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

#     return render(request, 'packing_received/add_packing_received.html')


 