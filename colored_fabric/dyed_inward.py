from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
from colored_fabric.models import *
import party
from program_app.models import knitting_table, sub_knitting_table
from yarn.models import *
from company.models import *
from grey_fabric.models import * 
from employee.models import * 

from purchase_app.models import *
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
from common.utils import *


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
from django.utils.timezone import make_aware

from program_app.models import *


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 


# Create your views here.


def dyed_fabric_inward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
      
        party =  party_table.objects.filter(status=1).filter(is_fabric=1)
 
        yarn_count = count_table.objects.filter(status=1)
        dyeing = dyeing_program_table.objects.filter(status=1,is_dyed_fabric=1)
        
        lot = (
            dyed_fabric_inward_table.objects
            .filter(status=1)
            .values('lot_no')  # Group by lot_no
            .annotate(
                total_gross_wt=Sum('total_wt'),
             
            )   
            .order_by('lot_no')
        )
        
        return render(request,'inward/dyed_fabric_inward.html',{'party':party,'yarn_count':yarn_count,'dyeing':dyeing,'lot':lot})
    else:
        return HttpResponseRedirect("/admin")
    

def generate_inw_num_series():
    last_purchase = dyed_fabric_inward_table.objects.filter(status=1).order_by('-id').first()
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




def dyed_fabric_inward_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        # supplier = party_table.objects.filter(is_knitting=1,status=1)

        # party = party_table.objects.filter(status=1,is_process=1)
        product = product_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        
        # fabric_program = fabric_program_table.objects.filter(status=1)
        fabric_program_qs = fabric_program_table.objects.filter(status=1)
        # linked_knitting_ids = grey_fabric_po_table.objects.filter(status=1).values('program_id')

        # Filter knitting_table
        # knitting = dyeing_program_table.objects.filter(status=1, is_dyed_fabric=1).exclude(id__in=linked_knitting_ids)
        knitting = dyeing_program_table.objects.filter(status=1, is_dyed_fabric=1)
        fabric_program = []
        for fp in fabric_program_qs:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                print(f"fabric_item: {fabric_item}, ID: {fp.fabric_id}, Name: {getattr(fabric_item, 'name', 'NO NAME')}")
                fabric_program.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                })
            except fabric_table.DoesNotExist:
                print(f"fabric_id {fp.fabric_id} not found in fabric_table")
                fabric_program.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': 'N/A'
                })
        # mill = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        # mill =  party_table.objects.filter(status=1).filter(is_trader=1)

        party = party_table.objects.filter(status=1,is_trader=1)
        compacting = party_table.objects.filter(status=1,is_compacting=1)
        inward_number = generate_inw_num_series

        dyeing = dyeing_program_table.objects.filter(status=1)

        fabric_program_qs = fabric_program_table.objects.filter(status=1)

        # Build fabric_program list with resolved fabric_name from fabric_table
        fabric_program_with_name = []
        for fp in fabric_program_qs:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                print(f"fabric_item: {fabric_item}, ID: {fp.fabric_id}, Name: {getattr(fabric_item, 'name', 'NO NAME')}")
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                })
            except fabric_table.DoesNotExist:
                print(f"fabric_id {fp.fabric_id} not found in fabric_table")
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': 'N/A'
                })


        return render(request, 'inward/add_inward.html', {
            'party': party,
            'dyeing':dyeing,
            'product': product,
            'count':count,
            'fabric_program':fabric_program,
            'inward_number': inward_number,
            'knitting':knitting, 
            'compacting':compacting,
            'fabric_program_with_name':fabric_program_with_name,


            
        }) 
    else:
        return HttpResponseRedirect("/admin")




@csrf_exempt  # Only if you don't want to handle CSRF tokens for this view (not recommended for production)
def get_dyed_inward_party_list(request):
    # material_type = request.POST.get('material_type')

    if request.method == 'POST' and 'material_type' in request.POST: 
        material_type = request.POST['material_type']
        print('m-type:',material_type)
        if material_type == 'grey':
            parties = party_table.objects.filter(is_process=1, status=1).order_by('name')
        elif material_type == 'dye':

            parties = party_table.objects.filter(status=1).filter(is_fabric=1).order_by('name')



            # parties = party_table.objects.filter(is_trader=1,status=1) | party_table.objects.filter(is_mill=1,status=1)
        else:
            parties = party_table.objects.none()

        data = [{"id": p.id, "name": p.name} for p in parties]
    return JsonResponse(data, safe=False)




from django.db.models import Sum, Max

@csrf_exempt
def get_grey_out_lot_lists(request): 
    if request.method == 'POST' and 'supplier_id' in request.POST: 
        supplier_id = request.POST['supplier_id']
        print('party-id:', supplier_id)

        if supplier_id:
            # Step 1: Get child orders with balance
            child_orders = grey_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                balance_wt__gt=0
            ).values_list('out_id', flat=True)

            print('balance-data:', child_orders)

            # Step 2: Group by lot_no
            orders = (
                parent_gf_delivery_table.objects
                .filter(id__in=child_orders, status=1)
                .values('lot_no')
                .annotate(
                    id=Max('id'),  # You can change to Min('id') if needed
                    do_number=Max('do_number'),  # Assuming latest one is desired
                    total_quantity=Sum('total_wt')
                )
                .order_by('-id')
            )

            # Step 3: Totals for overall PO weight and balances
            totals = grey_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                balance_wt__gt=0
            ).aggregate(
                outward_wt=Sum('outward_wt'), 
                inward_wt=Sum('inward_wt'),
                balance_wt=Sum('balance_wt')
            ) 

            balance_roll = (totals['outward_wt'] or 0) - (totals['inward_wt'] or 0)

            return JsonResponse({
                'orders': list(orders),
                'po_rolls': balance_roll,
                'balance_wt': float(totals['balance_wt'] or 0),
                'po_quantity': float(totals['balance_wt'] or 0),
                'inward_wt': float(totals['inward_wt'] or 0)
            })

    return JsonResponse({'orders': []})



from django.http import JsonResponse
def get_grey_outward_lists(request):
    if request.method == 'POST' and 'lot_no' in request.POST: 
        supplier_id = request.POST['supplier_id']
        lot_no = request.POST.get('lot_no')
        print('party-id:',lot_no)

        if lot_no:
            child_orders = grey_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                lot_no=lot_no,
                balance_wt__gt=0
            ).values_list('out_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(parent_gf_delivery_table.objects.filter( 
                id__in=child_orders, 
                status=1
            ).values('id', 'do_number', 'lot_no','total_wt').order_by('-id'))

            totals = grey_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                lot_no=lot_no,
                balance_wt__gt=0
            ).aggregate(
                outward_wt=Sum('outward_wt'),
                inward_wt=Sum('inward_wt'),
                
                balance_wt=Sum('balance_wt')
            ) 

            order_through = sub_child_gf_delivery_detail_table.objects.filter(status=1,tm_id__in=child_orders).first()
            order_through_party = party_table.objects.filter(status=1, id=order_through.party_id).values('id', 'name', 'mobile', 'gstin').first()
            balance_roll = (totals['outward_wt'] or 0) - (totals['inward_wt'] or 0)
            # wt = totals['balance_wt']
            # print('wt:',wt)
            return JsonResponse({
                'orders': orders,
                'po_rolls': balance_roll,
                'balance_wt': float(totals['balance_wt'] or 0),
                'po_quantity': float(totals['balance_wt'] or 0),
                'inward_wt': float(totals['inward_wt'] or 0),
                # 'available_wt':wt
                'order_through':order_through_party 
            })
 
    return JsonResponse({'orders': []})


from django.http import JsonResponse
from django.http import JsonResponse




def get_grey_outward_delivery_lists(request):
    if request.method == 'POST':
        outward_id = request.POST.get('outward_id')

        order_through_parties = []

        if outward_id:
            # Get all party_ids from matching sub_child entries
            order_through_qs = sub_child_gf_delivery_detail_table.objects.filter(
                status=1,
                tm_id=outward_id
            ).values_list('party_id', flat=True).distinct()

            if order_through_qs:
                # Fetch all matching parties
                order_through_parties = list(
                    party_table.objects.filter(
                        status=1,
                        id__in=order_through_qs
                    ).values('id', 'name', 'mobile', 'gstin')
                )

        return JsonResponse({
            'order_through': order_through_parties
        })

    return JsonResponse({'order_through': []})



def get_grey_outward_color_list(request):
    if request.method == 'POST':
        outward_id = request.POST.get('outward_id')
        colors = []

        if outward_id:
            color_dia_pairs = child_gf_delivery_table.objects.filter(
                status=1,
                tm_id=outward_id
            ).values_list('color_id').distinct()
            # ).values_list('color_id', 'dia_id').distinct()
            print('color_dia_pairs:',color_dia_pairs)
            color_ids = [color_id for color_id,  in color_dia_pairs]

            if color_ids:
                colors = list(
                    color_table.objects.filter(
                        status=1,
                        id__in=color_ids
                    ).values('id', 'name')
                )

        return JsonResponse({'color': colors})

    return JsonResponse({'order_through': []})




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Sum

