from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
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




def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 


# Create your views here.


def grey_fab_po(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1) 
        # party = party_table.objects.filter(status=1,is_supplier=1)
        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        # party =  party_table.objects.filter(status=1).filter(is_trader=1)
 
        yarn_count = count_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        lot = grey_fabric_po_table.objects.filter(status=1).distinct()

        program = knitting_table.objects.filter(status=1,is_grey_fabric=1)
        return render(request,'po/grey_fab_po.html',{'program':program,'supplier':supplier,'party':party,'product':product,'yarn_count':yarn_count,'lot':lot})
    else:
        return HttpResponseRedirect("/admin")


def get_fabric_names(request):
    if request.method == 'GET':
        fabric_names = list(fabric_program_table.objects.values_list('name', flat=True).distinct())
        return JsonResponse({'fabric_names': fabric_names})

 
def grey_fab_po_report(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)


    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    prg_id = request.POST.get('prg_id', '')
    lot_no = request.POST.get('lot_no', '')
    yarn_count = request.POST.get('yarn_count', '')
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Match if either created_on or updated_on falls in range
            date_filter = Q(po_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })
    
    if party:
            query &= Q(party_id=party)

    if yarn_count:
            query &= Q(yarn_count_id=yarn_count)


    if lot_no:
            query &= Q(lot_no=lot_no)


    if prg_id:
            query &= Q(program_id=prg_id)


    # Apply filters
    queryset = grey_fabric_po_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())

    # data = list(grey_fabric_po_table.objects.filter(status=1).order_by('-id').values())

    formatted = []

    for index, item in enumerate(data):
        # Fetch the child PO for each parent PO
        child_po = grey_fabric_po_table.objects.filter(id=item['id'], status=1).first()

        # if child_po:  # Ensure child_po is not None
        #     yarn = child_po.yarn_count_id
        # else:
        #     yarn = None  # If no child PO exists, handle accordingly

        formatted.append({
            'action': '<button type="button" onclick="po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="po_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>\
                        <button type="button" onclick="grey_fabric_po_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>' .format(item['id'], item['id'], item['id']),
            'id': index + 1,
            'po_date': item['po_date'] if item['po_date'] else '-', 
            'po_number': item['po_number'] if item['po_number'] else '-',
            'name': item['name'] if item['name'] else '-',
            'lot_no': item['lot_no'] if item['lot_no'] else '-', 
            'supplier_id': getSupplier(party_table, item['party_id']),
            'program': getKnittingDisplayNameById(knitting_table, item['program_id']),
            # 'fabric': getSupplier(fabric_program_table, item['fabric_id']) if yarn else '-',
            # 'gauge': getSupplier(gauge_table, item['gauge_id']) if yarn else '-',
            # 'tex': getSupplier(tex_table, item['tex_id']) if yarn else '-',
            # 'yarn_count': getSupplier(count_table, item['yarn_count_id']) if yarn else '-',
            'total_roll': item['total_roll'] if item['total_roll'] else '-',
            'total_roll_wt': item['total_roll_wt'] if item['total_roll_wt'] else '-',
            # 'total_quantity': item['quantity'] if item['quantity'] else '-',
         
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted}) 



from collections import defaultdict
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64



