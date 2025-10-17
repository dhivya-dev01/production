from cairo import Status
from django.shortcuts import render

from django.utils.text import slugify
from pandas import cut

from accessory.models import *
from company.models import *
from employee.models import *

from grey_fabric.models import *

from django.utils.timezone import make_aware

from accessory.views import quality, quality_prg_size_list
from production_app.models import parent_stiching_inward_table
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

from common.utils import *
from production_app.models import*

from software_app.views import fabric_program, getItemNameById, getSupplier, is_ajax, knitting_program, remarks_add

# ``````````````````````````````````````````````   cutting entry ``````````````````````````````````````````


def stiching_received(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_stiching=1)
        fabric_program = fabric_program_table.objects.filter(status=1) 

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        lot = (
            cutting_entry_table.objects.filter(status=1)
            .values('lot_no')  # Group by lot_no
            .annotate(
                total_gross_wt=Sum('total_wt'),
             
            )   
            .order_by('lot_no')
        )

        stiching = parent_stiching_outward_table.objects.filter(status=1)

        return render(request,'stiching_received/stiching_received.html',{'party':party,'fabric_program':fabric_program,'stiching':stiching,'quality':quality,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    



def generate_inward_num_series(): 
    last_purchase = parent_stiching_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_no:
        match = re.search(r'INW-(\d+)', last_purchase.inward_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
 
    return f"INW-{next_num:03d}"


def stiching_received_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        party = party_table.objects.filter(status=1,is_stiching=1) 
        fabric_program = fabric_program_table.objects.filter(status=1)  

        received_no = generate_inward_num_series 
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        stiching_outward = parent_stiching_outward_table.objects.filter(status=1,is_packing=0)
        return render(request,'stiching_received/add_stiching_received.html',{'party':party,'fabric_program':fabric_program,'received_no':received_no,'color':color
                                                                  ,'stiching_outward':stiching_outward,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
     




def update_stitching_received_data(request):
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
            parent_item = parent_stiching_inward_table.objects.get(id=tm_id)
         
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

        except parent_stiching_inward_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)}) 

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'}) 


def get_stiching_delivery_list(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']

        # ✅ Get only child orders with balance > 0
        child_orders = stiching_delivery_balance_table.objects.filter(
            balance_quantity__gt=0,
            party_id=party_id
        ).values_list('outward_id', flat=True)

        # ✅ Filter parent orders that still have available stock_quantity > 0
        valid_orders = []
        for outward_id in child_orders:
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity
                    FROM (
                        -- Outward quantity
                        SELECT 
                            ce.tm_id AS outward_id,
                            SUM(ce.quantity) AS total_out_quantity,
                            0 AS total_received_quantity
                        FROM tx_stiching_outward ce
                        WHERE ce.status = 1 AND ce.tm_id = %s AND ce.quantity > 0
                        GROUP BY ce.tm_id

                        UNION ALL

                        -- Inward quantity
                        SELECT 
                            so.outward_id,
                            0 AS total_out_quantity,
                            SUM(so.quantity) AS total_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id
                    ) AS Y
                """
                cursor.execute(query, [outward_id, outward_id])
                row = cursor.fetchone()
                available_stock_quantity = row[0] if row else 0

                if available_stock_quantity and available_stock_quantity > 0:
                    valid_orders.append(outward_id)

        # ✅ Now fetch only the valid outward orders
        orders = list(parent_stiching_outward_table.objects.filter(
            id__in=valid_orders,
            status=1
        ).values('id', 'outward_no', 'work_order_no').order_by('-id'))

        # ✅ Totals only for valid outward_ids
        totals = stiching_delivery_balance_table.objects.filter(
            party_id=party_id,
            outward_id__in=valid_orders,
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




def get_party_stiching_delivery_list(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']

        
        child_orders = stiching_delivery_balance_table.objects.filter(
            balance_quantity__gt=0,
            party_id=party_id
        ).values_list('outward_id', flat=True)
 
        orders = list(parent_stiching_outward_table.objects.filter(
            id__in=child_orders, 
            status=1
        ).values('id', 'outward_no','work_order_no').order_by('-id'))

        
 
        for order in orders:
            # order['mill_name'] = mill_map.get(order['mill_id'], '')
            totals = stiching_delivery_balance_table.objects.filter(
                party_id=party_id,
                balance_quantity__gt=0
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
from django.db import connection



# def get_stiching_delivery_details(request):
#     if request.method == "POST":
#         outward_id = request.POST.get("outward_id")
#         tm_id = request.POST.get("tm_id")  # optional

#         if not outward_id:
#             return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

#         with connection.cursor() as cursor:
#             if tm_id:
#                 query = """
#                     SELECT 
#                         Y.outward_id,
#                         Y.size_id,
#                         Y.color_id, 
#                         SUM(Y.total_out_quantity) AS total_out_quantity,
#                         SUM(Y.total_received_quantity) AS total_received_quantity,
#                         SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity
#                         FROM (
#                         SELECT 
#                             ce.tm_id AS outward_id,
#                             ce.size_id,
#                             ce.color_id, 
#                             SUM(ce.quantity) AS total_out_quantity,
#                             0 AS total_received_quantity
#                         FROM tx_stiching_outward ce
#                         WHERE ce.status = 1 AND ce.tm_id= %s AND ce.quantity>0
#                         GROUP BY ce.size_id, ce.color_id,ce.tm_id

#                         UNION ALL

#                         SELECT 
#                                 so.outward_id AS outward_id, 
#                             so.size_id,
#                             so.color_id,
#                             0 AS total_out_quantity,
#                             SUM(so.quantity) AS total_received_quantity
#                         FROM tx_stiching_inward so
#                         WHERE so.status = 1 AND so.outward_id=%s AND so.tm_id=%s AND so.quantity>0
#                         GROUP BY so.size_id, so.color_id,so.outward_id
#                         ) AS Y
#                         GROUP BY Y.size_id, Y.color_id,Y.outward_id
#                         ORDER BY Y.size_id, Y.color_id
#                 """
#                 params = [outward_id, outward_id, tm_id]
#             else:
#                 query = """
#                     SELECT 
#                         Y.outward_id,
#                         Y.size_id,
#                         Y.color_id,
#                         SUM(Y.total_out_quantity) AS total_out_quantity,
#                         SUM(Y.total_received_quantity) AS total_received_quantity,
#                         SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity
#                         FROM (
#                         SELECT 
#                             ce.tm_id AS outward_id,
#                             ce.size_id,
#                             ce.color_id,
#                             SUM(ce.quantity) AS total_out_quantity,
#                             0 AS total_received_quantity
#                         FROM tx_stiching_outward ce
#                         WHERE ce.status = 1 AND ce.tm_id= %s AND ce.quantity>0
#                         GROUP BY ce.size_id, ce.color_id,ce.tm_id

#                         UNION ALL

#                         SELECT 
#                                 so.outward_id AS outward_id,
#                             so.size_id,
#                             so.color_id,
#                             0 AS total_out_quantity,
#                             SUM(so.quantity) AS total_received_quantity
#                         FROM tx_stiching_inward so
#                         WHERE so.status = 1 AND so.outward_id=%s AND so.quantity>0
#                         GROUP BY so.size_id, so.color_id,so.outward_id
#                         ) AS Y
#                         GROUP BY Y.size_id, Y.color_id,Y.outward_id
#                         ORDER BY Y.size_id, Y.color_id
#                 """
#                 params = [outward_id, outward_id]

#             cursor.execute(query, params)
#             columns = [col[0] for col in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#             print('results:',results)
#         # Attach size/color names
#         size_ids = {row['size_id'] for row in results} 
#         color_ids = {row['color_id'] for row in results}

#         sizes = size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name')
#         colors = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name')

#         size_map = {s['id']: s['name'] for s in sizes}
#         color_map = {c['id']: c['name'] for c in colors}

#         for row in results:
#             row['size_name'] = size_map.get(row['size_id'], '')
#             row['color_name'] = color_map.get(row['color_id'], '')


#         try: 
#             inward = parent_stiching_outward_table.objects.get(status=1, id=outward_id)
#             fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id','name').first()
#             quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
#             style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
#         except parent_stiching_outward_table.DoesNotExist:
#             quality = None
#             style = None

#         return JsonResponse({
#             'status': 'success',
#             'data': results,
#             'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
#             'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
#             'style': {'id': style['id'], 'name': style['name']} if style else ''
#         })

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def get_stiching_delivery_details(request):
    if request.method == "POST":
        outward_id = request.POST.get("outward_id")
        tm_id = request.POST.get("tm_id")  # optional

        if not outward_id:
            return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

        with connection.cursor() as cursor:
            if tm_id:
                query = """
                    SELECT 
                        Y.outward_id,
                        Y.size_id,
                        Y.color_id, 
                        SUM(Y.total_out_quantity) AS total_out_quantity,
                        SUM(Y.total_received_quantity) AS total_received_quantity,
                        SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity,
                        SUM(Y.already_received_quantity) AS already_received_quantity
                    FROM (
                        -- Outward quantity
                        SELECT 
                            ce.tm_id AS outward_id,
                            ce.size_id,
                            ce.color_id, 
                            SUM(ce.quantity) AS total_out_quantity,
                            0 AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_outward ce
                        WHERE ce.status = 1 AND ce.tm_id = %s AND ce.quantity > 0
                        GROUP BY ce.tm_id, ce.size_id, ce.color_id

                        UNION ALL

                        -- Received quantity (all tm_ids)
                        SELECT 
                            so.outward_id,
                            so.size_id,
                            so.color_id,
                            0 AS total_out_quantity,
                            SUM(so.quantity) AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id, so.size_id, so.color_id

                        UNION ALL

                        -- Already received (specific tm_id)
                        SELECT 
                            so.outward_id,
                            so.size_id,
                            so.color_id, 
                            0 AS total_out_quantity,
                            0 AS total_received_quantity,
                            SUM(so.quantity) AS already_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.tm_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id, so.size_id, so.color_id
                    ) AS Y
                    GROUP BY Y.outward_id, Y.size_id, Y.color_id
                    HAVING (SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity)) > 0
                    ORDER BY Y.size_id, Y.color_id
                """
                params = [tm_id, outward_id, outward_id, tm_id]
            else:
                query = """
                    SELECT 
                        Y.outward_id,
                        Y.size_id,
                        Y.color_id,
                        SUM(Y.total_out_quantity) AS total_out_quantity,
                        SUM(Y.total_received_quantity) AS total_received_quantity,
                        SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity,
                        0 AS already_received_quantity
                    FROM (
                        SELECT 
                            ce.tm_id AS outward_id,
                            ce.size_id,
                            ce.color_id,
                            SUM(ce.quantity) AS total_out_quantity,
                            0 AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_outward ce
                        WHERE ce.status = 1 AND ce.tm_id = %s AND ce.quantity > 0
                        GROUP BY ce.tm_id, ce.size_id, ce.color_id

                        UNION ALL

                        SELECT 
                            so.outward_id,
                            so.size_id,
                            so.color_id,
                            0 AS total_out_quantity,
                            SUM(so.quantity) AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id, so.size_id, so.color_id
                    ) AS Y
                    GROUP BY Y.outward_id, Y.size_id, Y.color_id
                    HAVING (SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity)) > 0
                    ORDER BY Y.size_id, Y.color_id
                """
                params = [outward_id, outward_id]

            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description] 
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # --- size/color names mapping ---
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
            inward = parent_stiching_outward_table.objects.get(status=1, id=outward_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
        except parent_stiching_outward_table.DoesNotExist:
            fabric = quality = style = None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else ''
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




def get_stiching_delivery_details_23_8_25(request):
    if request.method == "POST":
        outward_id = request.POST.get("outward_id")
        tm_id = request.POST.get("tm_id")  # optional

        if not outward_id:
            return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

        with connection.cursor() as cursor:
            if tm_id:
                query = """
                    SELECT 
                        Y.outward_id,
                        Y.size_id,
                        Y.color_id, 
                        SUM(Y.total_out_quantity) AS total_out_quantity,
                        SUM(Y.total_received_quantity) AS total_received_quantity,
                        SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity,
                        SUM(Y.already_received_quantity) AS already_received_quantity
                    FROM (
                        -- Outward quantity from outward table
                        SELECT 
                            ce.tm_id AS outward_id,
                            ce.size_id,
                            ce.color_id, 
                            SUM(ce.quantity) AS total_out_quantity,
                            0 AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_outward ce
                        WHERE ce.status = 1 AND ce.tm_id = %s AND ce.quantity > 0
                        GROUP BY ce.tm_id, ce.size_id, ce.color_id

                        UNION ALL

                        -- Total received quantity from inward table (all tm_ids)
                        SELECT 
                            so.outward_id,
                            so.size_id,
                            so.color_id,
                            0 AS total_out_quantity,
                            SUM(so.quantity) AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id, so.size_id, so.color_id

                        UNION ALL

                        -- Already received quantity for specific tm_id
                        SELECT 
                            so.outward_id,
                            so.size_id,
                            so.color_id, 
                            0 AS total_out_quantity,
                            0 AS total_received_quantity,
                            SUM(so.quantity) AS already_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.tm_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id, so.size_id, so.color_id
                    ) AS Y
                    GROUP BY Y.outward_id, Y.size_id, Y.color_id
                    ORDER BY Y.size_id, Y.color_id
                """
                params = [tm_id, outward_id, outward_id, tm_id]
            else:
                query = """
                    SELECT 
                        Y.outward_id,
                        Y.size_id,
                        Y.color_id,
                        SUM(Y.total_out_quantity) AS total_out_quantity,
                        SUM(Y.total_received_quantity) AS total_received_quantity,
                        SUM(Y.total_out_quantity) - SUM(Y.total_received_quantity) AS available_stock_quantity,
                        0 AS already_received_quantity
                    FROM (
                        SELECT 
                            ce.tm_id AS outward_id,
                            ce.size_id,
                            ce.color_id,
                            SUM(ce.quantity) AS total_out_quantity,
                            0 AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_outward ce
                        WHERE ce.status = 1 AND ce.tm_id = %s AND ce.quantity > 0
                        GROUP BY ce.tm_id, ce.size_id, ce.color_id

                        UNION ALL

                        SELECT 
                            so.outward_id,
                            so.size_id,
                            so.color_id,
                            0 AS total_out_quantity,
                            SUM(so.quantity) AS total_received_quantity,
                            0 AS already_received_quantity
                        FROM tx_stiching_inward so
                        WHERE so.status = 1 AND so.outward_id = %s AND so.quantity > 0
                        GROUP BY so.outward_id, so.size_id, so.color_id
                    ) AS Y
                    GROUP BY Y.outward_id, Y.size_id, Y.color_id
                    ORDER BY Y.size_id, Y.color_id
                """
                params = [outward_id, outward_id] 

            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description] 
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # print('results:', results)
            # results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # # Filter out rows where available_stock_quantity is 0 or less
            # results = [row for row in results if float(row['available_stock_quantity']) > 0]
            # print('Filtered results:', results)

        # Get size/color names
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
            inward = parent_stiching_outward_table.objects.get(status=1, id=outward_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
        except parent_stiching_outward_table.DoesNotExist:
            fabric = quality = style = None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else ''
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




from collections import defaultdict
from django.db.models import Sum

def get_stiching_delivery_edit_details(request):
    if request.method == "POST":
        outward_id = request.POST.get("outward_id")
        tm_id = request.POST.get("tm_id")  # optional

        if not outward_id:
            return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

        outward_data = child_stiching_outward_table.objects.filter(status=1, tm_id=outward_id, quantity__gt=0).order_by('-id')
        outward_group = outward_data.values('size_id', 'color_id').annotate(total_out_quantity=Sum('quantity'))

        # Build result map: (size_id, color_id) => outward data
        result_map = {}
        for entry in outward_group:
            key = (entry['size_id'], entry['color_id'])
            result_map[key] = {
                'size_id': entry['size_id'],
                'color_id': entry['color_id'],
                'outward_id': outward_id,
                'total_out_quantity': entry['total_out_quantity'] or 0,
                'total_received_quantity': 0,
                'already_received_quantity': 0,
                'available_stock_quantity': 0
            }

        # Add total received (all tm_ids)
        total_received = child_stiching_inward_table.objects.filter(
            status=1, outward_id=outward_id, quantity__gt=0
        ).values('size_id', 'color_id').annotate(total_received=Sum('quantity'))

        for entry in total_received:
            key = (entry['size_id'], entry['color_id'])
            if key not in result_map:
                result_map[key] = {
                    'size_id': entry['size_id'],
                    'color_id': entry['color_id'],
                    'outward_id': outward_id,
                    'total_out_quantity': 0,
                    'total_received_quantity': 0,
                    'already_received_quantity': 0,
                    'available_stock_quantity': 0
                }
            result_map[key]['total_received_quantity'] = entry['total_received'] or 0

        # Add already received (for provided tm_id)
        if tm_id:
            already_received = child_stiching_inward_table.objects.filter(
                status=1, outward_id=outward_id, tm_id=tm_id, quantity__gt=0
            ).values('size_id', 'color_id').annotate(received_by_tm=Sum('quantity'))

            for entry in already_received:
                key = (entry['size_id'], entry['color_id'])
                if key not in result_map:
                    result_map[key] = {
                        'size_id': entry['size_id'],
                        'color_id': entry['color_id'],
                        'outward_id': outward_id,
                        'total_out_quantity': 0,
                        'total_received_quantity': 0,
                        'already_received_quantity': 0,
                        'available_stock_quantity': 0
                    }
                result_map[key]['already_received_quantity'] = entry['received_by_tm'] or 0

        # Compute available_stock_quantity
        for row in result_map.values():
            row['available_stock_quantity'] = row['total_out_quantity'] - row['total_received_quantity']

        results = list(result_map.values())

        # Fetch size/color names
        size_ids = {row['size_id'] for row in results}
        color_ids = {row['color_id'] for row in results}

        sizes = size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name').order_by('-sort_order_no')
        colors = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name').order_by('-name')

        size_map = {s['id']: s['name'] for s in sizes}
        color_map = {c['id']: c['name'] for c in colors}

        for row in results:
            row['size_name'] = size_map.get(row['size_id'], '')
            row['color_name'] = color_map.get(row['color_id'], '')

        try:
            inward = parent_stiching_outward_table.objects.get(status=1, id=outward_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
        except parent_stiching_outward_table.DoesNotExist:
            fabric = quality = style = None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else ''
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})





@csrf_exempt
def insert_stiching_received(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            party_id = request.POST.get('party_id', 0)
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            dc_no = request.POST.get('dc_no')
            dc_date = request.POST.get('dc_date')
            program_date = request.POST.get('inward_date')
            cutting_data = json.loads(request.POST.get('chemical_data', '[]'))
            lot_no = request.POST.get('lot_no') or ''
            work_order_no = request.POST.get('work_order_no')
            outward_id = request.POST.get('outward_id')
            fabric_id = request.POST.get('fabric_id')

            inward_no = generate_inward_num_series()

            # Create Parent Entry
            material_request = parent_stiching_inward_table.objects.create(
                inward_no=inward_no.upper(),
                inward_date=program_date,
                dc_no = dc_no,
                dc_date = dc_date,
                work_order_no=work_order_no,
                party_id=party_id,
                outward_id=outward_id,
                fabric_id = fabric_id,
                quality_id=quality_id,
                style_id=style_id,
                company_id=company_id,
                cfyear=2025,
                total_quantity=0,
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_qty = Decimal('0.00')

            # Create Sub Entries
            # for cutting in cutting_data:
            #     quantity = safe_decimal(cutting.get('quantity', 0))
            #     total_qty += quantity

            #     child_stiching_inward_table.objects.create(
            #         tm_id=material_request.id,
            #         work_order_no=work_order_no,
            #         quality_id=quality_id,
            #         style_id=style_id,
            #         outward_id=outward_id,
            #         size_id=cutting.get('size_id'),
            #         color_id=cutting.get('color_id'),
            #         quantity=quantity,
            #         created_by=user_id,
            #         created_on=timezone.now(),
            #         company_id=company_id,
            #         cfyear=2025,
            #     )


            # Create Sub Entries
            # Create Sub Entries
            for cutting in cutting_data:
                quantity = safe_decimal(cutting.get('quantity', 0))

                if quantity == 0:
                    continue  # 🔁 Skip storing this row if quantity is zero

                total_qty += quantity

                child_stiching_inward_table.objects.create(
                    tm_id=material_request.id,
                    work_order_no=work_order_no,
                    quality_id=quality_id,
                    style_id=style_id,
                    outward_id=outward_id,
                    size_id=cutting.get('size_id'),
                    color_id=cutting.get('color_id'),
                    quantity=quantity,
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,
                )



            # Update total quantity once after all entries
            material_request.total_quantity = total_qty
            material_request.save()

            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f"❌ Error in stitching received insert: {e}")
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'stiching_received/add_stiching_received.html')



def ajax_report_stiching_received(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})


    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    outward = request.POST.get('outward', '')
    quality = request.POST.get('quality', '')
    style = request.POST.get('style', '') 
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Match if either created_on or updated_on falls in range
            date_filter = Q(inward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
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

    if outward: 
        query &= Q(outward_id=outward)


 
    if style:
            query &= Q(style_id=style)



    # Apply filters
    queryset = parent_stiching_inward_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())



    # data = list(parent_stiching_inward_table.objects.filter(status=1).order_by('-id').values())
 
    formatted = [
        
        {
            'action': '<button type="button" onclick="stiching_received_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="stiching_received_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="stiching_received_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'inward_no': item['inward_no'] if item['inward_no'] else'-', 
            'work_order_no': item['work_order_no'] if item['work_order_no'] else'-', 
            'outward':getStichingDeliveryNoById(parent_stiching_outward_table, item['outward_id'] ), 
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
def delete_stiching_received(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        company_id = request.session.get('company_id')

        try:
            # Check if the delivery exists
            delivery = parent_stiching_inward_table.objects.filter(id=data_id, company_id=company_id, is_active=1).first()
            if not delivery:
                return JsonResponse({'message': 'No such delivery record'})

            # # Check for related packing entries (parent or child)
            # has_packing_parent = parent_packing_inward_table.objects.filter(
            #     stiching_outward_id=data_id, company_id=company_id, is_active=1
            # ).exists()

            # has_packing_child = child_packing_inward_table.objects.filter(
            #     stiching_outward_id=data_id, company_id=company_id, is_active=1
            # ).exists()

            # if has_packing_parent or has_packing_child:
            #     return JsonResponse({'message': 'Packing records exist. Cannot delete this delivery.'})

            # No packing linked, proceed to soft delete
            parent_stiching_inward_table.objects.filter(id=data_id).update(status=0, is_active=0)
            child_stiching_inward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'Invalid request method'})




def stiching_received_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'stiching_received/update_stiching_received.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'stiching_received/update_stiching_received.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_stiching_inward_table.objects.filter(tm_id=material_id).first()
   
        # Fetch the parent stock instance
        parent_stock_instance = parent_stiching_inward_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'stiching_received/update_stiching_received.html', {'error_message': 'Parent stock not found.'})


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
           
        }
        print('style-id:',parent_stock_instance.style_id)
        return render(request, 'stiching_received/update_stiching_received.html', context)

    except Exception as e:
        return render(request, 'stiching_received/update_stiching_received.html', {'error_message': 'An unexpected error occurred: ' + str(e)})





