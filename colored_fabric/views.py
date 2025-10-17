from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from program_app.models import *
from accessory.models import *
from colored_fabric.models import *
from program_app.models import dyeing_program_table, knitting_table, sub_knitting_table
from program_app.program import dyeing_program_delete
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
from colored_fabric.models import * 
from django.utils.timezone import make_aware

from yarn.views import dyeing_program




def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 


# Create your views here.


def dyed_fabric_po(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
      
        party =  party_table.objects.filter(status=1).filter(is_trader=1)
 
        yarn_count = count_table.objects.filter(status=1)
        dyeing = dyeing_program_table.objects.filter(status=1,is_dyed_fabric=1)

        lot = (
            dyed_fabric_po_table.objects
            .filter(status=1)
            .values('lot_no')  # Group by lot_no
            .annotate(
                total_gross_wt=Sum('total_wt'),
             
            )   
            .order_by('lot_no')
        )
        return render(request,'po/dyed_fabric_po.html',{'party':party,'yarn_count':yarn_count,'dyeing':dyeing,'lot':lot})
    else:
        return HttpResponseRedirect("/admin") 
    




def generate_po_num_series():
    last_purchase = dyed_fabric_po_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.po_number:
        match = re.search(r'PO-(\d+)', last_purchase.po_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"PO-{next_num:03d}"

def dyed_fab_po_add(request): 
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

        party = party_table.objects.filter(status=1,is_fabric=1)
        # out_party = party_table.objects.filter(status=1,is_process=1)
        purchase_number = generate_po_num_series
        return render(request, 'po/dyed_fabric_po_add.html', {
            'party': party,
            'product': product,
            'count':count,
            'fabric_program':fabric_program,
            'purchase_number': purchase_number,
            'knitting':knitting,
            
        }) 
    else:
        return HttpResponseRedirect("/admin")





from collections import defaultdict
from django.http import JsonResponse


def dyeing_program_list(request):
    if request.method == 'POST':
        prg_id = request.POST.get('prg_id')

        # Lookup dictionaries for names
        color_dict = dict(color_table.objects.values_list('id', 'name'))
        dia_dict = dict(dia_table.objects.values_list('id', 'name'))
        fabric_dict = dict(fabric_program_table.objects.values_list('id', 'name'))

        # Result format: fabric -> color -> dia -> {roll, roll_wt}
        result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'roll': 0, 'roll_wt': 0})))
        dia_names = set()
        fabric_names = set()
        color_names = set()

        records = sub_dyeing_program_table.objects.filter(tm_id=prg_id)

        for rec in records:
            fabric = fabric_dict.get(rec.fabric_id, 'NA')
            color = color_dict.get(rec.color_id, 'NA')
            dia = dia_dict.get(rec.dia_id, 'NA')

            result[fabric][color][dia]['roll'] += rec.roll
            result[fabric][color][dia]['roll_wt'] += rec.roll_wt

            dia_names.add(dia)
            color_names.add(color)
            fabric_names.add(fabric)

        sorted_dias = sorted(dia_names, key=lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else x)
        sorted_fabrics = sorted(fabric_names)
        sorted_colors = sorted(color_names)

        final_data = {
            'dias': sorted_dias,
            'rows': []
        }

        for fabric in sorted_fabrics:
            for color in sorted_colors:
                row = {'fabric': fabric, 'color': color}
                for dia in sorted_dias:
                    entry = result[fabric][color].get(dia, {'roll': 0, 'roll_wt': 0})
                    if entry['roll'] > 0 or entry['roll_wt'] > 0:
                        row[dia] = f"{entry['roll']} / {entry['roll_wt']:.1f}"
                    else:
                        row[dia] = ''
                final_data['rows'].append(row)

        return JsonResponse({'data': final_data})


# `````````````````````````````````````````````````````` add po ``````````````````````````````````````````````````````````

from django.db import transaction

