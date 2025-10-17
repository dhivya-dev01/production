from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
from company.models import *
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

from common.utils import *

from software_app.views import fabric_program, getItemNameById, getSupplier, is_ajax, knitting_program


# ```````````````````````````````````````````cutting program `````````````````````````````




def cutting_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        lot = (
            cutting_program_table.objects
            .filter(status=1)
            .values('work_order_no')  # Group by work_order_no
            .annotate(
                total_gross_wt=Sum('total_quantity'),
             
            )   
            .order_by('work_order_no')
        )
        return render(request,'cutting_program/cutting_program_list.html',{'party':party,'fabric_program':fabric_program,'lot':lot,'quality':quality,'style':style
                                                                           })
    else:
        return HttpResponseRedirect("/admin")
    


 
def cutting_prg_view(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    work_order_no = request.POST.get('work_no', '')
    quality = request.POST.get('quality', '')
    style = request.POST.get('style', '') 
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Match if either created_on or updated_on falls in range
            date_filter = Q(program_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })
    
    if work_order_no:
            query &= Q(work_order_no=work_order_no)

   
    if quality: 
            query &= Q(quality_id=quality)

    if style:
            query &= Q(style_id=style)



    # Apply filters
    queryset = cutting_program_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())
    # data = list(cutting_program_table.objects.filter(status=1).order_by('-id').values())
    print('dat:',data)
    formatted = [
        {
            'action': '<button type="button" onclick="cutting_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="cutting_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="cutting_prg__print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'cutting_no': item['cutting_no'] if item['cutting_no'] else'-', 
            'work_order_no': item['work_order_no'] if item['work_order_no'] else'-',  
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ),  
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 


from collections import defaultdict


@csrf_exempt
def cutting_program_print(request):
    po_id = request.GET.get('k') 
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('ord-id:',order_id)
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(cutting_program_table, id=order_id)

    prg_details = sub_cutting_program_table.objects.filter(tm_id=order_id).values(
        'id', 'quantity', 'quality_id', 'style_id','fabric_id', 'size_id','color_id'
    )
  
    combined_details = []
    total_quantity = 0

    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        color = get_object_or_404(color_table, id=prg_detail['color_id'])
        quality = get_object_or_404(quality_table, id=prg_detail['quality_id'])
        style = get_object_or_404(style_table, id=prg_detail['style_id'])
        # size = get_object_or_404(size_table, id=prg_detail['size_id']).order_by('sort_order_no')
        size = get_object_or_404(size_table, id=prg_detail['size_id'])
     
    
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
    # Step 1: Collect all unique size_ids from details
    unique_size_ids = set(prg_detail['size_id'] for prg_detail in prg_details)

    # Step 2: Fetch sizes sorted by sort_order_no
    sorted_sizes = size_table.objects.filter(id__in=unique_size_ids, status=1).order_by('sort_order_no')

    # Step 3: Extract names in sorted order
    sizes = [size.name for size in sorted_sizes]

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

    # for val in group_map.values():
    #     # Prebuild size_data_list to avoid dynamic dict access in template
    #     val['size_data_list'] = [
    #         val['size_data'].get(size, {'quantity': ''}) for size in sizes
    #     ]
    #     grouped_data.append(val)


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

    return render(request, 'cutting_program/cutting_prg_print.html', context)



from django.http import JsonResponse
from django.db.models import Sum

def tx_cutting_program_list(request):
    tm_id = request.POST.get('tm_id')

    # Fetch child data
    child_qs = sub_cutting_program_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')
    
    if child_qs.exists():
        # Calculate total quantity from child table
        total_quantity = child_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Fetch tax total from the parent table 
        parent_data = cutting_program_table.objects.filter(id=tm_id).first()
        total_quantity = parent_data.total_quantity if parent_data else 0

        # Convert queryset to list 
        child_data = list(child_qs.values())

        # Format response data
        formatted_data = [
            {
                'action': '<button type="button" onclick="cut_prg_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                           <button type="button" onclick="tx_cutting_prg_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
                'table_id': index + 1,
                'id': item['id'],
                'tm_id': item['tm_id'],
                'size_name': getSupplier(size_table, item['size_id']),
                'color_name': getSupplier(color_table, item['color_id']),
                'quantity': item['quantity'] if item['quantity'] else '-',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            }
            for index, item in enumerate(child_data)
        ]

        return JsonResponse({'data': formatted_data, 'total_quantity': total_quantity, 'total_quantity': total_quantity})

    else:
        return JsonResponse({'error': 'No cutting program data found for this TM ID'})




def generate_cut_prg_num_series():
    last_purchase = cutting_program_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.cutting_no:
        match = re.search(r'CP-(\d+)', last_purchase.cutting_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"CP-{next_num:03d}"



def generate_cut_prg_order_num_series():
    last_purchase = cutting_program_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.cutting_no:
        match = re.search(r'CP-(\d+)', last_purchase.cutting_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"CP-{next_num:03d}"




def add_cutting_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_cutting=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 

        prg_number = generate_cut_prg_num_series
 
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        return render(request,'cutting_program/add_cutting_program.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number,'color':color
                                                                  ,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
    


@csrf_exempt  # Use only if necessary
def get_quality_style_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')

        if not quality_id:
            return JsonResponse({'error': 'Quality ID is required'}, status=400)

        try:
            # Retrieve all fabric programs for the given quality_id
            fabric_programs = quality_program_table.objects.filter(quality_id=quality_id)
            if not fabric_programs.exists():
                return JsonResponse({'error': 'No matching records found'}, status=404)
 
            # Collect all styles linked to the fabric programs
           

            style_ids = fabric_programs.values_list('style_id', flat=True).distinct()
            styles = style_table.objects.filter(id__in=style_ids).values('id', 'name')
 
 
            
            # Get all quality_program_table IDs to use as tm_id
            program_ids = fabric_programs.values_list('id', flat=True)

            # Fetch all sizes and colors linked to these program IDs
            sub_programs = sub_quality_program_table.objects.filter(tm_id__in=program_ids).values('size_id').distinct()
            sizes = size_table.objects.filter(id__in=sub_programs).values('id', 'name')

            response_data = {
                'style': list(styles),
                'size': list(sizes),

                # 'sizes_colors': list(sub_programs)  # List of {size_id, color_id}
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def get_quality_fabric_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')

        if not quality_id:
            return JsonResponse({'error': 'Quality ID is required'}, status=400)

        try:
            # Get fabric programs for the given quality
            fabric_programs = quality_program_table.objects.filter(quality_id=quality_id)
            fabric_ids_qs = fabric_programs.values_list('fabric_id', flat=True).distinct()

            # Convert QuerySet to comma-separated string
            fabric_id_string = ",".join(str(f_id) for f_id in fabric_ids_qs if f_id is not None)

            # Split string and convert to int list (excluding 'None', empty, etc.)
            fabric_id_list = [int(fid) for fid in fabric_id_string.split(',') if fid.isdigit()]

            # Now fetch fabric names using fabric_id_list
            fabrics = fabric_program_table.objects.filter(id__in=fabric_id_list).values('id', 'name')

            return JsonResponse({
                'fabric': list(fabrics),
                'fabric_ids': fabric_id_string 
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
 
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# @csrf_exempt  # Use only if necessary
# def get_quality_fabric_list(request):
#     if request.method == 'POST':
#         quality_id = request.POST.get('quality_id')

#         if not quality_id:
#             return JsonResponse({'error': 'Quality ID is required'}, status=400)

#         try:
#             # Retrieve all fabric programs for the given quality_id
#             fabric_programs = quality_program_table.objects.filter(quality_id=quality_id)

#             if not fabric_programs.exists():
#                 return JsonResponse({'error': 'No matching records found'}, status=404)

#             # Collect all styles linked to the fabric programs
#             fabric_ids = fabric_programs.values_list('fabric_id', flat=True).distinct()
#             fabrics = fabric_program_table.objects.filter(id__in=fabric_ids).values('id', 'name')

#             # Get all quality_program_table IDs to use as tm_id

#             response_data = {
#                 'fabric': list(fabrics),

#                 # 'sizes_colors': list(sub_programs)  # List of {size_id, color_id}
#             }

#             return JsonResponse(response_data)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def save_cutting_program(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id') 

        try:
            # Extracting Data from Request  
            work_order_num = request.POST.get('work_ord_no',0) 
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            fabric_id = request.POST.get('fabric_id')
            program_date = request.POST.get('program_date')
            cutting_data = json.loads(request.POST.get('cutting_data', '[]'))

            print('Chemical Data:', cutting_data)

            def clean_amount(amount):
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()

            # Create Parent Entry (gf_inward_table)
            prg_no = generate_cut_prg_num_series()
            material_request = cutting_program_table.objects.create(
                cutting_no = prg_no,
                program_date=program_date, 
                work_order_no=work_order_num,
                quality_id=quality_id,
                style_id=style_id,
                fabric_id = fabric_id,
                company_id=company_id,
                cfyear = 2025,
                total_quantity=0,
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )

            po_ids = set()  # Store unique PO IDs to update later

            total_quantity = 0
            # Create    Sub Table Entries
            for cutting in cutting_data:
                print("Processing cutting Data:", cutting)
 
                po_id = cutting.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later
                quantity = Decimal(cutting.get('quantity', '0') or '0')

                sub_entry = sub_cutting_program_table.objects.create(
                    tm_id=material_request.id,  
                    quality_id = quality_id,
                    style_id=style_id,
                    size_id=cutting.get('size_id'), 
                    color_id=cutting.get('color_id'), 
                    fabric_id=fabric_id,
                    quantity=cutting.get('quantity'),
                    created_by=user_id, 
                    company_id= company_id,
                    cfyear=2025,
                    created_on=timezone.now()
                )
                total_quantity += quantity

                material_request.total_quantity = total_quantity
                material_request.save()
                print("Sub Table Entry Created:", sub_entry) 
 
           
            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'cutting_program/add_cutting_program.html')




def cutting_program_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'cutting_program/update_cutting_program.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'cutting_program/update_cutting_program.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'

    #     material_instance = list(sub_cutting_program_table.values(
    #     'tm_id', 'size_id', 'color_id', 'quantity'
    # ))
        material_instance = sub_cutting_program_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            size_id = request.POST.get('size_id')  # Adjust as per your input structure
            color_id = request.POST.get('color_id')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
           
            # Ensure valid data before saving
            if size_id :
                material_instance = sub_cutting_program_table.objects.create(
                    tm_id=material_id,
                    size_id=size_id, 
                    color_id=color_id,
                    quantity=quantity,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'cutting_program/update_cutting_program.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = cutting_program_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'cutting_program/update_cutting_program.html', {'error_message': 'Parent stock not found.'})

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
        party = party_table.objects.filter(is_cutting=1,status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
     

       
        # Render the edit page with the material instance and supplier name
        context = {
            'material_instance': material_instance,
            # 'material_instance': json.dumps(material_instance),  # ✅ serialize to JSON

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
        return render(request, 'cutting_program/update_cutting_program.html', context)

    except Exception as e:
        return render(request, 'cutting_program/update_cutting_program.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



def get_material_instance(request):
    tm_id = request.GET.get('tm_id')
    print('material-id',tm_id)

    if not tm_id:
        return JsonResponse({'error': 'Missing tm_id'}, status=400)

    data = list(sub_cutting_program_table.objects.filter(tm_id=tm_id).values(
        'tm_id', 'size_id', 'color_id', 'quantity'
    ))

    return JsonResponse({'material_instance': data})



def edit_cutting_prg_detail(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = sub_cutting_program_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  



def cutting_program_update(request):
    if request.method == 'POST': 
        master_id = request.POST.get('tm_id')
        work_ord_no = request.POST.get('work_ord_no')
        program_date = request.POST.get('program_date')
        remarks = request.POST.get('remarks')
      
 
        if not master_id or not work_ord_no:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = cutting_program_table.objects.get(id=master_id)
            parent_item.work_order_no = work_ord_no
            parent_item.program_date = program_date
            parent_item.remarks = remarks
     
            parent_item.save()

            return JsonResponse({'success': True, 'message': 'PO item updated successfully'})

        except cutting_program_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Parent PO not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




from django.http import JsonResponse


# def add_or_update_cutting_program(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('id')  # The ID of the row (if updating)
#         tm_id = request.POST.get('tm_id')     # The transaction master ID
#         size_id = request.POST.get('size_id')
#         color_id = request.POST.get('color_id')
#         quantity = request.POST.get('quantity')

#         print('tm-id:', tm_id)

#         # Validate required fields
#         if not tm_id or not size_id or not quantity:
#             return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

#         try:
#             # First, check if a record with the same tm_id, size_id, and color_id exists
#             existing_item = sub_cutting_program_table.objects.filter(
#                 tm_id=tm_id,
#                 size_id=size_id,
#                 color_id=color_id
#             ).exclude(id=master_id if master_id and master_id != "0" else None).first()

#             if existing_item:
#                 # Instead of returning an error, update the quantity
#                 existing_item.quantity = quantity
#                 existing_item.status = 1
#                 existing_item.is_active = 1
#                 existing_item.save()
#                 created = False
#             else:
#                 if master_id and master_id != "0":
#                     # Update existing row if master_id is provided
#                     child_item = sub_cutting_program_table.objects.filter(id=master_id, tm_id=tm_id).first()
#                     if child_item:
#                         child_item.color_id = color_id
#                         child_item.size_id = size_id
#                         child_item.quantity = quantity
#                         child_item.status = 1
#                         child_item.is_active = 1
#                         child_item.save()
#                         created = False
#                     else:
#                         created = True
#                 else:
#                     # Create a new row if master_id is not provided
#                     child_item = sub_cutting_program_table.objects.create(
#                         tm_id=tm_id,
#                         color_id=color_id,
#                         size_id=size_id,
#                         quantity=quantity,
#                         status=1,
#                         is_active=1
#                     )
#                     created = True

#             # Update totals after adding/updating
#             updated_totals = update_values(tm_id)

#             return JsonResponse({'success': True, 'created': created, **updated_totals})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})
#     else:
#         return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


# def update_cutting_program(request):
#     if request.method == 'POST': 
#         user_id = request.session.get('user_id')   
#         company_id = request.session.get('company_id')

#         try:
#             # Step 1: Collect data from request
#             program_date = request.POST.get('program_date')
#             work_order_no = request.POST.get('work_ord_no')
#             tm_id = request.POST.get('tm_id')
#             fabric_id = request.POST.get('fabric_id')
#             quality_id = request.POST.get('quality_id')
#             style_id = request.POST.get('style_id')
#             remarks = request.POST.get('remarks')
#             chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

#             # Step 2: Parse date safely
#             if program_date:
#                 try:
#                     program_date = datetime.fromisoformat(program_date).date()
#                 except ValueError:
#                     return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

#             # Step 3: Fetch or create parent
#             if tm_id:
#                 parent = get_object_or_404(cutting_program_table, id=tm_id)
#                 new_do_number = parent.cutting_no  # Reuse existing


#                  # Step 4: Update parent fields
#                 parent.program_date = program_date
#                 parent.work_order_no = work_order_no
#                 parent.quality_id = quality_id
#                 parent.style_id = style_id
#                 parent.fabric_id = fabric_id
#                 parent.remarks = remarks
#                 parent.total_quantity = 0  # Will be updated below
#                 parent.created_by = user_id
#                 parent.created_on = timezone.now()
#                 parent.save()
#                 # Delete previous children
#                 sub_cutting_program_table.objects.filter(tm_id=tm_id).delete()
            
               

#             # Step 5: Insert child records and calculate total
#             total_quantity = Decimal('0.00')

#             for cutting in chemical_data:
#                 qty = Decimal(cutting.get('quantity', '0'))

#                 sub_cutting_program_table.objects.create(
#                     tm_id=parent.id,
#                     quality_id=quality_id,
#                     style_id=style_id,
#                     size_id=cutting.get('size_id'),
#                     color_id=cutting.get('color_id'),
#                     quantity=qty,
#                     created_by=user_id,
#                     company_id=company_id,
#                     cfyear=2025,
#                     created_on=timezone.now()
#                 )

#                 total_quantity += qty

#             # Step 6: Update total
#             parent.total_quantity = total_quantity
#             parent.save()

#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Program data saved successfully.',
#                 'prg_number': new_do_number
#             })

#         except Exception as e:
#             print(f"❌ Error in update_cutting_program: {e}")
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return render(request, 'cutting_program/update_cutting_program.html')




from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
import json

from .models import cutting_program_table, sub_cutting_program_table

def update_cutting_program(request):
    if request.method == 'POST': 
        user_id = request.session.get('user_id')   
        company_id = request.session.get('company_id')

        try:
            # Step 1: Collect data from POST
            program_date = request.POST.get('program_date')
            work_order_no = request.POST.get('work_ord_no')
            tm_id = request.POST.get('tm_id')
            fabric_id = request.POST.get('fabric_id')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            remarks = request.POST.get('remarks')
            chemical_data = json.loads(request.POST.get('cutting_data', '[]'))

            # Step 2: Parse program_date safely
            if program_date:
                try:
                    program_date = datetime.fromisoformat(program_date).date()
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

            # Step 3: Load parent record (update only)
            if not tm_id:
                return JsonResponse({'status': 'error', 'message': 'Missing transaction ID for update'})

            parent = get_object_or_404(cutting_program_table, id=tm_id)
            new_do_number = parent.cutting_no  # Reuse existing number

            # Step 4: Update parent fields
            parent.program_date = program_date
            parent.work_order_no = work_order_no
            parent.quality_id = quality_id
            parent.style_id = style_id
            parent.fabric_id = fabric_id
            parent.remarks = remarks
            parent.total_quantity = 0  # Reset total
            parent.created_by = user_id
            parent.created_on = timezone.now()
            parent.save()

            # Step 5: Clear existing child records
            sub_cutting_program_table.objects.filter(tm_id=tm_id).delete()

            # Step 6: Insert new child records
            total_quantity = Decimal('0.00')
            for cutting in chemical_data:
                quantity = Decimal(cutting.get('quantity', '0') or '0')

                sub_cutting_program_table.objects.create(
                    tm_id=parent.id,
                    quality_id=quality_id, 
                    style_id=style_id,
                    size_id=cutting.get('size_id'),
                    color_id=cutting.get('color_id'),
                    quantity=quantity,
                    fabric_id=fabric_id,
                    created_by=user_id,
                    company_id=company_id,
                    cfyear=2025,
                    created_on=timezone.now()
                )

                total_quantity += quantity

            # Step 7: Update total quantity in parent
            parent.total_quantity = total_quantity
            parent.save()
            print('parent:',parent)
            return JsonResponse({
                'status': 'success',
                'message': 'Program data updated successfully.',
                'prg_number': new_do_number
            })

        except Exception as e:
            print(f"❌ Error in update_cutting_program: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    # For GET or invalid method
    return render(request, 'cutting_program/update_cutting_program.html')




def add_or_update_cutting_program_bk14(request):
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
            existing_item = sub_cutting_program_table.objects.filter(
                tm_id=tm_id,
                size_id=size_id,
                color_id=color_id
            ).exclude(id=master_id if master_id and master_id != "0" else None).first()

            if existing_item:
                return JsonResponse({'success': False, 'error_message': 'This size and color already exist for the selected TM ID.'})

            if master_id and master_id != "0":
                # Update existing row
                child_item = sub_cutting_program_table.objects.filter(id=master_id, tm_id=tm_id).first()
                if child_item:
                    child_item.color_id = color_id
                    child_item.size_id = size_id
                    child_item.quantity = quantity
                    child_item.status = 1
                    child_item.is_active = 1
                    child_item.save()
                    created = False
                else:
                    created = True
            else:
                # Create a new row if master_id is not provided
                child_item = sub_cutting_program_table.objects.create(
                    tm_id=tm_id,
                    color_id=color_id,
                    size_id=size_id,
                    quantity=quantity,
                    status=1,
                    is_active=1
                )
                created = True

            # Update totals after adding/updating
            updated_totals = update_values(tm_id)

            return JsonResponse({'success': True, 'created': created, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

from django.http import JsonResponse



# def check_existing_cutting_program(request):
#     if request.method == 'POST':
#         tm_id = request.POST.get('tm_id')
#         size_id = request.POST.get('size_id')
#         color_id = request.POST.get('color_id')

#         # Check if a record with the same tm_id, size_id, and color_id exists
#         exists = sub_cutting_program_table.objects.filter(
#             tm_id=tm_id, size_id=size_id, color_id=color_id
#         ).exists()

#         return JsonResponse({'exists': exists})
#     else:
#         return JsonResponse({'success': False, 'error_message': 'Invalid request method'})



def check_existing_cutting_program(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        size_id = request.POST.get('size_id')
        color_id = request.POST.get('color_id')

        existing_item = sub_cutting_program_table.objects.filter(
            tm_id=tm_id, size_id=size_id, color_id=color_id
        ).first()

        if existing_item:
            return JsonResponse({'exists': True, 'id': existing_item.id})
        else:
            return JsonResponse({'exists': False})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_values(tm):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given tm
        tx = sub_cutting_program_table.objects.filter(tm_id=tm, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')

        # Update values in parent_po_table
        cutting_program_table.objects.filter(id=tm).update(
            total_quantity=total_quantity,
 
        )

        # Return updated values for frontend update
        return {
            'total_quantity': total_quantity,
   
        }

    except Exception as e: 
        return {'error': str(e)}



def tx_cutting_prg_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_cutting_program_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_cutting_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'}) 
    



def tm_cutting_prg_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            cutting_program_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_cutting_program_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except cutting_program_table  & sub_cutting_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})

