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


def loose_pcs_entry(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_ironing=1)
        fabric_program = fabric_program_table.objects.filter(status=1) 
        delivery = parent_packing_outward_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        return render(request,'loose_pcs_entry/loose_pcs_entry_list.html',{'party':party,'fabric_program':fabric_program,'delivery':delivery,'quality':quality,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    


def generate_inward_num_series():
    last_purchase = parent_lp_entry_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_no:
        match = re.search(r'INW-(\d+)', last_purchase.inward_no)
        if match:
            next_num = int(match.group(1)) + 1 
        else: 
            next_num = 1
    else:
        next_num = 1
 
    return f"INW-{next_num:03d}"


def loose_pcs_entry_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        # party = party_table.objects.filter(status=1, is_cutting=1) 

        party = party_table.objects.filter(status=1).filter(is_stiching=1) | party_table.objects.filter(status=1).filter(is_ironing=1)



        fabric_program = fabric_program_table.objects.filter(status=1) 
        inward_no = generate_inward_num_series()

        quality = quality_table.objects.filter(status=1)  
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)

        child_orders = packing_deivery_balance_table.objects.filter( 
            # balance_quantity__gt=0
        ).values_list('outward_id', flat=True)
        print('child_orders:',child_orders)



        stiching = parent_stiching_outward_table.objects.filter(status=1,is_packing=1).values('id', 'outward_no', 'work_order_no','total_quantity').order_by('-id')
        orders = list(parent_packing_outward_table.objects.filter(
            id__in=child_orders,
            status=1
        ).values('id', 'outward_no', 'work_order_no','total_quantity').order_by('-id'))
        # ✅ Correct placement — aggregate totals outside the loop
        totals = packing_deivery_balance_table.objects.filter(
            # balance_quantity__gt=0
        ).aggregate(
            po_quantity=Sum('po_quantity'),
            inward_quantity=Sum('in_quantity'),
            balance_quantity=Sum('balance_quantity') 
        )  

        return render(request, 'loose_pcs_entry/add_loose_pcs_delivery.html', {
            'party': party,
            'fabric_program': fabric_program,
            'inward_no': inward_no,
            'color': color,
            'orders': orders,
            'balance_quantity': float(totals['balance_quantity'] or 0),
            'po_quantity': float(totals['po_quantity'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0),
            'quality': quality,
            'style': style,
            'size': size,
            'stiching':stiching
        })
    else:
        return HttpResponseRedirect("/admin")





from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from itertools import chain
from django.db.models import Sum, F, Value, IntegerField, ExpressionWrapper

# @csrf_exempt
# def get_lp_party_outward_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=400)

#     party_id = request.POST.get('party_id')
#     if not party_id:
#         return JsonResponse({'error': 'Party ID is required'}, status=400)

#     try:
#         # Packing outward
#         packing_outward = list(parent_packing_outward_table.objects.filter(
#             party_id=party_id, status=1
#         ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

#         for p in packing_outward:
#             p['type'] = 'P'

#         # Stitching outward
#         stitching_outward = list(parent_stiching_outward_table.objects.filter(
#             party_id=party_id, is_packing=1, status=1
#         ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

#         for s in stitching_outward:
#             s['type'] = 'SP'

#         # Combine all outward records
#         combined_outward = packing_outward + stitching_outward

#         # Process inward quantities for each outward
#         for outward in combined_outward:
#             outward_no = outward['outward_no']
#             outward_id = outward['id']

#             # Find related inward records
#             inwards = parent_packing_inward_table.objects.filter(
#                 outward_id=outward_id, party_id=party_id, status=1
#             ).values('id')

#             # Get inward IDs
#             inward_ids = [inward['id'] for inward in inwards]

#             # Sum child quantities: box_pcs + loose_pcs + seconds_pcs + shortage_pcs
#             total_inward = child_packing_inward_table.objects.filter(
#                 tm_id__in=inward_ids,status=1
#             ).aggregate(
#                 total_inward_quantity=Sum(
#                     F('box_pcs') + F('loose_pcs') + F('seconds_pcs') + F('shortage_pcs'),
#                     output_field=IntegerField()
#                 )
#             )['total_inward_quantity'] or 0

#             # Add total_inward_quantity to outward record
#             outward['total_inward_quantity'] = total_inward

#         if not combined_outward:
#             return JsonResponse({'error': 'Outward not found for the given party ID'}, status=404)

#         return JsonResponse({'outward': combined_outward})

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum, F, IntegerField
from itertools import chain




@csrf_exempt
def get_lp_party_outward_lists(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    party_id = request.POST.get('party_id')
    if not party_id:
        return JsonResponse({'error': 'Party ID is required'}, status=400)

    try:
        # Packing outward
        packing_outward = list(parent_packing_outward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

        for p in packing_outward:
            p['type'] = 'P'

        # Stitching outward
        stitching_outward = list(parent_stiching_outward_table.objects.filter(
            party_id=party_id, is_packing=1, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

        for s in stitching_outward:
            s['type'] = 'SP'

        # Combine all outward records
        combined_outward = packing_outward + stitching_outward

        filtered_outward = []

        for outward in combined_outward:
            outward_id = outward['id']
            outward_no = outward['outward_no']
            total_outward_quantity = outward.get('total_quantity', 0) or 0

            # Related inward entries
            inwards = parent_packing_inward_table.objects.filter(
                outward_id=outward_id, party_id=party_id, status=1
            ).values_list('id', flat=True)

            # Total inward quantity
            total_inward_quantity = child_packing_inward_table.objects.filter(
                tm_id__in=inwards, status=1
            ).aggregate(
                total=Sum(
                    F('box_pcs') + F('loose_pcs') + F('seconds_pcs') + F('shortage_pcs'),
                    output_field=IntegerField()
                )
            )['total'] or 0

            # Total loose pcs (from loosepcs table)
            total_loosepcs_quantity = parent_lp_entry_table.objects.filter(
                status=1,
                party_id=party_id,
                packing_id=outward_id  # Assumes packing_id maps to outward ID
            ).aggregate(
                total_loose=Sum('total_quantity')
            )['total_loose'] or 0

            # Final value calculation
            value = total_outward_quantity - total_inward_quantity - total_loosepcs_quantity

            if value > 0:
                outward['total_inward_quantity'] = total_inward_quantity
                outward['total_loosepcs_quantity'] = total_loosepcs_quantity
                outward['value'] = value
                filtered_outward.append(outward)

        if not filtered_outward:
            return JsonResponse({'message': 'No pending outward records found.'}, status=200)

        return JsonResponse({'outward': filtered_outward}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@csrf_exempt
def get_lp_update_party_delivery_list(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    party_id = request.POST.get('party_id')
    if not party_id:
        return JsonResponse({'error': 'Party ID is required'}, status=400)

    try:
        # Packing outward
        packing_outward = list(parent_packing_outward_table.objects.filter(
            party_id=party_id, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

        for p in packing_outward:
            p['type'] = 'P'

        # Stitching outward
        stitching_outward = list(parent_stiching_outward_table.objects.filter(
            party_id=party_id, is_packing=1, status=1
        ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

        for s in stitching_outward:
            s['type'] = 'SP'

        # Combine all outward records
        combined_outward = packing_outward + stitching_outward

        filtered_outward = []

        for outward in combined_outward:
            outward_id = outward['id']
            outward_no = outward['outward_no']
            total_outward_quantity = outward.get('total_quantity', 0) or 0

            # Related inward entries
            inwards = parent_packing_inward_table.objects.filter(
                outward_id=outward_id, party_id=party_id, status=1
            ).values_list('id', flat=True)

            # Total inward quantity
            total_inward_quantity = child_packing_inward_table.objects.filter(
                tm_id__in=inwards, status=1
            ).aggregate(
                total=Sum(
                    F('box_pcs') + F('loose_pcs') + F('seconds_pcs') + F('shortage_pcs'),
                    output_field=IntegerField()
                )
            )['total'] or 0

            # Total loose pcs (from loosepcs table)
            total_loosepcs_quantity = parent_lp_entry_table.objects.filter(
                status=1,
                party_id=party_id,
                packing_id=outward_id  # Assumes packing_id maps to outward ID
            ).aggregate(
                total_loose=Sum('total_quantity')
            )['total_loose'] or 0

            # Final value calculation
            value = total_outward_quantity - total_inward_quantity - total_loosepcs_quantity

            # if value > 0:
            if value :
                outward['total_inward_quantity'] = total_inward_quantity
                outward['total_loosepcs_quantity'] = total_loosepcs_quantity
                outward['value'] = value
                filtered_outward.append(outward)

        if not filtered_outward:
            return JsonResponse({'message': 'No pending outward records found.'}, status=200)

        return JsonResponse({'outward': filtered_outward}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




# @csrf_exempt
# def get_lp_party_outward_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=400)

#     party_id = request.POST.get('party_id')
#     if not party_id:
#         return JsonResponse({'error': 'Party ID is required'}, status=400)

#     try:
#         # Packing outward
#         packing_outward = list(parent_packing_outward_table.objects.filter(
#             party_id=party_id, status=1
#         ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

#         for p in packing_outward:
#             p['type'] = 'P'

#         # Stitching outward
#         stitching_outward = list(parent_stiching_outward_table.objects.filter(
#             party_id=party_id, is_packing=1, status=1
#         ).values('id', 'outward_no', 'work_order_no', 'total_quantity'))

#         for s in stitching_outward:
#             s['type'] = 'SP'

#         # Combine all outward records
#         combined_outward = packing_outward + stitching_outward

#         # Final filtered outward list
#         filtered_outward = []

#         for outward in combined_outward:
#             outward_no = outward['outward_no']
#             outward_id = outward['id']

#             # Find related inward records
#             inwards = parent_packing_inward_table.objects.filter(
#                 outward_id=outward_id, party_id=party_id, status=1
#             ).values('id')

#             inward_ids = [inward['id'] for inward in inwards]

#             # Sum child inward quantities
#             total_inward = child_packing_inward_table.objects.filter(
#                 tm_id__in=inward_ids, status=1
#             ).aggregate(
#                 total_inward_quantity=Sum(
#                     F('box_pcs') + F('loose_pcs') + F('seconds_pcs') + F('shortage_pcs'),
#                     output_field=IntegerField() 
#                 )
#             )['total_inward_quantity'] or 0

#             outward['total_inward_quantity'] = total_inward

#             total_loose_pcs = parent_lp_entry_table.objects.filter(status=1,party_id=party_id,packing_id__in=outward_id).aggregate(
#                     total_loose_pcs_quantity = Sum(F('total_quantity'))
#             )
#             print('total-lp-qty:',total_loose_pcs)

#             # Filter if remaining quantity is greater than 0
#             if (outward['total_quantity'] or 0) - total_inward > 0:
#                 filtered_outward.append(outward)

#         if not filtered_outward:
#             return JsonResponse({'message': 'No pending outward records found.'}, status=200)

#         return JsonResponse({'outward': filtered_outward})

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def get_stitching_delivery_lists(request):
    if request.method == 'POST':
        # prg_id = request.POST.get('prg_id')
        prg_id = request.POST.getlist('prg_id')  # ✅ gets list of all selected IDs
        print('p-id:',prg_id)

        if not prg_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            program_value = get_object_or_404(parent_stiching_outward_table, id__in=prg_id)
            quality = get_object_or_404(quality_table, id=program_value.quality_id)
            style = get_object_or_404(style_table, id=program_value.style_id)
            # fabric = get_object_or_404(fabric_program_table, id=program_value.fabric_id)

            # Fetch all related sub cutting program entries
            tx_prg_list = child_stiching_outward_table.objects.filter(tm_id__in=prg_id)


            size_ids = set() 
            for tx_prg in tx_prg_list:
                raw_value = tx_prg.size_id
                if isinstance(raw_value, str): 
                    size_ids.update(
                        int(sid.strip()) for sid in raw_value.split(',') if sid.strip().isdigit()
                    )
                elif isinstance(raw_value, int):
                    size_ids.add(raw_value)

            size_qs = size_table.objects.filter(id__in=size_ids)
            size_id_list = [{'id': s.id, 'name': s.name} for s in size_qs]


            color_ids = set()
            for tx_prg in tx_prg_list:
                raw_value = tx_prg.color_id
                if isinstance(raw_value, str): 
                    color_ids.update(
                        int(sid.strip()) for sid in raw_value.split(',') if sid.strip().isdigit()
                    )
                elif isinstance(raw_value, int):
                    color_ids.add(raw_value)

            color_qs = color_table.objects.filter(id__in=color_ids)
            color_id_list = [{'id': s.id, 'name': s.name} for s in color_qs]

            response_data = {
                'quality': {'id': quality.id, 'name': quality.name},
                'style': {'id': style.id, 'name': style.name},
                'sizes': size_id_list,
                'colors':color_id_list,
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)





@csrf_exempt
def get_packing_delivery_list(request):
    if request.method == 'POST':
        # prg_id = request.POST.get('prg_id')
        prg_id = request.POST.getlist('prg_id')  # ✅ gets list of all selected IDs
        print('p-id:',prg_id)

        if not prg_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            program_value = get_object_or_404(parent_packing_outward_table, id__in=prg_id)
            quality = get_object_or_404(quality_table, id=program_value.quality_id)
            style = get_object_or_404(style_table, id=program_value.style_id)
            # fabric = get_object_or_404(fabric_program_table, id=program_value.fabric_id)

            # Fetch all related sub cutting program entries
            tx_prg_list = child_packing_outward_table.objects.filter(tm_id__in=prg_id)


            size_ids = set() 
            for tx_prg in tx_prg_list:
                raw_value = tx_prg.size_id
                if isinstance(raw_value, str): 
                    size_ids.update(
                        int(sid.strip()) for sid in raw_value.split(',') if sid.strip().isdigit()
                    )
                elif isinstance(raw_value, int):
                    size_ids.add(raw_value)

            size_qs = size_table.objects.filter(id__in=size_ids)
            size_id_list = [{'id': s.id, 'name': s.name} for s in size_qs]


            color_ids = set()
            for tx_prg in tx_prg_list:
                raw_value = tx_prg.color_id
                if isinstance(raw_value, str): 
                    color_ids.update(
                        int(sid.strip()) for sid in raw_value.split(',') if sid.strip().isdigit()
                    )
                elif isinstance(raw_value, int):
                    color_ids.add(raw_value)

            color_qs = color_table.objects.filter(id__in=color_ids)
            color_id_list = [{'id': s.id, 'name': s.name} for s in color_qs]

            response_data = {
                'quality': {'id': quality.id, 'name': quality.name},
                'style': {'id': style.id, 'name': style.name},
                'sizes': size_id_list,
                'colors':color_id_list,
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def get_packing_delivery_lists(request):
    if request.method == 'POST':
        prg_ids = request.POST.getlist('prg_id')  # Retrieve as a list
        print('Received prg_ids:', prg_ids)

        if not prg_ids:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            # Assuming prg_ids contains a list of IDs, process each ID
            program_values = parent_packing_outward_table.objects.filter(id__in=prg_ids)
            if not program_values:
                return JsonResponse({'error': 'No matching programs found'}, status=404)

            # Initialize lists to hold related data 
            quality_list = []
            style_list = []
            size_ids = set()
            color_ids = set()

            for program_value in program_values:
                quality = get_object_or_404(quality_table, id=program_value.quality_id)
                style = get_object_or_404(style_table, id=program_value.style_id)
                tx_prg_list = child_packing_outward_table.objects.filter(tm_id=program_value.id)

                for tx_prg in tx_prg_list:
                    # Assuming size_id and color_id are stored as comma-separated strings
                    size_ids.update(map(int, tx_prg.size_id.split(',')))
                    color_ids.update(map(int, tx_prg.color_id.split(',')))

                quality_list.append({'id': quality.id, 'name': quality.name})
                style_list.append({'id': style.id, 'name': style.name})

            # Fetch related size and color data
            size_qs = size_table.objects.filter(id__in=size_ids)
            color_qs = color_table.objects.filter(id__in=color_ids)

            size_id_list = [{'id': s.id, 'name': s.name} for s in size_qs]
            color_id_list = [{'id': c.id, 'name': c.name} for c in color_qs]

            response_data = {
                'quality': quality_list,
                'style': style_list,
                'sizes': size_id_list,
                'colors': color_id_list,
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



# def get_packing_delivery_list(request):
#     if request.method == 'POST':
#     # and 'party_id' in request.POST:
#     #     party_id = request.POST['party_id']

        
#         child_orders = packing_deivery_balance_table.objects.filter(
#             balance_quantity__gt=0
#         ).values_list('entry_id', flat=True)

#         orders = list(parent_packing_outward_table.objects.filter(
#             id__in=child_orders,
#             status=1
#         ).values('id', 'outward_no','work_order_no').order_by('-id'))

        

#         for order in orders:
#             # order['mill_name'] = mill_map.get(order['mill_id'], '')

#             totals = packing_deivery_balance_table.objects.filter(
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


@csrf_exempt
def insert_loose_pcs_entry(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id') 

        try: 
            # Extracting Data from Request  
            packing_id = request.POST.get('prg_id') 
            party_id = request.POST.get('party_id') 
            print('party:',party_id)
             
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            fab_id = request.POST.get('fab_id')
            style_id = request.POST.get('style_id')
            inward_date = request.POST.get('inward_date')
            entry_data = json.loads(request.POST.get('entry_data', '[]'))
            lot_no = request.POST.get('lot_no')
            work_order_no = request.POST.get('work_order_no')
            print('Chemical Data:', entry_data)  

            def clean_amount(amount):
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()


            # Validate material type (must be either 'yarn' or 'grey')
            material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
            # is_damage = 1 if material_type == 'dye' else 0
            is_damage = 0
            # is_gry_fabric = 1 if material_type == 'grey' else 0

            is_stitching = request.POST.get('is_stitching')
            is_packing = request.POST.get('is_packing')

            # # # Ensure only one of them is set to 1
            # if is_seconds + is_packing != 1:
            #     return JsonResponse({'status': 'error', 'message': 'Select either seconds or  packing !.'}, safe=False)
            
 

            inward_no = generate_inward_num_series()

            # Create Parent Entry (gf_inward_table)
            material_request = parent_lp_entry_table.objects.create(
                inward_no = inward_no.upper(),
                inward_date=inward_date, 
                party_id = party_id,
                packing_id = packing_id,
                work_order_no = work_order_no,
                quality_id=quality_id, 
                style_id=style_id,
                company_id=company_id,
                cfyear = 2025,
                is_damage = is_damage,
                is_packing=is_packing,
                is_stitching= is_stitching, 
                fabric_id=fab_id or 0,
                total_quantity=0,
                remarks=remarks,  
                created_by=user_id,
                created_on=timezone.now()
            ) 
            print('m-req:',material_request)

            po_ids = set()  # Store unique PO IDs to update later

          

            # Initialize a variable to keep track of the total quantity
            total_quantity = 0

            # Create Sub Table Entries
            for cutting in entry_data:
                print("Processing cutting Data:", cutting)

                po_id = cutting.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later

                # Get the quantity for the current item
                current_quantity = cutting.get('quantity', 0)
                
                # Add the current item's quantity to the total
                total_quantity += current_quantity

                sub_entry = child_lp_entry_table.objects.create(
                    work_order_no=work_order_no,
                    tm_id=material_request.id,  
                    quality_id=quality_id,
                    style_id=style_id,
                    size_id=cutting.get('size_id'),  
                    color_id=cutting.get('color_id'),
                    quantity=current_quantity, # Use the correct quantity here
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,
                )

            # After the loop, update the parent entry with the final total quantity
            material_request.total_quantity = total_quantity
            material_request.save()

            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'loose_pcs_entry/add_loose_pcs_delivery.html')

 


def loose_pcs_entry_report_list(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    # cut_prg = request.POST.get('cut_prg', '')
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
    
 
    # if cut_prg:
    #         query &= Q(tm_cutting_prg_id=cut_prg)

    if quality:
            query &= Q(quality_id=quality)

    if style:
            query &= Q(style_id=style)



    # Apply filters
    queryset = parent_lp_entry_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())


    # data = list(cutting_entry_table.objects.filter(status=1).order_by('-id').values())
   
    formatted = [
        {
            'action': '<button type="button" onclick="lp_entry_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="lp_entry_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="lp_entry_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'],item['id']),
                        # # <button type="button" onclick="cutting_entry_abstract_print(\'{}\')" class="btn btn-success btn-xs">Abstract</button>\
                        # <button type="button" onclick="cutting_entry_qrcode_print(\'{}\')" class="btn btn-info btn-xs">QR</button>'.format(item['id'],item['id'],item['id'], item['id'],item['id']),
            'id': index + 1, 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'inward_no': item['inward_no'] if item['inward_no'] else'-', 
            'outward': (
                getOutward_entryNoById(parent_packing_outward_table, item['packing_id'])
                if item.get('is_packing') == 1 else
                getOutward_entryNoById(parent_stiching_outward_table, item['packing_id'])
                if item.get('is_stitching') == 1 else '-'
            ),
            # 'outward':getOutward_entryNoById(parent_packing_outward_table, item['packing_id'] ),  
            'party':getSupplier(party_table, item['party_id'] ), 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'damage': '<span class="badge bg-success">Damage</span>' if item['is_active'] else '<span class="badge bg-danger">Packing</span>',
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 


@csrf_exempt
def lp_entry_print(request):
    po_id = request.GET.get('k') 
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(parent_lp_entry_table, id=order_id)

    prg_details = child_lp_entry_table.objects.filter(tm_id=order_id).values(
        'id', 'quantity', 'size_id', 'color_id'
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

    context = {
        'total_values': total_values,
        'combined_details': combined_details,
        'grand_total': total_quantity,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
    }

    return render(request, 'loose_pcs_entry/lp_entry_print.html', context)







def tx_lp_entry_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting
            child_lp_entry_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except child_lp_entry_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'}) 
    
from django.core.exceptions import ObjectDoesNotExist

def tm_lp_entry_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            parent_lp_entry_table.objects.filter(id=data_id).update(status=0,is_active=0)

            child_lp_entry_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})

 

# def tm_lp_entry_delete(request):
#     if request.method == 'POST': 
#         data_id = request.POST.get('id')
#         try: 
#             # Update the status field to 0 instead of deleting 
#             parent_lp_entry_table.objects.filter(id=data_id).update(status=0,is_active=0)

#             child_lp_entry_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
#             return JsonResponse({'message': 'yes'})
#         except parent_lp_entry_table  & child_lp_entry_table.DoesNotExist:
#             return JsonResponse({'message': 'no such data'}) 
#     else:
#         return JsonResponse({'message': 'Invalid request method'})



def edit_lp_entry(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'loose_pcs_entry/update_lp_delivery.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'loose_pcs_entry/update_lp_delivery.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_lp_entry_table.objects.filter(tm_id=material_id).first()
   
        # Fetch the parent stock instance
        parent_stock_instance = parent_lp_entry_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'loose_pcs_entry/update_lp_delivery.html', {'error_message': 'Parent stock not found.'})

        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        # party = party_table.objects.filter(is_stiching=1,status=1)
        


        party = party_table.objects.filter(status=1).filter(is_stiching=1) | party_table.objects.filter(status=1).filter(is_ironing=1)



        quality = quality_table.objects.filter(status=1) 
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
     
        child_orders = packing_deivery_balance_table.objects.filter(
            # balance_quantity__gt=0
        ).values_list('outward_id', flat=True)
        print('child_orders:',child_orders)

        orders = list(parent_packing_outward_table.objects.filter(
            id__in=child_orders,
            status=1
        ).values('id', 'outward_no', 'work_order_no','total_quantity').order_by('-id'))
        # ✅ Correct placement — aggregate totals outside the loop
        totals = packing_deivery_balance_table.objects.filter(
            # balance_quantity__gt=0
        ).aggregate(
            po_quantity=Sum('po_quantity'),
            inward_quantity=Sum('in_quantity'),
            balance_quantity=Sum('balance_quantity')
        )  

       
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
            'orders':orders
            
        }
        print('style-id:',parent_stock_instance.style_id)
        return render(request, 'loose_pcs_entry/update_lp_delivery.html', context)

    except Exception as e:
        return render(request, 'loose_pcs_entry/update_lp_delivery.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



def tx_lp_entry_list(request):
    tm_id = request.POST.get('id')

    # Fetch child data
    child_qs = child_lp_entry_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')

    if child_qs.exists():
        # Calculate total quantity and total weight from child table
        total_quantity = child_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Fetch master cutting entry
        parent_data = parent_lp_entry_table.objects.filter(id=tm_id).first()

        if not parent_data:
            return JsonResponse({'message': 'error', 'error_message': 'Loose piece entry Entry not found in parent table'})

        # Convert child queryset to list
        child_data = list(child_qs.values())
      

        formatted_data = []

        for index, item in enumerate(child_data):
            size_name = getSupplier(size_table, item['size_id']) or ''
            color_name = getSupplier(color_table, item['color_id']) or ''
            quality_id = parent_data.quality_id or ''
            style_id = parent_data.style_id or ''

            formatted_data.append({
                'action': f'<button type="button" onclick="lp_entry_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '
                        f'<button type="button" onclick="tx_lp_entry_delete(\'{item["id"]}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>',
                'id': index + 1,
                'size': size_name,
                'color': color_name,
                'quantity': item['quantity'] if item['quantity'] else '-',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            })


        print('b-dat:',formatted_data)


        # Prepare master values for summary
        summary_data = {  
            'total_quantity': total_quantity,
       
        }

        return JsonResponse({
            'data': formatted_data,
            **summary_data
        })

    else:
        return JsonResponse({'message': 'error', 'error_message': 'No cutting program data found for this TM ID'})


def loose_pcs_data_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = child_lp_entry_table.objects.filter(id=item_id).values()  
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  


from django.http import JsonResponse

def check_existing_lp_entry(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        size_id = request.POST.get('size_id')
        color_id = request.POST.get('color_id') 

        # Check if a record with the same tm_id, size_id, and color_id exists
        existing_entry = sub_cutting_entry_table.objects.filter(
            tm_id=tm_id, size_id=size_id, color_id=color_id
        ).first()

        if existing_entry:
            return JsonResponse({'exists': True, 'existing_id': existing_entry.id})
        else:
            return JsonResponse({'exists': False})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_lp_data(request):
    if request.method == 'POST':
        master_id = request.POST.get('id')  # The ID of the row (if updating)
        tm_id = request.POST.get('tm_id')   # The transaction master ID 
        size_id = request.POST.get('size_id')  
        color_id = request.POST.get('color_id')
        quantity = request.POST.get('quantity')

        print('tm-id:', tm_id) 

        # Validate required fields
        if not tm_id or not size_id or not quantity:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Check if the same tm_id, size_id, and color_id already exist
            existing_item = child_lp_entry_table.objects.filter( 
                id=master_id,
                tm_id=tm_id,
                size_id=size_id,
                color_id=color_id
            ).first()
 
            if existing_item:
                # Update existing entry
                existing_item.quantity = quantity
                existing_item.save()
                
                updated_totals = update_values(tm_id)  # Update totals
                return JsonResponse({'success': True, 'updated': True, **updated_totals})

            else:
                # Create a new row if no existing entry
                child_item = child_lp_entry_table.objects.create(
                    tm_id=tm_id,  
                    color_id=color_id,
                    size_id=size_id,
                    quantity=quantity,
                    status=1,
                    is_active=1
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
        tx = child_lp_entry_table.objects.filter(tm_id=tm, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')

        # Update values in parent_po_table 
        parent_lp_entry_table.objects.filter(id=tm).update(
            total_quantity=total_quantity,
 
        )

        # Return updated values for frontend update
        return {
            'total_quantity': total_quantity,
   
        }

    except Exception as e: 
        return {'error': str(e)}