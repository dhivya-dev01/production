# from cairo import Status
from django.shortcuts import render

from django.utils.text import slugify


from accessory.models import *
from colored_fabric.models import dyed_fabric_inward_table
from company.models import *
from employee.models import *

from grey_fabric.models import *


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


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 





def check_user_access(user_type, module_name, action_type):
    print('test-access:',user_type, module_name)
    try:
        # Check if the module exists and is active
        module = AdminModules.objects.get(name=module_name, is_active=1)
        print(f"Module found: {module}")
    except AdminModules.DoesNotExist:
        print(f"Module '{module_name}' not found or inactive")
        return False, "Module not found"

    try:
        # Get the user based on the user type (role)
        user = AdminRoles.objects.filter(name=user_type, is_active=1).first()
        if not user:
            print(f"User type '{user_type}' not found or inactive")
            return False, "User not found" 
        user_id = user.id 
        print(f"User found: {user}, ID: {user_id}")
    except AdminRoles.DoesNotExist:
        print(f"User type '{user_type}' does not exist")
        return False, "User not found"

    try: 
        # Check if the user has the privilege for the specified module
        privilege = AdminPrivilege.objects.get(
            role_id=user_id, 
            module=module.id,
            is_active=1,
            status=1
        )
        print(f"Privilege found: {privilege}")
    except AdminPrivilege.DoesNotExist:
        print(f"No privilege found for User ID {user_id} and Module ID {module.id}")
        return False, "Access denied"

    # Check based on the action type requested
    if action_type == 'create' and not privilege.is_create:
        print(f"User ID {user_id} does not have create access for Module ID {module.id}")
        return False, "Access denied for create"
    
    elif action_type == 'read' and not privilege.is_read:
        print(f"User ID {user_id} does not have read access for Module ID {module.id}")
        return False, "Access denied for read"
    
    elif action_type == 'update' and not privilege.is_update:
        print(f"User ID {user_id} does not have update access for Module ID {module.id}")
        return False, "Access denied for update"
    
    elif action_type == 'delete' and not privilege.is_delete:
        print(f"User ID {user_id} does not have delete access for Module ID {module.id}")
        return False, "Access denied for delete"

    return True, ""

# Create your views here.


# ````````````````````` knitting program ```````````````````````````````````




import re

def generate_next_knit_number():
    last_purchase = knitting_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.knitting_number:
        match = re.search(r'KN-(\d+)', last_purchase.knitting_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"KN-{next_num:03d}"




def knitting_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1,is_knitting=1)
        product = fabric_program_table.objects.filter(status=1)
        purchase = parent_po_table.objects.filter(status=1) 
     
        delivery_number = generate_next_knit_number

        gauge = gauge_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        # fabric_program = fabric_program_table.objects.filter(status=1)
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
        return render(request,'knitting/knitting.html',{'purchase':purchase,'supplier':supplier,'fabric_programs': fabric_program_with_name,
                                                        'party':party,'product':product,'delivery_number':delivery_number,'gauge':gauge,'count':count,'tex':tex})
    else:
        return HttpResponseRedirect("/signin")


  
from django.http import JsonResponse
from datetime import datetime
import json
from decimal import Decimal




# Function to generate knitting number series with a prefix (e.g., PO)
def generate_knit_num_series(model, field_name='knitting_number', padding=4, prefix='KN'):  
    # Get the maximum knitting number, and remove the prefix part to get the number
    # max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']
    max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']

    try:
        # Extract the number part and increment
        if max_value:
            # Extract the number from the field and increment
            current_number = int(max_value.replace(prefix, '')) if max_value else 0
        else:
            current_number = 0
    except ValueError:
        current_number = 0

    # Generate the next knitting number with prefix and padding
    return f"{prefix}{str(current_number + 1).zfill(padding)}"

@csrf_exempt
def add_knitting(request): 
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try: 
            # Extract data from request
            prg_date = request.POST.get('program_date')
            supplier_id = request.POST.get('supplier_id') 
            lot_no = request.POST.get('lot_no')
            name = request.POST.get('name')
            po_id = request.POST.get('po_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            print('sub-table-yarn-deliver:', chemical_data) 

            # Generate knitting number
            knitting_no = generate_next_knit_number()

            # Validate material type (must be either 'yarn' or 'grey')
            material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
            is_yarn = 1 if material_type == 'yarn' else 0
            is_gry_fabric = 1 if material_type == 'grey' else 0

            # Ensure only one of them is set to 1
            if is_yarn + is_gry_fabric != 1:
                return JsonResponse({'status': 'error', 'message': 'Select either Yarn or Grey Fabric !.'}, safe=False)

            # Create knitting_table entry (Parent)
            material_request = knitting_table.objects.create(
                knitting_number=knitting_no,   
                name=name,
                is_yarn=is_yarn,
                is_grey_fabric=is_gry_fabric,
                program_date=prg_date,
                company_id=company_id,
                total_quantity=0,  # Initially set to 0
                created_by=user_id, 
                created_on=datetime.now()
            ) 

            total_quantity = 0

            # Process child entries in sub_knitting_table
            for chemical in chemical_data:
                if chemical and chemical.get('product_id') and chemical.get('quantity') not in [None, 'undefined']:
                    try:
                        quantity = int(float(chemical.get('quantity', 0)))

                        sub_knitting_table.objects.create(
                            tm_id=material_request.id,
                            fabric_id=chemical.get('product_id'),
                            count_id=chemical.get('count_id'),
                            gauge=chemical.get('gauge_id'),
                            tex=chemical.get('tex_id'), 
                            dia=chemical.get('dia_id'),
                            gsm=chemical.get('gsm'), 
                            rolls=chemical.get('rolls'),
                            wt_per_roll=chemical.get('wt_per_roll'),
                            quantity=quantity,
                            created_by=user_id,
                            created_on=datetime.now()
                        )

                        total_quantity += quantity

                    except ValueError as ve:
                        print(f"Invalid data for product {chemical.get('product_id')}: {ve}")
                else:
                    print("Invalid entry found:", chemical)

            # Update total_quantity
            material_request.total_quantity = total_quantity
            material_request.save()

            return JsonResponse({'status': 'success', 'message': 'Knitting program added successfully.'}, safe=False)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, safe=False)

    return render(request, 'knitting/knitting.html')



@csrf_exempt
def add_knitting_24(request): 
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')
  
        try: 
            # Extracting data from request
            prg_date = request.POST.get('program_date')
            supplier_id = request.POST.get('supplier_id') 
            lot_no = request.POST.get('lot_no')
            name = request.POST.get('name')
            po_id = request.POST.get('po_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            print('sub-table-yarn-deliver:', chemical_data) 

            # Generate knitting number
            knitting_no = generate_next_knit_number()
            # generate_knit_num_series(knitting_table, 'knitting_number', padding=4, prefix='KN')
            material_type = request.POST.get('material_type')  # either 'yarn' or 'grey'
            is_yarn = 1 if material_type == 'yarn' else 0
            is_gry_fabric = 1 if material_type == 'grey' else 0

            # Create knitting_table entry (Parent)
            material_request = knitting_table.objects.create(
                knitting_number=knitting_no,   
                name=name,
                is_yarn=is_yarn,
                is_grey_fabric=is_gry_fabric,
                program_date=prg_date,
                company_id=company_id,
                total_quantity= 0,  # Initially set to 0
                created_by=user_id, 
                created_on=datetime.now()
            ) 

            total_quantity = 0  # <-- initialize total quantity accumulator

            # Process child entries in sub_knitting_table
            for chemical in chemical_data:
                if chemical and chemical.get('product_id') and chemical.get('quantity') not in [None, 'undefined']:
                    try:
                        quantity = int(float(chemical.get('quantity', 0)))  # Ensure proper conversion

                        sub_knitting_table.objects.create(
                            tm_id=material_request.id,  # ForeignKey to knitting_table
                            fabric_id=chemical.get('product_id'),
                            count_id=chemical.get('count_id'),
                            gauge=chemical.get('gauge_id'),
                            tex=chemical.get('tex_id'), 
                            dia=chemical.get('dia_id'),
                            gsm=chemical.get('gsm'), 
                            rolls=chemical.get('rolls'),
                            wt_per_roll=chemical.get('wt_per_roll'),
                            quantity=quantity,
                            created_by=user_id,
                            created_on=datetime.now()
                        )

                        # ✅ Update total_quantity after processing each child entry
                        total_quantity += quantity  # Add quantity of current item 

                    except ValueError as ve:
                        print(f"Invalid data for product {chemical.get('product_id')}: {ve}")
                else:
                    print("Invalid entry found:", chemical)

            # After processing all child entries, update total_quantity in the parent table
            material_request.total_quantity = total_quantity
            material_request.save()

            return JsonResponse({'status': 'success', 'message': 'Knitting program added successfully.'}, safe=False)

        except Exception as e:
            print(f"Error: {e}")  # Debugging
            return JsonResponse({'status': 'error', 'message': str(e)}, safe=False)

    return render(request, 'knitting/knitting.html')



def knitting_program_edit(request):
    try:
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'knitting/update_knitting_program.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decode-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'knitting/update_knitting_program.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_knitting_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            fabric_id = request.POST.get('fabric_id')  # Adjust as per your input structure
            count = request.POST.get('count')  # Adjust as per your input structure
            gauge = request.POST.get('gauge')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            tex = request.POST.get('tex')  # Adjust as per your input structure
            rolls = request.POST.get('rolls')  # Adjust as per your input structure
            dia = request.POST.get('dia')  # Adjust as per your input structure
            wt_per_roll = request.POST.get('wt_per_roll')  # Adjust as per your input structure
            gsm = request.POST.get('gsm')  # Adjust as per your input structure

            # Ensure valid data before saving
            if fabric_id and quantity:
                material_instance = sub_knitting_table.objects.create(
                    tm_id=material_id,
                    count_id=count,
                    gauge=gauge,
                    gsm=gsm,
                    rolls=rolls,
                    tex=tex,
                    dia=dia,
                    wt_per_role=wt_per_roll,
                    quantity=quantity,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'knitting/update_knitting_program.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = knitting_table.objects.filter(id=material_id).first()
   
        # Fetch active products and UOM
        # product = fabric_program_table.objects.filter(status=1)

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
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_knitting=1,status=1)

        count=count_table.objects.filter(status=1)
        gauge=gauge_table.objects.filter(status=1) 
        tex=tex_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'product': fabric_program_with_name,
            'party': party, 
            # 'supplier_id': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'count':count,
            'gauge':gauge,
            'tex':tex,
        }
        print('date-value:',parent_stock_instance.program_date)
        return render(request, 'knitting/update_knitting_program.html', context)
 
    except Exception as e:
        return render(request, 'knitting/update_knitting_program.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


from django.db.models import Sum

def tx_knitting_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data
                child_data = sub_knitting_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = knitting_table.objects.filter(id=master_id).first()
                    if parent_data:
                        total_tax = Decimal(parent_data.total_tax or 0)
                        try:
                            round_off = Decimal(parent_data.round_off) if parent_data.round_off else Decimal(0)
                        except (ValueError, TypeError):
                            round_off = Decimal(0)
                        grand_total = Decimal(total_amount) + total_tax + round_off
                    else:
                        total_tax = round_off = grand_total = Decimal(0)

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
                            'count': getCountNameById(count_table, item['count_id']),
                            'gauge': getItemNameById(gauge_table, item['gauge']),
                            'tex': getItemNameById(tex_table, item['tex']),
                            'dia': getItemNameById(dia_table, item['dia']),
                            # 'dia': item['dia'] or '-',
                            'rolls': item['rolls'] or '-',
                            'wt_per_roll': item['wt_per_roll'] or '-',
                            'rate': item['rate'] or '-',
                            'quantity': item['quantity'] or '-',
                            'total_amount': item['total_amount'] or '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': float(total_quantity),  # Convert to float for JSON compatibility
                        'total_amount': float(total_amount),
                        'total_tax': float(total_tax),
                        'round_off': float(round_off),
                        'grand_total': float(grand_total),
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})


 
def tm_knitting_details_update(request):
    if request.method == 'POST':
        name = request.POST.get('prg_name')
        print('names:',name)
        tm_id = request.POST.get('tm_id')
        program_date_str = request.POST.get('program_date')
        # material_type = request.POST.get('material_type')  # 'yarn' or 'grey'
        # print('material-type:',material_type)

        # is_yarn = 1 if material_type == 'yarn' else 0
        # is_grey_fabric = 1 if material_type == 'grey' else 0



        material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
        is_yarn = 1 if material_type == 'yarn' else 0
        is_gry_fabric = 1 if material_type == 'grey' else 0

        # Ensure only one of them is set to 1
        if is_yarn + is_gry_fabric != 1:
            return JsonResponse({'status': 'error', 'message': 'Select either Yarn or Grey Fabric !.'}, safe=False)



        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = knitting_table.objects.get(id=tm_id)
            parent_item.name = name
            parent_item.is_yarn = is_yarn
            parent_item.is_grey_fabric = is_gry_fabric

            if program_date_str:
                program_date = datetime.strptime(program_date_str, '%Y-%m-%d').date()
                parent_item.program_date = program_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except knitting_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


 

def knitting_program_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            knitting_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_knitting_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except knitting_table  & sub_knitting_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})

 

# #tx table



def delete_knitting_program(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_knitting_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_knitting_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




def getCountNameById(tbl,count):
    try:
        count = tbl.objects.get(id=count).name
    except ObjectDoesNotExist:
        count = '-'
    return count

def tx_knitting_detail_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST 
    data = sub_knitting_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0]) 




from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from django.http import JsonResponse