@csrf_exempt
def get_grey_outward_detail_lists(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        out_id_str = request.POST.get('outward_list', '')
        out_ids = [x.strip() for x in out_id_str.split(',') if x.strip()]
        color_ids = [int(x.strip()) for x in request.POST.get('color_id', '').split(',') if x.strip()]
        tm_inward_id = request.POST.get('tm_id')

        print('out-ids:', out_ids, 'color-ids:', color_ids)
        print('tm_inward_id:', tm_inward_id)

        child_orders = grey_out_available_balance_table.objects.filter(
            out_id__in=out_ids, balance_wt__gt=0
        ).values('out_id')

        order_number = parent_gf_delivery_table.objects.filter(
            id__in=child_orders, status=1
        ).values('id', 'do_number', 'lot_no').order_by('-id')

        totals = grey_out_available_balance_table.objects.filter(
            out_id__in=out_ids, balance_wt__gt=0
        ).aggregate(
            po_roll=Sum('outward_wt'),
            outward_wt=Sum('outward_wt'),
            inward_quantity=Sum('inward_wt'),
            balance_wt=Sum('balance_wt'),
        )

        program_id_list = list(
            grey_out_available_balance_table.objects.filter(
                out_id__in=out_ids, balance_wt__gt=0
            ).values_list('program_id', flat=True).distinct()
        )

        program_qs = dyed_fab_program_balance_table.objects.filter(
            balance_quantity__gt=0, program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(dyeing_program_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'program_no', 'name', 'total_wt', 'fabric_id'))

        program = dyed_fab_inw_available_wt_table.objects.filter(
            program_id__in=program_qs, color_id__in=color_ids
        ).values_list(
            'program_id', 'dia_id', 'color_id', 'pg_roll', 'pg_wt', 'in_rolls',
            'in_wt', 'in_gross_wt','out_rolls', 'out_wt', 'balance_roll', 'balance_wt'
        )

        formatted_data = [
            {
                'program_id': row[0],
                'dia_id': row[1],
                'color_id': row[2],
                'pg_roll': row[3],
                'pg_wt': row[4],
                'in_rolls': row[5],
                'in_wt': row[6],
                'in_gross_wt': row[7],
                'out_rolls': row[8],
                'out_wt': row[9],
                'balance_roll': row[10],
                'balance_wt': row[11]
            } for row in program
        ]

        program_details = []
        program_seen_keys = set()

        for pid in program_id_list:
            knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            sub_knits = sub_dyeing_program_table.objects.filter(
                tm_id=knit.id, color_id__in=color_ids, status=1
            ).order_by('dia_id')

            for sub in sub_knits:
                key = (sub.tm_id, sub.dia_id, sub.fabric_id, sub.color_id)
                if key in program_seen_keys:
                    continue
                program_seen_keys.add(key)

                fabric_qs = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_data = []
                for fp in fabric_qs:
                    fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
                    fabric_data.append({
                        'id': fp.id,
                        'name': fp.name,
                        'fabric_id': fp.fabric_id,
                        'fabric_name': fabric_item.name if fabric_item else 'N/A'
                    })

                dia = dia_table.objects.filter(id=sub.dia_id).first()
                color = color_table.objects.filter(id=sub.color_id).first()

                inward_ids = dyed_fabric_inward_table.objects.filter(
                    outward_id__in=out_ids, status=1
                ).values_list('id', flat=True)

                inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
                    tm_id__in=inward_ids, dia_id=sub.dia_id, status=1
                ).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = (sub.roll or 0) - inward_roll_sum
                total_wt_balance = (sub.roll or 0) * (sub.roll_wt or 0)
                inward_quantity = inward_roll_sum * (sub.roll_wt or 0)

                program_details.append({
                    'program_id': sub.tm_id,
                    'program_name': knit.name,
                    'fabric': fabric_data,
                    'fabric_id': sub.fabric_id,
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia_id,
                    'color': color.name if color else '',
                    'color_id': sub.color_id,
                    'lot_roll': remaining_roll,
                    'per_roll_wt': sub.roll_wt,
                    'lot_roll_wt': total_wt_balance - inward_quantity,
                    'out_id': out_ids,
                    'total_roll': inward_roll_sum,
                    'total_wt': inward_quantity,
                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id and row['color_id'] == sub.color_id
                    ]
                })

        # ✅ Group by color and dia
        color_grouped_details = defaultdict(lambda: defaultdict(list))
        for detail in program_details:
            color_grouped_details[detail['color_id']][detail['dia_id']].append(detail)

        # Convert to JSON-serializable dict
        final_color_grouped = {
            color: dict(dias) for color, dias in color_grouped_details.items()
        }

        sub_po = parent_gf_delivery_table.objects.filter(id__in=out_ids, status=1).first()
        fabric_ids = {detail['fabric_id'] for detail in program_details if detail.get('fabric_id')}

        fabric_id_value = next(iter(fabric_ids)) if len(fabric_ids) == 1 else None

        # ORDER SECTION
        order_data = []
        if tm_inward_id:
            parent_pos = dyed_fabric_inward_table.objects.filter(id=tm_inward_id)
            for po in parent_pos:
                deliveries = sub_dyed_fabric_inward_table.objects.filter(tm_id=tm_inward_id, status=1)
                for delivery in deliveries:
                    programs = dyeing_program_table.objects.filter(id__in=program_qs, is_active=1)
                    for program in programs:
                        if not sub_dyeing_program_table.objects.filter(tm_id=program.id).exists():
                            continue

                        product = fabric_program_table.objects.filter(id=delivery.fabric_id).first()

                        inward_totals = sub_dyed_fabric_inward_table.objects.filter(
                            tm_id=tm_inward_id, is_active=1
                        ).aggregate(
                            inward_roll=Sum('roll'),
                            inward_quantity=Sum('roll_wt'),
                            inward_gross=Sum('gross_wt')
                        )

                        order_data.append({
                            'po_roll': delivery.roll or 0,
                            'total_rolls': inward_totals.get('inward_roll') or 0,
                            'po_quantity': delivery.gross_wt or 0,
                            'inward_roll': inward_totals.get('inward_roll') or 0,
                            'inward_quantity': inward_totals.get('inward_quantity') or 0,
                            'inward_gross_wt': inward_totals.get('inward_gross') or 0,
                            'balance_quantity': 0,
                            'tax_value': 5,
                            'fabric_id': delivery.fabric_id,
                            'dia': delivery.dia_id,
                            'color': delivery.color_id,
                            'program_id': program.id,
                            'wt_per_roll': sub_po.total_wt if sub_po else 0,
                            'roll': delivery.roll_wt or 0,
                            'per_roll': delivery.roll_wt or 0,
                            'tx_quantity': delivery.roll_wt or 0,
                            'gross_wt': 0,
                            'id': program.id,
                            'out_id': po.id,
                            'tm_id': po.id,
                            'tx_id': delivery.id,
                            'total_quantity': delivery.roll_wt or 0,
                            'total_gross_wt': delivery.gross_wt or 0,
                            'product': product.name if product else '',
                        })

        return JsonResponse({
            'orders': list(order_number),
            'po_roll': totals.get('po_roll') or 0,
            'po_quantity': float(totals.get('outward_wt') or 0),
            'inward_quantity': float(totals.get('inward_quantity') or 0),
            'balance_wt': 0,
            'program_id': program_id_list,
            'gross_wt': sub_po.gross_wt if sub_po else 0,
            'quantity': 0,
            'program': prg_list,
            'order_data': order_data,
            'program_details': program_details,
            'fabric_id': fabric_id_value,
            'color_grouped_details': final_color_grouped
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


# @csrf_exempt
# def get_grey_outward_detail_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     out_id_str = request.POST.get('outward_list', '')
#     out_id = [x.strip() for x in out_id_str.split(',') if x.strip()]

#     color_ids = request.POST.get('color_id', '')
#     color_id = [int(x.strip()) for x in color_ids.split(',') if x.strip()]

#     # color_id = [x.strip() for x in color_ids.split(',') if x.strip()]
#     tm_inward_id = request.POST.get('tm_id')

#     print('out-ids:', out_id, 'color-ids:',color_id)
#     print('tm_inward_id:', tm_inward_id)

#     try:
#         # Get child orders with available balance
#         child_orders = grey_out_available_balance_table.objects.filter(
#             out_id__in=out_id, balance_wt__gt=0
#         ).values('out_id')

#         order_number = parent_gf_delivery_table.objects.filter(
#             id__in=child_orders, status=1
#         ).values('id', 'do_number', 'lot_no').order_by('-id')

#         print('order_number:', order_number)

#         totals = grey_out_available_balance_table.objects.filter(
#             out_id__in=out_id, balance_wt__gt=0
#         ).aggregate(
#             po_roll=Sum('outward_wt'),
#             outward_wt=Sum('outward_wt'),
#             inward_quantity=Sum('inward_wt'),
#             balance_wt=Sum('balance_wt'), 
#         )

#         print('totals:', totals)

#         program_id_list = list(
#             grey_out_available_balance_table.objects.filter(
#                 out_id__in=out_id, balance_wt__gt=0
#             ).values_list('program_id', flat=True).distinct()
#         )

#         program_qs = dyed_fab_program_balance_table.objects.filter(
#             balance_quantity__gt=0, program_id__in=program_id_list
#         ).values_list('program_id', flat=True)

#         prg_list = list(dyeing_program_table.objects.filter(
#             id__in=program_qs, status=1 
#         ).values('id', 'program_no', 'name', 'total_wt','fabric_id')) 

#         program = list(
#             # dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs)
#             dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs,color_id__in=color_id)
#             .values_list('program_id', 'dia_id', 'color_id', 'pg_roll', 'pg_wt', 'in_rolls', 'in_wt', 'out_rolls','out_wt','balance_roll', 'balance_wt')
#         )

#         formatted_data = [
#             {
#                 'program_id': row[0],
#                 'dia_id': row[1],
#                 'color_id': row[2],
#                 'pg_roll': row[3], 
#                 'pg_wt': row[4], 
#                 'in_rolls': row[5],
#                 'in_wt': row[6],
#                 'out_rolls': row[7],
#                 'out_wt': row[8],
#                 'balance_roll': row[9],
#                 'balance_wt': row[10]
#             } for row in program
#         ]

#         sub_po = parent_gf_delivery_table.objects.filter(id__in=out_id, status=1).first()
#         po_total_roll = totals['po_roll'] or 0

#         # Collect all program details
#         program_details = []
#         program_seen_keys = set()
 
#         for pid in program_id_list:
#             knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
#             if not knit:
#                 continue

#             sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id,  color_id__in=color_id, status=1).order_by('dia_id')
#             for sub in sub_knits:
#                 key = (sub.tm_id, sub.dia_id, sub.fabric_id)
#                 if key in program_seen_keys:
#                     continue
#                 program_seen_keys.add(key)

#                 fabric_data = []
#                 fabric_qs = fabric_program_table.objects.filter(id=sub.fabric_id)
#                 for fp in fabric_qs:
#                     fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
#                     fabric_data.append({
#                         'id': fp.id,
#                         'name': fp.name,
#                         'fabric_id': fp.fabric_id,
#                         'fabric_name': fabric_item.name if fabric_item else 'N/A'
#                     })

#                 dia = dia_table.objects.filter(id=sub.dia_id).first()
#                 color = color_table.objects.filter(id=sub.color_id).first()

#                 inward_ids = list(dyed_fabric_inward_table.objects.filter(outward_id__in=out_id, status=1).values_list('id', flat=True))
#                 inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(tm_id__in=inward_ids, dia_id=sub.dia_id, status=1).aggregate(total=Sum('roll'))['total'] or 0

#                 remaining_roll = (sub.roll or 0) - inward_roll_sum
#                 total_wt_balance = (sub.roll or 0) * (sub.roll_wt or 0)
#                 inward_quantity = inward_roll_sum * (sub.roll_wt or 0)

#                 program_details.append({
#                     'program_id': sub.tm_id,
#                     'program_name': knit.name,
#                     'fabric': fabric_data,
#                     'fabric_id': sub.fabric_id,
#                     'dia': dia.name if dia else '',
#                     'dia_id': sub.dia_id,
#                     'color': color.name if color else '',
#                     'color_id': sub.color_id,
#                     'lot_roll': remaining_roll,
#                     'per_roll_wt': sub.roll_wt,
#                     'lot_roll_wt': total_wt_balance - inward_quantity,
#                     'out_id': out_id,
#                     'total_roll': inward_roll_sum,
#                     'total_wt': inward_quantity,
#                     'program_bal_value': [
#                         row for row in formatted_data
#                         if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id and row['color_id'] == sub.color_id
#                     ]
#                 })

#                 color_grouped_details = defaultdict(list)

#                 for detail in program_details:
#                     color_grouped_details[detail['color_id']].append(detail)

#                 # Convert defaultdict to regular dict for JSON serialization
#                 color_grouped_details = dict(color_grouped_details)
#                 print('color-grp:',color_grouped_details)

#                 # Extract fabric_ids from program_details
#                 fabric_ids = set(
#                     detail['fabric_id']
#                     for detail in program_details
#                     if 'fabric_id' in detail and detail['fabric_id'] is not None
#                 )

#                 # Decide what to return for fabric_id
#                 if len(fabric_ids) == 1:
#                     fabric_id_value = next(iter(fabric_ids))  # The only fabric ID
#                 else:
#                     fabric_id_value = None  # or "multiple", as needed

#         # ---- ORDER DATA SECTION ----
#         order_data = []

#         if tm_inward_id:
#             print('tm-inward-ids:',tm_inward_id)
#             parent_pos = dyed_fabric_inward_table.objects.filter(id=tm_inward_id)
#             for po in parent_pos:
#                 deliveries = sub_dyed_fabric_inward_table.objects.filter(tm_id=tm_inward_id, status=1)

#                 for delivery in deliveries:
#                     programs = dyeing_program_table.objects.filter(id__in=program_qs, is_active=1)
#                     for program in programs:
#                         sub_knit = sub_dyeing_program_table.objects.filter(tm_id=program.id)
#                         if not sub_knit.exists():
#                             continue

#                         product = fabric_program_table.objects.filter(id=delivery.fabric_id).first()

#                         inward_totals = sub_dyed_fabric_inward_table.objects.filter(
#                             tm_id=tm_inward_id, is_active=1
#                         ).aggregate(
#                             inward_roll=Sum('roll'),
#                             inward_quantity=Sum('roll_wt'), 
#                             inward_gross=Sum('gross_wt')
#                         )

#                         inward_roll = inward_totals.get('inward_roll') or 0
#                         inward_quantity = inward_totals.get('inward_quantity') or 0
#                         inward_gross = inward_totals.get('inward_gross') or 0

#                         remaining_roll_wt = delivery.roll_wt or 0
#                         qty = delivery.roll_wt or 0
#                         remaining_quantity = delivery.gross_wt or 0

#                         # bal_roll = remaining_roll_wt - inward_roll
#                         # bal_quantity = qty - inward_quantity

#                         # # Skip if no balance left
#                         # if bal_roll == 0 and bal_quantity == 0:
#                         #     continue

#                         order_data.append({
#                             'po_roll': delivery.roll or 0,
#                             'total_rolls': inward_roll,
#                             'po_quantity': remaining_quantity,
#                             'inward_roll': inward_roll,
#                             'inward_quantity': inward_quantity,
#                             'inward_gross_wt': inward_gross,
#                             'balance_quantity':0,# bal_quantity,
#                             'tax_value': 5,
#                             'fabric_id': delivery.fabric_id,
#                             'dia': delivery.dia_id,
#                             'color': delivery.color_id,
#                             'program_id': program.id,
#                             'wt_per_roll': sub_po.total_wt if sub_po else 0,
#                             'roll': remaining_roll_wt,
#                             'per_roll': delivery.roll_wt,
#                             'tx_quantity': qty,
#                             'gross_wt': 0,
#                             'id': program.id,
#                             'out_id': po.id,
#                             'tm_id': po.id,
#                             'tx_id': delivery.id,
#                             'total_quantity': qty,
#                             'total_gross_wt': delivery.gross_wt or 0,
#                             'total_roll': delivery.roll or 0,
#                             'product': product.name if product else '',
#                         })

#         return JsonResponse({
#             'orders': list(order_number),
#             'po_roll': po_total_roll,
#             'balance_wt': 0,
#             'po_quantity': float(totals['outward_wt'] or 0),
#             'inward_quantity': float(totals['inward_quantity'] or 0),
#             'program_id': program_id_list,
#             'gross_wt': sub_po.gross_wt if sub_po else 0,
#             'quantity': 0,
#             'program': prg_list,
#             'order_data': order_data,
#             'program_details': program_details,
#             'fabric_id':fabric_id_value,
#             'color_grouped_details':color_grouped_details
#         }) 

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_grey_outward_detail_lists_bk_972025(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    out_id_str = request.POST.get('outward_list', '')
    out_id = [x.strip() for x in out_id_str.split(',') if x.strip()]
    tm_inward_id = request.POST.get('tm_id')

    print('out-ids:', out_id)
    print('tm_inward_id:', tm_inward_id)

    try:
        # Get child orders with available balance
        child_orders = grey_out_available_balance_table.objects.filter(
            out_id__in=out_id, balance_wt__gt=0
        ).values('out_id')

        order_number = parent_gf_delivery_table.objects.filter(
            id__in=child_orders, status=1
        ).values('id', 'do_number', 'lot_no').order_by('-id')

        print('order_number:', order_number)

        totals = grey_out_available_balance_table.objects.filter(
            out_id__in=out_id, balance_wt__gt=0
        ).aggregate(
            po_roll=Sum('outward_wt'),
            outward_wt=Sum('outward_wt'),
            inward_quantity=Sum('inward_wt'),
            balance_wt=Sum('balance_wt'), 
        )

        print('totals:', totals)

        program_id_list = list(
            grey_out_available_balance_table.objects.filter(
                out_id__in=out_id, balance_wt__gt=0
            ).values_list('program_id', flat=True).distinct()
        )

        program_qs = dyed_fab_program_balance_table.objects.filter(
            balance_quantity__gt=0, program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(dyeing_program_table.objects.filter(
            id__in=program_qs, status=1 
        ).values('id', 'program_no', 'name', 'total_wt','fabric_id')) 

        program = list(
            dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs)
            .values_list('program_id', 'dia_id', 'color_id', 'pg_roll', 'pg_wt', 'in_rolls', 'in_wt', 'out_rolls','out_wt','balance_roll', 'balance_wt')
        )

        formatted_data = [
            {
                'program_id': row[0],
                'dia_id': row[1],
                'color_id': row[2],
                'pg_roll': row[3], 
                'pg_wt': row[4], 
                'in_rolls': row[5],
                'in_wt': row[6],
                'out_rolls': row[7],
                'out_wt': row[8],
                'balance_roll': row[9],
                'balance_wt': row[10]
            } for row in program
        ]

        sub_po = parent_gf_delivery_table.objects.filter(id__in=out_id, status=1).first()
        po_total_roll = totals['po_roll'] or 0

        # Collect all program details
        program_details = []
        program_seen_keys = set()
 
        for pid in program_id_list:
            knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id, status=1).order_by('dia_id')
            for sub in sub_knits:
                key = (sub.tm_id, sub.dia_id, sub.fabric_id)
                if key in program_seen_keys:
                    continue
                program_seen_keys.add(key)

                fabric_data = []
                fabric_qs = fabric_program_table.objects.filter(id=sub.fabric_id)
                for fp in fabric_qs:
                    fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
                    fabric_data.append({
                        'id': fp.id,
                        'name': fp.name,
                        'fabric_id': fp.fabric_id,
                        'fabric_name': fabric_item.name if fabric_item else 'N/A'
                    })

                dia = dia_table.objects.filter(id=sub.dia_id).first()
                color = color_table.objects.filter(id=sub.color_id).first()

                inward_ids = list(dyed_fabric_inward_table.objects.filter(outward_id__in=out_id, status=1).values_list('id', flat=True))
                inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(tm_id__in=inward_ids, dia_id=sub.dia_id, status=1).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = (sub.roll or 0) - inward_roll_sum
                total_wt_balance = (sub.roll or 0) * (sub.roll_wt or 0)
                inward_quantity = inward_roll_sum * (sub.roll_wt or 0)

                program_details.append({
                    'program_id': sub.tm_id,
                    'program_name': knit.name,
                    'fabric': fabric_data,
                    'fabric_id': sub.fabric_id,
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia_id,
                    'color': color.name if color else '',
                    'color_id': sub.color_id,
                    'lot_roll': remaining_roll,
                    'per_roll_wt': sub.roll_wt,
                    'lot_roll_wt': total_wt_balance - inward_quantity,
                    'out_id': out_id,
                    'total_roll': inward_roll_sum,
                    'total_wt': inward_quantity,
                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id and row['color_id'] == sub.color_id
                    ]
                })


                # Extract fabric_ids from program_details
                fabric_ids = set(
                    detail['fabric_id']
                    for detail in program_details
                    if 'fabric_id' in detail and detail['fabric_id'] is not None
                )

                # Decide what to return for fabric_id
                if len(fabric_ids) == 1:
                    fabric_id_value = next(iter(fabric_ids))  # The only fabric ID
                else:
                    fabric_id_value = None  # or "multiple", as needed

        # ---- ORDER DATA SECTION ----
        order_data = []

        if tm_inward_id:
            print('tm-inward-ids:',tm_inward_id)
            parent_pos = dyed_fabric_inward_table.objects.filter(id=tm_inward_id)
            for po in parent_pos:
                deliveries = sub_dyed_fabric_inward_table.objects.filter(tm_id=tm_inward_id, status=1)

                for delivery in deliveries:
                    programs = dyeing_program_table.objects.filter(id__in=program_qs, is_active=1)
                    for program in programs:
                        sub_knit = sub_dyeing_program_table.objects.filter(tm_id=program.id)
                        if not sub_knit.exists():
                            continue

                        product = fabric_program_table.objects.filter(id=delivery.fabric_id).first()

                        inward_totals = sub_dyed_fabric_inward_table.objects.filter(
                            tm_id=tm_inward_id, is_active=1
                        ).aggregate(
                            inward_roll=Sum('roll'),
                            inward_quantity=Sum('roll_wt'),
                            inward_gross=Sum('gross_wt')
                        )

                        inward_roll = inward_totals.get('inward_roll') or 0
                        inward_quantity = inward_totals.get('inward_quantity') or 0
                        inward_gross = inward_totals.get('inward_gross') or 0

                        remaining_roll_wt = delivery.roll_wt or 0
                        qty = delivery.roll_wt or 0
                        remaining_quantity = delivery.gross_wt or 0

                        # bal_roll = remaining_roll_wt - inward_roll
                        # bal_quantity = qty - inward_quantity

                        # # Skip if no balance left
                        # if bal_roll == 0 and bal_quantity == 0:
                        #     continue

                        order_data.append({
                            'po_roll': delivery.roll or 0,
                            'total_rolls': inward_roll,
                            'po_quantity': remaining_quantity,
                            'inward_roll': inward_roll,
                            'inward_quantity': inward_quantity,
                            'inward_gross_wt': inward_gross,
                            'balance_quantity':0,# bal_quantity,
                            'tax_value': 5,
                            'fabric_id': delivery.fabric_id,
                            'dia': delivery.dia_id,
                            'color': delivery.color_id,
                            'program_id': program.id,
                            'wt_per_roll': sub_po.total_wt if sub_po else 0,
                            'roll': remaining_roll_wt,
                            'per_roll': delivery.roll_wt,
                            'tx_quantity': qty,
                            'gross_wt': 0,
                            'id': program.id,
                            'out_id': po.id,
                            'tm_id': po.id,
                            'tx_id': delivery.id,
                            'total_quantity': qty,
                            'total_gross_wt': delivery.gross_wt or 0,
                            'total_roll': delivery.roll or 0,
                            'product': product.name if product else '',
                        })

        return JsonResponse({
            'orders': list(order_number),
            'po_roll': po_total_roll,
            'balance_wt': 0,
            'po_quantity': float(totals['outward_wt'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0),
            'program_id': program_id_list,
            'gross_wt': sub_po.gross_wt if sub_po else 0,
            'quantity': 0,
            'program': prg_list,
            'order_data': order_data,
            'program_details': program_details,
            'fabric_id':fabric_id_value
        }) 

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)




# @csrf_exempt
# def get_grey_outward_edit_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     # out_id = request.POST.getlist('outward_list[]')  # from AJAX: ['3', '4']

#     out_id_str = request.POST.get('outward_list', '')
#     print('out:',out_id_str)
#     out_id = out_id_str.split(',') if out_id_str else []
#     print('out_id:',out_id)
#     tm_inward_id = request.POST.get('tm_id')         # from AJAX: '15'
#     print('tm-ids:',tm_inward_id)

#     color_ids = [int(x.strip()) for x in request.POST.get('color_id', '').split(',') if x.strip()]
    
#     try:
#         order_data = []
#         program_details = []
#         program_details_inward = []

#         # Get already inwarded outward_ids for this tm_id
#         existing_out_ids = list(
#             dyed_fabric_inward_table.objects.filter(
#                 id=tm_inward_id,
#                 outward_id__in=out_id,
#                 status=1
#             ).values_list('outward_id', flat=True)
#         ) if tm_inward_id else []

#         new_out_ids = list(set(out_id) - set(existing_out_ids))

#         all_out_ids = list(set(out_id)) 
#         print('all-out-id:',all_out_ids)
#         order_number = parent_gf_delivery_table.objects.filter(
#             id__in=all_out_ids, status=1
#         ).values('id', 'do_number', 'lot_no').order_by('-id')

#         totals = grey_out_available_balance_table.objects.filter(
#             out_id__in=new_out_ids
#         ).aggregate(
#             po_roll=Sum('outward_wt'),
#             outward_wt=Sum('outward_wt'),
#             inward_quantity=Sum('inward_wt'),
#             balance_wt=Sum('balance_wt'),
#         )

#         program_id_list = list(
#             grey_out_available_balance_table.objects.filter(
#                 out_id__in=all_out_ids
#             ).values_list('program_id', flat=True).distinct()
#         )
#         print('prgm-id:',program_id_list)




#         # program_qs = grey_fab_program_balance_table.objects.filter(
#         #    program_id__in=program_id_list
#         #     # balance_quantity__gt=0, program_id__in=program_id_list
#         # ).values_list('program_id', flat=True)

#         program_qs = dyeing_program_table.objects.filter(
#            id__in=program_id_list
#             # balance_quantity__gt=0, program_id__in=program_id_list
#         ).values_list('id', flat=True)
#         print('prg-qs:',program_qs)
#         prg_list = list(dyeing_program_table.objects.filter(
#             id__in=program_qs, status=1
#         ).values('id', 'program_no', 'name', 'total_wt'))

#         program_balance_data = list(
#             dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs)
#             .values_list('program_id','dia_id','color_id','pg_roll','pg_wt','in_rolls', 'in_wt','out_rolls', 'out_wt','balance_roll','balance_wt')
#         )
#         print('program_balance_data:',program_balance_data)

#         formatted_data = [
#             {
#                 'program_id': row[0],
#                 'dia_id': row[1],
#                 'color_id': row[2],
#                 'pg_roll': row[3],
#                 'pg_wt': row[4],
#                 'in_rolls': row[5],
#                 'in_wt': row[6],
#                 'out_rolls': row[7],
#                 'out_wt': row[8],
#                 'balance_roll': row[9],
#                 'balance_wt': row[10]
#             }
#             for row in program_balance_data
#         ]
#         print('formatted_data:',formatted_data)
#         for pid in program_id_list:
#             knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
#             print('knit:',knit)
#             if not knit:
#                 continue

#             sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id, status=1)
#             for sub in sub_knits:
#                 products = fabric_program_table.objects.filter(id=sub.fabric_id)
#                 fabric_program_data = []

#                 for fp in products:
#                     try:
#                         fabric_item = fabric_table.objects.get(id=fp.fabric_id)
#                         fabric_program_data.append({
#                             'id': fp.id,
#                             'name': fp.name,
#                             'fabric_id': fp.fabric_id,
#                             'fabric_name': fabric_item.name
#                         })
#                     except fabric_table.DoesNotExist:
#                         fabric_program_data.append({
#                             'id': fp.id,
#                             'name': fp.name,
#                             'fabric_id': fp.fabric_id,
#                             'fabric_name': 'N/A'
#                         })

#                 # gauge = gauge_table.objects.filter(id=sub.gauge).first()
#                 # tex = tex_table.objects.filter(id=sub.tex).first()
#                 dia = dia_table.objects.filter(id=sub.dia_id).first()
#                 color = color_table.objects.filter(id=sub.color_id).first()

#                 inward_ids = list(dyed_fabric_inward_table.objects.filter(
#                     outward_id__in=all_out_ids, id=tm_inward_id, status=1
#                 ).values_list('id', flat=True)) if tm_inward_id else []
        
#                 inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
#                     tm_id__in=inward_ids,
#                     dia_id=sub.dia_id,
#                     color_id=sub.color_id,
#                     status=1
#                 ).aggregate(
#                     total_roll=Sum('roll'),
#                     total_wt=Sum('roll_wt'),
#                     total_gross=Sum('gross_wt')
#                 )

#                 inward_roll = inward_roll_sum['total_roll'] or 0
#                 inward_quantity = inward_roll_sum['total_wt'] or 0

#                 rec_data = sub_dyed_fabric_inward_table.objects.filter(
#                     # outward_id__in=all_out_ids,
#                     tm_id__in=inward_ids,
#                     dia_id=sub.dia_id,
#                     status=1
#                 ).aggregate(
#                     total_roll=Sum('roll'),
#                     total_wt=Sum('roll_wt'),
#                     total_gross=Sum('gross_wt')
#                 )

#                 rec_roll = rec_data['total_roll'] or 0
#                 rec_inward_quantity = rec_data['total_wt'] or 0

#                 program_details.append({
#                     'program_id': sub.tm_id,
#                     'fabric': fabric_program_data,
#                     'fabric_id': sub.fabric_id,
              
#                     'dia': dia.name if dia else '',
#                     'dia_id': sub.dia_id,

#                     'color': color.name if color else '',
#                     'color_id': sub.color_id,
#                     'program_roll': sub.roll,
#                     'program_roll_wt': sub.roll_wt,
#                     'per_roll_wt': sub.roll_wt,
#                     'remaining_roll': rec_roll,
#                     'remaining_roll_wt': rec_inward_quantity,
#                     'out_id': all_out_ids,
#                     'total_roll': inward_roll,
#                     'total_inward_wt': inward_quantity,
#                     'program_total_wt': sub.roll_wt, #sub.rolls * sub.roll_wt,
#                     'inward_roll': inward_roll,
#                     'inward_roll_wt': inward_quantity,
#                     'program_bal_value': [
#                         row for row in formatted_data
#                         if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id  and row['color_id'] == sub.color_id
#                     ]
#                 })

#                 # Extract fabric_ids from program_details
#                 fabric_ids = set(
#                     detail['fabric_id']
#                     for detail in program_details
#                     if 'fabric_id' in detail and detail['fabric_id'] is not None
#                 )

#                 # Decide what to return for fabric_id
#                 if len(fabric_ids) == 1:
#                     fabric_id_value = next(iter(fabric_ids))  # The only fabric ID
#                 else:
#                     fabric_id_value = None  # or "multiple", as needed



#         if tm_inward_id:
#             print('tm-inw-id:',tm_inward_id)
#             inward_ids = dyed_fabric_inward_table.objects.filter(
#                 # outward_id__in=all_out_ids,
#                 id=tm_inward_id,
#                 status=1
#             ).values_list('id', flat=True)
#             print('inw:',inward_ids)
#             dia_wise = sub_dyed_fabric_inward_table.objects.filter(
#                 tm_id__in=inward_ids,color_id__in = color_ids,
#                 status=1
#             ).values('fabric_id', 'dia_id','color_id').annotate(
#                 total_roll=Sum('roll'),
#                 total_quantity=Sum('roll_wt'),
#                 gross_wt=Sum('gross_wt')
#             )

#             print('dia-wise:',dia_wise)
#             for item in dia_wise:
#                 fabric_name = fabric_table.objects.filter(id=item['fabric_id']).first()
#                 dia_name = dia_table.objects.filter(id=item['dia_id']).first()
#                 color_name = color_table.objects.filter(id=item['color_id']).first()

#                 rec_data = sub_dyed_fabric_inward_table.objects.filter(
#                     # outward_id__in=all_out_ids,
#                     dia_id=item['dia_id'],
#                     color_id=item['color_id'],
#                     status=1
#                 ).aggregate(
#                     total_roll=Sum('roll'),
#                     total_wt=Sum('roll_wt'),
#                     total_gross=Sum('gross_wt') 
#                 )

#                 rec_roll = rec_data['total_roll'] or 0
#                 rec_inward_quantity = rec_data['total_wt'] or 0

#                 order_data.append({ 
#                     'fabric_id': item['fabric_id'],
#                     # 'out_id':item['outward_id'],
#                     'fabric_name': fabric_name.name if fabric_name else 'N/A',
#                     'dia_id': item['dia_id'],
#                     'color_id': item['color_id'],
#                     'dia': dia_name.name if dia_name else 'N/A',
#                     'color': color_name.name if color_name else 'N/A',
#                     'po_roll': float(item['total_roll'] or 0),
#                     'inward_roll': float(item['total_roll'] or 0),
#                     'total_quantity': float(item['total_quantity'] or 0),
#                     'inward_roll_wt': float(item['total_quantity'] or 0),
#                     'gross_wt': float(item['gross_wt'] or 0),
#                     'remaining_roll': rec_roll,
#                     'remaining_roll_wt': rec_inward_quantity,
#                     'already_rec_roll': rec_roll - (item['total_roll'] or 0),
#                     'already_rec_wt': rec_inward_quantity - (item['total_quantity'] or 0),
#                 })

#                 for pid in program_id_list:
#                     knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
#                     print('knit:',knit)
#                     if not knit:
#                         continue

#                     sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id, status=1)
#                     for sub in sub_knits:
#                         products = fabric_program_table.objects.filter(id=sub.fabric_id)
#                         fabric_program_data = []

#                         for fp in products:
#                             try:
#                                 fabric_item = fabric_table.objects.get(id=fp.fabric_id)
#                                 fabric_program_data.append({
#                                     'id': fp.id,
#                                     'name': fp.name,
#                                     'fabric_id': fp.fabric_id,
#                                     'fabric_name': fabric_item.name
#                                 })
#                             except fabric_table.DoesNotExist:
#                                 fabric_program_data.append({
#                                     'id': fp.id,
#                                     'name': fp.name,
#                                     'fabric_id': fp.fabric_id,
#                                     'fabric_name': 'N/A'
#                                 })

#                         # gauge = gauge_table.objects.filter(id=sub.gauge).first()
#                         # tex = tex_table.objects.filter(id=sub.tex).first()
#                         dia = dia_table.objects.filter(id=sub.dia_id).first()
#                         color = color_table.objects.filter(id=sub.color_id).first()

#                         inward_ids = list(dyed_fabric_inward_table.objects.filter(
#                             outward_id__in=all_out_ids, id=tm_inward_id, status=1
#                         ).values_list('id', flat=True)) if tm_inward_id else []
                
#                         inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
#                             tm_id__in=inward_ids,
#                             dia_id=sub.dia_id,
#                             color_id=sub.color_id,
#                             status=1
#                         ).aggregate(
#                             total_roll=Sum('roll'),
#                             total_wt=Sum('roll_wt'),
#                             total_gross=Sum('gross_wt')
#                         )

#                         inward_roll = inward_roll_sum['total_roll'] or 0
#                         inward_quantity = inward_roll_sum['total_wt'] or 0

#                         rec_data = sub_dyed_fabric_inward_table.objects.filter(
#                             # outward_id__in=all_out_ids,
#                             tm_id__in=inward_ids,
#                             dia_id=sub.dia_id,
#                             status=1
#                         ).aggregate(
#                             total_roll=Sum('roll'),
#                             total_wt=Sum('roll_wt'),
#                             total_gross=Sum('gross_wt')
#                         )

#                         rec_roll = rec_data['total_roll'] or 0
#                         rec_inward_quantity = rec_data['total_wt'] or 0

#                         program_details_inward.append({
#                             'program_id': sub.tm_id,
#                             'fabric': fabric_program_data,
#                             'fabric_id': sub.fabric_id,
                    
#                             'dia': dia.name if dia else '',
#                             'dia_id': sub.dia_id,

#                             'color': color.name if color else '',
#                             'color_id': sub.color_id,
#                             'program_roll': sub.roll,
#                             'program_roll_wt': sub.roll_wt,
#                             'per_roll_wt': sub.roll_wt,
#                             'remaining_roll': rec_roll,
#                             'remaining_roll_wt': rec_inward_quantity,
#                             'out_id': all_out_ids,
#                             'total_roll': inward_roll,
#                             'total_inward_wt': inward_quantity,
#                             'program_total_wt': sub.roll_wt, #sub.rolls * sub.roll_wt,
#                             'inward_roll': inward_roll,
#                             'inward_roll_wt': inward_quantity,
#                             'program_bal_value': [
#                                 row for row in formatted_data
#                                 if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id  and row['color_id'] == sub.color_id
#                             ]
#                         })




#         return JsonResponse({
#             "order_numbers": list(order_number),
#             "totals": totals,
#             "programs": prg_list,
#             "program_details": program_details,
#             "order_data": order_data,
#             'fabric_id':fabric_id_value,
#             'program_details_inward':program_details_inward,
#         }, safe=False)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


from django.db.models import Sum, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q, Sum

@csrf_exempt
def get_grey_outward_edit_lists(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    out_id = request.POST.get('outward_list', '').split(',') if request.POST.get('outward_list') else []
    tm_inward_id = request.POST.get('tm_id')
    color_ids = [int(x.strip()) for x in request.POST.get('color_id', '').split(',') if x.strip()]
    out_id = [int(x) for x in out_id if x.strip()]

    print('colors:', color_ids)

    # Convert tm_id to int
    tm_inward_id = int(tm_inward_id) if tm_inward_id else None

    # Step 1: Fallback resolution
    if not tm_inward_id and out_id and color_ids:
        fallback = dyed_fabric_inward_table.objects.filter(
            outward_id__in=out_id,
            status=1,
            sub_dyed_fabric_inward__color_id__in=color_ids
        ).distinct().first()
        tm_inward_id = fallback.id if fallback else None

    order_data = []
    program_details = []
    program_details_inward = []
    fabric_id_value = None

    # Get new outward_ids to process
    new_out_ids = list(set(out_id) - set(
        dyed_fabric_inward_table.objects.filter(
            id=tm_inward_id, outward_id__in=out_id, status=1
        ).values_list('outward_id', flat=True)
    )) if tm_inward_id else out_id

    all_out_ids = list(set(out_id))

    # Header-level info
    order_number = parent_gf_delivery_table.objects.filter(id__in=all_out_ids, status=1) \
        .values('id', 'do_number', 'lot_no').order_by('-id')

    totals = grey_out_available_balance_table.objects.filter(out_id__in=new_out_ids).aggregate(
        po_roll=Sum('outward_wt'),
        outward_wt=Sum('outward_wt'),
        inward_quantity=Sum('inward_wt'),
        balance_wt=Sum('balance_wt'),
    )

    program_id_list = list(grey_out_available_balance_table.objects
                           .filter(out_id__in=all_out_ids)
                           .values_list('program_id', flat=True).distinct())

    program_qs = list(dyeing_program_table.objects.filter(id__in=program_id_list)
                      .values_list('id', flat=True))

    prg_list = list(dyeing_program_table.objects.filter(id__in=program_qs, status=1)
                    .values('id', 'program_no', 'name', 'total_wt'))

    formatted_data = [
        dict(zip(
            ['program_id', 'dia_id', 'color_id', 'pg_roll', 'pg_wt',
             'in_rolls', 'in_wt', 'out_rolls', 'out_wt', 'balance_roll', 'balance_wt'],
            row
        ))
        for row in dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs)
        .values_list('program_id', 'dia_id', 'color_id',
                     'pg_roll', 'pg_wt', 'in_rolls', 'in_wt',
                     'out_rolls', 'out_wt', 'balance_roll', 'balance_wt')
    ]

    # Filtered inward_ids for tm_id and color_ids
    inward_ids = list(
        dyed_fabric_inward_table.objects.filter(
            id=tm_inward_id,
            # sub_dyed_fabric_inward__color_id__in=color_ids,
            status=1
        ).values_list('id', flat=True).distinct()
    )

    # Common inward filter
    inward_filter = Q(status=1, tm_id=tm_inward_id, color_id__in=color_ids)

    all_fabric_ids = set()

    for pid in program_id_list:
        if not dyeing_program_table.objects.filter(id=pid, is_active=1).exists():
            continue

        for sub in sub_dyeing_program_table.objects.filter(tm_id=pid, status=1):
            dia = dia_table.objects.filter(id=sub.dia_id).first()
            color = color_table.objects.filter(id=sub.color_id).first()

            sums = sub_dyed_fabric_inward_table.objects.filter(
                inward_filter,
                dia_id=sub.dia_id,
                color_id=sub.color_id
            ).aggregate(total_roll=Sum('roll'), total_wt=Sum('roll_wt'))

            inward_roll = sums['total_roll'] or 0
            inward_wt = sums['total_wt'] or 0

            fabric_entries = []
            for fp in fabric_program_table.objects.filter(id=sub.fabric_id):
                try:
                    fi = fabric_table.objects.get(id=fp.fabric_id)
                    fabric_entries.append({
                        'id': fp.id, 'name': fp.name,
                        'fabric_id': fp.fabric_id, 'fabric_name': fi.name
                    })
                except fabric_table.DoesNotExist:
                    fabric_entries.append({
                        'id': fp.id, 'name': fp.name,
                        'fabric_id': fp.fabric_id, 'fabric_name': 'N/A'
                    })

            all_fabric_ids.update([e['fabric_id'] for e in fabric_entries])

            program_details.append({
                'program_id': pid, 'fabric': fabric_entries, 'fabric_id': sub.fabric_id,
                'dia': dia.name if dia else '', 'dia_id': sub.dia_id,
                'color': color.name if color else '', 'color_id': sub.color_id,
                'program_roll': sub.roll, 'program_roll_wt': sub.roll_wt,
                'per_roll_wt': sub.roll_wt, 'remaining_roll': inward_roll,
                'remaining_roll_wt': inward_wt, 'out_id': all_out_ids,
                'total_roll': inward_roll, 'total_inward_wt': inward_wt,
                'program_total_wt': sub.roll_wt,
                'inward_roll': inward_roll, 'inward_roll_wt': inward_wt,
                'program_bal_value': [
                    row for row in formatted_data
                    if row['program_id'] == pid and
                    row['dia_id'] == sub.dia_id and
                    row['color_id'] == sub.color_id
                ]
            })

    # Unique fabric
    if len(all_fabric_ids) == 1:
        fabric_id_value = next(iter(all_fabric_ids))

    # Order data for selected tm_id + color_ids
    if tm_inward_id:
        dia_wise = sub_dyed_fabric_inward_table.objects.filter(
            tm_id=tm_inward_id, color_id__in=color_ids, status=1
        ).values('fabric_id', 'dia_id', 'color_id').annotate(
            total_roll=Sum('roll'), total_quantity=Sum('roll_wt'),
            gross_wt=Sum('gross_wt')
        )

        for item in dia_wise:
            rec = sub_dyed_fabric_inward_table.objects.filter(
                dia_id=item['dia_id'], color_id=item['color_id'], status=1
            ).aggregate(total_roll=Sum('roll'), total_wt=Sum('roll_wt'))

            rec_roll = rec['total_roll'] or 0
            rec_wt = rec['total_wt'] or 0

            for pid in program_id_list:
                if not dyeing_program_table.objects.filter(id=pid, is_active=1):
                    continue

                fabric_name = fabric_program_table.objects.filter(id=item['fabric_id']).first()
                order_data.append({
                    'fabric_id': item['fabric_id'],
                    'fabric_name': fabric_name.name if fabric_name else '',
                    'dia_id': item['dia_id'], 'color_id': item['color_id'],
                    'dia': dia_table.objects.filter(id=item['dia_id']).first().name,
                    'color': color_table.objects.filter(id=item['color_id']).first().name,
                    'po_roll': float(item['total_roll'] or 0),
                    'inward_roll': float(item['total_roll'] or 0),
                    'total_quantity': float(item['total_quantity'] or 0),
                    'inward_roll_wt': float(item['total_quantity'] or 0),
                    'gross_wt': float(item['gross_wt'] or 0),
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_wt,
                    'already_rec_roll': rec_roll - (item['total_roll'] or 0),
                    'already_rec_wt': rec_wt - (item['total_quantity'] or 0),
                })

    return JsonResponse({
        "order_numbers": list(order_number),
        "totals": totals,
        "programs": prg_list,
        "program_details": program_details,
        "order_data": order_data,
        "fabric_id": fabric_id_value,
        "program_details_inward": program_details_inward,
    }, safe=False)



@csrf_exempt
def get_grey_outward_edit_lists_test1625(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    out_id = request.POST.get('outward_list', '').split(',') if request.POST.get('outward_list') else []
    tm_inward_id = request.POST.get('tm_id')
    # color_ids = [int(x.strip()) for x in request.POST.get('color_id[]', '').split(',') if x.strip()]
    color_ids = [int(x.strip()) for x in request.POST.get('color_id', '').split(',') if x.strip()]
    print('colors:',color_ids)
    # Step 1: Fallback resolution of tm_inward_id by color and outward list
    if not tm_inward_id and out_id and color_ids:
        fallback = dyed_fabric_inward_table.objects.filter(
            outward_id__in=out_id,
            status=1,
            sub_dyed_fabric_inward__color_id__in=color_ids
        ).distinct().first()
        tm_inward_id = fallback.id if fallback else None

    order_data = []
    program_details = []
    program_details_inward = []
    fabric_id_value = None  # Always define upfront

    new_out_ids = list(set(out_id) - set(
        dyed_fabric_inward_table.objects.filter(
            id=tm_inward_id, outward_id__in=out_id, status=1
        ).values_list('outward_id', flat=True)
    )) if tm_inward_id else out_id

    all_out_ids = list(set(out_id))

    # Header-level aggregations
    order_number = parent_gf_delivery_table.objects.filter(id__in=all_out_ids, status=1) \
        .values('id', 'do_number', 'lot_no').order_by('-id')
    totals = grey_out_available_balance_table.objects.filter(out_id__in=new_out_ids).aggregate(
        po_roll=Sum('outward_wt'),
        outward_wt=Sum('outward_wt'),
        inward_quantity=Sum('inward_wt'),
        balance_wt=Sum('balance_wt'),
    )
    program_id_list = list(grey_out_available_balance_table.objects
                           .filter(out_id__in=all_out_ids).values_list('program_id', flat=True).distinct())
    program_qs = list(dyeing_program_table.objects.filter(id__in=program_id_list).values_list('id', flat=True))
    prg_list = list(dyeing_program_table.objects.filter(id__in=program_qs, status=1)
                    .values('id', 'program_no', 'name', 'total_wt'))
    formatted_data = [
        dict(zip(
            ['program_id','dia_id','color_id','pg_roll','pg_wt',
             'in_rolls','in_wt','out_rolls','out_wt','balance_roll','balance_wt'],
            row
        ))
        for row in dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs)
                                   .values_list('program_id','dia_id','color_id',
                                                'pg_roll','pg_wt','in_rolls','in_wt',
                                                'out_rolls','out_wt','balance_roll','balance_wt')
    ]

    # Step 2: Build program_details and accumulate fabric_ids
    all_fabric_ids = set()
    inward_filter = Q(status=1)
    if tm_inward_id:
        inward_filter &= (Q(tm_id__in=tm_inward_id) )
                        #   | Q(outward_id__in=all_out_ids))
    if color_ids:
        inward_filter &= Q(color_id__in=color_ids)

    inward_ids = list(dyed_fabric_inward_table.objects.filter(status=1,id=tm_inward_id)
                                                            #   outward_id=out_id)
                      .values_list('id', flat=True).distinct())
    
    
    # inward_ids = dyed_fabric_inward_table.objects.filter(
    #     outward_id__in=out_id, status=1,
    #     # sub_dyed_fabric_inward__color_id__in=color_ids 
    # ).values_list('id', flat=True).distinct()

    for pid in program_id_list:
        if not dyeing_program_table.objects.filter(id=pid, is_active=1).exists():
            continue

        for sub in sub_dyeing_program_table.objects.filter(tm_id=pid, status=1):
            dia = dia_table.objects.filter(id=sub.dia_id).first()
            color = color_table.objects.filter(id=sub.color_id).first()

            sums = sub_dyed_fabric_inward_table.objects.filter(inward_filter
                # tm_id__in=inward_ids, dia_id=sub.dia_id, color_id=sub.color_id, status=1,
            ).aggregate(total_roll=Sum('roll'), total_wt=Sum('roll_wt'))
            inward_roll = sums['total_roll'] or 0
            inward_wt = sums['total_wt'] or 0

            fabric_entries = []
            for fp in fabric_program_table.objects.filter(id=sub.fabric_id):
                try:
                    fi = fabric_table.objects.get(id=fp.fabric_id)
                    fabric_entries.append({
                        'id': fp.id, 'name': fp.name,
                        'fabric_id': fp.fabric_id, 'fabric_name': fi.name
                    })
                except fabric_table.DoesNotExist:
                    fabric_entries.append({
                        'id': fp.id, 'name': fp.name,
                        'fabric_id': fp.fabric_id, 'fabric_name': 'N/A'
                    })
            all_fabric_ids.update([e['fabric_id'] for e in fabric_entries])

            program_details.append({
                'program_id': pid, 'fabric': fabric_entries, 'fabric_id': sub.fabric_id,
                'dia': dia.name if dia else '', 'dia_id': sub.dia_id,
                'color': color.name if color else '', 'color_id': sub.color_id,
                'program_roll': sub.roll, 'program_roll_wt': sub.roll_wt,
                'per_roll_wt': sub.roll_wt, 'remaining_roll': inward_roll,
                'remaining_roll_wt': inward_wt, 'out_id': all_out_ids,
                'total_roll': inward_roll, 'total_inward_wt': inward_wt,
                'program_total_wt': sub.roll_wt,
                'inward_roll': inward_roll, 'inward_roll_wt': inward_wt,
                'program_bal_value': [
                    row for row in formatted_data
                    if row['program_id'] == pid and
                       row['dia_id'] == sub.dia_id and
                       row['color_id'] == sub.color_id
                ]
            })

    # Step 3: Set fabric_id_value if unique
    if len(all_fabric_ids) == 1:
        fabric_id_value = next(iter(all_fabric_ids))

    # Step 4: Build order_data if tm_inward_id present
    if tm_inward_id:
        dia_wise = sub_dyed_fabric_inward_table.objects.filter(
            tm_id__in=inward_ids, color_id__in=color_ids, status=1
        ).values('fabric_id', 'dia_id', 'color_id').annotate(
            total_roll=Sum('roll'), total_quantity=Sum('roll_wt'),
            gross_wt=Sum('gross_wt')
        )
        for item in dia_wise:
            rec = sub_dyed_fabric_inward_table.objects.filter(
                dia_id=item['dia_id'], color_id=item['color_id'], status=1
            ).aggregate(total_roll=Sum('roll'), total_wt=Sum('roll_wt'))
            rec_roll = rec['total_roll'] or 0
            rec_wt = rec['total_wt'] or 0

            for pid in program_id_list:
                if not dyeing_program_table.objects.filter(id=pid, is_active=1):
                    continue
                # Aggregated order_data entry
                order_data.append({
                    'fabric_id': item['fabric_id'],
                    'fabric_name': fabric_program_table.objects.filter(id=item['fabric_id'])
                                        .first().name,
                    'dia_id': item['dia_id'], 'color_id': item['color_id'],
                    'dia': dia_table.objects.filter(id=item['dia_id'])
                                    .first().name,
                    'color': color_table.objects.filter(id=item['color_id'])
                                      .first().name,
                    'po_roll': float(item['total_roll'] or 0),
                    'inward_roll': float(item['total_roll'] or 0),
                    'total_quantity': float(item['total_quantity'] or 0),
                    'inward_roll_wt': float(item['total_quantity'] or 0),
                    'gross_wt': float(item['gross_wt'] or 0),
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_wt,
                    'already_rec_roll': rec_roll - (item['total_roll'] or 0),
                    'already_rec_wt': rec_wt - (item['total_quantity'] or 0),
                })

    return JsonResponse({
        "order_numbers": list(order_number),
        "totals": totals,
        "programs": prg_list,
        "program_details": program_details,
        "order_data": order_data,
        "fabric_id": fabric_id_value,
        "program_details_inward": program_details_inward,
    }, safe=False)


@csrf_exempt
def get_grey_outward_edit_lists_test(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # out_id = request.POST.getlist('outward_list[]')  # from AJAX: ['3', '4']

    out_id_str = request.POST.get('outward_list', '')
    print('out:',out_id_str)
    out_id = out_id_str.split(',') if out_id_str else []
    print('out_id:',out_id)
    tm_inward_id = request.POST.get('tm_id')         # from AJAX: '15'
    print('tm-ids:',tm_inward_id)
    color_ids = [int(x.strip()) for x in request.POST.get('color_id', '').split(',') if x.strip()]

    try:
        order_data = []
        program_details = []
        program_details_inward = []

        # Get already inwarded outward_ids for this tm_id
        existing_out_ids = list(
            dyed_fabric_inward_table.objects.filter(
                id=tm_inward_id,
                outward_id__in=out_id,
                status=1
            ).values_list('outward_id', flat=True)
        ) if tm_inward_id else []

        new_out_ids = list(set(out_id) - set(existing_out_ids))

        all_out_ids = list(set(out_id)) 
        print('all-out-id:',all_out_ids)
        order_number = parent_gf_delivery_table.objects.filter(
            id__in=all_out_ids, status=1
        ).values('id', 'do_number', 'lot_no').order_by('-id')

        totals = grey_out_available_balance_table.objects.filter(
            out_id__in=new_out_ids
        ).aggregate(
            po_roll=Sum('outward_wt'),
            outward_wt=Sum('outward_wt'),
            inward_quantity=Sum('inward_wt'),
            balance_wt=Sum('balance_wt'),
        )

        program_id_list = list(
            grey_out_available_balance_table.objects.filter(
                out_id__in=all_out_ids
            ).values_list('program_id', flat=True).distinct()
        )
        print('prgm-id:',program_id_list)




        # program_qs = grey_fab_program_balance_table.objects.filter(
        #    program_id__in=program_id_list
        #     # balance_quantity__gt=0, program_id__in=program_id_list
        # ).values_list('program_id', flat=True)

        program_qs = dyeing_program_table.objects.filter(
           id__in=program_id_list
            # balance_quantity__gt=0, program_id__in=program_id_list
        ).values_list('id', flat=True)
        print('prg-qs:',program_qs)
        prg_list = list(dyeing_program_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'program_no', 'name', 'total_wt'))

        program_balance_data = list(
            dyed_fab_inw_available_wt_table.objects.filter(program_id__in=program_qs,color_id__in=color_ids)
            .values_list('program_id','dia_id','color_id','pg_roll','pg_wt','in_rolls', 'in_wt','out_rolls', 'out_wt','balance_roll','balance_wt')
        )
        print('program_balance_data:',program_balance_data)

        formatted_data = [
            {
                'program_id': row[0],
                'dia_id': row[1],
                'color_id': row[2],
                'pg_roll': row[3],
                'pg_wt': row[4],
                'in_rolls': row[5],
                'in_wt': row[6],
                'out_rolls': row[7],
                'out_wt': row[8],
                'balance_roll': row[9],
                'balance_wt': row[10]
            }
            for row in program_balance_data
        ]
        print('formatted_data:',formatted_data)

        program_seen_keys = set()
        fabric_id_value = None  # 🔧 Add this line

        for pid in program_id_list:
            knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
            print('knit:',knit)
            if not knit:
                continue

            # sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id, status=1)
            sub_knits = sub_dyeing_program_table.objects.filter(
                tm_id=knit.id, color_id__in=color_ids, status=1
            ).order_by('dia_id')


            for sub in sub_knits:

                key = (sub.tm_id, sub.dia_id, sub.fabric_id, sub.color_id)
                if key in program_seen_keys:
                    continue
                program_seen_keys.add(key)



                fabric_qs = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_data = []
                for fp in fabric_qs:
                    fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
                    fabric_data.append({
                        'id': fp.id,
                        'name': fp.name,
                        'fabric_id': fp.fabric_id,
                        'fabric_name': fabric_item.name if fabric_item else 'N/A'
                    })

                dia = dia_table.objects.filter(id=sub.dia_id).first()
                color = color_table.objects.filter(id=sub.color_id).first()

                inward_ids = dyed_fabric_inward_table.objects.filter(
                    outward_id__in=out_id, status=1
                ).values_list('id', flat=True)

                inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
                    tm_id__in=inward_ids, dia_id=sub.dia_id, status=1
                ).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = (sub.roll or 0) - inward_roll_sum
                total_wt_balance = (sub.roll or 0) * (sub.roll_wt or 0)
                inward_quantity = inward_roll_sum * (sub.roll_wt or 0)


                products = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_program_data = []

                for fp in products:
                    try:
                        fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                        fabric_program_data.append({
                            'id': fp.id,
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': fabric_item.name
                        })
                    except fabric_table.DoesNotExist:
                        fabric_program_data.append({
                            'id': fp.id,
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': 'N/A'
                        })

                # gauge = gauge_table.objects.filter(id=sub.gauge).first()
                # tex = tex_table.objects.filter(id=sub.tex).first()
                dia = dia_table.objects.filter(id=sub.dia_id).first()
                color = color_table.objects.filter(id=sub.color_id).first()

                inward_ids = list(dyed_fabric_inward_table.objects.filter(
                    outward_id__in=all_out_ids, id=tm_inward_id, status=1
                ).values_list('id', flat=True)) if tm_inward_id else []
        
                inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia_id,
                    color_id=sub.color_id,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('roll_wt'),
                    total_gross=Sum('gross_wt')
                )

                inward_roll = inward_roll_sum['total_roll'] or 0
                inward_quantity = inward_roll_sum['total_wt'] or 0

                rec_data = sub_dyed_fabric_inward_table.objects.filter(
                    # outward_id__in=all_out_ids,
                    tm_id__in=inward_ids,
                    dia_id=sub.dia_id,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('roll_wt'),
                    total_gross=Sum('gross_wt')
                )

                rec_roll = rec_data['total_roll'] or 0
                rec_inward_quantity = rec_data['total_wt'] or 0

                program_details.append({
                    'program_id': sub.tm_id,
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
              
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia_id,

                    'color': color.name if color else '',
                    'color_id': sub.color_id,
                    'program_roll': sub.roll,
                    'program_roll_wt': sub.roll_wt,
                    'per_roll_wt': sub.roll_wt,
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_inward_quantity,
                    'out_id': all_out_ids,
                    'total_roll': inward_roll,
                    'total_inward_wt': inward_quantity,
                    'program_total_wt': sub.roll_wt, #sub.rolls * sub.roll_wt,
                    'inward_roll': inward_roll,
                    'inward_roll_wt': inward_quantity,
                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id  and row['color_id'] == sub.color_id
                    ]
                })

                # Extract fabric_ids from program_details
                # fabric_ids = set(
                #     detail['fabric_id']
                #     for detail in program_details
                #     if 'fabric_id' in detail and detail['fabric_id'] is not None
                # )

                # # Decide what to return for fabric_id
                # if len(fabric_ids) == 1:
                #     fabric_id_value = next(iter(fabric_ids))  # The only fabric ID
                # else:
                #     fabric_id_value = None  # or "multiple", as needed

                 # ✅ Group by color and dia
                color_grouped_details = defaultdict(lambda: defaultdict(list))
                for detail in program_details:
                    color_grouped_details[detail['color_id']][detail['dia_id']].append(detail)

                # Convert to JSON-serializable dict
                final_color_grouped = {
                    color: dict(dias) for color, dias in color_grouped_details.items()
                }

                sub_po = parent_gf_delivery_table.objects.filter(id__in=out_ids, status=1).first()
                fabric_ids = {detail['fabric_id'] for detail in program_details if detail.get('fabric_id')}

                fabric_id_value = next(iter(fabric_ids)) if len(fabric_ids) == 1 else None

                

        if tm_inward_id:
            print('tm-inw-id:',tm_inward_id)
            inward_ids = dyed_fabric_inward_table.objects.filter(
                # outward_id__in=all_out_ids,
                id=tm_inward_id,
                status=1
            ).values_list('id', flat=True)
            print('inw:',inward_ids)
            dia_wise = sub_dyed_fabric_inward_table.objects.filter(
                tm_id__in=inward_ids,color_id__in=color_ids, 
                status=1
            ).values('fabric_id', 'dia_id','color_id').annotate(
                total_roll=Sum('roll'),
                total_quantity=Sum('roll_wt'),
                gross_wt=Sum('gross_wt')
            )

            print('dia-wise:',dia_wise)
            for item in dia_wise:
                fabric_name = fabric_table.objects.filter(id=item['fabric_id']).first()
                dia_name = dia_table.objects.filter(id=item['dia_id']).first()
                color_name = color_table.objects.filter(id=item['color_id']).first()

                rec_data = sub_dyed_fabric_inward_table.objects.filter(
                    # outward_id__in=all_out_ids,
                    dia_id=item['dia_id'],
                    color_id=item['color_id'],
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('roll_wt'),
                    total_gross=Sum('gross_wt')
                )

                rec_roll = rec_data['total_roll'] or 0
                rec_inward_quantity = rec_data['total_wt'] or 0

                order_data.append({ 
                    'fabric_id': item['fabric_id'],
                    # 'out_id':item['outward_id'],
                    'fabric_name': fabric_name.name if fabric_name else 'N/A',
                    'dia_id': item['dia_id'],
                    'color_id': item['color_id'],
                    'dia': dia_name.name if dia_name else 'N/A',
                    'color': color_name.name if color_name else 'N/A',
                    'po_roll': float(item['total_roll'] or 0),
                    'inward_roll': float(item['total_roll'] or 0),
                    'total_quantity': float(item['total_quantity'] or 0),
                    'inward_roll_wt': float(item['total_quantity'] or 0),
                    'gross_wt': float(item['gross_wt'] or 0),
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_inward_quantity,
                    'already_rec_roll': rec_roll - (item['total_roll'] or 0),
                    'already_rec_wt': rec_inward_quantity - (item['total_quantity'] or 0),
                })

                for pid in program_id_list:
                    knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
                    print('knit:',knit)
                    if not knit:
                        continue

                    sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id, status=1)
                    for sub in sub_knits:
                        products = fabric_program_table.objects.filter(id=sub.fabric_id)
                        fabric_program_data = []

                        for fp in products:
                            try:
                                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                                fabric_program_data.append({
                                    'id': fp.id,
                                    'name': fp.name,
                                    'fabric_id': fp.fabric_id,
                                    'fabric_name': fabric_item.name
                                })
                            except fabric_table.DoesNotExist:
                                fabric_program_data.append({
                                    'id': fp.id,
                                    'name': fp.name,
                                    'fabric_id': fp.fabric_id,
                                    'fabric_name': 'N/A'
                                })

                        # gauge = gauge_table.objects.filter(id=sub.gauge).first()
                        # tex = tex_table.objects.filter(id=sub.tex).first()
                        dia = dia_table.objects.filter(id=sub.dia_id).first()
                        color = color_table.objects.filter(id=sub.color_id).first()

                        inward_ids = list(dyed_fabric_inward_table.objects.filter(
                            outward_id__in=all_out_ids, id=tm_inward_id, status=1
                        ).values_list('id', flat=True)) if tm_inward_id else []
                
                        inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
                            tm_id__in=inward_ids,
                            dia_id=sub.dia_id,
                            color_id=sub.color_id,
                            status=1
                        ).aggregate(
                            total_roll=Sum('roll'),
                            total_wt=Sum('roll_wt'),
                            total_gross=Sum('gross_wt')
                        )

                        inward_roll = inward_roll_sum['total_roll'] or 0
                        inward_quantity = inward_roll_sum['total_wt'] or 0

                        rec_data = sub_dyed_fabric_inward_table.objects.filter(
                            # outward_id__in=all_out_ids,
                            tm_id__in=inward_ids,
                            dia_id=sub.dia_id,
                            status=1
                        ).aggregate(
                            total_roll=Sum('roll'),
                            total_wt=Sum('roll_wt'),
                            total_gross=Sum('gross_wt')
                        )

                        rec_roll = rec_data['total_roll'] or 0
                        rec_inward_quantity = rec_data['total_wt'] or 0

                        program_details_inward.append({
                            'program_id': sub.tm_id,
                            'fabric': fabric_program_data,
                            'fabric_id': sub.fabric_id,
                    
                            'dia': dia.name if dia else '',
                            'dia_id': sub.dia_id,

                            'color': color.name if color else '',
                            'color_id': sub.color_id,
                            'program_roll': sub.roll,
                            'program_roll_wt': sub.roll_wt,
                            'per_roll_wt': sub.roll_wt,
                            'remaining_roll': rec_roll,
                            'remaining_roll_wt': rec_inward_quantity,
                            'out_id': all_out_ids,
                            'total_roll': inward_roll,
                            'total_inward_wt': inward_quantity,
                            'program_total_wt': sub.roll_wt, #sub.rolls * sub.roll_wt,
                            'inward_roll': inward_roll,
                            'inward_roll_wt': inward_quantity,
                            'program_bal_value': [
                                row for row in formatted_data
                                if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id  and row['color_id'] == sub.color_id
                            ]
                        })




        return JsonResponse({
            "order_numbers": list(order_number),
            "totals": totals,
            "programs": prg_list,
            "program_details": program_details,
            "order_data": order_data,
            'fabric_id':fabric_id_value,
            'program_details_inward':program_details_inward,
        }, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





# `````````````````````````` ajax reports ``````````````````````````````````


def dyed_fabric_inward_ajax_report(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)


    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    dye_prg = request.POST.get('dye_prg', '')
    lot_no = request.POST.get('lot_no', '') 
    # yarn_count = request.POST.get('yarn_count', '')
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

    if dye_prg:
            query &= Q(program_id=dye_prg)

    if lot_no:
            query &= Q(lot_no=lot_no)



    # Apply filters
    queryset = dyed_fabric_inward_table.objects.filter(status=1)
    # queryset = dyed_fabric_inward_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())


    print('data:',data)

    # data = list(dyed_fabric_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = []

    for index, item in enumerate(data):
        # Fetch the child PO for each parent PO
        child_po = dyed_fabric_inward_table.objects.filter(id=item['id'], status=1)

        # Fetch child PO data with related lookups to optimize database queries
        child_data = sub_dyed_fabric_inward_table.objects.filter(tm_id=item['id'], status=1, is_active=1).select_related(
            'fabric_id', 'dia_id','color_id'
        )    
        if child_data.exists():
                    # Aggregate child data totals
            total_rolls = child_data.aggregate(Sum('roll'))['roll__sum'] or 0
            total_gross_wt = child_data.aggregate(Sum('gross_wt'))['gross_wt__sum'] or 0

        # if child_po:  # Ensure child_po is not None
        #     yarn = child_po.yarn_count_id
        # else:
        #     yarn = None  # If no child PO exists, handle accordingly

        formatted = []

        for index, item in enumerate(data):
            child_data = sub_dyed_fabric_inward_table.objects.filter(tm_id=item['id'], status=1, is_active=1).select_related(
                'fabric_id', 'dia_id','color_id'
            )

            if child_data.exists():
                total_rolls = child_data.aggregate(Sum('roll'))['roll__sum'] or 0
                total_gross_wt = child_data.aggregate(Sum('gross_wt'))['gross_wt__sum'] or 0

                formatted.append({
                    'action': '<button type="button" onclick="dyed_inward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                                <button type="button" onclick="dyed_fabric_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>\
                                <button type="button" onclick="dyed_fabric_inward_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>' .format(item['id'], item['id'], item['id']),
                    'id': index + 1,
                    'inward_date': item['inward_date'] if item['inward_date'] else '-', 
                    'inward_no': item['inward_number'] if item['inward_number'] else '-',
                    'lot_no': item['lot_no'] if item['lot_no'] else '-',
                    'party': getItemNameById(party_table, item['party_id']),
                    'program': getItemNameById(dyeing_program_table, item['program_id']),
                    'total_roll': item['total_roll'] if item['total_roll'] else '-',
                    'total_wt': item['total_wt'] if item['total_wt'] else '-',
                    'total_gross_wt': total_gross_wt,
                    'total_rolls': total_rolls,
                    'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
                })

        # Move response return here after loop
        return JsonResponse({'data': formatted})


# ````````````````````` dyed po list `````````````````````



def get_dyed_fabric_po_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('party-id:',supplier_id)

        if supplier_id:
            child_orders = dyed_fab_po_balance_table.objects.filter( 
                party_id=supplier_id,
                balance_quantity__gt=0
            ).values_list('po_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(dyed_fabric_po_table.objects.filter(
                id__in=child_orders,
                status=1
            ).values('id', 'po_number', 'po_name','lot_no', 'party_id').order_by('-id'))

    
            totals = dyed_fab_po_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).aggregate(
                # po_rolls=Sum('ord_rolls'),
                po_roll_wt=Sum('ord_roll_wt'),
                po_quantity=Sum('po_quantity'),
                # inward_bag=Sum('in_rolls'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            ) 

            balance_roll = (totals['po_roll_wt'] or 0) - (totals['inward_quantity'] or 0)

            return JsonResponse({
                'orders': orders,
                'po_roll_wt': balance_roll,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                # 'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})





@csrf_exempt
def get_dyed_po_detail_lists(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    po_id = request.POST.get('po_list')
    print('po-id:',po_id)
    # deliver_ids_json = request.POST.get('deliver_ids', '[]')
    tm_inward_id = request.POST.get('tm_id')
   
    if not po_id:
        return JsonResponse({"error": "PO ID not provided"}, status=400)

    try:
        # Get child orders with balance 
        child_orders = dyed_fab_po_balance_table.objects.filter(
            po_id=po_id, balance_quantity__gt=0
        ).values('po_id') 

        order_number = dyed_fabric_po_table.objects.filter( 
            id__in=child_orders, status=1
        ).values('id', 'po_number', 'po_name','lot_no','program_id').order_by('po_name')

        totals = dyed_fab_po_balance_table.objects.filter(
            po_id=po_id, balance_quantity__gt=0
        ).aggregate(
            po_roll=Sum('ord_roll_wt'),
            po_quantity=Sum('po_quantity'),
            # inward_roll=Sum('in_rolls'),
            inward_quantity=Sum('in_quantity'), 
            balance_quantity=Sum('balance_quantity'),
        )

        print('in-qty:',totals['inward_quantity'])
        program_id_list = list(
            dyed_fab_po_balance_table.objects.filter(
                po_id=po_id, balance_quantity__gt=0
            ).values_list('program_id', flat=True).distinct()
        )


        program_qs = dyed_fab_program_balance_table.objects.filter( 
            balance_quantity__gt=0, program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(dyeing_program_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'program_no', 'name', 'total_wt'))

        program = list(
            dyed_po_inward_balance_table.objects.filter(program_id__in=program_qs)
            .values_list('program_id','dia_id','color_id','pg_roll','pg_wt','in_rolls', 'in_wt','out_rolls','out_wt','balance_roll','balance_wt')
        )


        formatted_data = [
        {
            'program_id': row[0],
            'dia_id': row[1],
            'color_id': row[2],
            'pg_roll': row[3],
            'pg_wt': row[4],
            'in_rolls': row[5],
            'in_wt': row[6],
            'out_rolls': row[7],
            'out_wt': row[8],
            'balance_roll': row[9],
            'balance_wt': row[10]
        }
        for row in program
        ]
        print('programs:',program, formatted_data)


        po_total_roll = totals['po_roll'] or 0
        # balance_roll = po_total_roll - (totals['inward_roll'] or 0)
 
        sub_po = dyed_fabric_po_table.objects.filter(id=po_id, status=1).first()

        order_data = []
        program_details = []  # ➕ Collect detailed info for each program_id
        # List fabric/gauge/tex/gsm/dia for each program_id regardless of delivery

        for pid in program_id_list:
            knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            # Get sub knitting entries for this knitting program
            sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id,status=1)

            for sub in sub_knits:
                # Get related fabric_program data 
                products = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_program_data = []

                for fp in products:
                    try:
                        fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                        fabric_program_data.append({
                            'id': fp.id,
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                        })
                    except fabric_table.DoesNotExist:
                        fabric_program_data.append({
                            'id': fp.id,
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': 'N/A'
                        })

              
                dia = dia_table.objects.filter(id=sub.dia_id).first()
                color = color_table.objects.filter(id=sub.color_id).first()

                # Get list of inward IDs where outward_id is in out_id
                inward_ids = list(dyed_fabric_inward_table.objects.filter(po_id__in=po_id, status=1).values_list('id', flat=True))
                print('inw-ids:', inward_ids)

                # Now get sub_gf_inward_table records for these inward IDs and dia
                inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia_id,
                    status=1
                ).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = sub.roll - inward_roll_sum
                print('prg-rolls:', sub.roll)
                print('inw-rolls:', inward_roll_sum, 'remaining:', remaining_roll)

                # Calculate total weights
                total_wt_balance = sub.roll * sub.roll_wt
                inward_quantity = inward_roll_sum * sub.roll_wt

                program_details.append({
                    'program_id': sub.tm_id if hasattr(sub, 'tm_id') else 0,
                    'program_name':knit.name or 0 ,
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
                    # 'yarn_count': yarn.name if yarn else '',
                    # 'yarn_count_id': sub.count_id,
                    # 'gauge': gauge.name if gauge else '',
                    # 'gauge_id': sub.gauge,
                    # 'tex': tex.name if tex else '',
                    # 'tex_id': sub.tex,
                    # 'gsm': sub.gsm,
                    'dia': dia.name if dia else '',
                    'color': color.name if color else '',
                    'dia_id': sub.dia_id,
                    'color_id': sub.color_id,
                    'lot_roll': remaining_roll,
                    'per_roll_wt': sub.roll_wt,
                    'lot_roll_wt': total_wt_balance - inward_quantity,
                    'po_id': po_id,
                    'total_roll': inward_roll_sum,
                    'total_wt': inward_quantity,
                    # 'program_bal_value':program

                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id and row['color_id'] == sub.color_id
                    ]


                })



                # Extract fabric_ids from program_details
                fabric_ids = set(
                    detail['fabric_id']
                    for detail in program_details
                    if 'fabric_id' in detail and detail['fabric_id'] is not None
                )

                # Decide what to return for fabric_id
                if len(fabric_ids) == 1:
                    fabric_id_value = next(iter(fabric_ids))  # The only fabric ID
                else:
                    fabric_id_value = None  # or "multiple", as needed


        if tm_inward_id:
            parent_pos = gf_inward_table.objects.filter(id=tm_inward_id)

            for po in parent_pos:
                deliveries = sub_gf_inward_table.objects.filter(
                    tm_id=tm_inward_id,  status=1 
                )
                print('deli',deliveries)

                for delivery in deliveries:
                    programs = knitting_table.objects.filter(id__in=program_qs, is_active=1)

                    for program in programs:
                        sub_knit = sub_knitting_table.objects.filter(tm_id=program.id)
                        print('t-roll:',sub_knit)

                        if not sub_knit:
                            continue

                        product = fabric_program_table.objects.filter(id=delivery.fabric_id).first()
                        yarn_count = count_table.objects.filter(id=delivery.yarn_count_id).first()
                        gauge = gauge_table.objects.filter(id=delivery.gauge_id).first()
                        tex = tex_table.objects.filter(id=delivery.tex_id).first()

                        total_roll = delivery.roll or 0
                        remaining_roll = delivery.roll or 0
                        remaining_roll_wt = delivery.wt_per_roll or 0
                        total_roll_wt = delivery.wt_per_roll or 0
                        qty = delivery.wt_per_roll or 0
                        remaining_quantity = delivery.gross_wt or 0 

                        inward_totals = sub_gf_inward_table.objects.filter(
                            tm_id=tm_inward_id, party_id=delivery.party_id, is_active=1
                        ).aggregate(
                            inward_roll=Sum('roll'),
                            inward_quantity=Sum('wt_per_roll'),
                            inward_gross=Sum('gross_wt')
                        )

                        inward_roll = inward_totals.get('inward_roll') or 0
                        inward_quantity = inward_totals.get('inward_quantity') or 0
                        inward_gross = inward_totals.get('inward_gross') or 0

                        bal_roll = remaining_roll_wt - inward_roll
                        bal_quantity = qty - inward_quantity

                        if bal_roll == 0 and bal_quantity == 0:
                            continue

                        order_data.append({
                            'po_roll': total_roll,
                            'total_rolls':inward_roll_sum,
                            'po_quantity': remaining_quantity,
                            'inward_roll': inward_roll,
                            'inward_quantity': inward_quantity,
                            'inward_gross_wt': inward_gross,
                            # 'balance_roll': bal_roll,
                            'balance_quantity': bal_quantity,
                            'tax_value': 5,
                            'fabric_id': delivery.fabric_id,
                            'yarn_count_id': delivery.yarn_count_id,
                            'gauge_id': delivery.gauge_id,
                            'tex_id': delivery.tex_id,
                            'gsm': delivery.gsm,
                            'dia': delivery.dia_id,
                            'program_id': program.id,
                            'wt_per_roll': sub_po.total_wt if sub_po else 0,
                            'roll': remaining_roll_wt,
                            'per_roll': delivery.wt_per_roll,
                            'tx_quantity': qty,
                            'quantity': remaining_quantity,
                            'gross_wt': 0,
                            'id': program.id,
                            # 'out_id': po.id,
                            'tm_id': po.id,
                            'tx_id': delivery.id,
                            'total_quantity': delivery.total_wt or 0,
                            'total_gross_wt': delivery.gross_wt or 0,
                            'total_roll': total_roll,            
                            'product': product.name if product else '',
                        })


              
        return JsonResponse({
            'orders': list(order_number),
            'po_roll': po_total_roll,
            # 'balance_roll': balance_roll,
            'balance_wt':0, #float(totals['balance_wt'] or 0), 
            'balance_quantity':0,# float(totals['balance_wt'] or 0), 
            'po_quantity': float(totals['po_quantity'] or 0),
            # 'inward_roll': float(totals['inward_roll'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0),
            'program_id': program_id_list,
            # 'roll': balance_roll,
            'wt_per_roll': sub_po.total_wt if sub_po else 0,
            'quantity': 0,#float(totals['balance_wt'] or 0),
            'program': prg_list,
            'order_data': order_data,
            'program_details': program_details , # ✅ fabric, gauge, tex, gsm, dia per program_id
            'fabric_id':fabric_id_value,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





# update screen list

@csrf_exempt
def get_dyed_inward_po_detail_lists(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    po_id = request.POST.get('po_list')
    print('po-id:',po_id)
    # deliver_ids_json = request.POST.get('deliver_ids', '[]')
    tm_inward_id = request.POST.get('tm_id')
   
    if not po_id:
        return JsonResponse({"error": "PO ID not provided"}, status=400)

    try:
        # Get child orders with balance 
        child_orders = dyed_fab_po_balance_table.objects.filter(
            po_id=po_id, 
            # balance_quantity__gt=0
        ).values('po_id') 

        order_number = dyed_fabric_po_table.objects.filter( 
            id__in=child_orders, status=1
        ).values('id', 'po_number', 'po_name','lot_no','program_id').order_by('po_name')

        totals = dyed_fab_po_balance_table.objects.filter(
            po_id=po_id, 
            # balance_quantity__gt=0
        ).aggregate(
            po_roll=Sum('ord_roll_wt'),
            po_quantity=Sum('po_quantity'),
            # inward_roll=Sum('in_rolls'),
            inward_quantity=Sum('in_quantity'), 
            balance_quantity=Sum('balance_quantity'),
        )

        print('in-qty:',totals['inward_quantity'])
        program_id_list = list(
            dyed_fab_po_balance_table.objects.filter(
                po_id=po_id, 
                # balance_quantity__gt=0
            ).values_list('program_id', flat=True).distinct()
        )


        program_qs = dyed_fab_program_balance_table.objects.filter( 
            # balance_quantity__gt=0, program_id__in=program_id_list
           program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(dyeing_program_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'program_no', 'name', 'total_wt'))

        program = list(
            dyed_po_inward_balance_table.objects.filter(program_id__in=program_qs)
            .values_list('program_id','dia_id','color_id','pg_roll','pg_wt','in_rolls', 'in_wt','out_rolls','out_wt','balance_roll','balance_wt')
        )


        formatted_data = [
        {
            'program_id': row[0],
            'dia_id': row[1],
            'color_id': row[2],
            'pg_roll': row[3],
            'pg_wt': row[4],
            'in_rolls': row[5],
            'in_wt': row[6],
            'out_rolls': row[7],
            'out_wt': row[8],

            'balance_roll': row[9],
            'balance_wt': row[10]
        }
        for row in program
        ]
        print('programs:',program, formatted_data)


        po_total_roll = totals['po_roll'] or 0
        # balance_roll = po_total_roll - (totals['inward_roll'] or 0)
 
        sub_po = dyed_fabric_po_table.objects.filter(id=po_id, status=1).first()

        order_data = []
        program_details = []  # ➕ Collect detailed info for each program_id
        # List fabric/gauge/tex/gsm/dia for each program_id regardless of delivery

        for pid in program_id_list:
            knit = dyeing_program_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            # Get sub knitting entries for this knitting program
            sub_knits = sub_dyeing_program_table.objects.filter(tm_id=knit.id,status=1)

            for sub in sub_knits:
                # Get related fabric_program data 
                products = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_program_data = []

                for fp in products:
                    try:
                        fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                        fabric_program_data.append({
                            'id': fp.id,
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                        })
                    except fabric_table.DoesNotExist:
                        fabric_program_data.append({
                            'id': fp.id, 
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': 'N/A'
                        })

              
                dia = dia_table.objects.filter(id=sub.dia_id).first()
                color = color_table.objects.filter(id=sub.color_id).first()

                # Get list of inward IDs where outward_id is in out_id
                inward_ids = list(dyed_fabric_inward_table.objects.filter(po_id__in=po_id, status=1).values_list('id', flat=True))
                print('inw-ids:', inward_ids)

                # Now get sub_gf_inward_table records for these inward IDs and dia
                inward_roll_sum = sub_dyed_fabric_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia_id,
                    status=1
                ).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = sub.roll - inward_roll_sum
                print('prg-rolls:', sub.roll)
                print('inw-rolls:', inward_roll_sum, 'remaining:', remaining_roll)

                # Calculate total weights
                total_wt_balance = sub.roll * sub.roll_wt
                inward_quantity = inward_roll_sum * sub.roll_wt

                program_details.append({
                    'program_id': sub.tm_id if hasattr(sub, 'tm_id') else 0,
                    'program_name':knit.name or 0 ,
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
                    # 'yarn_count': yarn.name if yarn else '',
                    # 'yarn_count_id': sub.count_id,
                    # 'gauge': gauge.name if gauge else '',
                    # 'gauge_id': sub.gauge,
                    # 'tex': tex.name if tex else '',
                    # 'tex_id': sub.tex,
                    # 'gsm': sub.gsm,
                    'dia': dia.name if dia else '',
                    'color': color.name if color else '',
                    'dia_id': sub.dia_id,
                    'color_id': sub.color_id,
                    'lot_roll': remaining_roll,
                    'per_roll_wt': sub.roll_wt,
                    'lot_roll_wt': total_wt_balance - inward_quantity,
                    'po_id': po_id,
                    'total_roll': inward_roll_sum,
                    'total_wt': inward_quantity,
                    # 'program_bal_value':program

                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia_id and row['color_id'] == sub.color_id
                    ]


                })

                print('fab-det:',program_details)

                # Extract fabric_ids from program_details
                fabric_ids = set(
                    detail['fabric_id']
                    for detail in program_details
                    if 'fabric_id' in detail and detail['fabric_id'] is not None
                )

                # Decide what to return for fabric_id
                if len(fabric_ids) == 1:
                    fabric_id_value = next(iter(fabric_ids))  # The only fabric ID
                else:
                    fabric_id_value = None  # or "multiple", as needed

        if tm_inward_id:
            parent_pos = dyed_fabric_inward_table.objects.filter(id=tm_inward_id)

            for po in parent_pos:
                deliveries = sub_dyed_fabric_inward_table.objects.filter(
                    tm_id=tm_inward_id,  status=1 
                )
                print('deli',deliveries)

                for delivery in deliveries:
                    programs = dyeing_program_table.objects.filter(id__in=program_qs, is_active=1)

                    for program in programs:
                        sub_knit = sub_dyeing_program_table.objects.filter(tm_id=program.id)
                        print('t-roll:',sub_knit)

                        if not sub_knit:
                            continue

                        product = fabric_program_table.objects.filter(id=delivery.fabric_id).first()
                        # yarn_count = count_table.objects.filter(id=delivery.yarn_count_id).first()
                        # gauge = gauge_table.objects.filter(id=delivery.gauge_id).first()
                        # tex = tex_table.objects.filter(id=delivery.tex_id).first()

                        total_roll = delivery.roll or 0
                        remaining_roll = delivery.roll or 0
                        remaining_roll_wt = delivery.roll_wt or 0
                        total_roll_wt = delivery.roll_wt or 0
                        qty = delivery.roll_wt or 0
                        remaining_quantity = delivery.gross_wt or 0 

                        inward_totals = sub_dyed_fabric_inward_table.objects.filter(
                            tm_id=tm_inward_id, is_active=1
                            # tm_id=tm_inward_id, party_id=delivery.party_id, is_active=1
                        ).aggregate(
                            inward_roll=Sum('roll'),
                            inward_quantity=Sum('roll_wt'),
                            inward_gross=Sum('gross_wt')
                        )

                        inward_roll = inward_totals.get('inward_roll') or 0
                        inward_quantity = inward_totals.get('inward_quantity') or 0
                        inward_gross = inward_totals.get('inward_gross') or 0

                        bal_roll = remaining_roll_wt - inward_roll
                        bal_quantity = qty - inward_quantity

                        if bal_roll == 0 and bal_quantity == 0:
                            continue

                        dia = dia_table.objects.filter(id=delivery.dia_id).first()
                        color = color_table.objects.filter(id=delivery.color_id).first()

                        order_data.append({
                            'po_roll': total_roll,
                            'total_rolls':inward_roll_sum,
                            'po_quantity': remaining_quantity,
                            'inward_roll': inward_roll,
                            'inward_quantity': inward_quantity,
                            'inward_gross_wt': inward_gross,
                            # 'balance_roll': bal_roll,
                            'balance_quantity': bal_quantity,
                            'tax_value': 5,
                            'fabric_id': delivery.fabric_id,
                            'dia_id': delivery.dia_id,
                            'color_id': delivery.color_id,
                            'dia': dia.name,
                            'color': color.name,
                            'program_id': program.id,
                            'wt_per_roll': sub_po.total_wt if sub_po else 0,
                            'roll': remaining_roll_wt,
                            'per_roll': delivery.roll_wt,
                            'tx_quantity': qty,
                            'quantity': remaining_quantity,
                            'gross_wt': 0,
                            'id': program.id,
                            # 'out_id': po.id,
                            'tm_id': po.id,
                            'tx_id': delivery.id,
                            # 'total_quantity': delivery.total_wt or 0,
                            'total_gross_wt': delivery.gross_wt or 0,
                            'total_roll': total_roll,            
                            'product': product.name if product else '',
                        })


              
        return JsonResponse({
            'orders': list(order_number),
            'po_roll': po_total_roll,
            # 'balance_roll': balance_roll,
            'balance_wt':0, #float(totals['balance_wt'] or 0), 
            'balance_quantity':0,# float(totals['balance_wt'] or 0), 
            'po_quantity': float(totals['po_quantity'] or 0),
            # 'inward_roll': float(totals['inward_roll'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0),
            'program_id': program_id_list,
            'wt_per_roll': sub_po.total_wt if sub_po else 0,
            'quantity': 0,#float(totals['balance_wt'] or 0),
            'program': prg_list,
            'order_data': order_data,
            'program_details': program_details , # ✅ fabric, gauge, tex, gsm, dia per program_id
            # 'fabric_id':fabric_id_value or 0,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




# ````````````````````````````` add function ```````````````````````````````````````




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal
import json

@csrf_exempt
def insert_dyed_fabric_inward(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    user_id = request.session.get('user_id') 
    company_id = request.session.get('company_id')

    try:
        supplier_id = request.POST.get('supplier_id') 
        through_id = request.POST.get('through_id',0) 
        remarks = request.POST.get('remarks')
        out_id = request.POST.get('do_list')

        print('out-id:',out_id)
        # ✅ Get PO list safely as comma-separated string
        # po_list = request.POST.getlist('po_list[]') or []
        # po_str = ",".join(map(str, po_list))  # final value to store in DB
        # po_str = 0
        # print('po-ids:',po_str)
        # ✅ Get DO list safely
        # out_ids = request.POST.getlist('do_list[]') or []
        # out_id = ",".join(map(str, out_ids))

        inward_date = request.POST.get('inward_date')
        receive_no = request.POST.get('receive_no')
        receive_date = request.POST.get('receive_date') 

        dye_receive_no = request.POST.get('dye_receive_no')
        dye_receive_date = request.POST.get('dye_receive_date') 


        lot = request.POST.get('lot_name')
        prg_id = request.POST.get('prg_id')

        # ✅ Parse chemical data
        chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
        print('datas:',chemical_data)
        # ✅ Generate inward number
        inward_no = generate_inw_num_series()
        print('Generated Inward No:', inward_no)

        material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
        print('material-type:',material_type)
        is_grey_fabric = 1 if material_type == 'grey' else 0
        is_dyed_fabric = 1 if material_type == 'dye' else 0

        # Ensure only one of them is set to 1
        if is_grey_fabric + is_dyed_fabric != 1:
            return JsonResponse({'status': 'error', 'message': 'Select either grey_fabric or Grey Fabric !.'}, safe=False)



        # # ✅ Create main inward record
        # material_request = dyed_fabric_inward_table.objects.create(
        #     inward_number=inward_no,
        #     inward_date=inward_date, 
        #     party_id=supplier_id,
        #     receive_no=receive_no,
        #     is_grey_fabric=is_grey_fabric,
        #     is_dyed_fabric=is_dyed_fabric,
        #     dye_receive_no=dye_receive_no,
        #     order_through_id=through_id or 0,
        #     dye_receive_date=dye_receive_date,
        #     receive_date=receive_date,
        #     cfyear=2025,
        #     po_id=0, 
        #     program_id=prg_id, 
        #     outward_id=out_id or "0", 
        #     lot_no=lot, 
        #     company_id=company_id,
        #     total_roll=0,
        #     total_wt=Decimal('0.00'),
        #     remarks=remarks, 
        #     created_by=user_id, 
        #     created_on=timezone.now()
        # )

        # print('material-req:',material_request)
        # total_wt = Decimal('0.00')
        # total_roll = 0

        # # ✅ Loop over chemical items
        # for chemical in chemical_data:
        #     program_id = int(chemical.get('program_id') or 0)
        #     fabric_id = int(chemical.get('fabric_id') or 0)
        #     color_id = str(chemical.get('color_id') or '')  
        #     dia_id = int(chemical.get('dia_id') or 0)
        #     lot_no = str(chemical.get('lot_no') or '')

        #     delivered_roll = safe_decimal(chemical.get('roll'))
        #     gross_wt = safe_decimal(chemical.get('gross_wt'))
        #     wt_per_roll = safe_decimal(chemical.get('roll_wt'))

        #     # ✅ Create sub-inward record
        #     sub_dyed_fabric_inward_table.objects.create(
        #         tm_id=material_request.id,
        #         fabric_id=fabric_id,
        #         dia_id=dia_id,
        #         color_id=color_id,
        #         lot_no= lot, #lot_no,
        #         po_id=0,
        #         cfyear=2025,
        #         company_id=company_id,
        #         program_id=program_id,
        #         roll=delivered_roll,
        #         roll_wt=wt_per_roll,
        #         gross_wt=gross_wt,
        #         created_by=user_id,
        #         created_on=timezone.now()
        #     )

        #     total_roll += delivered_roll
        #     total_wt += gross_wt
        #     print(f'Added roll: {delivered_roll}, weight: {gross_wt}')

        # ✅ Create main inward record
        material_request = dyed_fabric_inward_table.objects.create(
            inward_number=inward_no,
            inward_date=inward_date,
            party_id=supplier_id,
            receive_no=receive_no,
            is_grey_fabric=is_grey_fabric,
            is_dyed_fabric=is_dyed_fabric,
            dye_receive_no=dye_receive_no,
            order_through_id=through_id or 0,
            dye_receive_date=dye_receive_date,
            receive_date=receive_date,
            cfyear=2025,
            po_id=0, 
            program_id=prg_id, 
            outward_id=out_id or "0", 
            lot_no=lot, 
            company_id=company_id,
            total_roll=0,
            total_wt=Decimal('0.00'),
            remarks=remarks, 
            created_by=user_id, 
            created_on=timezone.now()
        )

        print('material-req:', material_request)
        total_wt = Decimal('0.00')
        total_roll = 0

        # ✅ Loop over chemical items
        for chemical in chemical_data:
            program_id = int(chemical.get('program_id') or 0)
            fabric_id = int(chemical.get('fabric_id') or 0)
            color_id = str(chemical.get('color_id') or '')  
            dia_id = int(chemical.get('dia_id') or 0)
            lot_no = str(chemical.get('lot_no') or '')

            delivered_roll = safe_decimal(chemical.get('roll'))
            gross_wt = safe_decimal(chemical.get('gross_wt'))
            wt_per_roll = safe_decimal(chemical.get('roll_wt'))

            # ✅ Create sub-inward record
            sub_dyed_fabric_inward_table.objects.create(
                tm_id=material_request.id,
                fabric_id=fabric_id,
                dia_id=dia_id,
                color_id=color_id,
                lot_no=lot,  # lot_no,
                po_id=0,
                cfyear=2025,
                company_id=company_id,
                program_id=program_id,
                roll=delivered_roll,
                roll_wt=wt_per_roll,
                gross_wt=gross_wt,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_roll += delivered_roll
            total_wt += gross_wt
            print(f'Added roll: {delivered_roll}, weight: {gross_wt}')

        # ✅ Update main table with totals
        dyed_fabric_inward_table.objects.filter(id=material_request.id).update(
            total_roll=total_roll,
            total_wt=total_wt
        )

        print(f'Updated inward with total_roll={total_roll}, total_wt={total_wt}')


        # ✅ Update totals
        # dyed_fabric_inward_table.objects.filter(id=material_request.id).update(
        #     total_roll=total_roll,
        #     total_wt=total_wt
        # )

        # new_no = generate_inw_num_series()

        return JsonResponse({
            'status': 'success',
            'message': 'Inward entry added successfully.',
            # 'inward_no': new_no
        })

    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong: {str(e)}'
        })

from collections import defaultdict


# @csrf_exempt
# def dyed_fab_inward_print(request):
#     outward_id = request.GET.get('k')
#     order_id = base64.b64decode(outward_id)
#     print('print-id:',order_id)
    
#     if not order_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     delivery_data = dyed_fabric_inward_table.objects.filter(status=1, id=order_id)
    
#     inwards = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).first()

#     receive_no = inwards.receive_no if inwards else '-'
#     receive_date = inwards.receive_date if inwards else '-'
#     # outward_id_raw = inwards.outward_id or ''  # Might be '1,2,3'
#     po_id = inwards.po_id or 0
#     lot_no = inwards.lot_no

   
# # Process PO number
#     if po_id:
#         po_obj = dyed_fabric_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
#         po_number = po_obj['po_number'] if po_obj else '-'
#     else:
#         po_number = '-'
#         print('po-no:',po_number)


#     print('delivery:',   po_id)
#     outward = dyed_fabric_inward_table.objects.filter(id = order_id,status=1).values('id','inward_number','inward_date', 'lot_no','party_id', 'total_wt', 'total_roll')
#     # print('out:',outward)


#     program_details = []
#     delivery_details = [] 
#     # ✅ Initialize totals here
#     total_roll = 0
#     total_quantity = 0

    
#     # Then build the delivery details (independent of above)
#     # for out in outward:

#     #     total_gross = 0
#     #     total_roll = 0

#     #     tx_yarn_qs = sub_dyed_fabric_inward_table.objects.filter(
#     #         tm_id=out['id'],
#     #         status=1
#     #     # ).values(
#     #     #     'yarn_count_id', 'fabric_id', 'gauge_id', 'tex_id',
#     #     #     'gsm', 'dia_id', 'po_id', 'program_id',
#     #     #     'lot_no', 'roll', 'total_wt', 'gross_wt'
#     #     # )
#     #     ).values(
#     #         'fabric_id', 'dia_id','color_id', 'po_id', 'program_id',
#     #         'lot_no', 'roll', 'roll_wt', 'gross_wt'
#     #     )
#     #     print('tx-yarns:',tx_yarn_qs)

#     #     party = get_object_or_404(party_table, id=out['party_id'])
#     #     gstin = party.gstin
#     #     mobile = party.mobile
#     #     party_name = party.name

#     #     for tx_yarn in tx_yarn_qs:
#     #         if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
#     #             continue

#     #         dia = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
#     #         color = get_object_or_404(color_table, id=tx_yarn['color_id'])
#     #         fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
#     #         fab_id = fabric.fabric_id

#     #         yarn_count = get_object_or_404(count_table, id=fabric.count_id)
#     #         gauge = get_object_or_404(gauge_table, id=fabric.gauge_id)
#     #         tex = get_object_or_404(tex_table, id=fabric.tex_id)
#     #         fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)
#     #         fabric_display_name = f"{fabric.name} - {fabric_obj.name}"

#     #         delivery_details.append({
#     #             'mill': party.name,
#     #             'yarn_count': yarn_count.name,
#     #             'fabric': fabric_display_name,
#     #             'gauge': gauge.name,
#     #             'tex': tex.name,
#     #             'dia': dia.name,
#     #             'color': color.name,
#     #             'lot_no': out['lot_no'],
#     #             'inward_number': out['inward_number'],
#     #             'inward_date': out['inward_date'],
#     #             'roll': tx_yarn['roll'],
#     #             'total_wt': tx_yarn.get('roll_wt'),
#     #             'gsm': fabric.gray_gsm,
#     #             'gross_wt': tx_yarn['gross_wt'],
#     #         })

#     #         print('deli-details:',delivery_details)

#     #         # Accumulate totals 
#     #         total_roll += tx_yarn['roll'] or 0
#     #         total_gross += tx_yarn['gross_wt'] or 0
#     # Grouped structure: {dia_name: [entries]}
#     grouped_by_dia = defaultdict(list)

#     for out in outward:
#         total_gross = 0
#         total_roll = 0


#         tx_yarn_qs = sub_dyed_fabric_inward_table.objects.filter(
#             tm_id=out['id'],
#             status=1
#         ).values(
#             'fabric_id', 'dia_id', 'color_id', 'po_id', 'program_id',
#             'lot_no', 'roll', 'roll_wt', 'gross_wt'
#         )

#         party = get_object_or_404(party_table, id=out['party_id'])
#         gstin = party.gstin
#         mobile = party.mobile
#         party_name = party.name

#         for tx_yarn in tx_yarn_qs:
#             if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
#                 continue

#             dia = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
#             color = get_object_or_404(color_table, id=tx_yarn['color_id'])
#             fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
#             fab_id = fabric.fabric_id

#             yarn_count = get_object_or_404(count_table, id=fabric.count_id)
#             gauge = get_object_or_404(gauge_table, id=fabric.gauge_id)
#             tex = get_object_or_404(tex_table, id=fabric.tex_id)
#             fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)

#             fabric_display_name = f"{fabric.name} - {fabric_obj.name}"

#             entry = {
#                 'mill': party.name,
#                 'yarn_count': yarn_count.name,
#                 'fabric': fabric_display_name,
#                 'gauge': gauge.name,
#                 'tex': tex.name,
#                 'gsm': fabric.gray_gsm,
#                 'color': color.name,
#                 'lot_no': out['lot_no'],
#                 'inward_number': out['inward_number'],
#                 'inward_date': out['inward_date'],
#                 'roll': tx_yarn['roll'],
#                 'total_wt': tx_yarn.get('roll_wt'),
#                 'gross_wt': tx_yarn['gross_wt'],

#             }

#             grouped_by_dia[dia.name].append(entry)

#             total_roll += tx_yarn['roll'] or 0
#             total_gross += tx_yarn['gross_wt'] or 0

#     grouped_rows = defaultdict(list)

#     for row in delivery_details:
#         key = (
#             row['yarn_count'], row['fabric'], row['gauge'],
#             row['tex'], row['gsm'], row['dia']
#         )
#         grouped_rows[key].append(row)

#     # Convert to a list of tuples for rendering
#     grouped_rows = list(grouped_rows.items())

#     print('grp:',grouped_rows)
  
#     # image_url = 'http://localhost:8000/static/assets/images/mira.png'
#     image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'
#     # total_gross +=  tx_yarn['gross_wt'] 

#     delivery = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
#     remarks = delivery['remarks'] if delivery else ''
#     print('image_url:',image_url)
#     # total_roll +=  tx_yarn['roll'] 
#     # pre_no = previous_outward['do_number']

#     print('deli-data:',delivery_data)
#     context = { 
#         # 'inward_number': outward['inward_number'],
#         # 'inward_date': outward['inward_date'],
#         'inward_values':delivery_data,

#         'receive_no':receive_no,
#         'receive_date':receive_date,
#         'grouped_rows': grouped_rows,

#         'gstin':gstin,
#         'mobile':mobile,
#         'customer_name':party_name,
#         'program_details': program_details,
#         'total_roll': total_roll, 
#         'total_quantity': total_gross,

#         'inward_details': delivery_details,
#         'company':company_table.objects.filter(status=1).first(),
#         'grouped_by_dia': dict(grouped_by_dia),  # convert defaultdict to regular dict


#         'program':program,
#         'image_url':image_url,
#         'remarks':remarks, 
#         'outward':0,#outward_display,
#         'po':po_number,
#         'lot_no':lot_no,
#         # 'previous_no':pre_qty if pre_qty else '-',


#     } 

#     return render(request, 'inward/dyed_inward_print.html', context)







from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
import base64



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from collections import defaultdict
import base64
from django.views.decorators.csrf import csrf_exempt


# @csrf_exempt
# def dyed_fab_inward_print(request):
#     outward_id = request.GET.get('k')
#     try:
#         order_id = int(base64.b64decode(outward_id))
#     except Exception:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)

#     inwards = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).first()
#     if not inwards:
#         return JsonResponse({'error': 'Inward not found'}, status=404)

#     delivery_data = [inwards]

   
#     receive_no = inwards.receive_no or '-'
#     receive_date = inwards.receive_date or '-'
#     po_id = inwards.po_id or 0
#     outward_id = inwards.outward_id or 0
#     lot_no = inwards.lot_no or '-'

#     po_number = '-'
#     if po_id:
#         po_obj = dyed_fabric_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
#         po_number = po_obj['po_number'] if po_obj else '-'


#     out_no = '-'
#     if outward_id:
#         out_obj = parent_gf_delivery_table.objects.filter(status=1, id=outward_id).values('do_number').first()
#         out_no = out_obj['do_number'] if out_obj else '-'



#     outward = dyed_fabric_inward_table.objects.filter(
#         id=order_id, status=1
#     ).values('id', 'inward_number', 'inward_date', 'lot_no', 'party_id', 'total_wt', 'total_roll')

#     delivery_details = []
#     total_roll = 0
#     total_gross = 0
#     dias_set = set()

#     for out in outward:
#         tx_yarn_qs = sub_dyed_fabric_inward_table.objects.filter(
#             tm_id=out['id'], status=1
#         ).values(
#             'fabric_id', 'dia_id', 'color_id', 'po_id', 'program_id',
#             'lot_no', 'roll', 'roll_wt', 'gross_wt'
#         )

#         party = get_object_or_404(party_table, id=out['party_id'])
#         gstin = party.gstin
#         mobile = party.mobile
#         party_name = party.name

#         for tx_yarn in tx_yarn_qs:
#             if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
#                 continue

#             dia_obj = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
#             color = get_object_or_404(color_table, id=tx_yarn['color_id'])
#             fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
#             fabric_base = get_object_or_404(fabric_table, id=fabric.fabric_id, status=1)

#             yarn_count = get_object_or_404(count_table, id=fabric.count_id)
#             gauge = get_object_or_404(gauge_table, id=fabric.gauge_id)
#             tex = get_object_or_404(tex_table, id=fabric.tex_id)

#             fabric_display_name = f"{fabric.name} - {fabric_base.name}"

#             dia_name = dia_obj.name
#             dias_set.add(dia_name)

#             entry = {
#                 'mill': party.name,
#                 'yarn_count': yarn_count.name,
#                 'fabric': fabric_display_name,
#                 'gauge': gauge.name,
#                 'tex': tex.name,
#                 'gsm': fabric.gray_gsm,
#                 'dia': dia_name,
#                 'color': color.name,
#                 'lot_no': out['lot_no'],
#                 'inward_number': out['inward_number'],
#                 'inward_date': out['inward_date'],
#                 'roll': tx_yarn['roll'],
#                 'total_wt': tx_yarn.get('roll_wt', 0),
#                 'gross_wt': tx_yarn['gross_wt'],
#             }

#             delivery_details.append(entry)
#             total_roll += tx_yarn['roll']
#             total_gross += tx_yarn['gross_wt']

#     # Step 1: Grouping by fabric info → color → dia
#     grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'roll': 0, 'roll_wt': 0})))

#     for row in delivery_details:
#         fabric_key = (
#             row['fabric'], row['yarn_count'], row['gauge'],
#             row['tex'], row['gsm']
#         )
#         grouped_data[fabric_key][row['color']][row['dia']]['roll'] += row['roll']
#         grouped_data[fabric_key][row['color']][row['dia']]['roll_wt'] += row['total_wt']

#     dias = sorted(dias_set, key=lambda x: float(x))  # Ensure correct dia ordering
#     grouped_delivery_details = []

#     for fabric_key, color_map in grouped_data.items():
#         fabric_dict = {
#             'fabric_info': {
#                 'fabric': fabric_key[0],
#                 'yarn_count': fabric_key[1],
#                 'gauge': fabric_key[2],
#                 'tex': fabric_key[3],
#                 'gsm': fabric_key[4],
#             },
#             'color_groups': []
#         }

#         for color_name, dia_map in color_map.items():
#             row = {
#                 'color': color_name,
#                 'dias': [],
#                 'total_roll': 0,
#                 'total_weight': 0
#             }

#             for dia in dias:
#                 data = dia_map.get(dia, {'roll': 0, 'roll_wt': 0})
#                 row['dias'].append({
#                     'dia': dia,
#                     'roll': data['roll'],
#                     'roll_wt': data['roll_wt']
#                 })
#                 row['total_roll'] += data['roll']
#                 row['total_weight'] += data['roll_wt']

#             fabric_dict['color_groups'].append(row)

#         grouped_delivery_details.append(fabric_dict)
#         print('grp-details:',grouped_delivery_details)

#     # Dia totals
#     dia_totals_list = []
#     grand_total_roll = 0
#     grand_total_weight = 0

#     for dia in dias:
#         dia_roll_total = 0
#         dia_wt_total = 0
#         for fabric in grouped_delivery_details:
#             for color_row in fabric['color_groups']:
#                 for d in color_row['dias']:
#                     if d['dia'] == dia:
#                         dia_roll_total += d['roll']
#                         dia_wt_total += d['roll_wt']
#         dia_totals_list.append({'roll': dia_roll_total, 'roll_wt': dia_wt_total})
#         grand_total_roll += dia_roll_total
#         grand_total_weight += dia_wt_total

#     remarks_data = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
#     remarks = remarks_data['remarks'] if remarks_data else ''

#     image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

#     context = {
#         'inward_values': delivery_data,
#         'receive_no': receive_no,
#         'receive_date': receive_date,
#         'grouped_delivery_details': grouped_delivery_details,
#         'dias': dias,
#         'gstin': gstin,
#         'mobile': mobile,
#         'customer_name': party_name,
#         'total_roll': total_roll,
#         'total_quantity': total_gross,
#         'company': company_table.objects.filter(status=1).first(),
#         'program_details': [],
#         'image_url': image_url,
#         'remarks': remarks,
#         'outward': out_no,
#         'po': po_number,
#         'lot_no': lot_no,
#         'dia_totals_list': dia_totals_list,
#         'grand_total_roll': grand_total_roll,
#         'grand_total_weight': grand_total_weight
#     }

#     return render(request, 'inward/dyed_inward_print.html', context)



@csrf_exempt
def dyed_fab_inward_print(request):
    outward_id = request.GET.get('k')
    try:
        order_id = int(base64.b64decode(outward_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    inwards = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).first()
    if not inwards:
        return JsonResponse({'error': 'Inward not found'}, status=404)

    delivery_data = [inwards]

    receive_no = inwards.receive_no or '-'
    receive_date = inwards.receive_date or '-'
    po_id = inwards.po_id or 0
    outward_id = inwards.outward_id or 0
    lot_no = inwards.lot_no or '-'

    po_number = '-'
    if po_id:
        po_obj = dyed_fabric_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
        po_number = po_obj['po_number'] if po_obj else '-'

    out_no = '-'
    if outward_id:
        out_obj = parent_gf_delivery_table.objects.filter(status=1, id=outward_id).values('do_number').first()
        out_no = out_obj['do_number'] if out_obj else '-'

    outward = dyed_fabric_inward_table.objects.filter(
        id=order_id, status=1
    ).values('id', 'inward_number', 'inward_date', 'lot_no', 'party_id', 'total_wt', 'total_roll')

    delivery_details = []
    total_roll = 0
    total_gross = 0
    dias_set = set()

    for out in outward:
        tx_yarn_qs = sub_dyed_fabric_inward_table.objects.filter(
            tm_id=out['id'], status=1
        ).values(
            'fabric_id', 'dia_id', 'color_id', 'po_id', 'program_id',
            'lot_no', 'roll', 'gross_wt'
        )

        party = get_object_or_404(party_table, id=out['party_id'])
        gstin = party.gstin
        mobile = party.mobile
        party_name = party.name

        for tx_yarn in tx_yarn_qs:
            if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
                continue

            dia_obj = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
            color = get_object_or_404(color_table, id=tx_yarn['color_id'])
            fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
            fabric_base = get_object_or_404(fabric_table, id=fabric.fabric_id, status=1)

            yarn_count = get_object_or_404(count_table, id=fabric.count_id)
            gauge = get_object_or_404(gauge_table, id=fabric.gauge_id)
            tex = get_object_or_404(tex_table, id=fabric.tex_id)

            fabric_display_name = f"{fabric.name} - {fabric_base.name}"

            dia_name = dia_obj.name
            dias_set.add(dia_name)

            entry = {
                'mill': party.name,
                'yarn_count': yarn_count.name,
                'fabric': fabric_display_name,
                'gauge': gauge.name,
                'tex': tex.name,
                'gsm': fabric.gray_gsm,
                'dia': dia_name,
                'color': color.name,
                'lot_no': out['lot_no'],
                'inward_number': out['inward_number'],
                'inward_date': out['inward_date'],
                'roll': tx_yarn['roll'],
                'gross_wt': tx_yarn['gross_wt'],
            }

            delivery_details.append(entry)
            total_roll += tx_yarn['roll']
            total_gross += tx_yarn['gross_wt']

    # Step 1: Grouping by fabric info → color → dia
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'roll': 0, 'gross_wt': 0})))

    for row in delivery_details:
        fabric_key = (
            row['fabric'], row['yarn_count'], row['gauge'],
            row['tex'], row['gsm']
        )
        grouped_data[fabric_key][row['color']][row['dia']]['roll'] += row['roll']
        grouped_data[fabric_key][row['color']][row['dia']]['gross_wt'] += row['gross_wt']

    dias = sorted(dias_set, key=lambda x: float(x))  # Ensure correct dia ordering
    grouped_delivery_details = []

    for fabric_key, color_map in grouped_data.items():
        fabric_dict = {
            'fabric_info': {
                'fabric': fabric_key[0],
                'yarn_count': fabric_key[1],
                'gauge': fabric_key[2],
                'tex': fabric_key[3],
                'gsm': fabric_key[4],
            },
            'color_groups': []
        }

        for color_name, dia_map in color_map.items():
            row = {
                'color': color_name,
                'dias': [],
                'total_roll': 0,
                'total_weight': 0  # This will now represent gross weight
            }

            for dia in dias:
                data = dia_map.get(dia, {'roll': 0, 'gross_wt': 0})
                row['dias'].append({
                    'dia': dia,
                    'roll': data['roll'],
                    'gross_wt': data['gross_wt']
                })
                row['total_roll'] += data['roll']
                row['total_weight'] += data['gross_wt']

            fabric_dict['color_groups'].append(row)

        grouped_delivery_details.append(fabric_dict)

    # Dia totals
    dia_totals_list = []
    grand_total_roll = 0
    grand_total_weight = 0

    for dia in dias:
        dia_roll_total = 0
        dia_wt_total = 0
        for fabric in grouped_delivery_details:
            for color_row in fabric['color_groups']:
                for d in color_row['dias']:
                    if d['dia'] == dia:
                        dia_roll_total += d['roll']
                        dia_wt_total += d['gross_wt']
        dia_totals_list.append({'roll': dia_roll_total, 'gross_wt': dia_wt_total})
        grand_total_roll += dia_roll_total
        grand_total_weight += dia_wt_total

    remarks_data = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
    remarks = remarks_data['remarks'] if remarks_data else ''

    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'inward_values': delivery_data,
        'receive_no': receive_no,
        'receive_date': receive_date,
        'grouped_delivery_details': grouped_delivery_details,
        'dias': dias,
        'gstin': gstin,
        'mobile': mobile,
        'customer_name': party_name,
        'total_roll': total_roll,
        'total_quantity': total_gross,
        'company': company_table.objects.filter(status=1).first(),
        'program_details': [],
        'image_url': image_url,
        'remarks': remarks,
        'outward': out_no,
        'po': po_number,
        'lot_no': lot_no,
        'dia_totals_list': dia_totals_list,
        'grand_total_roll': grand_total_roll,
        'grand_total_weight': grand_total_weight
    }

    return render(request, 'inward/dyed_inward_print.html', context)



