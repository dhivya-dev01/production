


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

from production_app.models import parent_stiching_outward_table, stiching_delivery_balance_table
from yarn.views import *
from software_app.models import *
from collections import defaultdict

# `````````````````````````````````````````````````````````````````````



def generate_inward_num_series():
    last_purchase = parent_accessory_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_number:
        match = re.search(r'INW-(\d+)', last_purchase.inward_number) 
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"INW-{next_num:03d}"




def accessory_inward(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter( Q(is_trader=1) | Q(is_supplier=1),status=1)
        product = product_table.objects.filter(status=1)

        inward_number = generate_inward_num_series
        return render(request,'inward/purchase_inward.html',{'party':party,'product':product ,'inward_no':inward_number})
    else:
        return HttpResponseRedirect("/admin")


def accessory_inward_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(
                Q(is_trader=1) | Q(is_supplier=1),
                status=1
            )    
        
        product = product_table.objects.filter(status=1)

        inward_number = generate_inward_num_series
        return render(request,'inward/accessory_inward_add.html',{'party':party,'product':product ,'inward_no':inward_number})
    else:
        return HttpResponseRedirect("/admin")






def get_accessory_po_list(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('party-id:',supplier_id)

        if supplier_id:
            child_orders = accessory_po_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).values_list('po_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(parent_accessory_po_table.objects.filter(
                id__in=child_orders,
                status=1
            ).values('id', 'po_number', 'po_name', 'party_id').order_by('-id'))

           

            totals = accessory_po_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).aggregate(
                # po_roll_wt=Sum('ord_roll_wt'),
                po_quantity=Sum('po_quantity'),
                # inward_bag=Sum('in_rolls'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            ) 

            balance_roll = (totals['po_quantity'] or 0) - (totals['inward_quantity'] or 0)

            return JsonResponse({
                'orders': orders,
                # 'po_roll_wt': balance_roll,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                # 'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})

def get_accessory_pos(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('party-id:',supplier_id)

        if supplier_id:
            child_orders = accessory_po_balance_table.objects.filter(
                party_id=supplier_id,
                # balance_quantity__gt=0
            ).values_list('po_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(parent_accessory_po_table.objects.filter(
                id__in=child_orders,
                status=1
            ).values('id', 'po_number', 'party_id').order_by('-id'))

           

            totals = accessory_po_balance_table.objects.filter(
                party_id=supplier_id,
                # balance_quantity__gt=0
            ).aggregate(
                # po_roll_wt=Sum('ord_roll_wt'),
                po_quantity=Sum('po_quantity'),
                # inward_bag=Sum('in_rolls'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            ) 

            balance_roll = (totals['po_quantity'] or 0) - (totals['inward_quantity'] or 0)

            return JsonResponse({
                'orders': orders,
                # 'po_roll_wt': balance_roll,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                # 'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
import json


@csrf_exempt
def get_accesory_po_details(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        po_list_raw = request.POST.get('po_list')
        tm_inward_id = request.POST.get('tm_id')
        print('po-id',po_list_raw,   'tm-id:',tm_inward_id)

        if not po_list_raw:
            return JsonResponse({"error": "PO list not provided"}, status=400)

        # 🔁 Handle JSON list or comma-separated string
        try:
            po_list = json.loads(po_list_raw)
            if isinstance(po_list, int):
                po_list = [po_list]
            elif not isinstance(po_list, list):
                raise ValueError("Invalid PO list format")
        except json.JSONDecodeError:
            # Fall back to CSV parsing
            po_list = [int(x) for x in po_list_raw.split(',') if x.strip().isdigit()]

        final_data = []
        orders = []

        for po_id in po_list:
            # Fetch PO metadata
            order_number = parent_accessory_po_table.objects.filter(
                id=po_id, status=1
            ).values('id', 'po_number')
            orders.extend(order_number)

            # Fetch PO items
            po_items = child_accessory_po_table.objects.filter(
                tm_id=po_id
            ).order_by('item_group_id', 'item_id', 'quality_id', 'size_id', 'color_id')

            for item in po_items:
                po_quantity = item.quantity or 0
                po_rate = item.rate or 0
                po_amount = item.amount or 0

                # Get received quantity filtered by quality, size, color
                received = child_accessory_inward_table.objects.filter(
                    po_id=po_id,
                    item_group_id=item.item_group_id,
                    item_id=item.item_id,
                    quality_id=item.quality_id,
                    size_id=item.size_id,
                    color_id=item.color_id,
                    status=1,
                    is_active=1
                ).aggregate(
                    received_quantity=Sum('quantity'), 
                    # rec_rate=('rate'),
                    received_amount=Sum('amount')
                )

                received_quantity = received['received_quantity'] or 0
                received_amount = received['received_amount'] or 0
                # received_rate = (received_amount / received_quantity) if received_quantity else 0
                received_rate =po_rate or 0 

                # Get current inward entry (same filters)
                current_inward = child_accessory_inward_table.objects.filter(
                    tm_id=tm_inward_id,
                    po_id=po_id,
                    item_group_id=item.item_group_id,
                    item_id=item.item_id,
                    quality_id=item.quality_id,
                    size_id=item.size_id,
                    color_id=item.color_id,
                    status=1,
                    is_active=1
                ).first()

                inward_quantity = current_inward.quantity if current_inward else 0
                inward_rate = current_inward.rate if current_inward else 0
                inward_amount = current_inward.amount if current_inward else 0

                # Get foreign key display values
                item_group = item_group_table.objects.filter(id=item.item_group_id).first()
                item_obj = item_table.objects.filter(id=item.item_id).first()
                quality_obj = accessory_quality_table.objects.filter(id=item.quality_id).first()
                size_obj = accessory_size_table.objects.filter(id=item.size_id).first()
                color_obj = accessory_color_table.objects.filter(id=item.color_id).first()

                final_data.append({
                    'item_group': item_group.name if item_group else '',
                    'item': item_obj.name if item_obj else '',
                    'quality': quality_obj.name if quality_obj else '',
                    'size': size_obj.name if size_obj else '',
                    'color': color_obj.name if color_obj else '',
                    'po_quantity': po_quantity,
                    'po_rate': po_rate,
                    'po_amount': po_amount,
                    'received_quantity': received_quantity,
                    'received_rate': round(received_rate, 2),
                    'received_amount': received_amount,
                    'inward_quantity': inward_quantity,
                    'inward_rate': inward_rate,
                    'inward_amount': inward_amount,
                    'item_group_id': item.item_group_id,
                    'item_id': item.item_id,
                    'quality_id': item.quality_id,
                    'size_id': item.size_id,
                    'color_id': item.color_id,
                    'po_id': po_id
                })

        return JsonResponse({
            'orders': orders,
            'po_details': final_data
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




# ``````````````````````````````````````````````````````````````````````






def get_accessory_do_list(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('outward-ids:',supplier_id)
 
        if supplier_id: 
            child_orders = stiching_delivery_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).values_list('po_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(parent_stiching_outward_table.objects.filter(
                id__in=child_orders,
                status=1 
            ).values('id', 'outward_no', 'party_id').order_by('-id'))

           

            totals = stiching_delivery_balance_table.objects.filter(
                party_id=supplier_id, 
                balance_quantity__gt=0
            ).aggregate(
                # po_roll_wt=Sum('ord_roll_wt'),
                po_quantity=Sum('po_quantity'),
                # inward_bag=Sum('in_rolls'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            ) 

            balance_roll = (totals['po_quantity'] or 0) - (totals['inward_quantity'] or 0)

            return JsonResponse({
                'orders': orders,
                # 'po_roll_wt': balance_roll,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                # 'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})






def get_packing_delivery_list(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('outward-ids:',supplier_id)
 
        if supplier_id: 
            child_orders = stiching_delivery_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).values_list('po_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(parent_stiching_outward_table.objects.filter(
                id__in=child_orders,
                status=1 
            ).values('id', 'outward_no', 'party_id').order_by('-id'))

           

            totals = stiching_delivery_balance_table.objects.filter(
                party_id=supplier_id, 
                balance_quantity__gt=0
            ).aggregate(
                # po_roll_wt=Sum('ord_roll_wt'),
                po_quantity=Sum('po_quantity'),
                # inward_bag=Sum('in_rolls'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            ) 

            balance_roll = (totals['po_quantity'] or 0) - (totals['inward_quantity'] or 0)

            return JsonResponse({
                'orders': orders,
                # 'po_roll_wt': balance_roll,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                # 'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})






# @csrf_exempt
# def get_accesory_po_details(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     try:
#         po_list_raw = request.POST.get('po_list')
#         tm_inward_id = request.POST.get('tm_id')

#         if not po_list_raw:
#             return JsonResponse({"error": "PO list not provided"}, status=400)

#         po_list = json.loads(po_list_raw)  # Convert JSON string to Python list

#         final_data = []
#         orders = []

#         for po_id in po_list:
#             order_number = parent_accessory_po_table.objects.filter(id=po_id, status=1).values('id', 'po_number')
#             orders.extend(order_number)

#             po_items = child_accessory_po_table.objects.filter(tm_id=po_id).order_by('item_group_id', 'item_id','quality_id','size_id','color_id')

#             for item in po_items:
#                 po_quantity = item.quantity or 0
#                 po_rate = item.rate or 0
#                 po_amount = item.amount or 0

#                 received = child_accessory_inward_table.objects.filter(
#                     po_id=po_id,
#                     item_group_id=item.item_group_id,
#                     item_id=item.item_id,
#                     status=1,
#                     is_active=1
#                 ).aggregate(
#                     received_quantity=Sum('quantity'),
#                     received_amount=Sum('amount')
#                 )
#                 received_quantity = received['received_quantity'] or 0
#                 received_amount = received['received_amount'] or 0
#                 received_rate = (received_amount / received_quantity) if received_quantity else 0

#                 current_inward = child_accessory_inward_table.objects.filter(
#                     tm_id=tm_inward_id,
#                     po_id=po_id,
#                     item_group_id=item.item_group_id,
#                     item_id=item.item_id,
#                     status=1,
#                     is_active=1
#                 ).first()

#                 inward_quantity = current_inward.quantity if current_inward else 0
#                 inward_rate = current_inward.rate if current_inward else 0
#                 inward_amount = current_inward.amount if current_inward else 0

#                 item_group = item_group_table.objects.filter(id=item.item_group_id).first()
#                 item_obj = item_table.objects.filter(id=item.item_id).first()
#                 quality_obj = accessory_quality_table.objects.filter(id=item.quality_id).first()
#                 size_obj = accessory_size_table.objects.filter(id=item.size_id).first()
#                 color_obj = accessory_color_table.objects.filter(id=item.color_id).first()

#                 final_data.append({
#                     'item_group': item_group.name if item_group else '',
#                     'item': item_obj.name if item_obj else '',
#                     'quality': quality_obj.name if quality_obj else '',
#                     'size': size_obj.name if size_obj else '',
#                     'color': color_obj.name if color_obj else '',
#                     'po_quantity': po_quantity,
#                     'po_rate': po_rate,
#                     'po_amount': po_amount,
#                     'received_quantity': received_quantity,
#                     'received_rate': round(received_rate, 2),
#                     'received_amount': received_amount,
#                     'inward_quantity': inward_quantity,
#                     'inward_rate': inward_rate,
#                     'inward_amount': inward_amount,
#                     'item_group_id': item.item_group_id,
#                     'item_id': item.item_id,
#                     'quality_id': item.quality_id,
#                     'size_id': item.size_id,
#                     'color_id': item.color_id,
#                     'po_id': po_id  # Needed for frontend table tracking
#                 })

#         return JsonResponse({
#             'orders': orders,
#             'po_details': final_data
#         })

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)





@csrf_exempt
def get_party_lists(request): 
    if request.method == 'POST':
        material_type = request.POST.get('material_type')
        print('material-type:',material_type)
        delivery_type = request.POST.get('delivery_type', '')
 
        if material_type == 'po':
            parties = party_table.objects.filter(
                Q(is_trader=1) | Q(is_supplier=1), 
                status=1
            )

        elif material_type == 'outward':
            if delivery_type == 'stiching':
                parties = party_table.objects.filter(status=1, is_stiching=1)
            elif delivery_type == 'packing':
                parties = party_table.objects.filter(status=1, is_ironing=1)
            else:
                parties = party_table.objects.none()
        else:
            parties = party_table.objects.none()

        data = [{"id": p.id, "name": p.name} for p in parties]
        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)


# @csrf_exempt  # Only if you don't want to handle CSRF tokens for this view (not recommended for production)
# def get_party_lists(request):
#     # material_type = request.POST.get('material_type')

#     if request.method == 'POST' and 'material_type' in request.POST: 
#         material_type = request.POST['material_type']
#         print('m-type:',material_type)
#         if material_type == 'po':
#             # parties = party_table.objects.filter(is_knitting=1, status=1).order_by('name')
#             parties = party_table.objects.filter(
#             Q(is_trader=1) | Q(is_supplier=1),
#             status=1
#         )  
#         elif material_type == 'outward': 
#             parties = party_table.objects.filter(status=1,is_stiching=1) 

#         elif material_type == 'outward': 
#             parties = party_table.objects.filter(status=1,is_ironing=1) 

#             # parties = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1).order_by('name')



#             # parties = party_table.objects.filter(is_trader=1,status=1) | party_table.objects.filter(is_mill=1,status=1)
#         else:
#             parties = party_table.objects.none()

#         data = [{"id": p.id, "name": p.name} for p in parties]
#     return JsonResponse(data, safe=False)





@csrf_exempt
def get_accesory_po_details24(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    po_id = request.POST.get('po_list')
    tm_inward_id = request.POST.get('tm_id')

    print('tm-ids:',tm_inward_id)

    if not po_id:
        return JsonResponse({"error": "PO ID not provided"}, status=400)

    try:
        order_number = parent_accessory_po_table.objects.filter(
            id=po_id, status=1
        ).values('id', 'po_number')

        # Get all items in the PO
        po_items = child_accessory_po_table.objects.filter(tm_id=po_id).order_by('item_group_id', 'item_id')

        final_data = []

        for item in po_items:
            # Get master data
            po_quantity = item.quantity or 0
            po_rate = item.rate or 0
            po_amount = item.amount or 0

            # Aggregate all received inward (excluding current inward)
            received = child_accessory_inward_table.objects.filter(
                po_id=po_id,
                item_group_id=item.item_group_id,
                item_id=item.item_id,
                status=1,
                is_active=1
            ).aggregate(
                received_quantity=Sum('quantity'),
                received_amount=Sum('amount')
            )
            received_quantity = received['received_quantity'] or 0
            received_amount = received['received_amount'] or 0
            received_rate = (received_amount / received_quantity) if received_quantity else 0

            # Get current inward values
            current_inward = child_accessory_inward_table.objects.filter(
                tm_id=tm_inward_id,
                po_id=po_id,
                item_group_id=item.item_group_id,
                item_id=item.item_id,
                status=1,
                is_active=1
            ).first()

            inward_quantity = current_inward.quantity if current_inward else 0
            inward_rate = current_inward.rate if current_inward else 0
            inward_amount = current_inward.amount if current_inward else 0

            item_group = item_group_table.objects.filter(id=item.item_group_id).first()
            item_obj = item_table.objects.filter(id=item.item_id).first()

            final_data.append({
                'item_group': item_group.name if item_group else '',
                'item': item_obj.name if item_obj else '',
                'po_quantity': po_quantity,
                'po_rate': po_rate,
                'po_amount': po_amount,
                'received_quantity': received_quantity,
                'received_rate': round(received_rate, 2),
                'received_amount': received_amount,
                'inward_quantity': inward_quantity,
                'inward_rate': inward_rate,
                'inward_amount': inward_amount,
                'item_group_id': item.item_group_id,
                'item_id': item.item_id
            })

        return JsonResponse({
            'orders': list(order_number),
            'po_details': final_data
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






@csrf_exempt
def insert_accessory_inward(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    user_id = request.session.get('user_id') 
    company_id = request.session.get('company_id')

    try:
        supplier_id = request.POST.get('supplier_id')
        remarks = request.POST.get('remarks')
        po_list = request.POST.get('po_list', 0)

        inward_date = request.POST.get('inward_date')
        receive_no = request.POST.get('receive_no') 
        receive_date = request.POST.get('receive_date')
        # ✅ Parse chemical data 
        chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

        # ✅ Generate inward number
        inward_no = generate_inward_num_series()
  
        # ✅ Create main inward record
        material_request = parent_accessory_inward_table.objects.create(
            inward_number=inward_no,
            inward_date=inward_date,
            party_id=supplier_id,
            receive_no=receive_no,
            receive_date=receive_date,
            cfyear=2025,
            po_id=po_list, 
         
            company_id=company_id,
            total_quantity=Decimal('0.00'),
            total_amount=Decimal('0.00'),
            remarks=remarks,
            created_by=user_id,
            created_on=timezone.now()
        )

        total_quantity = Decimal('0.00')
        total_amount = Decimal('0.00')

        # ✅ Loop over chemical items
        for chemical in chemical_data:
            item_group_id = chemical.get('item_group_id')
            item_id = chemical.get('item_id')
            quality_id = chemical.get('quality_id')
            size_id = chemical.get('size_id')
            color_id = chemical.get('color_id')
          

            quantity = safe_decimal(chemical.get('quantity'))
            rate = safe_decimal(chemical.get('rate'))
            amount = safe_decimal(chemical.get('amount'))

            # ✅ Create sub-inward record 
            child_accessory_inward_table.objects.create(
                tm_id=material_request.id,
                item_group_id=item_group_id,
                item_id=item_id,
                quality_id=quality_id,
                size_id=size_id,
                color_id=color_id,
               
                po_id=po_list,
                cfyear=2025,
                company_id=company_id,
                party_id=supplier_id,
                # outward_id=chemical.get('outward_id'),  # one per row here
                quantity=quantity,
                rate=rate,
                amount=amount,
                created_by=user_id,
                created_on=timezone.now() 
            )

            total_quantity += quantity
            total_amount += amount
            print('Running total_quantity:', total_quantity)
            print('Running gross_wt:', total_amount)

        # ✅ Update totals
        parent_accessory_inward_table.objects.filter(id=material_request.id).update(
            total_quantity=total_quantity,
            total_amount=total_amount
        )

        new_no = generate_inward_num_series()

        return JsonResponse({
            'status': 'success',
            'message': 'Inward entry added successfully.',
            'inward_no': new_no
        })

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong: {str(e)}'
        })





def accessory_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(parent_accessory_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="acc_inward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="accessory_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="acc_inw_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'inward_number': item['inward_number'] if item['inward_number'] else'-', 
            'receive_no': item['receive_no'] if item['receive_no'] else'-', 
            'receive_date': item['receive_date'] if item['receive_date'] else'-', 
            'po_number':  getPONumberById(parent_accessory_po_table, item['po_id'] ), 
            'party_id':getSupplier(party_table, item['party_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 




def update_tm_accessory_inward_data(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        inward_date_str = request.POST.get('inward_date')
        receive_date_str = request.POST.get('receive_date')
        receive_no = request.POST.get('receive_no')  

      

        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = parent_accessory_inward_table.objects.get(id=tm_id)
            parent_item.receive_no = receive_no  

            if inward_date_str:
                po_date = datetime.strptime(inward_date_str, '%Y-%m-%d').date()
                parent_item.inward_date = po_date
            
            if receive_date_str:
                receive_date = datetime.strptime(receive_date_str, '%Y-%m-%d').date()
                parent_item.receive_date = receive_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except parent_accessory_inward_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

 



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





def update_accessory_inward(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')

            master_id = request.POST.get('tm_id')
            # inw_date = request.POST.get('inward_date')
            # rec_no = request.POST.get('receive_no')
            # rec_date = request.POST.get('receive_date')
            party_id = request.POST.get('supplier_id')
            po_list = request.POST.get('po_list')
            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            # Get and parse table data
            chemical_data = request.POST.get('chemical_data')
            print('c-data:',chemical_data)
            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'})

            table_data = json.loads(chemical_data)

            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Step 1: Delete previous entries with status = 0
            # sub_gf_inward_table.objects.filter(tm_id=master_id).update(status=0,is_active=0)
            parent_accessory_inward_table.objects.filter(id=master_id).update(party_id=party_id,
                                                                            #   receive_no=rec_no,
                                                                            #   receive_date=rec_date,
                                                                            #   inward_date=inw_date,
                                                                              po_id = po_list)
            child_accessory_inward_table.objects.filter(tm_id=master_id).delete()

            # Step 2: Create new entries
            for row in table_data:     
                print('tot-wt:',row.get('total_wt'))

                child_accessory_inward_table.objects.create(

                    tm_id=master_id,
                    item_group_id=row.get('item_group_id'),
                    item_id=row.get('item_id'),
                    quality_id=row.get('quality_id'),
                    size_id=row.get('size_id'),
                    color_id=row.get('color_id'),
            
                    po_id=row.get('po_id'),
                    cfyear=2025,
                    company_id=company_id,
                    party_id=party_id,
                    quantity=row.get('quantity'),
                    rate=row.get('rate'),
                    amount=row.get('amount'),
              
                    status=1,
                    is_active=1,
                    created_by=user_id,
                    updated_by=user_id,
                    created_on=datetime.now(),
                    updated_on=datetime.now(),
                )

            # Step 3: Update master totals
            updated_totals = update_inwards_total(master_id)
            if 'error' in updated_totals:
                return JsonResponse({'success': False, 'error_message': updated_totals['error']})

            return JsonResponse({'success': True, **updated_totals}) 

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

 
def update_inwards_total(master_id):
    try:
        qs = child_accessory_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        if not qs.exists():
            return {'error': 'No active inward items found.'}

        # Use Django ORM's Sum aggregation
        totals = qs.aggregate(
            total_amount=Sum('amount'),
            total_quantity=Sum('quantity')
        )

        total_amount = totals['total_amount'] or Decimal('0')
        total_quantity = totals['total_quantity'] or Decimal('0')

        parent_accessory_inward_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            total_amount=total_amount,
            updated_on=datetime.now()
        )

        return {
            'total_amount': str(total_amount),
            'total_quantity': str(total_quantity),
        }

    except Exception as e:
        return {'error': str(e)}
    

@csrf_exempt
def print_accessory_inward(request):
    po_id = request.GET.get('k')
    order_id = base64.b64decode(po_id)
    print('print-id:', order_id) 

    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    total_values = get_object_or_404(parent_accessory_inward_table, id=order_id)
    customer_value = get_object_or_404(party_table, status=1, id=total_values.party_id)

    details = (
        child_accessory_inward_table.objects
        .filter(tm_id=order_id)
        .values('item_group_id', 'item_id', 'size_id','quality_id', 'color_id',
                'id', 'rate', 'quantity', 'amount')
    )
    print('details:',details)
 
    combined_details = []
    total_quantity = 0
    total_amount = 0
    item_group_names = set()   # collect unique group names

    for detail in details:
        product = get_object_or_404(item_group_table, id=detail['item_group_id'])
        item = get_object_or_404(item_table, id=detail['item_id']or 0)
        size = get_object_or_404(accessory_size_table, id=detail['size_id'])
        quality = get_object_or_404(accessory_quality_table, id=detail['quality_id'])
        color = get_object_or_404(color_table, id=detail['color_id'])

        combined_details.append({
            'item_group': product.name, 
            'item': item.name,
            'size': size.po_name,
            'quality':quality.po_name, 
            'color': color.name, 
            'quantity': detail['quantity'],
            'rate': detail['rate'],
            'amount': detail['amount'],
        })

        # ✅ Add inside the loop
        item_group_names.add(product.name)
        total_quantity += detail['quantity']
        total_amount += detail['amount']

    # join unique names with commas
    item_group_name = ", ".join(sorted(item_group_names))
    print('grp-name:', item_group_name)

    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'total_values': total_values,
        'remarks': total_values.remarks,
        'customer_name': customer_value.name, 
        'mobile_no': customer_value.mobile,
        'gstin': customer_value.gstin,
        'phone_no': customer_value.mobile,
        'city': customer_value.city,
        'state': customer_value.state,
        'pincode': customer_value.pincode,
        'address_line1': customer_value.address,
        'combined_details': combined_details,
        'company': company_table.objects.filter(status=1).first(),
        'image_url': image_url,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'item_group_name': item_group_name,
    }
    return render(request, 'inward/acc_inward_print.html', context)