def update_knitting(master_id):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = sub_knitting_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
        total_amount = tx.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')

        # Convert tax rate to Decimal and perform multiplication safely
        tax_rate = Decimal('0.05')  # 5% tax
        total_tax = (total_amount * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Ensure 2 decimal places

        # Calculate raw total before rounding 
        raw_total = total_amount + total_tax

        # Compute round_off and grand_total
        rounded_total = Decimal(round(raw_total))  # Ensure Decimal type
        round_off = (rounded_total - raw_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Ensure 2 decimal places

        # Format round_off with a + or - sign
        round_off_str = f"+{round_off}" if round_off > 0 else f"{round_off}"

        grand_total = rounded_total  # Final rounded total

        # Update values in parent_po_table
        knitting_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            total_amount=total_amount.quantize(Decimal('0.01')),
            total_tax=total_tax,
            round_off=round_off_str,  # Store as string with sign
            grand_total=grand_total
        )

        # Return updated values for frontend update
        return {
            'total_quantity': total_quantity,
            'total_amount': total_amount.quantize(Decimal('0.01')),
            'total_tax': total_tax,
            'round_off': round_off_str,  # Send formatted round_off
            'grand_total': grand_total
        }

    except Exception as e:
        return {'error': str(e)}


# def update_knitting_program(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('parent_id')  # Parent Table ID
#         po_id = request.POST.get('po_id')
#         product_id = request.POST.get('fabric_id')
#         count = request.POST.get('count')
#         gauge = request.POST.get('gauge')
#         tex = request.POST.get('tex')
#         dia = request.POST.get('dia')
#         gsm = request.POST.get('gsm')
#         rolls = request.POST.get('rolls')
#         wt_per_roll = request.POST.get('wt_per_roll')
#         quantity = request.POST.get('quantity')
#         rate = request.POST.get('rate')
#         amount = request.POST.get('total_amount')
#         edit_id = request.POST.get('edit_id')  # This determines if it's an update or new entry

#         # Ensure required fields are provided
#         if not product_id or not po_id:
#             return JsonResponse({'success': False, 'error_message': 'Missing required data'})

#         try:
#             if edit_id:  # Update existing record
#                 child_item = sub_knitting_table.objects.get(id=edit_id)
#                 child_item.fabric_id = product_id
#                 child_item.count_id = count
#                 child_item.gauge = gauge
#                 child_item.tex = tex
#                 child_item.dia = dia
#                 # child_item.tm_po_id = po_id
#                 child_item.gsm = gsm
#                 child_item.rolls = rolls
#                 child_item.wt_per_roll = wt_per_roll
#                 child_item.quantity = quantity
#                 child_item.rate = rate
#                 child_item.total_amount = amount
#                 child_item.save()
#                 message = "Knitting program updated successfully."
         

#             else:
#                 # Check for existing entry with same tm_id, fabric, and dia
#                 existing = sub_knitting_table.objects.filter(
#                     tm_id=master_id,
#                     fabric_id=product_id,
#                     dia=dia,
#                     status=1,
#                     is_active=1
#                 ).first()

#                 if existing:
#                     # Sum rolls, quantity and amount
#                     existing.rolls = int(existing.rolls) + int(rolls)
#                     existing.quantity = float(existing.quantity) + float(quantity)
#                     existing.total_amount = float(existing.total_amount) + float(amount)
#                     existing.wt_per_roll = wt_per_roll  # Optionally update this if needed
#                     existing.rate = rate  # Optionally update this if needed
#                     existing.save()
#                     message = "Existing entry updated with new roll data."
#                 else:
#                     # Create new record if no match found
#                     sub_knitting_table.objects.create(
#                         fabric_id=product_id,
#                         tm_id=master_id,
#                         count_id=count,
#                         gauge=gauge,
#                         tex=tex,
#                         dia=dia,
#                         gsm=gsm,
#                         rolls=rolls,
#                         wt_per_roll=wt_per_roll,
#                         quantity=quantity,
#                         rate=rate,
#                         total_amount=amount,
#                         status=1,
#                         is_active=1
#                     )
#                     message = "New knitting entry created successfully."

#                 # message = "New knitting entry created successfully."

#             # Update `tm_table` totals
#             updated_totals = update_knitting(master_id)

#             return JsonResponse({'success': True, 'message': message, **updated_totals})

#         except sub_knitting_table.DoesNotExist:
#             return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})
    
#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# ✅ Helper functions to safely convert values
def to_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

def to_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

@csrf_exempt
def update_knitting_program(request):
    if request.method == 'POST':
        # 🔸 Extract POST data
        master_id = request.POST.get('parent_id')
        po_id = request.POST.get('po_id')
        product_id = request.POST.get('fabric_id')
        count = request.POST.get('count')
        gauge = request.POST.get('gauge')
        tex = request.POST.get('tex')
        dia = request.POST.get('dia')
        gsm = request.POST.get('gsm')
        rolls = request.POST.get('rolls')
        wt_per_roll = request.POST.get('wt_per_roll')
        quantity = request.POST.get('quantity')
        rate = request.POST.get('rate')
        amount = request.POST.get('total_amount')
        edit_id = request.POST.get('edit_id')

        if not product_id or not po_id:
            return JsonResponse({'success': False, 'error_message': 'Missing required data'})

        try:
            if edit_id:
                # 🔄 Update existing row by ID
                child_item = sub_knitting_table.objects.get(id=edit_id,dia=dia)
                child_item.fabric_id = product_id
                child_item.count_id = count
                child_item.gauge = gauge
                child_item.tex = tex
                child_item.dia = dia
                child_item.gsm = gsm
                child_item.rolls = rolls
                child_item.wt_per_roll = wt_per_roll
                child_item.quantity = quantity
                child_item.rate = rate
                child_item.total_amount = amount
                child_item.save()
                message = "Knitting program updated successfully."
            else:
                # ✅ Check if fabric + dia already exists → update it
                existing = sub_knitting_table.objects.filter(
                    tm_id=master_id,
                    fabric_id=product_id,
                    dia=dia,
                    status=1,
                    is_active=1
                ).first()

                if existing:
                    existing.rolls = to_int(existing.rolls) + to_int(rolls)
                    existing.quantity = to_float(existing.quantity) + to_float(quantity)
                    existing.total_amount = to_float(existing.total_amount) + to_float(amount)
                    existing.wt_per_roll = wt_per_roll or existing.wt_per_roll
                    existing.rate = rate or existing.rate
                    existing.save()
                    message = "Existing entry updated with new roll data."
                else:
                    # 🆕 Create new entry
                    sub_knitting_table.objects.create(
                        fabric_id=product_id,
                        tm_id=master_id,
                        count_id=count,
                        gauge=gauge,
                        tex=tex,
                        dia=dia,
                        gsm=gsm,
                        rolls=rolls,
                        wt_per_roll=wt_per_roll,
                        quantity=quantity,
                        rate=rate,
                        total_amount=amount,
                        status=1,
                        is_active=1
                    )
                    message = "New knitting entry created successfully."

            # 🔁 Update totals in tm_table or parent
            updated_totals = update_knitting(master_id)

            return JsonResponse({'success': True, 'message': message, **updated_totals})

        except sub_knitting_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': f'Failed to update knitting: {str(e)}'})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def knitting(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1) 
        product = fabric_program_table.objects.filter(status=1)
        return render(request,'knitting/knitting_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")



from django.db.models import Exists, OuterRef
from datetime import date


def knitting_program_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)

    # Subqueries to check for existence in inward and outward tables
    inward_exists = sub_yarn_inward_table.objects.filter(program_id=OuterRef('id'))
    outward_exists = yarn_delivery_table.objects.filter(program_id=OuterRef('id'))

    # Annotate knitting_table with flags for inward and outward links
    data = knitting_table.objects.filter(status=1).annotate(
        has_inward=Exists(inward_exists),
        has_outward=Exists(outward_exists)
    ).order_by('-id').values()

    formatted = [
        {
            'action': (
                # '<button type="button" onclick="knitting_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '.format(item['id']) +
                
                (
                    '<button type="button" onclick="knitting_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button>'.format(item['id'])
                    if not item['has_inward'] and not item['has_outward'] else ''
                )+ 
                (
                    '<button type="button" onclick="knitting_delete(\'{}\' )" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'])
                    if not item['has_inward'] and not item['has_outward'] else ''
                )+
                '<button type="button" onclick="knitting_print(\'{}\' )" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button> '.format(item['id']) 



            # 'action': '<button type="button" onclick="knitting_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '

            # (
            #     # '<button type="button" onclick="knitting_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '
            #     '<button type="button" onclick="knitting_delete(\'{}\' )" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'
            #     .format((item['id']), str(item['id']))
            #     if not item['has_inward'] and not item['has_outward'] else ''  # Disable buttons if linked

            ),
            'id': index + 1,
            'prg_date': item['program_date'].strftime('%d-%m-%Y') if isinstance(item.get('program_date'), date) else '-',
            'total_quantity': item['total_quantity'] if item['total_quantity'] else '-',
            'knitting_number': item['knitting_number'] if item['knitting_number'] else '-',
            'name': item['name'] if item['name'] else '-',
            'total_amount': item['total_amount'] if item['total_amount'] else '-',
            'total_tax': item['total_tax'] if item['total_tax'] else '-',
            'grand_total': item['grand_total'] if item['grand_total'] else '-',
            'lot_no': item['lot_no'] if item['lot_no'] else '-',
            'type': '<span class="badge bg-success">Yarn</span>' if item['is_yarn'] else '<span class="badge bg-danger">Grey Fabric</span>',
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        }
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})


 
 
from collections import defaultdict

 
@csrf_exempt
def program_print(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('knit-id:', order_id)
    except Exception as e:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(knitting_table, id=order_id)

    prg_details = sub_knitting_table.objects.filter(tm_id=order_id,status=1).values(
        'id', 'rolls', 'wt_per_roll', 'fabric_id', 'quantity', 'count_id',
        'tex', 'gauge', 'dia', 'gsm'
    )

    combined_details = []
    total_roll = 0
    total_wts = 0

    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])
        fab_id = product.fabric_id
        fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)
        fabric_display_name = f"{fabric_obj.name}"

        yarn = get_object_or_404(count_table, id=prg_detail['count_id'])
        tex = get_object_or_404(tex_table, id=prg_detail['tex'])
        gauge = get_object_or_404(gauge_table, id=prg_detail['gauge'])
        dia = get_object_or_404(dia_table, id=prg_detail['dia'])

        total_rolls = prg_detail['rolls']
        weight = prg_detail['rolls'] * prg_detail['wt_per_roll']

        total_roll += total_rolls
        total_wts += weight

        combined_details.append({
            'fabric': fabric_display_name,
            'yarn_count': yarn.name,
            'gauge': gauge.name,
            'tex': tex.name,
            'dia': dia.name,  # ✅ Important: this is used for sorting
            'gsm': prg_detail['gsm'],
            'roll': prg_detail.get('rolls', 0),
            'roll_wt': prg_detail.get('wt_per_roll', 0),
            'quantity': prg_detail.get('quantity', 0),
        })

    # ✅ Sort by dia name ascending
    combined_details = sorted(combined_details, key=lambda x: x['dia'])

    context = {
        'total_values': total_values,
        'total_rolls': total_roll,
        'weight': total_wts,
        'combined_details': combined_details,
        'company': company_table.objects.filter(status=1).first(),
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
    }

    return render(request, 'knitting/program_print.html', context)




# @csrf_exempt
# def program_print(request):
#     po_id = request.GET.get('k')
#     if not po_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     try:
#         order_id = int(base64.b64decode(po_id))
#         print('knit-id:', order_id)
#     except Exception as e:
#         return JsonResponse({'error': 'Invalid Order ID'}, status=400)

#     total_values = get_object_or_404(knitting_table, id=order_id)

#     # Only get relevant sub details
#     prg_details = sub_knitting_table.objects.filter(tm_id=order_id).values(
#         'id', 'rolls', 'wt_per_roll', 'fabric_id', 'quantity', 'count_id',
#         'tex', 'gauge', 'dia', 'gsm'
#     )

#     combined_details = []

    
#     total_roll = 0
#     total_wts = 0
#     for prg_detail in prg_details:
#         product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])

#         fab_id = product.fabric_id
#         fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)
#         fabric_display_name = f"{fabric_obj.name}"
        

#         yarn = get_object_or_404(count_table, id=prg_detail['count_id'])
#         tex = get_object_or_404(tex_table, id=prg_detail['tex'])
#         gauge = get_object_or_404(gauge_table, id=prg_detail['gauge'])
#         dia = get_object_or_404(dia_table, id=prg_detail['dia'])


#         total_rolls = prg_detail['rolls']
#         weight = prg_detail['rolls'] * prg_detail['wt_per_roll'] 

#         total_roll += total_rolls
#         total_wts += weight

#         combined_details.append({
#             'fabric': fabric_display_name,
#             'yarn_count': yarn.name,
#             'gauge': gauge.name,
#             'tex': tex.name,
#             'dia': dia.name,
#             'gsm': prg_detail['gsm'],
#             'roll': prg_detail.get('rolls', 0),
#             'roll_wt': prg_detail.get('wt_per_roll', 0),
#             'quantity': prg_detail.get('quantity', 0),
#         })

#     print('Combined details:', combined_details)

#     context = {
#         'total_values': total_values,
#         'total_rolls': total_roll,
#         'weight': total_wts,
#         'combined_details': combined_details,
#         'company': company_table.objects.filter(status=1).first(),
#         'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
#     }

#     return render(request, 'knitting/program_print.html', context)




@csrf_exempt
def program_print_test_6(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
        print('knit-id:',order_id)
    except Exception as e:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(knitting_table, id=order_id)

    details = knitting_table.objects.filter(id=order_id).values('id', 'total_quantity',)
    prg_details = sub_knitting_table.objects.filter(tm_id=order_id).values('id', 'rolls', 'wt_per_roll', 'fabric_id', 'quantity','count_id','tex','gauge','dia','gsm')
    print('prg-details:',prg_details)
    combined_details = []
    # delivery_details = []

    for detail in details:
        for prg_detail in prg_details:
            if prg_detail['id'] == detail['id']:
                program = get_object_or_404(knitting_table, id=prg_detail['id'])
                product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])
                yarn = get_object_or_404(count_table, id=prg_detail['count_id'])
                tex = get_object_or_404(tex_table, id=prg_detail['tex'])
                gauge = get_object_or_404(gauge_table, id=prg_detail['gauge'])
                dia = get_object_or_404(dia_table, id=prg_detail['dia'])

                
                combined_details.append({
                    'fabric': product.name,
                    'yarn_count': yarn.name,
                    'gauge': gauge.name,
                    'tex': tex.name,
                    'dia': dia.name,
                    'gsm':prg_detail['gsm'],
                    'program_name': program.name,
                    'rolls': prg_detail.get('rolls', 0),
                    'roll_wt': prg_detail.get('wt_per_roll', 0),
                    'quantity':prg_details['quantity'],
                })
                print('prg-datails:',combined_details)

    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'total_values': total_values,
  
        'combined_details': combined_details,
        'company': company_table.objects.filter(status=1).first(),
        'image_url': image_url,
    }

    return render(request, 'knitting/program_print.html', context)