@csrf_exempt
def dyed_fab_inward_print_test1472025(request):
    outward_id = request.GET.get('k')
    try:
        order_id = int(base64.b64decode(outward_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    inwards = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).first()
    if not inwards:
        return JsonResponse({'error': 'Inward not found'}, status=404)

    delivery_data = [inwards]

   
    receive_no = inwards.receive_no or '-'
    receive_date = inwards.receive_date or '-'
    po_id = inwards.po_id or 0
    outward_id = inwards.outward_id or 0
    lot_no = inwards.lot_no or '-'

    po_number = '-'
    if po_id:
        po_obj = dyed_fabric_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
        po_number = po_obj['po_number'] if po_obj else '-'


    out_no = '-' 
    if outward_id:
        out_obj = parent_gf_delivery_table.objects.filter(status=1, id=outward_id).values('do_number').first()
        out_no = out_obj['do_number'] if out_obj else '-'



    outward = dyed_fabric_inward_table.objects.filter(
        id=order_id, status=1
    ).values('id', 'inward_number', 'inward_date', 'lot_no', 'party_id', 'total_wt', 'total_roll')

    delivery_details = []
    total_roll = 0
    total_gross = 0
    dias_set = set()

    for out in outward:
        tx_yarn_qs = sub_dyed_fabric_inward_table.objects.filter(
            tm_id=out['id'], status=1
        ).values(
            'fabric_id', 'dia_id', 'color_id', 'po_id', 'program_id',
            # 'lot_no', 'roll', 'roll_wt', 'gross_wt'
            'lot_no', 'roll', 'gross_wt'
        )
        print('tx-datas:',tx_yarn_qs)

        party = get_object_or_404(party_table, id=out['party_id'])
        gstin = party.gstin
        mobile = party.mobile
        party_name = party.name

        for tx_yarn in tx_yarn_qs:
            if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
                continue

            dia_obj = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
            color = get_object_or_404(color_table, id=tx_yarn['color_id'])
            fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
            fabric_base = get_object_or_404(fabric_table, id=fabric.fabric_id, status=1)

            yarn_count = get_object_or_404(count_table, id=fabric.count_id)
            gauge = get_object_or_404(gauge_table, id=fabric.gauge_id)
            tex = get_object_or_404(tex_table, id=fabric.tex_id)

            fabric_display_name = f"{fabric.name} - {fabric_base.name}"

            dia_name = dia_obj.name
            dias_set.add(dia_name)

            entry = {
                'mill': party.name,
                'yarn_count': yarn_count.name,
                'fabric': fabric_display_name,
                'gauge': gauge.name,
                'tex': tex.name,
                'gsm': fabric.gray_gsm,
                'dia': dia_name,
                'color': color.name,
                'lot_no': out['lot_no'],
                'inward_number': out['inward_number'],
                'inward_date': out['inward_date'],
                'roll': tx_yarn['roll'],
                'total_wt': tx_yarn.get('roll_wt', 0),
                'gross_wt': tx_yarn['gross_wt'],
            }

            delivery_details.append(entry)
            total_roll += tx_yarn['roll'] 
            total_gross += tx_yarn['gross_wt']

    # Step 1: Grouping by fabric info → color → dia
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'roll': 0, 'roll_wt': 0})))
    print('grp-data:',grouped_data)
    for row in delivery_details:
        fabric_key = (
            row['fabric'], row['yarn_count'], row['gauge'],
            row['tex'], row['gsm']
        )
        grouped_data[fabric_key][row['color']][row['dia']]['roll'] += row['roll']
        grouped_data[fabric_key][row['color']][row['dia']]['roll_wt'] += row['total_wt']

    dias = sorted(dias_set, key=lambda x: float(x))  # Ensure correct dia ordering
    grouped_delivery_details = []

    for fabric_key, color_map in grouped_data.items():
        fabric_dict = {
            'fabric_info': {
                'fabric': fabric_key[0],
                'yarn_count': fabric_key[1],
                'gauge': fabric_key[2],
                'tex': fabric_key[3],
                'gsm': fabric_key[4],
            },
            'color_groups': []
        }

        for color_name, dia_map in color_map.items():
            row = {
                'color': color_name,
                'dias': [],
                'total_roll': 0,
                'total_weight': 0 
            }

            for dia in dias:
                data = dia_map.get(dia, {'roll': 0, 'roll_wt': 0})
                row['dias'].append({
                    'dia': dia,
                    'roll': data['roll'],
                    'gross_wt': data['gross_wt']
                })
                row['total_weight'] += data['gross_wt']




                # row['dias'].append({
                #     'dia': dia,
                #     'roll': data['roll'],
                #     'roll_wt': data['roll_wt']
                # })
                row['total_roll'] += data['roll']
                # row['total_weight'] += data['roll_wt']

            fabric_dict['color_groups'].append(row)

        grouped_delivery_details.append(fabric_dict)
        print('grp-details:',grouped_delivery_details)

    # Dia totals
    dia_totals_list = []
    grand_total_roll = 0
    grand_total_weight = 0

    for dia in dias:
        dia_roll_total = 0
        dia_wt_total = 0
        for fabric in grouped_delivery_details:
            for color_row in fabric['color_groups']:
                for d in color_row['dias']:
                    if d['dia'] == dia:
                        dia_roll_total += d['roll']
                        dia_wt_total += d['roll_wt']
        dia_totals_list.append({'roll': dia_roll_total, 'roll_wt': dia_wt_total})
        grand_total_roll += dia_roll_total
        grand_total_weight += dia_wt_total

    remarks_data = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
    remarks = remarks_data['remarks'] if remarks_data else ''

    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'inward_values': delivery_data,
        'receive_no': receive_no,
        'receive_date': receive_date,
        'grouped_delivery_details': grouped_delivery_details,
        'dias': dias,
        'gstin': gstin,
        'mobile': mobile,
        'customer_name': party_name,
        'total_roll': total_roll,
        'total_quantity': total_gross,
        'company': company_table.objects.filter(status=1).first(),
        'program_details': [],
        'image_url': image_url,
        'remarks': remarks,
        'outward': out_no,
        'po': po_number,
        'lot_no': lot_no,
        'dia_totals_list': dia_totals_list,
        'grand_total_roll': grand_total_roll,
        'grand_total_weight': grand_total_weight
    }

    return render(request, 'inward/dyed_inward_print.html', context)


