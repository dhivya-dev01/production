from cairo import Status
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
from colored_fabric.models import dyed_fabric_inward_table
from company.models import *
from employee.models import *

from grey_fabric.models import *


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

from django.utils.timezone import make_aware

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


from software_app.views import fabric_program, getItemNameById, getSupplier, is_ajax, knitting_program

# ``````````````````````````````````````````````   cutting entry ``````````````````````````````````````````


def cutting_entry(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1) 

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        lot = (
            cutting_entry_table.objects
            .filter(status=1)
            .values('lot_no')  # Group by lot_no 
            .annotate(
                total_gross_wt=Sum('total_wt'),
             
            )   
            .order_by('lot_no')
        )
        cutting = cutting_program_table.objects.filter(status=1)

        return render(request,'cutting_entry/cutting_entry_list.html',{'party':party,'fabric_program':fabric_program,
                                                                       'cutting':cutting,'lot':lot,'quality':quality,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    



from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils.timezone import make_aware
from datetime import datetime

def cutting_entry_view(request):   
    company_id = request.session.get('company_id') 
    print('company_id:', company_id)

    # Filters from POST request
    lot_no = request.POST.get('lot', '')
    cut_prg = request.POST.get('cut_prg', '')
    quality = request.POST.get('quality', '')
    style = request.POST.get('style', '')
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    query = Q()

    # Handle date range filter
    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            date_filter = Q(inward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })

    if lot_no:
        query &= Q(lot_no=lot_no)
    if cut_prg:
        query &= Q(tm_cutting_prg_id=cut_prg)
    if quality:
        query &= Q(quality_id=quality)
    if style:
        query &= Q(style_id=style)

    # Fetch main cutting entries
    queryset = cutting_entry_table.objects.filter(status=1).filter(query).order_by('-id')
    data = list(queryset.values())

    formatted = []

    for index, item in enumerate(data):
        # Fetch total_wt from sub_cutting_entry_table for each main record
        sub_data = sub_cutting_entry_table.objects.filter(status=1, tm_id=item['id'])
        total_wt = sub_data.aggregate(total_wt=Sum('wt'))['total_wt'] or 0

        formatted.append({
            'action': f'''
                <button type="button" onclick="cutting_entry_edit('{item['id']}')" class="btn btn-primary btn-xs">
                    <i class="feather icon-edit"></i>
                </button>
                <button type="button" onclick="cutting_entry_delete('{item['id']}')" class="btn btn-danger btn-xs">
                    <i class="feather icon-trash-2"></i>
                </button>
                <button type="button" onclick="cutting_entry_print('{item['id']}')" class="btn btn-success btn-xs">
                    <i class="feather icon-printer"></i>
                </button>
                <button type="button" onclick="cutting_entry_abstract_print('{item['id']}')" class="btn btn-success btn-xs">
                    Abstract
                </button>
                <button type="button" onclick="cutting_entry_qrcode_print('{item['id']}')" class="btn btn-info btn-xs">
                    QR
                </button>
            ''',
            'id': index + 1,
            'inward_date': item['inward_date'] or '-',
            'work_order_no': item['work_order_no'] or '-',
            'inward_no': item['cutting_no'] or '-',
            'lot_no': item['lot_no'] or '-',
            'cutting_prg': getCutting_entryNoById(cutting_program_table, item['tm_cutting_prg_id']),
            'quality': getSupplier(quality_table, item['quality_id']),
            'style': getSupplier(style_table, item['style_id']),
            'total_wt': total_wt,
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted})

 
# def cutting_entry_view(request):   
#     company_id = request.session['company_id'] 
#     print('company_id:',company_id)
#     # user_type = request.session.get('user_type')
#     # has_access, error_message = check_user_access(user_type, "customer", "read") 

#     # if not has_access:  
#     #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})


#     query = Q() 

#     # Date range filter
#     lot_no = request.POST.get('lot', '')
#     cut_prg = request.POST.get('cut_prg', '')
#     quality = request.POST.get('quality', '')
#     style = request.POST.get('style', '')
#     start_date = request.POST.get('from_date', '')
#     end_date = request.POST.get('to_date', '')

#     if start_date and end_date:
#         try:
#             start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
#             end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

#             # Match if either created_on or updated_on falls in range
#             date_filter = Q(inward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
#             query &= date_filter
#         except ValueError:
#             return JsonResponse({
#                 'data': [],
#                 'message': 'error',
#                 'error_message': 'Invalid date format. Use YYYY-MM-DD.'
#             })
    
#     if lot_no:
#             query &= Q(lot_no=lot_no)

#     if cut_prg:
#             query &= Q(tm_cutting_prg_id=cut_prg)

#     if quality:
#             query &= Q(quality_id=quality)

#     if style:
#             query &= Q(style_id=style)



#     # Apply filters
#     queryset = cutting_entry_table.objects.filter(status=1).filter(query)
#     data = list(queryset.order_by('-id').values())

#     sub_data = sub_cutting_entry_table.objects.filter(status=1,tm_id=data.id)
#     if sub_data:
#         total_wt = sum(sub_data.wt)
#     else:
#         total_wt=0

#     # data = list(cutting_entry_table.objects.filter(status=1).order_by('-id').values())
 
#     formatted = [
#         {
#             'action': '<button type="button" onclick="cutting_entry_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
#                         <button type="button" onclick="cutting_entry_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
#                         <button type="button" onclick="cutting_entry_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>\
#                         <button type="button" onclick="cutting_entry_abstract_print(\'{}\')" class="btn btn-success btn-xs">Abstract</button>\
#                         <button type="button" onclick="cutting_entry_qrcode_print(\'{}\')" class="btn btn-info btn-xs">QR</button>'.format(item['id'],item['id'],item['id'], item['id'],item['id']),
#             'id': index + 1, 
#             'inward_date': item['inward_date'] if item['inward_date'] else'-', 
#             'work_order_no': item['work_order_no'] if item['work_order_no'] else'-', 
#             'inward_no': item['cutting_no'] if item['cutting_no'] else'-', 
#             'lot_no': item['lot_no'] if item['lot_no'] else'-', 
#             'cutting_prg':getCutting_entryNoById(cutting_program_table, item['tm_cutting_prg_id'] ),  
#             'quality':getSupplier(quality_table, item['quality_id'] ), 
#             'style':getSupplier(style_table, item['style_id'] ), 
#             # 'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
#             'total_wt': total_wt, #item['total_wt'] if item['total_wt'] else'-', 
#             'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

#         } 
#         for index, item in enumerate(data)
#     ]
#     return JsonResponse({'data': formatted})  
 

from collections import defaultdict


@csrf_exempt
def cutting_entry_print_header_size(request):
    po_id = request.GET.get('k') 
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(cutting_entry_table, id=order_id)

    prg_details = sub_cutting_entry_table.objects.filter(tm_id=order_id).values(
        'id', 'quantity', 'size_id', 'color_id'
    )

    product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
    fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
    quality = get_object_or_404(quality_table, id=total_values.quality_id)
    style = get_object_or_404(style_table, id=total_values.style_id)

    # Unique sorted sizes
    unique_size_ids = set([p['size_id'] for p in prg_details])
    sorted_sizes_qs = size_table.objects.filter(id__in=unique_size_ids, status=1).order_by('sort_order_no')
    sizes = [s.name for s in sorted_sizes_qs]
    size_id_name_map = {s.id: s.name for s in sorted_sizes_qs}

    combined_details = []
    grand_total = 0

    for prg_detail in prg_details:
        size_name = size_id_name_map.get(prg_detail['size_id'], 'Unknown')
        color_obj = get_object_or_404(color_table, id=prg_detail['color_id'])

        row = {size: '' for size in sizes}
        row[size_name] = prg_detail['quantity']
        row['color'] = color_obj.name
        row['total'] = prg_detail['quantity']
        combined_details.append(row)
        grand_total += prg_detail['quantity']

    context = {
        'sizes': sizes,
        'combined_details': combined_details,
        'grand_total': grand_total, 
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
    }

    return render(request, 'cutting_entry/cutting_entry_print.html', context)



@csrf_exempt
def cutting_entry_print(request):
    po_id = request.GET.get('k') 
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(cutting_entry_table, id=order_id)
    total_dz = total_values.total_pcs
    dozen = total_dz //12
    pcs = total_dz % 12
    prg_details = sub_cutting_entry_table.objects.filter(tm_id=order_id).values(
        'id', 'quantity', 'size_id', 'color_id','wt','cutter'
    )
   
    combined_details = []
    total_quantity = 0 
    total_wt = 0 
 
    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        quality = get_object_or_404(quality_table, id=total_values.quality_id)
        style = get_object_or_404(style_table, id=total_values.style_id)

        size = get_object_or_404(size_table, id=prg_detail['size_id'])
        color = get_object_or_404(color_table, id=prg_detail['color_id'])

        quantity = prg_detail['quantity']
        wt = prg_detail['wt']
        cutter = prg_detail['cutter']
        total_quantity += quantity
        total_wt += wt



        combined_details.append({
            'fabric': fabric_obj.name,
            'style': style.name,
            'quality': quality.name,
            'color': color.name,
            'size': size.name,
            'quantity': quantity,
            'wt':wt,
            'cutter':cutter 
        }) 

    context = {
        'total_values': total_values,
        'combined_details': combined_details,
        'grand_total': total_quantity,
        'total_wt': total_wt,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
        'total_dozen':dozen,
        'total_pcs':pcs
    }

    return render(request, 'cutting_entry/cutting_entry_print.html', context)






from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
import base64


@csrf_exempt
def cutting_entry_abstract_print(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception: 
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(cutting_entry_table, id=order_id)
    total_pcs = total_values.total_pcs
    total_dozen = total_pcs / 12 if total_pcs else 0

    total_dozen = total_pcs // 12
    total_rem_pcs = total_pcs % 12

    prg_details = sub_cutting_entry_table.objects.filter(tm_id=order_id).values(
        'quantity', 'wt', 'size_id', 'color_id'
    )

    total_quantity = 0
    total_weight = 0

    product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
    fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
    quality = get_object_or_404(quality_table, id=total_values.quality_id)
    style = get_object_or_404(style_table, id=total_values.style_id)

    unique_size_ids = set()
    unique_color_ids = set()
    grouped_data_raw = []

    for entry in prg_details:
        size_id = entry['size_id']
        color_id = entry['color_id']
        qty = entry['quantity'] or 0
        wt = entry['wt'] or 0

        unique_size_ids.add(size_id)
        unique_color_ids.add(color_id)

        total_quantity += qty
        total_weight += wt

        grouped_data_raw.append({
            'size_id': size_id,
            'color_id': color_id,
            'quantity': qty,
            'wt': wt
        })

    size_objs = size_table.objects.filter(id__in=unique_size_ids, status=1).order_by('sort_order_no')
    color_objs = color_table.objects.filter(id__in=unique_color_ids, status=1)

    size_map = {s.id: s.name for s in size_objs}
    color_map = {c.id: c.name for c in color_objs}
    sizes = [size_map[s.id] for s in size_objs]

    # Group by color → size
    grouped_data_dict = defaultdict(lambda: defaultdict(lambda: {'quantity': 0, 'wt': 0}))

    for item in grouped_data_raw:
        size_name = size_map.get(item['size_id'], '-')
        color_name = color_map.get(item['color_id'], '-')
        grouped_data_dict[color_name][size_name]['quantity'] += item['quantity']
        grouped_data_dict[color_name][size_name]['wt'] += item['wt']

    # Prepare grouped data for display
    grouped_data = []
    for color_name, size_data in grouped_data_dict.items():
        row = {
            'color': color_name,
            'size_data_list': [],
            'total_quantity': 0,
            'total_wt': 0
        }

        for size_name in sizes:
            entry = size_data.get(size_name, {'quantity': 0, 'wt': 0})
            row['size_data_list'].append(entry)
            row['total_quantity'] += entry.get('quantity') or 0
            row['total_wt'] += entry.get('wt') or 0

        row['total_dozen'] = row['total_quantity'] / 12 if row['total_quantity'] else 0
        grouped_data.append(row)

    # ✅ Size-wise totals (pcs and wt)
    size_totals = {size: {'quantity': 0, 'wt': 0} for size in sizes}
    for row in grouped_data:
        for i, size_name in enumerate(sizes):
            entry = row['size_data_list'][i]
            size_totals[size_name]['quantity'] += entry.get('quantity') or 0
            size_totals[size_name]['wt'] += entry.get('wt') or 0

    # ✅ Add dozen per size

    for size in sizes:
        qty = size_totals[size]['quantity']
        dozen = qty // 12
        rem = qty % 12
        size_totals[size]['dozen'] = dozen
        size_totals[size]['remaining'] = rem



    # for size in sizes:
    #     qty = size_totals[size]['quantity']
    #     size_totals[size]['dozen'] = qty / 12 if qty else 0

    size_totals_list = [size_totals[size] for size in sizes]
    total_columns = 2 + len(sizes) * 2

    context = {
        'total_values': total_values,
        'sizes': sizes,
        'grouped_data': grouped_data,
        'dia_totals_list': size_totals_list,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'total_columns': total_columns,
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
        'grand_total_quantity': total_quantity,
        'grand_total_weight': total_weight,
        'total_dozen': total_dozen,  # ✅ Needed in footer
        'total_rem_pcs':total_rem_pcs
    }

    return render(request, 'cutting_entry/cutting_entry_abstract_print.html', context)



@csrf_exempt
def cutting_entry_abstract_print_test(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(cutting_entry_table, id=order_id)
    total_pcs = total_values.total_pcs
    total_dozen = total_pcs/ 12
    print('total-dozen:',total_dozen)
    prg_details = sub_cutting_entry_table.objects.filter(tm_id=order_id).values(
        'quantity', 'wt', 'size_id', 'color_id'
    )
 
    total_quantity = 0
    total_weight = 0

    product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
    fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
    quality = get_object_or_404(quality_table, id=total_values.quality_id)
    style = get_object_or_404(style_table, id=total_values.style_id)

    # Collect unique size IDs and color IDs for ordering and names
    unique_size_ids = set()
    unique_color_ids = set()
    grouped_data_raw = []

    for entry in prg_details:
        size_id = entry['size_id']
        color_id = entry['color_id']
        qty = entry['quantity'] or 0
        wt = entry['wt'] or 0

        unique_size_ids.add(size_id)
        unique_color_ids.add(color_id)

        total_quantity += qty
        total_weight += wt

        grouped_data_raw.append({
            'size_id': size_id,
            'color_id': color_id,
            'quantity': qty,
            'wt': wt
        })

    # Fetch size and color names
    size_objs = size_table.objects.filter(id__in=unique_size_ids, status=1).order_by('sort_order_no')
    color_objs = color_table.objects.filter(id__in=unique_color_ids, status=1)

    size_map = {s.id: s.name for s in size_objs}
    color_map = {c.id: c.name for c in color_objs}
    sizes = [size_map[s.id] for s in size_objs]

    # Group by color → size
    grouped_data_dict = defaultdict(lambda: defaultdict(lambda: {'quantity': 0, 'wt': 0}))

    for item in grouped_data_raw:
        size_name = size_map.get(item['size_id'], '-')
        color_name = color_map.get(item['color_id'], '-')
        grouped_data_dict[color_name][size_name]['quantity'] += item['quantity']
        grouped_data_dict[color_name][size_name]['wt'] += item['wt']

    grouped_data = []
    # for color_name, size_data in grouped_data_dict.items():
    #     row = {
    #         'color': color_name,
    #         'size_data_list': [], 
    #         'total_quantity': 0,
    #         'total_wt': 0
    #     }
 
    #     for size_name in sizes:
    #         entry = size_data.get(size_name, {'quantity': 0, 'wt': 0})
    #         row['size_data_list'].append(entry)
    #         row['total_quantity'] += entry.get('quantity') or 0
    #         row['total_wt'] += entry.get('wt') or 0

    #     grouped_data.append(row)


    for color_name, size_data in grouped_data_dict.items():
        row = {
            'color': color_name,
            'size_data_list': [],
            'total_quantity': 0,
            'total_wt': 0
        }

        for size_name in sizes:
            entry = size_data.get(size_name, {'quantity': 0, 'wt': 0})
            row['size_data_list'].append(entry)
            row['total_quantity'] += entry.get('quantity') or 0
            row['total_wt'] += entry.get('wt') or 0

        # 👉 Add this line to calculate total dozen for the color
        row['total_dozen'] = row['total_quantity'] / 12 if row['total_quantity'] else 0

        grouped_data.append(row)

    for size in sizes:
        qty = size_totals[size]['quantity']
        size_totals[size]['dozen'] = qty / 12 if qty else 0


    # Size-wise totals
    size_totals = {size: {'quantity': 0, 'wt': 0} for size in sizes}
    for row in grouped_data:
        for i, size_name in enumerate(sizes): 
            entry = row['size_data_list'][i]
            size_totals[size_name]['quantity'] += entry.get('quantity') or 0
            size_totals[size_name]['wt'] += entry.get('wt') or 0

    size_totals_list = [size_totals[size] for size in sizes]
    total_columns = 2 + len(sizes) * 2

    context = {
        'total_values': total_values,
        'sizes': sizes,
        'grouped_data': grouped_data,
        'dia_totals_list': size_totals_list,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'total_columns': total_columns,
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'style': style.name,
        'quality': quality.name,
        'grand_total_quantity': total_quantity,
        'grand_total_weight': total_weight, 
    }

    return render(request, 'cutting_entry/cutting_entry_abstract_print.html', context)



@csrf_exempt
def cutting_qr_code_print(request):
    from datetime import datetime
    from collections import defaultdict

    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(cutting_entry_table, id=order_id)
    product = get_object_or_404(fabric_program_table, id=total_values.fabric_id)
    fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
    quality = get_object_or_404(quality_table, id=total_values.quality_id)
    style = get_object_or_404(style_table, id=total_values.style_id)

    try:
        entry_month = total_values.created_on.month  # Adjust if different
    except AttributeError:
        from datetime import datetime
        entry_month = datetime.now().month

    month_str = str(entry_month).zfill(2)

    prg_details = sub_cutting_entry_table.objects.filter(tm_id=order_id).values('id', 'quantity', 'size_id', 'color_id','work_order_no')

    qr_blocks = []
    for detail in prg_details:
        size = get_object_or_404(size_table, id=detail['size_id'])
        color = get_object_or_404(color_table, id=detail['color_id'])
        quantity = detail['quantity']
        work_order_no = str(detail['work_order_no']).zfill(3)

        qr_text = f"2025{month_str}/{work_order_no}/{quality.name}/{style.name}/{size.name}/{color.name}/{quantity}"
        qr_base64 = generate_qr_base64(qr_text)

        qr_blocks.append({
            'work_order_no': work_order_no,
            'quality': quality.name,
            'style': style.name,
            'size': size.name,
            'color': color.name,
            'quantity': quantity,
            'qr_code': qr_base64,
        })

    context = {
        'qr_blocks': qr_blocks,
        'company': company_table.objects.filter(status=1).first(),
        'fabric': fabric_obj.name,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',

    }

    return render(request, 'cutting_entry/qrcode_print.html', context)


 
from django.http import JsonResponse
from django.db.models import Sum


def generate_inward_num_series():
    last_purchase = cutting_entry_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.cutting_no:
        match = re.search(r'INW-(\d+)', last_purchase.cutting_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
 
    return f"INW-{next_num:03d}"



from django.shortcuts import render, HttpResponseRedirect
from django.db import connection

def add_cutting_entry(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']

        party = party_table.objects.filter(status=1, is_cutting=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 
        inward_no = generate_inward_num_series()  # <-- call the function properly
        quality = quality_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1) 
        color = color_table.objects.filter(status=1)
        cutting_program = cutting_program_table.objects.filter(status=1)
 
        # ✅ Lot-wise available quantity query
        with connection.cursor() as cursor:
            cursor.execute("""  
                SELECT 
                    inward.lot_no,
                    inward.total_wt AS inw_wt,
                    COALESCE(inward.total_wt, 0) - COALESCE(cutting.total_cutting_wt, 0) AS available_wt
                FROM (
                    SELECT 
                        tx.lot_no,  
                        MAX(tm.total_wt) AS total_wt
                    FROM tx_dyed_fab_inward AS tx
                    LEFT JOIN tm_dyed_fab_inward AS tm ON tx.tm_id = tm.id
                    WHERE tx.status = 1
                    GROUP BY tx.lot_no
                ) AS inward
                LEFT JOIN (
                    SELECT 
                        lot_no,  
                        SUM(wt) AS total_cutting_wt
                    FROM tx_cutting_entry
                    WHERE status = 1
                    GROUP BY lot_no
                ) AS cutting ON inward.lot_no = cutting.lot_no
            """)
            lot_rows = cursor.fetchall()

        # ✅ Filter only lots with available weight > 0
        lot_no = [
            {'lot_no': row[0], 'total_wt': row[1], 'available_wt': row[2]}
            for row in lot_rows if row[2] > 0
        ]
        print('lot-no:',lot_no) 

        return render(request, 'cutting_entry/add_cutting_entry.html', {
            'party': party,
            'fabric_program': fabric_program, 
            'inward_no': inward_no, 
            'color': color, 
            'lot_no': lot_no,  # now includes available_wt
            'cutting_program': cutting_program,
            'quality': quality, 
            'style': style,
            'size': size 
        })
    else:
        return HttpResponseRedirect("/admin")



@csrf_exempt
def get_cutting_program_list(request):
    if request.method == 'POST':
        prg_id = request.POST.get('prg_id')

        if not prg_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            program_value = get_object_or_404(cutting_program_table, id=prg_id)
            quality = get_object_or_404(quality_table, id=program_value.quality_id)
            style = get_object_or_404(style_table, id=program_value.style_id)

            # Fetch all related sub cutting program entries
            tx_prg_list = sub_cutting_program_table.objects.filter(tm_id=prg_id)

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



# ``````````````````````````````````````````````````

def get_cutting_program_lists(request):
    prg_id = request.POST.get('prg_id')
    programs = cutting_program_table.objects.filter(id=prg_id,is_entry=0).values('id', 'cutting_no', 'total_quantity', 'quality_id', 'style_id')
    
    return JsonResponse(list(programs), safe=False)


from django.http import JsonResponse

def get_sub_cutting_program(request):
    prg_id = request.POST.get('prg_id')

    if not prg_id:
        return JsonResponse({'error': 'Program ID is required'}, status=400)

    program_details = sub_cutting_program_table.objects.filter(tm_id=prg_id).values(
        'size_id', 'color_id', 'quantity'
    )

    size_map = {size.id: size.name for size in size_table.objects.filter(id__in=[p['size_id'] for p in program_details])}
    color_map = {color.id: color.name for color in color_table.objects.filter(id__in=[p['color_id'] for p in program_details])}

    data = [
        {
            'size_id': item['size_id'],
            'size_name': size_map.get(item['size_id'], 'Unknown'),  # Get size name from size_map
            'color_id': item['color_id'],
            'color_name': color_map.get(item['color_id'], 'Unknown'),  # Get color name from color_map
            'quantity': item['quantity']
        }
        for item in program_details
    ]

    return JsonResponse(data, safe=False) 




@csrf_exempt  # Use only if necessary
def get_quality_style_fabrics_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not quality_id and not style_id:
            return JsonResponse({'error': 'Quality ID is required'}, status=400)

        try:
            # Retrieve all fabric programs for the given quality_id
            fabric_programs = quality_program_table.objects.filter(quality_id=quality_id,style_id = style_id)
            if not fabric_programs.exists():
                return JsonResponse({'error': 'No matching records found'}, status=404)
 
            # Collect all styles linked to the fabric programs
           

            fabric_ids = fabric_programs.values_list('fabric_id', flat=True).distinct()
            fabrics = fabric_program_table.objects.filter(id__in=fabric_ids).values('id', 'name')
    
 

            response_data = {
                'fabric': list(fabrics),

                # 'sizes_colors': list(sub_programs)  # List of {size_id, color_id}
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)




from decimal import Decimal, InvalidOperation

def parse_decimal(value):
    try:
        return Decimal(str(value).strip() or 0)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(0)


@csrf_exempt
def insert_cutting_entry(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try: 
            # Extracting Data from Request  
            print('insert-datas:',request.POST)
            party_id = request.POST.get('party_id',0) 
            print('party-id;',party_id)
            prg_id = request.POST.get('prg_id')
            fabric_id = request.POST.get('fab_id')
            print('fab-id:',fabric_id)
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            program_date = request.POST.get('inward_date')
            cutting_data = json.loads(request.POST.get('cutting_data', '[]'))
            lot_no = request.POST.get('lot_no')
            work_order_no = request.POST.get('work_order_no')
            print('Chemical Data:', cutting_data) 

            def clean_amount(amount):
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()


            inward_no = generate_inward_num_series()
 
            material_request = cutting_entry_table.objects.create(
                cutting_no=inward_no.upper(),
                inward_date=program_date,
                tm_cutting_prg_id=prg_id,
                fabric_id=fabric_id or 0,
                lot_no=lot_no,
                work_order_no=work_order_no,
                party_id=party_id,
                quality_id=quality_id,
                style_id=style_id,
                company_id=company_id,
                cfyear=2025, 

                bundle_wt=parse_decimal(request.POST.get('bundle_wt')),
                total_wt=parse_decimal(request.POST.get('total_wt')),
                cutting_waste=parse_decimal(request.POST.get('cutting_waste')),
                damages=parse_decimal(request.POST.get('damage')),
                air_loss=parse_decimal(request.POST.get('air_loss')),
                malai_waste=parse_decimal(request.POST.get('malai_waste')),
                folding_waste=parse_decimal(request.POST.get('folding_waste')),
                total_pcs=parse_decimal(request.POST.get('total_pcs')),
                total_bundles=parse_decimal(request.POST.get('total_bundles')),
                # total_dozen=parse_decimal(request.POST.get('total_dozen')),
                total_dozen=parse_decimal(request.POST.get('total_pcs')) / 12,

                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )



            print('m-req:',material_request)

            po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for cutting in cutting_data:
                print("Processing cutting Data:", cutting)
 
                po_id = cutting.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later 

                sub_entry = sub_cutting_entry_table.objects.create(
                    work_order_no = work_order_no,
                    lot_no = lot_no,
                    tm_id=material_request.id,  
                    size_id=cutting.get('size_id'),  
                    color_id=cutting.get('color_id'),
                    quantity=cutting.get('quantity'),
                    # fabric_id=fabric_id,
                    cutter=str(cutting.get('cutter') or '').upper(),  # ✅ fixed here
                    wt=cutting.get('wt'), 
                    created_by=user_id,
                    created_on=timezone.now(),
                    company_id=company_id,
                    cfyear=2025,

                )


            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, )
                #   'cutting_entry/add_cutting_entry.html')

 




# def cutting_barcode_detail(request):
#     barcode = request.GET.get('barcode')
#     if not barcode:
#         return HttpResponse("No barcode provided", status=400)
# # /CUTTING/BARCODE-DETAIL/?BARCODE=FY2025-1543-20-26-8-20-GOPI-5
#     # You can match based on the URL pattern stored as `barcode`
#     try:
#         entry = sub_cutting_entry_table.objects.get(barcode=barcode)

#         # entry = sub_cutting_entry_table.objects.get(barcode=f"/cutting/barcode-detail/?barcode={barcode}")
#     except sub_cutting_entry_table.DoesNotExist:
#         return HttpResponse("Barcode not found", status=404)

#     context = {
#         'entry': entry,
#     }
#     return render(request, 'cutting_entry/barcode_print.html', context)

# from .utils import generate_barcode_base64  # or wherever you defined it

def cutting_barcode_detail(request):
    barcode = request.GET.get('barcode')
    if not barcode:
        return HttpResponse("No barcode provided", status=400)

    try: 
        entry = sub_cutting_entry_table.objects.get(barcode=barcode)
        barcode_image = generate_barcode_base64(entry.barcode)
        # quality = quality_table.objects.filter(status=1,entry.quality_id)
    except sub_cutting_entry_table.DoesNotExist:
        return HttpResponse("Barcode not found", status=404)

  
    context = {  
        'entry': entry,
        'barcode_image': barcode_image,
    }
    return render(request, 'cutting_entry/barcode_print.html', context)


def cutting_entry_edit(request):
    try:  
        encoded_id = request.GET.get('id') 
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'cutting_entry/update_cutting_entry.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'cutting_entry/update_cutting_entry.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
 
        # Fetch the material instance using 'tm_id'
        material_instance = sub_cutting_entry_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance 
            # For example, we assume `product_id` and other fields are provided in the request
            size_id = request.POST.get('size_id')  # Adjust as per your input structure
            color_id = request.POST.get('color_id')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            wt = request.POST.get('wt')  # Adjust as per your input structure
           
            # Ensure valid data before saving
            if size_id :
                material_instance = sub_cutting_entry_table.objects.create(
                    tm_id=material_id,
                    size_id=size_id, 
                    color_id=color_id,
                    quantity=quantity,
                    wt=wt,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'cutting_entry/update_cutting_entry.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = cutting_entry_table.objects.filter(id=material_id).first()
    
        # Fetch active products and UOM
        party = party_table.objects.filter(status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        cutting_program = cutting_program_table.objects.filter(status=1)

        # ✅ Lot-wise available quantity query
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    inward.lot_no,
                    inward.total_wt AS inw_wt,
                    COALESCE(inward.total_wt, 0) - COALESCE(cutting.total_cutting_wt, 0) AS available_wt
                FROM (
                    SELECT 
                        tx.lot_no, 
                        MAX(tm.total_wt) AS total_wt
                    FROM tx_dyed_fab_inward AS tx
                    LEFT JOIN tm_dyed_fab_inward AS tm ON tx.tm_id = tm.id
                    WHERE tx.status = 1
                    GROUP BY tx.lot_no
                ) AS inward
                LEFT JOIN (
                    SELECT 
                        lot_no, 
                        SUM(wt) AS total_cutting_wt
                    FROM tx_cutting_entry
                    WHERE status = 1
                    GROUP BY lot_no
                ) AS cutting ON inward.lot_no = cutting.lot_no
            """)
            lot_rows = cursor.fetchall()

        # ✅ Filter only lots with available weight > 0
        lot_no = [
            {'lot_no': row[0], 'total_wt': row[1], 'available_wt': row[2]}
            for row in lot_rows if row[2] > 0
        ]
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance, 
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            'size':size,
            'color':color,
            'quality':quality,
            'style':style,
            'lot_no':lot_no,
            'cutting_program':cutting_program
           
        }
        return render(request, 'cutting_entry/update_cutting_entry.html', context)

    except Exception as e:
        return render(request, 'cutting_entry/update_cutting_entry.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



# import qrcode
# import base64
# from io import BytesIO

# def generate_qr_base64(data):
#     """Generate a QR code and return it as a base64 image string."""
#     qr = qrcode.make(data)
#     buffer = BytesIO()
#     qr.save(buffer, format="PNG")
#     buffer.seek(0)
#     return base64.b64encode(buffer.getvalue()).decode()





import barcode 
from barcode.writer import ImageWriter
import base64
from io import BytesIO

def generate_barcode_base64(data):
    print('datas;',data)
    """Generate a Code128 barcode as base64 PNG."""
    try:
        code128 = barcode.get('code128', data, writer=ImageWriter())
        buffer = BytesIO()
        code128.write(buffer, options={"write_text": False})  # Don't print the text under barcode
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print("Barcode generation error:", e)
        return ''

import base64
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import os



import qrcode


def generate_qr_base64(data):
    """Generate a QR code and return it as a base64 string."""
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()




def tx_cutting_entry_list(request):
    tm_id = request.POST.get('id')

    # Fetch child data
    child_qs = sub_cutting_entry_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')

    if child_qs.exists():
        # Calculate total quantity and total weight from child table
        total_quantity = child_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_wt = child_qs.aggregate(Sum('wt'))['wt__sum'] or 0

        # Fetch master cutting entry
        parent_data = cutting_entry_table.objects.filter(id=tm_id).first()

        if not parent_data:
            return JsonResponse({'message': 'error', 'error_message': 'Cutting Entry not found in parent table'})

        # Convert child queryset to list
        child_data = list(child_qs.values())
      

        formatted_data = []

        for index, item in enumerate(child_data):
            size_name = getSupplier(size_table, item['size_id']) or ''
            color_name = getSupplier(color_table, item['color_id']) or ''
            quality_id = parent_data.quality_id or ''
            style_id = parent_data.style_id or ''

            quality_name = getSupplier(quality_table, quality_id) or ''
            style_name = getSupplier(style_table, style_id) or ''

            work_order_no = str(item["id"]).zfill(3)

            from datetime import datetime

            try:
                entry_month = parent_data.created_on.month  # or replace with actual field like cutting_date
            except AttributeError:
                entry_month = datetime.now().month

            month_str = str(entry_month).zfill(2)



            # month_str = str(parent_data.entry_date.month).zfill(2) if parent_data.entry_date else '07'

            # Build QR text like "202507/001/BOBBY/RN WHITE/36/RED/100"
            qr_text = f"2025{month_str}/{work_order_no}/{quality_name}/{style_name}/{size_name}/{color_name}/{item['quantity']}"

            # Generate base64 QR image
            qr_base64 = generate_qr_base64(qr_text)

            formatted_data.append({
                'action': f'<button type="button" onclick="cut_entry_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '
                        f'<button type="button" onclick="tx_cutting_entry_delete(\'{item["id"]}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>',
                'id': index + 1,
                'size': size_name,
                'color': color_name,
                'cutter': item['cutter'] if item['cutter'] else '-',
                'quantity': item['quantity'] if item['quantity'] else '-',
                'wt': item['wt'] if item['wt'] else '-',
                'qrcode': f'<img src="data:image/png;base64,{qr_base64}" width="80">',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            })


        print('b-dat:',formatted_data)


        # Prepare master values for summary
        summary_data = {  
            'total_quantity': total_quantity,
            'total_wt': total_wt, 
            'bundle_wt': parent_data.bundle_wt,
            'cutting_waste': parent_data.cutting_waste,
            'malai_waste': parent_data.malai_waste,
            'air_loss': parent_data.air_loss,
            'total_dozen': parent_data.total_dozen,
            'folding_waste': parent_data.folding_waste,
            'damages': parent_data.damages,
            'total_wt': parent_data.total_wt,
        }

        return JsonResponse({
            'data': formatted_data,
            **summary_data
        })

    else:
        return JsonResponse({'message': 'error', 'error_message': 'No cutting program data found for this TM ID'})




def edit_cutting_entry_detail(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = sub_cutting_entry_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  


from django.http import JsonResponse

def check_existing_cutting_entry(request):
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



def update_cutting_values(request):
    if request.method == 'POST':
        company_id = request.session.get('company_id') 

        party_id = request.POST.get('party_id',0) 
        print('party-id;',party_id)
        prg_id = request.POST.get('prg_id')
        fabric_id = request.POST.get('fab_id')
        print('fab-id:',fabric_id)
        remarks = request.POST.get('remarks') 
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        program_date = request.POST.get('inward_date')
        print('inw-date:',program_date) 
        cutting_data = json.loads(request.POST.get('cutting_data', '[]'))
        lot_no = request.POST.get('lot_no')
        print('lot:',lot_no)
        work_order_no = request.POST.get('work_order_no')
        
        
        master_id = request.POST.get('id')  # The ID of the row (if updating)
        tm_id = request.POST.get('tm_id')   # The transaction master ID
        size_id = request.POST.get('size_id')
        color_id = request.POST.get('color_id')
        quantity = request.POST.get('quantity')
        cutter = request.POST.get('cutter')
        wt = request.POST.get('wt') 
        fabric_id = request.POST.get('fabric_id')
        print('fabric-id',fabric_id,prg_id)  
        print('tm-id:', tm_id) 

        parent = cutting_entry_table.objects.filter(status=1,id=tm_id).update(
            company_id =company_id,
            inward_date=program_date,
            lot_no=lot_no,
            work_order_no=work_order_no, 
            cfyear=2025, 
        )
        print('parent-data;',parent)
 
        # Validate required fields
        if not tm_id or not size_id or not quantity:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Check if the same tm_id, size_id, and color_id already exist
            # existing_item = sub_cutting_entry_table.objects.filter( 
            #     tm_id=tm_id,
            #     status=1
            #     # size_id=size_id,
            #     # color_id=color_id
            # ).first()

            # if existing_item:
            #     # Update existing entry
            #     existing_item.quantity = quantity
            #     existing_item.wt = wt
            #     existing_item.cutter= cutter
            #     existing_item.save()
                
            #     updated_totals = update_values(tm_id)  # Update totals
            #     return JsonResponse({'success': True, 'updated': True, **updated_totals})

            # else:
                # Create a new row if no existing entry 
            child_item = sub_cutting_entry_table.objects.create(
                company_id = company_id, 
                tm_id=tm_id,
                color_id=color_id,  
                size_id=size_id,
                quantity=quantity,
                cutter=cutter,
                work_order_no = parent.work_order_no,
                wt=wt, 
                status=1,
                is_active=1

            )
            print('child-items:',child_item)
            updated_totals = update_values(tm_id)  # Update totals
            return JsonResponse({'success': True, 'created': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


def parse_decimal(value):
    try:
        return Decimal(str(value).strip() or '0')
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(0)

@csrf_exempt
def update_cutting_summary(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        cutting_waste = parse_decimal(request.POST.get('cutting_waste'))
        malai_waste = parse_decimal(request.POST.get('malai_waste'))
        folding_waste = parse_decimal(request.POST.get('folding_waste'))
        air_loss = parse_decimal(request.POST.get('air_loss'))
        damage = parse_decimal(request.POST.get('damage'))
        total = parse_decimal(request.POST.get('total_wt'))
        total_pcs = parse_decimal(request.POST.get('total_pcs'))
        total_bundles = parse_decimal(request.POST.get('total_bundles'))

        print('tm-id:', tm_id)

        # Validate required ID
        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid TM ID submitted'})

        try:
            parent = cutting_entry_table.objects.get(id=tm_id, status=1)

            parent.cutting_waste = cutting_waste
            parent.folding_waste = folding_waste
            parent.air_loss = air_loss
            parent.malai_waste = malai_waste
            parent.damages = damage
            parent.total_wt = total  
            parent.total_pcs = total_pcs 
            parent.total_bundles = total_bundles
            parent.status = 1
            parent.is_active = 1
            parent.save()

            return JsonResponse({'success': True, 'updated': True})

        except cutting_entry_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Record not found for given TM ID'})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})





# def update_summary_table(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('id')  # The ID of the row (if updating)
#         tm_id = request.POST.get('tm_id')   # The transaction master ID
#         cutting_waste = request.POST.get('cutting_waste')
#         malai_waste = request.POST.get('malai_waste')
#         folding_waste = request.POST.get('folding_waste')
#         air_loss = request.POST.get('air_loss')
#         damage = request.POST.get('damage')
#         total = request.POST.get('total_wt')

#         print('tm-id:', tm_id) 

#         # Validate required fields
#         if not tm_id :
#             return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

       
#         # Create a new row if no existing entry
#         parent = cutting_entry_table.objects.where(
#             tm_id=tm_id,status=1)
    
#         parent.cutting_waste=cutting_waste,
#         parent.folding_waste=folding_waste,
#         parent.air_loss=air_loss,
#         parent.malai_waste=malai_waste,
#         parent.damages=damage, 
#         parent.total_wt = total,
#         parent.status=1,
#         parent.is_active=1
#         parent.save()
        
#         # updated_totals = update_values(tm_id)  # Update totals
#         return JsonResponse({'success': True, 'created': True})

      
#     else:
#         return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


 

def update_values(tm):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given tm
        tx = sub_cutting_entry_table.objects.filter(tm_id=tm, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_wt = tx.aggregate(Sum('wt'))['wt__sum'] or Decimal('0')
        bundle_wt = tx.aggregate(Sum('wt'))['wt__sum'] or Decimal('0')

        # Update values in parent_po_table 
        cutting_entry_table.objects.filter(id=tm).update(
            # total_wt=total_wt,
            bundle_wt=bundle_wt, 
 
        )

        # Return updated values for frontend update
        return {
            'bundle_wt': bundle_wt,
            'total_wt': total_wt,
   
        }

    except Exception as e: 
        return {'error': str(e)}




def tx_cutting_entry_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting
            sub_cutting_entry_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_cutting_entry_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'}) 
    

 

def tm_cutting_entry_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            cutting_entry_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_cutting_entry_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except cutting_entry_table  & sub_cutting_entry_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})





def cutting_entry_tm_update(request):
    if request.method == 'POST':
        inward_date_str = request.POST.get('inward_date')
        tm_id = request.POST.get('tm_id')
        prg_id = request.POST.get('prg_id')
        lot_no = request.POST.get('lot_no') 
        

        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = cutting_entry_table.objects.get(id=tm_id)
         
            parent_item.tm_cutting_prg_id= prg_id
            parent_item.lot_no= lot_no

            if inward_date_str:
                inward_date = datetime.strptime(inward_date_str, '%Y-%m-%d').date()
                parent_item.inward_date = inward_date

            
            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except cutting_entry_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)}) 

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'}) 
