# from shlex import join
from traceback import print_tb
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify
from numpy import delete

from accessory.models import *
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

from yarn.models import * 
from program_app.models import * 
from user_auth.models import * 
from company.models import * 
from employee.models import * 
from django.utils.timezone import make_aware

from software_app.views import fabric_program, getItemNameById, getSupplier, is_ajax


# `````````````````````````````````````````````````````````````````````````````````


def grey_fabric_inward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1) 
        # party = party_table.objects.filter(status=1,is_supplier=1)
        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
 
        yarn_count = count_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        from django.db.models import Sum, FloatField, ExpressionWrapper, F

        lot = (
            gf_inward_table.objects
            .filter(status=1)
            .values('lot_no')  # Group by lot_no
            .annotate(
                total_gross_wt=Sum('total_gross_wt'),
             
            )
            .order_by('lot_no')
        )

        return render(request,'inward/grey_fabric_inward.html',{'supplier':supplier,'party':party,'product':product,'yarn_count':yarn_count,'lot':lot})
    else:
        return HttpResponseRedirect("/admin")




# ```````````````````````````` grey fabric inward add ``````````````````



def generate_inward_num_series():
    last_purchase = gf_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_number:
        match = re.search(r'IN-(\d+)', last_purchase.inward_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
 
    return f"IN-{next_num:03d}"




def grey_fab_inward_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
       
        product = product_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)

        fabric_program_qs = fabric_program_table.objects.filter(status=1) 

        linked_knitting_ids = grey_fabric_po_table.objects.values('program_id')

        # Filter knitting_table
        knitting = knitting_table.objects.filter(status=1, is_grey_fabric=1).exclude(id__in=linked_knitting_ids)
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

        party = party_table.objects.filter(status=1).filter(is_trader=1)
        # party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)

        knitting_party = party_table.objects.filter(status=1,is_knitting=1)
        out_party = party_table.objects.filter(status=1,is_process=1)
        tex = tex_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
        inward_number = generate_inward_num_series()
        print('in-no:',inward_number) 
        return render(request, 'inward/grey_fabric_inward_add.html', {
            'knitting_party': knitting_party,
            'party': party,
            'out_party':out_party,
            'product': product,
            'count':count,
            'fabric_program':fabric_program,
            'inward_number': inward_number,
            'tex':tex,
            'gauge':gauge,
            'dia':dia,
            'knitting':knitting,
        }) 
    else:
        return HttpResponseRedirect("/admin")




def get_grey_fabric_po_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('party-id:',supplier_id)

        if supplier_id:
            child_orders = grey_fab_po_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).values_list('po_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(grey_fabric_po_table.objects.filter(
                id__in=child_orders,
                status=1
            ).values('id', 'po_number', 'name','lot_no', 'party_id').order_by('-id'))

          
            totals = grey_fab_po_balance_table.objects.filter(
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




def get_po_knitting_list(request):
    if request.method == 'POST':
        po_id = request.POST.get('po_id')
        if not po_id:
            return JsonResponse({'mills': []})  # Safe fallback

        try:
            po = grey_fabric_po_table.objects.filter(status=1,id=po_id).first()
            party = party_table.objects.filter(id=po.knitting_id).first()
 
            if party and party.is_knitting == 1:
                # Supplier is itself a mill
                return JsonResponse({'mills': [{'id': party.id, 'name': party.name}]})
            else:
                # Get all other mills
                mills = party_table.objects.filter(is_knitting=1)
                mills_data = [{'id': mill.id, 'name': mill.name} for mill in mills]
                return JsonResponse({'mills': mills_data})
        except Exception as e:
            return JsonResponse({'mills': [], 'error': str(e)}, status=500)

    return JsonResponse({'mills': []}, status=405)



from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only if you don't want to handle CSRF tokens for this view (not recommended for production)
def get_party_list(request):
    # material_type = request.POST.get('material_type')

    if request.method == 'POST' and 'material_type' in request.POST: 
        material_type = request.POST['material_type']
        print('m-type:',material_type)
        if material_type == 'yarn':
            parties = party_table.objects.filter(is_knitting=1, status=1).order_by('name')
        elif material_type == 'grey':

            parties = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1).order_by('name')



            # parties = party_table.objects.filter(is_trader=1,status=1) | party_table.objects.filter(is_mill=1,status=1)
        else:
            parties = party_table.objects.none()

        data = [{"id": p.id, "name": p.name} for p in parties]
    return JsonResponse(data, safe=False)