@csrf_exempt
def dyed_fab_inward_print_bk_372025(request):
    outward_id = request.GET.get('k')
    try:
        order_id = int(base64.b64decode(outward_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    print('print-id:', order_id)

    inwards = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).first()
    if not inwards:
        return JsonResponse({'error': 'Inward not found'}, status=404)

    delivery_data = [inwards]

    receive_no = inwards.receive_no or '-'
    receive_date = inwards.receive_date or '-'
    po_id = inwards.po_id or 0
    lot_no = inwards.lot_no or '-'

    # Process PO number
    po_number = '-'
    if po_id:
        po_obj = dyed_fabric_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
        po_number = po_obj['po_number'] if po_obj else '-'

    print('delivery:', po_id)

    outward = dyed_fabric_inward_table.objects.filter(
        id=order_id, status=1
    ).values('id', 'inward_number', 'inward_date', 'lot_no', 'party_id', 'total_wt', 'total_roll')

    delivery_details = []
    total_roll = 0
    total_gross = 0

    for out in outward:
        tx_yarn_qs = sub_dyed_fabric_inward_table.objects.filter(
            tm_id=out['id'], status=1
        ).values(
            'fabric_id', 'dia_id', 'color_id', 'po_id', 'program_id',
            'lot_no', 'roll', 'roll_wt', 'gross_wt'
        )

        party = get_object_or_404(party_table, id=out['party_id'])
        gstin = party.gstin
        mobile = party.mobile
        party_name = party.name

        for tx_yarn in tx_yarn_qs:
            if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
                continue

            dia = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
            color = get_object_or_404(color_table, id=tx_yarn['color_id'])
            fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
            fabric_base = get_object_or_404(fabric_table, id=fabric.fabric_id, status=1)

            yarn_count = get_object_or_404(count_table, id=fabric.count_id)
            gauge = get_object_or_404(gauge_table, id=fabric.gauge_id)
            tex = get_object_or_404(tex_table, id=fabric.tex_id)

            fabric_display_name = f"{fabric.name} - {fabric_base.name}"

            entry = {
                'mill': party.name,
                'yarn_count': yarn_count.name,
                'fabric': fabric_display_name,
                'gauge': gauge.name,
                'tex': tex.name,
                'gsm': fabric.gray_gsm,
                'dia': dia.name,
                'color': color.name,
                'lot_no': out['lot_no'],
                'inward_number': out['inward_number'],
                'inward_date': out['inward_date'],
                'roll': tx_yarn['roll'],
                'total_wt': tx_yarn.get('roll_wt'),
                'gross_wt': tx_yarn['gross_wt'],
            }

            delivery_details.append(entry)
            total_roll += tx_yarn['roll']
            total_gross += tx_yarn['gross_wt']

    # Grouping by: yarn → fabric → gauge → tex → gsm → dia
    grouped_rows = defaultdict(list)
    for row in delivery_details:
        key = (
            row['yarn_count'], row['fabric'], row['gauge'],
            row['tex'], row['gsm'], row['dia']
        )
        grouped_rows[key].append(row)

    grouped_rows = list(grouped_rows.items())

    remarks_data = dyed_fabric_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
    remarks = remarks_data['remarks'] if remarks_data else ''

    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'inward_values': delivery_data,
        'receive_no': receive_no,
        'receive_date': receive_date,
        'grouped_rows': grouped_rows,
        'gstin': gstin,
        'mobile': mobile,
        'customer_name': party_name,
        'total_roll': total_roll,
        'total_quantity': total_gross,
        'company': company_table.objects.filter(status=1).first(),
        'program_details': [],
        'image_url': image_url,
        'remarks': remarks,
        'outward': 0,
        'po': po_number,
        'lot_no': lot_no,
        'delivery_details':delivery_details
    }

    return render(request, 'inward/dyed_inward_print.html', context)
 



