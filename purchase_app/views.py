from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *

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

from yarn.models import *


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 


# Create your views here.


def yarn_po(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'purchase/yarn_po.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")


 
def yarn_po_report(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)

    data = list(parent_po_table.objects.filter(status=1).order_by('-id').values())

    formatted = []

    for index, item in enumerate(data):
        # Fetch the child PO for each parent PO
        child_po = parent_po_table.objects.filter(id=item['id'], status=1).first()

        if child_po:  # Ensure child_po is not None
            yarn = child_po.yarn_count_id
        else:
            yarn = None  # If no child PO exists, handle accordingly

        formatted.append({
            'action': '<button type="button" onclick="po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="po_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>' .format(item['id'], item['id']),
            'id': index + 1,
            'po_date': item['po_date'] if item['po_date'] else '-', 
            'po_number': item['po_number'] if item['po_number'] else '-',
            'name': item['name'] if item['name'] else '-',
            'supplier_id': getSupplier(party_table, item['party_id']),
            'yarn_count': getSupplier(count_table, yarn) if yarn else '-',
            'total_bag': item['bag'] if item['bag'] else '-',
            'total_quantity': item['quantity'] if item['quantity'] else '-',
            # 'tax_total': item['tax_total'] if item['tax_total'] else '-',
            # 'total_amount': item['total_amount'] if item['total_amount'] else '-',
            # 'grand_total': item['grand_total'] if item['grand_total'] else '-',
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted})


@require_POST
def purchase_print(request):
    order_id = request.POST.get('id')
    print('print-id:',order_id)
    
    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    total_values = get_object_or_404(parent_po_table, id=order_id)
    customer_value = get_object_or_404(party_table, status=1, id=total_values.party_id)
    
    details = (
        parent_po_table.objects.filter(tm_po_id=order_id) 
        .values('product_id', 'rate')
        .annotate(
            total_bag=Sum('bag'), 
            total_per_pag=Sum('per_bag'), 
            total_quantity=Sum('quantity'), 
            total_amount=Sum('amount')
        )
    )

    combined_hsn_data = {}
    combined_details =[]
    total_amount = Decimal('0.00')
    total_tax = total_values.tax_total

    for detail in details:
        product = get_object_or_404(product_table, id=detail['yarn_count_id'])
        # tax = tax_table.objects.filter(id=product.tax_id).first()
        tax = tax_table.objects.filter(status=1).first()
        
        tax_value = 5 #tax.tax if tax else Decimal('0.00')
        hsn_code = tax.hsn if tax else ""

        cgst_rate = tax_value / Decimal('2')  # Split tax rate
        sgst_rate = tax_value / Decimal('2')
        output_cgst = total_tax/2
        output_sgst = total_tax/2
        
        cgst_amount = detail['total_amount'] * cgst_rate / Decimal('100')
        sgst_amount = detail['total_amount'] * sgst_rate / Decimal('100')
        total_tax_amount = cgst_amount + sgst_amount
        total_amount += detail['total_amount']
        combined_details.append({
            'name': product.name,
            'hsn_sac': tax_value,
            'hsn': hsn_code,
            'quantity': detail['total_quantity'],
            'rate': detail['net_rate'],
            'amount': detail['total_amount'],
            'cgst_rate': cgst_rate,
            'cgst_amount': cgst_amount.quantize(Decimal('0.01')),
            'sgst_rate': sgst_rate,
            'sgst_amount': sgst_amount.quantize(Decimal('0.01')),
            'output_cgst_value': output_cgst,
            'output_sgst_value': output_sgst,
            'total_tax_amount': total_tax_amount.quantize(Decimal('0.01')),
        })
        if hsn_code in combined_hsn_data:
            # Update existing entry
            combined_hsn_data[hsn_code]['amount'] += detail['total_amount']
            combined_hsn_data[hsn_code]['cgst_amount'] += cgst_amount
            combined_hsn_data[hsn_code]['sgst_amount'] += sgst_amount
            combined_hsn_data[hsn_code]['total_tax_amount'] += total_tax_amount
        else:
            # Create new entry
            combined_hsn_data[hsn_code] = {
                'hsn': hsn_code,
                'amount': detail['total_amount'],
                'cgst_rate': cgst_rate,
                'cgst_amount': cgst_amount,
                'sgst_rate': sgst_rate,
                'sgst_amount': sgst_amount,
                'total_tax_amount': total_tax_amount,
            }

    tax_combined_details = list(combined_hsn_data.values())
    footer_totals = {
        'total_taxable_value': total_amount,
        'total_cgst_amount': sum(d['cgst_amount'] for d in tax_combined_details),
        'total_sgst_amount': sum(d['sgst_amount'] for d in tax_combined_details),
        'total_tax_amount': sum(d['total_tax_amount'] for d in tax_combined_details),
    }

    total = total_amount + total_tax
    rounded_off = total.quantize(Decimal('1.00'))
    rounding_difference = rounded_off - total  # Calculate rounding difference
   
   

    context = { 
        'total_values': total_values,
        'customer_name': customer_value.name,
        'phone_no': customer_value.mobile,
        'city': customer_value.city,
        'state': customer_value.state,
        'pincode': customer_value.pincode,
        'address_line1': customer_value.address,
        'combined_details': combined_details,
        'tax_combined_details':tax_combined_details,
        'company': company_table.objects.filter(status=1).first(),
        'footer_totals': footer_totals,
        'total_tax': total_tax,
        'cgst': cgst_rate,
        'sgst': sgst_rate,
        'cgst_amount':cgst_amount,
        'sgst_amount':sgst_amount,
        'output_cgst_value': output_cgst,
        'output_sgst_value': output_sgst,
        'amount': total_amount,
        'rounded_off' : rounding_difference,
        # 'rounded_off': (total_amount + total_tax).quantize(Decimal('1.00')),
        # 'amount_in_words': num2words((total_amount + total_tax).quantize(Decimal('1.00')), lang='en_IN'),
        # 'total_tax_amount_in_words': num2words(total_tax.quantize(Decimal('1.00')), lang='en_IN'),
    }

    return render(request, 'purchase/purchase_print.html', context)


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


#   party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)


# ``````````````````````````````````` yarn po `````````````````````````````````````````````````````````````     
  
def yarn_po_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        supplier = party_table.objects.filter(is_knitting=1,status=1)
        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)

        # party = party_table.objects.filter(status=1,is_mill=1,is_trader=1)
        product = product_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        
        # Get the last ID from parent_po_table and increment by 1
        last_purchase = parent_po_table.objects.order_by('-id').first()
        if last_purchase:
            purchase_number = last_purchase.id + 1 
        else:
            purchase_number = 1  # Default if no records exist

        return render(request, 'purchase/yarn_po_add.html', {
            'supplier': supplier,
            'party': party,
            'product': product,
            'count':count,
            'purchase_number': purchase_number
        }) 
    else:
        return HttpResponseRedirect("/admin")