@csrf_exempt
def get_grey_po_deliver_lists(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    po_id = request.POST.get('po_list')
    tm_inward_id = request.POST.get('tm_id')

    if not po_id:
        return JsonResponse({"error": "PO ID not provided"}, status=400)

    try:
        # ------------------- Core Initial Queries -------------------
        child_orders = grey_fab_po_balance_table.objects.filter(
            po_id=po_id, balance_quantity__gt=0
        ).values('po_id')

        order_number = grey_fabric_po_table.objects.filter(
            id__in=child_orders, status=1
        ).values('id', 'po_number', 'name', 'lot_no').order_by('name')

        totals = grey_fab_po_balance_table.objects.filter(
            po_id=po_id, balance_quantity__gt=0
        ).aggregate(
            po_roll=Sum('ord_roll_wt'),
            po_quantity=Sum('po_quantity'),
            inward_quantity=Sum('in_quantity'),
            balance_quantity=Sum('balance_quantity'),
        )

        program_id_list = list(
            grey_fab_po_balance_table.objects.filter(
                po_id=po_id, balance_quantity__gt=0
            ).values_list('program_id', flat=True).distinct()
        )

        program_qs = grey_fab_program_balance_table.objects.filter(
            balance_quantity__gt=0, program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(knitting_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'knitting_number', 'name', 'total_quantity'))

        raw_balances = yarn_outward_available_wt_table.objects.filter(
            program_id__in=program_qs
        ).values_list(
            'program_id', 'dia_id', 'pg_roll', 'pg_wt',
            'in_rolls', 'in_wt', 'balance_roll', 'balance_wt'
        )

        formatted_data = [
            {
                'program_id': row[0],
                'dia_id': row[1],
                'pg_roll': row[2],
                'pg_wt': row[3],
                'in_rolls': row[4],
                'in_wt': row[5],
                'balance_roll': row[6],
                'balance_wt': row[7]
            }
            for row in raw_balances
        ]

        sub_po = grey_fabric_po_table.objects.filter(id=po_id, status=1).first()

        # ------------------ Inward ID Handling ------------------
        inward_ids = []
        if tm_inward_id:
            inward_ids = list(gf_inward_table.objects.filter(
                id=tm_inward_id, status=1
            ).values_list('id', flat=True))

        # Fallback if no inward IDs found from tm_inward_id
        if not inward_ids:
            inward_ids = list(gf_inward_table.objects.filter(
                po_id=po_id, status=1
            ).values_list('id', flat=True))

        # ------------------ Program Detail Loop ------------------
        program_details = []
        for pid in program_id_list:
            knit = knitting_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            sub_knits = sub_knitting_table.objects.filter(tm_id=knit.id, status=1)
            for sub in sub_knits:
                products = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_program_data = []

                for fp in products:
                    fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
                    fabric_program_data.append({
                        'id': fp.id,
                        'name': fp.name,
                        'fabric_id': fp.fabric_id,
                        'fabric_name': fabric_item.name if fabric_item else 'N/A'
                    })

                gauge = gauge_table.objects.filter(id=sub.gauge).first()
                tex = tex_table.objects.filter(id=sub.tex).first()
                dia = dia_table.objects.filter(id=sub.dia).first()
                yarn = count_table.objects.filter(id=sub.count_id).first()

                inward_roll_sum = sub_gf_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia,
                    status=1
                ).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = sub.rolls - inward_roll_sum
                inward_quantity = inward_roll_sum * sub.wt_per_roll
                total_wt_balance = sub.rolls * sub.wt_per_roll

                program_details.append({
                    'program_id': sub.tm_id,
                    'program_name': knit.name,
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
                    'yarn_count': yarn.name if yarn else '',
                    'yarn_count_id': sub.count_id,
                    'gauge': gauge.name if gauge else '',
                    'gauge_id': sub.gauge,
                    'tex': tex.name if tex else '',
                    'tex_id': sub.tex,
                    'gsm': sub.gsm,
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia,
                    'lot_roll': remaining_roll,
                    'per_roll_wt': sub.wt_per_roll,
                    'lot_roll_wt': total_wt_balance - inward_quantity,
                    'quantity': sub.quantity,
                    'po_id': po_id,
                    'total_roll': inward_roll_sum,
                    'total_wt': inward_quantity,
                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia
                    ]
                })

        # ------------------ Delivery Order Data ------------------
        order_data = []
        deliveries = sub_gf_inward_table.objects.filter(
            tm_id__in=inward_ids,
            status=1
        )

        for delivery in deliveries:
            program = knitting_table.objects.filter(id=delivery.program_id).first()
            if not program:
                continue

            product = fabric_program_table.objects.filter(id=delivery.fabric_id).first()
            yarn_count = count_table.objects.filter(id=delivery.yarn_count_id).first()
            gauge = gauge_table.objects.filter(id=delivery.gauge_id).first()
            tex = tex_table.objects.filter(id=delivery.tex_id).first()

            inward_totals = sub_gf_inward_table.objects.filter(
                tm_id=delivery.tm_id, party_id=delivery.party_id, is_active=1
            ).aggregate(
                inward_roll=Sum('roll'),
                inward_quantity=Sum('wt_per_roll'),
                inward_gross=Sum('gross_wt')
            )

            inward_roll = inward_totals.get('inward_roll') or 0
            inward_quantity = inward_totals.get('inward_quantity') or 0
            inward_gross = inward_totals.get('inward_gross') or 0

            order_data.append({
                'po_roll': delivery.roll or 0,
                'total_rolls': delivery.roll or 0,
                'po_quantity': delivery.gross_wt or 0,
                'inward_roll': inward_roll,
                'inward_quantity': inward_quantity,
                'inward_gross_wt': inward_gross,
                'balance_quantity': (delivery.wt_per_roll or 0) - inward_quantity,
                'tax_value': 5,
                'fabric_id': delivery.fabric_id,
                'yarn_count_id': delivery.yarn_count_id,
                'gauge_id': delivery.gauge_id,
                'tex_id': delivery.tex_id,
                'gsm': delivery.gsm,
                'dia': delivery.dia_id,
                'program_id': delivery.program_id,
                'wt_per_roll': sub_po.total_roll_wt if sub_po else 0,
                'roll': delivery.roll or 0,
                'per_roll': delivery.wt_per_roll,
                'tx_quantity': delivery.wt_per_roll,
                'quantity': delivery.gross_wt or 0,
                'gross_wt': delivery.gross_wt or 0,
                'id': delivery.program_id,
                'tm_id': po_id,
                'tx_id': delivery.id,
                'total_quantity': delivery.total_wt or 0,
                'total_gross_wt': delivery.gross_wt or 0,
                'total_roll': delivery.roll or 0,
                'product': product.name if product else '',
            })

        # ------------------ Response ------------------
        return JsonResponse({
            'orders': list(order_number),
            'po_roll': float(totals['po_roll'] or 0),
            'balance_wt': 0,
            'balance_quantity': 0,
            'po_quantity': float(totals['po_quantity'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0),
            'program_id': program_id_list,
            'wt_per_roll': sub_po.total_roll_wt if sub_po else 0,
            'quantity': 0,
            'program': prg_list,
            'order_data': order_data,
            'program_details': program_details
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def grey_fabric_po_detail_report(request):
    if request.method == 'POST':
        master_id = request.POST.get('po_id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data 
                child_data = grey_fabric_po_program_table.objects.filter(po_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = sum(
                        (item.rolls or 0) * (item.roll_wt or 0)
                        for item in child_data
                    )


                    # Format child PO data for response
                    formatted_data = []
                    for index, item in enumerate(child_data.values(), start=1):
                        formatted_data.append({
                            'action': f'''
                                <button type="button" onclick="knitting_prg_detail_edit('{item['id']}')" class="btn btn-primary btn-xs">
                                    <i class="feather icon-edit"></i>
                                </button>
                                <button type="button" onclick="knitting_detail_delete('{item['id']}')" class="btn btn-danger btn-xs">
                                    <i class="feather icon-trash-2"></i>
                                </button>
                            ''',
                            'id': index,
                            'fabric_id': getItemNameById(fabric_program_table, item['fabric_id']),
                            'count': getItemNameById(count_table, item['yarn_count_id']),
                            'gauge': getItemNameById(gauge_table, item['gauge_id']),
                            'tex': getItemNameById(tex_table, item['tex_id']),
                            'dia': getItemNameById(dia_table, item['dia_id']),

                             # Raw IDs (hidden in table or used in JS only)
                            'fabric_id_raw': item['fabric_id'],
                            'count_id_raw': item['yarn_count_id'],
                            'gauge_id_raw': item['gauge_id'],
                            'gsm': item['gsm'],
                            'tex_id_raw': item['tex_id'],
                            'dia_id_raw': item['dia_id'],



                            'rolls': item['rolls'] or '-',
                            'wt_per_roll': item['roll_wt'] or '-',
                            # 'rate': item['rate'] or '-',
                            'quantity': item['rolls'] * item['roll_wt'],
                            # (item['rolls'] && item['wt_per_roll']) ? (item['rolls'] * item['wt_per_roll']).toFixed(2) : '-',

                            # 'total_amount': item['total_amount'] or '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': float(total_quantity),  # Convert to float for JSON compatibility
                        # 'total_amount': float(total_amount),
                     
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})




@csrf_exempt
def tx_load_gf_po_details_inward(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')
        deliver_ids = request.GET.getlist('deliver_to')

        if not po_ids or not deliver_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) and Delivery ID(s) are required.'}, status=400)

        try:
            parent_pos = grey_fabric_po_table.objects.filter(id__in=po_ids, party_id=supplier_id)
            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            total_po_roll = Decimal('0.00')
            total_po_quantity = Decimal('0.00')
            total_inward_roll = Decimal('0.00')
            total_inward_quantity = Decimal('0.00')

            for po in parent_pos:
                # Group by party_id and sum bag and quantity
                deliveries = sub_grey_fabric_po_table.objects.filter(
                    po_id=po.id,
                    party_id__in=deliver_ids,
                    status=1
                ).values('party_id').annotate(
                    total_roll=Sum('roll'),
                    total_quantity=Sum('roll_wt')
                )

                child = grey_fabric_po_table.objects.filter(id=po.id, is_active=1).first()
                if not child:
                    continue

                # product = fabric_program_table.objects.filter(id=child.fabric_id).first()
                program = knitting_table.objects.filter(id=child.program_id).first()
                total_roll = Decimal(child.total_roll or 0)
                total_quantity = Decimal(child.total_roll_wt or 0)

                for delivery in deliveries:
                    party_id = delivery['party_id']
                    po_roll = Decimal(delivery['total_roll'] or 0)
                    po_quantity = Decimal(delivery['total_quantity'] or 0)

                    inward_totals = sub_gf_inward_table.objects.filter(
                        po_id=po.id,
                        outward_party_id=party_id,
                        is_active=1
                    ).aggregate(
                        inward_roll=Sum('roll'),
                        inward_quantity=Sum('wt_per_roll')
                    )

                    inward_roll = Decimal(inward_totals.get('inward_roll') or 0)
                    inward_quantity = Decimal(inward_totals.get('inward_quantity') or 0)

                    balance_roll = po_roll - inward_roll
                    balance_quantity = po_quantity - inward_quantity

                    if balance_roll <= 0 and balance_quantity <= 0:
                        continue

                    total_po_roll += po_roll
                    total_po_quantity += po_quantity
                    total_inward_roll += inward_roll
                    total_inward_quantity += inward_quantity

                    order_data.append({
                        'party_id': party_id,
                        'po_roll': float(po_roll),
                        'po_quantity': float(po_quantity),
                        'inward_roll': float(inward_roll),
                        'inward_quantity': float(inward_quantity),
                        'balance_roll': float(balance_roll),
                        'balance_quantity': float(balance_quantity),
                        # 'product_id': child.yarn_count_id,
                        # 'product_name': product.name if product else "Unknown Product",
                        'tax_value': 5,
                        'roll': float(balance_roll),
                        'roll_wt': float(child.total_roll_wt or 0),
                        'tx_quantity': float(po_quantity),
                        'quantity': float(total_quantity),
                      
                        'gross_wt': 0,
                        'id': child.id,
                        'po_id': po.id,
                        'tm_id': po.id,
                        'total_quantity': float(total_quantity),
                        'total_roll': float(total_roll)
                    })

            balance_roll = total_po_roll - total_inward_roll
            balance_quantity = total_po_quantity - total_inward_quantity

            return JsonResponse({
                'orders': order_data,
                'po_roll_wt': float(total_po_roll),
                'po_quantitys': float(total_po_quantity),
                'inward_roll': float(total_inward_roll),
                'inward_quantity': float(total_inward_quantity),
                'balance_roll': float(balance_roll),
                'balance_quantity': float(balance_quantity),
                'roll_wt': order_data[0]['roll_wt'] if order_data else 0
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



# `````````````````````````````` by yarn outward ``````````````````````````````



from django.db.models import Sum, Max

@csrf_exempt
def get_lot_lists(request): 
    if request.method == 'POST' and 'supplier_id' in request.POST: 
        supplier_id = request.POST['supplier_id']
        print('party-id:', supplier_id)

        if supplier_id:
            # Step 1: Get child orders with balance
            child_orders = yarn_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                balance_wt__gt=0
            ).values_list('out_id', flat=True) 

            print('balance-data:', child_orders)

            # Step 2: Group by lot_no
            orders = (
                yarn_delivery_table.objects
                .filter(id__in=child_orders, status=1,is_active=1)
                .values('lot_no')
                .annotate(
                    id=Max('id'),  # You can change to Min('id') if needed
                    do_number=Max('do_number'),  # Assuming latest one is desired
                    total_quantity=Sum('total_quantity')
                )
                .order_by('-id')
            )

            # Step 3: Totals for overall PO weight and balances
            totals = yarn_out_available_balance_table.objects.filter(
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




def get_outward_list(request):
    if request.method == 'POST' and 'lot_no' in request.POST: 
        supplier_id = request.POST['supplier_id']
        lot_no = request.POST.get('lot_no')
        print('party-id:',lot_no)

        if lot_no:
            child_orders = yarn_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                lot_no=lot_no,
                balance_wt__gt=0
            ).values_list('out_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(yarn_delivery_table.objects.filter(  
                id__in=child_orders, 
                status=1
            ).values('id', 'do_number', 'lot_no','total_quantity').order_by('-id'))

            totals = yarn_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                lot_no=lot_no,
                balance_wt__gt=0
            ).aggregate(
                outward_wt=Sum('outward_wt'),
                inward_wt=Sum('inward_wt'),
                
                balance_wt=Sum('balance_wt')
            ) 

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
            })  

    return JsonResponse({'orders': []})
 

def get_yarn_outward_details(request):
    if request.method == 'POST' and 'outward_id' in request.POST:
        outward_id = request.POST['outward_id']
        print('outward-id:', outward_id)

        try:
            outward = yarn_delivery_table.objects.get(status=1, id=outward_id)
            program = knitting_table.objects.get(status=1, id=outward.program_id)  # use _id for FK
            prg_data = sub_knitting_table.objects.get(status=1, id=outward.program_id)  # use _id for FK
            fabric = fabric_program_table.objects.get(status=1, id=prg_data.fabric_id)  # use _id for FK

            response_data = {
                'program_id': outward.program_id,
                'program_number': program.knitting_number,  
                'total_quantity': outward.total_quantity,
                'fabric_id': prg_data.fabric_id,  
                'tex_id': prg_data.tex,  
                'gauge_id': prg_data.gauge, 
                'dia_id': prg_data.dia, 
                'gsm': prg_data.gsm,  
                'fabric_id': prg_data.fabric_id, 
                'fabric_name': fabric.name ,  # optional
                # Add more fields as needed
            }

            return JsonResponse({'status': 'success', 'data': response_data})
        
        except yarn_delivery_table.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Outward record not found'})
        except knitting_table.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Program record not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


from grey_fabric.models import *

 

@csrf_exempt
def get_outward_detail_lists(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # out_id = request.POST.get('outward_list')
     # Get the comma-separated string from POST
    out_id_str = request.POST.get('outward_list', '')  # e.g. "6,5"

    # Split string by comma to get a list of IDs
    out_id = [x.strip() for x in out_id_str.split(',') if x.strip()]

    print('out-ids:', out_id)  # ['6', '5']

    tm_inward_id = request.POST.get('tm_id')
    print('out-ids:',out_id)
  
   
    try:
        # Get child orders with balance 
        child_orders = yarn_out_available_balance_table.objects.filter(
            out_id__in=out_id, balance_wt__gt=0
        ).values('out_id') 

        order_number = yarn_delivery_table.objects.filter( 
            id__in=child_orders, status=1
        ).values('id', 'do_number', 'lot_no').order_by('-id')
        print('ord:',order_number)
        totals = yarn_out_available_balance_table.objects.filter(
            out_id__in=out_id, balance_wt__gt=0
        ).aggregate(
            po_roll=Sum('outward_wt'), 
            outward_wt=Sum('outward_wt'),
            inward_quantity=Sum('inward_wt'), 
            balance_wt=Sum('balance_wt'),
        ) 
        print('totals:',totals)

        program_id_list = list(
            yarn_out_available_balance_table.objects.filter(
                out_id__in=out_id, balance_wt__gt=0
            ).values_list('program_id', flat=True).distinct()
        )


        program_qs = grey_fab_program_balance_table.objects.filter(
            balance_quantity__gt=0, program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(knitting_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'knitting_number', 'name', 'total_quantity'))

        
        # program = yarn_outward_available_wt_table.objects.filter(program_id__in=program_qs).values_list('program_id','pg_roll','pg_wt','in_rolls', 'in_wt','balance_roll','balance_wt')
       
        # program = list(
        #     yarn_outward_available_wt_table.objects.filter(program_id__in=program_qs)
        #     .values_list('program_id','pg_roll','pg_wt','in_rolls', 'in_wt','balance_roll','balance_wt')
        # )
        program = list(
            yarn_outward_available_wt_table.objects.filter(program_id__in=program_qs)
            .values_list('program_id','dia_id','pg_roll','pg_wt','in_rolls', 'in_wt','balance_roll','balance_wt')
        )


        formatted_data = [
        {
            'program_id': row[0],
            'dia_id': row[1],
            'pg_roll': row[2],
            'pg_wt': row[3],
            'in_rolls': row[4],
            'in_wt': row[5],
            'balance_roll': row[6],
            'balance_wt': row[7]
        }
        for row in program
    ]
        print('programs:',program)
        po_total_roll = totals['po_roll'] or 0
        # balance_roll = po_total_roll - (totals['inward_roll'] or 0)

        sub_po = yarn_delivery_table.objects.filter(id__in=out_id, status=1).first()

        order_data = []
        
        # List fabric/gauge/tex/gsm/dia for each program_id regardless of delivery
        program_details = []
        program_seen_keys = set()  # To track unique combinations

        for pid in program_id_list:
            knit = knitting_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            prg_name = f"{knit.name}"
            # prg_name = f"{knit.name} - {knit.total_quantity}" 
            sub_knits = sub_knitting_table.objects.filter(tm_id=knit.id, status=1).order_by('dia')

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
                            'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                        })
                    except fabric_table.DoesNotExist:
                        fabric_program_data.append({
                            'id': fp.id,
                            'name': fp.name,
                            'fabric_id': fp.fabric_id,
                            'fabric_name': 'N/A'
                        })

                gauge = gauge_table.objects.filter(id=sub.gauge).first()
                tex = tex_table.objects.filter(id=sub.tex).first()
                dia = dia_table.objects.filter(id=sub.dia).first()
                yarn = count_table.objects.filter(id=sub.count_id).first()

                key = (sub.tm_id, sub.dia, sub.fabric_id)  # composite key to avoid duplicates
                if key in program_seen_keys:
                    continue
                program_seen_keys.add(key)

                inward_ids = list(
                    gf_inward_table.objects.filter(outward_id__in=out_id, status=1).values_list('id', flat=True)
                )
                inward_roll_sum = sub_gf_inward_table.objects.filter(
                    tm_id__in=inward_ids, dia_id=sub.dia, status=1
                ).aggregate(total=Sum('roll'))['total'] or 0

                remaining_roll = (sub.rolls or 0) - inward_roll_sum
                total_wt_balance = (sub.rolls or 0) * (sub.wt_per_roll or 0)
                inward_quantity = inward_roll_sum * (sub.wt_per_roll or 0)


                # Get out_ids related to this specific program_id
                related_out_ids = yarn_out_available_balance_table.objects.filter(
                    program_id=pid, out_id__in=out_id
                ).values_list('out_id', flat=True).distinct()

                for oid in related_out_ids:
                    inward_ids = list(gf_inward_table.objects.filter(outward_id=oid, status=1).values_list('id', flat=True))

                    inward_roll_sum = sub_gf_inward_table.objects.filter(
                        tm_id__in=inward_ids, dia_id=sub.dia, status=1
                    ).aggregate(total=Sum('roll'))['total'] or 0

                    remaining_roll = (sub.rolls or 0) - inward_roll_sum
                    total_wt_balance = (sub.rolls or 0) * (sub.wt_per_roll or 0)
                    inward_quantity = inward_roll_sum * (sub.wt_per_roll or 0)



                program_details.append({
                    'program_id': sub.tm_id or 0,
                    'program_name': prg_name or '',
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
                    'yarn_count': yarn.name if yarn else '',
                    'yarn_count_id': sub.count_id,
                    'gauge': gauge.name if gauge else '',
                    'gauge_id': sub.gauge,
                    'tex': tex.name if tex else '',
                    'tex_id': sub.tex,
                    'gsm': sub.gsm,
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia,
                    'lot_roll': remaining_roll,
                    'per_roll_wt': sub.wt_per_roll,
                    'lot_roll_wt': total_wt_balance - inward_quantity,
                    'quantity': sub.quantity,
                    'out_id': oid,   # optional: remove to avoid misleading data
                    'total_roll': inward_roll_sum,
                    'total_wt': inward_quantity,
                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia
                    ]
                })

     
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
                            'wt_per_roll': sub_po.total_quantity if sub_po else 0,
                            'roll': remaining_roll_wt,
                            'per_roll': delivery.wt_per_roll,
                            'tx_quantity': qty,
                            'quantity': remaining_quantity,
                            'gross_wt': 0,
                            'id': program.id,
                            'out_id': po.id,
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
            'po_quantity': float(totals['outward_wt'] or 0),
            # 'inward_roll': float(totals['inward_roll'] or 0),
            'inward_quantity': float(totals['inward_quantity'] or 0), 
            'program_id': program_id_list,
            # 'roll': balance_roll,
            'wt_per_roll': sub_po.total_quantity if sub_po else 0,
            'quantity': 0,#float(totals['balance_wt'] or 0),
            'program': prg_list,
            'order_data': order_data,
            'program_details': program_details  # ✅ fabric, gauge, tex, gsm, dia per program_id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    







def get_lot_outward_list(request):
    if request.method == 'POST' and 'lot_no' in request.POST: 
        supplier_id = request.POST['supplier_id']
        lot_no = request.POST.get('lot_no')
        print('party-id:',lot_no)

        if lot_no:
            child_orders = yarn_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                lot_no=lot_no,
                # balance_wt__gt=0
            ).values_list('out_id', flat=True)
            print('balance-data:',child_orders)
            orders = list(yarn_delivery_table.objects.filter( 
                id__in=child_orders, 
                status=1
            ).values('id', 'do_number', 'lot_no','total_quantity').order_by('-id'))

            totals = yarn_out_available_balance_table.objects.filter(
                party_id=supplier_id,
                lot_no=lot_no,
                # balance_wt__gt=0
            ).aggregate(
                outward_wt=Sum('outward_wt'),
                inward_wt=Sum('inward_wt'),
                
                balance_wt=Sum('balance_wt')
            ) 

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
            })

    return JsonResponse({'orders': []})