import base64

def dyed_inward_detail_edit(request):
    try:
        encoded_id = request.GET.get('id') 
        print('encoded-id:', encoded_id)

        if not encoded_id:
            return render(request, 'inward/update_dyed_fabric_inward.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID 
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode() 
            print('decoded-id:', decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'inward/update_dyed_fabric_inward.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
        print('material:', material_id)

        # Fetch the parent stock instance
        parent_stock_instance = dyed_fabric_inward_table.objects.filter(id=material_id).first()
        lot = parent_stock_instance.lot_no
        print('inw:', parent_stock_instance.id)

        # Fetch all sub-material instances (full list, not just one)
        material_instances = sub_dyed_fabric_inward_table.objects.filter(tm_id=material_id)
        # material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        print('material_instances:', material_instances)
        print('material_instances:', material_instances)


        color_ids = [str(m.color_id) for m in material_instances if m.color_id]

       
        # Fetch active products, supplier list, party list, and counts
        product = product_table.objects.filter(status=1) 
        supplier = party_table.objects.filter(status=1)
        # party = party_table.objects.filter(is_knitting=1, status=1)
        party = party_table.objects.filter( status=1,is_trader=1)
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)
        mill_list = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        po = dyed_fabric_po_table.objects.filter(status=1)
        outward = parent_gf_delivery_table.objects.filter(status=1,lot_no=lot) 
        fabric_program_qs = fabric_program_table.objects.filter(status=1) 
        dyeing = dyeing_program_table.objects.filter(status=1) 

        fabric_program = []
        for fp in fabric_program_qs:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                print(f"fabric_item: {fabric_item}, ID: {fp.fabric_id}, Name: {getattr(fabric_item, 'name', 'NO NAME')}")
                fabric_program.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                })
            except fabric_table.DoesNotExist:
                print(f"fabric_id {fp.fabric_id} not found in fabric_table")
                fabric_program.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': 'N/A'
                })       
                
        gauge = gauge_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        yarn_count = count_table.objects.filter(status=1)

        fabric_program_with_name = []
        for fp in fabric_program_qs:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                print(f"fabric_item: {fabric_item}, ID: {fp.fabric_id}, Name: {getattr(fabric_item, 'name', 'NO NAME')}")
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                })
            except fabric_table.DoesNotExist:
                print(f"fabric_id {fp.fabric_id} not found in fabric_table")
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': 'N/A'
                })


                context['color_ids_list'] = [str(m.color_id) for m in material_instances if m.color_id]

        # Prepare context for template
        context = {
            'material_instances': material_instances,
            'parent_stock_instance': parent_stock_instance,
            'product': product,
            'party': party,
            'supplier': supplier, 
            'count': count,
            'decode_id': parent_stock_instance.id,
            'program':program,
            'mill_list':mill_list,
            'po':po,
            'outward':outward,  
            'po_list': dyed_fabric_po_table.objects.filter(status=1),
            'fabric_program':fabric_program,
            'gauge':gauge,
            'tex':tex,
            'dia':dia,
            'yarn_count':yarn_count,
            'fabric_program_with_name':fabric_program_with_name,
            'dyeing':dyeing,
            'color_ids': color_ids,   # <---- Add color_ids here

        }

        # print('context values:', context)
        return render(request, 'inward/update_dyed_fabric_inward.html', context)

    except Exception as e:
        print('Exception:', e)
        return render(request, 'inward/update_dyed_fabric_inward.html', {'error_message': 'An unexpected error occurred: ' + str(e)})





