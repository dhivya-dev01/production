

from os import stat
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from purchase_app.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
from purchase_app.forms import *
import datetime

from datetime import datetime
from datetime import date
from django.utils import timezone

from django.db.models import Count


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from purchase_app.models import *

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
from user_auth.models import *
from common.models import *
from user_roles.models import *
from yarn.models import *
from company.models import *
from grey_fabric.models import *
from program_app.models import *
from django.db.models import Count



 




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


# ``````````````````````````````````````````````````````````````````````

# Create your views here. 
def purchase_order_list(request): 
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        print('user-id:',user_id)
        supplier = party_table.objects.filter(is_knitting=1) 
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)  
        count = count_table.objects.filter(status=1).order_by('id')
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        
        return render(request,'gcf/purchase_order_list.html',{'supplier':supplier,'party':party,'product':product,'count':count,'gauge':gauge,'tex':tex})
    else:
        return HttpResponseRedirect("/admin")
    

def purchase_order_gcf(request): 
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        print('user-id:',user_id)
        supplier = party_table.objects.filter(is_process=1) 
        party = party_table.objects.filter(status=1)
        # party = party_table.objects.filter(status=1,is_bleaching=1,is_dyeing=1)
        product = product_table.objects.filter(status=1)  
        count = count_table.objects.filter(status=1).order_by('id')
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
         # Get the last ID from parent_po_table and increment by 1
        last_purchase = parent_po_table.objects.order_by('-id').first()
        if last_purchase:
            purchase_number = last_purchase.id + 1
        else:
            purchase_number = 1  # Default if no records exist
        
        return render(request,'gcf/add_purchase_order.html',{'supplier':supplier,'party':party,'product':product,'count':count,'gauge':gauge,'tex':tex,'purchase_number':purchase_number})
    else:
        return HttpResponseRedirect("/admin")