# @csrf_exempt
# def get_yarn_deliver_edit_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=405)

#     try:
#         out_id_str = request.POST.get('outward_list', '')
#         tm_inward_id = request.POST.get('tm_id')
#         po_id = request.POST.get('po_id')

#         out_id = out_id_str.split(',') if out_id_str else []
#         all_out_ids = list(set(out_id))
#         print('out-id:',out_id)
#         # Get already inwarded outward_ids for this tm_id
#         existing_out_ids = list(
#             gf_inward_table.objects.filter(
#                 id=tm_inward_id,
#                 # outward_id__in=out_id,
#                 status=1
#             ).values_list('outward_id', flat=True)
#         ) if tm_inward_id else []

#         new_out_ids = list(set(out_id) - set(existing_out_ids))

#         # Fetch DO numbers
#         order_number = yarn_delivery_table.objects.filter(
#             id__in=all_out_ids, status=1
#         ).values('id', 'do_number', 'lot_no').order_by('-id')

#         # Total weights
#         totals = yarn_out_available_balance_table.objects.filter(
#             out_id__in=new_out_ids
#         ).aggregate(
#             po_roll=Sum('outward_wt'),
#             outward_wt=Sum('outward_wt'),
#             inward_quantity=Sum('inward_wt'),
#             balance_wt=Sum('balance_wt'),
#         )

