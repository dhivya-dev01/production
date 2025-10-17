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



 
def sales(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        return render(request,'sales/sales_list.html') 
    else:
        return HttpResponseRedirect("/signin")
 



def generate_sales_no():
    last_purchase = parent_sales_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.order_no:
        match = re.search(r'SO-(\d+)', last_purchase.order_no)
        if match:
            next_num = int(match.group(1)) + 1
        else: 
            next_num = 1
    else: 
        next_num = 1
 
    return f"SO-{next_num:03d}"


def add_sales(request): 
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        sales_order_no = generate_sales_no()
        party = party_table.objects.filter(status=1,is_ironing=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        return render(request,'sales/add_sales.html',
                      {'order_no':sales_order_no,
                       'party':party,
                       'quality':quality,
                       'style':style,
                       }
                    )
    else:
        return HttpResponseRedirect("/signin")
 

# def get_customer_sales_orders(request):
#     party_id = request.POST.get('customer_id')

#     if not party_id:
#         return JsonResponse({'status': 'error', 'message': 'Missing Customer list ID'})

#     try:
#         # Fetch inward data first
#         # inward_data = child.objects.filter(tm_id=packing_list_id)
#         party = party_table.objects.filter(status=1, id=party_id).first()
#         order = get_object_or_404(parent_sales_order_table.objects.filter(status=1, party_id=party_id))
#         print('orders:',order)
#         if not party or not order:
#             return JsonResponse({'status': 'error', 'message': 'Party or order not found'})

#         # Get the related price list
#         price = price_list_table.objects.filter(status=1, id=party.price_list_id).first()
#         if not price:
#             return JsonResponse({'status': 'error', 'message': 'Price list not found'})
 
#         data = []
#         for item in order:
         
#             # Get rate value
#             rate_value = (
#                 price_list_range_table.objects.filter(
#                     quality_id=order.quality_id,
#                     style_id=order.style_id,
#                     size_id=item.size_id,
#                     price_list_id=price.id,
#                     status=1
#                 )
#                 .values_list('rate', flat=True)
#                 .first()
#             )

#             data.append({
                
#                 'order_id':item.order_id,
#                 'order_no':item.order_no,

#                 'rate': rate_value or 0,

#             })

#         return JsonResponse({'status': 'success', 'data': data})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)})



def get_customer_sales_orders(request):
    party_id = request.POST.get('customer_id')

    if not party_id:
        return JsonResponse({'status': 'error', 'message': 'Missing Customer list ID'})

    try:
        # Fetch inward data first
        # inward_data = child.objects.filter(tm_id=packing_list_id)
        party = party_table.objects.filter(status=1, id=party_id).first()

        orders = parent_sales_order_table.objects.filter(status=1, party_id=party_id)



        # order = get_object_or_404(parent_sales_order_table.objects.filter(status=1, party_id=party_id))
        print('orders:',orders)
        if not party or not orders:
            return JsonResponse({'status': 'error', 'message': 'Party or order not found'})

        # Get the related price list
        price = price_list_table.objects.filter(status=1, id=party.price_list_id).first()
        if not price:
            return JsonResponse({'status': 'error', 'message': 'Price list not found'})
 

        data = []
        for item in orders:
            # rate_value = (
            #     price_list_range_table.objects.filter(
            #         quality_id=item.quality_id,
            #         style_id=item.style_id,
            #         size_id=item.size_id,
            #         price_list_id=price.id,
            #         status=1
            #     )
            #     .values_list('rate', flat=True)
            #     .first()
            # )

            data.append({
                'order_id': item.id,
                'order_no': item.order_no,
                # 'rate': rate_value or 0,
            })

        # data = []
        # for item in orders:
         
        #     # Get rate value
        #     rate_value = (
        #         price_list_range_table.objects.filter(
        #             quality_id=order.quality_id,
        #             style_id=order.style_id,
        #             size_id=item.size_id,
        #             price_list_id=price.id,
        #             status=1
        #         )
        #         .values_list('rate', flat=True)
        #         .first()
        #     )

        #     data.append({
                
        #         'order_id':item.order_id,
        #         'order_no':item.order_no,

        #         'rate': rate_value or 0,

        #     })

        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



from django.utils.timezone import make_aware, is_naive

 
def getSupplier(tbl, supplier_id):
    try: 
        party = tbl.objects.get(id=supplier_id).name 
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party

def sales_ajax_list(request):   
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

            date_filter = Q(order_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
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
    queryset = parent_sales_table.objects.filter(status=1).filter(query)
    child_data_map = child_sales_table.objects.filter(

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
        'id', 'order_no', 'order_date', 'party_id',
        'sales_order_id', 'total_box','total_pcs',
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
            
         

            'sales_order': (
                getInward_entryNoById(parent_sales_order_table, item['sales_order_id'])),

            'party': getSupplier(party_table, item['party_id']),
            # 'quality': getSupplier(quality_table, item['quality_id']),
            # 'style': getSupplier(style_table, item['style_id']), 
            'total_box': item.get('total_box') or '-',
            'total_pcs':item.get('total_pcs') or '-',
           
            'status': (
                '<span class="badge bg-success">active</span>'
                if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
            )
        }
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})
  
@csrf_exempt
def get_sales_order_data(request):
    sales_order_id = request.POST.get('sales_order_id')
    party_id = request.POST.get('party_id')

    if not sales_order_id or not party_id:
        return JsonResponse({'status': 'error', 'message': 'Missing sales_order_id or party_id'})

    try:
        parent_order = get_object_or_404(parent_sales_order_table, id=sales_order_id, party_id=party_id, status=1)
        party = get_object_or_404(party_table, id=party_id, status=1)
        price_list = get_object_or_404(price_list_table, id=party.price_list_id, status=1)

        child_items = child_sales_order_table.objects.filter(tm_id=parent_order.id, status=1)
        if not child_items.exists():
            return JsonResponse({'status': 'error', 'message': 'No child sales order items found'})

        data = []
        valid_rate_found = False

        for item in child_items:
            rate = price_list_range_table.objects.filter(
                quality_id=item.quality_id,
                style_id=item.style_id,
                size_id=item.size_id,
                price_list_id=price_list.id,
                status=1
            ).values_list('rate', flat=True).first() or 0

            if rate > 0:
                valid_rate_found = True

            box_qty = int(getattr(item, 'box_qty', 0) or 0)
            pcs_per_box = int(getattr(item, 'pcs_per_box', 0) or 0)
            total_pcs = int(getattr(item, 'total_pcs', 0) or 0)
            box_pcs = box_qty * pcs_per_box

            # Get size name
            size_name = ''
            if item.size_id:
                size_obj = size_table.objects.filter(id=item.size_id).first()
                size_name = size_obj.name if size_obj else ''

            quality = quality_table.objects.filter(status=1, id=item.quality_id).first()
            style = style_table.objects.filter(status=1, id=item.style_id).first()
            data.append({
                'size_name': size_name,
                'size_id': item.size_id,
                'box_qty': box_qty,
                'pcs_per_box': pcs_per_box,
                'box_pcs':item.box_pcs,
                'rate':item.rate,
                'tax':5,
                # 'box_pcs': box_pcs,
                'total_pcs': item.box_pcs,
                'sales_order_id': sales_order_id,
                # 'rate': rate,
                'quality_id':item.quality_id,
                'style_id':item.style_id,
                'quality':quality.name,
                'style':style.name,

            })

        if not valid_rate_found:
            return JsonResponse({
                'status': 'error',
                'message': 'The selected Style does not belong to the selected Quality. Please choose a valid combination.'
            })

        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})