# `````````````````````````````` DYEING PROGRAM ```````````````````````````````````````````


from django.db.models import Max


import re

def generate_next_do_number():
    last_purchase = dyeing_program_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.program_no:
        match = re.search(r'DY-(\d+)', last_purchase.program_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1 

    return f"DY-{next_num:03d}"





def dyeing_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)


        return render(request,'dyeing_program/dyeing_program_list.html',{'party':party,'fabric_program':fabric_program})
    else:
        return HttpResponseRedirect("/admin")
    



def get_outward_lot_no_details(request):
    if request.method == 'POST' and 'party_id' in request.POST:
        party_id = request.POST['party_id']
        print('mill-id:', party_id)

        # if party_id:
            # Step 1: Get relevant child POs
        lot_no = outward_lot_table.objects.filter(
            # party_id=party_id,
            out_quantity__gt=0
        ).values('lot_no')
        print('lot-balance:',lot_no)

           
        return JsonResponse({
            'lot_no':lot_no
            
        })

    return JsonResponse({'orders': []})
 




# def add_dyeing_program(request):
#     if 'user_id' in request.session:  
#         user_id = request.session['user_id']
#         party = party_table.objects.filter(status=1,is_process=1)

#         last_purchase = dyeing_program_table.objects.order_by('-id').first()
#         prg_number = generate_next_do_number

#         # Step 1: Get program IDs from both tables
#         outward_ids = yarn_delivery_table.objects.filter(status=1).values_list('program_id', flat=True)
#         # po_ids = grey_fabric_po_table.objects.filter(status=1).values_list('program_id', flat=True)

#         # Step 2: Get program IDs already used in dyeing program
#         used_ids = dyeing_program_table.objects.filter(status=1).values_list('program_id', flat=True)

#         # Step 3: Filter knitting_table with OR condition, then exclude used_ids
#         program = knitting_table.objects.filter(
#             status=1
#         ).filter(
#             Q(id__in=outward_ids) 
#             # | Q(id__in=po_ids)
#         ).exclude(
#             id__in=Subquery(used_ids)
#         ).order_by('id')

#         # outward = yarn_delivery_table.objects.filter(status=1).values('program_id')
#         # po = grey_fabric_po_table.objects.filter(status=1).values('knitting_program_id')
#         # if outward:
#         #     out_prg = outward
#         #     print('out-prg:',out_prg)
#         # # program = knitting_table.objects.filter(status=1,id__in=out_prg).order_by('id')

#         # # from django.db.models import Subquery

#         # used_program_ids = dyeing_program_table.objects.filter(status=1).values_list('program_id', flat=True)
#         # program = knitting_table.objects.filter(
#         #     status=1,
#         #     id__in=out_prg
#         # ).exclude(
#         #     id__in=Subquery(used_program_ids)
#         # ).order_by('id')

#         fabric_program = fabric_program_table.objects.filter(status=1)


#         print('prgs:',program)

#         return render(request,'dyeing_program/dyeing_program.html',{'party':party,'fabric_program':fabric_program,'program':program,
#                                                             #  'lot_no':lot_no,
#                                                              'prg_number':prg_number})
#     else:
#         return HttpResponseRedirect("/admin")
    