#         # Get program IDs
#         program_id_list = list(
#             yarn_out_available_balance_table.objects.filter(
#                 out_id__in=all_out_ids
#             ).values_list('program_id', flat=True).distinct()
#         )

#         # Get active programs
#         program_qs = grey_fab_program_balance_table.objects.filter(
#             program_id__in=program_id_list
#         ).values_list('program_id', flat=True)

#         prg_list = list(knitting_table.objects.filter(
#             id__in=program_qs, status=1
#         ).values('id', 'knitting_number', 'name', 'total_quantity'))

#         # Program balance breakdown
#         balance_raw = yarn_outward_available_wt_table.objects.filter(
#             program_id__in=program_qs
#         ).values_list(
#             'program_id', 'dia_id', 'pg_roll', 'pg_wt',
#             'in_rolls', 'in_wt', 'balance_roll', 'balance_wt'
#         )

#         program_balance_data = [
#             {
#                 'program_id': row[0],
#                 'dia_id': row[1],
#                 'pg_roll': row[2],
#                 'pg_wt': row[3],
#                 'in_rolls': row[4],
#                 'in_wt': row[5],
#                 'balance_roll': row[6],
#                 'balance_wt': row[7]
#             }
#             for row in balance_raw
#         ]

#         program_details = []
#         inward_ids = []

#         if tm_inward_id:
#             inward_ids = list(
#                 gf_inward_table.objects.filter(
#                     outward_id__in=all_out_ids, id=tm_inward_id, status=1
#                 ).values_list('id', flat=True)
#             )

#         for pid in program_id_list:
#             knit = knitting_table.objects.filter(id=pid, is_active=1).first()
#             if not knit:
#                 continue

#             sub_knits = sub_knitting_table.objects.filter(tm_id=knit.id, status=1)
#             for sub in sub_knits:
#                 products = fabric_program_table.objects.filter(id=sub.fabric_id)
#                 fabric_program_data = []
#                 for fp in products:
#                     fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
#                     fabric_program_data.append({
#                         'id': fp.id,
#                         'name': fp.name,
#                         'fabric_id': fp.fabric_id,
#                         'fabric_name': fabric_item.name if fabric_item else 'N/A'
#                     })

#                 gauge = gauge_table.objects.filter(id=sub.gauge).first()
#                 tex = tex_table.objects.filter(id=sub.tex).first()
#                 dia = dia_table.objects.filter(id=sub.dia).first()
#                 yarn = count_table.objects.filter(id=sub.count_id).first()

#                 inward_roll_sum = sub_gf_inward_table.objects.filter(
#                     tm_id__in=inward_ids,
#                     dia_id=sub.dia,
#                     status=1
#                 ).aggregate(
#                     total_roll=Sum('roll'),
#                     total_wt=Sum('total_wt')
#                 )

#                 inward_roll = inward_roll_sum['total_roll'] or 0
#                 inward_quantity = inward_roll_sum['total_wt'] or 0

#                 rec_data = sub_gf_inward_table.objects.filter(
#                     tm_id__in=inward_ids,
#                     dia_id=sub.dia,
#                     status=1
#                 ).aggregate(
#                     total_roll=Sum('roll'),
#                     total_wt=Sum('total_wt')
#                 )

#                 rec_roll = rec_data['total_roll'] or 0
#                 rec_inward_quantity = rec_data['total_wt'] or 0

#                 program_details.append({
#                     'program_id': sub.tm_id,
#                     'fabric': fabric_program_data,
#                     'fabric_id': sub.fabric_id,
#                     'yarn_count': yarn.name if yarn else '',
#                     'yarn_count_id': sub.count_id,
#                     'gauge': gauge.name if gauge else '',
#                     'gauge_id': sub.gauge,
#                     'tex': tex.name if tex else '',
#                     'tex_id': sub.tex,
#                     'gsm': sub.gsm,
#                     'dia': dia.name if dia else '',
#                     'dia_id': sub.dia,
#                     'program_roll': sub.rolls,
#                     'program_roll_wt': sub.wt_per_roll,
#                     'per_roll_wt': sub.wt_per_roll,
#                     'remaining_roll': rec_roll,
#                     'remaining_roll_wt': rec_inward_quantity,
#                     'quantity': sub.quantity,
#                     'out_id': all_out_ids,
#                     'total_roll': inward_roll,
#                     'total_inward_wt': inward_quantity,
#                     'program_total_wt': sub.rolls * sub.wt_per_roll,
#                     'inward_roll': inward_roll,
#                     'inward_roll_wt': inward_quantity,
#                     'program_bal_value': [
#                         row for row in program_balance_data
#                         if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia
#                     ]
#                 })

#         order_data = []
#         if inward_ids:
#             dia_wise = sub_gf_inward_table.objects.filter(
#                 tm_id__in=inward_ids,
#                 status=1
#             ).values('fabric_id', 'dia_id').annotate(
#                 total_roll=Sum('roll'),
#                 total_quantity=Sum('total_wt'),
#                 gross_wt=Sum('gross_wt')
#             )

#             for item in dia_wise:
#                 fabric_name = fabric_table.objects.filter(id=item['fabric_id']).first()
#                 dia_name = dia_table.objects.filter(id=item['dia_id']).first()

#                 rec_data = sub_gf_inward_table.objects.filter(
#                     dia_id=item['dia_id'],
#                     program_id__in=program_id_list,
#                     status=1
#                 ).aggregate(
#                     total_roll=Sum('roll'),
#                     total_wt=Sum('total_wt')
#                 )

#                 rec_roll = rec_data['total_roll'] or 0
#                 rec_inward_quantity = rec_data['total_wt'] or 0

#                 order_data.append({
#                     'fabric_id': item['fabric_id'],
#                     'fabric_name': fabric_name.name if fabric_name else 'N/A',
#                     'dia_id': item['dia_id'],
#                     'dia': dia_name.name if dia_name else 'N/A',
#                     'po_roll': float(item['total_roll'] or 0),
#                     'total_quantity': float(item['total_quantity'] or 0),
#                     'gross_wt': float(item['gross_wt'] or 0),
#                     'remaining_roll': rec_roll,
#                     'remaining_roll_wt': rec_inward_quantity,
#                     'already_rec_roll': rec_roll - (item['total_roll'] or 0),
#                     'already_rec_wt': rec_inward_quantity - (item['total_quantity'] or 0),
#                 })