@csrf_exempt
def dyed_fabric_inward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        if not data_id:
            return JsonResponse({'message': 'Inward ID is required.'})

        try:
            # Get the inward entry
            inward = dyed_fabric_inward_table.objects.get(id=data_id)
            po_id = inward.po_id  # Can be None

            # # Check for active delivery entries
            # has_active_delivery = sub_dyed_fabric_inward_table.objects.filter(
            #     tm_id=data_id
            # ).exclude(status=0).exists()

            # if has_active_delivery:
            #     return JsonResponse({
            #         'message': 'Cannot delete: This inward is linked to an active delivery. Please delete the delivery first.'
            #     })

            # Check for active PO linkage
            # if po_id and parent_po_table.objects.filter(id=po_id, status=1, is_active=1).exists():
            #     return JsonResponse({
            #         'message': 'Cannot delete: This inward is linked to an active PO. Please delete the PO first.'
            #     })



            # Safe to soft-delete
            dyed_fabric_inward_table.objects.filter(id=data_id).update(status=0, is_active=0,updated_on=timezone.now())
            sub_dyed_fabric_inward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0,updated_on=timezone.now())
          
            # dyed_fabric_inward_table.objects.filter(id=data_id).delete()
            # sub_dyed_fabric_inward_table.objects.filter(tm_id=data_id).delete()



            return JsonResponse({'message': 'yes'})

        except dyed_fabric_inward_table.DoesNotExist:
            return JsonResponse({'message': 'Inward entry not found.'})
        except Exception as e:
            print("Error during inward deletion:", e)
            return JsonResponse({'message': 'Error occurred during inward deletion.'})

    return JsonResponse({'message': 'Invalid request method'})






