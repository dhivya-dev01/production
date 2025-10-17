

from os import stat
from django.shortcuts import render
from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify 

from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
# from accessory.forms import *
import datetime

from datetime import datetime
from datetime import date
from django.utils import timezone

from django.db.models import Count 


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from accessory.models import *

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

from yarn.views import *
from software_app.models import *
from collections import defaultdict

# `````````````````````````````````````````````````````````````````````



def generate_po_num_series():
    last_purchase = parent_accessory_po_table.objects.filter(status=1).order_by('-id').first()
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



def accessory_po(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        po_number = generate_po_num_series
        return render(request,'po/purchase_order_list.html',{'supplier':supplier,'party':party,'product':product,'po_number':po_number})
    else:
        return HttpResponseRedirect("/admin")





def add_po(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(
            Q(is_trader=1) | Q(is_supplier=1),
            status=1
        )  
        item_group = item_group_table.objects.filter(status=1)
        item = item_table.objects.filter(status=1) 

        po_number = generate_po_num_series

        return render(request,'po/add_po.html',{'item':item,'party':party,'item_group':item_group,'po_number':po_number})
    else:
        return HttpResponseRedirect("/admin")


from django.http import JsonResponse
from django.shortcuts import get_list_or_404
from django.views.decorators.csrf import csrf_exempt

def get_item_list(request):
    if request.method == 'GET':
        item_group_id = request.GET.get('item_group_id')

        if not item_group_id:
            return JsonResponse({'success': False, 'message': 'Item Group ID is required'}, status=400)

        try:
            # Get all items under this group
            items = item_table.objects.filter(item_group_id=item_group_id)

            # Convert items to list of dictionaries
            item_list = [{'id': item.id, 'name': item.name} for item in items]
            item_ids = [item.id for item in items]  # For sub_size filter

            # Now get sub_size values for these items
            sub_values = sub_size_table.objects.filter(status=1, item_id__in=item_ids)

            # Collect unique quality, size, and color IDs
            quality_ids = sub_values.values_list('quality_id', flat=True).distinct()
            size_ids = sub_values.values_list('size_id', flat=True).distinct()
            color_ids = sub_values.values_list('m_color_id', flat=True).distinct()
            
            # Fetch actual names from respective tables
            qualities = accessory_quality_table.objects.filter(id__in=quality_ids)
            sizes = accessory_size_table.objects.filter(id__in=size_ids)
            colors = color_table.objects.filter(id__in=color_ids)

            # quality_list = [{'id': q.id, 'name': q.po_name} for q in qualities]
            # size_list = [{'id': s.id, 'name': s.po_name} for s in sizes]
            color_list = [{'id': c.id, 'name': c.name} for c in colors]
            quality_list = [
                {
                    'id': q.id,
                    'name': f"{q.name} - ({q.po_name if q.po_name else '-'})"
                }
                for q in qualities
            ]

            size_list = [
                {
                    'id': s.id,
                    'name': f"{s.name} - ({s.po_name if s.po_name else '-'})"
                }
                for s in sizes
            ]
            return JsonResponse({
                'success': True,
                'items': item_list,
                'qualities': quality_list,
                'sizes': size_list,
                'colors': color_list,
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


from django.http import JsonResponse




def get_acc_value_list(request):
    if request.method == 'GET':
        item_id = request.GET.get('item_id')
        print('item-ids:', item_id)
        
        if not item_id:
            return JsonResponse({'success': False, 'message': 'Item ID is required'}, status=400)

        try:
            # Handle multiple item IDs (if comma-separated)
            item_ids = [int(i.strip()) for i in item_id.split(',') if i.strip().isdigit()]
            sub_items = sub_size_table.objects.filter(status=1, item_id__in=item_ids)

            # Get quality and size IDs directly
            quality_ids = sub_items.values_list('quality_id', flat=True).distinct()
            size_ids = sub_items.values_list('size_id', flat=True).distinct()

            # Handle color_ids as comma-separated values
            color_id_strings = sub_items.values_list('m_color_id', flat=True)

            # Flatten and convert to individual integers
            color_ids = set()
            for color_str in color_id_strings:
                if color_str:
                    ids = [int(cid.strip()) for cid in color_str.split(',') if cid.strip().isdigit()]
                    color_ids.update(ids)

            # Fetch actual names from respective tables
            qualities = accessory_quality_table.objects.filter(id__in=quality_ids)
            sizes = accessory_size_table.objects.filter(id__in=size_ids)
            colors = color_table.objects.filter(id__in=color_ids)
 
            # quality_list = [{'id': q.id, 'name': q.po_name} for q in qualities]
            # size_list = [{'id': s.id, 'name': s.po_name} for s in sizes]
            color_list = [{'id': c.id, 'name': c.name} for c in colors]
             
            quality_list = [
                { 
                    'id': q.id,
                    'name': f"{q.name} - ({q.po_name if q.po_name else '-'})"
                }
                for q in qualities
            ]

            size_list = [
                {
                    'id': s.id,
                    'name': f"{s.name} - ({s.po_name if s.po_name else '-'})"
                }
                for s in sizes
            ]
            
            return JsonResponse({
                'success': True,
                'qualities': quality_list,
                'sizes': size_list,
                'colors': color_list,
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)







@csrf_exempt
def purchase_order_add(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try:
            # Extracting Data from Request  
            supplier_id = request.POST.get('supplier_id',0)
            remarks = request.POST.get('remarks')
            price_list = request.POST.get('price_list')
            po_date = request.POST.get('purchase_date')
            # po_name = request.POST.get('purchase_name')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            # Create Parent Entry (gf_inward_table)

            po_number = request.POST.get('purchase_number')
            material_request = parent_accessory_po_table.objects.create(
                po_number = po_number,
                # po_name = po_name,
                po_date=po_date, 
                party_id=supplier_id,
                company_id=company_id,
                cfyear = 2025,
                total_quantity=request.POST.get('total_quantity'),
                total_amount=request.POST.get('sub_total'),
                total_tax=request.POST.get('tax_total'),
                round_off=request.POST.get('round_off'),
                grand_total=request.POST.get('total_payable'), 
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )

            # po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for chemical in chemical_data: 
                print("Processing Chemical Data:", chemical)

                rate = Decimal(str(chemical.get('rate', 0)).replace(',', ''))
                amount = Decimal(str(chemical.get('amount', 0)).replace(',', ''))

                sub_entry = child_accessory_po_table.objects.create(
                    tm_id=material_request.id, 
                    company_id=company_id, 
                    cfyear = 2025, 
                    item_group_id=chemical.get('item_group_id'),
                    item_id=chemical.get('item_id'),
                    quality_id=chemical.get('quality_id'),
                    size_id=chemical.get('size_id'), 
                    color_id=chemical.get('color_id'),
                    quantity = chemical.get('quantity'),
                    rate=rate ,#chemical.get('rate'), 
                    amount= amount,#chemical.get('amount'),
                    created_by=user_id, 
                    created_on=timezone.now()
                )


                print("Sub Table Entry Created:", sub_entry)  
 
            return JsonResponse({'status': 'Success', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'po/add_po.html')



def purchase_order_view(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    po_id = request.POST.get('po_id', '')
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

    if po_id:
            query &= Q(po_id=po_id)


    # Apply filters 
    queryset = parent_accessory_po_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())


    # data = list(parent_accessory_po_table.objects.filter(queryset).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="accessory_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="accessory_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="accessory_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'po_date': item['po_date'] if item['po_date'] else'-', 
            'po_number': item['po_number'] if item['po_number'] else'-', 
            # 'po_name': item['po_name'] if item['po_name'] else'-', 
            'party':getSupplier(party_table, item['party_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'tax_total': item['total_tax'] if item['total_tax'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})  
 


def accessory_po_detail_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            parent_accessory_po_table.objects.filter(id=data_id).update(status=0,is_active=0)

            child_accessory_po_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except parent_accessory_po_table  & child_accessory_po_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})








def po_details_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'po/purchase_details_update.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()  
            print('ids:',decoded_id)

        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'po/purchase_details_update.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer 
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_accessory_po_table.objects.filter(tm_id=material_id)
       
        # Fetch the parent stock instance
        parent_stock_instance = parent_accessory_po_table.objects.filter(id=material_id).first()
        print('parent:',parent_stock_instance)
        if not parent_stock_instance:
            return render(request, 'po/purchase_details_update.html', {'error_message': 'Parent stock not found.'})

       
        # Fetch active products and UOM
        item_group = item_group_table.objects.filter(status=1)
        item = item_table.objects.filter(status=1)
        # supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(
            Q(is_trader=1) | Q(is_supplier=1),
            status=1
        )  
        print('item:',party)

        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'item_group': item_group,
            'item':item,
            'party': party,
            'supplier': party
        }
        print('cntexrt:',context)
        return render(request, 'po/purchase_details_update.html', context)

    except Exception as e:
        return render(request, 'po/purchase_details_update.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




def update_po_lists(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data
                child_data = child_accessory_po_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('amount'))['amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = parent_accessory_po_table.objects.filter(id=master_id).first()
                    if parent_data:
                        tax_total = parent_data.total_tax or 0
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
                            'action': '<button type="button" onclick="purchase_order_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="accessory_po_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'item_group': getItemNameById(item_group_table, item['item_group_id']),
                            'item': getItemNameById(item_table, item['item_id']),
                            'quality': get_po_name_by_id(accessory_quality_table, item['quality_id']),
                            'size': get_po_name_by_id(accessory_size_table, item['size_id']),
                            'color': getItemNameById(color_table, item['color_id']),
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'rate': item['rate'] if item['rate'] else '-',
                            'amount': item['amount'] if item['amount'] else '-',
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




# def getPONAMEById(tbl, product_id):
    # try:
        # party = tbl.objects.get(id=product_id).po_name
    # except ObjectDoesNotExist:
        # party = "-"  # Handle the error by providing a default value or appropriate message 
    # return party



def get_po_name_by_id(tbl, product_id):
    try:
        obj = tbl.objects.get(id=product_id)
        name = getattr(obj, 'name', '-')
        po_name = getattr(obj, 'po_name', '-')
        return f"{name} - ({po_name})"
    except ObjectDoesNotExist:
        return "- -"


@csrf_exempt
def accessory_po_items_update(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

    try:
        master_id = request.POST.get('tm_id')
        edit_id = request.POST.get('edit_id')  # used to check if it's an update
        item_group_id = request.POST.get('item_group_id')
        item_id = request.POST.get('item_id')
        quality_id = request.POST.get('quality_id')
        size_id = request.POST.get('size_id')
        color_id = request.POST.get('color_id')
        rate = request.POST.get('rate')
        quantity = request.POST.get('quantity')
        amount = request.POST.get('amount')

        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        # Validate required fields
        if not master_id or not item_id:
            return JsonResponse({'success': False, 'error_message': 'Missing master ID or item ID'})

        # Shared data for both create/update
        data = {
            'item_group_id': int(item_group_id) if item_group_id else None,
            'item_id': int(item_id),
            'quality_id': int(quality_id) if quality_id else None,
            'size_id': int(size_id) if size_id else None,
            'color_id': int(color_id) if color_id else None,
            'rate': float(rate) if rate else 0,
            'quantity': float(quantity) if quantity else 0,
            'amount': float(amount) if amount else 0,
            'status': 1,
            'is_active': 1,
            'updated_by': int(user_id) if user_id else None,
            'company_id': int(company_id) if company_id else None,
            'cfyear': 2025
        }

        if edit_id:
            # ✅ UPDATE
            try:
                obj = child_accessory_po_table.objects.get(id=int(edit_id))
                for key, value in data.items():
                    setattr(obj, key, value)
                obj.save()
                created = False
            except child_accessory_po_table.DoesNotExist:
                return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
        else:
            # ✅ CREATE
            obj = child_accessory_po_table.objects.create(
                tm_id=int(master_id),
                **data
            )
            created = True

        # Optional: update totals on master
        updated_totals = update_accessory_value(master_id)

        return JsonResponse({
            'success': True,
            'created': created,
            'obj_id': obj.id,
            **updated_totals
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error_message': str(e)})




def update_accessory_value(master_id):
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = child_accessory_po_table.objects.filter(tm_id=master_id, status=1, is_active=1)

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

        parent_accessory_po_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            total_amount=total_amount.quantize(Decimal('0.01')),
            total_tax=tax_total,
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





def po_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id') 
        try:
            # Update the status field to 0 instead of deleting
            child_accessory_po_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except child_accessory_po_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




def update_accessory_po_details(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        po_date_str = request.POST.get('po_date')
        party_id = request.POST.get('party_id')  
        # lot_no = request.POST.get('lot_no')  
        remarks = request.POST.get('remarks')  
        # po_name = request.POST.get('po_name')   
      

        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = parent_accessory_po_table.objects.get(id=tm_id)
            parent_item.party_id = party_id
            # parent_item.lot_no = lot_no
            # parent_item.po_name = po_name 
            parent_item.remarks = remarks
         
            if po_date_str:
                po_date = datetime.strptime(po_date_str, '%Y-%m-%d').date()
                parent_item.po_date = po_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except parent_accessory_po_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})



@csrf_exempt
def print_accessory_po(request):
    po_id = request.GET.get('k')
    order_id = base64.b64decode(po_id)
    print('print-id:', order_id) 

    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    total_values = get_object_or_404(parent_accessory_po_table, id=order_id)
    customer_value = get_object_or_404(party_table, status=1, id=total_values.party_id)

    details = (
        child_accessory_po_table.objects
        .filter(tm_id=order_id)
        .values('item_group_id', 'item_id', 'size_id','quality_id', 'color_id',
                'id', 'rate', 'quantity', 'amount')
    )
 
    combined_details = []
    total_quantity = 0
    total_amount = 0
    item_group_names = set()   # collect unique group names

    for detail in details:
        product = get_object_or_404(item_group_table, id=detail['item_group_id'])
        item = get_object_or_404(item_table, id=detail['item_id'])
        size = get_object_or_404(accessory_size_table, id=detail['size_id'])
        quality = get_object_or_404(accessory_quality_table, id=detail['quality_id'])
        color = get_object_or_404(color_table, id=detail['color_id'])

        combined_details.append({
            'item_group': product.name,
            'item': item.name,
            'size': size.po_name,
            'quality':quality.po_name, 
            'color': color.name,
            'quantity': detail['quantity'],
            'rate': detail['rate'],
            'amount': detail['amount'],
        })

        # ✅ Add inside the loop
        item_group_names.add(product.name)
        total_quantity += detail['quantity']
        total_amount += detail['amount']

    # join unique names with commas
    item_group_name = ", ".join(sorted(item_group_names))
    print('grp-name:', item_group_name)

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
        'company': company_table.objects.filter(status=1).first(),
        'image_url': image_url,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'item_group_name': item_group_name,
    }
    return render(request, 'po/po_print.html', context)




# @csrf_exempt
# def print_accessory_po(request): 
#     po_id = request.GET.get('k') 
#     order_id = base64.b64decode(po_id)
#     print('print-id:',order_id) 
    
#     if not order_id:
#         return JsonResponse({'error': 'Order ID not provided'}, status=400)

#     total_values = get_object_or_404(parent_accessory_po_table, id=order_id)
#     # mill = get_object_or_404(party_table, status=1, id=total_values.mill_id)
#     # print('mill:',mill)
#     customer_value = get_object_or_404(party_table, status=1, id=total_values.party_id)
    
#     details = (
#         child_accessory_po_table.objects.filter(tm_id=order_id) 
#         .values('item_group_id', 'item_id', 'size_id','color_id','id','rate','quantity', 'amount')
 
#     )

#     combined_details =[]
#     total_quantity=0
#     total_amount=0
#     item_group_names = set()          # collect unique group names

#     for detail in details:
#         product = get_object_or_404(item_group_table, id=detail['item_group_id'])
#         item = get_object_or_404(item_table, id=detail['item_id'])
#         size = get_object_or_404(accessory_size_table, id=detail['size_id'])
#         color = get_object_or_404(color_table, id=detail['color_id'])

#         combined_details.append({
#             'item_group': product.name,
#             'item': item.name,
#             'size':size.name,
#             'color':color.name,
#             'quantity': detail['quantity'],
#             'rate': detail['rate'],
#             'amount': detail['amount'],
            
#         })

#     # add to the set for unique names
#     item_group_names.add(product.name)

#     # join unique names with commas
#     item_group_name = ", ".join(sorted(item_group_names))
#     print('grp-name:',item_group_names)
#     total_quantity += detail['quantity']
#     total_amount += detail['amount']
       
#     # image_url = 'http://localhost:8000/static/assets/images/mirra-logo.jpg'
#     image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

#     print('image_url:',image_url)

#     context = { 
#         'total_values': total_values,
#         'remarks':total_values.remarks, 
#         'customer_name': customer_value.name,
#         'mobile_no': customer_value.mobile, 
#         'gstin': customer_value.gstin,
    
#         'phone_no': customer_value.mobile,
#         'city': customer_value.city,
#         'state': customer_value.state,
#         'pincode': customer_value.pincode,
#         'address_line1': customer_value.address,
#         'combined_details': combined_details,
        
#         'company': company_table.objects.filter(status=1).first(),
#         'image_url':image_url,
#         'total_amount':total_amount,
#         'total_quantity':total_quantity,
#         'item_group_name':item_group_name,
      
#     }

#     return render(request, 'po/po_print.html', context)