#         return JsonResponse({
#             "order_numbers": list(order_number),
#             "totals": totals,
#             "programs": prg_list,
#             "program_details": program_details,
#             "order_data": order_data,
#         }, safe=False)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def get_yarn_deliver_edit_lists(request):
    print('gf-yarn-delivery-edit')
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        out_id_str = request.POST.get('outward_list', '')
        tm_inward_id = request.POST.get('tm_id')
        po_id = request.POST.get('po_id')

        # ✅ Convert outward_list to list of ints
        out_id = [int(x.strip()) for x in out_id_str.split(',') if x.strip().isdigit()]
        all_out_ids = list(set(out_id))
        print('out-id:', out_id)

        existing_out_ids = list(
            gf_inward_table.objects.filter(
                id=tm_inward_id,
                outward_id__in=out_id,
                status=1
            ).values_list('outward_id', flat=True)
        ) if tm_inward_id else []

        new_out_ids = list(set(out_id) - set(existing_out_ids))

        order_number = yarn_delivery_table.objects.filter(
            id__in=all_out_ids, status=1
        ).values('id', 'do_number', 'lot_no').order_by('-id')

        totals = yarn_out_available_balance_table.objects.filter(
            out_id__in=new_out_ids
        ).aggregate(
            po_roll=Sum('outward_wt'),
            outward_wt=Sum('outward_wt'),
            inward_quantity=Sum('inward_wt'),
            balance_wt=Sum('balance_wt'),
        )

        program_id_list = list(
            yarn_out_available_balance_table.objects.filter(
                out_id__in=all_out_ids
            ).values_list('program_id', flat=True).distinct()
        )

        program_qs = grey_fab_program_balance_table.objects.filter(
            program_id__in=program_id_list
        ).values_list('program_id', flat=True)

        prg_list = list(knitting_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'knitting_number', 'name', 'total_quantity'))

        balance_raw = yarn_outward_available_wt_table.objects.filter(
            program_id__in=program_qs
        ).values_list(
            'program_id', 'dia_id', 'pg_roll', 'pg_wt',
            'in_rolls', 'in_wt', 'balance_roll', 'balance_wt'
        )

        program_balance_data = [
            {
                'program_id': row[0],
                'dia_id': row[1],
                'pg_roll': row[2],
                'pg_wt': row[3],
                'in_rolls': row[4],
                'in_wt': row[5],
                'balance_roll': row[6],
                'balance_wt': row[7]
            }
            for row in balance_raw
        ]

        program_details = []
        inward_ids = []

        if tm_inward_id:
            inward_ids = list(
                gf_inward_table.objects.filter(
                    # outward_id__in=all_out_ids, id=tm_inward_id, status=1
                  id=tm_inward_id, status=1
                ).values_list('id', flat=True)
            )
            print('inward_id:',inward_ids)
        for pid in program_id_list:
            knit = knitting_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            sub_knits = sub_knitting_table.objects.filter(tm_id=knit.id, status=1)
            for sub in sub_knits:
                products = fabric_program_table.objects.filter(id=sub.fabric_id)
                fabric_program_data = []
                for fp in products:
                    fabric_item = fabric_table.objects.filter(id=fp.fabric_id).first()
                    fabric_program_data.append({
                        'id': fp.id,
                        'name': fp.name,
                        'fabric_id': fp.fabric_id,
                        'fabric_name': fabric_item.name if fabric_item else 'N/A'
                    })

                gauge = gauge_table.objects.filter(id=sub.gauge).first()
                tex = tex_table.objects.filter(id=sub.tex).first()
                dia = dia_table.objects.filter(id=sub.dia).first()
                yarn = count_table.objects.filter(id=sub.count_id).first()

                inward_roll_sum = sub_gf_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('total_wt')
                )

                inward_roll = inward_roll_sum['total_roll'] or 0
                inward_quantity = inward_roll_sum['total_wt'] or 0

                rec_data = sub_gf_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('total_wt')
                )

                rec_roll = rec_data['total_roll'] or 0
                rec_inward_quantity = rec_data['total_wt'] or 0

                program_details.append({
                    'program_id': sub.tm_id,
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
                    'yarn_count': yarn.name if yarn else '',
                    'yarn_count_id': sub.count_id,
                    'gauge': gauge.name if gauge else '',
                    'gauge_id': sub.gauge,
                    'tex': tex.name if tex else '',
                    'tex_id': sub.tex,
                    'gsm': sub.gsm,
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia,
                    'program_roll': sub.rolls,
                    'program_roll_wt': sub.wt_per_roll,
                    'per_roll_wt': sub.wt_per_roll,
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_inward_quantity,
                    'quantity': sub.quantity,
                    'out_id': all_out_ids,
                    'total_roll': inward_roll,
                    'total_inward_wt': inward_quantity,
                    'program_total_wt': sub.rolls * sub.wt_per_roll,
                    'inward_roll': inward_roll,
                    'inward_roll_wt': inward_quantity,
                    'program_bal_value': [
                        row for row in program_balance_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia
                    ]
                })

        order_data = []
        if inward_ids:
            
            dia_wise = sub_gf_inward_table.objects.filter(
                tm_id__in=inward_ids,
                status=1
            ).values('fabric_id', 'dia_id').annotate(
                total_roll=Sum('roll'),
                total_quantity=Sum('total_wt'),
                gross_wt=Sum('gross_wt')
            )

            for item in dia_wise:
                fabric_name = fabric_table.objects.filter(id=item['fabric_id']).first()
                dia_name = dia_table.objects.filter(id=item['dia_id']).first()

                rec_data = sub_gf_inward_table.objects.filter(
                    dia_id=item['dia_id'],
                    program_id__in=program_id_list,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('total_wt')
                )

                rec_roll = rec_data['total_roll'] or 0
                rec_inward_quantity = rec_data['total_wt'] or 0

                order_data.append({
                    'fabric_id': item['fabric_id'],
                    'fabric_name': fabric_name.name if fabric_name else 'N/A',
                    'dia_id': item['dia_id'],
                    'dia': dia_name.name if dia_name else 'N/A',
                    'po_roll': float(item['total_roll'] or 0),
                    'total_quantity': float(item['total_quantity'] or 0),
                    'gross_wt': float(item['gross_wt'] or 0),
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_inward_quantity,
                    'already_rec_roll': rec_roll - (item['total_roll'] or 0),
                    'already_rec_wt': rec_inward_quantity - (item['total_quantity'] or 0),
                })

        return JsonResponse({
            "order_numbers": list(order_number),
            "totals": totals,
            "programs": prg_list,
            "program_details": program_details,
            "order_data": order_data,
        }, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_grey_po_detail_update_list(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # Getting list of outward IDs from POST request

    po_id = request.POST.get('po_id')

    tm_inward_id = request.POST.get('tm_id')
    print('pos;',po_id, tm_inward_id)

    try:
        order_data = []
        program_details = []
        # outward = yarn_delivery_table.objects.filter(
        #     id=out_id, balance_quantity__gt=0
        # ).values('id') 



    # if po_id:
        # Get child orders with balance 
        child_orders = grey_fab_po_balance_table.objects.filter(
            po_id=po_id, 
            # balance_quantity__gt=0
        ).values('po_id') 

        order_number = grey_fabric_po_table.objects.filter( 
            id__in=child_orders, status=1
        ).values('id', 'po_number', 'name','lot_no').order_by('name')

        totals = grey_fab_po_balance_table.objects.filter(
            po_id=po_id, 
            # balance_quantity__gt=0
        ).aggregate(
            po_roll=Sum('ord_roll_wt'),
            po_quantity=Sum('po_quantity'),
            # inward_roll=Sum('in_rolls'),
            inward_quantity=Sum('in_quantity'), 
            balance_quantity=Sum('balance_quantity'),
        )
       
        program_id_list = list(
            grey_fab_po_balance_table.objects.filter( 
                # po_id=po_id, balance_quantity__gt=0
                po_id=po_id,
            ).values_list('program_id', flat=True).distinct()
        )

        print('prg-list:',program_id_list, po_id    )


        program_qs = grey_fab_program_balance_table.objects.filter(
             program_id__in=program_id_list
        ).values_list('program_id', flat=True)
        print('prg-qS:',program_qs)
        prg_list = list(knitting_table.objects.filter(
            id__in=program_qs, status=1
        ).values('id', 'knitting_number', 'name', 'total_quantity'))

        program = list(
            yarn_outward_available_wt_table.objects.filter(program_id__in=program_qs)
            .values_list('program_id','dia_id','pg_roll','pg_wt','in_rolls', 'in_wt','balance_roll','balance_wt')
        )
        print('program:',program)


        formatted_data = [
        {
            'program_id': row[0],
            'dia_id': row[1],
            'pg_roll': row[2],
            'pg_wt': row[3],
            'in_rolls': row[4],
            'in_wt': row[5],
            'balance_roll': row[6],
            'balance_wt': row[7]
        }
        for row in program
    ]

        print('programs:',program,  formatted_data)

        
        # Get the first delivery object for given out_id
        sub_po = grey_fabric_po_table.objects.filter(id__in=po_id, status=1).first()

        program_details = []

        # Loop through each program ID
        for pid in program_id_list:
            knit = knitting_table.objects.filter(id=pid, is_active=1).first()
            if not knit:
                continue

            # Fetch sub-knitting rows for this program
            sub_knits = sub_knitting_table.objects.filter(tm_id=knit.id, status=1)

            for sub in sub_knits:
                # Fetch fabric program data
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

                # Lookup other tables
                gauge = gauge_table.objects.filter(id=sub.gauge).first()
                tex = tex_table.objects.filter(id=sub.tex).first()
                dia = dia_table.objects.filter(id=sub.dia).first()
                yarn = count_table.objects.filter(id=sub.count_id).first()

                # Get inward IDs
                inward_ids = list(gf_inward_table.objects.filter(
                    po_id__in=po_id, id=tm_inward_id, status=1
                ).values_list('id', flat=True))

                print('sub.dia:', sub.dia)

                # Get total inward data for this DIA and tm_id
                inward_roll_sum = sub_gf_inward_table.objects.filter(
                    tm_id__in=inward_ids,
                    dia_id=sub.dia,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('total_wt'),
                    total_gross=Sum('gross_wt')
                )

                inward_roll = inward_roll_sum['total_roll'] or 0
                inward_quantity = inward_roll_sum['total_wt'] or 0

                # Also get all received (recorded) data for this DIA from all relevant outwards
                rec_data = sub_gf_inward_table.objects.filter(
                    po_id__in=po_id,
                    dia_id=sub.dia,
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('total_wt'),
                    total_gross=Sum('gross_wt')
                )

                rec_roll = rec_data['total_roll'] or 0
                rec_inward_quantity = rec_data['total_wt'] or 0

                # Compute remaining rolls and weight
                remaining_roll = sub.rolls - inward_roll
                total_wt_balance = sub.rolls * sub.wt_per_roll
                remaining_roll_wt = total_wt_balance - inward_quantity

                print(f"DIA {sub.dia}: Received Rolls: {rec_roll}, Received Qty: {rec_inward_quantity}")

                program_details.append({
                    'program_id': sub.tm_id,
                    'fabric': fabric_program_data,
                    'fabric_id': sub.fabric_id,
                    'yarn_count': yarn.name if yarn else '',
                    'yarn_count_id': sub.count_id,
                    'gauge': gauge.name if gauge else '',
                    'gauge_id': sub.gauge,
                    'tex': tex.name if tex else '',
                    'tex_id': sub.tex,
                    'gsm': sub.gsm,
                    'dia': dia.name if dia else '',
                    'dia_id': sub.dia,
                    'program_roll': sub.rolls,
                    'program_roll_wt': sub.wt_per_roll,
                    'per_roll_wt': sub.wt_per_roll,

                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_inward_quantity,

                    'quantity': sub.quantity,
                    'out_id': po_id,
                    'po_id': po_id,
                    'total_roll': inward_roll,
                    'total_inward_wt': inward_quantity,
                    'program_total_wt': sub.rolls * sub.wt_per_roll,
                    'inward_roll': inward_roll,
                    'inward_roll_wt': inward_quantity,
                    # 'program_bal_value':formatted_data
                    'program_bal_value': [
                        row for row in formatted_data
                        if row['program_id'] == sub.tm_id and row['dia_id'] == sub.dia
                    ]


                })
    

            print(f"[DIA {sub.dia}] Received Rolls: {rec_roll}, Received Qty: {rec_inward_quantity}")

        if tm_inward_id:
            print('inw-id:',tm_inward_id)
            parent_pos = gf_inward_table.objects.filter(id=tm_inward_id, status=1)
            print('parent-inwards:', parent_pos)

            # Ensure po_id is a list
            if isinstance(po_id, str):
                po_id = [po_id]
            print('PO ID:', po_id)

            inward_ids = list(gf_inward_table.objects.filter(po_id__in=po_id, id=tm_inward_id, status=1).values_list('id', flat=True))


            # Query for either matching po_id OR tm_inward_id, AND status=1
            # inward_ids = gf_inward_table.objects.filter(
            #     Q(po_id__in=po_id) | Q(id=tm_inward_id),
            #     status=1
            # ).values_list('id', flat=True)

            # inward_ids = list(inward_ids)


            print('inward_ids:', inward_ids)

            if not inward_ids:
                print("⚠️ No inward_ids found for given PO ID and Inward ID.")
            
            dia_wise = sub_gf_inward_table.objects.filter(
                tm_id__in=inward_ids,
                status=1
            ).values('fabric_id', 'dia_id').annotate(
                total_roll=Sum('roll'),
                total_quantity=Sum('total_wt'),
                gross_wt=Sum('gross_wt')
            )
            print('Dia-wise Data:', list(dia_wise))

            if not dia_wise:
                print("❌ No fabric dia data found for provided inward IDs.")



            # Dia-wise Fabric Order Data
            order_data = []

            # Ensure inward_ids is defined before this block
            inward_ids = list(gf_inward_table.objects.filter(po_id__in=po_id,status=1).values_list('id', flat=True))
            print('inws:',inward_ids)
            dia_wise = sub_gf_inward_table.objects.filter(
                tm_id__in=inward_ids,
                status=1
            ).values('fabric_id', 'dia_id').annotate(
                total_roll=Sum('roll'),
                total_quantity=Sum('total_wt'),
                gross_wt=Sum('gross_wt')
            ) 
            print('data-wise:',dia_wise)
            
 
            for item in dia_wise: 
                try:
                    fabric_obj = fabric_table.objects.get(id=item['fabric_id'])
                    fabric_name = fabric_obj.name
                except fabric_table.DoesNotExist:
                    fabric_name = 'N/A'

                try:
                    dia_obj = dia_table.objects.get(id=item['dia_id'])
                    dia_name = dia_obj.name
                except dia_table.DoesNotExist:
                    dia_name = 'N/A'

                # ✅ Move rec_data inside the loop to make it DIA-specific
                rec_data = sub_gf_inward_table.objects.filter(
                    po_id__in=po_id,
                    dia_id=item['dia_id'],
                    status=1
                ).aggregate(
                    total_roll=Sum('roll'),
                    total_wt=Sum('total_wt'),
                    total_gross=Sum('gross_wt')
                )

                rec_roll = rec_data['total_roll'] or 0
                rec_inward_quantity = rec_data['total_wt'] or 0

                order_data.append({
                    'fabric_id': item['fabric_id'],
                    'fabric_name': fabric_name,
                    'dia_id': item['dia_id'],
                    'dia': dia_name,
                    'po_roll': float(item['total_roll'] or 0),
                    'total_quantity': float(item['total_quantity'] or 0),
                    'gross_wt': float(item['gross_wt'] or 0),
                    'remaining_roll': rec_roll,
                    'remaining_roll_wt': rec_inward_quantity,
                    'already_rec_roll':( rec_roll) - (item['total_roll']),
                    'already_rec_wt':( rec_inward_quantity) - (item['total_quantity']),
                })

                print('item-roll:', item['total_roll'])
                print('item-roll-wt:', item['total_quantity'])
                print(f"[DIA {item['dia_id']}] Received Rolls: {rec_roll}, Received Qty: {rec_inward_quantity}")



        # Final response data
        response = {
            "order_numbers": list(order_number),
            "totals": totals,
            "programs": prg_list,
            "program_details": program_details,
            "order_data": order_data,
        }

        return JsonResponse(response, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ``````````````````````````````` add grey fabric inward `````````````````````````````````````
def generate_do_num_series():
    last_purchase = gf_delivery_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.do_number:
        match = re.search(r'DO-(\d+)', last_purchase.do_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"DO-{next_num:03d}"


from collections import defaultdict

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
import json

from .models import gf_inward_table, sub_gf_inward_table

def safe_decimal(value):
    """Safely convert value to Decimal."""
    try:
        return Decimal(str(value or "0").strip())
    except (InvalidOperation, TypeError):
        return Decimal('0.00')


@csrf_exempt
def add_grey_fabric_inward(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    user_id = request.session.get('user_id') 
    company_id = request.session.get('company_id')

    try:
        supplier_id = request.POST.get('supplier_id')
        remarks = request.POST.get('remarks')
        po_list = request.POST.get('po_list', 0)

        # ✅ Get DO list as list of strings
        out_ids = request.POST.getlist('do_list')  # e.g., ['4', '3']
        print('out-id list:', out_ids)

        # ✅ Convert list to comma-separated string
        out_id = ",".join(out_ids)  # '4,3'
        print('out_id (comma-separated):', out_id)

        inward_date = request.POST.get('inward_date')
        receive_no = request.POST.get('receive_no')
        receive_date = request.POST.get('receive_date')
        lot = request.POST.get('lot_name')
        prg_id = request.POST.get('prg_id')
        # ✅ Parse chemical data
        chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

        # ✅ Generate inward number
        inward_no = generate_inward_num_series()

        # ✅ Create main inward record
        material_request = gf_inward_table.objects.create(
            inward_number=inward_no,
            inward_date=inward_date,
            party_id=supplier_id,
            receive_no=receive_no,
            receive_date=receive_date,
            cfyear=2025,
            po_id=po_list,
            program_id = prg_id,
            outward_id=out_id,  # ✅ Now properly as string
            lot_no=lot,
            company_id=company_id,
            total_wt=Decimal('0.00'),
            total_gross_wt=Decimal('0.00'),
            remarks=remarks,
            created_by=user_id,
            created_on=timezone.now()
        )

        total_wt = Decimal('0.00')
        total_gross_wt = Decimal('0.00')

        # ✅ Loop over chemical items
        for chemical in chemical_data:
            program_id = chemical.get('program_id', 0)
            deliver_id = chemical.get('deliver_id', 0)
            lot_no = chemical.get('lot_no')
            fabric_id = chemical.get('fabric_id')
            yarn_count_id = chemical.get('yarn_count_id')
            gauge_id = chemical.get('gauge_id')
            tex_id = chemical.get('tex_id')
            gsm = chemical.get('gsm') 
            dia_id = chemical.get('dia_id', 0)

            delivered_roll = safe_decimal(chemical.get('roll'))
            delivered_quantity = safe_decimal(chemical.get('quantity'))
            gross_wt = safe_decimal(chemical.get('gross_wt'))
            wt_per_roll = safe_decimal(chemical.get('wt_per_roll'))

            # ✅ Create sub-inward record
            sub_gf_inward_table.objects.create(
                tm_id=material_request.id,
                fabric_id=fabric_id,
                yarn_count_id=yarn_count_id,
                gauge_id=gauge_id,
                tex_id=tex_id,
                dia_id=dia_id or 0,
                gsm=gsm,
                lot_no=lot_no,
                po_id=po_list,
                cfyear=2025,
                company_id=company_id,
                program_id=program_id or 0,
                party_id=0,
                # outward_id=chemical.get('outward_id'),  # one per row here
                roll=delivered_roll,
                wt_per_roll=wt_per_roll,
                total_wt=wt_per_roll,
                gross_wt=gross_wt,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_wt += wt_per_roll
            total_gross_wt += gross_wt
            print('Running total_wt:', total_wt)
            print('Running gross_wt:', total_gross_wt)

        # ✅ Update totals
        gf_inward_table.objects.filter(id=material_request.id).update(
            total_wt=total_wt,
            total_gross_wt=total_gross_wt
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



# ``````````````````````` tm lists`````````````````````````
def grey_fabric_inward_lists(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    lot_no = request.POST.get('lot_no', '')
    party = request.POST.get('party', '')
    po_id = request.POST.get('po_id', '')
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

    if po_id:
            query &= Q(po_id=po_id)


    if lot_no:
            query &= Q(lot_no=lot_no)


    # Apply filters
    queryset = gf_inward_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())
    ids = [item['id'] for item in data]
  
    formatted = [ 
        {
            'action': '<button type="button" onclick="inward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="grey_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>\
                        <button type="button" onclick="inward_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_no': item['inward_number'] if item['inward_number'] else'-', 
            'inward_date': item['inward_date'].strftime('%d-%m-%Y') if item['inward_date'] else '-',
            'po_number':getPONumberById(grey_fabric_po_table, item['po_id'] ), 
            'party_id':getSupplier(party_table, item['party_id'] ),  
            'total_wt': item['total_wt'] if item['total_wt'] else'-', 
            'lot_no': item['lot_no'] if item['lot_no'] else'-', 

            'total_gross_wt': item['total_gross_wt'] if item['total_gross_wt'] else'-', 
           
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ] 
    return JsonResponse({'data': formatted}) 
 



@csrf_exempt
def grey_fab_inward_print(request):
    outward_id = request.GET.get('k')
    order_id = base64.b64decode(outward_id)
    print('print-id:',order_id)
    
    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    delivery_data = gf_inward_table.objects.filter(status=1, id=order_id)
    
    inwards = gf_inward_table.objects.filter(status=1, id=order_id).first()

    receive_no = inwards.receive_no if inwards else '-'
    receive_date = inwards.receive_date if inwards else '-'
    outward_id_raw = inwards.outward_id or ''  # Might be '1,2,3'
    po_id = inwards.po_id or 0
    print('o-id:',outward_id_raw)
    lot_no = inwards.lot_no

    # Process outward_ids as list
    # Normalize outward_id to list
# Normalize outward_id to list
    outward_numbers = []

    if outward_id_raw:
        if isinstance(outward_id_raw, str):
            # Case: comma-separated string
            outward_ids = [int(x.strip()) for x in outward_id_raw.split(',') if x.strip().isdigit()]
        else:
            # Case: single integer
            outward_ids = [int(outward_id_raw)]

        outward_numbers = list(
            yarn_delivery_table.objects.filter(status=1, id__in=outward_ids)
            .values_list('do_number', flat=True)
        )
        print('order:', outward_numbers)

        outward_display = ', '.join(outward_numbers) if outward_numbers else '-'
    else:
        outward_display = '-'

    # ✅ Now move this here
    print('outward-display:', outward_display)



# Process PO number
    if po_id:
        po_obj = grey_fabric_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
        po_number = po_obj['po_number'] if po_obj else '-'
    else:
        po_number = '-'
        print('po-no:',po_number)


    print('delivery:',outward_id,   po_id)
    outward = gf_inward_table.objects.filter(id = order_id,status=1).values('id','inward_number','inward_date', 'lot_no','party_id', 'total_wt', 'total_gross_wt')
    print('out:',outward)


    program_details = []
    delivery_details = []
    # ✅ Initialize totals here
    total_roll = 0
    total_quantity = 0

    
    # Then build the delivery details (independent of above)
    for out in outward:

        total_gross = 0
        total_roll = 0

        tx_yarn_qs = sub_gf_inward_table.objects.filter(
            tm_id=out['id'],
            status=1
        ).values(
            'yarn_count_id', 'fabric_id', 'gauge_id', 'tex_id',
            'gsm', 'dia_id', 'po_id', 'program_id',
            'lot_no', 'roll', 'total_wt', 'gross_wt'
        )

        print('tx-yarns:',tx_yarn_qs)

        party = get_object_or_404(party_table, id=out['party_id'])
        gstin = party.gstin
        mobile = party.mobile
        party_name = party.name

        for tx_yarn in tx_yarn_qs:
            if not tx_yarn['roll'] or tx_yarn['roll'] == 0:
                continue  # Skip this entry if roll is 0

            yarn_count = get_object_or_404(count_table, id=tx_yarn['yarn_count_id'])
            gauge = get_object_or_404(gauge_table, id=tx_yarn['gauge_id'])
            tex = get_object_or_404(tex_table, id=tx_yarn['tex_id']) 
            dia = get_object_or_404(dia_table, id=tx_yarn['dia_id']) 
            fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
            fab_id = fabric.fabric_id

            # Use get instead of filter to fetch a single fabric record
            fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)
            fabric_display_name = f"{fabric.name} - {fabric_obj.name}"  # Combine program name and fabric name
            # fabric_display_name = f"{fabric_obj.name}"  # Combine program name and fabric name

            delivery_details.append({
                'mill': party.name,
                'yarn_count': yarn_count.name,
                'fabric': fabric_display_name,
                'gauge': gauge.name,
                'tex': tex.name,
                'dia': dia.name,
                'lot_no': out['lot_no'],
                'inward_number': out['inward_number'],
                'inward_date': out['inward_date'],
                'roll': tx_yarn['roll'],
                'total_wt': tx_yarn.get('total_wt'),
                'gsm': tx_yarn['gsm'],
                'gross_wt': tx_yarn['gross_wt'],
                
            })
            print('deli-details:',delivery_details)

            # Accumulate totals 
            total_roll += tx_yarn['roll'] or 0
            total_gross += tx_yarn['gross_wt'] or 0



  
    # image_url = 'http://localhost:8000/static/assets/images/mira.png'
    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'
    # total_gross +=  tx_yarn['gross_wt'] 

    delivery = gf_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
    remarks = delivery['remarks'] if delivery else ''
    print('image_url:',image_url)
    # total_roll +=  tx_yarn['roll'] 
    # pre_no = previous_outward['do_number']

    print('deli-data:',delivery_data)
    context = { 
        # 'inward_number': outward['inward_number'],
        # 'inward_date': outward['inward_date'],
        'inward_values':delivery_data,

        'receive_no':receive_no,
        'receive_date':receive_date,

        'gstin':gstin, 
        'mobile':mobile,
        'customer_name':party_name,
        'program_details': program_details,
        'total_roll': total_roll,
        'total_quantity': total_gross,

        'inward_details': delivery_details,
        'company':company_table.objects.filter(status=1).first(),

        'image_url':image_url,
        'remarks':remarks,
        'outward':outward_display,
        'po':po_number,
        'lot_no':lot_no,
        # 'previous_no':pre_qty if pre_qty else '-',


    } 

    return render(request, 'inward/inward_print.html', context)



import base64

def grey_inward_detail_edit(request):
    try:
        encoded_id = request.GET.get('id') 
        print('encoded-id:', encoded_id)

        if not encoded_id:
            return render(request, 'inward/grey_fab_inward_details.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID 
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode() 
            print('decoded-id:', decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'inward/grey_fab_inward_details.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
        print('material:', material_id)

        # Fetch the parent stock instance
        parent_stock_instance = gf_inward_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'inward/grey_fab_inward_details.html', {'error_message': 'Parent stock not found.'})

        print('inw:', parent_stock_instance.id)

        # Fetch all sub-material instances (full list, not just one)
        material_instances = sub_gf_inward_table.objects.filter(tm_id=material_id)
        # material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        print('material_instances:', material_instances)



       
        # Fetch active products, supplier list, party list, and counts
        product = product_table.objects.filter(status=1)
        supplier = party_table.objects.filter(status=1)
        # party = party_table.objects.filter(is_knitting=1, status=1)
        party = party_table.objects.filter( status=1)
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)
        mill_list = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        po = grey_fabric_po_table.objects.filter(status=1)
        outward = yarn_delivery_table.objects.filter(status=1)
        fabric_program_qs = fabric_program_table.objects.filter(status=1) 

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
            'po_list': grey_fabric_po_table.objects.filter(status=1),
            'fabric_program':fabric_program,
            'gauge':gauge,
            'tex':tex,
            'dia':dia,
            'yarn_count':yarn_count,
        }

        # print('context values:', context)
        return render(request, 'inward/grey_fab_inward_details.html', context)

    except Exception as e:
        print('Exception:', e)
        return render(request, 'inward/grey_fab_inward_details.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


def update_grey_fab_inward_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('po-out-tmid:',master_id)
        if master_id:
            try:
                child_data = sub_gf_inward_table.objects.filter(tm_id=master_id, status=1)

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
                        'yarn_count': getItemNameById(count_table, item.yarn_count_id),
                        'tex': getItemNameById(tex_table, item.tex_id),
                        'gauge': getItemNameById(gauge_table, item.gauge_id),
                        'gsm': item.gsm,
                        'dia': getItemNameById(dia_table, item.dia_id),
                        'roll': item.roll or 0,
                        'total_wt': item.total_wt or 0,
                        'gross_wt': item.gross_wt or 0,
                        'received_roll': 0,
                        'received_roll_wt': 0,
                        'fabric_id': item.fabric_id or '-',
                        'yarn_count_id': item.yarn_count_id or '-',
                        'tex_id': item.tex_id or '-',
                        'gauge_id': item.gauge_id or '-',
                        'dia_id': item.dia_id or '-',
                    })

                return JsonResponse({'success': True, 'data': formatted_data})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request, missing ID parameter'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})




def sub_inward_detail_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_gf_inward_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


def gf_inward_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_gf_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_gf_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})






@csrf_exempt
def grey_fabric_inward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        if not data_id:
            return JsonResponse({'message': 'Inward ID is required.'})

        try:
            # Get the inward entry
            inward = gf_inward_table.objects.get(id=data_id)
            po_id = inward.po_id  # Can be None

            # # Check for active delivery entries
            # has_active_delivery = sub_gf_inward_table.objects.filter(
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
            # gf_inward_table.objects.filter(id=data_id).update(status=0, is_active=0)
            # sub_gf_inward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)
            gf_inward_table.objects.filter(id=data_id).delete()
            sub_gf_inward_table.objects.filter(tm_id=data_id).delete()



            return JsonResponse({'message': 'yes'})

        except gf_inward_table.DoesNotExist:
            return JsonResponse({'message': 'Inward entry not found.'})
        except Exception as e:
            print("Error during inward deletion:", e)
            return JsonResponse({'message': 'Error occurred during inward deletion.'})

    return JsonResponse({'message': 'Invalid request method'})




# def update_grey_fabric_inward(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')
#         company_id = request.session.get('company_id')

#         master_id = request.POST.get('tm_id')
#         tx_id = request.POST.get('tx_id')
#         print('tm_id:',master_id)
#         fabric_id = request.POST.get('fabric_id')
#         yarn_count_id = request.POST.get('yarn_count_id')
#         tex_id = request.POST.get('tex_id')
#         gauge_id = request.POST.get('gauge_id')
#         dia_id = request.POST.get('dia_id')
#         gsm = request.POST.get('gsm')
#         roll = request.POST.get('roll')
#         roll_wt = request.POST.get('roll_wt')
#         gross_wt = request.POST.get('gross_wt')
        
#         po_id = int(request.POST.get('po_id', 0) or 0)
#         outward_id = int(request.POST.get('outward_id', 0) or 0)
#         supplier_id = int(request.POST.get('supplier_id', 0) or 0)

  

#         if not master_id or not fabric_id:
#             return JsonResponse({'success': False, 'error_message': 'Missing master_id or product_id'})

#         try:
#             # Try updating existing record
#             existing_item = sub_gf_inward_table.objects.filter(
#                 tm_id=master_id,
#                 id=tx_id,
#                 # party_id=supplier_id,
#                 # po_id=po_id,
#                 # outward_id=outward_id,
#                 fabric_id=fabric_id,
#                 # yarn_count_id=yarn_count_id,
#                 # gauge_id=gauge_id,
#                 # tex_id=tex_id,
#                 # dia_id=dia_id,
#                 # gsm=gsm,
#             ).first()

#             if existing_item:
#                 existing_item.roll = roll
#                 existing_item.yarn_count_id=yarn_count_id
#                 existing_item.fabric_id=fabric_id
#                 existing_item.gauge_id=gauge_id
#                 existing_item.tex_id=tex_id
#                 existing_item.gsm=gsm
#                 existing_item.dia_id=dia_id 
#                 existing_item.wt_per_roll = roll_wt
#                 existing_item.total_wt = roll_wt
#                 existing_item.gross_wt = gross_wt
#                 existing_item.updated_by = user_id
#                 existing_item.updated_on = datetime.now()
#                 existing_item.save()
#             else:
#                 sub_gf_inward_table.objects.create(
#                     tm_id=master_id,
#                     company_id=company_id,
#                     cfyear=2025,
#                     roll=roll,
#                     wt_per_roll=roll_wt,
#                     total_wt=roll_wt,
#                     gross_wt=gross_wt,
#                     po_id=po_id,
#                     outward_id=outward_id,
#                     party_id=supplier_id,
#                     yarn_count_id=yarn_count_id,
#                     fabric_id=fabric_id,
#                     gauge_id=gauge_id,
#                     tex_id=tex_id,
#                     gsm=gsm,
#                     dia_id=dia_id, 
#                     status=1,
#                     is_active=1,
#                     created_by=user_id,
#                     updated_by=user_id,
#                     created_on=datetime.now(),
#                     updated_on=datetime.now(),
#                 )

#             # Safely update master totals
#             updated_totals = update_inwards_total(master_id)
#             if 'error' in updated_totals:
#                 return JsonResponse({'success': False, 'error_message': updated_totals['error']})

#             return JsonResponse({'success': True, **updated_totals})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})

#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


# def update_grey_fabric_inward(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')
#         company_id = request.session.get('company_id')

#         master_id = request.POST.get('tm_id')
#         tx_id = request.POST.get('tx_id')
#         print('tm_id:',master_id)
#         fabric_id = request.POST.get('fabric_id')
#         yarn_count_id = request.POST.get('yarn_count_id')
#         tex_id = request.POST.get('tex_id')
#         gauge_id = request.POST.get('gauge_id')
#         dia_id = request.POST.get('dia_id')
#         gsm = request.POST.get('gsm')
#         roll = request.POST.get('roll')
#         roll_wt = request.POST.get('roll_wt')
#         gross_wt = request.POST.get('gross_wt')
        
#         po_id = int(request.POST.get('po_id', 0) or 0)
#         outward_id = int(request.POST.get('outward_id', 0) or 0)
#         supplier_id = int(request.POST.get('supplier_id', 0) or 0)

  

#         if not master_id or not fabric_id:
#             return JsonResponse({'success': False, 'error_message': 'Missing master_id or product_id'})

#         try:
           
#             sub_gf_inward_table.objects.filter(tm_id=master_id).delete() 

           
#             sub_gf_inward_table.objects.create(
#                 tm_id=master_id,
#                 company_id=company_id,
#                 cfyear=2025,
#                 roll=roll,
#                 wt_per_roll=roll_wt,
#                 total_wt=roll_wt,
#                 gross_wt=gross_wt,
#                 po_id=po_id,
#                 outward_id=outward_id,
#                 party_id=supplier_id,
#                 yarn_count_id=yarn_count_id,
#                 fabric_id=fabric_id,
#                 gauge_id=gauge_id,
#                 tex_id=tex_id,
#                 gsm=gsm,
#                 dia_id=dia_id, 
#                 status=1,
#                 is_active=1,
#                 created_by=user_id,
#                 updated_by=user_id,
#                 created_on=datetime.now(),
#                 updated_on=datetime.now(),
#             )

#             # Safely update master totals
#             updated_totals = update_inwards_total(master_id)
#             if 'error' in updated_totals:
#                 return JsonResponse({'success': False, 'error_message': updated_totals['error']})

#             return JsonResponse({'success': True, **updated_totals})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})

#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


def update_grey_fabric_inward(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            company_id = request.session.get('company_id')

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
            # sub_gf_inward_table.objects.filter(tm_id=master_id).update(status=0,is_active=0)
            sub_gf_inward_table.objects.filter(tm_id=master_id).delete()

            # Step 2: Create new entries
            for row in table_data:     
                print('tot-wt:',row.get('total_wt'))

                sub_gf_inward_table.objects.create(
                    tm_id=master_id, 
                    company_id=company_id,
                    cfyear=2025,
                    roll=row.get('roll'),
                    wt_per_roll=row.get('total_wt'), 
                    total_wt=row.get('total_wt'), 
                    gross_wt=row.get('gross_wt'),
                    program_id=row.get('program_id'),
                    lot_no=row.get('lot_no'),

                    po_id=row.get('po_id') or 0,
                    # outward_id=row.get('outward_id',0) or 0,
                    party_id=row.get('supplier_id') or 0,

                    yarn_count_id=row.get('yarn_count_id'),
                    fabric_id=row.get('fabric_id'),
                    gauge_id=row.get('gauge_id'),
                    tex_id=row.get('tex_id'),
                    gsm=row.get('gsm'),
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
        qs = sub_gf_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        if not qs.exists():
            return {'error': 'No active inward items found.'}

        # Use Django ORM's Sum aggregation
        totals = qs.aggregate(
            total_wt=Sum('total_wt'),
            gross_wt=Sum('gross_wt')
        )

        total_wt = totals['total_wt'] or Decimal('0')
        gross_wt = totals['gross_wt'] or Decimal('0')

        gf_inward_table.objects.filter(id=master_id).update(
            total_wt=total_wt,
            total_gross_wt=gross_wt,
            updated_on=datetime.now()
        )

        return {
            'total_quantity': str(total_wt),
            'total_gross': str(gross_wt),
        }

    except Exception as e:
        return {'error': str(e)}
    