def update_dyed_fab_inward_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('po-out-tmid:',master_id)
        if master_id:
            try:
                child_data = sub_dyed_fabric_inward_table.objects.filter(tm_id=master_id, status=1)
                # parent = dyed_fabric_inward_table.objects.filter(id=master_id, status=1)


                if not child_data.exists():
                    return JsonResponse({'success': True, 'data': []})  # still return success with empty data

                formatted_data = []
                for index, item in enumerate(child_data, start=1):
                    formatted_data.append({
                        'action': f'''
                            <button type="button" onclick="inward_detail_edit('{item.id}')" class="btn btn-primary btn-xs">
                                <i class="feather icon-edit"></i>
                            </button>
                            <button type="button" onclick="inward_detail_delete('{item.id}')" class="btn btn-danger btn-xs">
                                <i class="feather icon-trash-2"></i>
                            </button>
                        ''',
                        'fabric': getItemFabNameById(fabric_program_table, item.fabric_id),
                        'color': getItemNameById(color_table, item.color_id),
                        'dia': getItemNameById(dia_table, item.dia_id),
                        'roll': item.roll or 0,
                        'total_wt': item.roll_wt or 0,
                        'gross_wt': item.gross_wt or 0,
                        'received_roll': 0,
                        'received_roll_wt': 0,
                        'fabric_id': item.fabric_id or '-',
                        'color_id': item.color_id or '-',
                        'dia_id': item.dia_id or '-',
                    })

                return JsonResponse({'success': True, 'data': formatted_data})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request, missing ID parameter'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})