def generate_sales_no():
    last_purchase = parent_sales_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.order_no:
        match = re.search(r'SO-(\d+)', last_purchase.order_no)
        if match:
            next_num = int(match.group(1)) + 1
        else: 
            next_num = 1
    else: 
        next_num = 1
 
    return f"SO-{next_num:03d}"



@csrf_exempt
def insert_sales(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try: 
            # Extracting Data from Request  
            order_date = request.POST.get('order_date')
            party_id = request.POST.get('customer_id')

            remarks = request.POST.get('remarks')  
            # price_list = request.POST.get('price_list') 

            sales_order_id = request.POST.get('sales_order_id') 

       
            data = json.loads(request.POST.get('order-data', '[]'))


            print('Chemical Data:', data)  

 
            inward_no = generate_sales_no()
            
            # Create Parent Entry (gf_inward_table)
            material_request = parent_sales_table.objects.create(
                order_no = inward_no.upper(),
                order_date=order_date,   
                
                sales_order_id = sales_order_id, 
                party_id = party_id,
              
                company_id=company_id,  
                cfyear = 2025,  
              
                total_box=request.POST.get('sub_total'),
                total_pcs=request.POST.get('total_pcs'),
                      
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            ) 
            print('m-req:',material_request)

            po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for order in data:
                print("Processing order Data:", order)
 
                po_id = order.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later
 
                sub_entry = child_sales_table.objects.create(
                    tm_id=material_request.id,  
                    sales_order_id = sales_order_id,
                    size_id=order.get('size_id',0),  
                    quality_id=order.get('quality_id'),  
                    style_id=order.get('style_id'),  
                    box=order.get('box'),
                    pcs_per_box=order.get('pcs_per_box'), 
                    box_pcs=order.get('total_pcs'),

                    rate = order.get('rate'),
                    amount = order.get('amount') ,

                    created_by=user_id,
                    created_on=timezone.now(), 
                    company_id=company_id,
                    cfyear=2025, 

                )
                print('sub:',sub_entry)


            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'packing_received/add_packing_received.html')