@csrf_exempt
def print_grey_fab_po(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception as e:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(grey_fabric_po_table, id=order_id)
    customer_value = get_object_or_404(party_table, status=1, id=total_values.party_id)

    details = grey_fabric_po_table.objects.filter(id=order_id).values('id', 'total_roll', 'total_roll_wt', 'program_id')
    prg_details = grey_fabric_po_program_table.objects.filter(po_id=order_id).values(
        'id', 'rolls', 'roll_wt', 'fabric_id', 'program_id',
        'yarn_count_id', 'tex_id', 'gauge_id', 'dia_id', 'gsm'
    )

    combined_details = []
    delivery_details = []

    total_roll = 0
    total_wts = 0

    for detail in details:
        for prg_detail in prg_details:
            if prg_detail['program_id'] == detail['program_id']:
                program = get_object_or_404(knitting_table, id=prg_detail['program_id'])
                product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])
                yarn = get_object_or_404(count_table, id=prg_detail['yarn_count_id'])
                tex = get_object_or_404(tex_table, id=prg_detail['tex_id'])
                gauge = get_object_or_404(gauge_table, id=prg_detail['gauge_id'])
                dia = get_object_or_404(dia_table, id=prg_detail['dia_id'])

                fab_id = product.fabric_id
                fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)
                fabric_display_name = f"{fabric_obj.name}"

                tx_yarns = sub_grey_fabric_po_table.objects.filter(po_id=detail['id']).values(
                    'party_id', 'roll_wt', 'delivery_date'
                )

                for tx in tx_yarns:
                    party = get_object_or_404(party_table, id=tx['party_id'])
                    delivery_details.append({
                        'party': party.name,
                        'roll_wt': tx['roll_wt'],
                        'delivery_date': tx['delivery_date'],
                        'gstin': party.gstin,
                        'mobile': party.mobile,
                    })

                total_rolls = prg_detail['rolls']
                weight = prg_detail['rolls'] * prg_detail['roll_wt']

                total_roll += total_rolls
                total_wts += weight

                combined_details.append({
                    'fabric': fabric_display_name,
                    'yarn_count': yarn.name,
                    'gauge': gauge.name,
                    'tex': tex.name,
                    'dia': dia.name,
                    'gsm': prg_detail['gsm'],
                    'program_name': program.name,
                    'rolls': prg_detail.get('rolls', 0),
                    'roll_wt': prg_detail.get('roll_wt', 0),
                    'rate': total_values.rate,
                    'net_rate': total_values.net_rate,
                    'total_wt': weight,
                    'discount': total_values.discount
                })

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
        'delivery_details': delivery_details,
        'company': company_table.objects.filter(status=1).first(),
        'image_url': image_url,
        'total_rolls': total_roll,
        'weight': total_wts,
    }

    return render(request, 'po/print_po.html', context)


def getSupplier(tbl, supplier_id):
    try:
        party = tbl.objects.get(id=supplier_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party

def getParty(tbl, deliverd_to):
    try:
        party = tbl.objects.get(id=deliverd_to).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party




# ``````````````````````````````````` grey fabric po `````````````````````````````````````````````````````````````     
  


from django.db.models import Max



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum

@csrf_exempt
def get_knitting_fabric_details(request):
    if request.method == 'POST':
        program_id = request.POST.get('program_id')

        if not program_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            knitting = get_object_or_404(knitting_table, id=program_id)

            # Aggregate total rolls and total weight
            totals = sub_knitting_table.objects.filter(tm_id=program_id).aggregate(
                total_rolls=Sum('rolls'),
                total_wt=Sum('wt_per_roll')
            )

            # Get the first matching sub_knitting (if multiple exist)
            sub_knitting = sub_knitting_table.objects.filter(tm_id=program_id).first()
            if not sub_knitting:
                return JsonResponse({'error': 'No sub knitting found for this program ID'}, status=404)

            fabric_program = get_object_or_404(fabric_program_table, id=sub_knitting.fabric_id)
            count = get_object_or_404(count_table, id=fabric_program.count_id)
            gauge = get_object_or_404(gauge_table, id=fabric_program.gauge_id)
            tex = get_object_or_404(tex_table, id=fabric_program.tex_id)

            dia_ids = [int(d) for d in str(fabric_program.dia_id).split(',') if d.isdigit()]
            dia_list = list(dia_table.objects.filter(id__in=dia_ids).values('id', 'name'))
            
            
            dia_rolls_qs = (
                sub_knitting_table.objects
                .filter(tm_id=program_id)
                .values('dia')  # group by dia_id
                .annotate(
                    total_rolls=Sum('rolls'),
                    total_wt=Sum('wt_per_roll')
                )
            )
            dia_id_map = dict(dia_table.objects.filter(id__in=[d['dia'] for d in dia_rolls_qs]).values_list('id', 'name'))



            # Format DIA-wise result
            dia_rolls = []
            for item in dia_rolls_qs:
                dia_rolls.append({
                    'dia_id': item['dia'],
                    'dia_name': dia_id_map.get(item['dia'], ''),
                    'total_rolls': item['total_rolls'] or 0,
                    'total_wt': item['total_wt'] or 0
                })

            # Add to response
            # response_data['dia_rolls'] = dia_rolls



            response_data = {
                'fabric_program': {'id': fabric_program.id, 'name': fabric_program.name},
                'count': {'id': count.id, 'count': count.name},
                'dia': dia_list,
                'gauge': {'id': gauge.id, 'name': gauge.name},
                'tex': {'id': tex.id, 'name': tex.name},
                'gsm': {'id': fabric_program.id, 'gray_gsm': fabric_program.gray_gsm},
                'totals': {
                    'total_rolls': totals['total_rolls'] or 0,
                    'total_wt': totals['total_wt'] or 0,
                },
                'dia_rolls' : dia_rolls
            }

            return JsonResponse(response_data)

        except Exception as e: 
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)