def insert_dyed_fabric_po(request):
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

            

            # Handle knitting data
            program_data_raw = request.POST.get('program_data', '[]')
            program_data = json.loads(program_data_raw) if program_data_raw else []

            po_no = generate_po_num_series()

            actual_rate = float(request.POST.get('actual_rate', 0))
            gross_wt = float(request.POST.get('gross_wt', 0))
            discount = float(request.POST.get('discount', 0))
            rate = float(request.POST.get('rate', 0))
            # amount = float(request.POST.get('amount', 0))

            with transaction.atomic():
                # Create parent PO   
                material_request = dyed_fabric_po_table.objects.create(
                    po_number=po_no,
                    po_date=po_date,
                    po_name=name,
                    lot_no = lot_no,
                    program_id=program_id,
                    party_id=party_id,
                    company_id=company_id,
                    cfyear=2025,
                    remarks=remarks,
                    total_rolls = sum(int(k.get('roll', 0)) for k in program_data),
                    # total_roll_wt = sum(float(k.get('roll_wt', 0.00)) for k in program_data),
                    total_wt = sum(float(k.get('roll_wt', 0.00)) for k in program_data),

                    rate=actual_rate,
                    # gross_quantity=gross_wt,
                    discount=discount,
                    net_rate=rate,


                    is_active=1,
                    status=1,
                    created_by=user_id,
                    created_on=timezone.now(),
                )

            

                # Save knitting table values into grey_fabric_po_program_table
                for knit in program_data:
                    sub_dyed_fab_po_table.objects.create( 
                        dyeing_program_id=program_id, 
                        tm_id=material_request.id,
                        knitting_program_id = 0 ,
                        # tex_id=knit.get('tex_id'),
                        dia_id=knit.get('dia_id'),
                        fabric_id=knit.get('fabric_id'),
                        color_id=int(knit.get('color_id', 0)), 
                        roll=int(knit.get('roll', 0)),
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

    return render(request, 'po/dyed_fabric_po_add.html')





def dyed_po_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)


    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    dye_prg = request.POST.get('dye_prg', '')
    lot_no = request.POST.get('lot_no', '')
    party = request.POST.get('party', '')
    # yarn_count = request.POST.get('yarn_count', '')
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


    if dye_prg:
        query &= Q(program_id=dye_prg)

    if lot_no:
            query &= Q(lot_no=lot_no)
 



    # Apply filters
    queryset = dyed_fabric_po_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())

    # data = list(dyed_fabric_po_table.objects.filter(status=1).order_by('-id').values())

    formatted = []

    for index, item in enumerate(data):
        # Fetch the child PO for each parent PO
        child_po = dyed_fabric_po_table.objects.filter(id=item['id'], status=1).first()

        # if child_po:  # Ensure child_po is not None
        #     yarn = child_po.yarn_count_id
        # else:
        #     yarn = None  # If no child PO exists, handle accordingly

        formatted.append({
            'action': '<button type="button" onclick="dyed_po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="dyed_fabric_po_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>\
                        <button type="button" onclick="dyed_fabric_po_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>' .format(item['id'], item['id'], item['id']),
            'id': index + 1,
            'po_date': item['po_date'] if item['po_date'] else '-', 
            'po_number': item['po_number'] if item['po_number'] else '-',
            'lot_no': item['lot_no'] if item['lot_no'] else '-',
            'name': item['po_name'] if item['po_name'] else '-', 
            'party': getItemNameById(party_table, item['party_id']),
            'program': getDyeingDisplayNameById(dyeing_program_table, item['program_id']), 
           
            'total_roll': item['total_rolls'] if item['total_rolls'] else '-',
            'total_roll_wt': item['total_wt'] if item['total_wt'] else '-',
         
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted}) 



from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
import base64
from collections import defaultdict



@csrf_exempt
def dyed_fabric_po_print(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(dyed_fabric_po_table, id=order_id)
    customer_value = get_object_or_404(party_table, status=1, id=total_values.party_id)

    prg_details = sub_dyed_fab_po_table.objects.filter(tm_id=order_id, status=1).values(
        'roll', 'roll_wt', 'fabric_id', 'dyeing_program_id', 'dia_id', 'color_id'
    )

    # Group by (fabric, color), then by dia
    grouped_data = defaultdict(lambda: defaultdict(lambda: {'roll': 0, 'roll_wt': 0}))
    dia_set = set()

    for item in prg_details:
        try:
            product = get_object_or_404(fabric_program_table, id=item['fabric_id'])
            fabric = get_object_or_404(fabric_table, id=product.fabric_id, status=1).name
            color = get_object_or_404(color_table, id=item['color_id']).name
            dia = get_object_or_404(dia_table, id=item['dia_id']).name

            dia_set.add(dia)

            key = (fabric, color)
            grouped_data[key][dia]['roll'] += item['roll']
            grouped_data[key][dia]['roll_wt'] += float(item['roll_wt'])

        except Exception as e:
            print('Error processing record:', e)
            continue

    # Sort dias for consistent columns
    sorted_dias = sorted(dia_set, key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else x)

    # Build final table_rows
    table_rows = []
    for (fabric, color), dia_data in grouped_data.items():
        row = {
            'fabric': fabric,
            'color': color,
            'dias': []
        }
        for dia in sorted_dias:
            row['dias'].append({
                'roll': dia_data[dia]['roll'] if dia in dia_data else '',
                'roll_wt': dia_data[dia]['roll_wt'] if dia in dia_data else ''
            })
        table_rows.append(row)
        print('tbl-rows:',table_rows)
    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'dias': sorted_dias,
        'table_rows': table_rows,
        'customer_name': customer_value.name,
        'mobile_no': customer_value.mobile,
        'address_line1': customer_value.address,
        'gstin': customer_value.gstin,
        'total_rolls': sum([sum(d['roll'] for d in r['dias'] if isinstance(d['roll'], (int, float))) for r in table_rows]),
        'total_wt': sum([sum(d['roll_wt'] for d in r['dias'] if isinstance(d['roll_wt'], (int, float))) for r in table_rows]),
        'image_url': image_url,
        'total_values': total_values,
        'company': company_table.objects.filter(status=1).first()
    }

    return render(request, 'po/dyed_po_print.html', context)



