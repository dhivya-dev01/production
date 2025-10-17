from unittest import result
from cairo import Status
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
from company.models import *
import cutting_entry
from employee.models import *

from grey_fabric.models import *

from django.utils.timezone import make_aware

from accessory.views import quality, quality_prg_size_list
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


def stiching_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_stiching=1)
        fabric_program = fabric_program_table.objects.filter(status=1) 

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        lot = (
            parent_stiching_outward_table.objects
            .filter(status=1)
            .values('work_order_no')  # Group by work_order_no
            .annotate(
                total_gross_wt=Sum('total_quantity'),
             
            )   
            .order_by('work_order_no')
        )
        cutting = cutting_entry_table.objects.filter(status=1)
        return render(request,'stiching_outward/stiching_delivery.html',{'party':party,'fabric_program':fabric_program,'lot':lot,'quality':quality,'style':style,'cutting':cutting})
    else:
        return HttpResponseRedirect("/admin")
    



def generate_outward_num_series(): 
    last_purchase = parent_stiching_outward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.outward_no:
        match = re.search(r'DO-(\d+)', last_purchase.outward_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
 
    return f"DO-{next_num:03d}"


def stiching_delivery_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_stiching=1) 
        packing_party = party_table.objects.filter(status=1,is_ironing=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 

        outward_no = generate_outward_num_series
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        cutting_entry = cutting_entry_table.objects.filter(status=1)
        return render(request,'stiching_outward/add_stiching_delivery.html',{'party':party,'fabric_program':fabric_program,'outward_no':outward_no,'color':color
                                                               ,'packing_party':packing_party   ,'cutting_entry':cutting_entry,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
     



# def get_cutting_entry_available_list(request):
#     if request.method == 'POST' and 'party_id' in request.POST:
#         party_id = request.POST['party_id']
#         print('party-:',party_id)

        
#         child_orders = cutting_entry_balance_table.objects.filter(
#             balance_quantity__gt=0
#         ).values_list('entry_id', flat=True)
 
#         orders = list(cutting_entry_table.objects.filter(
#             id__in=child_orders,
#             status=1
#         ).values('id', 'cutting_no','work_order_no').order_by('-id'))

        
        
#         for order in orders:

#             # order['mill_name'] = mill_map.get(order['mill_id'], '')

#             totals = cutting_entry_balance_table.objects.filter(
#                 # party_id=party_id,
#                 balance_quantity__gt=0 
#             ).aggregate(
#                 po_quantity=Sum('po_quantity'), 
#                 inward_quantity=Sum('in_quantity'),
#                 balance_quantity=Sum('balance_quantity')
#             )


#             return JsonResponse({
#                 'orders': orders,
#                 'balance_quantity': float(totals['balance_quantity'] or 0),
#                 'po_quantity': float(totals['balance_quantity'] or 0),
#                 'inward_quantity': float(totals['inward_quantity'] or 0)
#             })


#     return JsonResponse({'orders': []})

# SELECT 
                    #     COALESCE(SUM(Y.total_out_quantity),0) - COALESCE(SUM(Y.total_received_quantity),0) AS available_stock_quantity
                    # FROM (
                    #     SELECT 
                    #         ce.tm_id AS entry_id,
                    #         SUM(ce.quantity) AS total_out_quantity,
                    #         0 AS total_received_quantity
                    #     FROM tx_stiching_outward ce
                    #     WHERE ce.status = 1 AND ce.entry_id = %s AND ce.quantity > 0
                    #     GROUP BY ce.tm_id

                    #     UNION ALL

                    #     SELECT 
                    #         so.outward_id AS entry_id,
                    #         0 AS total_out_quantity,
                    #         SUM(so.quantity) AS total_received_quantity
                    #     FROM tx_stiching_inward so
                    #     WHERE so.status = 1 AND so.outward_id = %s AND so.quantity > 0
                    #     GROUP BY so.outward_id
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from django.db import connection

def get_cutting_entry_available_list(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('party-:', party_id)

        # Step 1: Get all entry_ids with balance_quantity > 0
        child_orders = cutting_entry_balance_table.objects.filter(
            balance_quantity__gt=0
        ).values_list('entry_id', flat=True)

        # Step 2: Filter IDs with available_stock_quantity > 0 using raw SQL
        valid_ids = []
        for entry_id in child_orders:
            with connection.cursor() as cursor:
                cursor.execute("""
                               
                    SELECT 
                        Y.entry_id,
                        COALESCE(SUM(Y.total_out_quantity), 0) AS total_out_quantity,
                        COALESCE(SUM(Y.total_received_quantity), 0) AS total_received_quantity,
                        COALESCE(SUM(Y.total_out_quantity), 0) - COALESCE(SUM(Y.total_received_quantity), 0) AS available_stock_quantity
                    FROM (
                        -- Cutting entry (outward qty)
                        SELECT 
                            ce.tm_id AS entry_id,
                            SUM(ce.quantity) AS total_out_quantity,
                            0 AS total_received_quantity
                        FROM tx_cutting_entry ce
                        WHERE ce.status = 1 
                        AND ce.tm_id = %s 
                        AND ce.quantity > 0
                        GROUP BY ce.tm_id
 
                        UNION ALL 

                        -- Stitching outward (received qty)
                        SELECT 
                            tx.entry_id AS entry_id,
                            0 AS total_out_quantity,
                            SUM(tx.quantity) AS total_received_quantity
                        FROM tx_stiching_outward tx
                        WHERE tx.status = 1 
                        AND tx.entry_id = %s 
                        AND tx.quantity > 0
                        GROUP BY tx.entry_id
                    ) Y
                    GROUP BY Y.entry_id;


                    # 
                    ) AS Y
                """, [entry_id, entry_id])
                row = cursor.fetchone()
                available_stock_quantity = row[0] if row else 0

                if available_stock_quantity > 0:
                    valid_ids.append(entry_id)

        # Step 3: Fetch order data only for valid_ids
        orders = list(cutting_entry_table.objects.filter(
            id__in=valid_ids,
            status=1
        ).values('id', 'cutting_no', 'work_order_no').order_by('-id'))

        # Step 4: Totals from balance table for these valid entries
        totals = cutting_entry_balance_table.objects.filter(
            entry_id__in=valid_ids,
            balance_quantity__gt=0
        ).aggregate(
            po_quantity=Sum('po_quantity'),
            inward_quantity=Sum('in_quantity'),
            balance_quantity=Sum('balance_quantity')
        ) 

        return JsonResponse({
            'orders': orders,
            'balance_quantity': float(totals['balance_quantity'] or 0),
            'po_quantity': float(totals['po_quantity'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0)
        })

    return JsonResponse({'orders': []})

# def get_cutting_entry_available_list(request):
#     if request.method == 'POST' and 'party_id' in request.POST:
#         party_id = request.POST['party_id']
#         print('party-:', party_id)

#         # Step 1: Find child orders that still have balance > 0
#         child_orders = cutting_entry_balance_table.objects.filter(
#             party_id=party_id,
#             balance_quantity__gt=0
#         ).values_list('entry_id', flat=True)

#         print('entry:',child_orders)
 
#         # Step 2: Get main orders
#         orders = list(cutting_entry_table.objects.filter(
#             id__in=child_orders,
#             status=1
#         ).values('id', 'cutting_no', 'work_order_no').order_by('-id'))

#         valid_orders = []
#         # Step 3: Validate available stock for each entry
#         for entry_id in child_orders:
#             with connection.cursor() as cursor:
#                 query = """
#                     SELECT 
#                         COALESCE(SUM(Y.total_out_quantity),0) - COALESCE(SUM(Y.total_received_quantity),0) AS available_stock_quantity
#                     FROM (
#                         -- Outward quantity
#                         SELECT 
#                             ce.tm_id AS entry_id,
#                             SUM(ce.quantity) AS total_out_quantity,
#                             0 AS total_received_quantity
#                         FROM tx_stiching_outward ce
#                         WHERE ce.status = 1 AND ce.tm_id = %s AND ce.quantity > 0
#                         GROUP BY ce.tm_id

#                         UNION ALL

#                         -- Inward quantity
#                         SELECT 
#                             so.entry_id,
#                             0 AS total_out_quantity,
#                             SUM(so.quantity) AS total_received_quantity
#                         FROM tx_stiching_inward so
#                         WHERE so.status = 1 AND so.entry_id = %s AND so.quantity > 0
#                         GROUP BY so.entry_id
#                     ) AS Y
#                 """
#                 cursor.execute(query, [entry_id, entry_id])
#                 row = cursor.fetchone()
#                 available_stock_quantity = row[0] if row else 0

#                 if available_stock_quantity > 0:
#                     valid_orders.append(entry_id)

#         # Step 4: Keep only valid orders
#         orders = [order for order in orders if order['id'] in valid_orders]

#         # Step 5: Totals for this party
#         totals = cutting_entry_balance_table.objects.filter(
#             party_id=party_id,
#             balance_quantity__gt=0
#         ).aggregate(
#             po_quantity=Sum('po_quantity'),
#             inward_quantity=Sum('in_quantity'),
#             balance_quantity=Sum('balance_quantity')
#         )

#         return JsonResponse({
#             'orders': orders,
#             'balance_quantity': float(totals['balance_quantity'] or 0),
#             'po_quantity': float(totals['po_quantity'] or 0),
#             'inward_quantity': float(totals['inward_quantity'] or 0)
#         })

#     return JsonResponse({'orders': []})





# def get_st_delivery_available_list(request):
#     if request.method == 'POST' and 'party_id' in request.POST:
#         party_id = request.POST['party_id']
#         print('party-:',party_id)

        
#         child_orders = stiching_delivery_balance_table.objects.filter(
#             balance_quantity__gt=0
#         ).values_list('outward_id', flat=True)
 
#         orders = list(parent_stiching_outward_table.objects.filter(
#             id__in=child_orders,
#             status=1
#         ).values('id', 'outward_no','work_order_no').order_by('-id'))

        
        
#         for order in orders:

#             # order['mill_name'] = mill_map.get(order['mill_id'], '')

#             totals = stiching_delivery_balance_table.objects.filter(
#                 # party_id=party_id,
#                 balance_quantity__gt=0 
#             ).aggregate(
#                 po_quantity=Sum('po_quantity'), 
#                 inward_quantity=Sum('in_quantity'),
#                 balance_quantity=Sum('balance_quantity')
#             )

#             return JsonResponse({
#                 'orders': orders,
#                 'balance_quantity': float(totals['balance_quantity'] or 0),
#                 'po_quantity': float(totals['balance_quantity'] or 0),
#                 'inward_quantity': float(totals['inward_quantity'] or 0)
#             })

#     return JsonResponse({'orders': []})


def get_stitching_outward_list(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_ironing=1)
       
        stitching = parent_stiching_outward_table.objects.filter(status=1)
        return render(request,'folding_delivery/folding_delivery.html',{'party':party,'stitching':stitching})
    else:
        return HttpResponseRedirect("/admin")
    


from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import F, Q, Sum, Value
from django.db.models.functions import Coalesce

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q, F, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper

# @csrf_exempt
# def get_st_delivery_available_list(request):
#     if request.method == 'POST':
#         party_id = request.POST.get('party_id')
#         if not party_id:
#             return JsonResponse({'error': 'Missing party_id'}, status=400)

#         # Query stitching outwards for the given party and status=1
#         stitching_outwards = parent_stiching_outward_table.objects.filter(
#             status=1,
#             party_id=party_id
#         ).annotate(
#             folding_total=Coalesce(
#                 Sum('foldings__total_quantity', filter=Q(foldings__status=1)),
#                 Value(0),
#                 output_field=DecimalField()
#             )
#         ).annotate(
#             available_balance=ExpressionWrapper(
#                 F('total_quantity') - F('folding_total'),
#                 output_field=DecimalField()
#             )
#         ).filter(
#             available_balance__gt=0
#         )

#         filtered_orders = []
#         total_po_quantity = 0
#         total_inward_quantity = 0  # Not tracked here, set to 0
#         total_balance_quantity = 0

#         for outward in stitching_outwards:
#             filtered_orders.append({
#                 'id': outward.id,
#                 'outward_no': outward.outward_no,
#                 'work_order_no': outward.work_order_no
#             })

#             total_po_quantity += outward.total_quantity
#             total_balance_quantity += outward.available_balance

#         return JsonResponse({
#             'orders': filtered_orders,
#             'po_quantity': float(total_po_quantity),
#             'inward_quantity': float(total_inward_quantity),
#             'balance_quantity': float(total_balance_quantity)
#         })

#     return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def get_st_delivery_available_list(request):
#     if request.method == 'POST':
#         party_id = request.POST.get('party_id')
#         if not party_id:
#             return JsonResponse({'error': 'Missing party_id'}, status=400)


#         # Fetch all relevant outward records
#         stitching_outwards = parent_stiching_outward_table.objects.filter(
#             status=1,
#             party_id=party_id
#         )

#         filtered_orders = []
#         total_po_quantity = 0
#         total_balance_quantity = 0

#         for outward in stitching_outwards:
            
#             folding_total = parent_folding_delivery_table.objects.filter(
#                 stitching_outward_id=outward.id,
#                 status=1
#             ).aggregate(
#                 total=Coalesce(Sum('total_quantity'), Value(0))
#             )['total']

#             available_balance = outward.total_quantity - folding_total

#             if available_balance > 0:
#                 filtered_orders.append({
#                     'id': outward.id,
#                     'outward_no': outward.outward_no,
#                     'work_order_no': outward.work_order_no
#                 })

#                 total_po_quantity += outward.total_quantity
#                 total_balance_quantity += available_balance 

#         return JsonResponse({
#             'orders': filtered_orders,
#             'po_quantity': float(total_po_quantity),
#             'inward_quantity': 0,
#             'balance_quantity': float(total_balance_quantity)
#         })

#         # # ````````````````````````````````````/
#         # # Step 1: Filter outward records for this party with status = 1
#         # stitching_outwards = parent_stiching_outward_table.objects.filter(
#         #     status=1,
#         #     party_id=party_id
#         # ).annotate(
#         #     folding_total=Coalesce(
#         #         Sum('foldings__total_quantity', filter=Q(foldings__status=1)),  # related_name='foldings' is required
#         #         Value(0)
#         #     )
#         # ).annotate(
#         #     available_balance=F('total_quantity') - F('folding_total')
#         # ).filter(
#         #     available_balance__gt=0
#         # )

#         # # Step 2: Prepare JSON data
#         # filtered_orders = []
#         # total_po_quantity = 0
#         # total_inward_quantity = 0  # Not tracked here
#         # total_balance_quantity = 0

#         # for outward in stitching_outwards:
#         #     filtered_orders.append({
#         #         'id': outward.id,
#         #         'outward_no': outward.outward_no,
#         #         'work_order_no': outward.work_order_no
#         #     })

#         #     total_po_quantity += outward.total_quantity
#         #     total_balance_quantity += outward.available_balance

#         # return JsonResponse({
#         #     'orders': filtered_orders,
#         #     'po_quantity': float(total_po_quantity),
#         #     'inward_quantity': float(total_inward_quantity),
#         #     'balance_quantity': float(total_balance_quantity)
#         # })

#     return JsonResponse({'error': 'Invalid request method'}, status=405) 


@csrf_exempt
def get_st_delivery_available_list(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('party-:', party_id)

        # Get all outward IDs with some remaining stitching balance
        child_orders = stiching_delivery_balance_table.objects.filter(
            # balance_quantity__gt=0
        ).values_list('outward_id', flat=True).distinct()

        # Now iterate through each outward and compute available weight
        filtered_orders = []
        total_po_quantity = 0
        total_inward_quantity = 0
        total_balance_quantity = 0

        for outward_id in child_orders:
            # Total stitching weight for this outward 
            stitching_totals = stiching_delivery_balance_table.objects.filter(
                outward_id=outward_id
            ).aggregate(
                total_po=Sum('po_quantity'),
                total_in=Sum('in_quantity'),
                total_balance=Sum('balance_quantity')
            )

            # Total folding weight already done for this outward
            folding_totals = parent_folding_delivery_table.objects.filter(
                stitching_outward_id=outward_id, 
                status=1
            ).aggregate(
                total_folding=Sum('total_quantity')
            )

            stiching_wt = stitching_totals['total_balance'] or 0
            folding_wt = folding_totals['total_folding'] or 0
            available_wt = stiching_wt - folding_wt

            print(f"Outward {outward_id} → Stitching: {stiching_wt}, Folding: {folding_wt}, Available: {available_wt}")

            if available_wt > 0:
                # Include this outward order
                outward_data = parent_stiching_outward_table.objects.filter(
                    id=outward_id,
                    status=1
                ).values('id', 'outward_no', 'work_order_no').first()

                if outward_data:
                    filtered_orders.append(outward_data)

                    # For totals
                    total_po_quantity += stitching_totals['total_po'] or 0
                    total_inward_quantity += stitching_totals['total_in'] or 0
                    total_balance_quantity += available_wt

        return JsonResponse({
            'orders': filtered_orders,
            'po_quantity': float(total_po_quantity),
            'inward_quantity': float(total_inward_quantity),
            'balance_quantity': float(total_balance_quantity)
        })

    return JsonResponse({'orders': []})



def get_cutting_entry_available(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('party-:',party_id)

        
        child_orders = cutting_entry_balance_table.objects.filter(
            # balance_quantity__gt=0
        ).values_list('entry_id', flat=True)
 
        orders = list(cutting_entry_table.objects.filter(
            id__in=child_orders,
            status=1
        ).values('id', 'cutting_no','work_order_no').order_by('-id'))

        

        for order in orders:

            # order['mill_name'] = mill_map.get(order['mill_id'], '')

            totals = cutting_entry_balance_table.objects.filter(
                # party_id=party_id,
                # balance_quantity__gt=0  
            ).aggregate(
                po_quantity=Sum('po_quantity'), 
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            )

            return JsonResponse({
                'orders': orders,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Optional if you're using @csrf_exempt

# def get_cutting_entry_quality_style_list(request):
#     if request.method == 'POST' and 'entry_id' in request.POST:
#         entry_id = request.POST['entry_id']
#         print('Received entry_id:', entry_id)

#         try:
#             inward = cutting_entry_table.objects.get(status=1, id=entry_id)
#         except cutting_entry_table.DoesNotExist:
#             return JsonResponse({'error': 'Invalid entry_id'}, status=404)
#         if inward:
#             child_data = sub_cutting_entry_table.objects.filter(status=1,tm_id=inward.id)
#             inward_colors = child_data.color_id
#             print('inw-colors:',inward_colors) 
#         else:
#             inward_colors = 0

#         fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id','name').first()
#         quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
#         style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()

#         return JsonResponse({
#             'quality': quality if quality else None,
#             'style': style if style else None,
#             'fabric': fabric if fabric else None,
#             'lot_no':inward.lot_no,
#             'inw_colors':inward_colors,
#         })

#     return JsonResponse({'error': 'Invalid request'}, status=400)


# ``````````````````````````````````````````````````````````````````````````````````````
from django.http import JsonResponse
from django.db.models import F


def get_cutting_entry_quality_style_list(request):
    if request.method == 'POST' and 'entry_id' in request.POST:
        entry_id = request.POST['entry_id']
        print('Received entry_id:', entry_id)

        try:
            inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        except cutting_entry_table.DoesNotExist:
            return JsonResponse({'error': 'Invalid entry_id'}, status=404)

        # Query all child data to get unique color_ids
        child_data_colors = sub_cutting_entry_table.objects.filter(
            status=1, 
            tm_id=inward.id
        ).values_list('color_id', flat=True).distinct()

        # Get color details (id and name) for the unique color_ids
        inward_colors = color_table.objects.filter(
            status=1, 
            id__in=child_data_colors
        ).values('id', 'name') 

        print('inw-colors:', list(inward_colors))

        # fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        # quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        # style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()

        # quality_prg = quality_program_table.objects.filter(status=1,qualtity_id=inward.quality_id,style_id=inward.style_id).first()
        # sub_q_prg = sub_quality_program_table.objects.filter(status=1,tm_id=quality_prg.id)
        # sizes = sub_q_prg.sizes_id 

        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()

        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=inward.quality_id, style_id=inward.style_id
        ).first()

        # Make sure quality_prg is not None
        # if quality_prg:
        #     sub_q_prg = sub_quality_program_table.objects.filter(status=1, tm_id=quality_prg.id)
        #     sizes = sub_q_prg.values_list('size_id', flat=True) 
        #     size_list = size_table.objects.filter(status=1,id=sizes).values('id', 'name')
        # else:
        #     sizes = []


        if quality_prg:
            sub_q_prg = sub_quality_program_table.objects.filter(status=1, tm_id=quality_prg.id)
            sizes = sub_q_prg.values_list('size_id', flat=True)
            # cutting_size = sub_cutting_entry_table.objec
            size_list = size_table.objects.filter(status=1, id__in=sizes).values('id', 'name')
        else:
            size_list = []



        return JsonResponse({
            'quality': quality if quality else None,
            'style': style if style else None,
            'fabric': fabric if fabric else None,
            'lot_no': inward.lot_no, 
            'inw_colors': list(inward_colors),
            'sizes': list(size_list)
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)






def get_st_delivery_quality_style_list(request):
    if request.method == 'POST' and 'entry_id' in request.POST:
        entry_id = request.POST['entry_id']
        print('Received entry_id:', entry_id)

        try: 
            inward = parent_stiching_outward_table.objects.get(status=1, id=entry_id)
            cutting_entry = cutting_entry_table.objects.get(status=1, id=inward.cutting_entry_id)
            print('c-e:',cutting_entry) 
        except parent_stiching_outward_table.DoesNotExist:
            return JsonResponse({'error': 'Invalid entry_id'}, status=404)

        # Query all child data to get unique color_ids
        child_data_colors = child_stiching_outward_table.objects.filter(
            status=1, 
            tm_id=inward.id
        ).values_list('color_id', flat=True).distinct()

        # Get color details (id and name) for the unique color_ids
        inward_colors = color_table.objects.filter(
            status=1, 
            id__in=child_data_colors
        ).values('id', 'name') 

        print('inw-colors:', list(inward_colors))

        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()

        quality_prg = quality_program_table.objects.filter(
            status=1, quality_id=inward.quality_id, style_id=inward.style_id
        ).first()

       
        if quality_prg:
            sub_q_prg = sub_quality_program_table.objects.filter(status=1, tm_id=quality_prg.id)
            sizes = sub_q_prg.values_list('size_id', flat=True)
            # cutting_size = child_stiching_outward_table.objec
            size_list = size_table.objects.filter(status=1, id__in=sizes).values('id', 'name')
        else:
            size_list = []

        return JsonResponse({
            'quality': quality if quality else None,
            'style': style if style else None,
            'fabric': fabric if fabric else None,
            'lot_no': cutting_entry.lot_no, 
            'inw_colors': list(inward_colors),
            'sizes': list(size_list)
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)



# ``````````````````````````````````````````````````````````````````````````````````````````````````````````````
# def get_cutting_entry_quality_style_list(request):
#     if request.method == 'POST' and 'entry_id' in request.POST:
#         entry_id = request.POST['entry_id']
#         print('Received entry_id:', entry_id)

#         try:
#             inward = cutting_entry_table.objects.get(status=1, id=entry_id)
#         except cutting_entry_table.DoesNotExist:
#             return JsonResponse({'error': 'Invalid entry_id'}, status=404)

#         # Query all child data related to the inward entry
#         child_data = sub_cutting_entry_table.objects.filter(status=1, tm_id=inward.id)

#         # Create a list of color_ids from the child_data queryset
#         inward_colors = [row.color_id for row in child_data]
#         colors = color_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
#         print('inw-colors:', inward_colors)

#         fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
#         quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
#         style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()

#         return JsonResponse({
#             'quality': quality if quality else None,
#             'style': style if style else None,
#             'fabric': fabric if fabric else None,
#             'lot_no': inward.lot_no,
#             'inw_colors': inward_colors,
#         })

#     return JsonResponse({'error': 'Invalid request'}, status=400)


from django.http import JsonResponse
from django.db import connection

from django.http import JsonResponse
from django.db import connection



from django.http import JsonResponse
from django.db import connection

def get_cutting_stock_modal(request):
    entry_id = request.POST.get('entry_id')
    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

    try:
        query = """
            SELECT 
                entry_id,
                size_id,
                size_name,
                color_id,
                color_name,
                SUM(in_quantity) AS total_in_quantity,
                SUM(out_quantity) AS total_out_quantity,
                (SUM(in_quantity) - SUM(out_quantity)) AS available_stock_quantity
            FROM (
                SELECT 
                    s.tm_id AS entry_id,
                    s.size_id,
                    sz.name AS size_name,
                    s.color_id,
                    cl.name AS color_name,
                    SUM(s.quantity) AS in_quantity,
                    0 AS out_quantity
                FROM tx_cutting_entry s
                LEFT JOIN size sz ON sz.id = s.size_id
                LEFT JOIN color cl ON cl.id = s.color_id
                WHERE s.status = 1 AND s.tm_id = %s
                GROUP BY s.tm_id, s.size_id, sz.name, s.color_id, cl.name

                UNION ALL

                SELECT 
                    so.entry_id, 
                    so.size_id,
                    sz.name AS size_name,
                    so.color_id,
                    cl.name AS color_name,
                    0 AS in_quantity,
                    SUM(so.quantity) AS out_quantity
                FROM tx_stiching_outward so
                LEFT JOIN size sz ON sz.id = so.size_id
                LEFT JOIN color cl ON cl.id = so.color_id
                WHERE so.status = 1 AND so.entry_id = %s
                GROUP BY so.entry_id, so.size_id, sz.name, so.color_id, cl.name
            ) AS combined_data
            GROUP BY entry_id, size_id, size_name, color_id, color_name
            HAVING (SUM(in_quantity) - SUM(out_quantity)) 
              --  > 0
        """ 
        params = [entry_id, entry_id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            print('entry-data:',results)
        data = [dict(zip(columns, row)) for row in results]


        
        try:
            inward = cutting_entry_table.objects.get(status=1, id=entry_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
        except cutting_entry_table.DoesNotExist:
            quality = None
            style = None 
            fabric=None


    
        return JsonResponse({'status': 'success', 'data': data,
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else '',
            'fabric':fabric,
        })
     
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



@csrf_exempt
def delete_stiching_entry(request):
    tm_id = request.POST.get('tm_id')
    entry_id = request.POST.get('entry_id')
    color_id = request.POST.get('color_id')
    size_id = request.POST.get('size_id')

    if not all([tm_id, entry_id, color_id, size_id]):
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'})

    try:
        with connection.cursor() as cursor:
            delete_query = """
                DELETE FROM tx_stiching_outward
                WHERE tm_id = %s AND entry_id = %s AND color_id = %s AND size_id = %s AND status = 1
            """
            cursor.execute(delete_query, [tm_id, entry_id, color_id, size_id])

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



def get_stiching_delivery_data(request):
    tm_id = request.POST.get('tm_id')
    entry_id = request.POST.get('entry_id')
    if not tm_id or not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID and TM ID are required'})

    try:
        with connection.cursor() as cursor:

            # Get data for this entry + tm_id
            query_present = """
                SELECT 
                    so.size_id,
                    sz.name AS size_name,
                    so.color_id,
                    cl.name AS color_name,
                    SUM(so.quantity) AS total_out_quantity
                FROM tx_stiching_outward so
                LEFT JOIN size sz ON sz.id = so.size_id
                LEFT JOIN color cl ON cl.id = so.color_id
                WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
                GROUP BY so.id
                 -- so.size_id, sz.name, so.color_id, cl.name
            """
            cursor.execute(query_present, [entry_id, tm_id])
            present_rows = cursor.fetchall()
            present_cols = [col[0] for col in cursor.description]
            present_data = [dict(zip(present_cols, row)) for row in present_rows]

            # Get all data for this entry_id regardless of tm_id
            query_all = """
                SELECT 
                    so.size_id,
                    sz.name AS size_name,
                    so.color_id,
                    cl.name AS color_name,
                    SUM(so.quantity) AS total_out_quantity
                FROM tx_stiching_outward so
                LEFT JOIN size sz ON sz.id = so.size_id
                LEFT JOIN color cl ON cl.id = so.color_id
                WHERE so.status = 1 AND so.entry_id = %s
                GROUP BY so.size_id, sz.name, so.color_id, cl.name
            """
            cursor.execute(query_all, [entry_id])
            all_rows = cursor.fetchall()
            all_cols = [col[0] for col in cursor.description]
            all_data = [dict(zip(all_cols, row)) for row in all_rows]

            # Compute missing items
            present_keys = set(f"{row['color_id']}_{row['size_id']}" for row in present_data)
            missing_data = [
                row for row in all_data
                if f"{row['color_id']}_{row['size_id']}" not in present_keys
            ]

        return JsonResponse({
            'status': 'success',
            'data': present_data,
            'missing': missing_data
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})




def get_stiching_delivery_data_16(request):
    tm_id = request.POST.get('tm_id')
    entry_id = request.POST.get('entry_id')
    if not tm_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

    try:

        query = """

            SELECT 
                so.size_id,
                sz.name AS size_name,
                so.color_id,
                cl.name AS color_name,
                SUM(so.quantity) AS total_out_quantity
            FROM tx_stiching_outward so
            LEFT JOIN size sz ON sz.id = so.size_id
            LEFT JOIN color cl ON cl.id = so.color_id
            WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
            GROUP BY so.size_id, sz.name, so.color_id, cl.name
        """
        params = [entry_id, tm_id]

        with connection.cursor() as cursor: 
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            print('entry-data:',results)
        data = [dict(zip(columns, row)) for row in results] 
        return JsonResponse({'status': 'success', 'data': data})
      
    except Exception as e:  
        return JsonResponse({'status': 'error', 'message': str(e)})




def get_cutting_stock_modal_test_2172025(request):
    entry_id = request.POST.get('entry_id')
    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

    try:
        query = """
            SELECT 
                entry_id,
                size_id,
                sz.name AS size_name,
                color_id,
                cl.name AS color_name,
                SUM(in_quantity) AS total_in_quantity,
                SUM(out_quantity) AS total_out_quantity,
                (SUM(in_quantity) - SUM(out_quantity)) AS available_stock_quantity
            FROM (
                SELECT 
                    s.tm_id AS entry_id,
                    s.size_id,
                    sz.name,
                    s.color_id,
                    cl.name,
                    SUM(s.quantity) AS in_quantity,
                    0 AS out_quantity
                FROM tx_cutting_entry s
                LEFT JOIN size sz ON sz.id = s.size_id
                LEFT JOIN color cl ON cl.id = s.color_id
                WHERE s.status = 1 AND s.tm_id = %s
                GROUP BY s.entry_id, s.size_id, sz.name, s.color_id, cl.name

                UNION ALL

                SELECT 
                    so.entry_id,
                    so.size_id,
                    sz.name,
                    so.color_id,
                    cl.name,
                    0 AS in_quantity,
                    SUM(so.quantity) AS out_quantity
                FROM tx_stiching_outward so
                LEFT JOIN size sz ON sz.id = so.size_id
                LEFT JOIN color cl ON cl.id = so.color_id
                WHERE so.status = 1 AND so.entry_id = %s
                GROUP BY so.entry_id, so.size_id, sz.name, so.color_id, cl.name
            ) AS combined_data
            GROUP BY entry_id, size_id, sz.name, color_id, cl.name
            HAVING (SUM(in_quantity) - SUM(out_quantity)) > 0
        """
        params = [entry_id, entry_id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in results]
        return JsonResponse({'status': 'success', 'data': data})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json



# @csrf_exempt
# def get_stitching_delivery_summary(request):
#     try:
#         entry_ids = json.loads(request.POST.get('entry_ids', '[]'))
#         tm_ids = json.loads(request.POST.get('tm_ids', '[]'))

#         if not entry_ids or not tm_ids:
#             return JsonResponse({'status': 'error', 'message': 'Entry IDs and TM IDs are required'})

#         # Convert list to comma-separated placeholders for SQL query
#         entry_placeholders = ','.join(['%s'] * len(entry_ids))
#         tm_placeholders = ','.join(['%s'] * len(tm_ids))

#         query = f"""
#             SELECT 
#                 so.size_id,
#                 sz.name AS size_name,
#                 so.color_id,
#                 cl.name AS color_name,
#                 SUM(so.quantity) AS total_out_quantity
#             FROM tx_stiching_outward so
#             LEFT JOIN size sz ON sz.id = so.size_id
#             LEFT JOIN color cl ON cl.id = so.color_id
#             WHERE so.status = 1 
#               AND so.entry_id IN ({entry_placeholders}) 
#               AND so.tm_id IN ({tm_placeholders})
#             GROUP BY so.size_id, sz.name, so.color_id, cl.name
#         """

#         params = entry_ids + tm_ids  # Combine both sets of parameters

#         with connection.cursor() as cursor:
#             cursor.execute(query, params)
#             columns = [col[0] for col in cursor.description]
#             results = cursor.fetchall()

#         data = [dict(zip(columns, row)) for row in results]
#         return JsonResponse({'status': 'success', 'data': data})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)})


def get_stitching_delivery_summary(request):
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    if not entry_id or not tm_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID and TM ID required'})

    try:
        query = """

            SELECT 
                so.size_id,
                sz.name AS size_name,
                sz.sort_order_no,
                so.color_id,
                cl.name AS color_name,
                SUM(so.quantity) AS total_out_quantity
            FROM tx_stiching_outward so
            LEFT JOIN size sz ON sz.id = so.size_id
            LEFT JOIN color cl ON cl.id = so.color_id
            WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
            GROUP BY so.size_id, sz.name, sz.sort_order_no, so.color_id, cl.name
            ORDER BY sz.sort_order_no ASC
          
        """
        params = [entry_id, tm_id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in results]
        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


  # SELECT 
            #     so.size_id,
            #     sz.name AS size_name,
            #     so.color_id,
            #     cl.name AS color_name,
            #     SUM(so.quantity) AS total_out_quantity
            # FROM tx_stiching_outward so
            # LEFT JOIN size sz ON sz.id = so.size_id
            # LEFT JOIN color cl ON cl.id = so.color_id
            # WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
            # GROUP BY so.size_id, sz.name, so.color_id, cl.name

# views.py
from django.http import JsonResponse
from django.db import connection

def get_cutting_summary_stock_mmmm(request):
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    print('stiching:',entry_id,tm_id)
    data = []

    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

    try:
        if tm_id:
            # For #stiching_delivery_table – show only used
            query = """
                SELECT 
                    so.entry_id AS entry_id,
                    so.size_id,
                    sz.name,
                    so.color_id,
                    cl.name,
                    0 AS total_in_quantity,
                    SUM(so.quantity) AS total_out_quantity,
                    0 AS available_stock_quantity
                FROM tx_stiching_outward so
                LEFT JOIN size sz ON sz.id = so.size_id
                LEFT JOIN color cl ON cl.id = so.color_id
                WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
                GROUP BY so.size_id,so.color_id
            """
            params = [entry_id, tm_id]
        else:
            # For modal #purchaseTable – show full available stock
            query = """
                SELECT 
                    entry_id,
                    size_id,
                    size_name,
                    color_id,
                    color_name,
                    SUM(in_quantity) AS total_in_quantity,
                    SUM(out_quantity) AS total_out_quantity,
                    (SUM(in_quantity) - SUM(out_quantity)) AS available_stock_quantity
                FROM (
                    SELECT 
                        s.tm_id AS entry_id,
                        s.size_id,
                        sz.name AS size_name,
                        s.color_id,
                        cl.name AS color_name,
                        SUM(s.quantity) AS in_quantity,
                        0 AS out_quantity
                    FROM tx_cutting_entry s
                    LEFT JOIN size sz ON sz.id = s.size_id
                    LEFT JOIN color cl ON cl.id = s.color_id
                    WHERE s.status = 1 AND s.tm_id = %s
                    GROUP BY s.tm_id, s.size_id, s.color_id

                    UNION ALL

                    SELECT 
                        so.entry_id,
                        so.size_id,
                        sz.name AS size_name,
                        so.color_id,
                        cl.name AS color_name,
                        0 AS in_quantity,
                        SUM(so.quantity) AS out_quantity 
                    FROM tx_stiching_outward so
                    LEFT JOIN size sz ON sz.id = so.size_id
                    LEFT JOIN color cl ON cl.id = so.color_id
                    WHERE so.status = 1 AND so.entry_id = %s
                    GROUP BY so.entry_id, so.size_id, sz.name, so.color_id, cl.name
                ) AS combined_data
                GROUP BY entry_id, size_id,  color_id
                HAVING SUM(in_quantity) - SUM(out_quantity) > 0
            """
            params = [entry_id, entry_id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in results]


        try:
            inward = cutting_entry_table.objects.get(status=1, id=entry_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
        except cutting_entry_table.DoesNotExist:
            quality = None
            style = None
            fabric=None

        # return JsonResponse({
        #     'status': 'success',
        #     'data': results,
        #     'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        #     'style': {'id': style['id'], 'name': style['name']} if style else '',
        #     'fabric':fabric,
        # })
    
 

        return JsonResponse({'status': 'success', 'summary_data': data, 'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else '',
            'fabric':fabric,})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# def get_cutting_summary_stock(request):
#     if request.method == "POST":
#         entry_id = request.POST.get("entry_id")
#         tm_id = request.POST.get("tm_id")

#         if not entry_id:
#             return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

#         with connection.cursor() as cursor:
#             if tm_id:
#                 query = """
#                     SELECT 
#                         Y.entry_id,
#                         Y.size_id,
#                         Y.color_id,
#                         SUM(Y.total_in_quantity) AS total_in_quantity, 
#                         SUM(Y.total_out_quantity) AS total_out_quantity,
#                         SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
#                     FROM (
#                         SELECT 
#                             ce.tm_id as entry_id,
#                             ce.size_id,
#                             ce.color_id,
#                             ce.quantity AS total_in_quantity,
#                             0 AS total_out_quantity
#                         FROM tx_cutting_entry ce
#                         WHERE ce.status = 1 AND ce.tm_id = %s
#                         AND NOT EXISTS (
#                             SELECT 1 FROM tx_stiching_outward d
#                             WHERE d.status = 1 AND d.tm_id = %s
#                             AND d.size_id = ce.size_id AND d.color_id = ce.color_id
#                         )
#                         GROUP BY ce.size_id, ce.color_id

#                         UNION ALL

#                         SELECT 
#                             so.entry_id AS entry_id,
#                             so.size_id, 
#                             so.color_id,
#                             0 AS total_in_quantity, 
#                             so.quantity AS total_out_quantity
#                         FROM tx_stiching_outward so
#                         WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
#                         GROUP BY so.size_id, so.color_id
#                     ) AS Y
#                     GROUP BY Y.size_id, Y.color_id
#                     ORDER BY Y.size_id, Y.color_id
#                 """
#                 params = [entry_id, tm_id, entry_id, tm_id]
#             else:
#                 query = """

#                 SELECT 
#                     ce.tm_id as entry_id,
#                     ce.size_id,
#                     ce.color_id,
#                     ce.quantity AS total_in_quantity,
#                     --  SUM(ce.quantity) AS total_in_quantity,
#                     0 AS total_out_quantity
#                 FROM tx_cutting_entry ce
#                 WHERE ce.status = 1 AND ce.tm_id = %s
#                   GROUP BY ce.size_id, ce.color_id, ce.tm_id

#                 UNION ALL

#                 SELECT 
#                     so.entry_id AS entry_id, 
#                     so.size_id,
#                     so.color_id,
#                     0 AS total_in_quantity,
#                     so.quantity AS total_out_quantity
#                 FROM tx_stiching_outward so 
#                 WHERE so.status = 1 AND so.entry_id =%s  
#                   GROUP BY so.size_id, so.color_id, so.entry_id
#                 """
#                 params = [entry_id, entry_id]

#             cursor.execute(query, params)
#             columns = [col[0] for col in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]

#         # attach color/size names
#         size_ids = {r['size_id'] for r in results}
#         color_ids = {r['color_id'] for r in results}
#         size_map = {s['id']: s['name'] for s in size_table.objects.filter(id__in=size_ids).values('id', 'name')}
#         color_map = {c['id']: c['name'] for c in color_table.objects.filter(id__in=color_ids).values('id', 'name')}

#         for r in results:
#             r['size_name'] = size_map.get(r['size_id'], '')
#             r['color_name'] = color_map.get(r['color_id'], '')

#         # stitched data = rows already used in outward
#         stitched_qs = child_stiching_outward_table.objects.filter(entry_id=entry_id, status=1)
#         if tm_id:
#             stitched_qs = stitched_qs.filter(tm_id=tm_id)

#         stitched_list = list(stitched_qs.values_list('color_id', 'size_id'))

#         stitched_set = [{'color_id': c, 'size_id': s} for c, s in stitched_list]

#         try:
#             inward = cutting_entry_table.objects.get(status=1, id=entry_id)
#             fabric = fabric_program_table.objects.filter(id=inward.fabric_id).values('id').first()
#             quality = quality_table.objects.filter(id=inward.quality_id).values('id', 'name').first()
#             style = style_table.objects.filter(id=inward.style_id).values('id', 'name').first()
#         except cutting_entry_table.DoesNotExist:
#             fabric = quality = style = None

#         return JsonResponse({
#             'status': 'success',
#             'data': results,
#             'stitched_items': stitched_set,
#             'quality': quality,
#             'style': style,
#             'fabric': fabric
#         })

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


from django.db import connection
from django.http import JsonResponse 




from django.db import connection

def get_cutting_summary_stock_lists_19(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    entry_id = request.POST.get("entry_id")
    # Correctly get multiple color IDs from the POST data
    color_ids = request.POST.getlist("color_ids[]")
    tm_id = request.POST.get("tm_id")
    print('tm_id:',tm_id)

    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'}, status=400)
    
    # Handle case where no colors are selected
    if not color_ids:
        return JsonResponse({'status': 'error', 'message': 'At least one color must be selected'}, status=400)

    with connection.cursor() as cursor:
        # Create a comma-separated string for the SQL IN clause
        color_ids_str = ','.join(['%s'] * len(color_ids))

        query = f"""
            SELECT
                Y.size_id,
                Y.color_id,
                SUM(Y.total_in_quantity) AS total_in_quantity,
                SUM(Y.total_out_quantity) AS total_out_quantity,
                SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
            FROM (
                SELECT
                    ce.size_id,
                    ce.color_id,
                    SUM(ce.quantity) AS total_in_quantity,
                    0 AS total_out_quantity
                FROM tx_cutting_entry ce
                WHERE ce.status = 1 AND ce.tm_id = %s
                GROUP BY ce.size_id, ce.color_id

                UNION ALL

                SELECT
                    so.size_id,
                    so.color_id,
                    0 AS total_in_quantity,
                    SUM(so.quantity) AS total_out_quantity
                FROM tx_stiching_outward so
                WHERE so.status = 1 AND so.entry_id = %s
                GROUP BY so.size_id, so.color_id
            ) AS Y
            WHERE Y.color_id IN ({color_ids_str})
            GROUP BY Y.size_id, Y.color_id
            ORDER BY Y.size_id, Y.color_id
        """
        
        # Build the parameters list with the color IDs at the end
        params = [entry_id, tm_id if tm_id else entry_id] + color_ids
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Attach color/size names
    size_ids = {r['size_id'] for r in results}
    color_ids_in_results = {r['color_id'] for r in results}

    size_map = {s['id']: s['name'] for s in size_table.objects.filter(id__in=size_ids).values('id', 'name')}
    color_map = {c['id']: c['name'] for c in color_table.objects.filter(id__in=color_ids_in_results).values('id', 'name')}
    
    for r in results:
        r['size_name'] = size_map.get(r['size_id'], '')
        r['color_name'] = color_map.get(r['color_id'], '')

    # Get stitched data for the specific color_ids
    stitched_qs = child_stiching_outward_table.objects.filter(
        entry_id=entry_id, 
        color_id__in=color_ids, # Filter by multiple color IDs
        status=1
    )
    if tm_id: 
        stitched_qs = stitched_qs.filter(tm_id=tm_id) 

    stitched_set = list(stitched_qs.values('color_id', 'size_id'))

    # Get related main entry data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(id=inward.fabric_id).values('id').first()
        quality = quality_table.objects.filter(id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        fabric = quality = style = None

    return JsonResponse({
        'status': 'success',
        'data': results,
        'stitched_items': stitched_set,
        'quality': quality, 
        'style': style,
        'fabric': fabric
    })




def get_cutting_summary_stock_lists(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    entry_id = request.POST.get("entry_id")
    # Correctly get multiple color IDs from the POST data
    size_ids = request.POST.getlist("size_ids[]")
    tm_id = request.POST.get("tm_id")
    print('tm_id:',tm_id)

    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'}, status=400)
    
    # Handle case where no colors are selected
    if not size_ids:
        return JsonResponse({'status': 'error', 'message': 'At least one color must be selected'}, status=400)

    # with connection.cursor() as cursor:
    #     # Create a comma-separated string for the SQL IN clause
    #     size_ids_str = ','.join(['%s'] * len(size_ids))

    #     query = f"""
    #         SELECT
    #             Y.size_id,
    #             Y.color_id,
    #             SUM(Y.total_in_quantity) AS total_in_quantity,
    #             SUM(Y.total_out_quantity) AS total_out_quantity,
    #             SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
    #         FROM (
    #             SELECT
    #                 ce.size_id,
    #                 ce.color_id,
    #                 SUM(ce.quantity) AS total_in_quantity,
    #                 0 AS total_out_quantity
    #             FROM tx_cutting_entry ce
    #             WHERE ce.status = 1 AND ce.tm_id = %s and ce.size_id= %s
    #        --    GROUP BY ce.color_id

    #             UNION ALL

    #             SELECT
    #                 so.size_id,
    #                 so.color_id,
    #                 0 AS total_in_quantity,
    #                 SUM(so.quantity) AS total_out_quantity
    #             FROM tx_stiching_outward so
    #             WHERE so.status = 1 AND so.entry_id = %s
    #             GROUP BY so.size_id, so.color_id
    #         ) AS Y
    #         WHERE Y.size_id IN ({size_ids_str})
    #          GROUP BY Y.size_id, Y.color_id
    #         ORDER BY Y.size_id, Y.color_id
    #     """
        
    #     # Build the parameters list with the color IDs at the end
    #     params = [entry_id, tm_id if tm_id else entry_id] + size_ids

    with connection.cursor() as cursor:
        size_ids_str = ','.join(['%s'] * len(size_ids))

        query = f"""
            SELECT 
                ce.size_id,
                ce.color_id,
                ce.quantity AS total_in_quantity,
                COALESCE(so.total_out_quantity, 0) AS total_out_quantity,
                ce.quantity - COALESCE(so.total_out_quantity, 0) AS available_stock_quantity
            FROM tx_cutting_entry ce
            LEFT JOIN (
                SELECT 
                    size_id,
                    color_id,
                    SUM(quantity) AS total_out_quantity
                FROM tx_stiching_outward
                WHERE status = 1 AND entry_id = %s
                GROUP BY size_id, color_id
            ) so ON ce.size_id = so.size_id AND ce.color_id = so.color_id
            WHERE ce.status = 1 AND ce.tm_id = %s AND ce.size_id IN ({size_ids_str})
            ORDER BY ce.size_id, ce.color_id
        """

        params = [entry_id, tm_id if tm_id else entry_id] + size_ids
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]



    # with connection.cursor() as cursor:
    #     size_ids_str = ','.join(['%s'] * len(size_ids))  # for the final WHERE IN clause

    #     query = f"""
    #         SELECT
    #             Y.size_id,
    #             Y.color_id,
    #             SUM(Y.total_in_quantity) AS total_in_quantity,
    #             SUM(Y.total_out_quantity) AS total_out_quantity,
    #             SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
    #         FROM (
    #             -- Don't group cutting_entry here
    #             SELECT
    #                 ce.size_id,
    #                 ce.color_id,
    #                 ce.quantity AS total_in_quantity,
    #                 0 AS total_out_quantity
    #             FROM tx_cutting_entry ce
    #             WHERE ce.status = 1 AND ce.tm_id = %s

    #             UNION ALL

    #             SELECT
    #                 so.size_id,
    #                 so.color_id,
    #                 0 AS total_in_quantity,
    #                 SUM(so.quantity) AS total_out_quantity
    #             FROM tx_stiching_outward so
    #             WHERE so.status = 1 AND so.entry_id = %s
    #             GROUP BY so.size_id, so.color_id
    #         ) AS Y
    #         WHERE Y.size_id IN ({size_ids_str})
    #         GROUP BY Y.size_id, Y.color_id
    #         ORDER BY Y.size_id, Y.color_id
    #     """

    #     # Parameters: [tm_id, entry_id] + size_ids list
    #     params = [tm_id if tm_id else entry_id, entry_id] + size_ids

    # # cursor.execute(query, params)
    # # columns = [col[0] for col in cursor.description]
    # # results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        
    #     cursor.execute(query, params)
    #     columns = [col[0] for col in cursor.description]
    #     results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Attach color/size names
    size_ids = {r['size_id'] for r in results}
    color_ids_in_results = {r['color_id'] for r in results}

    size_map = {s['id']: s['name'] for s in size_table.objects.filter(id__in=size_ids).values('id', 'name')}
    color_map = {c['id']: c['name'] for c in color_table.objects.filter(id__in=color_ids_in_results).values('id', 'name')}
    
    for r in results:
        r['size_name'] = size_map.get(r['size_id'], '')
        r['color_name'] = color_map.get(r['color_id'], '')

    # Get stitched data for the specific color_ids
    stitched_qs = child_stiching_outward_table.objects.filter(
        entry_id=entry_id, 
        size_id__in=size_ids, # Filter by multiple color IDs
        status=1
    )
    if tm_id: 
        stitched_qs = stitched_qs.filter(tm_id=tm_id) 

    stitched_set = list(stitched_qs.values('color_id', 'size_id'))

    # Get related main entry data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(id=inward.fabric_id).values('id').first()
        quality = quality_table.objects.filter(id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        fabric = quality = style = None

    return JsonResponse({
        'status': 'success',
        'data': results,
        'stitched_items': stitched_set,
        'quality': quality, 
        'style': style,
        'fabric': fabric
    })







def get_cutting_summary_stock_data(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    entry_id = request.POST.get("entry_id")
    # Correctly get multiple color IDs from the POST data
    # size_ids = request.POST.getlist("size_ids[]")
    tm_id = request.POST.get("tm_id")
    print('tm_id:',tm_id)

    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'}, status=400)
    
    # Handle case where no colors are selected
    # if not size_ids:
    #     return JsonResponse({'status': 'error', 'message': 'At least one color must be selected'}, status=400)


    with connection.cursor() as cursor:
        # size_ids_str = ','.join(['%s'] * len(size_ids))            --   AND ce.size_id IN ({size_ids_str})


        # query = f"""
        #     SELECT 
        #         ce.size_id,
        #         ce.color_id,
        #         ce.quantity AS total_in_quantity,
        #         COALESCE(so.total_out_quantity, 0) AS total_out_quantity,
        #         ce.quantity - COALESCE(so.total_out_quantity, 0) AS available_stock_quantity
        #     FROM tx_cutting_entry ce
        #     LEFT JOIN (
        #         SELECT 
        #             size_id,
        #             color_id,
        #             SUM(quantity) AS total_out_quantity
        #         FROM tx_stiching_outward
        #         WHERE status = 1 AND entry_id = %s
        #         GROUP BY size_id, color_id
        #     ) so ON ce.size_id = so.size_id AND ce.color_id = so.color_id
        #     WHERE ce.status = 1 AND ce.tm_id = %s 
        #     ORDER BY ce.size_id, ce.color_id
        # """


        query = f"""
            SELECT * FROM (
                SELECT 
                    ce.size_id,
                    ce.color_id,
                    ce.quantity AS total_in_quantity,
                    COALESCE(so.total_out_quantity, 0) AS total_out_quantity,
                    ce.quantity - COALESCE(so.total_out_quantity, 0) AS available_stock_quantity
                FROM tx_cutting_entry ce
                LEFT JOIN (
                    SELECT 
                        size_id,
                        color_id,
                        SUM(quantity) AS total_out_quantity
                    FROM tx_stiching_outward
                    WHERE status = 1 AND entry_id = %s
                    GROUP BY size_id, color_id
                ) so ON ce.size_id = so.size_id AND ce.color_id = so.color_id
                WHERE ce.status = 1 AND ce.tm_id = %s 
            ) X
            WHERE X.available_stock_quantity > 0
            ORDER BY X.size_id, X.color_id
        """




        params = [entry_id, tm_id if tm_id else entry_id] 
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]


    # Attach color/size names
    size_ids = {r['size_id'] for r in results}
    color_ids_in_results = {r['color_id'] for r in results}

    size_map = {s['id']: s['name'] for s in size_table.objects.filter(id__in=size_ids).values('id', 'name')}
    color_map = {c['id']: c['name'] for c in color_table.objects.filter(id__in=color_ids_in_results).values('id', 'name')}
    
    for r in results:
        r['size_name'] = size_map.get(r['size_id'], '')
        r['color_name'] = color_map.get(r['color_id'], '')

    # Get stitched data for the specific color_ids
    stitched_qs = child_stiching_outward_table.objects.filter(
        entry_id=entry_id, 
        size_id__in=size_ids, # Filter by multiple color IDs
        status=1
    )
    if tm_id: 
        stitched_qs = stitched_qs.filter(tm_id=tm_id) 

    stitched_set = list(stitched_qs.values('color_id', 'size_id'))

    # Get related main entry data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(id=inward.fabric_id).values('id').first()
        quality = quality_table.objects.filter(id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        fabric = quality = style = None

    return JsonResponse({
        'status': 'success',
        'data': results,
        'stitched_items': stitched_set,
        'quality': quality, 
        'style': style,
        'fabric': fabric
    })




def get_cutting_summary_stock(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    entry_id = request.POST.get("entry_id")
    color_ids = request.POST.getlist("color_ids[]")
    tm_id = request.POST.get("tm_id")
    print('tm-id:',tm_id,entry_id)
    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'}, status=400)

    if not color_ids:
        return JsonResponse({'status': 'error', 'message': 'At least one color must be selected'}, status=400)

    # Use a dictionary to store dynamic query parameters to prevent SQL injection
    query_params = {
        'entry_id_1': entry_id,
        'entry_id_2': entry_id,
        'color_ids': tuple(color_ids)
    } 

    # Base query for all items
    base_query = """
            SELECT 
                Y.size_id,
                Y.color_id,
                COALESCE(SUM(Y.total_in_quantity), 0) AS total_in_quantity,
                COALESCE(SUM(Y.total_out_quantity), 0) AS total_out_quantity,
                COALESCE(SUM(Y.total_in_quantity), 0) - COALESCE(SUM(Y.total_out_quantity), 0) AS available_stock_quantity
            FROM (
                SELECT
                    ce.size_id,
                    ce.color_id, 
                    SUM(ce.quantity) AS total_in_quantity,
                    0 AS total_out_quantity
                FROM tx_cutting_entry ce
                WHERE ce.status = 1 AND ce.id = %(entry_id_1)s
                GROUP BY ce.size_id, ce.color_id

                UNION ALL

                SELECT
                    so.size_id,
                    so.color_id,
                    0 AS total_in_quantity,
                    SUM(so.quantity) AS total_out_quantity
                FROM tx_stiching_outward so
                WHERE so.status = 1 AND so.entry_id = %(entry_id_2)s
                GROUP BY so.size_id, so.color_id
            ) AS Y
            WHERE Y.color_id IN %(color_ids)s
    """
    

    # If tm_id is provided, adjust the query
    if tm_id:
        # Add a filter for tm_id to the cutting entry part
        base_query = """
            SELECT
                Y.size_id,
                Y.color_id,
                COALESCE(SUM(Y.total_in_quantity), 0) AS total_in_quantity,
                COALESCE(SUM(Y.total_out_quantity), 0) AS total_out_quantity,
                COALESCE(SUM(Y.total_in_quantity), 0) - COALESCE(SUM(Y.total_out_quantity), 0) AS available_stock_quantity
            FROM (
                SELECT
                    ce.size_id,
                    ce.color_id,
                    SUM(ce.quantity) AS total_in_quantity,
                    0 AS total_out_quantity
                FROM tx_cutting_entry ce
                WHERE ce.status = 1 AND ce.tm_id = %(tm_id)s
                GROUP BY ce.size_id, ce.color_id

                UNION ALL

                SELECT
                    so.size_id,
                    so.color_id,
                    0 AS total_in_quantity,
                    SUM(so.quantity) AS total_out_quantity
                FROM tx_stiching_outward so
                WHERE so.status = 1 AND so.entry_id = %(entry_id_2)s AND so.tm_id = %(tm_id)s
                GROUP BY so.size_id, so.color_id
            ) AS Y
            WHERE Y.color_id IN %(color_ids)s
        """
        # Update parameters for the tm_id-specific query
        query_params['tm_id'] = tm_id

    # Append GROUP BY and ORDER BY clauses
    final_query = f"""
        {base_query}
        GROUP BY Y.size_id, Y.color_id
        ORDER BY Y.size_id, Y.color_id
    """
 
    with connection.cursor() as cursor:
        cursor.execute(final_query, query_params)
        columns = [col[0] for col in cursor.description]
        print('columns:',columns)
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print('data-list:',results)
    # ... (rest of your code for mapping names, fetching stitched items, and related data) ...
    # Size & color name mapping
    size_ids = {r['size_id'] for r in results}
    color_ids_in_results = {r['color_id'] for r in results}
    size_map = {s['id']: s['name'] for s in size_table.objects.filter(id__in=size_ids).values('id', 'name')}
    color_map = {c['id']: c['name'] for c in color_table.objects.filter(id__in=color_ids_in_results).values('id', 'name')}

    for r in results:
        r['size_name'] = size_map.get(r['size_id'], '')
        r['color_name'] = color_map.get(r['color_id'], '')

    # Stitched data
    stitched_qs = child_stiching_outward_table.objects.filter(
        entry_id=entry_id,
        status=1,
        color_id__in=color_ids
    )
    if tm_id:
        stitched_qs = stitched_qs.filter(tm_id=tm_id)

    stitched_set = list(stitched_qs.values('color_id', 'size_id'))
    
    # All stitched items
    stitched_items_all = list(
        child_stiching_outward_table.objects.filter(
            entry_id=entry_id,
            status=1,
            color_id__in=color_ids
        ).values('color_id', 'size_id')
    )

    # Related data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(id=inward.fabric_id).values('id').first()
        quality = quality_table.objects.filter(id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        fabric = quality = style = None

    return JsonResponse({
        'status': 'success',
        'data': results,
        'stitched_items': stitched_set,           # Stitched items for the current tm_id
        'stitched_items_all': stitched_items_all, # All stitched items regardless of tm_id
        'quality': quality,
        'style': style,
        'fabric': fabric
    })




# def get_cutting_summary_stock(request):
#     if request.method != "POST":
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

#     entry_id = request.POST.get("entry_id")
#     color_ids = request.POST.getlist("color_ids[]")
#     tm_id = request.POST.get("tm_id")

#     if not entry_id:
#         return JsonResponse({'status': 'error', 'message': 'Entry ID is required'}, status=400)

#     if not color_ids:
#         return JsonResponse({'status': 'error', 'message': 'At least one color must be selected'}, status=400)

#     with connection.cursor() as cursor:
#         color_ids_str = ','.join(['%s'] * len(color_ids))

#         # If tm_id is given, apply your posted query logic
#         if tm_id:
#             query = f"""
#                 SELECT
#                     Y.size_id,
#                     Y.color_id,
#                     SUM(Y.total_in_quantity) AS total_in_quantity,
#                     SUM(Y.total_out_quantity) AS total_out_quantity,
#                     SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
#                 FROM (
#                     SELECT
#                         ce.size_id,
#                         ce.color_id,
#                         SUM(ce.quantity) AS total_in_quantity,
#                         0 AS total_out_quantity
#                     FROM tx_cutting_entry ce
#                     WHERE ce.status = 1 AND ce.tm_id = %s
#                     GROUP BY ce.size_id, ce.color_id

#                     UNION ALL

#                     SELECT
#                         so.size_id,
#                         so.color_id,
#                         0 AS total_in_quantity,
#                         SUM(so.quantity) AS total_out_quantity
#                     FROM tx_stiching_outward so
#                     WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = 1
#                     GROUP BY so.size_id, so.color_id
#                 ) AS Y
#                 WHERE Y.color_id IN ({color_ids_str})
#                 GROUP BY Y.size_id, Y.color_id
#                 ORDER BY Y.size_id, Y.color_id
#             """
#             params = [tm_id, entry_id] + color_ids
#         else:
#             # Fallback: original logic without tm_id condition
#             query = f"""
#                 SELECT
#                     Y.size_id,
#                     Y.color_id,
#                     SUM(Y.total_in_quantity) AS total_in_quantity,
#                     SUM(Y.total_out_quantity) AS total_out_quantity,
#                     SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
#                 FROM (
#                     SELECT
#                         ce.size_id,
#                         ce.color_id,
#                         SUM(ce.quantity) AS total_in_quantity,
#                         0 AS total_out_quantity
#                     FROM tx_cutting_entry ce
#                     WHERE ce.status = 1 AND ce.id = %s
#                     GROUP BY ce.size_id, ce.color_id

#                     UNION ALL

#                     SELECT
#                         so.size_id,
#                         so.color_id,
#                         0 AS total_in_quantity,
#                         SUM(so.quantity) AS total_out_quantity
#                     FROM tx_stiching_outward so
#                     WHERE so.status = 1 AND so.entry_id = %s
#                     GROUP BY so.size_id, so.color_id
#                 ) AS Y
#                 WHERE Y.color_id IN ({color_ids_str})
#                 GROUP BY Y.size_id, Y.color_id
#                 ORDER BY Y.size_id, Y.color_id
#             """
#             params = [entry_id, entry_id] + color_ids

#         cursor.execute(query, params)
#         columns = [col[0] for col in cursor.description]
#         results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         print('lists:',results)
#     # Size & color name mapping
#     size_ids = {r['size_id'] for r in results}
#     color_ids_in_results = {r['color_id'] for r in results}
#     size_map = {s['id']: s['name'] for s in size_table.objects.filter(id__in=size_ids).values('id', 'name')}
#     color_map = {c['id']: c['name'] for c in color_table.objects.filter(id__in=color_ids_in_results).values('id', 'name')}

#     for r in results:
#         r['size_name'] = size_map.get(r['size_id'], '')
#         r['color_name'] = color_map.get(r['color_id'], '')


#     stitched_items_all = list(
#     child_stiching_outward_table.objects.filter(
#         entry_id=entry_id,
#         color_id__in=color_ids,
#         status=1
#     ).values('color_id', 'size_id')
# )



#     # Stitched data
#     stitched_qs = child_stiching_outward_table.objects.filter(
#         entry_id=entry_id,
#         color_id__in=color_ids,
#         status=1
#     )
#     if tm_id:
#         stitched_qs = stitched_qs.filter(tm_id=tm_id)

#     stitched_set = list(stitched_qs.values('color_id', 'size_id'))

#     # Related data
#     try:
#         inward = cutting_entry_table.objects.get(status=1, id=entry_id)
#         fabric = fabric_program_table.objects.filter(id=inward.fabric_id).values('id').first()
#         quality = quality_table.objects.filter(id=inward.quality_id).values('id', 'name').first()
#         style = style_table.objects.filter(id=inward.style_id).values('id', 'name').first()
#     except cutting_entry_table.DoesNotExist:
#         fabric = quality = style = None

#     # return JsonResponse({
#     #     'status': 'success',
#     #     'data': results,
#     #     'stitched_items': stitched_set,
#     #     'quality': quality,
#     #     'style': style,
#     #     'fabric': fabric
#     # })

#     return JsonResponse({
#         'status': 'success',
#         'data': results,
#         'stitched_items': stitched_set,           # current tm_id only
#         'stitched_items_all': stitched_items_all, # all tm_ids
#         'quality': quality,
#         'style': style,
#         'fabric': fabric
#     })





def get_cutting_summary_stock_crt21072025(request):
    if request.method == "POST":
        entry_id = request.POST.get("entry_id")
        tm_id = request.POST.get("tm_id")  # optional

        print('entrys:',entry_id,tm_id)
        if not entry_id:
            return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

        with connection.cursor() as cursor:
          
            if tm_id:
                query = """
                    SELECT 
                        Y.entry_id,
                        Y.size_id,
                        Y.color_id,
                        SUM(Y.total_in_quantity) AS total_in_quantity, 
                        SUM(Y.total_out_quantity) AS total_out_quantity,
                        SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
                    FROM (
                        SELECT 
                            ce.tm_id as entry_id,
                            ce.size_id,
                            ce.color_id,
                            ce.quantity AS total_in_quantity,
                            0 AS total_out_quantity
                        FROM tx_cutting_entry ce
                        WHERE ce.status = 1 AND ce.tm_id = %s
                        AND NOT EXISTS (
                            SELECT 1 FROM tx_stiching_outward d
                            WHERE d.status = 1 AND d.tm_id = %s
                            AND d.size_id = ce.size_id AND d.color_id = ce.color_id
                        )
                        GROUP BY ce.size_id, ce.color_id

                        UNION ALL

                        SELECT 
                            so.entry_id AS entry_id,
                            so.size_id, 
                            so.color_id,
                            0 AS total_in_quantity, 
                            so.quantity AS total_out_quantity
                        FROM tx_stiching_outward so
                        WHERE so.status = 1 AND so.entry_id = %s AND so.tm_id = %s
                        GROUP BY so.size_id, so.color_id
                    ) AS Y
                    GROUP BY Y.size_id, Y.color_id
                    ORDER BY Y.size_id, Y.color_id
                """
                params = [entry_id, tm_id, entry_id, tm_id]



            else:
            
                query = """

                SELECT 
                    ce.tm_id as entry_id,
                    ce.size_id,
                    ce.color_id,
                    ce.quantity AS total_in_quantity,
                    --  SUM(ce.quantity) AS total_in_quantity,
                    0 AS total_out_quantity
                FROM tx_cutting_entry ce
                WHERE ce.status = 1 AND ce.tm_id = %s
                --  GROUP BY ce.size_id, ce.color_id, ce.tm_id

                UNION ALL

                SELECT 
                    so.entry_id AS entry_id,
                    so.size_id,
                    so.color_id,
                    0 AS total_in_quantity,
                    so.quantity AS total_out_quantity
                FROM tx_stiching_outward so
                WHERE so.status = 1 AND so.entry_id =%s
                --  GROUP BY so.size_id, so.color_id, so.entry_id
                """
                params = [entry_id, entry_id]

            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print('results:',results)
        # Attach size/color names
        size_ids = {row['size_id'] for row in results}  
        color_ids = {row['color_id'] for row in results}

        sizes = size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name')
        colors = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name')

        size_map = {s['id']: s['name'] for s in sizes}
        color_map = {c['id']: c['name'] for c in colors}

        for row in results:
            row['size_name'] = size_map.get(row['size_id'], '') 
            row['color_name'] = color_map.get(row['color_id'], '')

    
        try:
            inward = cutting_entry_table.objects.get(status=1, id=entry_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
        except cutting_entry_table.DoesNotExist:
            quality = None
            style = None
            fabric=None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else '',
            'fabric':fabric,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

from django.http import JsonResponse


# def get_cutting_summary_stock(request):
#     if request.method != "POST":
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

#     entry_id = request.POST.get("entry_id")
#     tm_id = request.POST.get("tm_id")

#     if not entry_id:
#         return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

#     # Step 1: Get all inward entries (cutting entries)
#     # inwards = cutting_entry_table.objects.filter(status=1, tm_id=tm_id).values('size_id', 'color_id').annotate(
#     #     total_in_quantity=Sum('quantity')
#     # )



#     inwards = sub_cutting_entry_table.objects.filter(status=1, tm_id=tm_id).values('size_id', 'color_id').annotate(
#         total_in_quantity=Sum('quantity')
#     )

#     # Step 2: Get all stitching outwards
#     if tm_id:
#         outwards = child_stiching_outward_table.objects.filter(status=1, entry_id=entry_id, tm_id=tm_id).values(
#             'size_id', 'color_id').annotate(total_out_quantity=Sum('quantity'))
#     else:
#         outwards = child_stiching_outward_table.objects.filter(status=1, entry_id=entry_id).values(
#             'size_id', 'color_id').annotate(total_out_quantity=Sum('quantity'))

#     # Step 3: Convert to dictionaries for lookup
#     outward_map = {
#         (o['size_id'], o['color_id']): o['total_out_quantity']
#         for o in outwards
#     }

#     result = []
#     for inward in inwards:
#         key = (inward['size_id'], inward['color_id'])
#         in_qty = inward['total_in_quantity']
#         out_qty = outward_map.get(key, 0)
#         available_qty = in_qty - out_qty

#         result.append({
#             'size_id': inward['size_id'],
#             'color_id': inward['color_id'],
#             'total_in_quantity': in_qty,
#             'total_out_quantity': out_qty,
#             'available_stock_quantity': available_qty
#         })

#     # Step 4: Attach size and color names
#     size_ids = [r['size_id'] for r in result]
#     color_ids = [r['color_id'] for r in result]

#     size_map = {
#         s['id']: s['name']
#         for s in size_table.objects.filter(status=1, id__in=size_ids)
#     }
#     color_map = {
#         c['id']: c['name']
#         for c in color_table.objects.filter(status=1, id__in=color_ids)
#     }

#     for row in result:
#         row['size_name'] = size_map.get(row['size_id'], '')
#         row['color_name'] = color_map.get(row['color_id'], '')

#     # Step 5: Fetch fabric/style/quality for this entry
#     try:
#         inward = cutting_entry_table.objects.get(status=1, id=entry_id)
#         fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
#         quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
#         style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
#     except cutting_entry_table.DoesNotExist:
#         fabric = quality = style = None

#     return JsonResponse({
#         'status': 'success',
#         'data': result,
#         'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
#         'style': {'id': style['id'], 'name': style['name']} if style else '',
#         'fabric': fabric,
#     })






def get_cutting_summary_stock_test2(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    entry_id = request.POST.get("entry_id")
    tm_id = request.POST.get("tm_id")

    if not entry_id:
        return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

    # Fallback: fetch tm_id from parent
    if not tm_id:
        try:
            tm_id = cutting_entry_table.objects.get(status=1, id=entry_id).tm_id
        except cutting_entry_table.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid entry ID'})

    # Fetch cutting inwards
    inwards = sub_cutting_entry_table.objects.filter(status=1, tm_id=tm_id).values('size_id', 'color_id').annotate(
        total_in_quantity=Sum('quantity')
    )
    print("Inwards:", list(inwards))

    # Fetch stitching outwards
    outwards = child_stiching_outward_table.objects.filter(status=1, entry_id=entry_id, tm_id=tm_id).values(
        'size_id', 'color_id'
    ).annotate(total_out_quantity=Sum('quantity'))
    print("Outwards:", list(outwards))

    outward_map = {
        (o['size_id'], o['color_id']): o['total_out_quantity']
        for o in outwards
    }

    result = []
    for inward in inwards:
        key = (inward['size_id'], inward['color_id'])
        in_qty = inward['total_in_quantity']
        out_qty = outward_map.get(key, 0)
        available_qty = in_qty - out_qty

        result.append({
            'size_id': inward['size_id'],
            'color_id': inward['color_id'],
            'total_in_quantity': in_qty,
            'total_out_quantity': out_qty,
            'available_stock_quantity': available_qty
        })

    size_ids = [r['size_id'] for r in result]
    color_ids = [r['color_id'] for r in result]

    size_map = {
        s['id']: s['name']
        for s in size_table.objects.filter(status=1, id__in=size_ids)
    }
    color_map = {
        c['id']: c['name']
        for c in color_table.objects.filter(status=1, id__in=color_ids)
    }

    for row in result:
        row['size_name'] = size_map.get(row['size_id'], '')
        row['color_name'] = color_map.get(row['color_id'], '')

    # Get fabric/style/quality
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        fabric = quality = style = None

    return JsonResponse({
        'status': 'success',
        'data': result,
        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric': fabric,
    })



def get_cutting_summary_stock_test1(request): 
    if request.method == "POST":
        entry_id = request.POST.get("entry_id")

        if not entry_id:
            return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

        try:
            entry_id = int(entry_id)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid Entry ID'}) 

        results = []

        # Get the cutting entry
        cutting_entry = cutting_entry_table.objects.filter(status=1, id=entry_id).first()
        if not cutting_entry:
            return JsonResponse({'status': 'error', 'message': 'Cutting entry not found'})

        # Check if this entry is already used in parent outward table
        parent_exists = parent_stiching_outward_table.objects.filter(
            status=1, cutting_entry_id=cutting_entry.id 
        ).exists() 

        # All cutting child rows for this entry
        sub_entries = sub_cutting_entry_table.objects.filter(status=1, tm_id=cutting_entry.id)

        # Group sub_entries by (size_id, color_id) to track available qty
        for sub_row in sub_entries:
            size_id = sub_row.size_id
            color_id = sub_row.color_id
            quantity = float(sub_row.quantity or 0)

            # Default full quantity
            available_qty = quantity

            # Get size/color names (optional)
            size_name = size_table.objects.filter(id=size_id).first()
            color_name = color_table.objects.filter(id=color_id).first()

            if parent_exists:
                # If already used in parent, calculate remaining qty by subtracting used qty
                used_qty = child_stiching_outward_table.objects.filter(
                    status=1,
                    entry_id=cutting_entry.id,
                    size_id=size_id,
                    color_id=color_id
                ).aggregate(total=Sum('quantity'))['total'] or 0

                balance_qty = quantity - float(used_qty or 0)
                if balance_qty <= 0:
                    continue  # Fully used, skip

                available_qty = balance_qty 

            try:
                inward = cutting_entry_table.objects.get(status=1, id=entry_id)
                fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
                quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
                style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
            except cutting_entry_table.DoesNotExist:
                quality = None
                style = None
                fabric=None

            results.append({
                'size_id': size_id,
                'color_id': color_id,
                'size_name': size_name.name if size_name else '',
                'color_name': color_name.name if color_name else '',
                'total_in_quantity': quantity,
                'available_stock_quantity': round(available_qty, 2),
               
                'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
                'style': {'id': style['id'], 'name': style['name']} if style else '',
                'fabric':fabric,
            })

        # return JsonResponse({'status': 'success', 'data': results})

        
        return JsonResponse({
            'status': 'success',
            'data': results,
            'quality': quality,
            'style': style,
            'fabric': fabric,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




# update screen 
 


def get_cutting_summary_update_stock(request):
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    # Entries already in stitching table for tm_id
    stitched_rows = child_stiching_outward_table.objects.filter(tm_id=tm_id).values(
        'size_id', 'color_id'
    )
    print('stich:',stitched_rows) 

    stitched_set = {(r['size_id'], r['color_id']) for r in stitched_rows}

    # All from cutting entry table
    cutting_rows = sub_cutting_entry_table.objects.filter(entry_id=entry_id).values(
        'size_id', 'color_id', 'size__name', 'color__name'
    ).annotate(
        total_in_quantity=Sum('quantity')
    )



    result = [] 
    for row in cutting_rows:
        key = (row['size_id'], row['color_id'])
        row_data = {
            'size_id': row['size_id'],
            'color_id': row['color_id'],
            'size_name': row['size__name'],
            'color_name': row['color__name'],
            'total_in_quantity': row['total_in_quantity'],
            'available_stock_quantity': row['total_in_quantity'],  # You can adjust this
            'is_stitched': key in stitched_set,
        }
        result.append(row_data)


    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
    except cutting_entry_table.DoesNotExist:
        quality = None
        style = None
        fabric=None


    return JsonResponse({
        'status': 'success',
        'data': result,
        # 'quality': {...},
        # 'style': {...},
        # 'fabric': {...},

        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric':fabric,
    })

# def get_cutting_summary_stock(request): 
#     if request.method == "POST":
#         entry_id = request.POST.get("entry_id")
#         tm_id = request.POST.get("tm_id")  # optional

#         if not entry_id:
#             return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

#         results = []

#         try:
#             entry_id = int(entry_id)
#         except ValueError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid Entry ID'})

#         cutting_entry = cutting_entry_table.objects.filter(status=1, id=entry_id).first()
#         if cutting_entry:
#             # Directly fetch rows without grouping/summing
#             sub_entries = sub_cutting_entry_table.objects.filter(status=1, tm_id=cutting_entry.id)

#             for row in sub_entries:
#                 size_name = ''
#                 color_name = ''

#                 # Optional: fetch size & color names
#                 if row.size_id:
#                     size_obj = size_table.objects.filter(id=row.size_id).first()
#                     size_name = size_obj.name if size_obj else ''
#                 if row.color_id:
#                     color_obj = color_table.objects.filter(id=row.color_id).first()
#                     color_name = color_obj.name if color_obj else ''

#                 results.append({
#                     'size_id': row.size_id,
#                     'color_id': row.color_id,
#                     'size_name': size_name,
#                     'color_name': color_name,
#                     'total_in_quantity': float(row.quantity or 0),
#                     'available_stock_quantity': float(row.quantity or 0),  # Use actual available qty logic if needed
#                 })

#         return JsonResponse({
#             'status': 'success',
#             'data': results,
#         })

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def generate_packing_out_num_series():
    last_purchase = parent_packing_outward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.outward_no:
        match = re.search(r'DO-(\d+)', last_purchase.outward_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"DO-{next_num:03d}"



import json
from decimal import Decimal
from collections import defaultdict

from datetime import datetime

def safe_date(value):
    try:
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        elif isinstance(value, datetime):
            return value.date()
        return None
    except Exception:
        return None

@csrf_exempt
def insert_stiching_outward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id') 
        company_id = request.session.get('company_id')

        try:
            # Fetch and clean data
            party_id = request.POST.get('party_id')
            remarks = request.POST.get('remarks')
            style_id = request.POST.get('style_id')
            fabric_id = request.POST.get('fabric_id')
            quality_id = request.POST.get('quality_id')
            work_order_no = request.POST.get('work_order_no')
            # rec_date = request.POST.get('receive_date')
            # receive_date = safe_date(rec_date) if rec_date else None
            receive_no = request.POST.get('receive_no') 
            entry_id = request.POST.get('entry_id') 
            outward_date = request.POST.get('outward_date')  

            size_ids = request.POST.getlist('size_id')  # e.g., ['8', '25']
            size_id_str = ','.join(size_ids) 
            print('size-id:',size_id_str)
            # is_packing_raw = request.POST.get('is_packing')  # expected: 'yarn' or 'grey'
            # print('packing:',is_packing_raw)
            # is_packing = 1 if is_packing_raw == 'on' else 0 
            # print('✅ is_packing =', is_packing)

            # Fetch the value of is_packing from POST data
            is_packing_raw = request.POST.get('is_packing')  # This will be '1' or '0' based on the checkbox state

            # Convert '1' -> 1 and '0' -> 0
            is_packing = 1 if is_packing_raw == '1' else 0

            print('✅ is_packing =', is_packing)  # Debugging to see if it's correctly parsed as 1 or 0


            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            # Handle checkbox for is_packing


            # is_packing_raw = request.POST.get('is_packing', '0').strip().lower()
            # print('is=packing:',is_packing_raw)
            # is_packing = 1 if is_packing_raw in ['1', 'on', 'true'] else 0

            out_no = generate_outward_num_series()

            # Create main stitching outward entry
            material_request = parent_stiching_outward_table.objects.create(
                outward_no=out_no,
                outward_date=outward_date,
                work_order_no=work_order_no,
                receive_no=0,
                receive_date=outward_date,
                party_id=party_id,
                fabric_id = fabric_id,
                cfyear=2025,
                cutting_entry_id=entry_id,
                quality_id=quality_id,
                style_id=style_id,
                size_id=size_id_str,
                company_id=company_id,
                is_packing=is_packing,
                total_quantity=0,
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_quantity = Decimal('0.00')

            # Create child stitching outward rows
            for chemical in chemical_data:
                size_id = chemical.get('size_id', 0)
                color_id = chemical.get('color_id', 0)
                delivered_quantity = safe_decimal(chemical.get('quantity'))
                # delivered_dozen = delivered_quantity /12 
                # delivered_pcs = delivered_quantity % 12 
            
                child_stiching_outward_table.objects.create(
                    tm_id=material_request.id,
                    work_order_no=work_order_no,
                    cfyear=2025,
                    company_id=company_id,
                    entry_id=entry_id or 0,
                    party_id=party_id,
                    size_id=size_id,
                    color_id=color_id,
                    style_id=style_id,
                    quality_id=quality_id,
                    quantity=delivered_quantity,
                    # dozen = delivered_dozen,
                    # pieces =delivered_pcs,
                    created_by=user_id,
                    created_on=timezone.now()
                )

                total_quantity += delivered_quantity

            material_request.total_quantity = total_quantity
            material_request.save()

            # If packing is enabled, create grouped packing outward entries 
            # if is_packing:
            #     try:
            #         delivery_groups = defaultdict(list)
            #         for chem in chemical_data:
            #             size_key = chem.get('size_id')
            #             delivery_groups[size_key].append(chem)

            #         for size_id, delivery_items in delivery_groups.items():
            #             group_total_quantity = sum(safe_decimal(item.get('quantity')) for item in delivery_items)
            #             do_number = generate_packing_out_num_series()

            #             delivery_entry = parent_packing_outward_table.objects.create(
            #                 outward_no=do_number,
            #                 # receive_no=0,
            #                 # receive_date=outward_date,
            #                 company_id=company_id,
            #                 cfyear=2025, 
            #                 outward_date=safe_date(outward_date),
            #                 stiching_outward_id=material_request.id,
            #                 party_id=party_id,
            #                 quality_id=quality_id,
            #                 style_id=style_id,
            #                 work_order_no=work_order_no, 
            #                 total_quantity=group_total_quantity,
            #                 remarks=remarks,
            #                 created_by=user_id,
            #                 created_on=timezone.now()
            #             )

            #             for item in delivery_items:
            #                 child_packing_outward_table.objects.create(
            #                     tm_id=delivery_entry.id,
            #                     company_id=company_id,
            #                     cfyear=2025,
            #                     stiching_outward_id=material_request.id,
            #                     work_order_no=work_order_no,
            #                     size_id=item.get('size_id'),
            #                     quality_id=quality_id,
            #                     style_id=style_id,
            #                     color_id=item.get('color_id'),
            #                     quantity=safe_decimal(item.get('quantity')),
            #                     created_by=user_id,
            #                     created_on=timezone.now()
            #                 )
            #     except Exception as ke:
            #         print(f"❌ Packing creation error: {ke}")

            next_number = generate_outward_num_series()

            return JsonResponse({
                'status': 'success',
                'message': 'Added Successfully!',
                'inward_number': next_number
            })

        except Exception as e:
            print(f"❌ Stitching Outward Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'stiching_outward/add_stiching_delivery.html')
 
 
def ajax_report_stiching_outward(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    entry = request.POST.get('entry', '')
    quality = request.POST.get('quality', '')
    style = request.POST.get('style', '') 
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

   
    if quality: 
            query &= Q(quality_id=quality)

    if entry: 
        query &= Q(cutting_entry_id=entry)



    if style:
            query &= Q(style_id=style)



    # Apply filters
    queryset = parent_stiching_outward_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())


    # data = list(parent_stiching_outward_table.objects.filter(status=1).order_by('-id').values())
 
    formatted = [
        {
            'action': '<button type="button" onclick="stiching_delivery_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="stiching_delivery_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="stiching_delivery_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'outward_date': item['outward_date'] if item['outward_date'] else'-', 
            'outward_no': item['outward_no'] if item['outward_no'] else'-', 
            'work_order_no': item['work_order_no'] if item['work_order_no'] else'-', 
            'receive_date': item['receive_date'] if item['receive_date'] else'-', 
            'receive_no': item['receive_no'] if item['receive_no'] else'-', 
            'entry':getCutting_entryNoById(cutting_entry_table, item['cutting_entry_id'] ), 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'party':getSupplier(party_table, item['party_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
  
 


from django.db.models import Q

@csrf_exempt
def delete_stiching_delivery(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        company_id = request.session.get('company_id')

        try:
            # Check if the delivery exists
            delivery = parent_stiching_outward_table.objects.filter(id=data_id, company_id=company_id, is_active=1).first()
            if not delivery:
                return JsonResponse({'message': 'No such delivery record'})

            # Check for related packing entries (parent or child)
            has_packing_parent = parent_packing_outward_table.objects.filter(
                stiching_outward_id=data_id, company_id=company_id, is_active=1
            ).exists()

            has_packing_child = child_packing_outward_table.objects.filter(
                stiching_outward_id=data_id, company_id=company_id, is_active=1
            ).exists()

            if has_packing_parent or has_packing_child:
                return JsonResponse({'message': 'Packing records exist. Cannot delete this delivery.'})

            # No packing linked, proceed to soft delete
            parent_stiching_outward_table.objects.filter(id=data_id).update(status=0, is_active=0)
            child_stiching_outward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'Invalid request method'})




def stiching_delivery_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'stiching_outward/update_stiching_delivery.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'stiching_outward/update_stiching_delivery.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_packing_outward_table.objects.filter(tm_id=material_id)
        # inw_colors = material_instance.color_id
   
        child_data_colors = child_stiching_outward_table.objects.filter(
            status=1, 
            tm_id=material_id
        ).values_list('color_id', flat=True).distinct()


        # Get color details (id and name) for the unique color_ids
        inward_colors = color_table.objects.filter(
            status=1, 
            id__in=child_data_colors
        ).values('id', 'name')
        print('colors:',list(inward_colors))


        # Fetch the parent stock instance
        parent_stock_instance = parent_stiching_outward_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'stiching_outward/update_stiching_delivery.html', {'error_message': 'Parent stock not found.'})

        # # Fetch supplier name using supplier_id from parent_stock_instance
        # supplier_name = "-"
        # if parent_stock_instance.party_id:
        #     try: 
        #         supplier = party_table.objects.get(id=parent_stock_instance.party_id,status=1)
        #         supplier_name = supplier.name
        #     except party_table.DoesNotExist:
        #         supplier_name = "-"

        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_stiching=1,status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
     

       
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            # 'supplier_name': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'size':size,
            'color':color,
            'quality':quality,  
            'style':style,
            'inw_colors': list(inward_colors), 

        }
        print('style-id:',parent_stock_instance.style_id)
        return render(request, 'stiching_outward/update_stiching_delivery.html', context)

    except Exception as e:
        return render(request, 'stiching_outward/update_stiching_delivery.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




@csrf_exempt
def update_stiching_outward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id') 
        company_id = request.session.get('company_id')

        try:
            # Fetch and clean data
            tm_id = request.POST.get('tm_id')  # For update
            party_id = request.POST.get('party_id')
            remarks = request.POST.get('remarks') 
            style_id = request.POST.get('style_id') 
            quality_id = request.POST.get('quality_id')
            work_order_no = request.POST.get('work_order_no') 
            rec_date = request.POST.get('receive_date')
            receive_date = safe_date(rec_date) if rec_date else None  
            receive_no = request.POST.get('receive_no')
            entry_id = request.POST.get('entry_id')
            outward_date = request.POST.get('outward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
 
            # Handle checkbox for is_packing
            # is_packing_raw = request.POST.get('is_packing', '0').strip().lower()
            # is_packing = 1 if is_packing_raw in ['1', 'on', 'true'] else 0

            is_packing_raw = request.POST.get('is_packing')  # This will be '1' or '0' based on the checkbox state

            # Convert '1' -> 1 and '0' -> 0
            is_packing = 1 if is_packing_raw == '1' else 0

            print('✅ is_packing =', is_packing)  # Debugging to see if it's correctly parsed as 1 or 0

            # If tm_id exists, update the parent entry
            if tm_id:
                try:
                    material_request = parent_stiching_outward_table.objects.get(id=tm_id)
                    material_request.outward_date = outward_date
                    material_request.work_order_no = work_order_no
                    material_request.receive_no = receive_no
                    material_request.receive_date = receive_date
                    material_request.party_id = party_id 
                    material_request.quality_id = quality_id
                    material_request.style_id = style_id
                    material_request.remarks = remarks
                    material_request.is_packing = is_packing
                    material_request.updated_by = user_id
                    material_request.updated_on = timezone.now()
                    material_request.save()

                    # Delete old children
                    child_stiching_outward_table.objects.filter(tm_id=tm_id).delete()
                    parent_packing_outward_table.objects.filter(stiching_outward_id=tm_id).delete()
                    child_packing_outward_table.objects.filter(stiching_outward_id=tm_id).delete()
                except parent_stiching_outward_table.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Invalid tm_id provided'}, status=404)
            else:
                out_no = generate_outward_num_series()
                material_request = parent_stiching_outward_table.objects.create(
                    outward_no=out_no,
                    outward_date=outward_date,
                    work_order_no=work_order_no,
                    receive_no=receive_no,
                    receive_date=receive_date,
                    party_id=party_id,
                    cfyear=2025,
                    cutting_entry_id=entry_id,
                    quality_id=quality_id,
                    style_id=style_id,
                    company_id=company_id,
                    is_packing=is_packing,
                    total_quantity=0,
                    remarks=remarks,
                    created_by=user_id,
                    created_on=timezone.now()
                )

            total_quantity = Decimal('0.00')

            # Add new children
            for chemical in chemical_data:
                size_id = chemical.get('size_id', 0)
                color_id = chemical.get('color_id', 0)
                delivered_quantity = safe_decimal(chemical.get('quantity'))

                child_stiching_outward_table.objects.create(
                    tm_id=material_request.id,
                    work_order_no=work_order_no,
                    cfyear=2025,
                    company_id=company_id,
                    entry_id=entry_id or 0,
                    party_id=party_id,
                    size_id=size_id,
                    color_id=color_id,
                    style_id=style_id,
                    quality_id=quality_id,
                    quantity=delivered_quantity,
                    created_by=user_id,
                    created_on=timezone.now()
                )

                total_quantity += delivered_quantity

            material_request.total_quantity = total_quantity
            material_request.save()

            # Handle packing entries if checked
            if is_packing:
                try:
                    delivery_groups = defaultdict(list)
                    for chem in chemical_data:
                        delivery_groups[chem.get('size_id')].append(chem)

                    for size_id, delivery_items in delivery_groups.items():
                        group_total_quantity = sum(safe_decimal(item.get('quantity')) for item in delivery_items)
                        do_number = generate_packing_out_num_series()

                        delivery_entry = parent_packing_outward_table.objects.create(
                            outward_no=do_number,
                            receive_no=receive_no,
                            receive_date=receive_date,
                            company_id=company_id,
                            cfyear=2025,
                            outward_date=outward_date,
                            stiching_outward_id=material_request.id,
                            party_id=party_id,
                            quality_id=quality_id,
                            style_id=style_id,
                            work_order_no=work_order_no,
                            total_quantity=group_total_quantity,
                            remarks=remarks,
                            created_by=user_id,
                            created_on=timezone.now()
                        )

                        for item in delivery_items:
                            child_packing_outward_table.objects.create(
                                tm_id=delivery_entry.id,
                                company_id=company_id,
                                cfyear=2025,
                                stiching_outward_id=material_request.id,
                                work_order_no=work_order_no,
                                size_id=item.get('size_id'),
                                quality_id=quality_id,
                                style_id=style_id,
                                color_id=item.get('color_id'),
                                quantity=safe_decimal(item.get('quantity')),
                                created_by=user_id,
                                created_on=timezone.now()
                            )
                except Exception as pe:
                    print(f"❌ Packing creation error: {pe}")

            return JsonResponse({
                'status': 'success',
                'message': 'Stitching outward saved successfully.',
                'tm_id': material_request.id,
                'inward_number': material_request.outward_no
            })

        except Exception as e:
            print(f"❌ Stitching Outward Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'stiching_outward/add_stiching_delivery.html')




from collections import defaultdict

# @csrf_exempt
# def stiching_delivery_print(request):
#     po_id = request.GET.get('k')
#     if not po_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     try:
#         order_id = int(base64.b64decode(po_id))
#         print('ord-id:', order_id)
#     except Exception:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)

#     total_values = get_object_or_404(parent_stiching_outward_table, id=order_id)
#     party = get_object_or_404(party_table, id=total_values.party_id)
#     party_name = party.name
#     gstin = party.gstin
#     mobile = party.mobile

#     prg_details = child_stiching_outward_table.objects.filter(tm_id=order_id).values(
#         'id', 'quantity', 'size_id', 'color_id'
#     )

#     combined_details = []
    
#     # Pre-fetch common objects to avoid repeated database queries inside the loop
#     fabric_obj = get_object_or_404(fabric_table, id=total_values.fabric_id, status=1)
#     quality = get_object_or_404(quality_table, id=total_values.quality_id)
#     style = get_object_or_404(style_table, id=total_values.style_id)

#     for prg_detail in prg_details:
#         size = get_object_or_404(size_table, id=prg_detail['size_id'])
#         color = get_object_or_404(color_table, id=prg_detail['color_id'])

#         quantity = prg_detail['quantity']

#         combined_details.append({
#             'fabric': fabric_obj.name,
#             'style': style.name,
#             'quality': quality.name,
#             'color': color.name,
#             'size': size.name,
#             'quantity': quantity,
#         })

#     # Collect unique sizes in sorted order
#     sizes = sorted(set(item['size'] for item in combined_details))

#     # Group data by fabric + color
#     group_map = defaultdict(lambda: {'size_data': {}})
#     for item in combined_details:
#         key = (item['fabric'], item['color'])
#         group_map[key]['fabric'] = item['fabric']
#         group_map[key]['color'] = item['color']
#         group_map[key]['size_data'][item['size']] = {
#             'quantity': item['quantity'],
#         }

#     grouped_data = []
#     grand_total = 0

#     for val in group_map.values():
#         val['size_data_list'] = []
#         val['row_total'] = 0
#         for size in sizes:
#             entry = val['size_data'].get(size, {'quantity': ''})
#             if entry['quantity']:
#                 dozen, pcs = divmod(entry['quantity'], 12)
#                 entry['dozen_pcs'] = f"{dozen} dz ( {pcs} pcs)"
#                 val['row_total'] += entry['quantity']
#             else:
#                 entry['dozen_pcs'] = '-'
#             val['size_data_list'].append(entry)
#         grouped_data.append(val)
#         grand_total += val['row_total']

#     # Size-wise total (dict) and list (for template)
#     size_totals = {size: {'quantity': 0} for size in sizes}
#     for item in combined_details:
#         size_totals[item['size']]['quantity'] += item['quantity']

#     size_totals_list = []
#     for size in sizes:
#         total_quantity = size_totals[size]['quantity']
#         dozen, pcs = divmod(total_quantity, 12)
#         size_totals_list.append({
#             'quantity': total_quantity,
#             'dozen_pcs': f"{dozen} dz ({pcs} pcs)"
#         })

#     # Grand total in dozen and pieces
#     grand_dozen, grand_pcs = divmod(grand_total, 12)

#     context = {
#         'total_values': total_values,
#         'party_name': party_name,
#         'gstin': gstin or '-',
#         'mobile': mobile or '-',
#         'sizes': sizes,
#         'grouped_data': grouped_data,
#         'dia_totals_list': size_totals_list,
#         'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
#         'total_columns': 2 + len(sizes),
#         'company': company_table.objects.filter(status=1).first(),
#         'fabric': fabric_obj.name,
#         'style': style.name,
#         'quality': quality.name,
#         'grand_total_pcs': grand_total,
#         'grand_total_dozen_pcs': f"{grand_dozen} dz  ({grand_pcs} pcs)",
#     }

#     return render(request, 'stiching_outward/stiching_delivery_print.html', context)






# ... (your existing code)

@csrf_exempt
def stiching_delivery_print(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('ord-id:', order_id)
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_stiching_outward_table, id=order_id)
    party = get_object_or_404(party_table, id=total_values.party_id)
    party_name = party.name
    gstin = party.gstin
    mobile = party.mobile

    prg_details = child_stiching_outward_table.objects.filter(tm_id=order_id).values(
        'id', 'quantity', 'size_id', 'color_id'
    )

    combined_details = []
    
    # Pre-fetch common objects to avoid repeated database queries inside the loop
    # fabric_obj = get_object_or_404(fabric_table, id=total_values.fabric_id, status=1)
    
    fabric_obj = get_object_or_404(fabric_program_table, id=total_values.fabric_id, status=1)
    quality = get_object_or_404(quality_table, id=total_values.quality_id)
    style = get_object_or_404(style_table, id=total_values.style_id)

    for prg_detail in prg_details:
        size = get_object_or_404(size_table, id=prg_detail['size_id'])
        color = get_object_or_404(color_table, id=prg_detail['color_id'])

        quantity = prg_detail['quantity']

        combined_details.append({
            'fabric': fabric_obj.name,
            'style': style.name,    
            'quality': quality.name,
            'color': color.name,
            'size': size.name,
            'quantity': quantity,
        })

    # Collect unique sizes in sorted order
    # sizes = sorted(set(item['size'] for item in combined_details))
    sizes = sorted(set(item['size'] for item in combined_details), key=int)

    # Group data by fabric + color
    group_map = defaultdict(lambda: {'size_data': {}})
    for item in combined_details:
        key = (item['fabric'], item['color'])
        group_map[key]['fabric'] = item['fabric']
        group_map[key]['color'] = item['color']
        group_map[key]['size_data'][item['size']] = {
            'quantity': item['quantity'],
        }

    grouped_data = []
    grand_total = 0

    for val in group_map.values():
        val['size_data_list'] = []
        val['row_total'] = 0
        for size in sizes:
            entry = val['size_data'].get(size, {'quantity': ''})
            if entry['quantity']:
                dozen, pcs = divmod(entry['quantity'], 12)
                
                # Corrected logic for dozen_pcs string
                if pcs > 0:
                    entry['dozen_pcs'] = f"{dozen} dz ({pcs} pcs)"
                else:
                    entry['dozen_pcs'] = f"{dozen} dz"
                    
                val['row_total'] += entry['quantity']
            else:
                entry['dozen_pcs'] = '-'
            val['size_data_list'].append(entry)
        grouped_data.append(val)
        grand_total += val['row_total']

    # Size-wise total (dict) and list (for template)
    size_totals = {size: {'quantity': 0} for size in sizes}
    for item in combined_details:
        size_totals[item['size']]['quantity'] += item['quantity']

    size_totals_list = []
    for size in sizes:
        total_quantity = size_totals[size]['quantity']
        dozen, pcs = divmod(total_quantity, 12)

        # Corrected logic for dozen_pcs string
        if pcs > 0:
            dozen_pcs_str = f"{dozen} dz {int(pcs)} pcs"
        else:
            dozen_pcs_str = f"{dozen} dz"

        size_totals_list.append({
            'quantity': total_quantity,
            'dozen_pcs': dozen_pcs_str
        })

    # Grand total in dozen and pieces
    # grand_dozen, grand_pcs = divmod(grand_total, 12)

    # # Corrected logic for grand_total_dozen_pcs string
    # if grand_pcs > 0:
    #     grand_total_dozen_pcs_str = f"{grand_dozen} dz ({grand_pcs} pcs)"
    # else:
    #     grand_total_dozen_pcs_str = f"{grand_dozen} dz"


    grand_dozen, grand_pcs = divmod(grand_total, 12)

    # Corrected logic for grand_total_dozen_pcs string
    if grand_pcs > 0:
        grand_total_dozen_pcs_str = f"{grand_dozen} dz {int(grand_pcs)} pcs"
    else:
        grand_total_dozen_pcs_str = f"{grand_dozen} dz"

    context = {
        # ... (other context variables)
        'grand_total_pcs': grand_total,
        'grand_total_dozen_pcs': grand_total_dozen_pcs_str,
    }

    context = {
        'total_values': total_values,
        'party_name': party_name,
        'gstin': gstin or '-',
        'mobile': mobile or '-',  
        'sizes': sizes,
        'grouped_data': grouped_data,
        'dia_totals_list': size_totals_list,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'total_columns': 2 + len(sizes),
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
        'grand_total_pcs': grand_total,
        'grand_total_dozen_pcs': grand_total_dozen_pcs_str, 
    }

    return render(request, 'stiching_outward/stiching_delivery_print.html', context)


# @csrf_exempt
# def stiching_delivery_print(request):
#     po_id = request.GET.get('k') 
#     if not po_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     try:
#         order_id = int(base64.b64decode(po_id))
#         print('ord-id:',order_id)
#     except Exception:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)


#     total_values = get_object_or_404(parent_stiching_outward_table, id=order_id)
#     party = total_values.party_id
#     print('p-id:',party)
#     print('quality',total_values.quality_id)

#     party = get_object_or_404(party_table, id=total_values.party_id)
#     party_name = party.name
#     gstin = party.gstin
#     mobile = party.mobile

#     prg_details = child_stiching_outward_table.objects.filter(tm_id=order_id).values(
#         'id', 'quantity', 'size_id','color_id'
#     )
   

#     combined_details = []
#     total_quantity = 0 
 
#     for prg_detail in prg_details:
#         product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
#         fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
#         quality = get_object_or_404(quality_table, id=total_values.quality_id)
#         style = get_object_or_404(style_table, id=total_values.style_id)



#         size = get_object_or_404(size_table, id=prg_detail['size_id'])
#         color = get_object_or_404(color_table, id=prg_detail['color_id'])

     
#         quantity = prg_detail['quantity']
        

#         total_quantity += quantity
#         dozen, pcs = divmod(quantity, 12)

#         combined_details.append({
#             'fabric': fabric_obj.name,
#             'style': style.name,
#             'quality': quality.name,
#             'color': color.name,
#             'size': size.name,
#             'quantity': quantity,
#             'dozen_pcs': f"{dozen} dz + {pcs} pcs"

#         })

#     # Collect unique dia values in sorted order
#     sizes = sorted(set(item['size'] for item in combined_details))

#     # Group data by fabric + color
#     group_map = defaultdict(lambda: {'size_data': {}})
#     grouped_data = []

#     for item in combined_details:
#         key = (item['fabric'], item['color'])
#         group_map[key]['fabric'] = item['fabric']
#         group_map[key]['color'] = item['color']
#         group_map[key]['size_data'][item['size']] = {
#             'quantity': item['quantity'],
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
#         'party_name':party_name, 
#         'gstin':gstin or '-',
#         'mobile':mobile or '-',
#         'sizes': sizes,  
#         'grouped_data': grouped_data,
#         'dia_totals_list': size_totals_list,
#         'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
#         'total_columns':total_columns,
#         'company':company_table.objects.filter(status=1).first(),
#         'fabric': fabric_obj.name,
#         'style': style.name,
#         'quality': quality.name,
#         'color': color.name,
#         'size': size.name,
#         'grand_total':grand_total, 
 
#     }

#     return render(request, 'stiching_outward/stiching_delivery_print.html', context)






def tx_details_list(request):
    tm_id = request.POST.get('id')

    # Fetch child data 
    child_qs = child_stiching_outward_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')

    if child_qs.exists():
        # Calculate total quantity and total weight from child table
        total_box = child_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Fetch master cutting entry
        parent_data = parent_stiching_outward_table.objects.filter(id=tm_id).first()

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
                'color': getSupplier(color_table, item['color_id']),
                'size': getSupplier(size_table, item['size_id']),
                'quantity': item['quantity'] if item['quantity'] else '-',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            }
            for index, item in enumerate(child_data)
        ]

        # Prepare master values for summary
        
        return JsonResponse({
            'data': formatted_data,

        })

    else:
        return JsonResponse({'message': 'error', 'error_message': 'No cutting program data found for this TM ID'})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from datetime import datetime



@csrf_exempt
def update_stiching_data(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    try:
        company_id = request.session.get('company_id')
        user_id = request.session.get('user_id')
        tm_id = request.POST.get('tm_id')
        entry_id = request.POST.get('entry_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        selected_data = json.loads(request.POST.get('selected_data', '[]'))

        if not tm_id or not selected_data:
            return JsonResponse({'status': 'error', 'message': 'Missing required data'})

        is_packing = 1 if request.POST.get('is_packing') == '1' else 0

        # Update parent record
        parent = parent_stiching_outward_table.objects.get(id=tm_id)
        parent.quality_id = quality_id
        parent.style_id = style_id
        parent.is_packing = is_packing
        parent.updated_by = user_id
        parent.updated_on = timezone.now()
        parent.save()

        # Remove existing child records (if needed)
        child_stiching_outward_table.objects.filter(tm_id=tm_id).delete()

        total_qty = 0  # Initialize total_qty

        # Insert new child rows
        for row in selected_data:
            size = size_table.objects.filter(id=row['size_id']).first()
            color = color_table.objects.filter(id=row['color_id']).first()

            if not size or not color:
                # If no size or color, log or skip
                continue

            child_stiching_outward_table.objects.create(
                tm_id=parent.id,
                quality_id=quality_id,
                style_id=style_id,
                work_order_no=parent.work_order_no,
                party_id=parent.party_id,
                company_id=company_id,
                cfyear=2025,
                updated_by=user_id,
                updated_on=timezone.now(),  # Use timezone.now()
                entry_id=entry_id,  
                size_id=size.id,
                color_id=color.id,
                quantity=row['quantity']
            )

            # Ensure row['quantity'] is treated as a number (convert to integer or Decimal)
            total_qty += float(row['quantity'])  # Explicitly convert to int or Decimal
            print('p-qty:', total_qty)

        # Update the total_quantity field on the parent
        parent.total_quantity = total_qty
        parent.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



# @csrf_exempt
# def update_stiching_data(request):
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

#     try:
#         company_id = request.session.get('company_id')
#         user_id = request.session.get('user_id')
#         tm_id = request.POST.get('tm_id')
#         entry_id = request.POST.get('entry_id')
#         quality_id = request.POST.get('quality_id')
#         style_id = request.POST.get('style_id')
#         selected_data = json.loads(request.POST.get('selected_data', '[]'))

#         if not tm_id or not selected_data:
#             return JsonResponse({'status': 'error', 'message': 'Missing required data'})

#         is_packing = 1 if request.POST.get('is_packing') == '1' else 0

#         # Update parent record
#         parent = parent_stiching_outward_table.objects.get(id=tm_id)
#         parent.quality_id = quality_id
#         parent.style_id = style_id
#         parent.is_packing = is_packing
#         parent.updated_by = user_id
#         parent.updated_on = timezone.now()
#         parent.save()

#         # Remove existing child records (if needed)
#         child_stiching_outward_table.objects.filter(tm_id=tm_id).delete()

#         # Insert new child rows
#         for row in selected_data:
#             size = size_table.objects.filter(id=row['size_id']).first()
#             color = color_table.objects.filter(id=row['color_id']).first()

#             if not size or not color:
#                 continue

#             child_stiching_outward_table.objects.create(
#                 tm_id=parent.id,
#                 quality_id=quality_id,
#                 style_id=style_id,
#                 work_order_no=parent.work_order_no,
#                 party_id=parent.party_id,
#                 company_id=company_id,
#                 cfyear=2025,
#                 updated_by=user_id,
#                 updated_on=datetime.now(),  
#                 entry_id=entry_id,  
#                 size_id=size.id,
#                 color_id=color.id,
#                 quantity=row['quantity']
#             )

#             total_qty += row['quantity']
#             print('p-qty:',total_qty)
#             parent.total_quantity= total_qty
#             parent.save()

#         return JsonResponse({'status': 'success'})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)})



# @csrf_exempt
# def update_stiching_data(request):
#     if request.method == 'POST':
#         try:
#             company_id = request.session['company_id']
#             user_id = request.session['user_id']
#             tm_id = request.POST.get('tm_id')
#             entry_id = request.POST.get('entry_id')
#             quality_id = request.POST.get('quality_id')
#             style_id = request.POST.get('style_id')
#             selected_data = json.loads(request.POST.get('selected_data', '[]'))

#             if not tm_id or not selected_data:
#                 return JsonResponse({'status': 'error', 'message': 'Missing data'})

#             is_packing_raw = request.POST.get('is_packing')  # This will be '1' or '0' based on the checkbox state

#             # Convert '1' -> 1 and '0' -> 0
#             is_packing = 1 if is_packing_raw == '1' else 0

#             print('✅ is_packing =', is_packing)  # Debugging to see if it's correctly parsed as 1 or 0
#             if tm_id:
                
#                 material_request = parent_stiching_outward_table.objects.get(id=tm_id)
#                 # material_request.outward_date = outward_date
#                 # material_request.work_order_no = work_order_no
#                 # material_request.receive_no = receive_no
#                 # material_request.receive_date = receive_date
#                 # material_request.party_id = party_id 
#                 material_request.quality_id = quality_id
#                 material_request.style_id = style_id
#                 # material_request.remarks = remarks
#                 material_request.is_packing = is_packing
#                 material_request.updated_by = user_id
#                 material_request.updated_on = timezone.now()
#                 material_request.save()



#             parent = parent_stiching_outward_table.objects.get(id=tm_id)

#             for row in selected_data:
#                 size = size_table.objects.filter(name=row['size_name']).first()
#                 color = color_table.objects.filter(name=row['color_name']).first()

#                 if not size or not color:
#                     continue

#                 # # If ht_id exists, update the row
#                 # if row.get('ht_id'):
#                 #     child = child_stiching_outward_table.objects.filter(id=row['ht_id']).first()
#                 #     if child:
#                 #         child.size_id = size.id
#                 #         child.color_id = color.id
#                 #         child.quantity = row['available_quantity']
#                 #         child.quality_id = quality_id
#                 #         child.style_id = style_id
#                 #         child.updated_by = user_id
#                 #         child.updated_on = datetime.now()
#                 #         child.entry_id = entry_id
#                 #         child.save()
#                 #     continue
 

#                 child_stiching_outward_table.objects.filter(tm_id=tm_id).delete()

#                 # Otherwise, create new
#                 child_stiching_outward_table.objects.create(
#                     tm_id=parent.id,
#                     quality_id=quality_id,
#                     style_id=style_id,
#                     work_order_no=parent.work_order_no,
#                     party_id=parent.party_id,
#                     company_id=company_id,
#                     cfyear=2025,
#                     updated_by=user_id,
#                     updated_on=datetime.now(),
#                     entry_id=entry_id,
#                     size_id=size.id,
#                     color_id=color.id,
#                     quantity=row['available_quantity']
#                 )

#             return JsonResponse({'status': 'success'})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return JsonResponse({'status': 'error', 'message': 'Invalid method'})




def update_master_data(request):
    if request.method == 'POST':
        outward_date_str = request.POST.get('outward_date')
        tm_id = request.POST.get('tm_id')
        party_id = request.POST.get('party_id')
        # program_date_str = request.POST.get('program_date') 
        
        is_packing_raw = request.POST.get('is_packing')  # This will be '1' or '0' based on the checkbox state

            # Convert '1' -> 1 and '0' -> 0
        is_packing = 1 if is_packing_raw == '1' else 0

        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = parent_stiching_outward_table.objects.get(id=tm_id)
            # parent_item.outward_date = outward_date
            parent_item.is_packing = is_packing
            parent_item.party_id = party_id

            if outward_date_str:
                outward_date = datetime.strptime(outward_date_str, '%Y-%m-%d').date()
                parent_item.outward_date = outward_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except parent_stiching_outward_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})






# @csrf_exempt
# def update_stiching_data(request):
#     if request.method == 'POST':
#         try:
#             company_id = request.session['company_id']
#             user_id = request.session['user_id']
#             tm_id = request.POST.get('tm_id')
#             entry_id = request.POST.get('entry_id')
#             quality_id = request.POST.get('quality_id')
#             style_id = request.POST.get('style_id')
#             selected_data = json.loads(request.POST.get('selected_data', '[]'))

#             if not tm_id or not selected_data:
#                 return JsonResponse({'status': 'error', 'message': 'Missing data'})

#             parent = parent_stiching_outward_table.objects.get(id=tm_id)
 
#             for row in selected_data:
#                 size = size_table.objects.filter(name=row['size_name']).first()
#                 color = color_table.objects.filter(name=row['color_name']).first()

#                 if size and color:
#                     child_stiching_outward_table.objects.create(
#                         tm_id=parent.id,
#                         quality_id = quality_id,
#                         style_id=style_id,
#                         work_order_no = parent.work_order_no,
#                         party_id = parent.party_id,
#                         company_id = company_id, 
#                         cfyear=2025,
#                         updated_by = user_id,
#                         updated_on = datetime.now(),
#                         entry_id=entry_id, 
#                         size_id=size.id or 0,
#                         color_id=color.id or 0,
#                         quantity=row['available_quantity']
#                     )

#             return JsonResponse({'status': 'success'})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return JsonResponse({'status': 'error', 'message': 'Invalid method'})