def grey_fab_po_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        # supplier = party_table.objects.filter(is_knitting=1,status=1)

        # party = party_table.objects.filter(status=1,is_process=1)
        product = product_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        
        # fabric_program = fabric_program_table.objects.filter(status=1)
        fabric_program_qs = fabric_program_table.objects.filter(status=1)
        # knitting = knitting_table.objects.filter(status=1,is_grey_fabric=1)
        linked_knitting_ids = grey_fabric_po_table.objects.filter(status=1).values('program_id')

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
        mill = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        # mill =  party_table.objects.filter(status=1).filter(is_trader=1)

        party = party_table.objects.filter(status=1,is_knitting=1)
        out_party = party_table.objects.filter(status=1,is_process=1)
        purchase_number = generate_po_num_series
        return render(request, 'po/grey_fab_po_add.html', {
            'mill': mill,
            'party': party,
            'out_party':out_party,
            'product': product,
            'count':count,
            'fabric_program':fabric_program,
            'purchase_number': purchase_number,
            'knitting':knitting,
            
        }) 
    else:
        return HttpResponseRedirect("/admin")



def get_mills(request):
    if request.method == 'POST':
        party_id = request.POST.get('party_id')
        if not party_id:
            return JsonResponse({'mills': []})  # Safe fallback

        try:
            party = party_table.objects.filter(id=party_id).first()

            if party and party.is_mill == 1:
                # Supplier is itself a mill
                return JsonResponse({'mills': [{'id': party.id, 'name': party.name}]})
            else:
                # Get all other mills
                mills = party_table.objects.filter(is_mill=1)
                mills_data = [{'id': mill.id, 'name': mill.name} for mill in mills]
                return JsonResponse({'mills': mills_data})
        except Exception as e:
            return JsonResponse({'mills': [], 'error': str(e)}, status=500)

    return JsonResponse({'mills': []}, status=405)



from django.core.exceptions import ValidationError
from datetime import datetime

