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


def packing_delivery(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_ironing=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
       
        lot = (
            parent_packing_outward_table.objects
            .filter(status=1)
            .values('work_order_no')  # Group by work_order_no
            .annotate(
                total_gross_wt=Sum('total_quantity'),
             
            )   
            .order_by('work_order_no')
        )

    

        return render(request,'packing_delivery/packing_delivery.html',{'party':party,'fabric_program':fabric_program,'quality':quality,'style':style,'lot':lot})
    else:
        return HttpResponseRedirect("/admin")
    




def packing_delivery_list(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 
 
    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})


    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    work_order = request.POST.get('work_no', '')
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

    if work_order: 
        query &= Q(work_order_no=work_order)



    if style:
            query &= Q(style_id=style)



    # Apply filters
    queryset = parent_packing_outward_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())

    # data = list(parent_packing_outward_table.objects.filter(status=1).order_by('-id').values())
 
    formatted = [
        {
            'action': '<button type="button" onclick="packing_delivery_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="packing_delivery_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="packing_delivery_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'outward_no': item['outward_no'] if item['outward_no'] else'-', 
            'outward_date': item['outward_date'] if item['outward_date'] else'-', 
            'work_order_no': item['work_order_no'] if item['work_order_no'] else'-', 
            'inward':getStichingDeliveryNoById(parent_stiching_inward_table, item['inward_id'] ) or '-', 
            'quality':getSupplier(quality_table, item['quality_id'] ),  
            'party':getSupplier(party_table, item['party_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ),  
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
  




def generate_delivery_num_series():
    last_purchase = parent_packing_outward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.outward_no:
        match = re.search(r'P-(\d+)', last_purchase.outward_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
 
    return f"P-{next_num:03d}"
 

def packing_delivery_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_ironing=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 

        delivery_no = generate_delivery_num_series()

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)   
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        cutting_program = cutting_program_table.objects.filter(status=1)
        return render(request,'packing_delivery/add_packing_delivery.html',{'party':party,'fabric_program':fabric_program,'delivery_no':delivery_no,'color':color
                                                                  ,'cutting_program':cutting_program,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
     
     
 
def get_stiching_received_avl_list(request):
    if request.method == 'POST' and 'party_id' in request.POST: 
        party_id = request.POST['party_id']

        # Get all inward_ids which still have balance quantity
        child_orders = stiching_received_balance_table.objects.filter(
            balance_quantity__gt=0
        ).values_list('inward_id', flat=True)

        # Get parent orders from those inward_ids
        parent_orders = parent_stiching_inward_table.objects.filter( 
            id__in=child_orders,
            status=1
        ).order_by('-id')

        orders = []
        total_po_quantity = 0
        total_inward_quantity = 0
        total_balance_quantity = 0

        for order in parent_orders:
            inward_id = order.id

            # SQL query to get available stock for this inward_id
            with connection.cursor() as cursor:
                query = """
                   SELECT 
                        SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
                    FROM (
                        SELECT 
                            ce.tm_id AS inward_id,
                            ce.size_id,
                            ce.color_id,
                            SUM(ce.quantity) AS total_in_quantity,
                            0 AS total_out_quantity
                        FROM tx_stiching_inward ce
                        WHERE ce.status = 1 AND ce.tm_id = %s
                        GROUP BY ce.size_id, ce.color_id

                        UNION ALL
 
                        SELECT 
                            so.inward_id AS inward_id,
                            so.size_id,
                            so.color_id, 
                            0 AS total_in_quantity,
                            SUM(so.quantity) AS total_out_quantity 
                        FROM tx_packing_outward so
                        WHERE so.status = 1 AND so.inward_id = %s
                        GROUP BY so.size_id, so.color_id
                    ) AS Y
                """
                cursor.execute(query, [inward_id, inward_id])
                result = cursor.fetchone()
                available_stock_quantity = result[0] or 0

            # Only include if stock is available
            if available_stock_quantity > 0:
                orders.append({
                    'id': order.id,
                    'inward_no': order.inward_no,
                    'work_order_no': order.work_order_no,
                })

                # Optional: calculate total po/in/balance if needed
                totals = stiching_received_balance_table.objects.filter(
                    inward_id=order.id,
                    balance_quantity__gt=0
                ).aggregate(
                    po_quantity=Sum('po_quantity'),
                    inward_quantity=Sum('in_quantity'),
                    balance_quantity=Sum('balance_quantity')
                )

                total_po_quantity += float(totals['po_quantity'] or 0)
                total_inward_quantity += float(totals['inward_quantity'] or 0)
                total_balance_quantity += float(totals['balance_quantity'] or 0)

        return JsonResponse({
            'orders': orders,
            'po_quantity': total_po_quantity,
            'inward_quantity': total_inward_quantity,
            'balance_quantity': total_balance_quantity
        })

    return JsonResponse({'orders': []})





from django.db import connection

# def get_stiching_summary_stock(request):
#     if request.method == "POST":
#         # inward_id = request.POST.get("inward_id")
#         inward_id = request.POST.getlist("inward_id[]") or request.POST.getlist("inward_id")

#         tm_id = request.POST.get("tm_id")  # optional

#         if not inward_id:
#             return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

#         with connection.cursor() as cursor:
#             if tm_id:
#                 query = """
#                     SELECT 
#                         Y.inward_id, 
#                         Y.size_id,
#                         Y.color_id,
#                         SUM(Y.total_in_quantity) AS total_in_quantity,
#                         SUM(Y.total_out_quantity) AS total_out_quantity,
#                         SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
#                         FROM (
#                         SELECT 
#                             ce.tm_id as inward_id,
#                             ce.size_id,
#                             ce.color_id,
#                             SUM(ce.quantity) AS total_in_quantity,
#                             0 AS total_out_quantity
#                         FROM tx_stiching_inward ce
#                         WHERE ce.status = 1 AND ce.tm_id = %s
#                         GROUP BY ce.size_id, ce.color_id

#                         UNION ALL

#                         SELECT 
#                             so.inward_id AS inward_id,
#                             so.size_id,
#                             so.color_id,
#                             0 AS total_in_quantity,
#                             SUM(so.quantity) AS total_out_quantity
#                         FROM tx_packing_outward so
#                         WHERE so.status = 1 AND so.inward_id = %s AND so.tm_id = %s
#                         GROUP BY so.size_id, so.color_id
#                         ) AS Y
#                         GROUP BY Y.size_id, Y.color_id
#                         ORDER BY Y.size_id, Y.color_id
#                 """
#                 params = [inward_id, inward_id, tm_id] 
#             else:
#                 query = """
#                    SELECT *
# FROM (
#     SELECT 
#         Y.inward_id,
#         Y.quality_id,
#         Y.style_id,
#         Y.size_id,
#         Y.color_id,
#         SUM(Y.total_in_quantity) AS total_in_quantity,
#         SUM(Y.total_out_quantity) AS total_out_quantity,
#         SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
#     FROM (
#         SELECT 
#             ce.tm_id AS inward_id,
#             ce.quality_id,
#             ce.style_id,
#             ce.size_id,
#             ce.color_id,
#             SUM(ce.quantity) AS total_in_quantity,
#             0 AS total_out_quantity
#         FROM tx_stiching_inward ce
#         WHERE ce.status = 1 AND ce.tm_id = %s
#         GROUP BY ce.size_id, ce.color_id, ce.tm_id, ce.quality_id, ce.style_id

#         UNION ALL

#         SELECT 
#             so.inward_id AS inward_id,
#             so.quality_id,
#             so.style_id,
#             so.size_id,
#             so.color_id,
#             0 AS total_in_quantity,
#             SUM(so.quantity) AS total_out_quantity
#         FROM tx_packing_outward so
#         WHERE so.status = 1 AND so.inward_id = %s
#         GROUP BY so.size_id, so.color_id, so.inward_id, so.quality_id, so.style_id
#     ) AS Y
#     GROUP BY Y.quality_id, Y.style_id, Y.size_id, Y.color_id, Y.inward_id
# ) AS final
# WHERE final.available_stock_quantity > 0
# ORDER BY final.quality_id, final.style_id, final.size_id, final.color_id;

#                 """
#                 params = [inward_id, inward_id]


#             cursor.execute(query, params)
#             columns = [col[0] for col in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#             # print('results:',results)
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
#             inward = parent_stiching_inward_table.objects.get(status=1, id=inward_id)
#             fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id').first()
#             quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id','name').first()
#             style = style_table.objects.filter(status=1, id=inward.style_id).values('id','name').first()
#         except parent_stiching_inward_table.DoesNotExist:
#             quality = None
#             style = None
#             fabric=None

#         return JsonResponse({
#             'status': 'success',
#             'data': results,
#             'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
#             'style': {'id': style['id'], 'name': style['name']} if style else '',
#             'fabric':fabric,
#         })

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




from django.db import connection
from django.http import JsonResponse

def get_stiching_summary_stock(request):
    if request.method == "POST":
        inward_ids = request.POST.getlist("inward_id[]") or request.POST.getlist("inward_id")
        tm_id = request.POST.get("tm_id")  # optional

        if not inward_ids:
            return JsonResponse({'status': 'error', 'message': 'Inward ID(s) required.'})

        # Convert to tuple for SQL IN clause
        inward_ids = tuple(map(int, inward_ids))

        with connection.cursor() as cursor:
            if tm_id:
                # NOTE: You’ll need to modify this query if supporting multiple inward_ids with tm_id
                return JsonResponse({'status': 'error', 'message': 'tm_id with multiple inward_ids not supported yet.'})
            else:
                query = f"""
                    SELECT *
                    FROM (
                        SELECT 
                            Y.inward_id,
                            Y.quality_id,
                            Y.style_id,
                            Y.size_id,
                            Y.color_id,
                            SUM(Y.total_in_quantity) AS total_in_quantity,
                            SUM(Y.total_out_quantity) AS total_out_quantity,
                            SUM(Y.total_in_quantity) - SUM(Y.total_out_quantity) AS available_stock_quantity
                        FROM (
                            SELECT 
                                ce.tm_id AS inward_id,
                                ce.quality_id,
                                ce.style_id,
                                ce.size_id,
                                ce.color_id,
                                SUM(ce.quantity) AS total_in_quantity,
                                0 AS total_out_quantity
                            FROM tx_stiching_inward ce
                            WHERE ce.status = 1 AND ce.tm_id IN %s
                            GROUP BY ce.size_id, ce.color_id, ce.tm_id, ce.quality_id, ce.style_id

                            UNION ALL

                            SELECT 
                                so.inward_id AS inward_id,
                                so.quality_id,
                                so.style_id,
                                so.size_id,
                                so.color_id,
                                0 AS total_in_quantity,
                                SUM(so.quantity) AS total_out_quantity
                            FROM tx_packing_outward so
                            WHERE so.status = 1 AND so.inward_id IN %s
                            GROUP BY so.size_id, so.color_id, so.inward_id, so.quality_id, so.style_id
                        ) AS Y
                        GROUP BY Y.quality_id, Y.style_id, Y.size_id, Y.color_id, Y.inward_id
                    ) AS final
                    WHERE final.available_stock_quantity > 0
                    ORDER BY final.quality_id, final.style_id, final.size_id, final.color_id
                """
                params = [inward_ids, inward_ids]

            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

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

        # === Detect if all entries have same quality/style ===
        quality_ids = {row['quality_id'] for row in results}
        style_ids = {row['style_id'] for row in results}

        if len(quality_ids) != 1 or len(style_ids) != 1:
            return JsonResponse({
                'status': 'error',
                'message': 'Multiple Quality or Style values found for selected entries.',
                'data': results,
            })

        quality_id = next(iter(quality_ids))
        style_id = next(iter(style_ids))

        quality = quality_table.objects.filter(status=1, id=quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=style_id).values('id', 'name').first()

        # If fabric is same across entries
        fabric_ids = list(
            parent_stiching_inward_table.objects.filter(status=1, id__in=inward_ids)
            .values_list('fabric_id', flat=True)
            .distinct()
        )
        fabric = fabric_program_table.objects.filter(status=1, id=fabric_ids[0]).values('id').first() if len(fabric_ids) == 1 else None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'quality': quality or '',
            'style': style or '', 
            'fabric': fabric or '',
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




from production_app.models import child_packing_outward_table, child_stiching_inward_table, parent_stiching_inward_table



from django.db.models import Sum
from django.http import JsonResponse

def get_stiching_inward_edit_details(request):
    if request.method == "POST":
        # Get list of inward IDs from POST
        inward_id_list = request.POST.getlist("inward_id[]")
        tm_id = request.POST.get("tm_id")  # optional

        # Validate inward IDs (make sure they are integers)
        try:
            inward_ids = [int(pid) for pid in inward_id_list if pid.strip().isdigit()]
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid inward_id(s)'})

        if not inward_ids:
            return JsonResponse({'status': 'error', 'message': 'Entry ID(s) required'})

        # Fetch outward_data for all inward_ids (filtering by 'id' field here)
        outward_data = child_stiching_inward_table.objects.filter(
            status=1,
            id__in=inward_ids,
            quantity__gt=0
        )

        # Aggregate quantities grouped by size and color
        outward_group = outward_data.values('size_id', 'color_id').annotate(total_in_quantity=Sum('quantity'))

        # Prepare result map keyed by (size_id, color_id)
        result_map = {}
        for entry in outward_group:
            key = (entry['size_id'], entry['color_id'])
            result_map[key] = {
                'size_id': entry['size_id'],
                'color_id': entry['color_id'],
                'total_in_quantity': entry['total_in_quantity'] or 0,
                'total_out_quantity': 0,
                'already_received_quantity': 0,
                'available_stock_quantity': 0
            }

        # Total received quantities from packing outward table (filter by inward_id list)
        total_received = child_packing_outward_table.objects.filter(
            status=1,
            inward_id__in=inward_ids,
            quantity__gt=0
        ).values('size_id', 'color_id').annotate(total_received=Sum('quantity'))

        for entry in total_received:
            key = (entry['size_id'], entry['color_id'])
            if key not in result_map:
                result_map[key] = {
                    'size_id': entry['size_id'],
                    'color_id': entry['color_id'],
                    'total_in_quantity': 0,
                    'total_out_quantity': 0,
                    'already_received_quantity': 0,
                    'available_stock_quantity': 0
                }
            result_map[key]['total_out_quantity'] = entry['total_received'] or 0

        # Already received quantities for specific tm_id (optional)
        if tm_id:
            already_received = child_packing_outward_table.objects.filter(
                status=1,
                inward_id__in=inward_ids,
                tm_id=tm_id,
                quantity__gt=0
            ).values('size_id', 'color_id').annotate(received_by_tm=Sum('quantity'))

            for entry in already_received:
                key = (entry['size_id'], entry['color_id'])
                if key not in result_map:
                    result_map[key] = {
                        'size_id': entry['size_id'],
                        'color_id': entry['color_id'],
                        'total_in_quantity': 0,
                        'total_out_quantity': 0,
                        'already_received_quantity': 0,
                        'available_stock_quantity': 0
                    }
                result_map[key]['already_received_quantity'] = entry['received_by_tm'] or 0

        # Calculate available stock quantity
        for row in result_map.values():
            row['available_stock_quantity'] = row['total_in_quantity'] - row['total_out_quantity']

        results = list(result_map.values())

        # Fetch size and color names for display
        size_ids = {row['size_id'] for row in results}
        color_ids = {row['color_id'] for row in results}

        sizes_queryset = size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name')
        sizes = sorted(list(sizes_queryset), key=lambda x: int(x['name']))  # Sort by size name (integer)
        colors = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name')

        size_map = {s['id']: s['name'] for s in sizes}
        color_map = {c['id']: c['name'] for c in colors}

        # Add human-readable names to each result row
        for row in results:
            row['size_name'] = size_map.get(row['size_id'], '')
            row['color_name'] = color_map.get(row['color_id'], '')

        # Sort results by size name (numerically)
        results.sort(key=lambda x: int(x['size_name']) if x['size_name'].isdigit() else 0)

        # Fetch fabric, quality, style info from parent_stiching_inward_table for the first inward_id
        try:
            inward = parent_stiching_inward_table.objects.get(status=1, id=inward_ids[0])
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
        except parent_stiching_inward_table.DoesNotExist:
            fabric = quality = style = None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else ''
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




def get_stiching_inward_edit_details_bk_5(request):
    if request.method == "POST":
        # inward_id = request.POST.get("inward_id[]")
        tm_id = request.POST.get("tm_id")  # optional
        # print('inw-id:',inward_id, tm_id)

        # if not inward_id:
        #     return JsonResponse({'status': 'error', 'message': 'Entry ID is required'})

        # outward_data = child_stiching_inward_table.objects.filter(status=1, tm_id__in=inward_id, quantity__gt=0)
        # outward_group = outward_data.values('size_id', 'color_id').annotate(total_in_quantity=Sum('quantity'))

        # # Build result map: (size_id, color_id) => outward data
        # result_map = {}
        # for entry in outward_group: 
        #     key = (entry['size_id'], entry['color_id'])
        #     result_map[key] = {
        #         'size_id': entry['size_id'],
        #         'color_id': entry['color_id'],
        #         'inward_id': inward_id,
        #         'total_in_quantity': entry['total_in_quantity'] or 0,
        #         'total_out_quantity': 0,
        #         'already_received_quantity': 0,
        #         'available_stock_quantity': 0
        #     }

        # # Add total received (all tm_ids)
        # total_received = child_packing_outward_table.objects.filter(
        #     status=1, inward_id__in=inward_id, quantity__gt=0
        # ).values('size_id', 'color_id').annotate(total_received=Sum('quantity')).order_by('-size_id')

        # for entry in total_received:
        #     key = (entry['size_id'], entry['color_id'])
        #     if key not in result_map:
        #         result_map[key] = {
        #             'size_id': entry['size_id'],
        #             'color_id': entry['color_id'],
        #             'inward_id': inward_id,
        #             'total_in_quantity': 0,
        #             'total_out_quantity': 0,
        #             'already_received_quantity': 0,
        #             'available_stock_quantity': 0
        #         }
        #     result_map[key]['total_out_quantity'] = entry['total_received'] or 0

        # # Add already received (for provided tm_id)
        # if tm_id:
        #     already_received = child_packing_outward_table.objects.filter(
        #         status=1, inward_id=inward_id, tm_id=tm_id, quantity__gt=0
        #     ).values('size_id', 'color_id').annotate(received_by_tm=Sum('quantity')).order_by('-size_id')

        #     for entry in already_received:
        #         key = (entry['size_id'], entry['color_id'])
        #         if key not in result_map:
        #             result_map[key] = {
        #                 'size_id': entry['size_id'],
        #                 'color_id': entry['color_id'],
        #                 'inward_id': inward_id,
        #                 'total_in_quantity': 0,
        #                 'total_out_quantity': 0,
        #                 'already_received_quantity': 0,
        #                 'available_stock_quantity': 0
        #             }
        #         result_map[key]['already_received_quantity'] = entry['received_by_tm'] or 0

        # # Compute available_stock_quantity
        # for row in result_map.values():
        #     row['available_stock_quantity'] = row['total_in_quantity'] - row['total_out_quantity']

        # results = list(result_map.values())3
 
        inward_id = request.POST.getlist("inward_id[]")
        inward_ids = [int(pid) for pid in inward_id if pid.strip().isdigit()]
        print('inw-id:',inward_ids) 
        if not inward_ids:
            return JsonResponse({'status': 'error', 'message': 'Entry ID(s) required'})

        # Convert to integers (optional but recommended)
        try:
            inward_ids = list(map(int, inward_ids))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid inward_id(s)'})

        # Fetch outward_data for all inward_ids 
        outward_data = child_stiching_inward_table.objects.filter(status=1, inward_id=inward_ids, quantity__gt=0)

        outward_group = outward_data.values('size_id', 'color_id').annotate(total_in_quantity=Sum('quantity'))

        result_map = {}
        for entry in outward_group:
            key = (entry['size_id'], entry['color_id'])
            result_map[key] = {
                'size_id': entry['size_id'],
                'color_id': entry['color_id'],
                'total_in_quantity': entry['total_in_quantity'] or 0,
                'total_out_quantity': 0,
                'already_received_quantity': 0,
                'available_stock_quantity': 0
            } 

        # Total received (packing outward)
        total_received = child_packing_outward_table.objects.filter(
            status=1,
            inward_id=inward_ids,
            quantity__gt=0
        ).values('size_id', 'color_id').annotate(total_received=Sum('quantity'))

        for entry in total_received:
            key = (entry['size_id'], entry['color_id'])
            if key not in result_map:
                result_map[key] = {
                    'size_id': entry['size_id'],
                    'color_id': entry['color_id'],
                    'total_in_quantity': 0,
                    'total_out_quantity': 0,
                    'already_received_quantity': 0,
                    'available_stock_quantity': 0
                }
            result_map[key]['total_out_quantity'] = entry['total_received'] or 0

        # Already received for given tm_id (optional)
        if tm_id:
            already_received = child_packing_outward_table.objects.filter(
                status=1,
                inward_id=inward_ids,
                tm_id=tm_id,
                quantity__gt=0
            ).values('size_id', 'color_id').annotate(received_by_tm=Sum('quantity'))

            for entry in already_received:
                key = (entry['size_id'], entry['color_id'])
                if key not in result_map:
                    result_map[key] = {
                        'size_id': entry['size_id'],
                        'color_id': entry['color_id'],
                        'total_in_quantity': 0,
                        'total_out_quantity': 0,
                        'already_received_quantity': 0,
                        'available_stock_quantity': 0
                    }
                result_map[key]['already_received_quantity'] = entry['received_by_tm'] or 0

        # Compute available_stock_quantity
        for row in result_map.values():
            row['available_stock_quantity'] = row['total_in_quantity'] - row['total_out_quantity']

        results = list(result_map.values())


        # Fetch size/color names
        size_ids = {row['size_id'] for row in results}
        color_ids = {row['color_id'] for row in results}

        # sizes = size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name').order_by('id')
        # Assuming size_ids is a list of IDs you already have
        # Assuming size_ids is a list of IDs you already have
        sizes_queryset = size_table.objects.filter(status=1, id__in=size_ids).values('id', 'name')

        # Sort the list of dictionaries by the integer value of the 'name' field
        sizes = sorted(list(sizes_queryset), key=lambda x: int(x['name']))
        # Now, the 'sizes' list is correctly sorted: 75, 80, 85, 90, 95, 100        
        # The 'sizes' list is now correctly sorted
        colors = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name')

        size_map = {s['id']: s['name'] for s in sizes}
        color_map = {c['id']: c['name'] for c in colors}

        # for row in results:
        #     row['size_name'] = size_map.get(row['size_id'], '')
        #     print('sies:',row['size_name'])
        #     row['color_name'] = color_map.get(row['color_id'], '')


        # ... (rest of the code)

        for row in results:
            row['size_name'] = size_map.get(row['size_id'], '')
            row['color_name'] = color_map.get(row['color_id'], '')
        
        # Sort results numerically by the 'size_name'
        results.sort(key=lambda x: int(x['size_name']))

        # Print after sorting
        for row in results:
            print('sies:', row['size_name'])

        try:
            inward = parent_stiching_inward_table.objects.get(status=1, id=inward_id)
            fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
            quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
            style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
        except parent_stiching_inward_table.DoesNotExist:
            fabric = quality = style = None

        return JsonResponse({
            'status': 'success',
            'data': results,
            'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
            'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            'style': {'id': style['id'], 'name': style['name']} if style else ''
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
        # for row in results:
            # row['size_name'] = size_map.get(row['size_id'], '')
            # row['color_name'] = color_map.get(row['color_id'], '')


        # results.sort(key=lambda x: x['size_name'])


        # for row in results:
            # print('sies:', row['size_name'])

        # try:
            # inward = parent_stiching_inward_table.objects.get(status=1, id=inward_id)
            # fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
            # quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
            # style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
        # except parent_stiching_inward_table.DoesNotExist:
            # fabric = quality = style = None

        # return JsonResponse({
            # 'status': 'success',
            # 'data': results,
            # 'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
            # 'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
            # 'style': {'id': style['id'], 'name': style['name']} if style else ''
        # })

    # return JsonResponse({'status': 'error', 'message': 'Invalid request method'})











@csrf_exempt
def insert_packing_outward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            party_id = request.POST.get('party_id', 0)
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            # receive_no = request.POST.get('receive_no')
            # receive_date = request.POST.get('receive_date')
            program_date = request.POST.get('outward_date')
            cutting_data = json.loads(request.POST.get('chemical_data', '[]'))
            work_order_no = request.POST.get('work_order_no')
            # inward_id = request.POST.get('inward_id')
            inward_ids = request.POST.getlist('inward_id')
            inward_id = ','.join(inward_ids)  # Store in parent table


            fabric_id = request.POST.get('fabric_id')

            outward_no = generate_delivery_num_series()
 
            # Create Parent Entry
            material_request = parent_packing_outward_table.objects.create(
                outward_no=outward_no.upper(),
                outward_date=program_date,
                work_order_no=work_order_no,
                party_id=party_id,
                # receive_no=receive_no,
                # receive_date=receive_date,
                inward_id=inward_id,
                fabric_id = fabric_id,
                stiching_outward_id=0,
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
            for cutting in cutting_data:
                quantity = safe_decimal(cutting.get('quantity', 0))
                print('inw-id:',cutting.get('inward_id'))
                total_qty += quantity

                child_packing_outward_table.objects.create(
                    tm_id=material_request.id,
                    work_order_no=work_order_no,
                    quality_id=quality_id,
                    style_id=style_id,
                    inward_id=cutting.get('inward_id'),
                    stiching_outward_id = 0,
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

    return render(request, 'packing_delivery/add_packing_delivery.html') 



from django.db.models import Q

# @csrf_exempt
# def delete_packing_delivery(request):
#     if request.method == 'POST':
#         data_id = request.POST.get('id')
#         company_id = request.session.get('company_id')

#         try:
#             # Check if the delivery exists
#             delivery = parent_packing_outward_table.objects.filter(id=data_id, company_id=company_id, is_active=1).first()
#             if not delivery:
#                 return JsonResponse({'message': 'No such delivery record'})

#             # # Check for related packing entries (parent or child)
#             # has_packing_parent = parent_packing_inward_table.objects.filter(
#             #     stiching_outward_id=data_id, company_id=company_id, is_active=1
#             # ).exists()

#             # has_packing_child = child_packing_inward_table.objects.filter(
#             #     stiching_outward_id=data_id, company_id=company_id, is_active=1
#             # ).exists()

#             # if has_packing_parent or has_packing_child:
#             #     return JsonResponse({'message': 'Packing records exist. Cannot delete this delivery.'})

#             # No packing linked, proceed to soft delete
#             parent_packing_outward_table.objects.filter(id=data_id).update(status=0, is_active=0)
#             child_packing_outward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

#             return JsonResponse({'message': 'yes'})

#         except Exception as e:
#             return JsonResponse({'message': 'error', 'error_message': str(e)})

#     return JsonResponse({'message': 'Invalid request method'})



@csrf_exempt
def delete_packing_delivery(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        company_id = request.session.get('company_id')

        try:
            # Check if the delivery exists
            delivery = parent_packing_outward_table.objects.filter(
                id=data_id, company_id=company_id, is_active=1
            ).first()

            if not delivery:
                return JsonResponse({'message': 'No such delivery record'})

            # Soft delete
            parent_packing_outward_table.objects.filter(id=data_id).update(status=0, is_active=0)
            child_packing_outward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'Invalid request method'})
 


def edit_packing_delivery(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'packing_delivery/update_packing_delivery.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'packing_delivery/update_packing_delivery.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_packing_outward_table.objects.filter(tm_id=material_id).first()
   
        # Fetch the parent stock instance
        parent_stock_instance = parent_packing_outward_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'packing_delivery/update_packing_delivery.html', {'error_message': 'Parent stock not found.'})


        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_ironing=1,status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1).order_by('-id')
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
     

        # stitching = parent_stiching_outward_table.objects.filter(status=1)
        stitching = parent_stiching_inward_table.objects.filter(status=1)
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
            'stitching':stitching,
           
        }
        print('style-id:',parent_stock_instance.style_id)
        return render(request, 'packing_delivery/update_packing_delivery.html', context)

    except Exception as e:
        return render(request, 'packing_delivery/update_packing_delivery.html', {'error_message': 'An unexpected error occurred: ' + str(e)})





@csrf_exempt
def update_packing_delivery(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')

            master_id = request.POST.get('tm_id')
            outward_date = request.POST.get('outward_date')
            remarks = request.POST.get('remarks')
            work_order_no = request.POST.get('work_order_no')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            fabric_id = request.POST.get('fabric_id')
            inward_id = request.POST.get('inward_id')

            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            chemical_data = request.POST.get('chemical_data')
            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'})

            table_data = json.loads(chemical_data)
            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Step 1: Update master table entry
            material_request = parent_packing_outward_table.objects.filter(id=master_id).first()
            if not material_request:
                return JsonResponse({'success': False, 'error_message': 'Invalid master ID'})

            material_request.outward_date = outward_date
            material_request.remarks = remarks
            material_request.quality_id = quality_id
            material_request.fabric_id=fabric_id
            material_request.style_id = style_id
            material_request.updated_by = user_id 
            material_request.updated_on = timezone.now()

            # Step 2: Delete existing child entries
            child_packing_outward_table.objects.filter(tm_id=master_id).delete()

            total_qty = Decimal('0.000')

            # Step 3: Insert updated child entries
            for row in table_data:
                quantity = safe_decimal(row.get('quantity', 0))
                total_qty += quantity

                child_packing_outward_table.objects.create(
                    tm_id=material_request.id,

                    work_order_no=work_order_no,
                    quality_id=quality_id,
                    style_id=style_id,
                    inward_id=inward_id,
                    stiching_outward_id = 0, 
                    size_id=row.get('size_id'),
                    color_id=row.get('color_id'),
                    quantity=quantity, 
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,
                    updated_by=user_id,
                    updated_on=timezone.now()
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
def packing_delivery_print(request):
    po_id = request.GET.get('k') 

    print('ids:',po_id)
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('ord-id:',order_id)
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_packing_outward_table, id=order_id)
    print('quality',total_values.quality_id)

    party = get_object_or_404(party_table, id=total_values.party_id)
    party_name = party.name 
    gstin = party.gstin
    mobile = party.mobile

    prg_details = child_packing_outward_table.objects.filter(tm_id=order_id).values(
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
        'sizes': sizes,   
        'party_name':party_name,
        'gstin':gstin,
        'mobile':mobile,
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

    return render(request, 'packing_delivery/packing_delivery_print.html', context)