def dyed_fabric_po_edit(request):  
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'po/dyed_fabric_po_details.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'po/dyed_fabric_po_details.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
       

        # Fetch the material instance using 'tm_id'
        # material_instance = sub_dyed_fab_po_table.objects.filter(tm_id=material_id).first()
       
        # Fetch the parent stock instance
        parent_stock_instance = dyed_fabric_po_table.objects.filter(id=material_id).first()

        # Fetch supplier name using supplier_id from parent_stock_instance
        
        # knitting = knitting_table.objects.filter(status=1)
        # knitting = knitting_table.objects.filter(status=1,is_grey_fabric=1)

        # Filter knitting_table
        program = dyeing_program_table.objects.filter(status=1, is_dyed_fabric=1)
        # program = dyeing_program_table.objects.filter(status=1, is_dyed_fabric=1)
        print('prg:',program)
        party = party_table.objects.filter(status=1,is_fabric=1)
       
        # Render the edit page with the material instance and supplier name
        context = { 
            # 'material_instance': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'party': party,
            'program':program, 
     
        
        }
        return render(request, 'po/dyed_fabric_po_details.html', context)

    except Exception as e:
        return render(request, 'po/dyed_fabric_po_details.html', {'error_message': 'An unexpected error occurred: ' + str(e)})





def update_dyed_fabric_po(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        master_id = request.POST.get('tm_id')
        program_id = request.POST.get('program_id')
       
        remarks = request.POST.get('remarks')
        party_id = request.POST.get('party_id')
        lot_no = request.POST.get('lot_no')
        po_rate = request.POST.get('actual_rate')
        price = request.POST.get('rate')
        discount = request.POST.get('discount')
        # amount = request.POST.get('amount')

        if not master_id or not program_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = dyed_fabric_po_table.objects.get(id=master_id)
            # parent_item.knitting_program_id = program_id
            parent_item.party_id = party_id
            parent_item.lot_no = lot_no
            parent_item.po_name = name

            parent_item.rate = po_rate
            parent_item.net_rate = price
            parent_item.discount = discount


            parent_item.remarks = remarks
            parent_item.save()

            return JsonResponse({'success': True, 'message': 'dyed Fabric PO item updated successfully'})

        except dyed_fabric_po_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Parent PO not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})






@csrf_exempt
def dyed_fabric_po_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        print('ids:',data_id)
        if not data_id:
            return JsonResponse({'message': 'PO ID is required.'})

        try:
            # Check if any inward entries for this PO have status ≠ 0 (i.e., still active)
            # has_nonzero_status = sub_dyed_fabric_inward_table.objects.filter(
            #     po_id=data_id
            # ).exclude(status=0).exists()
            po = dyed_fabric_po_table.objects.filter(id=data_id).first()
            po_name = po.po_name
            # if has_nonzero_status:
            #     return JsonResponse({
            #         # 'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active.'
            #         'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active. You must delete the inward first.'

            #     })

            # All inward entries are status=0, so proceed to soft-delete
            dyed_fabric_po_table.objects.filter(id=data_id).update(status=0, is_active=0)
            sub_dyed_fab_po_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            print("Error during deletion:", e)
            return JsonResponse({'message': 'Error occurred during deletion.'})

    return JsonResponse({'message': 'Invalid request method'})