def get_mills(request, party_id):
    # Retrieve the party corresponding to the provided party_id
    party = party_table.objects.filter(id=party_id).first()

    # Check if the party exists and if it has is_mill=1
    if party and party.is_mill == 1:
        # If is_mill = 1, return the party name
        return JsonResponse({'mills': [{'id': party.id, 'name': party.name}]})
    else:
        # If the party doesn't have is_mill = 1, return mills with is_mill=1 from the party list
        mills = party_table.objects.filter(is_mill=1)
        mills_data = [{'id': mill.id, 'name': mill.name} for mill in mills]
        return JsonResponse({'mills': mills_data})



from django.core.exceptions import ValidationError
from datetime import datetime

def validate_date_format(date_string):
    """Validates if a date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def insert_yarn_po(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        if not user_id or not company_id:
            return JsonResponse({'status': 'Failed', 'message': 'User or company information missing.'}, status=400)

        try:
            po_date = request.POST.get('purchase_date')
            name = request.POST.get('name')
            supplier_id = request.POST.get('supplier_id')
            order_through = request.POST.get('through_id')
            price_list = request.POST.get('price_list')
            remarks = request.POST.get('remarks')
            
            delivery_data_raw = request.POST.get('delivery_data', '[]')
            print('delivery:',delivery_data_raw)
            try:
                delivery_data = json.loads(delivery_data_raw)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'Failed', 'message': 'Invalid JSON format in delivery data.'}, status=400)

            if not po_date or not supplier_id:
                return JsonResponse({'status': 'Failed', 'message': 'Missing essential purchase order information.'}, status=400)

            # Initialize totals 
            total_quantity = 0
            total_amount = 0

            # Handling product data
            product_id = request.POST.get('product_id')
            bag = float(request.POST.get('bag', 0))
            per_bag = float(request.POST.get('per_bag', 0))
            quantity = float(request.POST.get('quantity', 0))
            actual_rate = float(request.POST.get('actual_rate', 0))
            gross_wt = float(request.POST.get('gross_wt', 0))
            discount = float(request.POST.get('discount', 0))
            rate = float(request.POST.get('rate', 0))
            amount = float(request.POST.get('amount', 0))

            # total_quantity += quantity
            # total_amount += amount

            # # Tax Calculation (5%)
            # tax_total = total_amount * 0.05

            # # Round-off Calculation
            # rounded_total = total_amount + tax_total
            # round_off = round(rounded_total) - rounded_total
            # grand_total = rounded_total + round_off

            # Create parent PO entry
            material_request = parent_po_table.objects.create(
                po_date=po_date, 
                name = name,
                party_id=supplier_id,
                mill_id=order_through,
                company_id=company_id,
                cfyear = 2025,
                remarks=remarks,
                
                yarn_count_id = product_id,
                bag=bag,
                per_bag=per_bag,
                quantity=quantity, 
                rate=actual_rate,
                gross_quantity=gross_wt,
                discount=discount,
                net_rate=rate,
                amount=amount,

                is_active=1,
                status=1,
                created_by=user_id,
                updated_by=user_id,
                created_on=timezone.now(),
                updated_on=timezone.now()
            )

        

            for contact in delivery_data: 
                try:
                    print("Processing Delivery:", contact)  # Debugging
                    bag = int(contact['bag'])
                    bag_wt = float(contact['bag_wt'])
                    qty = bag * bag_wt

                    print('qty:', qty)
                    yarn_po_delivery_table.objects.create(
                        yarn_count_id =product_id,
                        tm_po_id=material_request.id,
                        company_id=company_id,
                        cfyear=2025,
                        party_id=int(contact['knitting_id']),
                        delivery_date=contact['delivery_date'],
                        bag=bag,
                        bag_wt=bag_wt,
                        quantity=qty,
                        is_active=1,
                        status=1,
                        created_by=user_id,
                        updated_by=user_id, 
                        created_on=timezone.now(),
                        updated_on=timezone.now()
                    )
                    print("✅ Delivery added successfully!")
                except Exception as e:
                    print("❌ Error adding delivery:", str(e))
 



            return JsonResponse({'status': 'Success', 'message': 'Purchase order and delivery data saved successfully.'})
        
        except Exception as e:
            # traceback.print_exc()
            return JsonResponse({'status': 'Failed', 'message': str(e)}, status=500)

    return render(request, 'purchase/purchase_order.html')

 

def yarn_po_details(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'purchase/yarn_po_details.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'purchase/yarn_po_details.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = parent_po_table.objects.filter(id=material_id).first()
        if not material_instance:
            
            product_id = request.POST.get('product_id')  # Adjust as per your input structure
            bag = request.POST.get('bag')  # Adjust as per your input structure
            per_bag = request.POST.get('per_bag')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            net_rate = request.POST.get('rate')  # Adjust as per your input structure
            amount = request.POST.get('amount')  # Adjust as per your input structure

            # Ensure valid data before saving
            if product_id and bag and quantity:
                material_instance = parent_po_table.objects.create(
                    id=material_id,
                    yarn_count_id=product_id,
                    bag=bag,
                    per_bag=per_bag,
                    rate=net_rate,
                    quantity=quantity,
                    amount=amount,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'purchase/yarn_po_details.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = parent_po_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'purchase/yarn_po_details.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try:
                supplier = party_table.objects.get(id=parent_stock_instance.party_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_knitting=1)
        party = party_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        context = {
            'material_instance': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'party': party,
            'supplier_id': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'count':count
        }
        return render(request, 'purchase/yarn_po_details.html', context)

    except Exception as e:
        return render(request, 'purchase/yarn_po_details.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



def yarn_po_delivery_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id:
            try:
                # Fetch child PO data
                child_data = yarn_po_delivery_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)
           
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

                        'bag_wt': item['bag_wt'] if item['bag_wt'] else '-',
                        'bag': item['bag'] if item['bag'] else '-',
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



from django.http import JsonResponse
from django.db.models import Sum

def get_allowed_bags(request):
    tm_id = request.GET.get("tm_id")
    knitting_id = request.GET.get("knitting_id") 

    try:
        # Get the parent PO (assuming `bag` is the planned quantity)
        parent = parent_po_table.objects.get(id=tm_id)

        # Get the specific child PO (filtered by both tm and knitting)
        # child = child_po_table.objects.get(tm_po_id=tm_id, knitting_id=knitting_id)
        
        # Sum delivered bags for that tm + knitting
        delivered_total = yarn_po_delivery_table.objects.filter(
            tm_po_id=tm_id,
            party_id=knitting_id
        ).aggregate(total=Sum('bag'))['total'] or 0

        remaining = max(parent.bag - delivered_total, 0)

        return JsonResponse({'allowed_bags': remaining})
    except child_po_table.DoesNotExist:
        return JsonResponse({'allowed_bags': 0})
    except parent_po_table.DoesNotExist:
        return JsonResponse({'allowed_bags': 0})


# update or add po-deliverytable

@csrf_exempt
def add_deliver(request):
    if request.method == 'POST':
        company_id = request.session['company_id']


        try:
            # Parse incoming data
            data = json.loads(request.body)
            tm_id = data.get('tm_id')
            print('tm-id:',tm_id)
            knitting_id = data.get('knitting_id')
            deliver_date = data.get('deliver_date')
            deliver_bags = int(data.get('deliver_bags'))
            rate = data.get('rate')
            discount = data.get('discount')
            per_bag = data.get('per_bag')

            # Defensive extraction
            if isinstance(rate, dict): rate = rate.get('value', 0)
            if isinstance(discount, dict): discount = discount.get('value', 0)
            if isinstance(per_bag, dict): per_bag = per_bag.get('value', 0)
            pos = parent_po_table.objects.get(id=tm_id).first()
            print('pos:',pos)

            rate = float(rate)
            discount = float(discount)
            per_bag = float(per_bag)
            value = rate - discount
            price = value * per_bag
            amount_value = deliver_bags * per_bag
            # Get parent PO bag total
            try:
                parent_po = parent_po_table.objects.get(id=tm_id)
                print('parent-po:',parent_po)
                allowed_bags = parent_po.bag
            except parent_po_table.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid PO ID'})

            # Get delivered bag sum for tm_id only
            delivered_total = yarn_po_delivery_table.objects.filter(tm_po_id=tm_id).aggregate(
                total=Sum('bag'))['total'] or 0

            # Check if there's space to add new delivery
            if delivered_total + deliver_bags <= allowed_bags:
                # Add as a new row
                yarn_po_delivery_table.objects.create(
                    tm_po_id=tm_id,
                    company_id = company_id,
                    cfyear = 2025,
                    party_id=knitting_id,
                    delivery_date=deliver_date,
                    bag=deliver_bags,
                    bag_wt=per_bag,
                    quantity = amount_value,
                )
                return JsonResponse({'success': True, 'message': 'New delivery added successfully!'})
            else:
                # Update existing row for tm_id + knitting_id
                delivery = yarn_po_delivery_table.objects.filter(
                    tm_po_id=tm_id, knitting=knitting_id
                ).first()

                if delivery:
                    delivery.bag = deliver_bags
                    delivery.bag_wt = per_bag
                    delivery.quantity= amount_value
                    delivery.delivery_date = deliver_date
                    delivery.save()
                    return JsonResponse({'success': True, 'message': 'Existing delivery updated successfully!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Cannot add new entry and no existing row to update.'})

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
                    # parent_data = parent_po_table.objects.filter(id=master_id).first()
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
def delete_yarn_po(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        if not data_id:
            return JsonResponse({'message': 'PO ID is required.'})

        try:
            # Check if any inward entries for this PO have status ≠ 0 (i.e., still active)
            has_nonzero_status = sub_yarn_inward_table.objects.filter(
                po_id=data_id
            ).exclude(status=0).exists()
            po = parent_po_table.objects.filter(id=data_id).first()
            po_name = po.name
            if has_nonzero_status:
                return JsonResponse({
                    # 'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active.'
                    'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active. You must delete the inward first.'

                })

            # All inward entries are status=0, so proceed to soft-delete
            parent_po_table.objects.filter(id=data_id).update(status=0, is_active=0)
            yarn_po_delivery_table.objects.filter(tm_po_id=data_id).update(status=0, is_active=0)

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
    data = yarn_po_delivery_table.objects.filter(id=request.POST.get('id'))
    print('po-data:',data)
    return JsonResponse(data.values()[0])





def ypo_update(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        master_id = request.POST.get('tm_id')
        product_id = request.POST.get('product_id')
        bag = request.POST.get('bag')
        per_bag = request.POST.get('per_bag')
        quantity = request.POST.get('quantity')
        po_rate = request.POST.get('rate')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        amount = request.POST.get('amount')

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = parent_po_table.objects.get(id=master_id)
            parent_item.yarn_count_id = product_id
            parent_item.name = name
            parent_item.bag = bag
            parent_item.per_bag = per_bag
            parent_item.quantity = quantity
            parent_item.rate = po_rate
            parent_item.net_rate = price
            parent_item.discount = discount
            parent_item.amount = amount
            parent_item.save()

            return JsonResponse({'success': True, 'message': 'PO item updated successfully'})

        except parent_po_table.DoesNotExist:
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

        if not data_id:
            return JsonResponse({'message': 'PO ID is required.'})

        try: 
            po = parent_po_table.objects.filter(id=data_id).first()

            # Check if any inward entries for this PO have status ≠ 0 (i.e., still active)
            has_nonzero_status = sub_yarn_inward_table.objects.filter(
                po_id=po.id
            ).exclude(status=0).exists()
            po_name = po.name
            if has_nonzero_status:
                return JsonResponse({
                    # 'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active.'
                    'message': f'Cannot delete: PO ({po_name}) has inward entries that are still active. You must delete the inward first.'

                })

            # All inward entries are status=0, so proceed to soft-delete
            # parent_po_table.objects.filter(id=data_id).update(status=0, is_active=0)
            yarn_po_delivery_table.objects.filter(tm_po_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            print("Error during deletion:", e)
            return JsonResponse({'message': 'Error occurred during deletion.'})

    return JsonResponse({'message': 'Invalid request method'})



# `````````````````````````````` DYEING PROGRAM ```````````````````````````````````````````
 

def dyeing_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)

        last_purchase = gf_inward_table.objects.order_by('-id').first()
        if last_purchase: 
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist


        return render(request,'program/dyeing_program_list.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    



def add_dyeing_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)

        last_purchase = gf_inward_table.objects.order_by('-id').first()
        if last_purchase: 
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist


        return render(request,'program/dyeing_program.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    



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


# def get_fabric_details(request):
#     fabric_id = request.GET.get('fabric_id')
#     if fabric_id:
#         try:
#             # Fetch Color IDs mapped to the fabric
#             fabric = fabric_program_table.objects.get(id=fabric_id)
#             color_ids = fabric.color_id.split(",")  # Assuming color_id is stored as a comma-separated string
#             colors = color_table.objects.filter(id__in=color_ids).values("id", "name")


#             dia_ids = fabric.dia_id.split(",")  # Assuming color_id is stored as a comma-separated string
#             dia_values = dia_table.objects.filter(id__in=dia_ids).values("id", "name")



#             # Fetch Dia values mapped to the fabric
#             # dia_values = fabric_dia_table.objects.filter(fabric_prg_id=fabric_id).values_list("dia", flat=True)
#             # dia_values = sorted(list(set(dia_values)))  # Sort and remove duplicates

#             return JsonResponse({
#                 "success": True,
#                 "colors": list(colors),
#                 "dia_values": list(dia_values),
#                 # "dia_values": dia_values
#             })
#         except fabric_program_table.DoesNotExist:
#             return JsonResponse({"success": False, "message": "Fabric not found"})
#     return JsonResponse({"success": False, "message": "Invalid request"})


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

def clean_numeric(value):
    """Extracts only the numeric part from a value (removes non-numeric characters)."""
    return re.sub(r"[^\d.]", "", value)  # Removes everything except digits and decimal points

def save_dyeing_program(request):
    if request.method == "POST": 
        try:
            with transaction.atomic():
                party_id = request.POST.get("party_id")
                program_date = request.POST.get("program_date")
                total_rolls = clean_numeric(request.POST.get("total_rolls", "0"))  # Remove non-numeric
                total_wt = clean_numeric(request.POST.get("total_wt", "0"))  # Remove non-numeric
                remarks = request.POST.get("remarks", "")
                created_by = request.user.id

                # Create main dyeing program record
                main_program = dyeing_program_table.objects.create(
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

def save_dyeing_program_555(request):
    if request.method == "POST": 
        try:
            with transaction.atomic():
                # Fetch and validate program date
                # program_date_str = request.POST.get("program_date", "").strip()
                # program_date = parse_date(program_date_str)

                # if not program_date:
                #     return JsonResponse({"success": False, "message": "Invalid program date format."})

                party_id = request.POST.get("party_id")
                program_date = request.POST.get("program_date")
                total_rolls = request.POST.get("total_rolls", 0)
                total_wt = request.POST.get("total_wt", 0)
                remarks = request.POST.get("remarks", "")
                created_by = request.user.id

                # Create main dyeing program record
                main_program = dyeing_program_table.objects.create(
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
                rolls_values = request.POST.getlist("rolls[]")
                wt_values = request.POST.getlist("wt[]")

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




def dyeing_program_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(dyeing_program_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="dyeing_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="dyeing_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="gcf_po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'program_date': item['program_date'] if item['program_date'] else'-', 
            'party_id':getSupplier(party_table, item['party_id'] ), 
            'total_rolls': item['total_rolls'] if item['total_rolls'] else'-', 
            'total_wt': item['total_wt'] if item['total_wt'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 



def dyeing_program_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'program/update_dyeing_program.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'program/update_dyeing_program.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_dyeing_program_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            fabric_id = request.POST.get('fabric_id')  # Adjust as per your input structure
            color_id = request.POST.get('color_id')  # Adjust as per your input structure
            dia_id = request.POST.get('dia_id')  # Adjust as per your input structure
            rolls = request.POST.get('rolls')  # Adjust as per your input structure
            wt_per_roll = request.POST.get('wt_per_roll')  # Adjust as per your input structure

            # Ensure valid data before saving
            if fabric_id :
                material_instance = sub_dyeing_program_table.objects.create(
                    tm_id=material_id,
                    fabric_id=fabric_id,
                    color_id=color_id,
                    dia_id=dia_id,
                    rolls=rolls,
                    wt_per_roll=wt_per_roll, 
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'program/update_dyeing_program.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = dyeing_program_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'program/update_dyeing_program.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try: 
                supplier = party_table.objects.get(id=parent_stock_instance.party_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        product = fabric_program_table.objects.filter(status=1)
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_process=1,status=1)
        count = count_table.objects.filter(status=1) 
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)

        fabric_program = fabric_program_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
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
            'dia':dia,
            'fabric_program':fabric_program
        }
        return render(request, 'program/update_dyeing_program.html', context)

    except Exception as e:
        return render(request, 'program/update_dyeing_program.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



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





def tm_dyeing_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)
 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        prg_id = request.POST.get('prg_id')
        print('id:',prg_id)
        remarks = request.POST.get('remarks')
        # is_active = request.POST.get('is_active')
        
        try:
            tm = dyeing_program_table.objects.get(id=prg_id)
            tm.remarks = remarks
            # tm.is_active = is_active
            tm.updated_by = user_id
            tm.updated_on = datetime.now()
            tm.save()
            return JsonResponse({'message': 'success','remarks':remarks})
        except dyeing_program_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'tm not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})





# ```````````````````````````````````````````cutting program `````````````````````````````




def cutting_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)

        last_purchase = gf_inward_table.objects.order_by('-id').first()
        if last_purchase: 
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist


        return render(request,'program/cutting_program_list.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    


 
def cutting_program_view(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(cutting_program_table.objects.filter(status=1).order_by('-id').values())
 
    formatted = [
        {
            'action': '<button type="button" onclick="cutting_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="cutting_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="cutting_prg__print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'program_date': item['date'] if item['date'] else'-', 
            'party_id':getSupplier(party_table, item['party_id'] ), 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 


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
        parent_data = parent_gcf_delivery_table.objects.filter(id=tm_id).first()
        tax_total = parent_data.total_tax if parent_data else 0

        # Convert queryset to list 
        child_data = list(child_qs.values())

        # Format response data
        formatted_data = [
            {
                'action': '<button type="button" onclick="cut_prg_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                           <button type="button" onclick="tx_cutting_prg_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
                'id': index + 1,
                'size_id': getSupplier(size_table, item['size_id']),
                'color_id': getSupplier(color_table, item['color_id']),
                'quantity': item['quantity'] if item['quantity'] else '-',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            }
            for index, item in enumerate(child_data)
        ]

        return JsonResponse({'data': formatted_data, 'total_quantity': total_quantity, 'tax_total': tax_total})

    else:
        return JsonResponse({'error': 'No cutting program data found for this TM ID'})



def add_cutting_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_cutting=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 

        last_purchase = cutting_program_table.objects.order_by('-id').first()
        if last_purchase:  
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist
        print('prg-no:',prg_number) 

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        return render(request,'program/cutting_program/add_cutting_program.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number,'color':color
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
def save_cutting_program(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try:
            # Extracting Data from Request  
            party_id = request.POST.get('party_id',0) 
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            program_date = request.POST.get('delivery_date')
            cutting_data = json.loads(request.POST.get('cutting_data', '[]'))

            print('Chemical Data:', cutting_data)

            def clean_amount(amount):
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()

            # Create Parent Entry (gf_inward_table)
            material_request = cutting_program_table.objects.create(
                date=program_date, 
                party_id=party_id,
                quality_id=quality_id,
                style_id=style_id,
                company_id=company_id,
                total_quantity=clean_amount(request.POST.get('total_quantity')),
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )

            po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for cutting in cutting_data:
                print("Processing cutting Data:", cutting)
 
                po_id = cutting.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later

                sub_entry = sub_cutting_program_table.objects.create(
                    tm_id=material_request.id,  
                    size_id=cutting.get('size_id'), 
                    color_id=cutting.get('color_id'),
                    quantity=cutting.get('quantity'),
                    created_by=user_id,
                    created_on=timezone.now()
                )


                print("Sub Table Entry Created:", sub_entry) 
 
           
            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'program/cutting_program/add_cutting_program.html')




def cutting_program_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'program/cutting_program/update_cutting_program.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'program/cutting_program/update_cutting_program.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
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
                return render(request, 'program/cutting_program/update_cutting_program.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = cutting_program_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'program/cutting_program/update_cutting_program.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try: 
                supplier = party_table.objects.get(id=parent_stock_instance.party_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_process=1,status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
     

       
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            'supplier_name': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'size':size,
            'color':color,
            'quality':quality,
            'style':style,
           
        }
        return render(request, 'program/cutting_program/update_cutting_program.html', context)

    except Exception as e:
        return render(request, 'program/cutting_program/update_cutting_program.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




def edit_cutting_prg_detail(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = sub_cutting_program_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  





from django.http import JsonResponse

def add_or_update_cutting_program(request):
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

def check_existing_cutting_program(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        size_id = request.POST.get('size_id')
        color_id = request.POST.get('color_id')

        # Check if a record with the same tm_id, size_id, and color_id exists
        exists = sub_cutting_program_table.objects.filter(
            tm_id=tm_id, size_id=size_id, color_id=color_id
        ).exists()

        return JsonResponse({'exists': exists})
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



# ``````````````````````````````````````````````   cutting entry ``````````````````````````````````````````


def cutting_entry(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)

        last_purchase = gf_inward_table.objects.order_by('-id').first()
        if last_purchase: 
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist


        return render(request,'program/cutting_entry/cutting_entry_list.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number})
    else:
        return HttpResponseRedirect("/admin")
    


 
def cutting_entry_view(request):   
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:  
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(cutting_entry_table.objects.filter(status=1).order_by('-id').values())
 
    formatted = [
        {
            'action': '<button type="button" onclick="cutting_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="cutting_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="cutting_prg__print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'program_date': item['date'] if item['date'] else'-', 
            'party_id':getSupplier(party_table, item['party_id'] ), 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 


 
from django.http import JsonResponse
from django.db.models import Sum

def tx_cutting_entry_list(request):
    tm_id = request.POST.get('tm_id')

    # Fetch child data
    child_qs = sub_cutting_entry_table.objects.filter(status=1, tm_id=tm_id).order_by('-id')
    
    if child_qs.exists():
        # Calculate total quantity from child table
        total_quantity = child_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_wt = child_qs.aggregate(Sum('wt'))['wt__sum'] or 0

        # Fetch tax total from the parent table
        parent_data = cutting_entry_table.objects.filter(id=tm_id).first()
        # tax_total = parent_data.total_tax if parent_data else 0

        # Convert queryset to list 
        child_data = list(child_qs.values())

        # Format response data
        formatted_data = [
            {
                'action': '<button type="button" onclick="cut_entry_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                           <button type="button" onclick="tx_cutting_entry_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
                'id': index + 1,
                'size_id': getSupplier(size_table, item['size_id']),
                'color_id': getSupplier(color_table, item['color_id']),
                'balance_qty': item['balance_qty'] if item['balance_qty'] else '-',
                'quantity': item['quantity'] if item['quantity'] else '-',
                'wt': item['wt'] if item['wt'] else '-',
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            }
            for index, item in enumerate(child_data)
        ]

        return JsonResponse({'data': formatted_data, 'total_quantity': total_quantity,'total_wt':total_wt })

    else:
        return JsonResponse({'error': 'No cutting program data found for this TM ID'})



def add_cutting_entry(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_cutting=1) 
        fabric_program = fabric_program_table.objects.filter(status=1) 

        last_purchase = cutting_entry_table.objects.order_by('-id').first()
        if last_purchase:  
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist
        print('prg-no:',prg_number) 

        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        cutting_program = cutting_program_table.objects.filter(status=1,is_entry=0)
        return render(request,'program/cutting_entry/add_cutting_entry.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number,'color':color
                                                                  ,'cutting_program':cutting_program,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
     


def get_cutting_program_lists(request):
    party_id = request.POST.get('party_id')
    programs = cutting_program_table.objects.filter(party_id=party_id,is_entry=0).values('id', 'cutting_no', 'total_quantity', 'quality_id', 'style_id')
    
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


@csrf_exempt
def save_cutting_entry(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try: 
            # Extracting Data from Request  
            party_id = request.POST.get('party_id',0) 
            print('party-id;',party_id)
            prg_id = request.POST.get('prg_id')
            prg_quantity = request.POST.get('prg_quantity') 
            print('prg-qty:',prg_quantity)
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            style_id = request.POST.get('style_id')
            program_date = request.POST.get('program_date')
            cutting_data = json.loads(request.POST.get('cutting_data', '[]'))

            print('Chemical Data:', cutting_data)

            def clean_amount(amount):
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()

            # Create Parent Entry (gf_inward_table)
            material_request = cutting_entry_table.objects.create(
                date=program_date, 
                tm_cutting_prg_id = prg_id,
                prg_quantity = prg_quantity,
                party_id=party_id,
                quality_id=quality_id, 
                style_id=style_id,
                company_id=company_id,
                # total_quantity=request.POST.get('total_quantity'),
                # total_wt=request.POST.get('total_wt'),
                # loss_qty =request.POST.get('lo_totalQty'),
                # loss_wt =request.POST.get('lo_totalwt'),
                # shortage_qty =request.POST.get('sh_totalQty'),
                # shortage_wt=request.POST.get('sh_totalwt'),
                # balance_qty =request.POST.get('b_totalQty'),
                # grand_total_qty =request.POST.get('grand_totqty'),
                # grand_total_wt =request.POST.get('grand_totalwt'),

                total_quantity=request.POST.get('total_quantity'),
                total_wt=request.POST.get('total_wt'),
                loss_qty=request.POST.get('lo_totalQty'),
                loss_wt=request.POST.get('lo_totalwt'),
                shortage_qty=request.POST.get('sh_totalQty'),
                shortage_wt=request.POST.get('sh_totalwt'),
                balance_qty=request.POST.get('b_totalQty'),
                grand_total_qty=request.POST.get('grand_totqty'),
                grand_total_wt=request.POST.get('grand_totalwt'),
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )

            po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for cutting in cutting_data:
                print("Processing cutting Data:", cutting)
 
                po_id = cutting.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later

                sub_entry = sub_cutting_entry_table.objects.create(
                    tm_id=material_request.id,  
                    size_id=cutting.get('size_id'),  
                    color_id=cutting.get('color_id'),
                    quantity=cutting.get('quantity'),
                    balance_qty=cutting.get('balance_qty'),
                    original_qty=cutting.get('original_quantity'),
                    wt=cutting.get('wt'),
                    created_by=user_id,
                    created_on=timezone.now()
                )


                print("Sub Table Entry Created:", sub_entry) 
                program = cutting_program_table.objects.get(id=prg_id)
                program.is_entry = 1
                program.updated_by = user_id
                program.updated_on = timezone.now()
                program.save()

           
            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'program/cutting_entry/add_cutting_entry.html')

 




def cutting_entry_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'program/cutting_entry/update_cutting_entry.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'program/cutting_entry/update_cutting_entry.html', {'error_message': 'Invalid ID format.'})

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
                return render(request, 'program/cutting_entry/update_cutting_entry.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = cutting_entry_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'program/cutting_entry/update_cutting_entry.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try: 
                supplier = party_table.objects.get(id=parent_stock_instance.party_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_cutting=1,status=1)
        
        quality = quality_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1) 
        style = style_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        cutting_program = cutting_program_table.objects.filter(status=1)

       
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance, 
            'parent_stock_instance': parent_stock_instance, 
            'party': party,
            'supplier_name': supplier_name,  # Pass the supplier name to the template
            'supplier': supplier,
            'size':size,
            'color':color,
            'quality':quality,
            'style':style,
            'cutting_program':cutting_program
           
        }
        return render(request, 'program/cutting_entry/update_cutting_entry.html', context)

    except Exception as e:
        return render(request, 'program/cutting_entry/update_cutting_entry.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




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

def add_or_update_cutting_entry(request):
    if request.method == 'POST':
        master_id = request.POST.get('id')  # The ID of the row (if updating)
        tm_id = request.POST.get('tm_id')   # The transaction master ID
        size_id = request.POST.get('size_id')
        color_id = request.POST.get('color_id')
        quantity = request.POST.get('quantity')
        balance_qty = request.POST.get('balance_qty')
        wt = request.POST.get('wt')

        print('tm-id:', tm_id) 

        # Validate required fields
        if not tm_id or not size_id or not quantity:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Check if the same tm_id, size_id, and color_id already exist
            existing_item = sub_cutting_entry_table.objects.filter(
                tm_id=tm_id,
                size_id=size_id,
                color_id=color_id
            ).first()

            if existing_item:
                # Update existing entry
                existing_item.quantity = quantity
                existing_item.wt = wt
                existing_item.balance_qty = balance_qty
                existing_item.save()
                updated_totals = update_values(tm_id)  # Update totals
                return JsonResponse({'success': True, 'updated': True, **updated_totals})

            else:
                # Create a new row if no existing entry
                child_item = sub_cutting_entry_table.objects.create(
                    tm_id=tm_id,
                    color_id=color_id,
                    size_id=size_id,
                    quantity=quantity,
                    balance_qty=balance_qty,
                    wt=wt,
                    status=1,
                    is_active=1
                )
                updated_totals = update_values(tm_id)  # Update totals
                return JsonResponse({'success': True, 'created': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


 

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



# `````````````````````` accessory program ````````````````````````````````````````````````````````````````



def accessory_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)

        last_purchase = gf_inward_table.objects.order_by('-id').first()
        if last_purchase: 
            prg_number = last_purchase.id + 1
        else:
            prg_number = 1  # Default if no records exist


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
            'action': '<button type="button" onclick="cutting_program_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="cutting_program_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="cutting_prg__print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'program_date': item['date'] if item['date'] else'-', 
            'party_id':getSupplier(party_table, item['party_id'] ), 
            'quality':getSupplier(accessory_quality_table, item['quality_id'] ), 
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

        quality = accessory_quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)  
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        cutting_program = cutting_program_table.objects.filter(status=1,is_entry=0)
        accessory_item = item_table.objects.filter(status=1)
        fabric = fabric_program_table.objects.filter(status=1)
        uom = uom_table.objects.filter(status=1) 
        return render(request,'program/accessory_prg/add_accessory_program.html',{'party':party,'fabric_program':fabric_program,'prg_number':prg_number,'color':color
                                                            ,'uom':uom,'fabric':fabric,'accessory_item':accessory_item,'cutting_program':cutting_program,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
     


@csrf_exempt
def save_accessory_program(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try:
            # Extracting Data from Request  
            party_id = request.POST.get('party_id', 0) 
            remarks = request.POST.get('remarks')
            quality_id = request.POST.get('quality_id')
            program_date = request.POST.get('program_date')
            cutting_data = json.loads(request.POST.get('cutting_data', '[]'))

            total_quantity = request.POST.get('total_quantity', 0)

            print('Cutting Data:', cutting_data) 

            # Create Parent Entry
            material_request = accessory_program_table.objects.create(
                date=program_date, 
                party_id=party_id,
                quality_id=quality_id,
                company_id=company_id,
                total_quantity=total_quantity,
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )

            for cutting in cutting_data:
                sub_entry = sub_accessory_program_table.objects.create(
                    tm_id=material_request.id,  
                    uom_id=cutting.get('uom_id'), 
                    item_id=cutting.get('item_id'), 
                    program_type=cutting.get('program_type'), 
                    product_pieces=cutting.get('product_pieces'),
                    quantity=cutting.get('quantity'), 
                    created_by=user_id, 
                    created_on=timezone.now() 
                )

                print("Sub Table Entry Created:", sub_entry) 

            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'})

        except Exception as e:
            print(f"Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)})

    return render(request, 'program/accessory_prg/add_accessory_program.html')


# @csrf_exempt
# def save_accessory_program(request):
#     if request.method == 'POST':
#         user_id = request.session.get('user_id')  # Prevent KeyErrors
#         company_id = request.session.get('company_id')

#         try:
#             # Extracting Data from Request  
#             party_id = request.POST.get('party_id',0) 
#             remarks = request.POST.get('remarks')
#             quality_id = request.POST.get('quality_id')
#             # item_id = request.POST.get('item_id')
#             program_date = request.POST.get('delivery_date')
#             cutting_data = json.loads(request.POST.get('cutting_data', '[]'))

#             print('Chemical Data:', cutting_data)

#             def clean_amount(amount):
#                 """Remove currency symbols and commas from amount values."""
#                 return amount.replace('₹', '').replace(',', '').strip()

#             # Create Parent Entry (gf_inward_table)
#             material_request = accessory_program_table.objects.create(
#                 date=program_date, 
#                 party_id=party_id,
#                 quality_id=quality_id,
#                 # item_id=item_id,
#                 company_id=company_id,
#                 total_quantity=request.POST.get('total_quantity'),
#                 remarks=remarks, 
#                 created_by=user_id,
#                 created_on=timezone.now()
#             )

#             po_ids = set()  # Store unique PO IDs to update later

#             # Create Sub Table Entries
#             for cutting in cutting_data:
#                 print("Processing cutting Data:", cutting)
 
#                 po_id = cutting.get('tm_id')  # Get PO ID
#                 po_ids.add(po_id)  # Store for updating later

#                 sub_entry = sub_accessory_program_table.objects.create(
#                     tm_id=material_request.id,  
#                     item_id=cutting.get('item_id'), 
#                     program_type=cutting.get('program_type'), 
#                     product_pieces=cutting.get('product_pieces'),
#                     quantity=cutting.get('quantity'),
#                     created_by=user_id,
#                     created_on=timezone.now()
#                 )


#                 print("Sub Table Entry Created:", sub_entry) 
 
           
#             # Return a success response
#             return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

#         except Exception as e:
#             print(f" Error: {e}")  # Log error
#             return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

#     return render(request, 'program/accessory_prg/add_accessory_program.html')


@csrf_exempt  # Use only if necessary
def get_quality_item_list(request):
    if request.method == 'POST':
        quality_id = request.POST.get('quality_id')

        if not quality_id:
            return JsonResponse({'error': 'Quality ID is required'}, status=400)

        try:
            # Retrieve all fabric programs for the given quality_id
            fabric_programs = sub_item_table.objects.filter(quality_id=quality_id)

            if not fabric_programs.exists():
                return JsonResponse({'error': 'No matching records found'}, status=404)

            # Collect all styles linked to the fabric programs
            items = fabric_programs.values_list('item_id', flat=True).distinct()
            items = item_table.objects.filter(id__in=items).values('id', 'name')

            # Get all quality_program_table IDs to use as tm_id
            # program_ids = fabric_programs.values_list('id', flat=True)

            # # Fetch all sizes and colors linked to these program IDs
            # sub_programs = sub_quality_program_table.objects.filter(tm_id__in=program_ids).values('size_id').distinct()
            # sizes = size_table.objects.filter(id__in=sub_programs).values('id', 'name')

            response_data = {
                'item': list(items),

                # 'sizes_colors': list(sub_programs)  # List of {size_id, color_id}
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