@csrf_exempt
def update_stiching_received(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')

            master_id = request.POST.get('tm_id')
            dc_no = request.POST.get('dc_no')
            dc_date = request.POST.get('dc_date')
            remarks = request.POST.get('remarks')
            work_order_no = request.POST.get('work_order_no')
            print('wk-no:',work_order_no)
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            fabric_id = request.POST.get('fabric_id')

            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            chemical_data = request.POST.get('chemical_data')
            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'})

            table_data = json.loads(chemical_data)
            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Step 1: Update master table entry
            material_request = parent_stiching_inward_table.objects.filter(id=master_id).first()
            if not material_request:
                return JsonResponse({'success': False, 'error_message': 'Invalid master ID'})

            # material_request.inward_date = inward_date
            material_request.remarks = remarks
            material_request.dc_no = dc_no
            material_request.dc_date = dc_date
            material_request.work_order_no=work_order_no
            material_request.quality_id = quality_id
            material_request.fabric_id=fabric_id
            material_request.style_id = style_id
            material_request.updated_by = user_id 
            material_request.updated_on = timezone.now()

            # Step 2: Delete existing child entries
            child_stiching_inward_table.objects.filter(tm_id=master_id).delete()

            total_qty = Decimal('0.000')

            # Step 3: Insert updated child entries
            # for row in table_data:
            #     quantity = safe_decimal(row.get('quantity', 0))
            #     total_qty += quantity

            #     child_stiching_inward_table.objects.create(
            #         tm_id=material_request.id,
            #         work_order_no=work_order_no,
            #         quality_id=quality_id,
            #         style_id=style_id,
            #         outward_id=row.get('outward_id'),
            #         size_id=row.get('size_id'),
            #         color_id=row.get('color_id'),
            #         quantity=quantity,
            #         company_id=company_id,
            #         cfyear=2025,
            #         status=1,
            #         is_active=1,
            #         created_by=user_id,
            #         updated_by=user_id,
            #         created_on=timezone.now(),
            #         updated_on=timezone.now()
            #     )


            for cutting in table_data:
                quantity = safe_decimal(cutting.get('quantity', 0))

                if quantity == 0:
                    continue  # 🔁 Skip storing this row if quantity is zero

                total_qty += quantity

                child_stiching_inward_table.objects.create(
                    tm_id=material_request.id,
                    work_order_no=work_order_no,
                    quality_id=quality_id,
                    style_id=style_id,
                    outward_id=cutting.get('outward_id'),
                    size_id=cutting.get('size_id'),
                    color_id=cutting.get('color_id'),
                    quantity=quantity,
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,
                ) 

            # Step 4: Update master total quantity
            material_request.total_quantity = total_qty
            material_request.save()

          
            return JsonResponse({'success': True, 'message': 'Updated successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})





from collections import defaultdict

@csrf_exempt
def stiching_received_print(request):
    po_id = request.GET.get('k') 
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('ord-id:',order_id)
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_stiching_inward_table, id=order_id)
    print('quality',total_values.quality_id)


    party = get_object_or_404(party_table, id=total_values.party_id)
    party_name = party.name
    gstin = party.gstin
    mobile = party.mobile

    prg_details = child_stiching_inward_table.objects.filter(tm_id=order_id).values(
        'id', 'quantity', 'size_id','color_id'
    )
   
    combined_details = []
    total_quantity = 0 
 
    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        quality = get_object_or_404(quality_table, id=total_values.quality_id)
        style = get_object_or_404(style_table, id=total_values.style_id)



        size = get_object_or_404(size_table, id=prg_detail['size_id'])
        color = get_object_or_404(color_table, id=prg_detail['color_id'])

     
        quantity = prg_detail['quantity']
        

        total_quantity += quantity

        combined_details.append({
            'fabric': fabric_obj.name,
            'style': style.name,
            'quality': quality.name,
            'color': color.name,
            'size': size.name,
            'quantity': quantity,
        })

    # Collect unique dia values in sorted order
    # sizes = sorted(set(item['size'] for item in combined_details))
    sizes = sorted(set(item['size'] for item in combined_details), key=int)

    # Group data by fabric + color
    group_map = defaultdict(lambda: {'size_data': {}})
    grouped_data = []

    for item in combined_details:
        key = (item['fabric'], item['color'])
        group_map[key]['fabric'] = item['fabric']
        group_map[key]['color'] = item['color']
        group_map[key]['size_data'][item['size']] = {
            'quantity': item['quantity'],
        }

    

    for val in group_map.values():
    # Prebuild size_data_list to avoid dynamic dict access in template
        val['size_data_list'] = [
            val['size_data'].get(size, {'quantity': ''}) for size in sizes
        ]

        # Compute row total
        val['row_total'] = sum(entry['quantity'] for entry in val['size_data_list'] if entry['quantity'])

        grouped_data.append(val)
        grand_total = sum(val['row_total'] for val in grouped_data) 
 
 
    # size-wise total (dict) and list (for template)
    size_totals = {size: {'quantity': 0} for size in sizes}
    for item in combined_details:
        size_totals[item['size']]['quantity'] += item['quantity']

    size_totals_list = [size_totals[size] for size in sizes]
    total_columns = 2 + len(sizes) * 2

    context = {

        'total_values': total_values,
        'party_name':party_name,
        'gstin':gstin,
        'mpbile':mobile,
        'sizes': sizes,
        'grouped_data': grouped_data,
        'dia_totals_list': size_totals_list,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'total_columns':total_columns,
        'company':company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
        'color': color.name,
        'size': size.name,
        'grand_total':grand_total,
 
    }

    return render(request, 'stiching_received/stiching_received_print.html', context)