def add_dyeing_program(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_process=1)

        last_purchase = dyeing_program_table.objects.order_by('-id').first()
        prg_number = generate_next_do_number()
 
        # Step 1: Get program IDs from both tables 
        outward_ids = knitting_table.objects.filter(status=1).values_list('id', flat=True)
        po_ids = parent_gf_delivery_table.objects.filter(status=1).values_list('knitting_program_id')
        # outward_ids = yarn_delivery_table.objects.filter(status=1).values_list('program_id', flat=True)

        # Step 2: Get program IDs already used in dyeing program
        used_ids = dyeing_program_table.objects.filter(status=1).values_list('program_id', flat=True)

        # Step 3: Filter knitting_table with OR condition, then exclude used_ids
        program = knitting_table.objects.filter(
            status=1
        ).filter(
            Q(id__in=outward_ids) 
            # | Q(id__in=po_ids)
        ).exclude(
            # id__in=Subquery(used_ids)
            id__in=Subquery(used_ids,po_ids)
        ).order_by('id')

        # outward = yarn_delivery_table.objects.filter(status=1).values('program_id')
        # po = grey_fabric_po_table.objects.filter(status=1).values('knitting_program_id')
        # if outward:
        #     out_prg = outward
        #     print('out-prg:',out_prg)
        # # program = knitting_table.objects.filter(status=1,id__in=out_prg).order_by('id')

        # # from django.db.models import Subquery

        # used_program_ids = dyeing_program_table.objects.filter(status=1).values_list('program_id', flat=True)
        # program = knitting_table.objects.filter(
        #     status=1,
        #     id__in=out_prg
        # ).exclude(
        #     id__in=Subquery(used_program_ids)
        # ).order_by('id')

        fabric_program = fabric_program_table.objects.filter(status=1)


        print('prgs:',program)

        return render(request,'dyeing_program/dyeing_program.html',{'party':party,'fabric_program':fabric_program,'program':program,
                                                            #  'lot_no':lot_no,
                                                             'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    


def add_dyeing_program_test05062025(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_process=1)

        last_purchase = dyeing_program_table.objects.order_by('-id').first()
        prg_number = generate_next_do_number

        # Step 1: Get program IDs from both tables
        outward_ids = yarn_delivery_table.objects.filter(status=1).values_list('program_id', flat=True)
        po_ids = grey_fabric_po_table.objects.filter(status=1).values_list('program_id', flat=True)

        # Step 2: Get program IDs already used in dyeing program
        used_ids = dyeing_program_table.objects.filter(status=1).values_list('program_id', flat=True)

        # Step 3: Filter knitting_table with OR condition, then exclude used_ids
        program = knitting_table.objects.filter(
            status=1
        ).filter(
            Q(id__in=outward_ids) | Q(id__in=po_ids)
        ).exclude(
            id__in=Subquery(used_ids)
        ).order_by('id')

        # outward = yarn_delivery_table.objects.filter(status=1).values('program_id')
        # po = grey_fabric_po_table.objects.filter(status=1).values('knitting_program_id')
        # if outward:
        #     out_prg = outward
        #     print('out-prg:',out_prg)
        # # program = knitting_table.objects.filter(status=1,id__in=out_prg).order_by('id')

        # # from django.db.models import Subquery

        # used_program_ids = dyeing_program_table.objects.filter(status=1).values_list('program_id', flat=True)
        # program = knitting_table.objects.filter(
        #     status=1,
        #     id__in=out_prg
        # ).exclude(
        #     id__in=Subquery(used_program_ids)
        # ).order_by('id')

        fabric_program = fabric_program_table.objects.filter(status=1)


        print('prgs:',program)

        return render(request,'dyeing_program/dyeing_program.html',{'party':party,'fabric_program':fabric_program,'program':program,
                                                            #  'lot_no':lot_no,
                                                             'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    




# Function to generate knitting number series with a prefix (e.g., PO)
def generate_dye_num_series(model, field_name='program_no', padding=4, prefix='DY'):  
    # Get the maximum knitting number, and remove the prefix part to get the number
    # max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']
    max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']

    try:
        # Extract the number part and increment
        if max_value:
            # Extract the number from the field and increment
            current_number = int(max_value.replace(prefix, '')) if max_value else 0
        else:
            current_number = 0
    except ValueError:
        current_number = 0

    # Generate the next knitting number with prefix and padding
    return f"{prefix}{str(current_number + 1).zfill(padding)}"


@csrf_exempt
def insert_dyeing_program(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  
        company_id = request.session.get('company_id')
        # print('cpm-id:',company_id)
        # fyf = request.session.get('fyf')
        # print('c-fyear:',fyf)



        # # Parse financial year range (e.g., '2025-2026') to get start and end year
        # fy_start, fy_end = map(int, fyf.split('-'))

        # # Get current month and day
        # today = datetime.now()
        # month = today.month
        # day = today.day

        # # Determine correct FY integer value based on month
        # if month >= 3:  # March to December
        #     financial_year = fy_start

        # else:  # January to February
        #     financial_year = fy_end

        # print('fy:',financial_year)
        try:
            # Extracting Data from Request
            program_name = request.POST.get('name', '') 
            program_date = request.POST.get('program_date', '')
            program_id = request.POST.get('program_id', '')
            # fabric_id = request.POST.get('fabric_id', '')
            
            # Handle JSON Parsing Safely
            try:
                cutting_data = json.loads(request.POST.get('chemical_data', '[]'))
            except json.JSONDecodeError:
                cutting_data = []

            # print('Parsed Cutting Data:', cutting_data)
 
            # ✅ Create Parent Entry

             # Validate material type (must be either 'yarn' or 'grey')
            material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
            print('material-type:',material_type)
            is_grey_fabric = 1 if material_type == 'grey' else 0
            is_dyed_fabric = 1 if material_type == 'dye' else 0

            # Ensure only one of them is set to 1
            if is_grey_fabric + is_dyed_fabric != 1:
                return JsonResponse({'status': 'error', 'message': 'Select either grey_fabric or Grey Fabric !.'}, safe=False)



            dy_no = generate_next_do_number()
            
            material_request = dyeing_program_table.objects.create( 
                program_no = dy_no,
                program_date=program_date,
                name = program_name,
                program_id = program_id,
                is_grey_fabric=is_grey_fabric,
                is_dyed_fabric=is_dyed_fabric,
                # fabric_id = fabric_id,
                # company_id=company_id,
                # cfyear = 2025,
                total_rolls=0,
                total_wt=0,
                created_by=user_id,
                created_on=timezone.now() 
            )

  

            # Initialize totals
            total_rolls = 0
            total_wt = 0

            # ✅ Create Sub-Entries
            sub_entries = []
            for cutting in cutting_data:
                try:
                    fabric_id = int(cutting.get('fabric_id', 0) or 0)
                    color_id = int(cutting.get('color_id', 0) or 0)
                    dia_id = int(cutting.get('dia_id', 0) or 0)
                    rolls = int(cutting.get('roll', 0) or 0)
                    roll_wt = float(cutting.get('roll_wt', 0) or 0)
                except (ValueError, TypeError):
                    continue  # skip faulty data

                # Update totals
                total_rolls += rolls
                total_wt += roll_wt

                sub_entries.append(sub_dyeing_program_table(
                    tm_id=material_request.id,
                    fabric_id=fabric_id,
                    color_id=color_id,
                    dia_id=dia_id,
                    roll=rolls,
                    roll_wt=roll_wt,
                    created_by=user_id,
                    created_on=timezone.now()
                ))
                print('sub_entries:',sub_entries) 

            # ✅ Bulk Create Sub Entries
            # sub_dyeing_program_table.objects.bulk_create(sub_entries)

            # ✅ Update the Parent Entry with totals
            material_request.total_rolls = total_rolls
            material_request.total_wt = total_wt
            material_request.save()

            # ✅ Bulk Insert for Efficiency
            sub_dyeing_program_table.objects.bulk_create(sub_entries)

            print(f"✅ {len(sub_entries)} Sub Table Entries Created")  

            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Data added successfully'})

        except Exception as e:
            print(f"🚨 Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}) 

    return render(request, 'dyeing_program/dyeing_program.html')



from django.http import JsonResponse




# def get_lot_fabric_list(request):
#     out_id = request.POST.get('prg_id')
#     print('lot:', out_id)

#     if out_id:
#         try:
#             # Get fabric_program_table IDs from sub_knitting_table
#             program_qs = sub_knitting_table.objects.filter(tm_id=out_id, status=1).values("fabric_id")
#             fabric_program_ids = [item['fabric_id'] for item in program_qs]

#             # Fetch fabric_program entries
#             # fabric_programs = fabric_program_table.objects.filter(status=1, id__in=fabric_program_ids)
#             fabric_programs = get_object_or_404(fabric_program_table, id__in=fabric_program_ids)

#             count = get_object_or_404(count_table, id=fabric_programs.count_id)
#             gauge = get_object_or_404(gauge_table, id=fabric_programs.gauge_id)
#             tex = get_object_or_404(tex_table, id=fabric_programs.tex_id)

#             # Collect related fabric_table IDs
#             # fabric_ids = fabric_programs.values_list('fabric_id', flat=True).distinct()
#             fabric_ids = fabric_programs.values_list('fabric_id', flat=True).distinct()
#             fabric_map = {
#                 f.id: f.name
#                 for f in fabric_table.objects.filter(status=1, id__in=fabric_ids)
#             }

#             # Build response list
#             fabric_list = []
#             for fp in fabric_programs:
#                 fp_id = fp.id
#                 fabric_name =fp.name
#                 fp_name = fp.fabric_id or ""
#                 real_fabric_name = fabric_map.get(fp.fabric_id, "Unknown")
#                 fabric_list.append([fp_id, fabric_name, real_fabric_name])

#             print('fabric_list:', fabric_list)

#             return JsonResponse({
#                 "success": True,
#                 'count': {'id': count.id, 'count': count.name},
#                 'gauge': {'id': gauge.id, 'name': gauge.name},
#                 'tex': {'id': tex.id, 'name': tex.name},
#                 'gsm': {'id': fabric_programs.id, 'gray_gsm': fabric_programs.gray_gsm}
           
#                 "fabric": fabric_list
#             })

#         except Exception as e:
#             return JsonResponse({"success": False, "message": str(e)})

#     return JsonResponse({"success": False, "message": "Invalid request"})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_lot_fabric_list(request):
    out_id = request.POST.get('prg_id')
    print('lot:', out_id)

    if out_id:
        try:
            # Step 1: Get fabric_program IDs from sub_knitting_table
            program_qs = sub_knitting_table.objects.filter(tm_id=out_id, status=1).values_list("fabric_id", flat=True).distinct()
            fabric_programs = fabric_program_table.objects.filter(status=1, id__in=program_qs)

            # Step 2: Get all related fabric IDs
            fabric_ids = fabric_programs.values_list('fabric_id', flat=True).distinct()
            fabric_map = {
                f.id: f.name for f in fabric_table.objects.filter(status=1, id__in=fabric_ids)
            }

            # Step 3: Build response
            fabric_list = []
            for fp in fabric_programs:
                try:
                    count = get_object_or_404(count_table, id=fp.count_id)
                    gauge = get_object_or_404(gauge_table, id=fp.gauge_id)
                    tex = get_object_or_404(tex_table, id=fp.tex_id)
                except:
                    continue  # Skip if any FK not found

                real_fabric_name = fabric_map.get(fp.fabric_id, "Unknown")

                fabric_list.append({
                    'fabric_program_id': fp.id,
                    'fabric_program_name': fp.name,
                    'real_fabric_name': real_fabric_name,
                    'gsm': fp.gray_gsm,
                    'count': {'id': count.id, 'name': count.name},
                    'gauge': {'id': gauge.id, 'name': gauge.name},
                    'tex': {'id': tex.id, 'name': tex.name},
                })

            print('fabric_list:', fabric_list)

            return JsonResponse({
                "success": True,
                "fabric": fabric_list
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})


from collections import defaultdict

def get_fabric_dia_list(request):
    out_id = request.POST.get('id')
    fabric_id = request.POST.get('fabric_id')

    if out_id:
        try:
            # fabric = yarn_delivery_table.objects.get(program_id=out_id)
            # prg_id = fabric.program_id if fabric else 0

            prg = knitting_table.objects.get(status=1, id=out_id)
            program_rows = sub_knitting_table.objects.filter(tm_id=out_id,status=1).values(
                "fabric_id", "dia", "rolls", "wt_per_roll"
            )
            print('sub-prgs:',program_rows)

            # Extract unique fabric and dia IDs
            fabric_ids = list(set(row['fabric_id'] for row in program_rows))
            dia_ids = list(set(row['dia'] for row in program_rows))

            # Get fabric and dia details
            fab = fabric_program_table.objects.get(id__in=fabric_ids)
            fabrics = fabric_program_table.objects.filter(status=1, id__in=fabric_ids).values('id', 'name', 'color_id')
            dias = dia_table.objects.filter(status=1, id__in=dia_ids).values('id', 'name')

            # Get colors
            color_ids = fab.color_id.split(",") if fab.color_id else []
            colors = color_table.objects.filter(id__in=color_ids).values("id", "name")

            # Build a mapping of dia -> { rolls, wt_per_roll }
            dia_data = defaultdict(lambda: {"rolls": 0, "wt_per_roll": 0})
            for row in program_rows:
                dia_id = row["dia"]
                dia_data[dia_id] = {
                    "rolls": row["rolls"],
                    "wt_per_roll": row["wt_per_roll"]
                }

            return JsonResponse({
                "success": True,
                "colors": list(colors),
                "fabric": list(fabrics),
                "dia": list(dias),
                "dia_data": dia_data,  # send as a dictionary keyed by dia_id
                "quantity": prg.total_quantity,
            })
        except yarn_delivery_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Fabric not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})




from collections import defaultdict

def get_colors_for_fabric(request):
    fabric_id = request.GET.get('fabric_id')
    if fabric_id:
        try:
            fabric = fabric_program_table.objects.get(id=fabric_id)
            color_ids = fabric.color_id.split(",")  # Assuming color_id is stored as a comma-separated string
            colors = color_table.objects.filter(id__in=color_ids).values("id", "name")
            return JsonResponse({"success": True, "colors": list(colors)})
        except fabric_program_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Fabric not found"})
    return JsonResponse({"success": False, "message": "Invalid request"})

from django.http import JsonResponse


def get_fabric_details(request):
    fabric_id = request.GET.get('fabric_id')
    if fabric_id:
        try:
            fabric = fabric_program_table.objects.get(id=fabric_id)
            
            # Ensure color_id is a list of integers
            color_ids = [int(cid) for cid in fabric.color_id.split(",") if cid.isdigit()]
            colors = list(color_table.objects.filter(id__in=color_ids).values("id", "name"))

            # Get dia IDs stored in fabric_program_table
            fabric_dia_ids = [str(did) for did in fabric.dia_id.split(",") if did.isdigit()]

            # Get all available dia values
            dia_values = list(dia_table.objects.filter(status=1).values("id", "name"))

            return JsonResponse({
                "success": True,
                "colors": colors, 
                "dia_values": dia_values,
                "fabric_dia_ids": fabric_dia_ids  # Return dia IDs linked to the fabric
            })
        except fabric_program_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Fabric not found"})
    
    return JsonResponse({"success": False, "message": "Invalid request"})



from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction

from django.utils.timezone import now


 
from django.utils.dateparse import parse_date
import re
from django.utils.timezone import now

# def clean_numeric(value):
#     """Extracts only the numeric part from a value (removes non-numeric characters)."""
#     return re.sub(r"[^\d.]", "", value)  # Removes everything except digits and decimal points


def clean_numeric(value):
    value = re.sub(r"[^\d.]", "", value)
    try:
        return Decimal(value)
    except:
        return Decimal("0.00")



# Function to generate knitting number series with a prefix (e.g., PO)
def generate_do_num_series(model, field_name='program_number', padding=4, prefix='DY'):  
    # Get the maximum knitting number, and remove the prefix part to get the number
    # max_value = model.objects.aggregate(max_val=Max(field_name),status=1)['max_val']
    max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']

    try:
        # Extract the number part and increment
        if max_value:
            # Extract the number from the field and increment
            current_number = int(max_value.replace(prefix, '')) if max_value else 0
        else:
            current_number = 0
    except ValueError:
        current_number = 0

    # Generate the next knitting number with prefix and padding
    return f"{prefix}{str(current_number + 1).zfill(padding)}"

def save_dyeing_program(request):
    if request.method == "POST": 
        try:
            with transaction.atomic():
                party_id = request.POST.get("party_id")
                name = request.POST.get("name")
                gauge_id = request.POST.get("gauge_id")
                tex_id = request.POST.get("tex_id")
                count_id = request.POST.get("count_id")
                gsm = request.POST.get("gsm")
                program_date = request.POST.get("program_date")
                total_rolls = clean_numeric(request.POST.get("total_rolls", "0.00"))  # Remove non-numeric
                total_wt = clean_numeric(request.POST.get("total_wt", "0.00"))  # Remove non-numeric
                print('totals:',total_rolls, total_wt)
                remarks = request.POST.get("remarks", "")
                created_by = request.user.id

                # Create main dyeing program record
                do_number = generate_do_num_series(dyeing_program_table, 'program_no', padding=4, prefix='DY')

                main_program = dyeing_program_table.objects.create(
                    program_no = do_number,
                    name= name,
                    program_date=program_date,
                    party_id=party_id,
                    total_rolls=total_rolls, 
                    total_wt=total_wt,
                    remarks=remarks,
                    created_on=now(), 
                    updated_on=now(),
                    created_by=created_by,
                    updated_by=created_by
                )

                # Fetch all fabric, color, dia, rolls, and weight details
                fabric_ids = request.POST.getlist("fabric_id[]")
                color_ids = request.POST.getlist("color_id[]")
                dia_ids = request.POST.getlist("dia_id[]")
                rolls_values = [clean_numeric(val) for val in request.POST.getlist("rolls[]")]
                wt_values = [clean_numeric(val) for val in request.POST.getlist("wt[]")]

                # Insert sub-program records
                sub_records = []
                for i in range(len(fabric_ids)):
                    sub_records.append(sub_dyeing_program_table(
                        tm_id=main_program.id,
                        fabric_id=fabric_ids[i],
                        color_id=color_ids[i],
                        dia_id=dia_ids[i],
                        rolls=rolls_values[i],
                        wt_per_roll=wt_values[i],
                        tex_id=tex_id,
                        gauge_id=gauge_id,
                        gsm=gsm,
                        yarn_count_id=count_id,
                        created_on=now(),
                        updated_on=now(),
                        created_by=created_by,
                        updated_by=created_by
                    ))

                # Bulk insert for efficiency
                sub_dyeing_program_table.objects.bulk_create(sub_records)

            return JsonResponse({"success": True, "message": "Dyeing program saved successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})




from django.db.models import Sum

def dyeing_program_list(request):
    company_id = request.session['company_id'] 
    print('company_id:', company_id)

    # Fetch all active dyeing programs
    # dyeing_programs = list(dyeing_program_table.objects.filter(status=1).order_by('-id').values())



    inward_exists = dyed_fabric_inward_table.objects.filter(program_id=OuterRef('id'),status=1)
    outward_exists = parent_gf_delivery_table.objects.filter(dyeing_program_id=OuterRef('id'),status=1)

    # Annotate knitting_table with flags for inward and outward links
    dyeing_programs = dyeing_program_table.objects.filter(status=1).annotate(
        has_inward=Exists(inward_exists),
        has_outward=Exists(outward_exists)
    ).order_by('-id').values()

    # Pre-aggregate all roll and roll_wt sums from sub_dyeing_program_table 
    roll_summaries = sub_dyeing_program_table.objects.values('tm_id').annotate(
        total_rolls=Sum('roll'),
        total_wt=Sum('roll_wt')
    )

    # Map the roll summaries by tm_id for quick lookup 
    roll_summary_map = {entry['tm_id']: entry for entry in roll_summaries}

    # Build the final response list
    formatted = [
        {
            # 'action': '<button type="button" onclick="dyeing_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
            #             # <button type="button" onclick="dyeing_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>\
            #             <button type="button" onclick="dyeing_prg_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'], item['id'], item['id']),

            'action': (
                # '<button type="button" onclick="dyeing_program_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> '.format(item['id']) +
               
                (
                    '<button type="button" onclick="dyeing_program_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button>'.format(item['id'])
                    if not item['has_inward'] and not item['has_outward'] else ''
                )+

                (
                    '<button type="button" onclick="dyeing_program_delete(\'{}\' )" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'])
                    if not item['has_inward'] and not item['has_outward'] else ''
                )+


                
                '<button type="button" onclick="dyeing_prg_print(\'{}\' )" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button> '.format(item['id']) 
            ),
            'id': index + 1,
            'program_no': item['program_no'] if item['program_no'] else'-', 
            'program_date': item['program_date'].strftime('%d-%m-%Y') if item['program_date'] else '-',
            'name': item['name'] if item['name'] else '-',
            'outward_id': getProgram_number(knitting_table, item['program_id']),
            'total_rolls': item['total_rolls'],
            'total_wt': item['total_wt'],
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        }
        for index, item in enumerate(dyeing_programs)
    ]

    return JsonResponse({'data': formatted})




from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from collections import defaultdict
import base64
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def dyeing_program_print(request):
    po_id = request.GET.get('k')
    if not po_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(dyeing_program_table, id=order_id)

    prg_details = sub_dyeing_program_table.objects.filter(tm_id=order_id).values(
        'id', 'roll', 'roll_wt', 'fabric_id', 'dia_id', 'color_id'
    )

    combined_details = []
    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1) 
        color = get_object_or_404(color_table, id=prg_detail['color_id'])
        dia = get_object_or_404(dia_table, id=prg_detail['dia_id'])


        fab_id = product.fabric_id

        # Use get instead of filter to fetch a single fabric record 
        fabric_obj = get_object_or_404(fabric_table, id=fab_id, status=1)
        #fabric_display_name = f"{fabric.name} - {fabric_obj.name}"  # Combine program name and fabric name
        fabric_display_name = f"{fabric_obj.name}"  # Combine program name and fabric name


        combined_details.append({
            'fabric': fabric_display_name,
            'dia': dia.name,
            'color': color.name,
            'roll': prg_detail['roll'],
            'roll_wt': prg_detail['roll_wt'],
        })

    dias = sorted(set(item['dia'] for item in combined_details))

    group_map = defaultdict(lambda: {'dia_data': {}})
    grouped_data = []

    for item in combined_details:
        key = (item['fabric'], item['color'])
        group_map[key]['fabric'] = item['fabric']
        group_map[key]['color'] = item['color']
        group_map[key]['dia_data'][item['dia']] = {
            'roll': item['roll'],
            'roll_wt': item['roll_wt']
        }

    for val in group_map.values():
        val['dia_data_list'] = [
            val['dia_data'].get(dia, {'roll': '', 'roll_wt': ''}) for dia in dias
        ]

        row_total_roll = sum([entry.get('roll') or 0 for entry in val['dia_data_list']])
        row_total_weight = sum([entry.get('roll_wt') or 0 for entry in val['dia_data_list']])

        val['row_total_roll'] = row_total_roll
        val['row_total_weight'] = row_total_weight

        grouped_data.append(val)

    dia_totals = {dia: {'roll': 0, 'roll_wt': 0} for dia in dias}
    for item in combined_details:
        dia_totals[item['dia']]['roll'] += item['roll']
        dia_totals[item['dia']]['roll_wt'] += item['roll_wt']

    dia_totals_list = [dia_totals[dia] for dia in dias]
    grand_total_roll = sum(item['roll'] for item in dia_totals_list)
    grand_total_weight = sum(item['roll_wt'] for item in dia_totals_list)

    total_columns = 2 + len(dias) * 2 + 2

    context = {
        'total_values': total_values,
        'dias': dias,
        'grouped_data': grouped_data,
        'dia_totals_list': dia_totals_list,
        'grand_total_roll': grand_total_roll,
        'grand_total_weight': grand_total_weight,
        'total_columns': total_columns,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'company': company_table.objects.filter(status=1).first(),
    }

    return render(request, 'dyeing_program/program_print.html', context)



@csrf_exempt
def dyeing_program_print_test172025(request):
    po_id = request.GET.get('k') 
    if not po_id: 
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(po_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    total_values = get_object_or_404(dyeing_program_table, id=order_id)

    prg_details = sub_dyeing_program_table.objects.filter(tm_id=order_id).values(
        'id', 'roll', 'roll_wt', 'fabric_id', 'dia_id', 'color_id'
    )
  
    combined_details = []
    total_roll = 0
    total_wts = 0

    for prg_detail in prg_details:
        product = get_object_or_404(fabric_program_table, id=prg_detail['fabric_id'])
        fabric_obj = get_object_or_404(fabric_table, id=product.fabric_id, status=1)
        color = get_object_or_404(color_table, id=prg_detail['color_id'])
        dia = get_object_or_404(dia_table, id=prg_detail['dia_id'])
     
     
        # party = get_object_or_404(party_table, id=total_values.partyid)
        # gstin = party.gstin
        # mobile = party.mobile
        # party_name = party.name

        roll = prg_detail['roll']
        roll_wt = prg_detail['roll_wt']
        weight = roll * roll_wt

        total_roll += roll
        total_wts += weight

        combined_details.append({
            'fabric': fabric_obj.name,
            'dia': dia.name,
            'color': color.name,
            'roll': roll,
            'roll_wt': roll_wt,
        })

    # Collect unique dia values in sorted order
    dias = sorted(set(item['dia'] for item in combined_details))

    # Group data by fabric + color
    group_map = defaultdict(lambda: {'dia_data': {}})
    grouped_data = []

    for item in combined_details:
        key = (item['fabric'], item['color'])
        group_map[key]['fabric'] = item['fabric']
        group_map[key]['color'] = item['color']
        group_map[key]['dia_data'][item['dia']] = {
            'roll': item['roll'],
            'roll_wt': item['roll_wt']
        }

    for val in group_map.values():
        # Prebuild dia_data_list to avoid dynamic dict access in template
        val['dia_data_list'] = [
            val['dia_data'].get(dia, {'roll': '', 'roll_wt': ''}) for dia in dias
        ]
        grouped_data.append(val)

    # Dia-wise total (dict) and list (for template)
    dia_totals = {dia: {'roll': 0, 'roll_wt': 0} for dia in dias}
    for item in combined_details:
        dia_totals[item['dia']]['roll'] += item['roll']
        dia_totals[item['dia']]['roll_wt'] += item['roll_wt']

    dia_totals_list = [dia_totals[dia] for dia in dias]
    total_columns = 2 + len(dias) * 2


    grand_total_roll = sum([item['roll'] for item in dia_totals_list])
    grand_total_weight = sum([item['roll_wt'] for item in dia_totals_list])



    context = {

        # 'gstin':gstin,
        # 'mobile':mobile,
        # 'customer_name':party_name,
        'total_values': total_values,
        'dias': dias,
        'grouped_data': grouped_data,
        'dia_totals_list': dia_totals_list,
        'image_url': 'http://mpms.ideapro.in:7026/static/assets/images/mira.png',
        'total_columns':total_columns,
        'company':company_table.objects.filter(status=1).first(),
        'grand_total_roll':grand_total_roll,
        'grand_total_weight':grand_total_weight,

    }

    return render(request, 'dyeing_program/program_print.html', context)




 
def getProgram_number(tbl, supplier_id):
    try:
        party = tbl.objects.get(id=supplier_id).knitting_number
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party

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

def dyeing_program_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'dyeing_program/update_dyeing_program.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'dyeing_program/update_dyeing_program.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_dyeing_program_table.objects.filter(tm_id=material_id).first()
        
        # Fetch the parent stock instance
        parent_stock_instance = dyeing_program_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'dyeing_program/update_dyeing_program.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
      
        # Fetch active products and UOM
        product = fabric_program_table.objects.filter(status=1)
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_process=1,status=1)
        count = count_table.objects.filter(status=1) 
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        
        
        program = knitting_table.objects.filter(
            status=1,).order_by('id')

        fabric_program = fabric_program_table.objects.filter(status=1)





        fabric_program = fabric_program_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance, 
            'product': product,
            'party': party,
            'supplier': supplier,
            'count':count,
            'gauge':gauge,
            'tex':tex,
            'dia':dia,
            'fabric_program':fabric_program,
            'program':program
        }
        return render(request, 'dyeing_program/update_dyeing_program.html', context)

    except Exception as e:
        return render(request, 'dyeing_program/update_dyeing_program.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




def dyeing_program_detail_ajax_report(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data
                child_data = sub_dyeing_program_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_roll = child_data.aggregate(Sum('roll'))['roll__sum'] or 0
                    total_roll_wt = child_data.aggregate(Sum('roll_wt'))['roll_wt__sum'] or 0

                  
                    # Format child PO data for response
                    formatted_data = []
                    for index, item in enumerate(child_data.values(), start=1):
                        formatted_data.append({
                            'action': f'''
                                <button type="button" onclick="dyeing_detail_edit('{item['id']}')" class="btn btn-primary btn-xs">
                                    <i class="feather icon-edit"></i>
                                </button>
                                <button type="button" onclick="dyeing_detail_delete('{item['id']}')" class="btn btn-danger btn-xs">
                                    <i class="feather icon-trash-2"></i>
                                </button>

                                 

                            ''',
                            'id': index,
                            'fabric': getItemFabNameById(fabric_program_table, item['fabric_id']),
                            'color': getItemNameById(color_table, item['color_id']),
                            'dia': getItemNameById(dia_table, item['dia_id']),
                            'fabric_id': item['fabric_id'] or '-',
                            'dia_id': item['dia_id'] or '-',
                            'color_id': item['color_id'] or '-',
                            'roll': item['roll'] or '-',
                            'roll_wt': item['roll_wt'] or '-',
                        
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_roll': float(total_roll),  # Convert to float for JSON compatibility
                        'total_roll_wt': float(total_roll_wt),
                     
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})


 

def dyeing_program_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            dyeing_program_table.objects.filter(id=data_id).update(status=0,is_active=0,updated_on=timezone.now())

            sub_dyeing_program_table.objects.filter(tm_id=data_id).update(status=0,is_active=0,updated_on=timezone.now())
            return JsonResponse({'message': 'yes'})
        except dyeing_program_table  & sub_dyeing_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})

  
 



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def update_sub_dyeing_program(request):
    if request.method == 'POST':
        try:
            tm_id = request.POST.get('tm_id')
            fabric_id = request.POST.get('fabric_id')
            count_id = request.POST.get('count_id')

            gauge_id = request.POST.get('gauge_id')
            tex_id = request.POST.get('tex_id')
            gsm = request.POST.get('gsm')
            chemical_data_json = request.POST.get('chemical_data',[])

            # Ensure chemical_data is a list
            records = json.loads(chemical_data_json)

            if not isinstance(records, list):
                return JsonResponse({'success': False, 'error': 'Invalid data format for chemical_data'})

            print('tm-id:', tm_id)
            print('records:', records)

            sub_dyeing_program_table.objects.filter(tm_id=tm_id).delete() 

            for record in records:
                sub_dyeing_program_table.objects.create(
                    tm_id=tm_id,
                    fabric_id=fabric_id,
                    tex_id=tex_id,
                    gauge_id=gauge_id,
                    gsm=gsm,
                    yarn_count_id=count_id,
                    color_id=record.get('color_id'),
                    dia_id=record.get('dia_id'),
                    roll=record.get('roll'),
                    roll_wt=record.get('roll_wt')
                )


                # Aggregate total rolls and roll weight after insertion
                totals = sub_dyeing_program_table.objects.filter(tm_id=tm_id).aggregate(
                    total_rolls=Sum('roll'), total_wt=Sum('roll_wt')
                )

                # Update the parent dyeing_program_table
                dyeing_program_table.objects.filter(id=tm_id).update(
                    total_rolls=totals['total_rolls'] or 0,
                    total_wt=totals['total_wt'] or 0
                )

            return JsonResponse({'success': True, 'message': 'Program updated successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ``````````````````````````````````

from django.http import JsonResponse
from django.db.models import Max

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def tx_dyeing_program(request): 
    if request.method == "POST":
        tm_id = request.POST.get("tm_id")
        # tx_id = request.POST.get("tx_id")
        # print('dyeing-tx-id:',tx_id)

        if not tm_id :
            return JsonResponse({"error": "Invalid TM ID ."})

        # Fetch all dia records (id, name)
        dia_list = list(dia_table.objects.values("id", "name"))
        dia_ids = {str(dia["id"]): dia["name"] for dia in dia_list}

        # Fetch fabric and color names
        fabric_mapping = {f["id"]: f["name"] for f in fabric_program_table.objects.values("id", "name")}
        color_mapping = {c["id"]: c["name"] for c in color_table.objects.values("id", "name")}

        # Fetch valid fabric-diameter associations
        valid_fabric_dia = sub_dyeing_program_table.objects.filter(tm_id=tm_id).values_list("fabric_id", "dia_id")
        fabric_dia_map = {}
        for fabric_id, dia_id in valid_fabric_dia:
            fabric_id = str(fabric_id)  # Convert fabric_id to string for consistency
            if fabric_id not in fabric_dia_map:
                fabric_dia_map[fabric_id] = set()
            fabric_dia_map[fabric_id].add(str(dia_id))

        # Fetch dyeing program data
        program_data = sub_dyeing_program_table.objects.filter(tm_id=tm_id).values(
            'id','tm_id',"fabric_id", "color_id", "dia_id", "rolls", "wt_per_roll"
        )

        # Format response data
        data = {}
        for item in program_data:
            tx_id = str(item["id"])
            fabric_id = str(item["fabric_id"])
            color_id = str(item["color_id"])
            dia_id = str(item["dia_id"])

            key = (fabric_id, color_id)
            if key not in data:
                data[key] = {
                    "fabric_id": fabric_id,
                    'tx_id':tx_id,
                    "tm_id": item["tm_id"],
                    "fabric_name": fabric_mapping.get(int(fabric_id), "Unknown"),
                    "color_id": color_id,
                    "color_name": color_mapping.get(int(color_id), "Unknown"),
                    "dia_values": {str(d_id): {"rolls": "-", "wt_per_roll": "-"} for d_id in dia_ids},
                    "valid_dia_ids": list(fabric_dia_map.get(fabric_id, set()))  # ✅ Convert set to list
                }

            # Update dia values if available
            if dia_id in dia_ids:
                data[key]["dia_values"][dia_id] = {
                    "rolls": item["rolls"],
                    "wt_per_roll": item["wt_per_roll"]
                }

        return JsonResponse({"dia_list": dia_list, "data": list(data.values())})

    return JsonResponse({"error": "Invalid request method."})


# `````````````````````````````````````````test ````````````````````````````````````````

from django.http import JsonResponse
from django.db import transaction

from django.utils.timezone import now



from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_dyeing_program(request):
    if request.method == "POST":
        try:
            # Get data from AJAX request
            tm_id = request.POST.get("tm_id")  # Main program ID
            tx_id = request.POST.get("tx_id")  # Sub dyeing program ID
            fabric_id = request.POST.get("fabric_id")
            color_id = request.POST.get("color_id")
            dia_id = request.POST.get("dia_id")
            rolls = request.POST.get("rolls")
            weight = request.POST.get("weight")

            print("Received Data:", tm_id, tx_id, color_id, dia_id, fabric_id, rolls, weight)

            # Validate required fields
            if not tm_id or not color_id or not dia_id:
                return JsonResponse({"status": "error", "message": "Missing required parameters (tm_id, color_id, dia_id)"}, status=400)

            try:
                rolls = float(rolls) if rolls else 0
                weight = float(weight) if weight else 0
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid numeric value for rolls or weight"}, status=400)

            # Check if a matching record exists
            record = sub_dyeing_program_table.objects.filter(
                tm_id=tm_id, color_id=color_id, dia_id=dia_id, fabric_id=fabric_id 
            ).first()

            if record:
                # Update existing record
                record.rolls = rolls
                record.wt_per_roll = weight
                record.save()
                return JsonResponse({"status": "success", "message": "Record updated"})
            else:
                return JsonResponse({"status": "error", "message": "Mismatch error: No matching record found"}, status=404)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_fabric_dias(request):
    if request.method == "POST":
        fabric_id = request.POST.get("fabric_id")
        print('fab-id:',fabric_id)
        if not fabric_id:
            return JsonResponse({"success": False, "message": "Fabric ID is required."}) 

        # ✅ Get all valid dia sizes for the fabric
        dia_list = list(dia_table.objects.values("id", "name"))

        return JsonResponse({"success": True, "dia_list": dia_list})

    return JsonResponse({"success": False, "message": "Invalid request method."})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def add_fabric_rolls(request):
    """Save dia_id, rolls, and color_id against fabric_id in sub_dyeing_table."""
    if request.method == "POST":
        try:
            # ✅ Retrieve fabric_id and tm_id
            fabric_id = request.POST.get("fabric_id")
            tm_id = request.POST.get("tm_id")
            dia_data_json = request.POST.get("dia_data", "[]")  # JSON String

            # ✅ Convert JSON string to Python list
            dia_data = json.loads(dia_data_json)

            if not fabric_id or not tm_id or not dia_data:
                return JsonResponse({"success": False, "message": "Missing required fields."})

            # ✅ Get fabric details
            try:
                fabric = fabric_program_table.objects.get(id=fabric_id)

                # Get valid dia IDs from fabric_program_table
                valid_dia_ids = set(str(did) for did in fabric.dia_id.split(",") if did.isdigit())

                # Get valid color IDs from fabric_program_table
                valid_color_ids = [int(cid) for cid in fabric.color_id.split(",") if cid.isdigit()]
                
                # Fetch color details
                colors = list(color_table.objects.filter(id__in=valid_color_ids).values("id", "name"))

            except fabric_program_table.DoesNotExist:
                return JsonResponse({"success": False, "message": "Fabric not found"})

            # ✅ Loop through dia_data and save only if dia_id is in fabric_program_table
            for entry in dia_data:
                dia_id = str(entry.get("dia_id"))  # Convert to string for comparison
                rolls = entry.get("rolls", "0")
                wt_per_roll = entry.get("wt_per_roll", "0")

                # Skip if dia_id is not linked to the fabric
                if dia_id not in valid_dia_ids:
                    continue

                # ✅ Store entry for each color linked to fabric_id
                for color in colors:
                    sub_dyeing_program_table.objects.create(
                        tm_id=tm_id,
                        fabric_id=fabric_id,
                        color_id=color["id"],  # Store color_id
                        dia_id=dia_id,
                        rolls=rolls,
                        wt_per_roll=wt_per_roll
                    )

            return JsonResponse({"success": True, "message": "Dia, rolls, and color_id saved successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format in dia_data."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method."})





def update_dyeing_master(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)
 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        prg_id = request.POST.get('tm_id')
        print('id:',prg_id)
        remarks = request.POST.get('remarks')
        # is_active = request.POST.get('is_active')
        program_date_str = request.POST.get('program_date')

        material_type = request.POST.get('material_type')  # expected: 'yarn' or 'grey'
        print('material-type:',material_type)
        is_grey_fabric = 1 if material_type == 'grey' else 0
        is_dyed_fabric = 1 if material_type == 'dye' else 0

        # Ensure only one of them is set to 1
        if is_grey_fabric + is_dyed_fabric != 1:
            return JsonResponse({'status': 'error', 'message': 'Select either grey_fabric or Grey Fabric !.'}, safe=False)



        
        try:
            tm = dyeing_program_table.objects.get(id=prg_id)
            tm.remarks = remarks
            # tm.is_active = is_active
            tm.is_dyed_fabric = is_dyed_fabric
            tm.is_grey_fabric = is_grey_fabric

            if program_date_str:
                program_date = datetime.strptime(program_date_str, '%Y-%m-%d').date()
                tm.program_date = program_date

                
            tm.updated_by = user_id
            tm.updated_on = datetime.now()
            tm.save()
            return JsonResponse({'message': 'success'})
        except dyeing_program_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'tm not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})




# `````````````````````` accessory program ````````````````````````````````````````````````````````````````



def accessory_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 

        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        last_purchase = accessory_program_table.objects.order_by('-id').first()
        if last_purchase: 
            prg_number = last_purchase.id + 1 
        else:
            prg_number = 1   # Default if no records exist


        return render(request,'program/accessory_prg/accessory_program_list.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    


 
def accessory_program_view(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(accessory_program_table.objects.filter(status=1).order_by('-id').values())
 
    formatted = [
        {
            'action': '<button type="button" onclick="accessory_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="accessory_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'],item['id']),
            'id': index + 1, 
            'acc_no': item['accessory_no'] if item['accessory_no'] else'-', 
            # 'party_id':getSupplier(party_table, item['party_id'] ), 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})  
  

 
def add_accessory_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_cutting=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 

        last_purchase = accessory_program_table.objects.order_by('-id').first()
        if last_purchase:  
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist
        print('prg-no:',prg_number) 

        quality = quality_table.objects.filter(status=1).order_by('name')
        # if quality:
        #     qulaity_str = quality_table.objects.filter(id=quality.id,status=1) 
        # else:
        #     quality_str = None
        style = style_table.objects.filter(status=1).order_by('name')
        size = size_table.objects.filter(status=1).order_by('name')
        color = color_table.objects.filter(status=1).order_by('name')
        cutting_program = cutting_program_table.objects.filter(status=1)
        accessory_item = item_table.objects.filter(status=1).order_by('name')
        fabric = fabric_program_table.objects.filter(status=1).order_by('name')
        uom = uom_table.objects.filter(status=1).order_by('name')
        group = item_group_table.objects.filter(status=1,is_active=1).order_by('name')
        return render(request,'program/accessory_prg/add_accessory_program.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number,'color':color
                                                            ,'group':group,'uom':uom,'fabric':fabric,'accessory_item':accessory_item,'cutting_program':cutting_program,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
     


@csrf_exempt
def save_accessory_program(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  
        company_id = request.session.get('company_id')

        try:
            # Extracting Data from Request
            quality_id = int(request.POST.get('quality_id', 0) or 0)
            # program_type = request.POST.get('program_type', '')
            style_id = int(request.POST.get('style_id', 0) or 0)
            total_quantity = int(request.POST.get('total_quantity', '0') or 0)

            # Handle JSON Parsing Safely
            try:
                cutting_data = json.loads(request.POST.get('cutting_data', '[]'))
            except json.JSONDecodeError:
                cutting_data = []

            print('Parsed Cutting Data:', cutting_data)

            # ✅ Create Parent Entry
            material_request = accessory_program_table.objects.create(
                quality_id=quality_id,
                # program_type=program_type,
                style_id=style_id,
                company_id=company_id,
                total_quantity=total_quantity,
                created_by=user_id,
                created_on=timezone.now()
            )

            # ✅ Create Sub-Entries
            sub_entries = []
            for cutting in cutting_data:
                sub_entries.append(sub_accessory_program_table(
                    tm_id=material_request.id, 
                    uom_id=int(cutting.get('uom_id', 0) or 0),
                    item_id=int(cutting.get('item_id', 0) or 0),
                    item_group_id = int(cutting.get('item_group_id', 0) or 0),
                    program_type=cutting.get('program_type', 'SIZE'),
                    product_pieces=int(cutting.get('product_pieces', 0) or 0),
                    acc_quality_id=int(cutting.get('quality_id', 0) or 0),
                    acc_size_id=int(cutting.get('accessory_size_id', 0) or 0),
                    size_id=int(cutting.get('quality_size_id', 0) or 0),
                    position=int(cutting.get('position', 0) or 0),
                    # quantity=int(cutting.get('quantity', 0) or 0),
                    quantity=float(cutting.get('quantity', 0) or 0),  # ✅ Convert to float
                    created_by=user_id,
                    created_on=timezone.now()
                ))

            # ✅ Bulk Insert for Efficiency
            sub_accessory_program_table.objects.bulk_create(sub_entries)

            print(f"✅ {len(sub_entries)} Sub Table Entries Created")  

            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'})

        except Exception as e:
            print(f"🚨 Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)})

    return render(request, 'program/accessory_prg/add_accessory_program.html')



from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json

# @csrf_exempt
# def update_save_color_selection(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')
#         company_id = request.session.get('company_id')

#         try:
#             payload = json.loads(request.POST.get('payload', '{}'))

#             program_type = payload.get('program_type')
#             product_pieces = payload.get('product_pieces')
#             quality_id = payload.get('quality_id')
#             item_group_id = payload.get('item_group_id')
#             item_id = payload.get('item_id')
#             uom_id = payload.get('uom_id')

#             tm_id = int(request.POST.get('tm_id', 0))

#             sizes = payload.get('sizes', [])

#             created_count = 0
#             updated_count = 0

#             for size_data in sizes:
#                 accessory_size_id = size_data.get('accessory_size_id')
#                 quantities = size_data.get('quantities', [])

#                 for quantity_data in quantities:
#                     quantity = float(quantity_data.get('quantity', 0))
#                     position = quantity_data.get('position', 0)
#                     quality_size_id = quantity_data.get('quality_size_id')

#                     # Check if the entry already exists
#                     existing = sub_accessory_program_table.objects.filter(
#                         tm_id=tm_id,
#                         item_id=item_id,
#                         item_group_id=item_group_id,
#                         acc_size_id=accessory_size_id
#                     ).first()

#                     if existing:
#                         # Update quantity
#                         existing.quantity = quantity
#                         existing.position = position
#                         existing.updated_by = user_id
#                         existing.updated_on = timezone.now()
#                         existing.save()
#                         updated_count += 1
#                     else:
#                         # Create new entry
#                         sub_accessory_program_table.objects.create(
#                             tm_id=tm_id,
#                             uom_id=uom_id,
#                             item_id=item_id,
#                             item_group_id=item_group_id,
#                             program_type=program_type,
#                             product_pieces=product_pieces,
#                             acc_quality_id=quality_id,
#                             acc_size_id=accessory_size_id,
#                             size_id=quality_size_id,
#                             position=position,
#                             quantity=quantity,
#                             created_by=user_id,
#                             created_on=timezone.now()
#                         )
#                         created_count += 1

#             print(f"✅ {created_count} created, {updated_count} updated.")
#             return JsonResponse({'status': 'yes', 'message': f'{created_count} added, {updated_count} updated'})

#         except Exception as e:
#             print(f"🚨 Error: {e}")
#             return JsonResponse({'status': 'no', 'message': str(e)})

#     return JsonResponse({'status': 'no', 'message': 'Invalid request method.'})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json

@csrf_exempt
def update_save_color_selection_test_9425(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            payload = json.loads(request.POST.get('payload', '{}'))

            program_type = payload.get('program_type')
            product_pieces = payload.get('product_pieces')
            quality_id = payload.get('quality_id')
            item_group_id = payload.get('item_group_id')
            item_id = payload.get('item_id')
            uom_id = payload.get('uom_id')

            tm_id = int(request.POST.get('tm_id', 0))

            sizes = payload.get('sizes', [])

            for size_data in sizes:
                accessory_size_id = size_data.get('accessory_size_id')
                quantities = size_data.get('quantities', [])

                for quantity_data in quantities:
                    quantity = float(quantity_data.get('quantity', 0))
                    position = quantity_data.get('position', 0)
                    quality_size_id = quantity_data.get('quality_size_id')

                    # Check if this exact combo already exists
                    duplicate_exists = sub_accessory_program_table.objects.filter(
                        tm_id=tm_id,
                        item_id=item_id,
                        item_group_id=item_group_id,
                        acc_size_id=accessory_size_id,
                        acc_quality_id=quality_id,
                        size_id=quality_size_id

                    ).exists()

                    if duplicate_exists:
                        return JsonResponse({
                            'status': 'no',
                            'message': 'Program already exists in this table. Please click its row to update instead of adding again.'
                        })

                    # If not duplicate, create new entry
                    sub_accessory_program_table.objects.create(
                        tm_id=tm_id,
                        uom_id=uom_id,
                        item_id=item_id,
                        item_group_id=item_group_id,
                        program_type=program_type,
                        product_pieces=product_pieces,
                        acc_quality_id=quality_id,
                        acc_size_id=accessory_size_id,
                        size_id=quality_size_id,
                        position=position,
                        quantity=quantity,
                        created_by=user_id,
                        created_on=timezone.now()
                    )

            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'})

        except Exception as e:
            print(f"🚨 Error: {e}")
            return JsonResponse({'status': 'no', 'message': str(e)})

    return JsonResponse({'status': 'no', 'message': 'Invalid request method.'})




@csrf_exempt
def update_save_color_selection(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  
        company_id = request.session.get('company_id')

        try:
            # Retrieve the payload from the request
            payload = json.loads(request.POST.get('payload', '{}'))

            # Extract fields from the payload
            program_type = payload.get('program_type')
            print('p-type:',program_type)
            product_pieces = payload.get('product_pieces')
            quality_id = payload.get('quality_id')
            quality_name = payload.get('quality_name')
            item_group_id = payload.get('item_group_id')
            item_group_name = payload.get('item_group_name')
            item_id = payload.get('item_id')
            item_name = payload.get('item_name')
            uom_id = payload.get('uom_id')
            uom_name = payload.get('uom_name')

            # Get the sizes from the payload
            sizes = payload.get('sizes', [])

            # Prepare the list of sub_entries to bulk create
            sub_entries = []
            tm_id = int(request.POST.get('tm_id', 0))

            for size_data in sizes:
                accessory_size_id = size_data.get('accessory_size_id')
                size_id = size_data.get('size_id')
                size_name = size_data.get('size_name')
                quantities = size_data.get('quantities', [])

                for quantity_data in quantities:
                    quantity = quantity_data.get('quantity', 0)
                    position = quantity_data.get('position', 0)
                    quality_size_id = quantity_data.get('quality_size_id')
                    # quality_size_id = quantity_data.get('quality_size_id')

                    duplicate_exists = sub_accessory_program_table.objects.filter(
                        tm_id=tm_id,
                        item_id=item_id,
                        item_group_id=item_group_id,
                        acc_size_id=accessory_size_id,
                        acc_quality_id=quality_id,
                        size_id=quality_size_id,
                        program_type = program_type,
                        status=1,

                    ).exists()

                    if duplicate_exists:
                        return JsonResponse({
                            'status': 'no',
                            'message': 'Program already exists in this table. Please click its row to update instead of adding again.'
                        })
                    # Append the new sub-accessory program entry
                    sub_entries.append(sub_accessory_program_table(
                        tm_id=int(request.POST.get('tm_id', 0)),  # Retrieve tm_id from POST
                        uom_id=uom_id,  
                        item_id=item_id,  
                        item_group_id=item_group_id,  
                        program_type=program_type,
                        product_pieces=product_pieces,
                        acc_quality_id=quality_id,
                        acc_size_id=accessory_size_id,
                        size_id=quality_size_id,
                        position=position,
                        quantity=float(quantity),  # Ensure quantity is saved as float
                        created_by=user_id,
                        created_on=timezone.now()
                    ))

            # Bulk insert for efficiency
            sub_accessory_program_table.objects.bulk_create(sub_entries)

            print(f"✅ {len(sub_entries)} Sub Table Entries Created")  

            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'})

        except Exception as e:
            print(f"🚨 Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)})

    return JsonResponse({'status': 'no', 'message': 'Invalid request method.'})




@csrf_exempt
def update_save_color_selection_test1(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  
        company_id = request.session.get('company_id')

        try:
            # Retrieve the payload from the request
            payload = json.loads(request.POST.get('payload', '{}'))

            tm_id = int(request.POST.get('tm_id', 0))

            # Get the sizes and other data from the payload
            sizes = payload.get('sizes', [])

            # Prepare the list of sub_entries to bulk create
            sub_entries = []

            for size_data in sizes:
                accessory_size_id = size_data.get('accessory_size_id')
                uom_id = size_data.get('uom_id')
                size_id = size_data.get('size_id')
                
                item_id = request.POST.get('item_id')
                item_group_id = request.POST.get('item_group_id')
                program_type = request.POST.get('program_type')
                product_pieces = request.POST.get('product_pieces')
                size_name = size_data.get('size_name')
               
                quantities = size_data.get('quantities', [])

                for quantity_data in quantities:
                    quantity = quantity_data.get('quantity', 0)
                    position = quantity_data.get('position', 0)
                    quality_size_id = quantity_data.get('quality_size_id')

                    # Append the new sub-accessory program entry 
                    sub_entries.append(sub_accessory_program_table(
                        tm_id=tm_id,
                        uom_id=uom_id,  # Add appropriate uom_id if needed
                        item_id=item_id,  # Add appropriate item_id if needed
                        item_group_id=item_group_id,  # Add appropriate item_group_id if needed
                        program_type = program_type,  # Add appropriate item_group_id if needed
                        product_pieces=product_pieces,  # Add product_pieces if needed
                        acc_quality_id=accessory_size_id,
                        acc_size_id=quality_size_id,
                        size_id=size_id,
                        position=position,
                        quantity=quantity,  # Save as float
                        created_by=user_id,
                        created_on=timezone.now()
                    ))

            # Bulk insert for efficiency
            sub_accessory_program_table.objects.bulk_create(sub_entries)

            print(f"✅ {len(sub_entries)} Sub Table Entries Created")  

            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'})

        except Exception as e:
            print(f"🚨 Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)})

    return JsonResponse({'status': 'no', 'message': 'Invalid request method.'})




@csrf_exempt  # Use only if necessary
def get_quality_item_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id') 
        print('Quality-ID:', quality_id)

        if not quality_id:
            return JsonResponse({'error': 'Quality ID is required'}, status=400)

        try:
            parent = quality_program_table.objects.filter(quality_id=quality_id)

            if not parent.exists():
                return JsonResponse({'error': 'No matching records found'}, status=404)

            items = parent.values_list('style_id', flat=True).distinct()
            q_items = parent.values_list('id', flat=True).distinct()
            print('Parent IDs:', items)

            child = sub_quality_program_table.objects.filter(tm_id__in=q_items)
            sub_items = child.values_list('tm_id', 'size_id').distinct()

            style = style_table.objects.filter(id__in=items).values('id', 'name').order_by('name')

            size_ids = [size_id for _, size_id in sub_items]  
            size = size_table.objects.filter(id__in=size_ids).values('id', 'name').order_by('name')

            response_data = {
                'style': list(style),
                'size': list(size),
            } 

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_style_based_sizes(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        print('Quality ID:', quality_id, 'Style ID:', style_id)

        if not quality_id or not style_id:
            return JsonResponse({'error': 'Quality ID and Style ID are required'}, status=400)

        try:
            parent = quality_program_table.objects.filter(quality_id=quality_id, style_id=style_id,status=1)

            if not parent.exists():
                return JsonResponse({'error': 'No matching records found'}, status=404)

            q_items = parent.values_list('id', flat=True).distinct()

            child = sub_quality_program_table.objects.filter(tm_id__in=q_items,status=1)
            print('child-q-size:',child)
            sub_items = child.values_list('size_id', 'position').distinct()

            # Create a list with size ID, name, and position
            size_data = []
            for size_id, position in sub_items:
                size_obj = size_table.objects.filter(id=size_id).values('id', 'name').first()
                if size_obj:
                    size_obj['position'] = position  # Add position field
                    size_data.append(size_obj)

            # ✅ Sort sizes based on position
            size_data = sorted(size_data, key=lambda x: x['position'])

            return JsonResponse({'size': size_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)





from django.http import JsonResponse
from django.db.models import Min

# def get_acc_quality_item_list(request):
#     if request.method == 'POST':
#         group_id = request.POST.get('group_id')
#         if not group_id:
#             return JsonResponse({'error': 'Group ID is required'}, status=400)

#         try:
#             acc_items = (
#                 item_table.objects.filter(item_group_id=group_id, is_active=1, status=1)
#                 .values('name')  # Group by name
#                 .annotate(id=Min('id'))  # Pick the smallest ID for uniqueness
#                 .order_by('name')
#             )

#             return JsonResponse({'item': list(acc_items)})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_acc_quality_item_list(request):
# def get_acc_item_list(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        if not group_id:
            return JsonResponse({'error': 'Group ID is required'}, status=400)

        try:
            acc_items = item_table.objects.filter(
                item_group_id=group_id, is_active=1, status=1
            ).values('id', 'name').order_by('name')

            return JsonResponse({'item': list(acc_items)})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def get_acc_quality_list(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if not item_id:
            return JsonResponse({'error': 'Item ID is required'}, status=400)

        try:
            quality_ids = sub_size_table.objects.filter(
                item_id=item_id, is_active=1, status=1
            ).values_list('quality_id', flat=True).distinct()
 
            qualities = accessory_quality_table.objects.filter(
                id__in=quality_ids, is_active=1, status=1
            ).values('id', 'name').order_by('name')
 
            return JsonResponse({'quality': list(qualities)})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)







def get_acc_item_size_list(request):
    if request.method == "POST":
        quality_id = request.POST.get("quality_id")
        item_id = request.POST.get("item_id")

        if not quality_id:
            return JsonResponse({"error": "Missing quality ID"}, status=400)
 
        try:
            # Get all item IDs associated with the given quality_id
            # quality_items = sub_item_table.objects.filter(
            #     quality_id=quality_id, status=1, 
            # ).values_list("item_id", flat=True)
            # print('quality-item-id:',quality_items)

            # Get size_ids linked to the extracted item IDs 
            size_values = sub_size_table.objects.filter(
                item_id=item_id, status=1,
            ).values_list("size_id", flat=True)

            # Get size names
            sizes = accessory_size_table.objects.filter(
                id__in=size_values,status=1,
            ).values("id", "name")

            return JsonResponse({"sizes": list(sizes)})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# ````````````````````````````````````````````````````````````````````

from django.http import JsonResponse

def get_size_list(request):
    if request.method == "POST":
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not quality_id or not style_id:
            return JsonResponse({'error': 'Missing quality or style ID'}, status=400)

        # Fetch the matching quality entry
        quality = quality_program_table.objects.filter(quality_id=quality_id, style_id=style_id,status=1).first()

        if not quality:
            return JsonResponse({'error': 'No matching quality found'}, status=404)

        # Fetch sizes linked to this quality entry
        sub_quality_sizes = sub_quality_program_table.objects.filter(tm_id=quality.id, status=1).values('size_id')

        # Extract size IDs from the queryset
        size_ids = [item['size_id'] for item in sub_quality_sizes]

        # Fetch size details from size_table using the extracted size_ids
        sizes = size_table.objects.filter(id__in=size_ids).values('id', 'name')

        return JsonResponse({'sizes': list(sizes)})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_color_list(request):
    if request.method == "POST": 
        size_id = request.POST.get('size_id') 

        if not size_id:
            return JsonResponse({'error': 'Missing size ID'}, status=400)

        colors = color_table.objects.filter(status=1,is_active=1).values('id', 'name')  # Adjust filtering as needed
        return JsonResponse({'colors': list(colors)})

    return JsonResponse({'error': 'Invalid request method'}, status=405) 




@csrf_exempt 
def get_color_lists(request): 
    if request.method == "POST": 
        fabric_id = request.POST.get("fabric_id") 
 
        try:
            fabric = fabric_program_table.objects.filter(status=1, is_active=1, id=fabric_id).first()
            print('fab-:',fabric)
            if not fabric:
                return JsonResponse({'colors': []})  # Fabric not found

            color_id = getattr(fabric, 'color_id', None)
  
            if not color_id:
                return JsonResponse({'colors': []})  # No color_id in fabric

            # Support comma-separated string or single ID
            if isinstance(color_id, str) and ',' in color_id:
                color_ids = [int(cid) for cid in color_id.split(',') if cid.strip().isdigit()]
                colors = color_table.objects.filter(status=1, is_active=1, id__in=color_ids).values('id', 'name')
            else: 
                colors = color_table.objects.filter(status=1, is_active=1, id=color_id).values('id', 'name')

            print('color:', colors)
            return JsonResponse({'colors': list(colors)})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def get_quality_size_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')

        if not quality_id or not style_id:
            return JsonResponse({'error': 'Missing quality or style'}, status=400)

        try:
            quality = quality_program_table.objects.filter(
                status=1, quality_id=quality_id, style_id=style_id
            ).first()

            if not quality:
                return JsonResponse({'error': 'No matching quality found'}, status=404)

            # Get all sub-programs with related size_id
            sub_qs = sub_quality_program_table.objects.filter(
                status=1,
                is_active=1,
                tm_id=quality.id
            ).values_list('size_id', flat=True).distinct()

            sizes = size_table.objects.filter(
                status=1,
                is_active=1,
                id__in=sub_qs
            ).values('id', 'name').order_by('id')

            return JsonResponse({'sizes': list(sizes)})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def get_color_lists(request):
#     if request.method == "POST": 
#         fabric_id = request.POST.get("fabric_id")

#         try:
#             fabric = fabric_program_table.objects.filter(status=1, is_active=1, id=fabric_id).first()

#             if not fabric or not fabric.color_id:
#                 return JsonResponse({'colors': []})  # No matching fabric or no color_id

#             colors = color_table.objects.filter(
#                 status=1,
#                 is_active=1,
#                 id=fabric.color_id  # Assuming color_id is a single FK
#             ).values('id', 'name')
#             print('color:',colors)
#             return JsonResponse({'colors': list(colors)})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_acc_size_list(request):
    if request.method == "POST":
        quality_id = request.POST.get("quality_id")
        item_id = request.POST.get("item_id")

        if not quality_id:
            return JsonResponse({"error": "Missing quality ID"}, status=400)

        try:
            # Get all item IDs associated with the given quality_id
            # quality_items = sub_item_table.objects.filter(
            #     item_id=item_id,quality_id=quality_id, status=1, 
            # ).values_list("item_id", flat=True)
            # print('quality-item-id:',quality_items)

            # Get size_ids linked to the extracted item IDs 
            size_values = sub_size_table.objects.filter(
                item_id=item_id, status=1,
            ).values_list("size_id", flat=True)

            # Get size names
            sizes = accessory_size_table.objects.filter(
                id__in=size_values,status=1,
            ).values("id", "name")

            return JsonResponse({"sizes": list(sizes)})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def accessory_program_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'program/accessory_prg/update_accessory_program.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'program/accessory_prg/update_accessory_program.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_accessory_program_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            # acc_size_id = request.POST.get('acc_size_id')  # Adjust as per your input structure
            # uom_id = request.POST.get('uom_id')  # Adjust as per your input structure
            # size_id = request.POST.get('size_id')  # Adjust as per your input structure
            # item_id = request.POST.get('item_id')  # Adjust as per your input structure
            # item_group_id = request.POST.get('item_group_id')  # Adjust as per your input structure
            # quantity = request.POST.get('quantity')  # Adjust as per your input structure
           
            # Ensure valid data before saving 
            # if size_id :
            #     material_instance = sub_accessory_program_table.objects.create(
            #         tm_id=material_id,
            #         acc_size_id=acc_size_id, 
            #         item_id=item_id, 
            #         item_group_id=item_group_id, 
            #         size_id=size_id, 
            #         uom_id=uom_id, 
            #         quantity=quantity,
            #         # Add any other necessary fields here
            #     )
            # else:
            return render(request, 'program/accessory_prg/update_accessory_program.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = accessory_program_table.objects.filter(id=material_id).first()
        print('parent-data:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'program/accessory_prg/update_accessory_program.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
       
        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_cutting=1,status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)


        accessory_item = item_table.objects.filter(status=1).order_by('name')
        fabric = fabric_program_table.objects.filter(status=1).order_by('name')
        uom = uom_table.objects.filter(status=1).order_by('name')
        group = item_group_table.objects.filter(status=1,is_active=1).order_by('name')
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            'supplier': supplier,
            'size':size,
            'quality':quality,
            'style':style,
            'accessory_item':accessory_item,
            'fabric':fabric,
            'uom':uom,
            'group':group
           
        }
        print('style-id:',parent_stock_instance.style_id)
        return render(request, 'program/accessory_prg/update_accessory_program.html', context)

    except Exception as e:
        return render(request, 'program/accessory_prg/update_accessory_program.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



from collections import defaultdict

def update_acc_ratio_view(request):
    tm_id = request.POST.get('tm_id')

    if not tm_id:
        return JsonResponse({'error': 'Invalid TM ID'})

    # Fetch child data
    child_qs = sub_accessory_program_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')
    print('tx-prg:',child_qs)
 
    if child_qs.exists():
        parent_data = accessory_program_table.objects.filter(id=tm_id).first()

        quality_name = ''
        style_name = ''

        if parent_data:
            quality_obj = quality_table.objects.filter(id=parent_data.quality_id).first()
            style_obj = style_table.objects.filter(id=parent_data.style_id).first()

            quality_name = quality_obj.name if quality_obj else ""
            style_name = style_obj.name if style_obj else ""



        child_data = list(child_qs.values())

        formatted_data = []
        grouped_data = defaultdict(lambda: {
            'id': None,
            'product_pieces': None,
            'tm_id': tm_id,
            'acc_size': None,
            'item': None,
            'group': None,
            'acc_quality': None,
            'status': None,
            'action': None,
            'size_columns': {f'size_{i}': '-' for i in range(1, 9)}
        })

        for index, item in enumerate(child_data):
            # acc_size_id = item['acc_size_id']
            # item_id = item['item_id']  # Ensure different accessories are separate rows

            # key = f"{acc_size_id}-{item_id}"  # Group by accessory size and accessory item

            # row = grouped_data[key]

            acc_size_id = item['acc_size_id']
            uom_id = item['uom_id']
            item_id = item['item_id']
            item_group_id = item['item_group_id'] 
            acc_quality_id = item['acc_quality_id']
            program_type = item['program_type']

            # More specific grouping key
            key = f"{item_id}-{item_group_id}-{acc_quality_id}-{acc_size_id}-{program_type}-{uom_id}" 

            row = grouped_data[key]


            if row['id'] is None:  # Populate row only once
                row.update({  
                    'id': item['id'],
                    'product_pieces': item['product_pieces'], 
                    'program_type': item['program_type'],
                    'uom': getSupplier(uom_table, uom_id),
                    'acc_size': getSupplier(accessory_size_table, acc_size_id),
                    'item': getSupplier(item_table, item_id),
                    'group': getSupplier(item_group_table, item['item_group_id']),
                    'acc_quality': getSupplier(accessory_quality_table, item['acc_quality_id']),
                    'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
                    # Correctly format the 'action' field with correct variable passing
                    # 'action': f"<button type='button' onclick=\"tx_acc_ratio_delete('{item['tm_id']},{item['acc_size_id']},{item['program_type']}')\" class='btn btn-danger btn-xs'><i class='feather icon-trash-2'></i></button>",
                    'action': f"<button type='button' onclick=\"tx_acc_ratio_delete('{item['tm_id']},{item['acc_size_id']},{item['program_type']},{item['item_id']},{item['item_group_id']},{item['acc_quality_id']}')\" class='btn btn-danger btn-xs'><i class='feather icon-trash-2'></i></button>"
                    f"<button type='button' onclick=\"tx_acc_ratio_edit('{item['id']}')\" class='btn btn-primary btn-xs'><i class='feather icon-edit'></i></button>",
                    # f"<button type='button' onclick=\"tx_acc_ratio_edit('{item['id']},{item['tm_id']},{item['acc_size_id']},{item['program_type']},{item['item_id']},{item['item_group_id']},{item['acc_quality_id']}')\" class='btn btn-primary btn-xs'><i class='feather icon-edit'></i></button>",
                    'acc_size_id': acc_size_id,  # Ensure acc_size_id is included in the row
                })

            # Assign quantity to correct size column 
            position = item['position']
            if position and 1 <= position <= 8:
                row['size_columns'][f'size_{position}'] = item['quantity']

        # Convert grouped data into final format
        for row in grouped_data.values():
            row.update(row.pop('size_columns'))
            formatted_data.append(row)

        # return JsonResponse({'data': formatted_data, 'total_quantity': total_quantity})

        return JsonResponse({
            'data': formatted_data,
            # 'total_quantity': total_quantity,
            'quality_name': quality_name,
            'style_name': style_name
        }) 
    return JsonResponse({'error': 'No cutting program data found for this TM ID'})



# @csrf_exempt
# def edit_acc_ratio_settings(request):
#     if request.method == 'POST':
#         tx_id = request.POST.get('id')
    
#         print('tx_id',tx_id)
          


#         try:
#             # Update all positions (size_1 to size_8)
#             for pos in range(1, 9):
#                 quantity = request.POST.get(f'size_{pos}', 0)

#                 sub_item = sub_accessory_program_table.objects.filter(
#                     id=tx_id,
                   
#                 ).first()

                

#             return JsonResponse({'success': True})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def edit_acc_ratio_settings(request):
    if request.method == 'POST':
        tx_id = request.POST.get('id')

        try:
            sub_item = sub_accessory_program_table.objects.filter(id=tx_id, status=1).first()
            if not sub_item:
                return JsonResponse({'error': 'Record not found'}, status=404)

            # Resolve related names properly
            acc_size_name = accessory_size_table.objects.filter(
                status=1, id=sub_item.acc_size_id
            ).values_list("name", flat=True).first()
            item_name = item_table.objects.filter(
                status=1, id=sub_item.item_id
            ).values_list("name", flat=True).first()
            item_group_name = item_group_table.objects.filter(
                status=1, id=sub_item.item_group_id
            ).values_list("name", flat=True).first()
            acc_quality_name = accessory_quality_table.objects.filter(
                status=1, id=sub_item.acc_quality_id
            ).values_list("name", flat=True).first()
            uom_name = uom_table.objects.filter(
                status=1, id=sub_item.uom_id
            ).values_list("name", flat=True).first()

            # Base info
            data = {
                'id': sub_item.id,
                'tm_id': sub_item.tm_id,
                'acc_size_id': sub_item.acc_size_id,
                'acc_size_name': acc_size_name,
                'program_type': sub_item.program_type,
                'product_pieces': sub_item.product_pieces,
                'item_id': sub_item.item_id,
                'item_name': item_name,
                'item_group_id': sub_item.item_group_id,
                'item_group_name': item_group_name,
                'acc_quality_id': sub_item.acc_quality_id,
                'acc_quality_name': acc_quality_name,
                'acc_uom_name': uom_name,
                'is_active': sub_item.is_active,
            }

            # Fetch all size rows for this combination
            size_rows = sub_accessory_program_table.objects.filter(
                tm_id=sub_item.tm_id,
                acc_size_id=sub_item.acc_size_id,
                program_type=sub_item.program_type,
                item_id=sub_item.item_id,
                item_group_id=sub_item.item_group_id,
                acc_quality_id=sub_item.acc_quality_id,
                status=1
            ).values("size_id", "quantity", "position")

            # Map size_id -> name
            size_ids = [row["size_id"] for row in size_rows]
            size_names_map = dict(
                accessory_size_table.objects.filter(id__in=size_ids, status=1).values_list("id", "name")
            )

            # Build list
            sizes = []
            for row in size_rows:
                sizes.append({
                    "size_id": row["size_id"],
                    "size_name": size_names_map.get(row["size_id"], ""),
                    "quantity": row["quantity"],
                    "position": row["position"],
                })
            print('sizes:',sizes)

            data["sizes"] = sizes

            return JsonResponse(data, status=200, safe=False)

        except Exception as e: 
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)




@csrf_exempt
def acc_ratio_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        try:
            user_id = request.session.get('user_id')
            edit_id = request.POST.get('edit_tx_id')

            # Get one reference row
            sub_item = sub_accessory_program_table.objects.filter(id=edit_id, status=1).first()
            if not sub_item:
                return JsonResponse({'message': 'error', 'error_message': 'Record not found'})

            # Update base values
            program_type = request.POST.get('program_type')
            product_pieces = request.POST.get('edit_product_pieces')
            is_active = request.POST.get('is_active')

            print('types:',program_type, product_pieces)
            # Get all rows in the same "group"
            rows = sub_accessory_program_table.objects.filter( 
                tm_id=sub_item.tm_id,
                acc_size_id=sub_item.acc_size_id,
                item_id=sub_item.item_id,
                item_group_id=sub_item.item_group_id, 
                acc_quality_id=sub_item.acc_quality_id,
                status=1 
            )

            for row in rows:
                row.program_type = program_type 
                row.product_pieces = product_pieces
                row.is_active = is_active
                row.updated_by = user_id
                row.updated_on = datetime.now()

                # Update size-wise quantity dynamically
                field_name = f"size_{row.position}"  # size_1, size_2...
                qty = request.POST.get(field_name)
                if qty not in (None, ""):
                    row.quantity = qty

                row.save()

            return JsonResponse({'message': 'success'})

        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


# @csrf_exempt
# def acc_ratio_update(request):
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         edit_id = request.POST.get('edit_tx_id')

#         try:
#             # Get the main record
#             sub_item = sub_accessory_program_table.objects.filter(id=edit_id, status=1).first()
#             if not sub_item:
#                 return JsonResponse({'message': 'error', 'error_message': 'Record not found'})

#             # Update base fields (common for all rows)
#             program_type = request.POST.get('program_type')
#             product_pieces = request.POST.get('product_pieces')
#             is_active = request.POST.get('is_active')
#             edit_tm_id = request.POST.get('edit_tm_id')
#             edit_acc_size_id = request.POST.get('edit_acc_size_id')
#             edit_acc_quality_id = request.POST.get('edit_acc_quality_id')
#             edit_item_id = request.POST.get('edit_item_id')
#             edit_item_group_id = request.POST.get('edit_item_group_id')

#             # Update all rows that belong to this program combination
#             base_qs = sub_accessory_program_table.objects.filter(
#                 id=edit_id,
#                 tm_id=edit_tm_id,
#                 acc_size_id=edit_acc_size_id,
#                 item_id=edit_item_id,
#                 item_group_id=edit_item_group_id, 
#                 acc_quality_id=edit_acc_quality_id,
#                 status=1
#             )

#             for row in base_qs:
#                 row.program_type = program_type
#                 row.product_pieces = product_pieces
#                 row.is_active = is_active
#                 row.updated_by = user_id
#                 row.updated_on = datetime.now()

#                 # Update quantity if value passed from form
#                 field_name = f"size_{row.position}"   # ex: size_1, size_2
#                 qty = request.POST.get(field_name)
#                 if qty is not None and qty != "":
#                     row.quantity = qty

#                 row.save()

#             return JsonResponse({'message': 'success'})

#         except Exception as e:
#             return JsonResponse({'message': 'error', 'error_message': str(e)})

#     return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



# @csrf_exempt
# def edit_acc_ratio_settings(request):
#     if request.method == 'POST':
#         tx_id = request.POST.get('id')

#         try:
#             sub_item = sub_accessory_program_table.objects.filter(id=tx_id, status=1).first()
#             if not sub_item:
#                 return JsonResponse({'error': 'Record not found'}, status=404)

#             # Prepare response
#             data = {
#                 'id': sub_item.id,
#                 'tm_id': sub_item.tm_id,
#                 'acc_size_id': sub_item.acc_size_id,
#                 'acc_size_name':accessory_size_table.objects.filter(status=1,id=sub_item.acc_size_id),
#                 'program_type': sub_item.program_type,
#                 'product_pieces': sub_item.product_pieces,
#                 'item_id': sub_item.item_id,
#                 'item_name':item_table.objects.filter(status=1,id=sub_item.item_id),
#                 'item_group_id': sub_item.item_group_id,
#                 'item_group_name':item_group_table.objects.filter(status=1,id=sub_item.item_group_id),
#                 'acc_quality_id': sub_item.acc_quality_id,
#                 'acc_quality':accessory_quality_table.objects.filter(status=1,id=sub_item.acc_quality_id),
#                 'is_active': sub_item.is_active,
#             }

#             # Include size_1 ... size_8 (by position)
#             for pos in range(1, 12):
#                 row = sub_accessory_program_table.objects.filter(
#                     tm_id=sub_item.tm_id,
#                     acc_size_id=sub_item.acc_size_id,
#                     acc_size_name = acc_size_name,
#                     program_type=sub_item.program_type,
#                     item_id=sub_item.item_id,
#                     item_name=item_name,
#                     item_group_id=sub_item.item_group_id,
#                     item_group_name=item_group_name,
#                     acc_quality_id=sub_item.acc_quality_id,
#                     acc_quality_name=acc_quality_name,

#                     position=pos,
#                     status=1
#                 ).first()
#                 data[f'size_{pos}'] = row.quantity if row else 0

#             return JsonResponse(data, status=200)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request'}, status=400)


def tm_acc_ratio_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            accessory_program_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_accessory_program_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except accessory_program_table  & sub_accessory_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})



def tx_acc_ratio_delete(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        acc_size_id = request.POST.get('acc_size_id')
        program_type = request.POST.get('program_type')
        item_id = request.POST.get('item_id')
        item_group_id = request.POST.get('item_group_id')
        quality_id = request.POST.get('quality_id')
        print(f"tm_id: {tm_id}, acc_size_id: {acc_size_id},pg_type: {program_type},{item_id},{item_group_id},{quality_id}")  # Debugging
        
        try:
            # Update the status field instead of deleting
            sub_accessory_program_table.objects.filter(tm_id=tm_id,item_id=item_id,item_group_id=item_group_id,acc_quality_id=quality_id, acc_size_id=acc_size_id,program_type=program_type).update(status=0, is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_accessory_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


   # 'action': f'<button type="button" class="btn btn-primary btn-xs edit-btn" data-id="{item["id"]}" data-position="{item["position"]}" data-quantity="{item["quantity"]}" data-toggle="modal" data-target="#editQuantityModal"><i class="feather icon-edit"></i></button>'

                    # 'action': f'<button type="button" class="btn btn-primary btn-xs edit-btn" data-id="{item["id"]}"><i class="feather icon-edit"></i></button>'

                    # 'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
                   
# 'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
# 'action': f'<button type="button" class="btn btn-primary btn-xs edit-btn" data-id="{item["id"]}"><i class="feather icon-edit"></i></button>'


def update_quantity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.POST.get('updatedData'))
            row_id = data.get("id")
            update_fields = {}

            for key, value in data.items():
                if key.startswith("size_") and value.isdigit():  # Only update size columns
                    position = int(key.split("_")[1])
                    update_fields["position"] = position
                    update_fields["quantity"] = int(value)

            sub_accessory_program_table.objects.filter(id=row_id).update(**update_fields)

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})




def update_acc_ratio_view_bk(request):
    tm_id = request.POST.get('tm_id')

    if not tm_id:
        return JsonResponse({'error': 'Invalid TM ID'})

    # Fetch child data
    child_qs = sub_accessory_program_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')

    if child_qs.exists():
        parent_data = accessory_program_table.objects.filter(id=tm_id).first()
        total_quantity = parent_data.total_quantity if parent_data else 0

        child_data = list(child_qs.values())

        formatted_data = []
        grouped_data = defaultdict(lambda: {
            'action': '',
            'table_id': None,
            'id': None,
            'product_pieces': None,
            'tm_id': tm_id,
            'position': None,
            'size': None,
            'acc_size': None,
            'item': None,
            'group': None,
            'acc_quality': None,
            'quantity': None,
            'status': None,
            'size_columns': {f'size_{i}': '-' for i in range(1, 9)}
        })

        for index, item in enumerate(child_data):  
            acc_size_id = item['acc_size_id']
            size_id = item['size_id']

            key = f"{acc_size_id}-{size_id}"  # Unique key to group by accessory size and size
            row = grouped_data[key]
            print('size-row:',row)

            if row['id'] is None:  # Populate row only once
                row.update({
                    'table_id': index + 1,
                    'id': item['id'],
                    'product_pieces': item['product_pieces'],
                    'position': item['position'],
                    'size': getSupplier(size_table, size_id),
                    'acc_size': getSupplier(accessory_size_table, acc_size_id),
                    'item': getSupplier(item_table, item['item_id']),
                    'group': getSupplier(item_group_table, item['item_group_id']),
                    'acc_quality': getSupplier(accessory_quality_table, item['acc_quality_id']),
                    'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
                    'action': f'<button type="button" onclick="cut_prg_edit(\'{item["id"]}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                                <button type="button" onclick="tx_cutting_prg_delete(\'{item["tm_id"]}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2\"></i></button>'
                })

            # Assign quantity to size column
            position = item['position']
            if position and 1 <= position <= 8:
                row['size_columns'][f'size_{position}'] = item['quantity']

        # Convert grouped data into final format
        for row in grouped_data.values():
            row.update(row.pop('size_columns'))
            formatted_data.append(row)

        return JsonResponse({'data': formatted_data, 'total_quantity': total_quantity})

    return JsonResponse({'error': 'No cutting program data found for this TM ID'})



def getSizePosition(tbl, supplier_id):
    try:
        party = tbl.objects.get(id=supplier_id).position
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party




def tx_acc_ratio_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = sub_accessory_program_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  


def update_size(request):
    if request.method == 'POST':
        try:
            # Get data from the request
            user_id = request.session.get('user_id')
            tm_id = request.POST.get('tm_id')  # The ID of the item being updated
            acc_size_id = request.POST.get('acc_size_id')  # The accessory size ID
            position = int(request.POST.get('size'))  # The position (1, 2, 3, etc.)
            value = request.POST.get('value')  # The new value for the size

            print(f"tm_id: {tm_id}, acc_size_id: {acc_size_id}, position: {position}, value: {value}")  # For debugging

            # Validate the input
            if not tm_id or not acc_size_id or not position or not value:
                return JsonResponse({'success': False, 'error': 'Missing required data.'})

            # Make sure position is valid (1-8) 
            if position < 1 or position > 8:
                return JsonResponse({'success': False, 'error': 'Invalid size position.'})

            # Your logic to update the database here...
            try:
                acc = sub_accessory_program_table.objects.get(tm_id=tm_id, acc_size_id=acc_size_id, position=position)
            except sub_accessory_program_table.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Accessory not found for the given parameters.'})

            # Update the record with the new value
            acc.quantity = value
            acc.is_active = 1
            acc.updated_by = user_id
            acc.updated_on = datetime.now()
            acc.save()

            # Return success message
            return JsonResponse({'success': True, 'message': 'Size updated successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
