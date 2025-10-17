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


def folding_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_ironing=1)
        fabric_program = fabric_program_table.objects.filter(status=1) 
        delivery = parent_packing_outward_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        return render(request,'folding_delivery/folding_delivery.html',{'party':party,'fabric_program':fabric_program,'delivery':delivery,'quality':quality,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    




from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection




# @csrf_exempt
# def get_st_folding_delivery_available_list(request):
    # if request.method == 'POST' and 'party_id' in request.POST:
        # party_id = request.POST['party_id']
        # print('party-:', party_id)


        # child_orders = stiching_folding_delivery_balance_table.objects.filter(
            # balance_quantity__gt=0
        # ).values_list('outward_id', flat=True).distinct()
        # print('orders:',child_orders)


        # filtered_orders = []
        # total_po_quantity = 0
        # total_inward_quantity = 0
        # total_balance_quantity = 0

        # for outward_id in child_orders:

            # stitching_totals = stiching_folding_delivery_balance_table.objects.filter(
                # outward_id=outward_id,
                # balance_quantity__gt=0,
            # ).aggregate(
                # total_po=Sum('po_quantity'),
                # total_in=Sum('in_quantity'),
                # total_balance=Sum('balance_quantity')
            # )


            # folding_totals = parent_folding_delivery_table.objects.filter(
                # stitching_outward_id=outward_id, 
                # status=1
            # ).aggregate(
                # total_folding=Sum('total_quantity')
            # )

            # stiching_wt = stitching_totals['total_balance'] or 0
            # folding_wt = folding_totals['total_folding'] or 0
            # available_wt = stiching_wt - folding_wt

            # print(f"Outward {outward_id} → Stitching: {stiching_wt}, Folding: {folding_wt}, Available: {available_wt}")

            # if available_wt > 0:

                # outward_data = parent_stiching_outward_table.objects.filter(
                    # id=outward_id,
                    # status=1
                # ).values('id', 'outward_no', 'work_order_no').first()

                # if outward_data:

                    # filtered_orders[outward_data['id']].append(outward_data)


                    # total_po_quantity += stitching_totals['total_po'] or 0
                    # total_inward_quantity += stitching_totals['total_in'] or 0
                    # total_balance_quantity += available_wt

        # return JsonResponse({
            # 'orders': filtered_orders,
            # 'po_quantity': float(total_po_quantity),
            # 'inward_quantity': float(total_inward_quantity),
            # 'balance_quantity': float(total_balance_quantity)
        # })

    # return JsonResponse({'orders': []})


@csrf_exempt
def get_st_folding_delivery_available_list_bk(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('party-:', party_id)

        child_orders = stiching_folding_delivery_balance_table.objects.filter(
            balance_quantity__gt=0
        ).values_list('outward_id', flat=True).distinct()
        print('orders:', child_orders)

        filtered_orders = []
        total_po_quantity = 0
        total_inward_quantity = 0
        total_balance_quantity = 0

        for outward_id in child_orders:
            stitching_totals = stiching_folding_delivery_balance_table.objects.filter(
                outward_id=outward_id,
                balance_quantity__gt=0,
            ).aggregate(
                total_po=Sum('po_quantity'),
                total_in=Sum('in_quantity'),
                total_balance=Sum('balance_quantity')
            )

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
                outward_data = parent_stiching_outward_table.objects.filter(
                    id=outward_id,
                    status=1
                ).values('id', 'outward_no', 'work_order_no').first()

                if outward_data:
                    filtered_orders.append(outward_data)  # <-- FIX HERE

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



@csrf_exempt
def get_st_folding_delivery_available_list(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('party-:', party_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                WITH cutting_data AS (
                    SELECT
                        tm.id AS entry_id,
                        tm.outward_no AS outward_no,
                        tm.work_order_no AS work_order_no,
                        tm.quality_id,
                        tm.style_id,
                        tx.color_id,
                        qt.name AS quality_name,
                        st.name AS style_name,
                        cr.name AS color_name,
                        SUM(tx.quantity) AS cutting_wt
                    FROM tx_stiching_outward tx
                    LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id and tm.party_id=%s
                    LEFT JOIN color cr ON tx.color_id = cr.id
                    LEFT JOIN quality qt ON tm.quality_id = qt.id
                    LEFT JOIN style st ON tm.style_id = st.id
                    WHERE tx.status = 1 AND tx.is_active = 1
                    GROUP BY tm.id, tm.outward_no, tm.work_order_no, tm.quality_id, tm.style_id,
                             tx.color_id, qt.name, st.name, cr.name
                ),
                delivery_data AS (
                    SELECT
                        fo.stitching_outward_id AS entry_id,
                        fo.quality_id,
                        fo.style_id,
                        fo.color_id,
                        SUM(fo.wt) AS delivered_wt
                    FROM tx_folding_outward fo
                    WHERE fo.status = 1
                    GROUP BY fo.stitching_outward_id, fo.quality_id, fo.style_id, fo.color_id
                ),
                size_data AS (
                    SELECT
                        tm.id AS entry_id,
                        tx.quality_id,
                        tx.style_id,
                        tx.color_id,
                        sz.name AS size_name,
                        SUM(tx.quantity) AS base_quantity,
                        CASE sz.name
                            WHEN '75' THEN prg.size_1
                            WHEN '80' THEN prg.size_2
                            WHEN '85' THEN prg.size_3
                            WHEN '90' THEN prg.size_4
                            WHEN '95' THEN prg.size_5
                            WHEN '100' THEN prg.size_6
                            WHEN '105' THEN prg.size_7
                            WHEN '110' THEN prg.size_8
                            ELSE 0
                        END AS folding_multiplier,
                        ROUND(SUM(tx.quantity) / 12, 3) AS dozen_qty,
                        ROUND(
                            (1.0 * SUM(tx.quantity) / 12) *
                            CASE sz.name
                                WHEN '75' THEN prg.size_1
                                WHEN '80' THEN prg.size_2
                                WHEN '85' THEN prg.size_3
                                WHEN '90' THEN prg.size_4
                                WHEN '95' THEN prg.size_5
                                WHEN '100' THEN prg.size_6
                                WHEN '105' THEN prg.size_7
                                WHEN '110' THEN prg.size_8
                                ELSE 0
                            END, 3
                        ) AS final_quantity
                    FROM tx_stiching_outward tx
                    LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
                    LEFT JOIN size sz ON tx.size_id = sz.id
                    LEFT JOIN tm_folding_program prg ON prg.quality_id = tx.quality_id AND prg.style_id = tx.style_id
                    WHERE tx.status = 1 AND tx.is_active = 1 AND prg.status = 1
                    GROUP BY tm.id, tx.quality_id, tx.style_id, tx.color_id, sz.name,
                             prg.size_1, prg.size_2, prg.size_3, prg.size_4,
                             prg.size_5, prg.size_6, prg.size_7, prg.size_8
                ),
                color_summary AS (
                    SELECT 
                        sd.entry_id,
                        sd.quality_id,
                        sd.style_id,
                        sd.color_id,
                        SUM(sd.base_quantity) AS base_qty,
                        SUM(sd.dozen_qty) AS dozen_qty,
                        SUM(sd.final_quantity) AS final_qty
                    FROM size_data sd
                    GROUP BY sd.entry_id, sd.quality_id, sd.style_id, sd.color_id
                )
                SELECT
                    c.entry_id,
                    MIN(c.outward_no) AS outward_no,
                    MIN(c.work_order_no) AS work_order_no,
                    MIN(c.quality_id) AS quality_id,
                    MIN(c.style_id) AS style_id,
                    SUM(cs.final_qty) AS total_final_qty,
                    SUM(COALESCE(d.delivered_wt, 0)) AS total_delivered_wt,
                    ROUND(SUM(cs.final_qty) - SUM(COALESCE(d.delivered_wt, 0)), 3) AS total_available_balance
                FROM cutting_data c
                LEFT JOIN delivery_data d
                    ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id
                    AND d.style_id = c.style_id AND d.color_id = c.color_id
                LEFT JOIN color_summary cs
                    ON cs.entry_id = c.entry_id AND cs.quality_id = c.quality_id
                    AND cs.style_id = c.style_id AND cs.color_id = c.color_id
                GROUP BY c.entry_id
                HAVING ROUND(SUM(cs.final_qty) - SUM(COALESCE(d.delivered_wt, 0)), 3) > 0
                ORDER BY c.entry_id;

              
            """, [party_id])
  # SELECT
                    # c.entry_id,
                    # c.outward_no,
                    # c.work_order_no,
                    # c.quality_id,
                    # c.style_id,
                    # c.color_id,
                    # c.quality_name,
                    # c.style_name,
                    # c.color_name,
                    # cs.final_qty,
                    # COALESCE(d.delivered_wt, 0) AS delivered_wt,
                    # ROUND(cs.final_qty - COALESCE(d.delivered_wt, 0), 3) AS available_balance
                # FROM cutting_data c
                # LEFT JOIN delivery_data d
                    # ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id
                    # AND d.style_id = c.style_id AND d.color_id = c.color_id
                # LEFT JOIN color_summary cs
                    # ON cs.entry_id = c.entry_id AND cs.quality_id = c.quality_id
                    # AND cs.style_id = c.style_id AND cs.color_id = c.color_id
                # WHERE ROUND(cs.final_qty - COALESCE(d.delivered_wt, 0), 3) > 0
                # ORDER BY c.entry_id;
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            available_list = [dict(zip(columns, row)) for row in results]

        return JsonResponse({
            'status': 'success',
            'orders': available_list
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@csrf_exempt
def get_st_folding_delivery_available_list_bk_28(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('party-:', party_id)

        # Get all outward IDs with some remaining stitching balance
        child_orders = stiching_folding_delivery_balance_table.objects.filter(
            balance_quantity__gt=0
        ).values_list('outward_id', flat=True).distinct()
        print('orders:',child_orders)

        # Now iterate through each outward and compute available weight
        filtered_orders = []
        total_po_quantity = 0
        total_inward_quantity = 0
        total_balance_quantity = 0

        for outward_id in child_orders:
            # Total stitching weight for this outward 
            stitching_totals = stiching_folding_delivery_balance_table.objects.filter(
                outward_id=outward_id,
                balance_quantity__gt=0,
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


def generate_folding_delivery_num_series():
    last_purchase = parent_folding_delivery_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.outward_no:
        match = re.search(r'DO-(\d+)', last_purchase.outward_no)
        if match:
            next_num = int(match.group(1)) + 1
        else: 
            next_num = 1
    else: 
        next_num = 1
 
    return f"DO-{next_num:03d}"




def folding_delivery_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1, is_stiching=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 
        folding_no = generate_folding_delivery_num_series()

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)

        child_orders = packing_deivery_balance_table.objects.filter(
            balance_quantity__gt=0
        ).values_list('outward_id', flat=True)
        print('child_orders:',child_orders)

        orders = list(parent_packing_outward_table.objects.filter(
            id__in=child_orders,
            status=1
        ).values('id', 'outward_no', 'work_order_no','total_quantity').order_by('-id'))
        # ✅ Correct placement — aggregate totals outside the loop
        totals = packing_deivery_balance_table.objects.filter(
            balance_quantity__gt=0
        ).aggregate(
            po_quantity=Sum('po_quantity'),
            inward_quantity=Sum('in_quantity'),
            balance_quantity=Sum('balance_quantity')
        ) 
        stitching = parent_stiching_outward_table.objects.filter(status=1)

        return render(request, 'folding_delivery/add_folding_delivery.html', {
            'party': party,
            'fabric_program': fabric_program,
            'folding_no': folding_no,
            'color': color,
            'orders': orders,
            'balance_quantity': float(totals['balance_quantity'] or 0),
            'po_quantity': float(totals['po_quantity'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0),
            'quality': quality,
            'stitching':stitching,
            'style': style,
            'size': size
        })
    else:
        return HttpResponseRedirect("/admin")





def folding_delivery_report(request):   
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

    if outward: 
        query &= Q(outward_id=outward)
 
    if style:
            query &= Q(style_id=style)

    # Apply filters
    queryset = parent_folding_delivery_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())
 
    formatted = [
        {
            'action': '<button type="button" onclick="folding_delivery_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="folding_delivery_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="folding_delivery_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'outward_date': item['outward_date'] if item['outward_date'] else'-', 
            'outward_no': item['outward_no'] if item['outward_no'] else'-', 
            'work_order_no': item['work_order_no'] if item['work_order_no'] else'-', 
            'outward_id':getStichingDeliveryNoById(parent_stiching_outward_table, item['stitching_outward_id'] ), 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'party':getSupplier(party_table, item['party_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
  




# @csrf_exempt
# def folding_delivery_print(request):
#     po_id = request.GET.get('k') 
#     if not po_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     try:
#         order_id = int(base64.b64decode(po_id))
#         print('ord-id:',order_id)
#     except Exception:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)


#     total_values = get_object_or_404(parent_folding_delivery_table, id=order_id)
#     party = total_values.party_id
#     print('p-id:',party)
#     print('quality',total_values.quality_id)

#     party = get_object_or_404(party_table, id=total_values.party_id)
#     party_name = party.name
#     gstin = party.gstin
#     mobile = party.mobile

#     prg_details = child_folding_delivery_table.objects.filter(tm_id=order_id).values(
#         'id', 'wt','color_id'
#     )
   

#     combined_details = []
#     total_quantity = 0 
 
#     for prg_detail in prg_details:
#         product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
#         fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
#         quality = get_object_or_404(quality_table, id=total_values.quality_id)
#         style = get_object_or_404(style_table, id=total_values.style_id)



#         # size = get_object_or_404(size_table, id=prg_detail['size_id'])
#         color = get_object_or_404(color_table, id=prg_detail['color_id'])

     
#         wt = prg_detail['wt']
        

#         total_quantity += wt

#         combined_details.append({
#             'fabric': fabric_obj.name,
#             'style': style.name,
#             'quality': quality.name,
#             'color': color.name,
#             # 'size': size.name,
#             'wt': wt,
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
#             'wt': item['wt'],
#         }

    

#     for val in group_map.values():
#     # Prebuild size_data_list to avoid dynamic dict access in template
#         val['size_data_list'] = [
#             val['size_data'].get(size, {'wt': ''}) for size in sizes
#         ]

#         # Compute row total
#         val['row_total'] = sum(entry['wt'] for entry in val['size_data_list'] if entry['wt'])

#         grouped_data.append(val)
#         grand_total = sum(val['row_total'] for val in grouped_data) 
 
 
#     # # size-wise total (dict) and list (for template)
#     # size_totals = {size: {'wt': 0} for size in sizes}
#     # for item in combined_details:
#     #     size_totals[item['size']]['wt'] += item['wt']

#     # size_totals_list = [size_totals[size] for size in sizes]
#     # total_columns = 2 + len(sizes) * 2

#     context = {

#         'total_values': total_values, 
#         'party_name':party_name,
#         'gstin':gstin,
#         'mobile':mobile,
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
#         # 'size': size.name,
#         'grand_total':grand_total, 
 
#     }

#     return render(request, 'stiching_outward/stiching_delivery_print.html', context)





@csrf_exempt
def folding_delivery_print(request):
    po_id = request.GET.get('k') 
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('ord-id:', order_id)
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_folding_delivery_table, id=order_id)
    party = get_object_or_404(party_table, id=total_values.party_id)

    party_name = party.name
    gstin = party.gstin
    mobile = party.mobile 

    prg_details = child_folding_delivery_table.objects.filter(tm_id=order_id).values(
        'id', 'wt', 'color_id'
    )

    combined_details = []
    total_quantity = 0 

    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        quality = get_object_or_404(quality_table, id=total_values.quality_id)
        style = get_object_or_404(style_table, id=total_values.style_id)
        color = get_object_or_404(color_table, id=prg_detail['color_id'])

        wt = prg_detail['wt']
        total_quantity += wt

        combined_details.append({
            'fabric': fabric_obj.name,
            'style': style.name,
            'quality': quality.name,
            'color': color.name,
            'wt': wt,
        })

    # Group by fabric + color
    group_map = defaultdict(lambda: {'wt_list': []})
    grouped_data = []

    for item in combined_details:
        key = (item['fabric'], item['color'])
        group_map[key]['fabric'] = item['fabric']
        group_map[key]['color'] = item['color']
        group_map[key]['wt_list'].append(item['wt'])

    grand_total = 0
    for val in group_map.values():
        val['row_total'] = sum(val['wt_list'])
        grouped_data.append(val)
        grand_total += val['row_total']

    context = {
        'total_values': total_values, 
        'party_name': party_name,
        'gstin': gstin,
        'mobile': mobile,
        'grouped_data': grouped_data,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png', 
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
        'color': color.name,
        'grand_total': grand_total, 
    }

    return render(request, 'folding_delivery/folding_delivery_print.html', context)

def folding_delivery_edit(request):
    try:  
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'folding_delivery/update_folding_delivery.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID


        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'folding_delivery/update_folding_delivery.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_folding_delivery_table.objects.filter(tm_id=material_id).first()
   
        # Fetch the parent stock instance
        parent_stock_instance = parent_folding_delivery_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'folding_delivery/update_folding_delivery.html', {'error_message': 'Parent stock not found.'})

        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_stiching=1,status=1)
        
        quality = quality_table.objects.filter(status=1) 
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
     
        fabric = fabric_program_table.objects.filter(status=1)
        stitching = parent_stiching_outward_table.objects.filter(status=1)
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
            'fabric':fabric,
            'stitching':stitching,
           
        }
        print('style-id:',parent_stock_instance.style_id)
        return render(request, 'folding_delivery/update_folding_delivery.html', context)

    except Exception as e:
        return render(request, 'folding_delivery/update_folding_delivery.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete_folding_delivery(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try:
            updated_master = parent_folding_delivery_table.objects.filter(id=data_id).update(status=0, is_active=0)
            updated_children = child_folding_delivery_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            if updated_master == 0:
                return JsonResponse({'message': 'No such master record'}, status=404)

            return JsonResponse({'message': 'yes'})
        except Exception as e:
            return JsonResponse({'message': 'Error occurred', 'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)





@csrf_exempt
def get_entry_details(request):
    entry_id = request.POST.get('entry_id')
    entry = cutting_entry_table.objects.filter(id=entry_id).first()
    print('entry:',entry)
    if not entry:
        return JsonResponse({'error': 'Invalid entry ID'}, status=404)
    tx_entries = sub_cutting_entry_table.objects.filter(tm_id=entry.id)



    lot_numbers = list(set(tx_entries.values_list('lot_no', flat=True)))
    default_fabric = entry.fabric_id  #entry.values_list('fabric_id', flat=True).first()


    return JsonResponse({
        'lot_numbers': lot_numbers,
        'default_fabric': default_fabric,
        'work_order_no': entry.work_order_no
    })




@csrf_exempt
def get_st_delivery_details(request):
    entry_id = request.POST.get('entry_id')
    entry = parent_stiching_outward_table.objects.filter(id=entry_id).first()
    print('entry:',entry)
    if not entry:
        return JsonResponse({'error': 'Invalid entry ID'}, status=404)
    tx_entries = child_stiching_outward_table.objects.filter(tm_id=entry.id)

    lot_numbers = list(set(tx_entries.values_list('work_order_no', flat=True)))
    default_fabric = entry.fabric_id  #entry.values_list('fabric_id', flat=True).first()

    # lot_numbers = list(set(entry.tx_cutting_entry_set.values_list('lot_no', flat=True)))
    # default_fabric = entry.tx_cutting_entry_set.values_list('fabric_id', flat=True).first()

    return JsonResponse({
        'lot_numbers': lot_numbers,
        'default_fabric': default_fabric,
        'work_order_no': entry.work_order_no
    })

 


from django.db import connection
from django.template.loader import render_to_string
from django.http import HttpResponse

 
@csrf_exempt
def get_cutting_entry_list(request):
    if request.method == 'POST':
        party_id = request.POST.get('party_id')

        # Get entry_ids that are already used in folding delivery
        used_entry_ids = parent_folding_delivery_table.objects.values_list('cutting_entry_id', flat=True)

        # Filter cutting entries for this party and exclude the used ones
        cutting_entries = cutting_entry_table.objects.filter( 
            # party_id=party_id
            status=1
        ).exclude(id__in=used_entry_ids)

        data = {
            'orders': [
                { 
                    'id': entry.id,
                    'cutting_no': entry.cutting_no,
                    'work_order_no': entry.work_order_no
                }
                for entry in cutting_entries
            ]
        }

        return JsonResponse(data)





def get_cutting_entry_folding_details(request):
    """
    Retrieves cutting entry and folding details.
    """
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    # Fetch current page delivered wt for the given tm_id
    current_page_deliverwt = 0
    if tm_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ROUND(SUM(wt), 2)
                FROM tx_folding_outward
                WHERE tm_id = %s AND status = 1
            """, [tm_id])
            result = cursor.fetchone()
            if result and result[0]:
                current_page_deliverwt = result[0]

    with connection.cursor() as cursor: 
        cursor.execute("""
            WITH cutting_data AS (
                SELECT
                    tm.id AS entry_id,
                    tm.quality_id,
                    tm.style_id,
                    tx.color_id,
                    qt.name AS quality_name,
                    st.name AS style_name,
                    cr.name AS color_name,
                    SUM(tx.wt) AS cutting_wt
                FROM tx_cutting_entry tx
                LEFT JOIN tm_cutting_entry tm ON tx.tm_id = tm.id
                LEFT JOIN color cr ON tx.color_id = cr.id
                LEFT JOIN quality qt ON tm.quality_id = qt.id
                LEFT JOIN style st ON tm.style_id = st.id
                WHERE
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                GROUP BY
                    tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
            ),
            delivery_data AS (
                SELECT
                    fo.entry_id,
                    fo.quality_id,
                    fo.style_id,
                    fo.color_id,
                    SUM(fo.wt) AS delivered_wt
                FROM tx_folding_outward fo
                WHERE
                    fo.entry_id = %s AND fo.status = 1
                GROUP BY
                    fo.entry_id, fo.quality_id, fo.style_id, fo.color_id
            )
            SELECT
                c.entry_id,
                c.quality_id,
                c.quality_name,
                c.style_id,
                c.style_name,
                c.color_id,
                c.color_name,
                c.cutting_wt,
                ROUND(COALESCE(d.delivered_wt, 0), 2) AS delivered_wt,
                ROUND(
                    c.cutting_wt - COALESCE(d.delivered_wt, 0),
                    2
                ) AS balance_wt
            FROM cutting_data c
            LEFT JOIN delivery_data d ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id AND d.style_id = c.style_id AND d.color_id = c.color_id
           -- WHERE
          --     c.cutting_wt - COALESCE(d.delivered_wt, 0) > 0;
        """, [entry_id, entry_id])

        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        rows = [dict(zip(columns, row)) for row in results]
        print('folding-prg-data:', rows)

    # Fetch related master data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        quality = None
        style = None
        fabric = None

    return JsonResponse({
        'status': 'success',
        'data': rows,
        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
        'current_page_deliverwt': current_page_deliverwt
    })



 
 
 
def get_st_delivery_folding_details(request):
    """
    Retrieves cutting entry and folding details.
    """
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    # Fetch current page delivered wt for the given tm_id
    current_page_deliverwt = 0
    if tm_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ROUND(SUM(wt), 2)
                FROM tx_folding_outward
                WHERE tm_id = %s AND status = 1
            """, [tm_id])
            result = cursor.fetchone()
            if result and result[0]:
                current_page_deliverwt = result[0]

    with connection.cursor() as cursor: 
        cursor.execute("""
            # 
                       
            WITH cutting_data AS (
                SELECT
                    tm.id AS entry_id,
                    tm.quality_id,
                    tm.style_id,
                    tx.color_id,
                    qt.name AS quality_name,
                    st.name AS style_name,
                    cr.name AS color_name,
                    SUM(tx.quantity) AS cutting_wt
                FROM tx_stiching_outward tx
                LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
                LEFT JOIN color cr ON tx.color_id = cr.id
                LEFT JOIN quality qt ON tm.quality_id = qt.id
                LEFT JOIN style st ON tm.style_id = st.id
                WHERE
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                GROUP BY
                    tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
            ),

            delivery_data AS ( 
                SELECT
                    fo.stitching_outward_id AS entry_id,
                    fo.quality_id,
                    fo.style_id,
                    fo.color_id,
                    SUM(fo.wt) AS delivered_wt,
                    SUM(CASE WHEN fo.tm_id = 1 THEN fo.wt ELSE 0 END) AS delivered_wt_excluding_tm_id
                FROM tx_folding_outward fo
                WHERE
                    fo.stitching_outward_id = %s AND fo.status = 1
                GROUP BY
                    fo.stitching_outward_id, fo.quality_id, fo.style_id, fo.color_id
            ),

            size_data AS (
                SELECT
                    tm.id AS entry_id,
                    tx.quality_id,
                    tx.style_id,
                    tx.color_id,
                    sz.name AS size_name,
                    SUM(tx.quantity) AS base_quantity,

                    -- Folding multiplier based on size
                    CASE sz.name
                        WHEN '75' THEN prg.size_1
                        WHEN '80' THEN prg.size_2
                        WHEN '85' THEN prg.size_3
                        WHEN '90' THEN prg.size_4
                        WHEN '95' THEN prg.size_5
                        WHEN '100' THEN prg.size_6
                        WHEN '105' THEN prg.size_7
                        WHEN '110' THEN prg.size_8
                        ELSE 0
                    END AS folding_multiplier,

                    -- Accurate dozen and final quantity (no FLOOR, decimals retained)
                    ROUND(SUM(tx.quantity) / 12, 3) AS dozen_qty,

                    ROUND(
                        (1.0 * SUM(tx.quantity) / 12) * 
                        CASE sz.name
                            WHEN '75' THEN prg.size_1
                            WHEN '80' THEN prg.size_2
                            WHEN '85' THEN prg.size_3
                            WHEN '90' THEN prg.size_4
                            WHEN '95' THEN prg.size_5
                            WHEN '100' THEN prg.size_6
                            WHEN '105' THEN prg.size_7
                            WHEN '110' THEN prg.size_8
                            ELSE 0
                        END, 3
                    ) AS final_quantity

                FROM tx_stiching_outward tx
                LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
                LEFT JOIN size sz ON tx.size_id = sz.id
                LEFT JOIN tm_folding_program prg ON prg.quality_id = tx.quality_id AND prg.style_id = tx.style_id
                WHERE
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                    AND prg.status = 1
                GROUP BY
                    tm.id, tx.quality_id, tx.style_id, tx.color_id, sz.name,
                    prg.size_1, prg.size_2, prg.size_3, prg.size_4,
                    prg.size_5, prg.size_6, prg.size_7, prg.size_8
            ),

            color_summary AS (
                SELECT
                    sd.entry_id,
                    sd.quality_id,
                    sd.style_id,
                    sd.color_id,
                    SUM(sd.base_quantity) AS base_qty,
                    SUM(sd.dozen_qty) AS dozen_qty,
                    SUM(sd.final_quantity) AS final_qty
                FROM size_data sd
                GROUP BY sd.entry_id, sd.quality_id, sd.style_id, sd.color_id
            )

            SELECT
                c.entry_id,
                c.quality_id,
                c.quality_name, 
                c.style_id,
                c.style_name,
                c.color_id,
                c.color_name,  
                c.cutting_wt,
                ROUND(COALESCE(d.delivered_wt, 0), 3) AS delivered_wt,
                ROUND(COALESCE(d.delivered_wt_excluding_tm_id, 0), 3) AS already_rec_wt,
                ROUND(c.cutting_wt - COALESCE(d.delivered_wt, 0), 3) AS balance_wt,

                cs.base_qty,
                cs.dozen_qty,
                cs.final_qty,
                ROUND(cs.final_qty - COALESCE(d.delivered_wt, 0), 3) AS available_balance

            FROM cutting_data c
            LEFT JOIN delivery_data d ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id AND d.style_id = c.style_id AND d.color_id = c.color_id
            LEFT JOIN color_summary cs ON cs.entry_id = c.entry_id AND cs.quality_id = c.quality_id AND cs.style_id = c.style_id AND cs.color_id = c.color_id
            ORDER BY c.entry_id, c.color_id;

        

        #    
        """, [entry_id, entry_id,entry_id])

        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        # rows = [dict(zip(columns, row)) for row in results]
        rows = [dict(zip(columns, row)) for row in results if row[columns.index('available_balance')] > 0]

        print('folding-prg-data:', rows)

    # Fetch related master data
    try:
        inward = parent_stiching_outward_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
    except parent_stiching_outward_table.DoesNotExist:
        quality = None
        style = None
        fabric = None
 
    return JsonResponse({
        'status': 'success',
        'data': rows,
        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
        'current_page_deliverwt': current_page_deliverwt
    })



 
def get_st_delivery_folding_details_bk_26(request):
    """
    Retrieves cutting entry and folding details.
    """
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    # Fetch current page delivered wt for the given tm_id
    current_page_deliverwt = 0
    if tm_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ROUND(SUM(wt), 2)
                FROM tx_folding_outward
                WHERE tm_id = %s AND status = 1
            """, [tm_id])
            result = cursor.fetchone()
            if result and result[0]:
                current_page_deliverwt = result[0]

    with connection.cursor() as cursor: 
        cursor.execute("""
            WITH cutting_data AS (
                SELECT
                    tm.id AS entry_id,
                    tm.quality_id,
                    tm.style_id,
                    tx.color_id,
                    qt.name AS quality_name,
                    st.name AS style_name,
                    cr.name AS color_name,

                    SUM(tx.quantity) AS cutting_wt
                FROM tx_stiching_outward tx
                LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
                LEFT JOIN color cr ON tx.color_id = cr.id
                LEFT JOIN quality qt ON tm.quality_id = qt.id
                LEFT JOIN style st ON tm.style_id = st.id
                WHERE
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                GROUP BY
                    tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
            ),
            delivery_data AS (
                SELECT
                    fo.stitching_outward_id AS entry_id,
                    fo.quality_id,
                    fo.style_id,
                    fo.color_id,
                    SUM(fo.wt) AS delivered_wt
                FROM tx_folding_outward fo
                WHERE
                    fo.stitching_outward_id = %s AND fo.status = 1
                GROUP BY
                    fo.stitching_outward_id, fo.quality_id, fo.style_id, fo.color_id
            )
            SELECT
                c.entry_id,
                c.quality_id,
                c.quality_name,
                c.style_id,
                c.style_name,
                c.color_id,
                c.color_name,
                c.cutting_wt,
                ROUND(COALESCE(d.delivered_wt, 0), 2) AS delivered_wt,
                ROUND(
                    c.cutting_wt - COALESCE(d.delivered_wt, 0),
                    2
                ) AS balance_wt
            FROM cutting_data c
            LEFT JOIN delivery_data d ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id AND d.style_id = c.style_id AND d.color_id = c.color_id
           -- WHERE
          --     c.cutting_wt - COALESCE(d.delivered_wt, 0) > 0;
                       

        #    
        """, [entry_id, entry_id])

        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        rows = [dict(zip(columns, row)) for row in results]
        print('folding-prg-data:', rows)

    # Fetch related master data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        quality = None
        style = None
        fabric = None

    return JsonResponse({
        'status': 'success',
        'data': rows,
        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
        'current_page_deliverwt': current_page_deliverwt
    })





from django.db import connection
from django.http import JsonResponse


def get_cutting_entry_folding_details_update(request):
    """
    Retrieves cutting entry and folding details.
    """
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')

    # The existing query for current_page_deliverwt is correct and does not need changes.
    current_page_deliverwt = 0
    if tm_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ROUND(SUM(wt), 2)
                FROM tx_folding_outward
                WHERE tm_id = %s AND status = 1
            """, [tm_id])
            result = cursor.fetchone()
            if result and result[0]:
                current_page_deliverwt = result[0]

    with connection.cursor() as cursor:
        cursor.execute("""
            WITH cutting_data AS (
                SELECT
                    tm.id AS entry_id,
                    tm.quality_id,
                    tm.style_id,
                    tx.color_id,
                    qt.name AS quality_name,
                    st.name AS style_name,
                    cr.name AS color_name,
                    SUM(tx.wt) AS cutting_wt
                FROM tx_cutting_entry tx
                LEFT JOIN tm_cutting_entry tm ON tx.tm_id = tm.id
                LEFT JOIN color cr ON tx.color_id = cr.id
                LEFT JOIN quality qt ON tm.quality_id = qt.id
                LEFT JOIN style st ON tm.style_id = st.id
                WHERE
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                GROUP BY
                    tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
            ),
            delivery_data AS (
                SELECT
                    fo.entry_id,
                    fo.quality_id,
                    fo.style_id,
                    fo.color_id,
                    SUM(fo.wt) AS delivered_wt,
                    SUM(CASE WHEN fo.tm_id != %s THEN fo.wt ELSE 0 END) AS delivered_wt_excluding_tm_id
                FROM tx_folding_outward fo
                WHERE
                    fo.entry_id = %s AND fo.status = 1
                GROUP BY
                    fo.entry_id, fo.quality_id, fo.style_id, fo.color_id
            )
            SELECT
                c.entry_id,
                c.quality_id,
                c.quality_name,
                c.style_id,
                c.style_name,
                c.color_id,
                c.color_name,
                c.cutting_wt,
                ROUND(COALESCE(d.delivered_wt, 0), 2) AS delivered_wt,
                ROUND(COALESCE(d.delivered_wt_excluding_tm_id, 0), 2) AS already_rec_wt,
                ROUND(
                    c.cutting_wt - COALESCE(d.delivered_wt, 0),
                    2
                ) AS balance_wt
            FROM cutting_data c
            LEFT JOIN delivery_data d ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id AND d.style_id = c.style_id AND d.color_id = c.color_id;
        """, [entry_id, tm_id, entry_id]) # Corrected parameters

        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        rows = [dict(zip(columns, row)) for row in results]
        print('folding-prg-data:', rows)

    # Fetch related master data
    try:
        inward = cutting_entry_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
    except cutting_entry_table.DoesNotExist:
        quality = None
        style = None
        fabric = None

    return JsonResponse({
        'status': 'success',
        'data': rows,
        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
        'current_page_deliverwt': current_page_deliverwt
    })



# WITH cutting_data AS (
#                 SELECT
#                     tm.id                     AS entry_id,
#                     tm.quality_id,
#                     tm.style_id,
#                     tx.color_id,
#                     qt.name                  AS quality_name,
#                     st.name                  AS style_name,
#                     cr.name                  AS color_name,
#                     SUM(tx.quantity)         AS cutting_wt
#                 FROM tx_stiching_outward tx
#                 JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
#                 JOIN color cr ON tx.color_id = cr.id
#                 JOIN quality qt ON tm.quality_id = qt.id
#                 JOIN style st ON tm.style_id = st.id
#                 WHERE tx.status = 1 AND tx.is_active = 1 AND tx.tm_id = %s
#                 GROUP BY tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
#             ),
#             delivery_data AS (
#                 SELECT
#                     fo.stitching_outward_id  AS entry_id,
#                     fo.quality_id,
#                     fo.style_id,
#                     fo.color_id,
#                     SUM(fo.wt)               AS delivered_wt
#                 FROM tx_folding_outward fo
#                 WHERE fo.stitching_outward_id = %s AND fo.status = 1
#                 GROUP BY fo.stitching_outward_id, fo.quality_id, fo.style_id, fo.color_id
#             ),
#             size_data AS (
#                 SELECT
#                     tm.id                     AS entry_id,
#                     tx.quality_id,
#                     tx.style_id,
#                     tx.color_id,
#                     sz.name                  AS size_name,
#                     SUM(tx.quantity)         AS base_quantity,
#                     CASE sz.name
#                         WHEN '75' THEN prg.size_1 WHEN '80' THEN prg.size_2
#                         WHEN '85' THEN prg.size_3 WHEN '90' THEN prg.size_4
#                         WHEN '95' THEN prg.size_5 WHEN '100' THEN prg.size_6
#                         WHEN '105' THEN prg.size_7 WHEN '110' THEN prg.size_8
#                         ELSE 0
#                     END                      AS folding_multiplier,
#                     FLOOR(SUM(tx.quantity)/12) AS dozen_qty,
#                     (FLOOR(SUM(tx.quantity)/12) *
#                     CASE sz.name
#                         WHEN '75' THEN prg.size_1 WHEN '80' THEN prg.size_2
#                         WHEN '85' THEN prg.size_3 WHEN '90' THEN prg.size_4
#                         WHEN '95' THEN prg.size_5 WHEN '100' THEN prg.size_6
#                         WHEN '105' THEN prg.size_7 WHEN '110' THEN prg.size_8
#                         ELSE 0
#                     END)                      AS final_quantity
#                 FROM tx_stiching_outward tx
#                 JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
#                 JOIN size sz ON tx.size_id = sz.id
#                 JOIN tm_folding_program prg
#                     ON prg.quality_id = tx.quality_id AND prg.style_id = tx.style_id
#                 WHERE tx.status = 1 AND tx.is_active = 1 AND tx.tm_id = %s AND prg.status = 1
#                 GROUP BY tm.id, tx.quality_id, tx.style_id, tx.color_id,
#                          sz.name, prg.size_1, prg.size_2, prg.size_3, prg.size_4,
#                          prg.size_5, prg.size_6, prg.size_7, prg.size_8
#             ),
#             color_summary AS (
#                 SELECT
#                     sd.entry_id,
#                     sd.quality_id,
#                     sd.style_id,
#                     sd.color_id,
#                     SUM(sd.base_quantity)       AS base_qty,
#                     MAX(sd.dozen_qty)           AS dozen_qty,
#                     SUM(sd.final_quantity)      AS final_qty
#                 FROM size_data sd
#                 GROUP BY sd.entry_id, sd.quality_id, sd.style_id, sd.color_id
#             )
#             SELECT
#                 c.entry_id,
#                 c.quality_id,
#                 c.quality_name,
#                 c.style_id,
#                 c.style_name,
#                 c.color_id,
#                 c.color_name,
#                 c.cutting_wt,
#                 ROUND(COALESCE(d.delivered_wt, 0), 2)      AS delivered_wt,
#                 ROUND(c.cutting_wt - COALESCE(d.delivered_wt, 0), 2) AS balance_wt,
#                 cs.base_qty,
#                 cs.dozen_qty,
#                 cs.final_qty,
#                 ROUND(cs.final_qty - COALESCE(d.delivered_wt, 0), 2) AS available_balance
#             FROM cutting_data c
#             LEFT JOIN delivery_data d
#                 ON d.entry_id   = c.entry_id
#                AND d.quality_id = c.quality_id
#                AND d.style_id   = c.style_id
#                AND d.color_id   = c.color_id
#             LEFT JOIN color_summary cs
#                 ON cs.entry_id   = c.entry_id
#                AND cs.quality_id = c.quality_id
#                AND cs.style_id   = c.style_id
#                AND cs.color_id   = c.color_id
#             ORDER BY c.entry_id, c.color_id;


from django.db import connection
from django.http import JsonResponse


def get_st_delivery_folding_details_update(request):
    """
    Retrieves cutting entry and folding details, including size-wise and color-wise summaries.
    """
    entry_id = request.POST.get('entry_id')
    tm_id = request.POST.get('tm_id')
    print('data-ids:',entry_id, tm_id)

    # 1. Calculate delivered weight for this tm_id across the page
    current_page_deliverwt = 0
    if tm_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ROUND(SUM(wt), 2)
                FROM tx_folding_outward
                WHERE tm_id = %s AND status = 1
            """, [tm_id])
            result = cursor.fetchone()
            current_page_deliverwt = result[0] or 0 

    # 2. Execute aggregated SQL to fetch size-level details and color-level summaries
    with connection.cursor() as cursor:
        cursor.execute(""" 

            WITH cutting_data AS (
                SELECT
                    tm.id AS entry_id,
                    tm.quality_id,
                    tm.style_id,
                    tx.color_id,
                    qt.name AS quality_name,
                    st.name AS style_name,
                    cr.name AS color_name,
                    SUM(tx.quantity) AS cutting_wt
                FROM tx_stiching_outward tx
                LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
                LEFT JOIN color cr ON tx.color_id = cr.id 
                LEFT JOIN quality qt ON tm.quality_id = qt.id
                LEFT JOIN style st ON tm.style_id = st.id
                WHERE 
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                GROUP BY
                    tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
            ),

            delivery_data AS ( 
                SELECT
                    fo.stitching_outward_id AS entry_id,
                    fo.quality_id,
                    fo.style_id,
                    fo.color_id,
                    SUM(fo.wt) AS delivered_wt,
                    SUM(CASE WHEN fo.tm_id != %s THEN fo.wt ELSE 0 END) AS delivered_wt_excluding_tm_id
                FROM tx_folding_outward fo
                WHERE
                    fo.stitching_outward_id = %s  AND fo.status = 1
                GROUP BY
                    fo.stitching_outward_id, fo.quality_id, fo.style_id, fo.color_id
            ),

            size_data AS (
                SELECT
                    tm.id AS entry_id,
                    tx.quality_id,
                    tx.style_id,
                    tx.color_id,
                    sz.name AS size_name,
                    SUM(tx.quantity) AS base_quantity,

                    -- Folding multiplier based on size
                    CASE sz.name
                        WHEN '75' THEN prg.size_1
                        WHEN '80' THEN prg.size_2
                        WHEN '85' THEN prg.size_3
                        WHEN '90' THEN prg.size_4
                        WHEN '95' THEN prg.size_5
                        WHEN '100' THEN prg.size_6
                        WHEN '105' THEN prg.size_7
                        WHEN '110' THEN prg.size_8
                        ELSE 0
                    END AS folding_multiplier,

                    -- Accurate dozen and final quantity (no FLOOR, decimals retained)
                    ROUND(SUM(tx.quantity) / 12, 3) AS dozen_qty,

                    ROUND(
                        (1.0 * SUM(tx.quantity) / 12) * 
                        CASE sz.name
                            WHEN '75' THEN prg.size_1
                            WHEN '80' THEN prg.size_2
                            WHEN '85' THEN prg.size_3
                            WHEN '90' THEN prg.size_4
                            WHEN '95' THEN prg.size_5
                            WHEN '100' THEN prg.size_6
                            WHEN '105' THEN prg.size_7
                            WHEN '110' THEN prg.size_8
                            ELSE 0
                        END, 3
                    ) AS final_quantity

                FROM tx_stiching_outward tx
                LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
                LEFT JOIN size sz ON tx.size_id = sz.id
                LEFT JOIN tm_folding_program prg ON prg.quality_id = tx.quality_id AND prg.style_id = tx.style_id
                WHERE
                    tx.status = 1 AND tx.is_active = 1
                    AND tx.tm_id = %s
                    AND prg.status = 1
                GROUP BY
                    tm.id, tx.quality_id, tx.style_id, tx.color_id, sz.name,
                    prg.size_1, prg.size_2, prg.size_3, prg.size_4,
                    prg.size_5, prg.size_6, prg.size_7, prg.size_8
            ),

            color_summary AS (
                SELECT
                    sd.entry_id,
                    sd.quality_id,
                    sd.style_id,
                    sd.color_id,
                    SUM(sd.base_quantity) AS base_qty,
                    SUM(sd.dozen_qty) AS dozen_qty,
                    SUM(sd.final_quantity) AS final_qty
                FROM size_data sd
                GROUP BY sd.entry_id, sd.quality_id, sd.style_id, sd.color_id
            )

            SELECT
                c.entry_id,
                c.quality_id,
                c.quality_name, 
                c.style_id,
                c.style_name,
                c.color_id,
                c.color_name,  
                c.cutting_wt,
                ROUND(COALESCE(d.delivered_wt, 0), 3) AS delivered_wt, 
                ROUND(COALESCE(d.delivered_wt_excluding_tm_id, 0), 3) AS already_rec_wt,
                ROUND(c.cutting_wt - COALESCE(d.delivered_wt, 0), 3) AS balance_wt,

                cs.base_qty,
                cs.dozen_qty,
                cs.final_qty,
                ROUND(cs.final_qty - COALESCE(d.delivered_wt, 0), 3) AS available_balance

            FROM cutting_data c
            LEFT JOIN delivery_data d ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id AND d.style_id = c.style_id AND d.color_id = c.color_id
            LEFT JOIN color_summary cs ON cs.entry_id = c.entry_id AND cs.quality_id = c.quality_id AND cs.style_id = c.style_id AND cs.color_id = c.color_id
            ORDER BY c.entry_id, c.color_id;

            
        """, [entry_id, tm_id, entry_id,entry_id])
        # """, [tm_id, entry_id, tm_id,tm_id])

        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Add master data
    try:
        inward = parent_stiching_outward_table.objects.get(status=1, id=entry_id)
        fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
        quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
        style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
    except parent_stiching_outward_table.DoesNotExist:
        fabric = quality = style = None

    return JsonResponse({
        'status': 'success',
        'data': rows,  
        'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
        'style': {'id': style['id'], 'name': style['name']} if style else '',
        'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
        'current_page_deliverwt': current_page_deliverwt
    })




# def get_st_delivery_folding_details_update(request):
#     """
#     Retrieves cutting entry and folding details.
#     """
#     entry_id = request.POST.get('entry_id')
#     tm_id = request.POST.get('tm_id')

#     # The existing query for current_page_deliverwt is correct and does not need changes.
#     current_page_deliverwt = 0
#     if tm_id:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT ROUND(SUM(wt), 2)
#                 FROM tx_folding_outward
#                 WHERE tm_id = %s AND status = 1
#             """, [tm_id])
#             result = cursor.fetchone()
#             if result and result[0]:
#                 current_page_deliverwt = result[0]

#     with connection.cursor() as cursor:
#         cursor.execute("""
#             WITH cutting_data AS (
#                 SELECT
#                     tm.id AS entry_id,
#                     tm.quality_id,
#                     tm.style_id,
#                     tx.color_id,
#                     qt.name AS quality_name,
#                     st.name AS style_name,
#                     cr.name AS color_name,
#                     SUM(tx.quantity) AS cutting_wt
#                 FROM tx_stiching_outward tx
#                 LEFT JOIN tm_stiching_outward tm ON tx.tm_id = tm.id
#                 LEFT JOIN color cr ON tx.color_id = cr.id
#                 LEFT JOIN quality qt ON tm.quality_id = qt.id
#                 LEFT JOIN style st ON tm.style_id = st.id
#                 WHERE
#                     tx.status = 1 AND tx.is_active = 1
#                     AND tx.tm_id = %s
#                 GROUP BY
#                     tm.id, tm.quality_id, tm.style_id, tx.color_id, qt.name, st.name, cr.name
#             ),
#             delivery_data AS ( 
#                 SELECT
#                     fo.stitching_outward_id AS entry_id,
#                     fo.quality_id,
#                     fo.style_id,
#                     fo.color_id,
#                     SUM(fo.wt) AS delivered_wt,
#                     SUM(CASE WHEN fo.tm_id != %s THEN fo.wt ELSE 0 END) AS delivered_wt_excluding_tm_id
#                 FROM tx_folding_outward fo
#                 WHERE
#                     fo.stitching_outward_id = %s AND fo.status = 1
#                 GROUP BY
#                     fo.stitching_outward_id, fo.quality_id, fo.style_id, fo.color_id
#             )
#             SELECT
#                 c.entry_id,
#                 c.quality_id,
#                 c.quality_name, 
#                 c.style_id,
#                 c.style_name,
#                 c.color_id,
#                 c.color_name,  
#                 c.cutting_wt,
#                 ROUND(COALESCE(d.delivered_wt, 0), 2) AS delivered_wt,
#                 ROUND(COALESCE(d.delivered_wt_excluding_tm_id, 0), 2) AS already_rec_wt,
#                 ROUND(
#                     c.cutting_wt - COALESCE(d.delivered_wt, 0),
#                     2
#                 ) AS balance_wt
#             FROM cutting_data c
#             LEFT JOIN delivery_data d ON d.entry_id = c.entry_id AND d.quality_id = c.quality_id AND d.style_id = c.style_id AND d.color_id = c.color_id;
#         """, [entry_id, tm_id, entry_id]) # Corrected parameters

#         columns = [col[0] for col in cursor.description]
#         results = cursor.fetchall()
#         rows = [dict(zip(columns, row)) for row in results]
#         print('folding-prg-data:', rows)
 
#     # Fetch related master data
#     try:
#         inward = parent_stiching_outward_table.objects.get(status=1, id=entry_id)
#         fabric = fabric_program_table.objects.filter(status=1, id=inward.fabric_id).values('id', 'name').first()
#         quality = quality_table.objects.filter(status=1, id=inward.quality_id).values('id', 'name').first()
#         style = style_table.objects.filter(status=1, id=inward.style_id).values('id', 'name').first()
#     except parent_stiching_outward_table.DoesNotExist:
#         quality = None
#         style = None
#         fabric = None

#     return JsonResponse({
#         'status': 'success',
#         'data': rows,
#         'quality': {'id': quality['id'], 'name': quality['name']} if quality else '',
#         'style': {'id': style['id'], 'name': style['name']} if style else '',
#         'fabric': {'id': fabric['id'], 'name': fabric['name']} if fabric else '',
#         'current_page_deliverwt': current_page_deliverwt
#     })




def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]





@csrf_exempt
def insert_folding_delivery(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            fabric_id = request.POST.get('fabric_id')
            style_id = request.POST.get('style_id')
            party_id = request.POST.get('party_id')
            entry_id = request.POST.get('entry_id')
            folding_date = request.POST.get('folding_date')
            lot_no = request.POST.get('lot_no')
            work_order_no = request.POST.get('work_order_no')
            entry_data = json.loads(request.POST.get('chemical_data', '[]'))

            folding_no = generate_folding_delivery_num_series()

            # Create parent record
            material_request = parent_folding_delivery_table.objects.create(
                outward_no=folding_no.upper(),
                outward_date=folding_date,
                party_id=party_id,
                lot_no=lot_no,
                stitching_outward_id=entry_id,
                work_order_no=work_order_no,
                quality_id=quality_id,
                style_id=style_id,
                company_id=company_id,
                cfyear=2025,
                fabric_id=fabric_id or 0,
                total_quantity=0,  # Temp
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_quantity = 0  # Initialize counter

            # Create child entries
            for cutting in entry_data:
                # size_vals = [cutting.get(f'size_{i}', 0) or 0 for i in range(1, 9)]
                # row_total = sum(map(int, size_vals))  # Handle string or None
                weight =  cutting.get('outward_wt') 
                print('wt:',weight)
                child_folding_delivery_table.objects.create(
                    work_order_no=work_order_no,
                    tm_id=material_request.id,
                    quality_id=quality_id,
                    stitching_outward_id = entry_id,
                    style_id=style_id,
                    party_id=party_id,
                    color_id=cutting.get('color_id'),
                    wt = weight,
               
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025
                )

                wt = cutting.get('outward_wt') or 0
                total_quantity += float(wt)

                # total_quantity += (cutting.get('wt'))  # Add to total
                print('t_qty:')
            # Update parent with final total
            material_request.total_quantity = total_quantity
            material_request.save()

            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'folding_delivery/add_folding_delivery.html')





# Helper function to safely convert to Decimal
def safe_decimal(value, default=Decimal('0.00')):
    try:
        return Decimal(value)
    except (ValueError, TypeError, InvalidOperation):
        return default



@csrf_exempt
def update_folding_delivery(request):
    if request.method == 'POST':
        try:
            # Safely get and validate all POST data
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')
            master_id = request.POST.get('tm_id')
            outward_date = request.POST.get('outward_date')
            remarks = request.POST.get('remarks')
            work_order_no = request.POST.get('work_order_no')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            party_id = request.POST.get('party_id')
            fabric_id = request.POST.get('fabric_id')
            entry_id = request.POST.get('entry_id')

            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            chemical_data = request.POST.get('chemical_data')
            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'})

            try:
                table_data = json.loads(chemical_data)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error_message': 'Invalid JSON data'})

            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Use a database transaction to ensure atomicity
            with transaction.atomic():
                # Step 1: Update master table entry
                material_request = parent_folding_delivery_table.objects.filter(id=master_id).first()
                if not material_request:
                    return JsonResponse({'success': False, 'error_message': 'Invalid master ID'})

                material_request.outward_date = outward_date
                material_request.remarks = remarks
                material_request.quality_id = quality_id
                # material_request.fabric_id = fabric_id
                material_request.style_id = style_id
                material_request.updated_by = user_id 
                material_request.updated_on = timezone.now()

                # Step 2: Delete existing child entries
                child_folding_delivery_table.objects.filter(tm_id=master_id).delete()

                total_qty = Decimal('0.00')

                # Step 3: Insert updated child entries
                for row in table_data:
                    # Correctly and safely convert the outward_wt to a Decimal
                    outward_wt_decimal = safe_decimal(row.get('outward_wt'))
                    color_id = row.get('color_id')

                    # Skip rows with zero weight or invalid color_id
                    if outward_wt_decimal > 0 and color_id:
                        total_qty += outward_wt_decimal

                        child_folding_delivery_table.objects.create(
                            work_order_no=work_order_no,
                            tm_id=material_request.id,
                            quality_id=quality_id,
                            stitching_outward_id=entry_id,
                            style_id=style_id,
                            party_id=party_id,
                            color_id=color_id,
                            wt=outward_wt_decimal, # Use the correctly converted Decimal value
                            created_by=user_id,
                            created_on=timezone.now(),
                            company_id=company_id,
                            cfyear=timezone.now().year # Dynamically get the current year
                        )

                # Step 4: Update master total quantity 
                material_request.total_quantity = total_qty
                material_request.save()

            return JsonResponse({'success': 'true', 'message': 'Updated successfully!'}) 

        except Exception as e:
            return JsonResponse({'success': 'false', 'error_message': str(e)})

    return JsonResponse({'success': 'false', 'error_message': 'Invalid request method'})



def update_master_folding_delivery(request):
    if request.method == 'POST':
        outward_date_str = request.POST.get('outward_date')
        tm_id = request.POST.get('tm_id')
      
        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = parent_folding_delivery_table.objects.get(id=tm_id)
     

            if outward_date_str:
                outward_date = datetime.strptime(outward_date_str, '%Y-%m-%d').date()
                parent_item.outward_date = outward_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except parent_folding_delivery_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