def validate_date_format(date_string):
    """Validates if a date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def generate_po_num_series():
    last_purchase = grey_fabric_po_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.po_number:
        match = re.search(r'PO-(\d+)', last_purchase.po_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"PO-{next_num:03d}"


from django.db import transaction

def insert_grey_fab_po(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        if not user_id or not company_id:
            return JsonResponse({'status': 'Failed', 'message': 'User or company information missing.'}, status=400)

        try:
            po_date = request.POST.get('purchase_date')
            name = request.POST.get('name')
            party_id = request.POST.get('party_id')
            lot_no = request.POST.get('lot_no')
            remarks = request.POST.get('remarks')
            program_id = request.POST.get('program_id')
            is_delivery = request.POST.get('is_delivery') == 'on'

            # Handle delivery data
            delivery_data_raw = request.POST.get('delivery_data', '[]')
            delivery_data = json.loads(delivery_data_raw) if delivery_data_raw else []

            if is_delivery and not delivery_data:
                return JsonResponse({'status': 'Failed', 'message': 'Delivery data required.'}, status=400)

            # Handle knitting data
            knitting_data_raw = request.POST.get('knitting_data', '[]')
            knitting_data = json.loads(knitting_data_raw) if knitting_data_raw else []

            po_no = generate_po_num_series()
            is_deliverd = 1 if is_delivery else 0

            actual_rate = float(request.POST.get('actual_rate', 0))
            gross_wt = float(request.POST.get('gross_wt', 0))
            discount = float(request.POST.get('discount', 0))
            rate = float(request.POST.get('rate', 0))
            # amount = float(request.POST.get('amount', 0))

            with transaction.atomic():
                # Create parent PO
                material_request = grey_fabric_po_table.objects.create(
                    po_number=po_no,
                    po_date=po_date,
                    name=name,
                    lot_no = lot_no,
                    is_delivery=is_deliverd,
                    program_id=program_id,
                    party_id=party_id,
                    company_id=company_id,
                    cfyear=2025,
                    remarks=remarks,
                    total_roll = sum(int(k.get('roll', 0)) for k in knitting_data),
                    # total_roll_wt = sum(float(k.get('roll_wt', 0.00)) for k in knitting_data),
                    total_roll_wt = sum(float(k.get('quantity', 0.00)) for k in knitting_data),

                    rate=actual_rate,
                    # gross_quantity=gross_wt,
                    discount=discount,
                    net_rate=rate,


                    is_active=1,
                    status=1,
                    created_by=user_id,
                    created_on=timezone.now(),
                )

                # Save delivery details
                for delivery in delivery_data:
                    sub_grey_fabric_po_table.objects.create(
                        po_id=material_request.id,
                        company_id=company_id,
                        cfyear=2025,
                        party_id=int(delivery['knitting_id']),
                        delivery_date=delivery['delivery_date'],
                        roll_wt=float(delivery['roll_wt']),
                        is_active=1,
                        status=1,
                        created_by=user_id,
                        created_on=timezone.now(),
                    )

                # Save knitting table values into grey_fabric_po_program_table
                for knit in knitting_data:
                    grey_fabric_po_program_table.objects.create( 
                        program_id=program_id,
                        po_id=material_request.id,
                        yarn_count_id=knit.get('count_id'),
                        gauge_id=knit.get('gauge_id'),
                        tex_id=knit.get('tex_id'),
                        dia_id=knit.get('dia_id'),
                        fabric_id=knit.get('fabric_id'),
                        gsm=int(knit.get('gsm', 0)), 
                        rolls=int(knit.get('roll', 0)),
                        roll_wt=float(knit.get('roll_wt', 0)),
                        is_active=1,
                        status=1,
                        created_by=user_id,
                        company_id=company_id,
                        cfyear=2025,
                        created_on=timezone.now(),
                    )

            new_po_number = generate_po_num_series()
            return JsonResponse({'status': 'Success', 'message': 'PO and knitting data saved.', 'po_number': new_po_number})

        except Exception as e:
            return JsonResponse({'status': 'Failed', 'message': str(e)}, status=500)

    return render(request, 'po/grey_fab_po.html')




def grey_fabric_po_program_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('prg_id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data 
                child_data = grey_fabric_po_program_table.objects.filter(program_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = sum(
                        (item.rolls or 0) * (item.roll_wt or 0)
                        for item in child_data
                    )

                    # total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    # total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                  

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
                            'fabric_id': getItemFabNameById(fabric_program_table, item['fabric_id']),
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






def grey_fab_po_details(request): 
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'po/grey_fab_po_details.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'po/grey_fab_po_details.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
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


        # Fetch the material instance using 'tm_id'
        material_instance = grey_fabric_po_table.objects.filter(id=material_id).first()
       
        # Fetch the parent stock instance
        parent_stock_instance = grey_fabric_po_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'po/grey_fab_po_details.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        
        # knitting = knitting_table.objects.filter(status=1)
        # knitting = knitting_table.objects.filter(status=1,is_grey_fabric=1)
        linked_knitting_ids = grey_fabric_po_table.objects.values('program_id')

        # Filter knitting_table
        knitting = knitting_table.objects.filter(status=1, is_grey_fabric=1)


        # Fetch active products and UOM
        mill = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)

        party = party_table.objects.filter(status=1,is_knitting=1)
        out_party = party_table.objects.filter(status=1,is_process=1)
        count = count_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1) 
        tex = tex_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material_instance': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'party': party,
            'mill':mill,
            'out_party': out_party,
            'count':count,
            'knitting':knitting,
            'fabric_program':fabric_program,
            'dia':dia,
            'gauge':gauge,
            'tex':tex,
        }
        return render(request, 'po/grey_fab_po_details.html', context)

    except Exception as e:
        return render(request, 'po/grey_fab_po_details.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




def grey_fabric_po_update(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        master_id = request.POST.get('tm_id')
        program_id = request.POST.get('program_id')
       
        remarks = request.POST.get('remarks')
        party_id = request.POST.get('supplier_id')
        lot_no = request.POST.get('lot_no')
        po_rate = request.POST.get('rate')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        # amount = request.POST.get('amount')

        if not master_id or not program_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = grey_fabric_po_table.objects.get(id=master_id)
            # parent_item.knitting_program_id = program_id
            parent_item.party_id = party_id
            parent_item.lot_no = lot_no
            parent_item.name = name

            parent_item.rate = po_rate
            parent_item.net_rate = price
            parent_item.discount = discount


            parent_item.remarks = remarks
            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Grey Fabric PO item updated successfully'})

        except grey_fabric_po_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Parent PO not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})



def get_allowed_roll(request):
    tm_id = request.GET.get("tm_id")
    knitting_id = request.GET.get("knitting_id") 

    try:
        # Get the parent PO (assuming `bag` is the planned quantity)
        parent = grey_fabric_po_table.objects.get(id=tm_id)
        # Sum delivered bags for that tm + knitting
        delivered_total = sub_grey_fabric_po_table.objects.filter(
            po_id=tm_id,
            party_id=knitting_id
        ).aggregate(total=Sum('roll'))['total'] or 0

        remaining = max(parent.roll - delivered_total, 0)

        return JsonResponse({'allowed_rolls': remaining})
    except sub_grey_fabric_po_table.DoesNotExist:
        return JsonResponse({'allowed_rolls': 0})
    except grey_fabric_po_table.DoesNotExist:
        return JsonResponse({'allowed_rolls': 0})


def grey_fab_po_delivery_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id:
            try:
                # Fetch child PO data
                child_data = sub_grey_fabric_po_table.objects.filter(po_id=master_id, status=1, is_active=1)
           
                # Format child PO data for response
                data = list(child_data.values())
                formatted_data = []
                index = 0
                for item in data: 
                    index += 1  
                    formatted_data.append({
                        'action': '<button type="button" onclick="po_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                    <button type="button" onclick="purchase_order_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                        'id': index,
                        'knitting': getItemNameById(party_table, item['party_id']),
                        # 'dia': getItemNameById(dia_table, item['dia_id']),

                        'roll_wt': item['roll_wt'] if item['roll_wt'] else '-',
                        # 'roll': item['roll'] if item['roll'] else '-',
                        'delivery_date': item['delivery_date'] if item['delivery_date'] else '-',
                        'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                    })
                formatted_data.reverse()

                # ✅ Add return statement to return JSON response
                return JsonResponse({'status': 'Success', 'data': formatted_data})

            except Exception as e:
                return JsonResponse({'status': 'Failed', 'error': str(e)}, status=500)

        else:
            return JsonResponse({'status': 'Failed', 'error': 'Invalid request, missing ID parameter'}, status=400)

    return JsonResponse({'status': 'Failed', 'error': 'Invalid request, POST method expected'}, status=400)





# update or add po-deliverytable
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
import json
            # yarn_count = data.get('yarn_count')


# @csrf_exempt
# def add_grey_po_deliver(request):
#     if request.method == 'POST':
#         company_id = request.session.get('company_id')

#         try:
#             # Parse incoming data
#             data = json.loads(request.body)
#             tm_id = data.get('tm_id')
#             print('tm-id:', tm_id)
#             # fabric_id = data.get('fabric_id')
#             knitting_id = data.get('knitting_id')
#             deliver_date = data.get('deliver_date')
#             roll_wt = data.get('roll_wt')
#             print('roll-wt:'),roll_wt

#             # try:
#             #     # roll = int(data.get('roll'))
#             # except (TypeError, ValueError):
#             # #     return JsonResponse({'success': False, 'message': 'Invalid or missing roll value.'})
#             # try:
#             #     roll_wt = Decimal(str(roll_wt)) if roll_wt is not None else Decimal('0')
#             # except (InvalidOperation, TypeError, ValueError):
#             #     return JsonResponse({'success': False, 'message': 'Invalid numeric value for roll_wt.'})
#             pos = grey_fabric_po_table.objects.filter(id=tm_id).first()
            

#             # dia_id = data.get('dia_id')
           
#             # try:
#             #     # rate = float(rate) if rate is not None else 0.0
#             #     # discount = float(discount) if discount is not None else 0.0
#             #     roll_wt = float(roll_wt) if roll_wt is not None else 0.0
#             # except (TypeError, ValueError):
#             #     return JsonResponse({'success': False, 'message': 'Invalid numeric values for rate, discount, or roll_wt.'})

#             # value = rate - discount
#             # price = value * roll_wt  # Not used further but kept for logic context
#             # amount_value =  roll_wt

#             # # Get parent PO bag total
#             # try:
#             #     parent_po = grey_fabric_po_table.objects.get(id=tm_id)
#             #     allowed_wt = parent_po.total_roll_wt

#             # except grey_fabric_po_table.DoesNotExist:
#             #     return JsonResponse({'success': False, 'message': 'Invalid PO ID'})
 
#             # # Sum of already delivered bags for this PO
#             # delivered_total = sub_grey_fabric_po_table.objects.filter(po_id=tm_id).aggregate(
#             #     total=Sum('roll_wt'))['total'] or 0

#             # # Check if new delivery fits within the allowed bag limit
#             # if delivered_total + roll_wt <= allowed_wt:
#             #     sub_grey_fabric_po_table.objects.create( 
#             #         # fabric_id=fabric_id,
#             #         po_id=tm_id,
#             #         # dia_id = dia_id,
#             #         company_id=company_id,
#             #         cfyear=2025,
#             #         party_id=knitting_id,
#             #         delivery_date=deliver_date,
#             #         # roll=roll,
#             #         roll_wt=roll_wt, 
#             #         # quantity=amount_value, 
#             #     )
#             #     return JsonResponse({'success': True, 'message': 'New delivery added successfully!'})
#             # else:
#             #     # Try updating an existing roll if over limit
#             #     delivery = sub_grey_fabric_po_table.objects.filter(
#             #         po_id=tm_id, party_id=knitting_id
#             #     ).first()
#             #     print('true:',delivery) 
#             #     if delivery:
#             #     if delivered_total + roll_wt <= allowed_wt:
#             #         # delivery.dia_id = dia_id
#             #         # delivery.roll = roll
#             #         delivery.roll_wt = roll_wt
#             #         # delivery.quantity = amount_value
#             #         delivery.delivery_date = deliver_date
#             #         delivery.save()
#             #         return JsonResponse({'success': True, 'message': 'Existing delivery updated successfully!'})
#             #     else:
#             #         return JsonResponse({'success': False, 'message': 'Cannot add new entry and no existing row to update.'})


#             # Safely convert roll_wt to Decimal
#             try:
#                 roll_wt = Decimal(str(data.get('roll_wt'))) if data.get('roll_wt') is not None else Decimal('0.00')
#             except (InvalidOperation, TypeError, ValueError):
#                 return JsonResponse({'success': False, 'message': 'Invalid numeric value for roll_wt.'})

#             # Get parent PO bag total
#             try:
#                 parent_po = grey_fabric_po_table.objects.get(id=tm_id)
#                 allowed_wt = parent_po.total_roll_wt or Decimal('0.00')
#             except grey_fabric_po_table.DoesNotExist:
#                 return JsonResponse({'success': False, 'message': 'Invalid PO ID'})

#             # Sum of already delivered roll_wt for this PO (as Decimal)
#             delivered_total = sub_grey_fabric_po_table.objects.filter(po_id=tm_id).aggregate(
#                 total=Sum('roll_wt')
#             )['total'] or Decimal('0.00')

#             # Check if adding new roll_wt stays within allowed limit
#             if delivered_total + roll_wt <= allowed_wt:
#                 sub_grey_fabric_po_table.objects.create(
#                     po_id=tm_id,
#                     company_id=company_id,
#                     cfyear=2025,
#                     party_id=knitting_id,
#                     delivery_date=deliver_date,
#                     roll_wt=roll_wt
#                 )
#                 return JsonResponse({'success': True, 'message': 'New delivery added successfully!'})

#             else:
#                 # Try updating existing delivery if present
#                 delivery = sub_grey_fabric_po_table.objects.filter(
#                     po_id=tm_id, party_id=knitting_id
#                 ).first()

#                 if delivery:
#                     # Subtract current roll_wt from total to check if update is allowed
#                     previous_wt = delivery.roll_wt or Decimal('0.00')
#                     if (delivered_total - previous_wt + roll_wt) <= allowed_wt:
#                         delivery.roll_wt = roll_wt
#                         delivery.delivery_date = deliver_date
#                         delivery.save()
#                         return JsonResponse({'success': True, 'message': 'Existing delivery updated successfully!'})
#                     else:
#                         return JsonResponse({'success': False, 'message': 'Updated roll_wt exceeds the allowed limit.'})
#                 else:
#                     return JsonResponse({'success': False, 'message': 'Cannot add new entry and no existing row to update.'})


#         except Exception as e:
#             return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

#     return JsonResponse({'success': False, 'message': 'Invalid request method.'})




@csrf_exempt
def add_grey_po_deliver(request):
    if request.method == 'POST':
        company_id = request.session.get('company_id')

        try:
            # Parse incoming data
            data = json.loads(request.body)
            tm_id = data.get('tm_id')
            print('tm-id:', tm_id)
            knitting_id = data.get('knitting_id')
            print('party-id:',knitting_id)

            deliver_date = data.get('deliver_date')
            roll_wt = data.get('roll_wt')
            print('roll-wt:'),roll_wt

            pos = grey_fabric_po_table.objects.filter(id=tm_id).first() 
            

            try:
                roll_wt = Decimal(str(data.get('roll_wt'))) if data.get('roll_wt') is not None else Decimal('0.00')
            except (InvalidOperation, TypeError, ValueError):
                return JsonResponse({'success': False, 'message': 'Invalid numeric value for roll_wt.'})

            # Get parent PO bag total
            try:
                parent_po = grey_fabric_po_table.objects.get(id=tm_id)
                allowed_wt = parent_po.total_roll_wt or Decimal('0.00')
            except grey_fabric_po_table.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid PO ID'})

            # Sum of already delivered roll_wt for this PO (as Decimal)
            delivered_total = sub_grey_fabric_po_table.objects.filter(po_id=tm_id,status=1).aggregate(
                total=Sum('roll_wt')
            )['total'] or Decimal('0.00')

            # Check if adding new roll_wt stays within allowed limit
            if delivered_total + roll_wt <= allowed_wt:
                sub_grey_fabric_po_table.objects.create(
                    po_id=tm_id,
                    company_id=company_id,
                    cfyear=2025,
                    party_id=knitting_id,
                    delivery_date=deliver_date,
                    roll_wt=roll_wt
                )
                return JsonResponse({'success': True, 'message': 'New delivery added successfully!'})

            else:


                # Try updating existing delivery if present
                delivery = sub_grey_fabric_po_table.objects.filter(
                    po_id=tm_id,
                    party_id=knitting_id,status=1
                ).first()

                if delivery:
                    previous_wt = Decimal(str(delivery.roll_wt or 0))
                    if (delivered_total - previous_wt + roll_wt) <= allowed_wt:
                        delivery.roll_wt = roll_wt
                        delivery.delivery_date = deliver_date
                        delivery.save()
                        return JsonResponse({'success': True, 'message': 'Existing delivery updated successfully!'})
                    else:
                        return JsonResponse({'success': False, 'message': 'Updated roll_wt exceeds the allowed limit.'})
                else:
                    return JsonResponse({'success': False, 'message': 'Cannot add new entry and no existing row to update.'})




                # # Try updating existing delivery if present
                # delivery = sub_grey_fabric_po_table.objects.filter(
                #     po_id=tm_id
                #     # po_id=tm_id, party_id=knitting_id 
                # ).first()

                # if delivery:
                #     # Subtract current roll_wt from total to check if update is allowed
                #     # previous_wt = delivery.roll_wt or Decimal('0.00')
                #     previous_wt = Decimal(str(delivery.roll_wt or 0))

                #     if (delivered_total - previous_wt + roll_wt) <= allowed_wt:
                #         delivery.roll_wt = roll_wt
                #         delivery.delivery_date = deliver_date
                #         delivery.save()
                #         return JsonResponse({'success': True, 'message': 'Existing delivery updated successfully!'})
                #     else:
                #         return JsonResponse({'success': False, 'message': 'Updated roll_wt exceeds the allowed limit.'})
                # else:
                #     return JsonResponse({'success': False, 'message': 'Cannot add new entry and no existing row to update.'})


        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




def update_yarn_po(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data
                child_data = child_po_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('amount'))['amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    # parent_data = grey_fabric_po_table.objects.filter(id=master_id).first()
                    # if parent_data:
                    #     tax_total = parent_data.tax_total or 0
                    #     round_off = parent_data.round_off or 0
                    #     grand_total = total_amount + tax_total + round_off
                    # else:
                    #     tax_total = round_off = grand_total = 0

                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0  
                    for item in data: 
                        index += 1  
                        formatted_data.append({
                            'action': '<button type="button" onclick="purchase_order_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="purchase_order_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'product': getItemNameById(count_table, item['yarn_count_id']),
                            'bag': item['bag'] if item['bag'] else '-',
                            'per_bag': item['per_bag'] if item['per_bag'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'rate': item['net_rate'] if item['net_rate'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                       
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
def delete_grey_fab_po(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        if not data_id:
            return JsonResponse({'message': 'PO ID is required.'})

        try:
            # Check if any inward entries for this PO have status ≠ 0 (i.e., still active)
            has_nonzero_status = sub_gf_inward_table.objects.filter(
                po_id=data_id
            ).exclude(status=0).exists()
            po = grey_fabric_po_table.objects.filter(id=data_id).first()
            po_name = po.name
            if has_nonzero_status:
                return JsonResponse({
                    # 'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active.'
                    'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active. You must delete the inward first.'

                })

            # All inward entries are status=0, so proceed to soft-delete
            grey_fabric_po_table.objects.filter(id=data_id).update(status=0, is_active=0)
            sub_grey_fabric_po_table.objects.filter(po_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            print("Error during deletion:", e)
            return JsonResponse({'message': 'Error occurred during deletion.'})

    return JsonResponse({'message': 'Invalid request method'})



def getItemNameById(tbl, product_id):
    try:
        party = tbl.objects.get(id=product_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message 
    return party




def po_detail_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_grey_fabric_po_table.objects.filter(id=request.POST.get('id'))
    print('po-data:',data)
    return JsonResponse(data.values()[0])





def gfpo_update(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        master_id = request.POST.get('tm_id')
        product_id = request.POST.get('product_id')
        bag = request.POST.get('bag')
        per_bag = request.POST.get('per_bag')
        quantity = request.POST.get('quantity')
        fabric_id = request.POST.get('fabric_id')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        amount = request.POST.get('amount')

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = grey_fabric_po_table.objects.get(id=master_id)
            parent_item.fabric_id = fabric_id
            parent_item.yarn_count_id = product_id
            parent_item.name = name
            parent_item.roll = bag
            parent_item.roll_wt = per_bag
            parent_item.quantity = quantity

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'PO item updated successfully'})

        except grey_fabric_po_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Parent PO not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

@csrf_exempt
def po_detail_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        print('data-id:', data_id)

        if not data_id:
            return JsonResponse({'message': 'PO ID is required.'})

        try:
            pos = sub_grey_fabric_po_table.objects.filter(id=data_id,status=1).first()
            if not pos:
                return JsonResponse({'message': 'Sub PO entry not found.'})

            po_ids = pos.po_id
            po = grey_fabric_po_table.objects.filter(id=po_ids).first()
            if not po:
                return JsonResponse({'message': 'PO not found for deletion.'})

            # Check if any inward entries for this PO have status ≠ 0
            has_nonzero_status = sub_gf_inward_table.objects.filter(
                po_id=po.id
            ).exclude(status=0).exists()

            if has_nonzero_status:
                return JsonResponse({
                    'message': f'Cannot delete: PO ({po.name}) has inward entries that are still active. You must delete the inward first.'
                })

            # Soft-delete the sub entry only (not entire PO)
            pos.status = 0
            pos.is_active = 0
            pos.save()

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            print("Error during deletion:", e)
            return JsonResponse({'message': 'Error occurred during deletion.'})

    return JsonResponse({'message': 'Invalid request method'})