def purchase_order_view(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(gcf_po_table.objects.filter(status=1).order_by('-id').values()) 

    formatted = [
        {
            'action': '<button type="button" onclick="gcf_po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="gcf_po_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'po_date': item['purchase_date'] if item['purchase_date'] else'-', 
            'supplier_id':getSupplier(party_table, item['supplier_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'tax_total': item['tax_total'] if item['tax_total'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 


def getSupplier(tbl, supplier_id):
    try:
        party = tbl.objects.get(id=supplier_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party






def get_do_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST: 
        supplier_id = request.POST['supplier_id']
        print('supplier_id:', supplier_id) 

        if supplier_id:
            # Fetch all child purchase orders for the given supplier_id where is_assigned=0
            child_orders = sub_knitting_deliver_table.objects.filter(
                tm_po_id__in=knitting_deliver_table.objects.filter(supplier_id=supplier_id,status=1).values('id'),
               
            ).values('tm_po_id')  # Get the IDs of the parent orders

            # Now filter parent purchase orders based on these IDs
            order_number = knitting_deliver_table.objects.filter( 
                id__in=child_orders 
            ).values('id', 'do_number').order_by('-id')

            
            # Convert the queryset to a list
            data = list(order_number)
            # print('PO Numbers:', data)
            return JsonResponse(data, safe=False)  # Return the list of purchase orders
         
    return JsonResponse([], safe=False) 



@csrf_exempt
def add_purchase_order(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        if not user_id or not company_id:
            return JsonResponse({'status': 'Failed', 'message': 'User or company information missing.'}, status=400)

        try:
            # Extracting data from the request
            po_date = request.POST.get('purchase_date')
            do_date = request.POST.get('delivery_date')
            supplier_id = request.POST.get('supplier_id')
            remarks = request.POST.get('remarks') 
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            delivery_data = json.loads(request.POST.get('delivery_data', '[]'))
            print('delivery-data:',delivery_data)
            print('chemical-data:',chemical_data)
            # Validate essential fields
            if not po_date or not supplier_id or not chemical_data:
                return JsonResponse({'status': 'Failed', 'message': 'Missing essential purchase order information.'}, status=400)

            # Create a new parent_po_table instance
            material_request = gcf_po_table.objects.create(
                purchase_date=po_date, 
                supplier_id=supplier_id,
                company_id=company_id,
                total_quantity=request.POST.get('total_quantity'),
                total_amount=request.POST.get('sub_total'),
                round_off=request.POST.get('round_off'),
                tax_total=request.POST.get('tax_total'),
                grand_total=request.POST.get('total_payable'),
                remarks=remarks,
                price_list=request.POST.get('price_list'),
                is_active=1,
                status=1,
                created_by=user_id,
                updated_by=user_id,
                created_on=timezone.now(),  
                updated_on=timezone.now() 
            )

            # Iterate through chemical_data and create sub_po_table entries
            for chemical in chemical_data:
                product_id = chemical.get('product_id')
                quantity = chemical.get('quantity')
                rolls = int(chemical.get('rolls', 0))  # Convert rolls to an integer
                print('deivery-rolls:',rolls)

                if product_id and quantity and quantity != 'undefined':
                    sub_gcf_po_table.objects.create(
                        tm_po_id=material_request.id,
                        product_id=product_id,
                        count=chemical.get('count_id'), 
                        gauge=chemical.get('gauge_id'),
                        tex=chemical.get('tex_id'),
                        dia=chemical.get('dia'),  
                        rolls=chemical.get('rolls'),
                        wt_per_roll=chemical.get('wt_per_roll'),
                        rate=chemical.get('rate'),
                        quantity=chemical.get('quantity'),
                        total_amount=chemical.get('total_amount'),
                        is_active=1,
                        status=1,
                        created_by=user_id,
                        updated_by=user_id,
                        created_on=timezone.now(),
                        updated_on=timezone.now()
                    )
                else:
                    print('Invalid chemical entry:', chemical)
 
            for contact in delivery_data: 
                company_name = contact.get('company_name')
                knitting = contact.get('knitting_id')
                fabric_id = contact.get('fabric_id')
                delivery_date = contact.get('delivery_date')
                # wt_per_roll = contact.get('wt_per_roll')
                # total_amount = contact.get('total_amount')
                
                try:
                    delivered_rolls = int(contact.get('rolls', 0))  # Convert to integer
                except ValueError:
                    delivered_rolls = 0  # Default to 0 if conversion fails

                if company_name and knitting and delivery_date and delivered_rolls:
                    gcf_delivery_table.objects.create(
                        tm_po_id=material_request.id,
                        company_name=company_name, 
                        knitting_id=knitting,
                        fabric_id=fabric_id,
                        delivery_date=delivery_date,
                        rolls=delivered_rolls,
                        wt_per_roll=0,
                        total_amount=0,
                        is_active=1,
                        status=1,
                        created_by=user_id,
                        updated_by=user_id,
                        created_on=timezone.now(),
                        updated_on=timezone.now()
                    )
                else:
                    print('Invalid delivery entry:', contact)

          
          
            for chemical in chemical_data:
                fabric_id = chemical.get('fabric_id') or chemical.get('product_id')  # Try both keys
                  # ✅ Use 'chemical' instead of 'contact'
                print('Checking balance for fabric_id:', fabric_id)

                try:
                    required_rolls = int(chemical.get('rolls', 0))  # Convert to integer
                except ValueError:
                    required_rolls = 0  # Default to 0 if conversion fails

                # Get total delivered rolls for this specific fabric_id
                total_delivered_rolls = gcf_delivery_table.objects.filter(
                    tm_po_id=material_request.id,
                    fabric_id=fabric_id,  # ✅ Corrected to 'fabric_id'
                    is_active=1
                ).aggregate(total_rolls=models.Sum('rolls'))['total_rolls'] or 0

                print('delivered-roll:', total_delivered_rolls)

                # Calculate balance rolls
                if total_delivered_rolls < required_rolls:
                    balance_rolls = required_rolls - total_delivered_rolls
                    print('balance-roll:', balance_rolls) 


                    # Insert missing rolls with knitting = 0 
                    gcf_delivery_table.objects.create( 
                        tm_po_id=material_request.id, 
                        company_name='Mirra', 
                        knitting_id=0,  # Mark as pending 
                        delivery_date=date.today(),  # Use 'do_date' or fetch a relevant date
                        rolls=balance_rolls,
                        wt_per_roll=0,
                        total_amount=0,
                        fabric_id=fabric_id,  # ✅ Corrected
                        is_active=1, 
                        status=1,
                        created_by=user_id,
                        updated_by=user_id,
                        created_on=timezone.now(),
                        updated_on=timezone.now()
                    )
                    print(f"Added missing {balance_rolls} rolls for fabric_id {fabric_id}")

          

            return JsonResponse({'status': 'Success', 'message': 'Purchase order and delivery data saved successfully.'})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'Failed', 'message': 'An error occurred while processing the request.'}, status=500)

    return render(request, 'gf/add_purchase_order.html')





def gcf_po_details_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'gcf/update_purchase_order.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'gcf/update_purchase_order.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_gcf_po_table.objects.filter(tm_po_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            product_id = request.POST.get('product_id')  # Adjust as per your input structure
            bag = request.POST.get('bag')  # Adjust as per your input structure
            per_bag = request.POST.get('per_bag')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            rate = request.POST.get('rate')  # Adjust as per your input structure
            amount = request.POST.get('amount')  # Adjust as per your input structure

            # Ensure valid data before saving
            if product_id and bag and quantity: 
                material_instance = sub_gcf_po_table.objects.create(
                    tm_po_id=material_id,
                    product_id=product_id,
                    bag=bag,
                    per_bag=per_bag,
                    rate=rate,
                    quantity=quantity,
                    amount=amount,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'gcf/update_purchase_order.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = gcf_po_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'gcf/update_purchase_order.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.supplier_id:
            try:
                supplier = party_table.objects.get(id=parent_stock_instance.supplier_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        product = product_table.objects.filter(status=1)
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_knitting=1,status=1)
        count = count_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'product': product,
            'party': party,
            'supplier_id': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'count':count,
            'gauge':gauge,
            'tex':tex
        }
        return render(request, 'gcf/update_purchase_order.html', context)

    except Exception as e:
        return render(request, 'gcf/update_purchase_order.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



def gcf_po_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting
            gcf_po_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_gcf_po_table.objects.filter(tm_po_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except gcf_po_table  & sub_gcf_po_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




def update_gcf_po_view(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data
                child_data = sub_gcf_po_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = gcf_po_table.objects.filter(id=master_id).first()
                    if parent_data:
                        tax_total = parent_data.tax_total or 0 
                        round_off = parent_data.round_off or 0
                        grand_total = total_amount + tax_total + round_off
                    else:
                        tax_total = round_off = grand_total = 0

                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0
                    for item in data:  
                        index += 1 
                        formatted_data.append({
                            'action': '<button type="button" onclick="gcf_purchase_order_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="gcf_purchase_order_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'product': getItemNameById(product_table, item['product_id']),
                            'count': item['count'] if item['count'] else '-',
                            'gauge': item['gauge'] if item['gauge'] else '-', 
                            'tex': item['tex'] if item['tex'] else '-',
                            'dia': item['dia'] if item['dia'] else '-',
                            'rolls': item['rolls'] if item['rolls'] else '-',
                            'wt_per_roll': item['wt_per_roll'] if item['wt_per_roll'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'rate': item['rate'] if item['rate'] else '-',
                            'total_amount': item['total_amount'] if item['total_amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                        'tax_total': tax_total,
                        'round_off': round_off,
                        'grand_total': grand_total
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})

 

def getItemNameById(tbl, product_id):
    try:
        party = tbl.objects.get(id=product_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party





def update_tm_table_totals(master_id):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = sub_gcf_po_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
 
        # total_amount = tx.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')



        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
        total_amount = tx.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        print('total-amount:',total_amount)
        # Convert tax rate to Decimal and perform multiplication safely
        tax_rate = Decimal('0.05')  # 5% tax
        tax_total = (total_amount * tax_rate).quantize(Decimal('0.01'))  # Ensure 2 decimal places

        # Calculate raw total before rounding
        raw_total = total_amount + tax_total

        # Compute round_off and grand_total
        rounded_total = Decimal(round(raw_total))  # Ensure Decimal type
        round_off = (rounded_total - raw_total).quantize(Decimal('0.01'))  # Ensure 2 decimal places
        grand_total = rounded_total  # Final rounded total

        # Update values in parent_po_table
        gcf_po_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            total_amount=total_amount.quantize(Decimal('0.01')),
            tax_total=tax_total,
            round_off=round_off,
            grand_total=grand_total
        )

        # Return updated values for frontend update
        return {
            'total_quantity': total_quantity,
            'total_amount': total_amount.quantize(Decimal('0.01')),
            'tax_total': tax_total,
            'round_off': round_off,
            'grand_total': grand_total
        }

    except Exception as e:
        return {'error': str(e)}


def add_or_update_gcf_po_item(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        product_id = request.POST.get('product_id')
        count_id = request.POST.get('count_id')
        gauge_id = request.POST.get('gauge_id')
        tex_id = request.POST.get('tex_id')
        dia = request.POST.get('dia')
        rolls = request.POST.get('rolls')
        wt_per_roll = request.POST.get('wt_per_roll')
        quantity = request.POST.get('quantity')
        rate = request.POST.get('rate')
        total_amount = request.POST.get('total_amount')

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Add or update the child table record
            child_item, created = sub_gcf_po_table.objects.update_or_create(
                tm_po_id=master_id, product_id=product_id,
                defaults={
                    'count_id': count_id,
                    'gauge_id': gauge_id,
                    'tex_id':tex_id,
                    'dia':dia,
                    'rolls':rolls,
                    'wt_per_roll':wt_per_roll,
                    'quantity': quantity,
                    'rate': rate,
                    'total_amount': total_amount,
                    'status': 1,
                    'is_active': 1
                }
            )

            # Update `tm_table` with new totals
            updated_totals = update_tm_table_totals(master_id)

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})





def gcf_po_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_gcf_po_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_gcf_po_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


 
def gcf_po_detail_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_gcf_po_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])

 


# ```````````````````````````````````` Grey Colored Fabric INWARD ````````````````````````````````````






def grey_colored_fabric_inward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(status=1,is_process=1)
        party = party_table.objects.filter(status=1)
        product = fabric_program_table.objects.filter(status=1) 
        count = count_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1) 
        tex = tex_table.objects.filter(status=1)
        last_purchase = gf_inward_table.objects.order_by('-id').first() 
        if last_purchase:
            inward_number = last_purchase.id + 1
        else:
            inward_number = 1   # Default if no records exist 
       
        delivers = parent_gf_delivery_table.objects.filter(status=1,is_inward=0)
        purchase = knitting_table.objects.filter(status=1)
      

 
        for deliver in delivers: 
            print(deliver.id)  # ✅ Safe because we are iterating
            gf_delivery = child_gf_delivery_table.objects.filter(tm_id=deliver.id,status=1)


        # print('combined_prg:',combined_prg)
        dye_prg = dyeing_program_table.objects.filter(status=1)
        return render(request,'gcf/add_inward.html',{'supplier':supplier,'party':party,'product':product,'count':count,'color':color,
                                                        'dye_prg':dye_prg,'gf_delivery':gf_delivery,'inward_number':inward_number,'gauge':gauge,'tex':tex,'purchase':purchase})
    else:
        return HttpResponseRedirect("/admin")




@csrf_exempt
def get_gf_do_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('deliver-id:', supplier_id) 

        if supplier_id:
            # Get child orders where remaining_bag > 0 or remaining_quantity > 0
            child_orders = child_gf_delivery_table.objects.filter(
                tm_id__in=parent_gf_delivery_table.objects.filter(deliver_to=supplier_id, status=1).values('id'),
            ).filter(
                Q(rolls__gt=0) | Q(quantity__gt=0)
            ).values('tm_id').distinct()

            # Now filter parent orders based on these child IDs 
            order_numbers = parent_gf_delivery_table.objects.filter(
                id__in=child_orders, status=1
            ).values('id', 'do_number', 'lot_no','prg_id').order_by('-id')

            # Calculate total bags and total quantity only for relevant child orders
            total_bag_sum = 0
            total_quantity_sum = 0
            for order in order_numbers:
                # Only get child orders where remaining_bag or remaining_quantity > 0
                child_order = child_gf_delivery_table.objects.filter(
                    tm_id=order['id']
                ).filter(
                    Q(rolls__gt=0) | Q(quantity__gt=0)
                )
                
                for child in child_order:
                    total_bag_sum += child.rolls
                    total_quantity_sum += child.quantity

            # Convert the queryset to a list
            data = list(order_numbers)
            
            return JsonResponse({
                'orders': data,
                'total_bag': total_bag_sum,
                'total_quantity': total_quantity_sum
            }, safe=False)

    return JsonResponse([], safe=False)





@csrf_exempt
def get_gf_delivery_lists(request):
    if request.method == 'POST' and 'do_id' in request.POST:
        do_id = request.POST['do_id']
        dos = request.POST.getlist('do_id')  # Get the list of do_id values
        print('dos:',dos)
        print('Selected DO ID:', do_id)

        if do_id:
            # Check if the DO exists
            do = parent_gf_delivery_table.objects.filter(id=do_id, status=1).first()
            if not do:
                return JsonResponse({'error': 'DO not found'}, status=404)
            
            do_prg = do.prg_id
            do_id = do.id

            deliveries = dyeing_program_table.objects.filter(tm_id=do_prg).values(
                # 'count', 
                # 'fabric_id', 
                # 'gauge', 
                # 'tex', 
                # 'dia', 
                # 'gsm',  
                # 'rolls',
                # 'wt_per_roll',
                # 'quantity',
                # 'rate', 
                # 'total_amount', 
                # 'id',
                
                'tm_id',
                'fabric_id',
                'color_id',
                'dia_id',
                'rolls',
                'wt_per_roll',
                'id'
            )

            # Manually lookup yarn_count using yarn_count_id
            for delivery in deliveries:
                # yarn_count_id = delivery['count']
                fabric_id = delivery['fabric_id']
                color_id = delivery['color_id']
                dia_id = delivery['dia_id']



                fabric = fabric_program_table.objects.filter(id=fabric_id).first()  # Get yarn_count from the count_table
                color = color_table.objects.filter(id=color_id).first()  # Get yarn_count from the count_table

                dia = dia_table.objects.filter(id=dia_id).first()  # Get yarn_count from the count_table
                
                
                delivery['fabric'] = fabric.name  # Assuming 'name' is the correct field in count_table
                delivery['color'] = color.name  # Assuming 'name' is the correct field in count_table
                delivery['dia_name'] = dia.name  # Assuming 'name' is the correct field in count_table
              
              
            return JsonResponse({
                'deliveries': list(deliveries), 
                'prg_id': do_prg,
                'do_id':do_id
            }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)






def get_lot_product_id(request):
    if request.method == 'POST': 
        lot_id = request.POST.get('lot_no')

        if not lot_id:
            return JsonResponse({'error': 'Lot No. is required'}, status=400)

        try:
            # Retrieve first matching sub_knitting_table record
            knitting = sub_knitting_table.objects.filter(tm_id=lot_id).first()

            if knitting:  # Ensure knitting is not None
                product = get_object_or_404(fabric_program_table, id=knitting.fabric_id)
                
                response_data = {
                    'product': {'id': product.id, 'name': product.name},
                }
            else:
                response_data = {'error': 'No matching fabric found'}

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_gf_po_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('supplier_id:', supplier_id) 

        if supplier_id:
            # Fetch all child purchase orders for the given supplier_id where is_assigned=0
            child_orders = sub_gf_po_table.objects.filter(
                tm_po_id__in=gf_po_table.objects.filter(supplier_id=supplier_id,status=1,is_complete=0).values('id'),
               
            ).values('tm_po_id')  # Get the IDs of the parent orders

            # Now filter parent purchase orders based on these IDs
            order_number = gf_po_table.objects.filter( 
                id__in=child_orders 
            ).values('id', 'po_number').order_by('-id')

            
            # Convert the queryset to a list
            data = list(order_number)
            # print('PO Numbers:', data)
            return JsonResponse(data, safe=False)  # Return the list of purchase orders
         
    return JsonResponse([], safe=False) 


def load_gf_po_details(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')  # Accept multiple PO IDs
        print('po-id:', po_ids)

        if not supplier_id or not po_ids:
            return JsonResponse({'error': 'Supplier ID and Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided supplier and PO IDs
            parent_pos = gf_po_table.objects.filter(id__in=po_ids, supplier_id=supplier_id)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                # Retrieve child orders linked to each parent PO
                orders = sub_gf_po_table.objects.filter(tm_po_id=po.id)

                for order in orders:
                    product = product_table.objects.filter(id=order.product_id).first()
                    count = count_table.objects.filter(id=order.count).first()
                    gauge = gauge_table.objects.filter(id=order.gauge).first()
                    tex = tex_table.objects.filter(id=order.tex).first()

                    # Get remaining values
                    # remaining_bag = order.remaining_bag or 0
                    # remaining_quantity = order.remaining_quantity or 0
                    # remaining_amount = order.remaining_amount or 0

                    # 🔹 **Omit entries where all three values are zero**
                    # if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
                    #     continue  # Skip this record

                    # Prepare order details
                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "Unknown Product", 
                        'tax_value': 5,  
                        'count_id':order.count,
                        'gauge_id':order.gauge,
                        'tex_id':order.tex,
                        'dia':order.dia,
                        'rolls':order.rolls,
                        'wt_per_roll':order.wt_per_roll,
                        'price':order.rate,
                        'quantity':order.quantity,
                        'total_amount':order.total_amount,
                        'count':count.count if count else "Unknown count", 
                        'gauge':gauge.name if gauge else "Unknown gauge", 
                        'tex':tex.name if tex else "Unknown tex", 
                        'id': order.id,
                        'tm_id': order.tm_po_id,
                        'tx_id': order.id,
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)




# @csrf_exempt
# def add_gcf_inward(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')  # Prevent KeyErrors
#         company_id = request.session.get('company_id')

#         try:
#             # Extracting Data from Request  
#             supplier_id = request.POST.get('supplier_id',0)
#             through_id = request.POST.get('order_through_id',0)
#             remarks = request.POST.get('remarks')
#             lot_id = request.POST.get('lot_no')
#             inward_date = request.POST.get('inward_date')
#             chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

#             print('Chemical Data:', chemical_data)
#             lot = knitting_table.objects.filter(id=lot_id).first()
#             lot_no = lot.lot_no
#             # Create Parent Entry (gf_inward_table)
#             material_request = gcf_inward_table.objects.create(
#                 inward_date=inward_date, 
#                 supplier_id=0,
#                 order_through_id=through_id,
#                 lot_no=lot_no,
#                 company_id=company_id,
#                 total_quantity=request.POST.get('total_quantity'),
#                 total_amount=request.POST.get('sub_total'),
#                 tax_total=request.POST.get('tax_total'),
#                 grand_total=request.POST.get('total_payable'), 
#                 remarks=remarks, 
#                 created_by=user_id,
#                 created_on=timezone.now()
#             )

#             # po_ids = set()  # Store unique PO IDs to update later

#             # Create Sub Table Entries
#             for chemical in chemical_data:
#                 print("Processing Chemical Data:", chemical)
 
#                 # po_id = chemical.get('tm_id')  # Get PO ID
#                 # po_ids.add(po_id)  # Store for updating later
#                 color_ids = request.POST.getlist('color_id')  # Get multiple IDs as a list
#                 color_id_str = ",".join(color_ids)  # Convert to "1,2,3"

#                 # I

#                 sub_entry = sub_gcf_inward_table.objects.create(
#                     tm_id=material_request.id,  
#                     product_id=chemical.get('product_id'),
#                     po_id=0,#chemical.get('tm_po_id'),
#                     lot_no = chemical.get('lot_no'),
#                     count=chemical.get('count_id'),
#                     gauge=chemical.get('gauge_id'),
#                     color_id=color_id_str,
#                     tex=chemical.get('tex_id'),
#                     gsm=chemical.get('gsm'), 
#                     dia=chemical.get('dia'), 
#                     rolls=chemical.get('rolls'),
#                     wt_per_roll=chemical.get('wt_per_roll'), 
#                     quantity=chemical.get('quantity'),
#                     rate=chemical.get('rate'), 
#                     total_amount=chemical.get('total_amount'),
#                     created_by=user_id, 
#                     created_on=timezone.now()
#                 )


#                 print("Sub Table Entry Created:", sub_entry) 
 
#             # #  Update `is_completed=1` for the associated PO IDs
#             # prg = chemical.get('tm_id')
#             # update_knitting = parent_gf_delivery_table.objects.filter(id__in=prg).update(is_inward=1)
#             # # updated_count = gf_po_table.objects.filter(id__in=po_ids).update(is_inward=1)
#             # print(f" Updated {update_knitting} Purchase Inward as completed.")

#             # Return a success response
#             return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

#         except Exception as e:
#             print(f" Error: {e}")  # Log error
#             return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

#     return render(request, 'gcf/add_inward.html')


@csrf_exempt
def add_gcf_inward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  
        company_id = request.session.get('company_id')

        try:
            supplier_id = request.POST.get('supplier_id', 0)
            through_id = request.POST.get('order_through_id', 0)
            remarks = request.POST.get('remarks')
            lot_id = request.POST.get('lot_no')
            inward_date = request.POST.get('inward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))  # Convert JSON to list

            print('Chemical Data:', chemical_data)
            lot = knitting_table.objects.filter(id=lot_id).first()
            lot_no = lot.lot_no if lot else None

            if not lot_no:
                return JsonResponse({'status': 'no', 'message': 'Invalid lot number'}, safe=False)

            # Create Parent Entry
            material_request = gcf_inward_table.objects.create(
                inward_date=inward_date,
                supplier_id=supplier_id,
                order_through_id=through_id,
                lot_no=lot_no,
                company_id=company_id,
                total_quantity=request.POST.get('total_quantity'),
                total_amount=request.POST.get('sub_total'),
                tax_total=request.POST.get('tax_total'),
                grand_total=request.POST.get('total_payable'),
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            # Create Sub Table Entries
            for chemical in chemical_data:
                print("Processing Chemical Data:", chemical)

                                # Convert color_id from list to comma-separated string of integers
                # color_ids = chemical.get('color_id', [])

                # print('color:', color_ids)

                # # ✅ Ensure color_id is always handled as a list
                # if isinstance(color_ids, list):  
                #     color_ids = [str(c) for c in color_ids if isinstance(c, ( str)) and str(c).isdigit()]  # Convert to string list
                # elif isinstance(color_ids, str):  
                #     color_ids = [c.strip() for c in color_ids.split(',') if c.strip().isdigit()]  

                # color_id_str = ",".join(color_ids) if color_ids else None  # Store properly formatted string
                # Convert color_id from list to comma-separated string of integers
                # Ensure color_id is treated as a string before saving
                color_ids = chemical.get('color_id', []) 

                print('Raw color_id:', color_ids)

                if isinstance(color_ids, list):  
                    color_id_str = ",".join(map(str, color_ids))  # Convert list [1, 2] -> "1,2"
                elif isinstance(color_ids, str):  
                    color_id_str = color_ids  # Already a string, use it directly
                else:
                    color_id_str = ""  # Default empty if invalid

                print("Final color_id stored:", color_id_str)

                sub_entry = sub_gcf_inward_table.objects.create(
                    tm_id=material_request.id,
                    product_id=chemical.get('product_id'),
                    po_id=0,
                    lot_no=chemical.get('lot_no'),
                    count=chemical.get('count_id'),
                    gauge=chemical.get('gauge_id'),
                    color_id= color_id_str,  # ✅ Ensure correct format
                    tex=chemical.get('tex_id'),
                    gsm=chemical.get('gsm'),
                    dia=chemical.get('dia'),
                    rolls=chemical.get('rolls'),
                    wt_per_roll=chemical.get('wt_per_roll'),
                    quantity=chemical.get('quantity'),
                    rate=chemical.get('rate'),
                    total_amount=chemical.get('total_amount'),
                    created_by=user_id,
                    created_on=timezone.now()
                )


    

                print("Sub Table Entry Created:", sub_entry)

            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f"Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'gcf/add_inward.html')



@csrf_exempt
def add_gcf_inward_bk_26_02_2025(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try:
            # Extracting Data from Request  
            supplier_id = request.POST.get('supplier_id', 0)
            through_id = request.POST.get('order_through_id', 0)
            remarks = request.POST.get('remarks')
            lot_id = request.POST.get('lot_no')
            inward_date = request.POST.get('inward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            print('Chemical Data:', chemical_data)
            lot = knitting_table.objects.filter(id=lot_id).first()
            lot_no = lot.lot_no if lot else None

            if not lot_no:
                return JsonResponse({'status': 'no', 'message': 'Invalid lot number'}, safe=False)

            # Create Parent Entry (gf_inward_table)
            material_request = gcf_inward_table.objects.create(
                inward_date=inward_date, 
                supplier_id=supplier_id,
                order_through_id=through_id,
                lot_no=lot_no,
                company_id=company_id,
                total_quantity=request.POST.get('total_quantity'),
                total_amount=request.POST.get('sub_total'),
                tax_total=request.POST.get('tax_total'),
                grand_total=request.POST.get('total_payable'), 
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )

            # Create Sub Table Entries
            for chemical in chemical_data:
                print("Processing Chemical Data:", chemical)

                # Ensure `color_id` is retrieved correctly
                color_ids = chemical.get('color_id', '').split(',')  # Convert "1,2" to list
                color_ids = [c.strip() for c in color_ids if c.strip().isdigit()]  # Clean & validate
                color_id_str = ",".join(color_ids) if color_ids else None  # Convert back to string

                if not color_id_str:
                    print("Warning: No valid color_id found for chemical:", chemical)

                # Create sub-table entry
                sub_entry = sub_gcf_inward_table.objects.create(
                    tm_id=material_request.id,  
                    product_id=chemical.get('product_id'),
                    po_id=0,  # chemical.get('tm_po_id'),
                    lot_no=chemical.get('lot_no'),
                    count=chemical.get('count_id'),
                    gauge=chemical.get('gauge_id'),
                    color_id=color_id_str,
                    tex=chemical.get('tex_id'),
                    gsm=chemical.get('gsm'), 
                    dia=chemical.get('dia'), 
                    rolls=chemical.get('rolls'),
                    wt_per_roll=chemical.get('wt_per_roll'), 
                    quantity=chemical.get('quantity'),
                    rate=chemical.get('rate'), 
                    total_amount=chemical.get('total_amount'),
                    created_by=user_id, 
                    created_on=timezone.now()
                )

                print("Sub Table Entry Created:", sub_entry)

            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f"Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'gcf/add_inward.html')


def gcf_list(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'gcf/gcf_inward_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    

 

def gcf_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access: 
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(gcf_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="gcf_inward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="gcf_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="gcf_po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_no': item['inward_number'] if item['inward_number'] else'-', 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'supplier_id':getSupplier(party_table, item['supplier_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'tax_total': item['tax_total'] if item['tax_total'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 
 


def gcf_inward_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            gcf_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_gcf_inward_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except gcf_inward_table  & sub_gcf_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})



def gcf_inward_detail_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'gcf/update_gcf_inward.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'gcf/update_gcf_inward.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_gcf_inward_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            product_id = request.POST.get('product_id')  # Adjust as per your input structure
            bag = request.POST.get('bag')  # Adjust as per your input structure
            per_bag = request.POST.get('per_bag')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            rate = request.POST.get('rate')  # Adjust as per your input structure
            amount = request.POST.get('amount')  # Adjust as per your input structure

            # Ensure valid data before saving
            if product_id and bag and quantity:
                material_instance = sub_gcf_inward_table.objects.create(
                    tm_id=material_id,
                    product_id=product_id,
                    bag=bag,
                    per_bag=per_bag,
                    rate=rate,
                    quantity=quantity,
                    amount=amount,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'gcf/update_gcf_inward.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = gcf_inward_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'gcf/update_gcf_inward.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.supplier_id:
            try: 
                supplier = party_table.objects.get(id=parent_stock_instance.supplier_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        product = fabric_program_table.objects.filter(status=1)
        # supplier = party_table.objects.filter(is_dyeing=1)
        supplier = party_table.objects.filter(status=1,is_compacting=1)

        party = party_table.objects.filter(is_knitting=1,status=1)
        count = count_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        dia = fabric_dia_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance, 
            'product': product,
            'party': party,
            'supplier_id': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'count':count,
            'gauge':gauge,
            'tex':tex,
            'color':color,
            'dia':dia
        }
        return render(request, 'gcf/update_gcf_inward.html', context)

    except Exception as e:
        return render(request, 'gcf/update_gcf_inward.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


def update_gcf_inward_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_gcf_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = gcf_inward_table.objects.filter(id=master_id).first()
                    if parent_data:
                        tax_total = parent_data.tax_total or 0
                        round_off = parent_data.round_off or 0
                        grand_total = total_amount + tax_total + round_off
                    else:
                        tax_total = round_off = grand_total = 0 

                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0
                    for item in data: 
                        index += 1  
                        formatted_data.append({
                            'action': '<button type="button" onclick="gcf_inward_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="gcf_inward_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'product': getItemNameById(fabric_program_table, item['product_id']), 
                            'color': getColorItemNameById(color_table, item['color_id']), 
                            'count': getCountNameById(count_table, item['count']), 
                            'gauge': getItemNameById(gauge_table, item['gauge']), 
                            'tex': getItemNameById(tex_table, item['tex']), 
                            'dia': getDiaItemNameById(fabric_dia_table, item['dia']), 
                            'gsm': item['gsm'] if item['gsm'] else '-',
                            # 'dia': item['dia'] if item['dia'] else '-',
                            'rolls': item['rolls'] if item['rolls'] else '-',
                            'wt_per_roll': item['wt_per_roll'] if item['wt_per_roll'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'rate': item['rate'] if item['rate'] else '-',
                            'total_amount': item['total_amount'] if item['total_amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                        'tax_total': tax_total,
                        'round_off': round_off,
                        'grand_total': grand_total
                    })
                else: 
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})

def getColorItemNameById(tbl, product_ids):
    if not product_ids:
        return "-"

    # Ensure product_ids is a list
    if isinstance(product_ids, str):  
        product_ids = product_ids.split(",")  # Convert "1,2" -> ["1", "2"]

    try:
        # Fetch all names for the given IDs
        parties = tbl.objects.filter(id__in=product_ids).values_list('name', flat=True)
        return ", ".join(parties) if parties else "-"  # Join names into a single string
    except ObjectDoesNotExist:
        return "-"  # Return "-" if no records are found


 
def gcf_inward_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        print('edit-id:',item_id)
        data = sub_gcf_inward_table.objects.filter(id=item_id).values()

        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
 


def getCountNameById(tbl, product_id):
    try:
        party = tbl.objects.get(id=product_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party

def getDiaItemNameById(tbl, product_id):
    try:
        party = tbl.objects.get(id=product_id).dia
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party


def update_tm_table_totals(master_id):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = sub_gcf_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
        total_amount = tx.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # Convert tax rate to Decimal and perform multiplication safely
        tax_rate = Decimal('0.05')  # 5% tax
        tax_total = (total_amount * tax_rate).quantize(Decimal('0.01'))  # Ensure 2 decimal places

        # Calculate raw total before rounding
        raw_total = total_amount + tax_total

        # Compute round_off and grand_total
        rounded_total = Decimal(round(raw_total))  # Ensure Decimal type
        round_off = (rounded_total - raw_total).quantize(Decimal('0.01'))  # Ensure 2 decimal places
        grand_total = rounded_total  # Final rounded total

        # Update values in parent_po_table
        gcf_inward_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            total_amount=total_amount.quantize(Decimal('0.01')),
            tax_total=tax_total,
            round_off=round_off,
            grand_total=grand_total
        )

        # Return updated values for frontend update
        return {
            'total_quantity': total_quantity,
            'total_amount': total_amount.quantize(Decimal('0.01')),
            'tax_total': tax_total,
            'round_off': round_off,
            'grand_total': grand_total
        }

    except Exception as e:
        return {'error': str(e)}



from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from django.http import JsonResponse

def update_knitting(master_id):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = sub_gf_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

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
        gf_inward_table.objects.filter(id=master_id).update(
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

def add_or_update_gcf_inward_item(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')  
        po_id = request.POST.get('po_id', 0)
        product_id = request.POST.get('fabric_id')
        count = request.POST.get('count_id')
        gauge = request.POST.get('gauge_id')
        tex = request.POST.get('tex_id')  
        dia = request.POST.get('dia')
        gsm = request.POST.get('gsm')
        rolls = request.POST.get('rolls')
        wt_per_roll = request.POST.get('wt_per_roll')
        quantity = request.POST.get('quantity')
        rate = request.POST.get('rate')
        amount = request.POST.get('total_amount')
        edit_id = request.POST.get('edit_id')  
        tm_id = request.POST.get('tm_id')  

        # ✅ Fix: Get multiple selected color_ids and convert to comma-separated string
        color = request.POST.getlist('color_id')  # Get list of selected color IDs
        color = ",".join(color) if color else None  # Convert list to comma-separated string

        if not product_id:
            return JsonResponse({'success': False, 'error_message': 'Missing required data'})

        try:
            if edit_id:  # Update existing record
                child_item = sub_gcf_inward_table.objects.get(id=edit_id) 
                child_item.product_id = product_id 
                child_item.count = count
                child_item.color_id = color  # ✅ Save as comma-separated string
                child_item.gauge = gauge 
                child_item.tex = tex
                child_item.dia = dia
                child_item.po_id = po_id
                child_item.gsm = gsm
                child_item.rolls = rolls
                child_item.wt_per_roll = wt_per_roll
                child_item.quantity = quantity 
                child_item.rate = rate
                child_item.total_amount = amount
                child_item.save()
                message = "GF Inward updated successfully."
            else:  # Create new record
                child_item = sub_gcf_inward_table.objects.create( 
                    product_id=product_id,
                    tm_id=master_id, 
                    count=count, 
                    color_id=color,  # ✅ Store correctly formatted
                    gauge=gauge,
                    tex=tex, 
                    dia=dia,
                    po_id=po_id,
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

            updated_totals = update_knitting(master_id)

            return JsonResponse({'success': True, 'message': message, **updated_totals})

        except sub_gcf_inward_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

# def add_or_update_gcf_inward_item(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('tm_id')  # Parent Table ID
#         print('master:',master_id)
#         po_id = request.POST.get('po_id',0)
#         product_id = request.POST.get('fabric_id')
#         count = request.POST.get('count_id')
#         color = request.POST.get('color_id')
#         gauge = request.POST.get('gauge_id')
#         tex = request.POST.get('tex_id')  
#         dia = request.POST.get('dia')
#         gsm = request.POST.get('gsm')
#         rolls = request.POST.get('rolls')
#         wt_per_roll = request.POST.get('wt_per_roll')
#         quantity = request.POST.get('quantity')
#         rate = request.POST.get('rate')
#         amount = request.POST.get('total_amount')
#         edit_id = request.POST.get('edit_id')  # This determines if it's an update or new entry
#         tm_id = request.POST.get('tm_id')  # This determines if it's an update or new entry

#         # Ensure required fields are provided
#         if not product_id :
#             return JsonResponse({'success': False, 'error_message': 'Missing required data'})

#         try:
#             if edit_id:  # Update existing record
#                 child_item = sub_gcf_inward_table.objects.get(id=edit_id) 
#                 print('edit-child:',child_item)
#                 # child_item.tm_id = tm_id 
#                 child_item.product_id = product_id 
#                 child_item.count = count
#                 child_item.color_id = color
#                 child_item.gauge = gauge 
#                 child_item.tex = tex
#                 child_item.dia = dia
#                 child_item.po_id = po_id
#                 child_item.gsm = gsm
#                 child_item.rolls = rolls
#                 child_item.wt_per_roll = wt_per_roll
#                 child_item.quantity = quantity 
#                 child_item.rate = rate
#                 child_item.total_amount = amount
#                 child_item.save()
#                 message = "GF Inward updated successfully."
#             else:  # Create new record
#                 child_item = sub_gcf_inward_table.objects.create( 
#                     product_id=product_id,
#                     tm_id=master_id, 
#                     count=count, 
#                     color_id=color, 
#                     gauge=gauge,
#                     tex=tex, 
#                     dia=dia,
#                     po_id=po_id,
#                     gsm=gsm,
#                     rolls=rolls, 
#                     wt_per_roll=wt_per_roll,
#                     quantity=quantity,
#                     rate=rate,
#                     total_amount=amount, 
#                     status=1,
#                     is_active=1
#                 )
#                 message = "New knitting entry created successfully."

#             # Update `tm_table` totals
#             updated_totals = update_knitting(master_id)

#             return JsonResponse({'success': True, 'message': message, **updated_totals})

#         except sub_gcf_inward_table.DoesNotExist:
#             return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})
    
#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
 
 


def gcd_parent_inward_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session['user_id']
        frm = request.POST
        cid = frm.get('update_id')
        print('update-id:',cid)
        through = frm.get('order_through_id') 
        order=gcf_inward_table.objects.get(id=cid)
        order.order_through_id=through
        order.updated_by=user_id
        order.updated_on=timezone.now() 
        order.save()
        message=" Modified successfully"
        return render(request,'gcf/update_gcf_inward.html',{'msg':message})
    else:
        return HttpResponseRedirect('/admin')





def gf_inward_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_gcf_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_gcf_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


from django.http import JsonResponse

def gf_inward_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        print('id:',item_id)
        data = sub_gcf_inward_table.objects.filter(id=item_id).values()

        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
 
 





def load_gf_delivery_details(request):
    if request.method == "GET":
        # po_ids = request.GET.get('po_id', '').split(',')  # Convert to list
        # print('deliver-id:', po_ids)

        # if not po_ids or po_ids == ['']:
        #     return JsonResponse({'error': 'Purchase Order ID(s) are required.'}, status=400)
        po_ids = request.GET.getlist('po_id[]')  # Directly fetch list
        print('delivery-id:',po_ids)
        # if not po_ids:
        #     return JsonResponse({'error': 'Purchase Order ID(s) are required.'}, status=400)


        if not po_ids or po_ids == ['']:
            return JsonResponse({'error': 'No valid Purchase Order IDs received.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided PO IDs
            parent_pos = parent_gf_delivery_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                orders = child_gf_delivery_table.objects.filter(tm_id=po.id)

                for order in orders:
                    product = product_table.objects.filter(id=order.product_id).first()
                    count = count_table.objects.filter(id=order.count_id).first()
                    gauge = gauge_table.objects.filter(id=order.gauge_id).first()
                    tex = tex_table.objects.filter(id=order.tex_id).first()

                    # Prepare order details 
                    print('RATE:',order.rate)
                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "", 
                        'count': count.count if count else "", 
                        'count_id': order.count_id,
                        'gauge_id': order.gauge_id,
                        'tex_id': order.tex_id,
                        'gauge': gauge.name if gauge else "", 
                        'tex': tex.name if tex else "", 
                        'dia':order.dia,
                        'tax_value': 5,  
                        'rolls': order.rolls,
                        'wt_per_roll': order.wt_per_roll,    
                        'quantity': order.quantity, 
                        'rate': order.rate,
                        'total_amount': order.amount,  
                        'id': order.id,
                        'tm_id': order.tm_id,
                        'tx_id': order.id, 
                        'lot_no': order.lot_no
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



# `````````````````````````````````````` GCF DELIVERY LIST ````````````````````````````````````





def gcf_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'gcf/gcf_delivery_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    

 

def gcf_delivery_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(parent_gcf_delivery_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="gcf_delivery_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="gcf_delivery_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="gcf_po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'delivery_date': item['delivery_date'] if item['delivery_date'] else'-', 
            'deliver_to':getSupplier(party_table, item['deliver_to'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'total_tax': item['total_tax'] if item['total_tax'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 



def gcf_delivery_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_process=1) 
        through = party_table.objects.filter(is_compacting=1)

        # if supplier.exists():
        #     supplier_id = supplier.first().id  # Fetch the first supplier's ID 
        #     knitting = knitting_table.objects.filter(knitting_id=supplier_id)
        # else:
        #     supplier_id = None  
        #     knitting = knitting_table.objects.none()   # Return an empty queryset

        party = party_table.objects.filter(status=1) 
        product = fabric_program_table.objects.filter(status=1) 
        deliver = party_table.objects.filter(is_process=1)
        inward = gcf_inward_table.objects.filter(is_complete=0,status=1)
        last_purchase = gcf_delivery_table.objects.order_by('-id').first()
        if last_purchase:
            delivery_number = last_purchase.id + 1 
        else: 
            delivery_number = 1  # Default if no records exist

        process = process_table.objects.filter(status=1, stage__in=['bleaching', 'dyeing','inhouse'])

        count =  count_table.objects.filter(status=1)
        gauge =  gauge_table.objects.filter(status=1)
        tex =  tex_table.objects.filter(status=1)
        return render(request,'gcf/add_gcf_delivery.html',{'inward':inward,'supplier':supplier,'party':party,'product':product,'count':count,
                                                        'gauge':gauge,'tex':tex,'through':through,'process':process,'deliver':deliver,'do_number':delivery_number})
    else:
        return HttpResponseRedirect("/admin")
    

@csrf_exempt  # Use this only if necessary
def get_order_through_list(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')

        if not supplier_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)

        try:
            # Retrieve the fabric program
            data = get_object_or_404(gcf_inward_table, order_through_id=supplier_id)

            # Fetch related data
            # product = get_object_or_404(fabric_program_table, id=sub_data.product_id)
    #    

            response_data = {
                # 'product': {'id': product.id, 'product': product.name},
               
                'total_quantity': {'id': data.id, 'total_quantity': data.total_quantity}
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_list_or_404

@csrf_exempt  # Use only if CSRF is causing issues
def get_through_lot_list(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')
        # print()

        if not supplier_id:
            return JsonResponse({'error': 'Supplier ID is required'}, status=400)

        try:
            # Retrieve all lots for the supplier
            lots = gcf_inward_table.objects.filter(order_through_id=supplier_id)


            if not lots.exists():
                return JsonResponse({'error': 'No lots found for this supplier'}, status=404)

            # Format the response as a list
            response_data = {
                'lots': [{'id': lot.id, 'lot_no': lot.lot_no} for lot in lots],
                'total_quantity': [{'id': lot.id, 'total_quantity': lot.total_quantity} for lot in lots],


            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt  # Use only if necessary
def get_gcf_lot_details(request):
    if request.method == 'POST':
        lot_id = request.POST.get('lot_id')

        if not lot_id:
            return JsonResponse({'error': 'Lot ID is required'}, status=400)

        try:
            # **1. Get Inward Stock (In-House Stock)**
            fabric_program = get_object_or_404(gcf_inward_table, id=lot_id, status=1)
            lot_no = fabric_program.lot_no  # In-house stock
            inward_total_quantity = fabric_program.total_quantity  # In-house stock
            
            

            # **2. Get Fabric Program Quantity (Knitting Table)**
            knitting_record = knitting_table.objects.filter(lot_no=fabric_program.lot_no).first()
            program_total_quantity = knitting_record.total_quantity if knitting_record else Decimal('0.00')
            
            sub_data = sub_knitting_table.objects.filter(tm_id=knitting_record.id, status=1).first()
 
            prd_id = sub_data.fabric_id
            print('knit-prd-id:',prd_id)
            product = get_object_or_404(fabric_program_table, id=prd_id)

            # **3. Get Delivered Quantity (Parent GF Delivery Table)**
            delivery_record = parent_gf_delivery_table.objects.filter(lot_no=fabric_program.lot_no).first()
            delivered_quantity = delivery_record.total_quantity if delivery_record else Decimal('0.00')
 
            # **4. Calculate Balance Quantity**
            balance_quantity = inward_total_quantity - delivered_quantity

            # **Prepare Response Data**
            response_data = {
                'lot_no': fabric_program.lot_no, 
                'inward_total_quantity': inward_total_quantity,  # In-house stock
                'program_total_quantity': program_total_quantity,  # Fabric program
                'delivered_quantity': delivered_quantity,  # Delivered stock
                'balance_quantity': balance_quantity,  # Remaining balance
                'prd': {'id': product.id, 'product': product.name},
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)






def add_gcf_delivery(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        try: 
            # Extracting data from the request
            do_date = request.POST.get('delivery_date') 
            supplier_id = request.POST.get('supplier_id')
            # lot_no = request.POST.get('lot_no')
            deliver_id = request.POST.get('deliver_id')
            remarks = request.POST.get('remarks')
            quantity = request.POST.get('quantity')
            process_id = request.POST.get('process_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 

            # Get PO IDs
            po_ids = request.GET.getlist('po_id[]')  
            po_ids_str = ",".join(po_ids)

            # Create a new entry in knitting_deliver_table (Parent table)
            material_request = parent_gcf_delivery_table.objects.create(
                po_id=po_ids_str,
                delivery_date=do_date,
                deliver_to=deliver_id,
                supplier_id=supplier_id,
                quantity=quantity,
                process_id=process_id,
                lot_no=0,
                total_quantity=request.POST.get('total_quantity'),
                total_amount=request.POST.get('sub_total'),
                total_tax=request.POST.get('tax_total'),
                grand_total=request.POST.get('total_payable'),
                remarks=remarks,
                created_by=user_id,
                created_on=datetime.now()
            )

            # Iterate through chemical_data and save records
            for chemical in chemical_data:
                tm_po_id = chemical.get('tm_id')
                print('po-id:',tm_po_id)
                product_id = chemical.get('product_id')
                delivered_bag = Decimal(chemical.get('bag') or 0)
                delivered_quantity = Decimal(chemical.get('quantity') or 0)
                delivered_amount = Decimal(chemical.get('amount') or 0)
 
                # Create a new record in sub_knitting_deliver_table
                child_gcf_delivery_table.objects.create(
                    tm_id=material_request.id,
                    lot_no=chemical.get('lot_no'),
                    product_id=product_id,
                    tm_po_id=tm_po_id,
                    count_id=chemical.get('count_id'),
                    gauge_id=chemical.get('gauge_id'),
                    tex_id = chemical.get('tex_id'),
                    dia = chemical.get('dia'),
                    rolls= chemical.get('rolls'),
                    wt_per_roll = chemical.get('wt_per_roll'),
                    quantity=delivered_quantity,  
                    rate=chemical.get('rate'),
                    amount=delivered_amount,
                    created_by=user_id, 
                    created_on=datetime.now()
                    ) 

                # **Update child_po_table (Reduce Remaining Values)**
              
            # 🔹 **Update Parent PO Table (`po_table`)**  
            inward = chemical.get('tm_id') 

            if inward:
                updated_count = gcf_inward_table.objects.filter(id=inward).update(is_complete=1)
                if updated_count == 0:
                    print(f"⚠️ No matching record found for ID: {inward}")



            # gf_inward_table.objects.filter(id__in=inward).update(is_complete=1)

            return JsonResponse('yes', safe=False)  # Indicate success

        except Exception as e: 
            print(f"❌ Error: {e}")  # Log error for debugging
            return JsonResponse('no', safe=False)  # Indicate failure

    return render(request, 'gcf/add_gcf_delivery.html')



def load_gcf_delivery_details(request):
    if request.method == "GET":
        po_ids = request.GET.get('po_id', '').split(',')  # Convert to list
        print('po-id:', po_ids)

        if not po_ids or po_ids == ['']:
            return JsonResponse({'error': 'Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided PO IDs
            parent_pos = gcf_inward_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                orders = sub_gcf_inward_table.objects.filter(tm_id=po.id)

                for order in orders:
                    product = fabric_program_table.objects.filter(id=order.product_id).first()
                    count = count_table.objects.filter(id=order.count).first()
                    gauge = gauge_table.objects.filter(id=order.gauge).first()
                    tex = tex_table.objects.filter(id=order.tex).first()

                    # Prepare order details
                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "", 
                        'count': count.count if count else "", 
                        'count_id': order.count,
                        'gauge_id': order.gauge,
                        'tex_id': order.tex,
                        'gauge': gauge.name if gauge else "", 
                        'tex': tex.name if tex else "", 
                        'dia':order.dia,
                        'tax_value': 5,  
                        'rolls': order.rolls,
                        'wt_per_roll': order.wt_per_roll,   
                        'quantity': order.quantity,
                        'rate': order.rate,
                        'amount': order.total_amount, 
                        'id': order.id,
                        'tm_id': order.tm_id,
                        'tx_id': order.id,
                        'lot_no': order.lot_no
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)




 
def gcf_delivery_detail_edit(request):
    try: 
        encoded_id = request.GET.get('id') 
        print('encoded-id:',encoded_id) 
        if not encoded_id:
            return render(request, 'gcf/update_gcf_delivery.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode() 
            print('Decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'gcf/update_gcf_delivery.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
        print('material-id:',material_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_gcf_delivery_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            product_id = request.POST.get('product_id')  # Adjust as per your input structure
            bag = request.POST.get('bag')  # Adjust as per your input structure
            per_bag = request.POST.get('per_bag')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            rate = request.POST.get('rate')  # Adjust as per your input structure
            amount = request.POST.get('amount')  # Adjust as per your input structure

            # Ensure valid data before saving
            if product_id and bag and quantity:
                material_instance = child_gcf_delivery_table.objects.create(
                    tm_id=material_id,
                    product_id=product_id, 
                    bag=bag,
                    per_bag=per_bag,
                    rate=rate,
                    quantity=quantity, 
                    amount=amount,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'gcf/update_gcf_delivery.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = parent_gcf_delivery_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'gcf/update_gcf_delivery.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.supplier_id:
            try: 
                supplier = party_table.objects.get(id=parent_stock_instance.supplier_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        product = product_table.objects.filter(status=1)
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_knitting=1,status=1)
        count = count_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance, 
            'product': product,
            'party': party,
            'supplier_id': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'count':count,
            'gauge':gauge,
            'tex':tex
        }
        return render(request, 'gcf/update_gcf_delivery.html', context)

    except Exception as e:
        return render(request, 'gcf/update_gcf_delivery.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




def gcf_delivery_update_view(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id:  
            try:
                # Fetch child PO data
                child_data = child_gcf_delivery_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('amount'))['amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = parent_gcf_delivery_table.objects.filter(id=master_id).first()
                    if parent_data:
                        tax_total = parent_data.total_tax or 0
                        # round_off = parent_data.round_off or 0
                        grand_total = total_amount + tax_total 
                    else:
                        tax_total = grand_total = 0 

                    # Format child PO data for response
                    data = list(child_data.values()) 
                    formatted_data = []
                    index = 0
                    for item in data: 
                        index += 1  
                        formatted_data.append({
                            'action': '<button type="button" onclick="gcf_delivery_details_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="gcf_delivery_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'product': getItemNameById(product_table, item['product_id']), 
                            'count': getCountNameById(count_table, item['count_id']), 
                            'gauge': getItemNameById(gauge_table, item['gauge_id']), 
                            'tex': getItemNameById(tex_table, item['tex_id']),  
                            'dia': item['dia'] if item['dia'] else '-',
                            'rolls': item['rolls'] if item['rolls'] else '-',
                            'wt_per_roll': item['wt_per_roll'] if item['wt_per_roll'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'rate': item['rate'] if item['rate'] else '-',
                            'total_amount': item['amount'] if item['amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({ 
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_amount': total_amount,
                        'tax_total': tax_total,
                        # 'round_off': round_off,
                        'grand_total': grand_total
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})







def gcf_delivery_details_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = child_gcf_delivery_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
 



def update_gcf_delivery(master_id):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = child_gf_delivery_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
        total_amount = tx.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # Convert tax rate to Decimal and perform multiplication safely
        tax_rate = Decimal('0.05')  # 5% tax
        tax_total = (total_amount * tax_rate).quantize(Decimal('0.01'))  # Ensure 2 decimal places

        # Calculate raw total before rounding
        raw_total = total_amount + tax_total

        # Compute round_off and grand_total
        rounded_total = Decimal(round(raw_total))  # Ensure Decimal type
        round_off = (rounded_total - raw_total).quantize(Decimal('0.01'))  # Ensure 2 decimal places
        grand_total = rounded_total  # Final rounded total

        # Update values in parent_po_table
        parent_gf_delivery_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            total_amount=total_amount.quantize(Decimal('0.01')),
            tax_total=tax_total,
            round_off=round_off,
            grand_total=grand_total
        )

        # Return updated values for frontend update
        return {
            'total_quantity': total_quantity,
            'total_amount': total_amount.quantize(Decimal('0.01')),
            'tax_total': tax_total,
            'round_off': round_off,
            'grand_total': grand_total
        }

    except Exception as e:
        return {'error': str(e)}


def add_or_update_gcf_delivery_item(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('tm-id:',master_id)
        product_id = request.POST.get('fabric_id')
        count = request.POST.get('count_id')
        gauge = request.POST.get('gauge_id')
        tex = request.POST.get('tex_id') 
        dia = request.POST.get('dia')
        rolls = request.POST.get('rolls')
        wt_per_roll = request.POST.get('wt_per_roll') 
        quantity = request.POST.get('quantity')
        rate = request.POST.get('rate')
        total_amount = request.POST.get('total_amount')

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Add or update the child table record
            child_item, created = child_gf_delivery_table.objects.update_or_create(
                tm_id=master_id, product_id=product_id,
                defaults={
                    'count_id': count,
                    'gauge_id': gauge,
                    'tex_id': tex,
                    'dia':dia, 
                    'rolls':rolls,
                    'wt_per_roll':wt_per_roll,
                    'quantity': quantity,
                    'rate': rate,
                    'total_amount': total_amount,
                    'status': 1,
                    'is_active': 1
                }
            )

            # Update `tm_table` with new totals
            updated_totals = update_gcf_delivery(master_id)

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})



def gcf_delivery_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            child_gcf_delivery_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except child_gcf_delivery_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    