def update_dyed_fabric_inward(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')
            # receive_no = request.session.get('receive_no')
            # receive_date = request.session.get('receive_date')
            # inward_date = request.session.get('inward_date')

            # dye_receive_no = request.session.get('dye_receive_no')
            # dye_receive_date = request.session.get('dye_receive_date')


            receive_no = request.POST.get('receive_no')
            receive_date = request.POST.get('dye_receive_date')
            inward_date = request.POST.get('inward_date')
            do_list = request.POST.get('do_list')
            # dye_receive_no = request.POST.get('dye_receive_no')
            # dye_receive_date = request.POST.get('dye_receive_date')

            dye_receive_no = request.POST.get('receive_no')
            dye_receive_date = request.POST.get('dye_receive_date')


            master_id = request.POST.get('tm_id')
            if not master_id:
                return JsonResponse({'success': False, 'error_message': 'Missing tm_id'})

            # Get and parse table data
            chemical_data = request.POST.get('chemical_data')
            if not chemical_data:
                return JsonResponse({'success': False, 'error_message': 'Missing table data'}) 

            table_data = json.loads(chemical_data)

            if not table_data:
                return JsonResponse({'success': False, 'error_message': 'Table data is empty'})

            # Step 1: Delete previous entries with status = 0
            dyed_fabric_inward_table.objects.filter(id=master_id).update(inward_date=inward_date,
                                                                         receive_no=receive_no,
                                                                         receive_date=receive_date,
                                                                         dye_receive_no=dye_receive_no,
                                                                         dye_receive_date=dye_receive_date,
                                                                         )
 


            sub_dyed_fabric_inward_table.objects.filter(tm_id=master_id).delete() 
            print('yes')
            # Step 2: Create new entries
            for row in table_data:     
                print('tot-wt:',row.get('total_wt'))

                sub_dyed_fabric_inward_table.objects.create(
                    tm_id=master_id, 
                    company_id=company_id,
                    cfyear=2025,
                    roll=row.get('roll'),
                    roll_wt=row.get('total_wt'), 
                    gross_wt=row.get('gross_wt'),
                    program_id=row.get('program_id'),
                    lot_no=row.get('lot_no'),

                    po_id=row.get('po_id') or 0,
                    # outward_id=do_list or 0,
                    # party_id=row.get('supplier_id') or 0,

                    fabric_id=row.get('fabric_id'),
                    color_id=row.get('color_id'),
                    dia_id=row.get('dia_id'),

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
        qs = sub_dyed_fabric_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        if not qs.exists():
            return {'error': 'No active inward items found.'}

        # Use Django ORM's Sum aggregation
        totals = qs.aggregate(
            total_wt=Sum('roll_wt'),
            gross_wt=Sum('gross_wt'),
            total_roll=Sum('roll')
        )

        total_wt = totals['total_wt'] or Decimal('0')
        gross_wt = totals['gross_wt'] or Decimal('0')
        total_roll = totals['total_roll'] or Decimal('0')

        dyed_fabric_inward_table.objects.filter(id=master_id).update(
            total_wt=gross_wt,
            total_roll=total_roll,
            updated_on=datetime.now()
        )

        return {
            'total_roll': str(total_roll),
            'total_gross': str(gross_wt),
        }

    except Exception as e:
        return {'error': str(e)}
    
