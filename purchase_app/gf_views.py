

from os import stat
from traceback import print_tb
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import item_table
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
from yarn.models import *
from party.models import *
from program_app.models import *
from employee.models import *
from software_app.views import fabric_program, gauge, knitting_delivery
 


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 


# Create your views here. 
def purchase_order_gf(request): 
    if 'user_id' in request.session:  
        user_id = request.session['user_id']    
        print('user-id:',user_id)
        supplier = party_table.objects.filter(is_mill=1) 
        party = party_table.objects.filter(status=1,is_bleaching=1,is_dyeing=1)
        product = product_table.objects.filter(status=1)  
        count = count_table.objects.filter(status=1).order_by('count')
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1) 
        bag = bag_table.objects.filter(status=1) 
         # Get the last ID from parent_po_table and increment by 1
        last_purchase = parent_po_table.objects.order_by('-id').first()
        if last_purchase:
            purchase_number = last_purchase.id + 1
        else:
            purchase_number = 1  # Default if no records exist
        
        return render(request,'gf/add_purchase_order.html',{'supplier':supplier,'party':party,'product':product,'count':count,
                                                            'bag':bag,'gauge':gauge,'tex':tex,'purchase_number':purchase_number})
    else:
        return HttpResponseRedirect("/admin")


# def get_do_lists(request):
#     if request.method == 'POST' and 'supplier_id' in request.POST: 
#         supplier_id = request.POST['supplier_id']
#         print('supplier_id:', supplier_id) 

#         if supplier_id:
#             # Fetch all child purchase orders for the given supplier_id where is_assigned=0
#             child_orders = sub_knitting_deliver_table.objects.filter(
#                 tm_po_id__in=knitting_deliver_table.objects.filter(supplier_id=supplier_id,status=1).values('id'),
               
#             ).values('tm_po_id')  # Get the IDs of the parent orders

#             # Now filter parent purchase orders based on these IDs
#             order_number = knitting_deliver_table.objects.filter( 
#                 id__in=child_orders 
#             ).values('id', 'do_number').order_by('-id')

            
#             # Convert the queryset to a list
#             data = list(order_number)
#             # print('PO Numbers:', data)
#             return JsonResponse(data, safe=False)  # Return the list of purchase orders
         
#     return JsonResponse([], safe=False) 



def load_delivery_orders(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('do_id[]')  # Accept multiple PO IDs
        print('po-id:', po_ids)

        if not supplier_id or not po_ids:
            return JsonResponse({'error': 'Supplier ID and Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided supplier and PO IDs
            parent_pos = knitting_deliver_table.objects.filter(id__in=po_ids, supplier_id=supplier_id)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                # Retrieve child orders linked to each parent PO
                orders = sub_knitting_deliver_table.objects.filter(tm_id=po.id)

                for order in orders:
                    product = product_table.objects.filter(id=order.product_id).first()

                    # Get remaining values
                    # remaining_bag = order.remaining_bag or 0
                    # remaining_quantity = order.remaining_quantity or 0
                    # remaining_amount = order.remaining_amount or 0  

                    # # 🔹 **Omit entries where all three values are zero**
                    # if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
                    #     continue  # Skip this record

                    # Prepare order details
                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "Unknown Product", 
                        'tax_value': 5,  
                        'bag': order.bag,
                        'per_bag': order.per_bag,  
                        # 'actual_rate':order.actual_rate,
                        # 'discount':order.discount ,
                        # 'gross_wt':   order.gross_wt, 


                        'quantity': order.quantity,
                        'rate': order.rate,
                        'amount': order.amount,
                        'id': order.id,
                        'tm_id': order.tm_id,
                        'tm_po_id': order.tm_po_id,
                        'tx_id': order.id,
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

 


from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from datetime import date


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
            # do_date = request.POST.get('delivery_date')
            supplier_id = request.POST.get('supplier_id')
            remarks = request.POST.get('remarks') 
            # chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            delivery_data = json.loads(request.POST.get('delivery_data', '[]'))
            print('delivery-data:',delivery_data)
            # print('chemical-data:',chemical_data)
            # Validate essential fields
            if not po_date or not supplier_id :
                return JsonResponse({'status': 'Failed', 'message': 'Missing essential purchase order information.'}, status=400)

            # Create a new parent_po_table instance
            material_request = gf_po_table.objects.create(
                purchase_date=po_date,  
                supplier_id=supplier_id,
                company_id=company_id,
                total_quantity=float(request.POST.get('quantity')), 
                total_amount=float(request.POST.get('total_amount')),
                round_off= 0,#request.POST.get('round_off'),
                tax_total= 0,#request.POST.get('tax_total'),
                grand_total= float(request.POST.get('total_amount')),#request.POST.get('total_payable'), 
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
            # for chemical in chemical_data:
            product_id = request.POST.get('fabric_id')
            quantity = request.POST.get('quantity')
            rolls = int(request.POST.get('rolls', 0))  # Convert rolls to an integer
            print('deivery-rolls:',rolls)

            if product_id and quantity and quantity != 'undefined':

                po_date_obj = datetime.strptime(po_date, "%Y-%m-%d")  # Adjust format if necessary
                year = po_date_obj.year
                month = po_date_obj.month

                # Determine financial year
                if month < 4:  # Jan, Feb, Mar → previous year as start
                    financial_year = f"{year - 1}-{year}"
                else:  # Apr to Dec → current year as start
                    financial_year = f"{year}-{year + 1}"

                #


                sub_gf_po_table.objects.create(
                    tm_po_id=material_request.id,
                    product_id=product_id,
                    bag=request.POST.get('bag'), 
                    bag_wt=request.POST.get('bag_wt'), 
                    rate=request.POST.get('rate'),
                    quantity=request.POST.get('quantity'),
                    total_amount=request.POST.get('total_amount'),
                    is_active=1,
                    status=1,
                    created_by=user_id,
                    updated_by=user_id,
                    created_on=timezone.now(),
                    updated_on=timezone.now()
                )
                # else:
                #     print('Invalid chemical entry:', chemical)
 
            for contact in delivery_data: 
                company_name = contact.get('company_name')
                knitting = contact.get('knitting_id')
                # fabric_id = contact.get('fabric_id') 
                delivery_date = contact.get('delivery_date')
                
                try:
                    delivered_rolls = int(contact.get('bags', 0))  # Convert to integer
                except ValueError:
                    delivered_rolls = 0  # Default to 0 if conversion fails

                if company_name and knitting and delivery_date and delivered_rolls:
                    gf_delivery_table.objects.create(
                        tm_po_id=material_request.id,
                        company_name=company_name, 
                        knitting_id=knitting,
                        # fabric_id=fabric_id,
                        delivery_date=delivery_date,
                        bags=delivered_rolls,
                        is_active=1,
                        status=1,
                        created_by=user_id,
                        updated_by=user_id,
                        created_on=timezone.now(),
                        updated_on=timezone.now()
                    )
                else:
                    print('Invalid delivery entry:', contact)

         
         
            # for chemical in chemical_data:
            #     fabric_id = chemical.get('fabric_id') or chemical.get('product_id')  # Try both keys
            #       # ✅ Use 'chemical' instead of 'contact'
            #     print('Checking balance for fabric_id:', fabric_id)

            #     try:
            #         required_rolls = int(chemical.get('rolls', 0))  # Convert to integer
            #     except ValueError:
            #         required_rolls = 0  # Default to 0 if conversion fails

            #     # Get total delivered rolls for this specific fabric_id
            #     total_delivered_rolls = gf_delivery_table.objects.filter(
            #         tm_po_id=material_request.id,
            #         fabric_id=fabric_id,  # ✅ Corrected to 'fabric_id'
            #         is_active=1
            #     ).aggregate(total_rolls=models.Sum('rolls'))['total_rolls'] or 0

            #     print('delivered-roll:', total_delivered_rolls)

            #     # Calculate balance rolls
            #     if total_delivered_rolls < required_rolls:
            #         balance_rolls = required_rolls - total_delivered_rolls
            #         print('balance-roll:', balance_rolls) 


            #         # Insert missing rolls with knitting = 0 
            #         gf_delivery_table.objects.create( 
            #             tm_po_id=material_request.id, 
            #             company_name='Mirra', 
            #             knitting_id=0,  # Mark as pending 
            #             delivery_date=date.today(),  # Use 'do_date' or fetch a relevant date
            #             rolls=balance_rolls,
            #             fabric_id=fabric_id,  # ✅ Corrected
            #             is_active=1, 
            #             status=1,
            #             created_by=user_id,
            #             updated_by=user_id,
            #             created_on=timezone.now(),
            #             updated_on=timezone.now()
            #         )
            #         print(f"Added missing {balance_rolls} rolls for fabric_id {fabric_id}")

          

            return JsonResponse({'status': 'Success', 'message': 'Purchase order and delivery data saved successfully.'})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'Failed', 'message': 'An error occurred while processing the request.'}, status=500)

    return render(request, 'gf/add_purchase_order.html')





def gf_po_details_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'gf/purchase_detail_update.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'gf/purchase_detail_update.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_gf_po_table.objects.filter(tm_po_id=material_id).first()
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
                material_instance = sub_gf_po_table.objects.create(
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
                return render(request, 'gf/purchase_detail_update.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = gf_po_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'gf/purchase_detail_update.html', {'error_message': 'Parent stock not found.'})

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
        return render(request, 'gf/purchase_detail_update.html', context)

    except Exception as e:
        return render(request, 'gf/purchase_detail_update.html', {'error_message': 'An unexpected error occurred: ' + str(e)})



def gf_po_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting
            gf_po_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_gf_po_table.objects.filter(tm_po_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except gf_po_table  & sub_gf_po_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})






def gf_po_page(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'gf/purchase_order_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")





 

def purchase_order_view(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(gf_po_table.objects.filter(status=1).order_by('-id').values()) 

    formatted = [
        {
            'action': '<button type="button" onclick="gf_po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="gf_po_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'po_no': item['po_number'] if item['po_number'] else'-', 
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



def update_gf_po_view(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data
                child_data = sub_gf_po_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = gf_po_table.objects.filter(id=master_id).first()
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
                            'action': '<button type="button" onclick="gf_purchase_order_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="gf_purchase_order_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
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
        tx = sub_gf_po_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)

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
        gf_po_table.objects.filter(id=master_id).update(
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


def add_or_update_gf_po_item(request):
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
            child_item, created = sub_gf_po_table.objects.update_or_create(
                tm_po_id=master_id, product_id=product_id,
                defaults={
                    'count': count_id,
                    'gauge': gauge_id,
                    'tex':tex_id,
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





def gf_po_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_gf_po_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_gf_po_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


 
def gf_po_detail_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_gf_po_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])





# ```````````````````````````````````` Grey Fabric INWARD ````````````````````````````````````
import re

def generate_inward_num_series():
    last_purchase = gf_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_number:
        match = re.search(r'INV-(\d+)', last_purchase.inward_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"INV-{next_num:03d}"


def grey_fabric_inward(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        supplier = party_table.objects.filter( Q(status=1) & (Q(is_trader=1) | Q(is_knitting=1)))
        # supplier = party_table.objects.filter( Q(status=1) & Q(is_knitting=1))

            # status=1,is_knitting=1,is_trader=1) 
        party = party_table.objects.filter(status=1) 
        # product = product_table.objects.filter(status=1) 
        product = fabric_program_table.objects.filter(status=1) 
        count = count_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        purchase = parent_po_table.objects.filter(status=1,)     
        last_purchase = gf_inward_table.objects.order_by('-id').first()
        inward_number = generate_inward_num_series 
        delivers = yarn_delivery_table.objects.filter(status=1)

        prg_list = []  # Store all `prg` QuerySets

        for deliver in delivers: 
            print(deliver.id)  # ✅ Safe because we are iterating
            # po_ids = sub_knitting_deliver_table.objects.filter(status=1).values_list('inward_id', flat=True)
            po_ids = sub_yarn_deliver_table .objects.filter(status=1)
        

        # print('combined_prg:',combined_prg)
        knitting = knitting_table.objects.filter(status=1,is_inward=0) 
        print('knit:',knitting)
        dia = dia_table.objects.filter(status=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        return render(request,'gf/add_gf_inward.html',{'supplier':supplier,'party':party,'product':product,'count':count,'knitting':knitting,
                                                        'dia':dia,'fabric_program':fabric_program,'inward_number':inward_number,'gauge':gauge,'tex':tex,'purchase':purchase})
    else:
        return HttpResponseRedirect("/admin") 




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


# def load_gf_po_details(request):
#     if request.method == "GET":
#         # supplier_id = request.GET.get('supplier_id')
#         po_ids = request.GET.getlist('po_id[]')  # Accept multiple PO IDs
#         print('po-id:', po_ids)

#         if  not po_ids:
#             return JsonResponse({'error': ' Purchase Order ID(s) are required.'}, status=400)

#         try:
#             # Fetch parent purchase orders for the provided supplier and PO IDs
#             parent_pos = knitting_table.objects.filter(po_id__in=po_ids)

#             if not parent_pos.exists():
#                 return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

#             order_data = []
#             for po in parent_pos:
#                 # Retrieve child orders linked to each parent PO
#                 orders = sub_knitting_table.objects.filter(tm_id=po.id) 

#                 for order in orders:
#                     product = product_table.objects.filter(id=order.fabric_id).first()
#                     count = count_table.objects.filter(id=order.count).first()
#                     gauge = gauge_table.objects.filter(id=order.gauge).first()
#                     tex = tex_table.objects.filter(id=order.tex).first()

#                     # Get remaining values
#                     # remaining_bag = order.remaining_bag or 0
#                     # remaining_quantity = order.remaining_quantity or 0
#                     # remaining_amount = order.remaining_amount or 0

#                     # 🔹 **Omit entries where all three values are zero**
#                     # if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
#                     #     continue  # Skip this record
 
#                     # Prepare order details
#                     order_data.append({
#                         'product_id': order.fabric_id,
#                         'product': product.name if product else "Unknown Product", 
#                         'tax_value': 5,  
#                         'count_id':order.count,
#                         'gauge_id':order.gauge,
#                         'tex_id':order.tex,
#                         'dia':order.dia,
#                         'rolls':order.rolls,
#                         'wt_per_roll':order.wt_per_roll,
#                         'price':order.rate,
#                         'quantity':order.quantity,
#                         'total_amount':order.total_amount,
#                         'count':count.count if count else "Unknown count", 
#                         'gauge':gauge.name if gauge else "Unknown gauge", 
#                         'tex':tex.name if tex else "Unknown tex", 
#                         'id': order.id,
#                         'tm_id': order.tm_id,
#                         'tx_id': order.id,
#                         'lot_no':po.lot_no,
#                         'tm_po_id':order.tm_po_id
#                     })

#             return JsonResponse({'orders': order_data})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method.'}, status=400)




def load_gf_po_details(request):
    if request.method == "GET":
        # supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')  # Accept multiple PO IDs
        print('po-id:', po_ids)

        if  not po_ids:
            return JsonResponse({'error': ' Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided supplier and PO IDs
            parent_pos = knitting_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                # Retrieve child orders linked to each parent PO
                orders = sub_knitting_table.objects.filter(tm_po_id=po.id) 

                for order in orders:
                    product = fabric_program_table.objects.filter(id=order.fabric_id).first()
                    print('product_id:',order.fabric_id)
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
                        'product_id': order.fabric_id,
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
                        'tm_id': order.id,
                        'tx_id': order.id,
                        # 'lot_no':po.lot_no,
                        'tm_po_id':order.tm_po_id
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



from django.http import JsonResponse
import json
from django.utils import timezone

@csrf_exempt
def add_gf_inward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')  # Prevent KeyErrors
        company_id = request.session.get('company_id')

        try:
            # Extracting Data from Request  
            supplier_id = request.POST.get('supplier_id')
            remarks = request.POST.get('remarks')
            lot = request.POST.get('lot')
            print('lot:',lot)
            tm_prg = request.POST.get('prg_list')
            print('value:',lot,tm_prg)
            inward_date = request.POST.get('inward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            print('Chemical Data:', chemical_data)

            def clean_amount(amount):
                """Remove currency symbols and commas from amount values."""
                return amount.replace('₹', '').replace(',', '').strip()

            # Create Parent Entry (gf_inward_table)
            material_request = gf_inward_table.objects.create(
                inward_date=inward_date, 
                prg_id = tm_prg,
                supplier_id=supplier_id,
                lot_no=lot,
                company_id=company_id,
                total_quantity=   clean_amount(request.POST.get('total_quantity')),
                total_amount= clean_amount(request.POST.get('sub_total')),
                tax_total= clean_amount(request.POST.get('tax_total')),
                grand_total= clean_amount(request.POST.get('total_payable')),  
                remarks=remarks, 
                created_by=user_id,
                created_on=timezone.now()
            )
 
            po_ids = set()  # Store unique PO IDs to update later

            # Create Sub Table Entries
            for chemical in chemical_data:
                print("Processing Chemical Data:", chemical)
 
                po_id = chemical.get('tm_id')  # Get PO ID
                po_ids.add(po_id)  # Store for updating later

                sub_entry = sub_gf_inward_table.objects.create(
                    tm_id=material_request.id,  
                    do_id=chemical.get('do_id'),
                    tm_prg_id=tm_prg,
                    product_id=chemical.get('product_id'),
                    po_id=0,#chemical.get('tm_po_id'),
                    lot_no = 0,#chemical.get('lot_no'),
                    count=chemical.get('count_id'),
                    gauge=chemical.get('gauge_id'), 
                    tex=chemical.get('tex_id'),
                    gsm=chemical.get('gsm'),
                    dia=chemical.get('dia'), 
                    rolls=chemical.get('rolls'),
                    wt_per_roll=chemical.get('wt_per_roll'),
                    quantity=chemical.get('quantity'),
                    gross_wt=chemical.get('gross_wt'),
                    rate=clean_amount(chemical.get('rate')), 
                    total_amount=clean_amount(chemical.get('total_amount')),
                    created_by=user_id,
                    created_on=timezone.now()
                )


                print("Sub Table Entry Created:", sub_entry) 
 
            #  Update `is_completed=1` for the associated PO IDs
            prg = chemical.get('tm_id')
            update_knitting = knitting_table.objects.filter(id__in=prg).update(is_inward=1)
            # updated_count = gf_po_table.objects.filter(id__in=po_ids).update(is_inward=1)
            print(f" Updated {update_knitting} Purchase Inward as completed.")

            # Return a success response
            return JsonResponse({'status': 'yes', 'message': 'Data added successfully'}, safe=False)

        except Exception as e:
            print(f" Error: {e}")  # Log error
            return JsonResponse({'status': 'no', 'message': str(e)}, safe=False)

    return render(request, 'gf/add_gf_inward.html')





def gf_list(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'gf/gf_inward_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    

 

def gf_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access: 
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(gf_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="gf_inward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="gf_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="gf_po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_no': item['inward_number'] if item['inward_number'] else'-', 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'party_id':getSupplier(party_table, item['supplier_id'] ), 
            'prg_id':getSupplier(knitting_table, item['prg_id'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'tax_total': item['tax_total'] if item['tax_total'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 
 


def get_po_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('supplier_id:', supplier_id) 

        if supplier_id:
            # Fetch all child purchase orders for the given supplier_id where is_assigned=0
            child_orders = child_po_table.objects.filter(
                tm_po_id__in=parent_po_table.objects.filter(supplier_id=supplier_id,status=1,is_inward=0).values('id'),
               
            ).values('tm_po_id')  # Get the IDs of the parent orders

            # Now filter parent purchase orders based on these IDs
            order_number = parent_po_table.objects.filter( 
                id__in=child_orders 
            ).values('id', 'po_number').order_by('-id')

            knitting_prg = knitting_table.objects.filter( 
                id__in=child_orders 
            ).values('id', 'knitting_number','lot_no').order_by('-id')

            # Convert the queryset to a list
            data = list(order_number),list(knitting_prg)
            # print('PO Numbers:', data)
            return JsonResponse(data, safe=False)  # Return the list of purchase orders 
         
    return JsonResponse([], safe=False) 
 

# @csrf_exempt
# def get_do_lists(request):
#     if request.method == 'POST' and 'supplier_id' in request.POST:
#         supplier_id = request.POST['supplier_id']
#         print('deliver-id:', supplier_id) 

#         if supplier_id:
#             # First: Get only tm_ids
#             child_orders = sub_knitting_deliver_table.objects.filter(
#                 deliver_id=supplier_id 
#             ).values('tm_id').distinct()

#             # Extract only the tm_ids into a list
#             child_order_ids = [child['tm_id'] for child in child_orders]
#             print('child_order_ids:', child_order_ids)

#             # Now filter parent knitting orders
#             order_numbers = knitting_deliver_table.objects.filter( 
#                 id__in=child_order_ids, status=1
#             ).values('id', 'lot_no','do_number','prg_id').order_by('-id')

#             # Calculate total bags and quantity
#             total_bag_sum = 0
#             total_quantity_sum = 0 
#             for order in order_numbers: 
#                 child_order = sub_knitting_deliver_table.objects.filter(
#                     tm_id=order['id']
#                 ).filter(
#                     Q(bag__gt=0) | Q(gross_wt__gt=0)
#                 )
                
#                 for child in child_order:
#                     total_bag_sum += child.bag
#                     total_quantity_sum += child.gross_wt

#             # Prepare data
#             data = list(order_numbers)
             
#             return JsonResponse({
#                 'orders': data,
#                 'total_bag': total_bag_sum,
#                 'total_quantity': total_quantity_sum
#             }, safe=False)

#     return JsonResponse([], safe=False)




@csrf_exempt
def get_do_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('supplier_id:', supplier_id)

        if supplier_id:
            # Get child orders where remaining_bag > 0 or remaining_quantity > 0
            child_orders = sub_knitting_deliver_table.objects.filter(
                tm_id__in=knitting_deliver_table.objects.filter(deliver_to=supplier_id, status=1).values('id'),
            ).filter(
                Q(bag__gt=0) | Q(quantity__gt=0)
            ).values('tm_id').distinct()

            # Now filter parent orders based on these child IDs
            order_numbers = knitting_deliver_table.objects.filter(
                id__in=child_orders, status=1
            ).values('id', 'do_number', 'lot_no','prg_id').order_by('-id')

            # Calculate total bags and total quantity only for relevant child orders
            total_bag_sum = 0
            total_quantity_sum = 0
            for order in order_numbers:
                # Only get child orders where remaining_bag or remaining_quantity > 0
                child_order = sub_knitting_deliver_table.objects.filter(
                    tm_id=order['id']
                ).filter(
                    Q(bag__gt=0) | Q(quantity__gt=0)
                )
                
                for child in child_order:
                    total_bag_sum += child.bag
                    total_quantity_sum += child.quantity

            # Convert the queryset to a list
            data = list(order_numbers)
            
            return JsonResponse({
                'orders': data,
                'total_bag': total_bag_sum,
                'total_quantity': total_quantity_sum
            }, safe=False)

    return JsonResponse([], safe=False)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_knitting_deliveries_multiple(request):
    if request.method == 'POST' and 'do_id' in request.POST:
        do_ids = request.POST.getlist('do_id')  # Get the list of do_id values
        print('Selected DO IDs:', do_ids)

        if do_ids:
            # Check if the DOs exist
            dos = knitting_deliver_table.objects.filter(id__in=do_ids, status=1)  # Filter by multiple do_ids
            if not dos:
                return JsonResponse({'error': 'DOs not found'}, status=404)

            deliveries = []
            for do in dos:
                do_prg = do.prg_id
                do_id = do.id

                # Get deliveries for each DO based on the prg_id
                deliveries_query = sub_knitting_table.objects.filter(tm_id=do_prg).values(
                    'count', 
                    'fabric_id', 
                    'gauge', 
                    'tex', 
                    'dia', 
                    'gsm', 
                    'rolls',
                    'wt_per_roll',
                    'quantity',
                    'rate',
                    'total_amount', 
                    'id',
                )

                # Process each delivery and add related information
                for delivery in deliveries_query:
                    yarn_count_id = delivery['count']
                    fabric_id = delivery['fabric_id']
                    gauge = delivery['gauge']
                    tex = delivery['tex']
                    yarn_count = count_table.objects.filter(id=yarn_count_id).first()
                    fabric = fabric_program_table.objects.filter(id=fabric_id).first()
                    gauge = gauge_table.objects.filter(id=gauge).first()
                    tex = tex_table.objects.filter(id=tex).first()

                    # Set additional fields
                    delivery['fabric'] = fabric.name if fabric else 'Unknown'
                    delivery['gauge_name'] = gauge.name if gauge else 'Unknown'
                    delivery['tex_name'] = tex.name if tex else 'Unknown'

                    if yarn_count:
                        delivery['yarn_count'] = yarn_count.name
                    else:
                        delivery['yarn_count'] = 'Unknown'

                    deliveries.append(delivery)

            return JsonResponse({
                'deliveries': deliveries, 
                'prg_id': do_prg,
                'do_id': do_ids  # Return all selected do_ids
            }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
def get_knitting_deliveries(request):
    if request.method == 'POST' and 'do_id' in request.POST:
        do_id = request.POST['do_id']
        dos = request.POST.getlist('do_id')  # Get the list of do_id values
        print('dos:',dos)
        print('Selected DO ID:', do_id)

        if do_id:
            # Check if the DO exists
            do = knitting_deliver_table.objects.filter(id=do_id, status=1).first()
            if not do:
                return JsonResponse({'error': 'DO not found'}, status=404)
            
            do_prg = do.prg_id
            do_id = do.id


            deliveries = sub_knitting_table.objects.filter(tm_id=do_prg).values(
                'count', 
                'fabric_id', 
                'gauge', 
                'tex', 
                'dia', 
                'gsm', 
                'rolls',
                'wt_per_roll',
                'quantity',
                'rate',
                'total_amount', 
                'id',
                
            )

            # Manually lookup yarn_count using yarn_count_id
            for delivery in deliveries:
                yarn_count_id = delivery['count']
                fabric_id = delivery['fabric_id']
                gauge = delivery['gauge']
                tex = delivery['tex']
                dia = delivery['dia']
                print('id-dia:',dia)
                yarn_count = count_table.objects.filter(id=yarn_count_id).first()  # Get yarn_count from the count_table
                fabric = fabric_program_table.objects.filter(id=fabric_id).first()  # Get yarn_count from the count_table
                gauge = gauge_table.objects.filter(id=gauge).first()  # Get yarn_count from the count_table
                tex = tex_table.objects.filter(id=tex).first()  # Get yarn_count from the count_table
                dia = dia_table.objects.filter(id=dia).first()  # Get yarn_count from the count_table
                
                
                delivery['fabric'] = fabric.name  # Assuming 'name' is the correct field in count_table
                delivery['gauge_name'] = gauge.name  # Assuming 'name' is the correct field in count_table
                delivery['tex_name'] = tex.name  # Assuming 'name' is the correct field in count_table
                delivery['dia_name'] = dia.name  # Assuming 'name' is the correct field in count_table
                print('-name:', fabric_id ,fabric.name , gauge.name, yarn_count.name,dia.name)
                if yarn_count:
                    delivery['yarn_count'] = yarn_count.name  # Assuming 'name' is the correct field in count_table

            return JsonResponse({
                'deliveries': list(deliveries), 
                'prg_id': do_prg,
                'do_id':do_id
            }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)




# ```````````````````````` gf - delivery ``````````````````````````




@csrf_exempt
def get_gf_inward_details(request):
    if request.method == 'POST' and 'do_id' in request.POST:
        do_id = request.POST['do_id']
        dos = request.POST.getlist('do_id')  # Get the list of do_id values
        print('dos:',dos)
        print('Selected DO ID:', do_id)

        if do_id:
            # Check if the DO exists
            


            deliveries = sub_gf_inward_table.objects.filter(tm_id=do_id).values(
                'count', 
                'product_id', 
                'gauge', 
                'tex', 
                'dia', 
                'gsm', 
                'rolls',
                'wt_per_roll',
                'quantity',
                'rate',
                'gross_wt', 
                'id',
                'do_id'
                
            )
           
            # Manually lookup yarn_count using yarn_count_id
            for delivery in deliveries:
                yarn_count_id = delivery['count']
                fabric_id = delivery['product_id']
                gauge = delivery['gauge']
                tex = delivery['tex']
                dia = delivery['dia']
                print('id-dia:',dia)
                yarn_count = count_table.objects.filter(id=yarn_count_id).first()  # Get yarn_count from the count_table
                fabric = fabric_program_table.objects.filter(id=fabric_id).first()  # Get yarn_count from the count_table
                gauge = gauge_table.objects.filter(id=gauge).first()  # Get yarn_count from the count_table
                tex = tex_table.objects.filter(id=tex).first()  # Get yarn_count from the count_table
                dia = dia_table.objects.filter(id=dia).first()  # Get yarn_count from the count_table
                
                
                delivery['fabric'] = fabric.name  # Assuming 'name' is the correct field in count_table
                delivery['gauge_name'] = gauge.name  # Assuming 'name' is the correct field in count_table
                delivery['tex_name'] = tex.name  # Assuming 'name' is the correct field in count_table
                delivery['dia_name'] = dia.name  # Assuming 'name' is the correct field in count_table
                print('-name:', fabric_id ,fabric.name , gauge.name, yarn_count.name,dia.name)
                if yarn_count:
                    delivery['yarn_count'] = yarn_count.name  # Assuming 'name' is the correct field in count_table

            do_ids = delivery['do_id']

            do = knitting_deliver_table.objects.filter(id=do_ids, status=1).first()
            if not do:
                return JsonResponse({'error': 'DO not found'}, status=404)
            
            do_prg = do.prg_id
            lot_no = do.lot_no
            doId = do.id


            return JsonResponse({
                'deliveries': list(deliveries), 
                'prg_id': do_prg,
                'do_id':doId,
                'lot_no':lot_no
            }, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)




# ````````````````````````````````````````````````````````````````````````````
@csrf_exempt
def load_do_details_inward(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('do_id[]')  # Selected PO IDs
        deliver_ids = request.GET.getlist('deliver_to')  # Selected delivery IDs (could be multiple)

        if not po_ids or not deliver_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) and Delivery ID(s) are required.'}, status=400)

        try:
            parent_pos = knitting_deliver_table.objects.filter(id__in=po_ids, deliver_to=supplier_id)
            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            total_bag_sum = 0
            total_quantity_sum = 0

            for po in parent_pos:
                total_quantity = po.total_quantity or 0
                total_quantity_sum += total_quantity

  

                child = sub_knitting_deliver_table.objects.filter(tm_id=po.id, is_active=1).first()
                if not child:
                    continue

                product = count_table.objects.filter(id=child.yarn_count_id).first()


                order_data.append({ 
                    'product_id': child.yarn_count_id,
                    'product': product.name if product else "Unknown Product",
                    'tax_value': 5,
                    'bag': child.bag,  # Remaining bag
                    'per_bag': child.per_bag,
                    'quantity': child.quantity or 0,
                    'gross_wt': child.gross_wt,
                    
                    'id': child.id,
                    'parent_id': po.id,
                    'tm_id': po.id,
                    'tx_id': child.id or 0,
                    'program_lot': knitting_table.objects.filter(po_id=po.id).first().lot_no if knitting_table.objects.filter(po_id=po.id).exists() else 0,
                })

            return JsonResponse({'orders': order_data, 'total_bag': total_bag_sum, 'total_quantity': total_quantity_sum})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


# def get_po_lists(request):
#     if request.method == 'POST' and 'supplier_id' in request.POST: 
#         supplier_id = request.POST['supplier_id']
#         print('supplier_id:', supplier_id) 

#         if supplier_id:
#             # Fetch all child purchase orders for the given supplier_id where is_assigned=0
#             child_orders = child_po_table.objects.filter(
#                 tm_po_id__in=parent_po_table.objects.filter(supplier_id=supplier_id, status=1, is_inward=0).values('id')
#             ).values('tm_po_id')  # Get the IDs of the parent orders

#             # Fetch parent purchase orders
#             order_number = parent_po_table.objects.filter( 
#                 id__in=child_orders
#             ).values('id', 'po_number').order_by('-id')

#             # Fetch knitting programs
#             knitting_prg = knitting_table.objects.filter(  
#                 po_id__in=child_orders
#             ).values('id', 'knitting_number', 'lot_no').order_by('-id')

#             # Prepare data to return
#             data = {
#                 'po_list': list(order_number),  # List of purchase orders
#                 'knitting_prg': list(knitting_prg)  # List of knitting programs
#             }

#             return JsonResponse(data, safe=False)  # Return the dictionary as JSON response

#     return JsonResponse({'po_list': [], 'knitting_prg': []}, safe=False)  # Return empty lists if no data


def gf_inward_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            gf_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_gf_inward_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except gf_inward_table  & sub_gf_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})



def inward_detail_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'gf/update_gf_inward.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'gf/update_gf_inward.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = sub_gf_inward_table.objects.filter(tm_id=material_id).first()
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
                material_instance = sub_gf_inward_table.objects.create(
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
                return render(request, 'gf/update_gf_inward.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = gf_inward_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'gf/update_gf_inward.html', {'error_message': 'Parent stock not found.'})

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
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_knitting=1,status=1)
        count = count_table.objects.filter(status=1) 
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)

        fabric_program = fabric_program_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
        knitting = knitting_table.objects.filter(status=1)
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
            'fabric_program':fabric_program,
            'knitting':knitting
        }
        return render(request, 'gf/update_gf_inward.html', context)

    except Exception as e:
        return render(request, 'gf/update_gf_inward.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


def update_gf_inward_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_gf_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = gf_inward_table.objects.filter(id=master_id).first()
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
                            'action': '<button type="button" onclick="gf_inward_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="gf_inward_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'product': getProductNameById(fabric_program_table, item['product_id']),  
                            'count': getCountNameById(count_table, item['count']), 
                            'gauge': getItemNameById(gauge_table, item['gauge']),  
                            'tex': getItemNameById(tex_table, item['tex']),  
                            'dia': getItemNameById(dia_table, item['dia']),  
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


def getProductNameById(tbl, product_id):
    try:
        party = tbl.objects.get(id=product_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party


def getCountNameById(tbl, product_id):
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
        tx = sub_gf_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

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
        gf_inward_table.objects.filter(id=master_id).update(
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

 
# def add_or_update_gf_inward_item(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('tm_id')
#         print('tm-id:',master_id)
#         product_id = request.POST.get('fabric_id')
#         count = request.POST.get('count_id')
#         gauge = request.POST.get('gauge_id')
#         tex = request.POST.get('tex_id') 
#         dia = request.POST.get('dia')
#         rolls = request.POST.get('rolls')
#         wt_per_roll = request.POST.get('wt_per_roll') 
#         quantity = request.POST.get('quantity')
#         rate = request.POST.get('rate')
#         total_amount = request.POST.get('total_amount')

#         # if not master_id or not product_id:
#         #     return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

#         try:
#             # Add or update the child table record
#             child_item, created = sub_gf_inward_table.objects.update_or_create(
#                 tm_id=master_id, product_id=product_id,
#                 defaults={
#                     'count': count,
#                     'gauge': gauge,
#                     'tex': tex,
#                     'dia':dia,
#                     'rolls':rolls,
#                     'wt_per_roll':wt_per_roll,
#                     'quantity': quantity,
#                     'rate': rate,
#                     'total_amount': total_amount,
#                     'status': 1,
#                     'is_active': 1
#                 }
#             )

#             # Update `tm_table` with new totals
#             updated_totals = update_tm_table_totals(master_id)

#             return JsonResponse({'success': True, **updated_totals})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})
#     else:
#         return JsonResponse({'success': False, 'error_message': 'Invalid request method'})






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


# def add_or_update_gf_inward_item(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('do_id')  # Parent Table ID
#         print('master:',master_id)
#         po_id = request.POST.get('po_id',0)
#         product_id = request.POST.get('fabric_id')
#         count = request.POST.get('count_id')
#         gauge = request.POST.get('gauge_id')
#         tex = request.POST.get('tex_id')  
#         dia = request.POST.get('dia')
#         gsm = request.POST.get('gsm')
#         print('ud-gsm:',gsm)
#         rolls = request.POST.get('rolls')
#         wt_per_roll = request.POST.get('wt_per_roll')
#         quantity = request.POST.get('quantity')
#         rate = request.POST.get('rate')
#         amount = request.POST.get('total_amount')
#         edit_id = request.POST.get('edit_id')  # This determines if it's an update or new entry
#         tm_id = request.POST.get('tm_id')  # This determines if it's an update or new entry
#         do_id = request.POST.get('do_id')  # This determines if it's an update or new entry
#         prg_id = request.POST.get('prg_id')  # This determines if it's an update or new entry
#         print('data value:',do_id)
#         # Ensure required fields are provided
#         if not product_id :
#             return JsonResponse({'success': False, 'error_message': 'Missing required data'})
 
#         try: 
#             if edit_id:  # Update existing record
#                 child_item = sub_gf_inward_table.objects.get(id=edit_id,do_id=do_id) 
#                 print('edit-child:',child_item)
#                 # child_item.tm_id = tm_id 
#                 child_item.product_id = product_id 
#                 child_item.count = count
#                 child_item.gauge = gauge 
#                 child_item.tex = tex
#                 child_item.dia = dia
#                 child_item.po_id = po_id
#                 child_item.gsm = gsm
#                 child_item.rolls = rolls
#                 child_item.wt_per_roll = wt_per_roll
#                 child_item.quantity = quantity 
#                 child_item.rate = rate
#                 child_item.do_id = do_id
#                 child_item.tm_prg_id = prg_id
#                 child_item.total_amount = amount
#                 child_item.save()
#                 message = "GF Inward updated successfully."
#             else:  # Create new record
#                 child_item = sub_gf_inward_table.objects.create( 
#                     product_id=product_id,
#                     tm_id=master_id, 
#                     count=count, 
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

#         except sub_gf_inward_table.DoesNotExist:
#             return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})
    
#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

def add_or_update_gf_inward_item(request):
    if request.method == 'POST':
        try:
            master_id = request.POST.get('do_id')  # Parent Table ID
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
            do_id = request.POST.get('do_id')
            prg_id = request.POST.get('prg_id')

            print("Received do_id:", do_id)
            print("Received edit_id:", edit_id)

            # Basic validation
            if not product_id:
                return JsonResponse({'success': False, 'error_message': 'Missing required fabric_id'})

            if not master_id or master_id == 'undefined':
                return JsonResponse({'success': False, 'error_message': 'Invalid master (do_id)'})

            try:
                master_id = int(master_id)
                do_id = int(do_id) if do_id and do_id != 'undefined' else None
                edit_id = int(edit_id) if edit_id and edit_id != 'undefined' else None
            except ValueError:
                return JsonResponse({'success': False, 'error_message': 'Invalid ID(s) format'})

            # Attempt to update if edit_id exists
            if edit_id:
                try:
                    if do_id:
                        child_item = sub_gf_inward_table.objects.get( tm_id=tm_id,do_id=do_id)
                    else:
                        child_item = sub_gf_inward_table.objects.get(id=edit_id)

                    child_item.product_id = product_id
                    child_item.count = count
                    child_item.gauge = gauge
                    child_item.tex = tex
                    child_item.dia = dia
                    child_item.po_id = po_id
                    child_item.gsm = gsm
                    child_item.rolls = rolls
                    child_item.wt_per_roll = wt_per_roll
                    child_item.quantity = quantity
                    child_item.rate = rate
                    child_item.do_id = do_id
                    child_item.tm_prg_id = prg_id
                    child_item.total_amount = amount
                    child_item.save()
                    message = "GF Inward updated successfully."

                except sub_gf_inward_table.DoesNotExist:
                    # Fallback to creating new record
                    print(f"edit_id {edit_id} with do_id {do_id} not found. Creating new record instead.")
                    child_item = sub_gf_inward_table.objects.create(
                        product_id=product_id,
                        tm_id=tm_id,
                        count=count,
                        gauge=gauge,
                        do_id=do_id,
                        tm_prg_id=prg_id,
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
                    message = "Record not found. New entry created instead."

            else:
                # No edit_id — create new entry
                child_item = sub_gf_inward_table.objects.create(
                    product_id=product_id,
                    tm_id=tm_id,
                    do_id=do_id,
                    tm_prg_id=prg_id,
                    count=count,
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

            # Update totals in parent
            updated_totals = update_knitting(master_id)

            return JsonResponse({'success': True, 'message': message, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


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


from django.http import JsonResponse

def gf_inward_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        print('edit-id:',item_id)
        data = sub_gf_inward_table.objects.filter(id=item_id).values()

        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests




def add_gf_delivery(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        try: 
            # Extracting data from the request
            do_date = request.POST.get('delivery_date') 
            supplier_id = request.POST.get('supplier_id')
            inward_id = request.POST.get('inward_id')
            lot_no = request.POST.get('lot_no')
            deliver_id = request.POST.get('deliver_id')
            remarks = request.POST.get('remarks') 
            prg_id = request.POST.get('dye_prg_id') 
            # quantity = request.POST.get('quantity')
            process_id = request.POST.get('process_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 
            print('sub-data:',chemical_data)
            # Get PO IDs
            po_ids = request.GET.getlist('po_id[]')  
            po_ids_str = ",".join(po_ids)  
            color_id = ','.join(request.POST.getlist('color_id'))  # Convert list to comma-separated string

            # Create a new entry in knitting_deliver_table (Parent table)
            material_request = parent_gf_delivery_table.objects.create( 
                po_id=po_ids_str,
                delivery_date=do_date,
                deliver_to=deliver_id,
                supplier_id=supplier_id, 
                # quantity=quantity,
                prg_id = prg_id,
                process_id=process_id, 
                lot_no=lot_no,
                total_quantity = Decimal(request.POST.get('total_quantity') or '0.00'),
                gross_wt = Decimal(request.POST.get('sub_total') or '0.00'),
                # total_tax = Decimal(request.POST.get('tax_total') or '0.00') ,
                # grand_total = Decimal(request.POST.get('total_payable') or '0.00'),
                remarks=remarks,
                created_by=user_id,
                created_on=datetime.now()
            ) 


            color_ids = request.POST.getlist('color_id')  # Get multiple IDs as a list
            color_id_str = ",".join(color_ids)  # Convert to "1,2,3"

            # Iterate through chemical_data and save records
            for chemical in chemical_data:
                tm_po_id = chemical.get('tm_id')
                print('po-id:',tm_po_id)
                product_id = chemical.get('product_id')
                delivered_bag = Decimal(chemical.get('bag') or '0')
                delivered_quantity = Decimal(chemical.get('quantity') or '0')
                delivered_amount = Decimal(chemical.get('amount') or '0')

                # Create a new record in sub_knitting_deliver_table
                child_gf_delivery_table.objects.create(
                    tm_id=material_request.id,
                    lot_no=chemical.get('lot_no'),
                    product_id=product_id, 
                    tm_po_id=tm_po_id, 
                    count_id=chemical.get('count_id'),
                    gauge_id=chemical.get('gauge_id'),
                    # color_id = 0,#color_id_str,
                    tex_id = chemical.get('tex_id'),
                    dia = chemical.get('dia'),
                    rolls= chemical.get('rolls'),
                    wt_per_roll = chemical.get('wt_per_roll'),
                    quantity=chemical.get('quantity'),  
                    gross_wt=chemical.get('gross_wt'),  
                    rate=chemical.get('rate'),
                    amount=delivered_amount,
                    created_by=user_id, 
                    created_on=datetime.now()
                    ) 

                # **Update child_po_table (Reduce Remaining Values)**
              
            # 🔹 **Update Parent PO Table (`po_table`)**  
            # inward = chemical.get('tm_id') 

            inward = request.POST.get('inward_id')
            if inward:
                updated_count = gf_inward_table.objects.filter(id=inward).update(is_complete=1)
                if updated_count == 0:
                    print(f"⚠️ No matching record found for ID: {inward}")



            # gf_inward_table.objects.filter(id__in=inward).update(is_complete=1)

            return JsonResponse('yes', safe=False)  # Indicate success

        except Exception as e: 
            print(f"❌ Error: {e}")  # Log error for debugging
            return JsonResponse('no', safe=False)  # Indicate failure

    return render(request, 'knitting_deliver/add_knitting_deliver.html')


 

# ```````````````````````````````````` GREY FABRIC DELIVERY ````````````````````````````````````````

# if inward:
#     updated_count = gf_inward_table.objects.filter(id=inward).update(is_complete=1)
#     if updated_count == 0:
#         print(f"⚠️ No matching record found for ID: {inward}")





def gf_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'gf/gf_delivery_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    

 

def gf_delivery_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access: 
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(parent_gf_delivery_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="gf_delivery_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="gf_delivery_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="gf_po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'delivery_date': item['delivery_date'] if item['delivery_date'] else'-', 
            'deliver_to':getSupplier(party_table, item['deliver_to'] ), 
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            # 'gross_total': item['gross_total'] if item['gross_total'] else'-', 
            # 'total_tax': item['total_tax'] if item['total_tax'] else'-', 
            # 'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            # 'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 




def gf_delivery_edit(request):
    try: 
        encoded_id = request.GET.get('id')
        print('encoded-id:',encoded_id)
        if not encoded_id:
            return render(request, 'gf/update_gf_delivery.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
            print('decoded-id:',decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'gf/update_gf_delivery.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_gf_delivery_table.objects.filter(tm_id=material_id).first()
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
                material_instance = child_gf_delivery_table.objects.create(
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
                return render(request, 'gf/update_gf_delivery.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = parent_gf_delivery_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'gf/update_gf_delivery.html', {'error_message': 'Parent stock not found.'})

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
        supplier = party_table.objects.filter( Q(status=1) & (Q(is_process=1)))
        
        party = party_table.objects.filter(is_knitting=1,status=1)
        count = count_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        # Render the edit page with the material instance and supplier name
        dyeing_prg = dyeing_program_table.objects.filter(status=1)
        inward = gf_inward_table.objects.filter(is_complete=0,status=1)

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
            'dyeing_prg':dyeing_prg,
            'inward':inward
        }

        print('context:',context)
        return render(request, 'gf/update_gf_delivery.html', context)

    except Exception as e:
        return render(request, 'gf/update_gf_delivery.html', {'error_message': 'An unexpected error occurred: ' + str(e)})





def gf_delivery_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        # supplier = party_table.objects.filter(is_supplier=1) 
        supplier = party_table.objects.filter( Q(status=1) & (Q(is_process=1)))

        if supplier.exists(): 
            supplier_id = supplier.first().id  # Fetch the first supplier's ID 
            knitting = knitting_table.objects.filter(knitting_id=supplier_id)
        else:
            supplier_id = None  
            knitting = knitting_table.objects.none()   # Return an empty queryset 

        party = party_table.objects.filter(status=1)
        product = fabric_program_table.objects.filter(status=1) 
        deliver = party_table.objects.filter(is_process=1)
        inward = gf_inward_table.objects.filter(is_complete=0,status=1)
        last_purchase = gf_delivery_table.objects.order_by('-id').first()
        if last_purchase:
            delivery_number = last_purchase.id + 1  
        else: 
            delivery_number = 1  # Default if no records exist

        process = process_table.objects.filter(status=1, stage__in=['bleaching', 'dyeing','inhouse'])
        lot = knitting_deliver_table.objects.filter(status=1)
        dyeing_prg = dyeing_program_table.objects.filter(status=1)

        return render(request,'gf/add_gf_delivery.html',{'inward':inward,'supplier':supplier,'party':party,'product':product,'dyeing_prg':dyeing_prg,
                                                        'process':process,'deliver':deliver,'knitting':knitting,'do_number':delivery_number,'lot':lot})
    else:
        return HttpResponseRedirect("/admin")
    


def dye_program_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('prg_id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data 
                child_data = sub_dyeing_program_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_rolls = child_data.aggregate(Sum('rolls'))['rolls__sum'] or 0
                    total_wt = child_data.aggregate(Sum('wt_per_roll'))['wt_per_roll__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    # parent_data = knitting_table.objects.filter(id=master_id).first()
                    # if parent_data:
                    #     total_tax = Decimal(parent_data.total_tax or 0)
                    #     try:
                    #         round_off = Decimal(parent_data.round_off) if parent_data.round_off else Decimal(0)
                    #     except (ValueError, TypeError):
                    #         round_off = Decimal(0)
                    #     grand_total = Decimal(total_amount) + total_tax + round_off
                    # else:
                    #     total_tax = round_off = grand_total = Decimal(0)

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
                            'color': getCountNameById(color_table, item['color_id']),
                            'dia': getItemNameById(dia_table, item['dia_id']),
                            # 'tex': getItemNameById(tex_table, item['tex']),
                            # 'dia': item['dia'] or '-',
                            'rolls': item['rolls'] or '-',
                            'wt_per_roll': item['wt_per_roll'] or '-',
                            # 'rate': item['rate'] or '-',
                            # 'quantity': item['quantity'] or '-',
                            # 'total_amount': item['total_amount'] or '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_rolls': float(total_rolls),  # Convert to float for JSON compatibility
                        'total_wt': float(total_wt),
                    #     'total_tax': float(total_tax),
                    #     'round_off': float(round_off),
                    #     'grand_total': float(grand_total),
                    })
                # else:
                #     return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})


# @csrf_exempt  # Use only if necessary
# def get_lot_details(request): 
#     if request.method == 'POST':
#         lot_id = request.POST.get('lot_id')

#         if not lot_id:
#             return JsonResponse({'error': 'Lot ID is required'}, status=400)

#         try:
#             # **1. Get Inward Stock (In-House Stock)**
#             fabric_program = get_object_or_404(gf_inward_table, id=lot_id, status=1) 
#             lot_no = fabric_program.lot_no  # In-house stock
#             inward_total_quantity = fabric_program.total_quantity  # In-house stock
            
#             # **2. Get Fabric Program Quantity (Knitting Table)**
#             knitting_record = knitting_table.objects.filter(lot_no=fabric_program.lot_no,status=1).first()
#             program_total_quantity = knitting_record.total_quantity if knitting_record else Decimal('0.00')

#             # **3. Get Delivered Quantity (Parent GF Delivery Table)** 
#             # delivery_record = parent_gf_delivery_table.objects.filter(lot_no=fabric_program.lot_no).first()
#             # delivered_quantity = delivery_record.total_quantity if delivery_record else Decimal('0.00')
#             delivery_records = parent_gf_delivery_table.objects.filter(lot_no=fabric_program.lot_no,status=1)

#             # Sum the total_quantity from all matching records
#             delivered_quantity = delivery_records.aggregate(total_delivered=Sum('gross_wt'))['total_delivered'] or Decimal('0.00')

#             print(f"Total Delivered Quantity for Lot {fabric_program.lot_no}: {delivered_quantity}")
#             # **4. Calculate Balance Quantity**
#             balance_quantity = inward_total_quantity - delivered_quantity
#             print('b-qty:',inward_total_quantity,delivered_quantity,balance_quantity)

#             # **Prepare Response Data**
#             response_data = {
#                 'lot_no': fabric_program.lot_no,
#                 'inward_total_quantity': inward_total_quantity,  # In-house stock
#                 'program_total_quantity': program_total_quantity,  # Fabric program
#                 'delivered_quantity': delivered_quantity,  # Delivered stock
#                 'balance_quantity': balance_quantity,  # Remaining balance
#             }

#             return JsonResponse(response_data)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)




@csrf_exempt  # Use only if necessary
def get_lot_details(request): 
    if request.method == 'POST':
        lot_id = request.POST.get('lot_id')

        if not lot_id:
            return JsonResponse({'error': 'Lot ID is required'}, status=400)

        try:
            # **1. Get Inward Stock (In-House Stock)**
            fabric_program = get_object_or_404(gf_inward_table, lot_no=lot_id, status=1) 
            lot_no = fabric_program.lot_no  # In-house stock
            lot = knitting_deliver_table.objects.filter(id=lot_no)
            print('do-lot:',lot)
            inward_total_quantity = fabric_program.total_quantity  # In-house stock
            
            # **2. Get Fabric Program Quantity (Knitting Table)** 
            knitting_record = knitting_table.objects.filter(lot_no=fabric_program.lot_no,status=1).first()
            program_total_quantity = knitting_record.total_quantity if knitting_record else Decimal('0.00')

            # **3. Get Delivered Quantity (Parent GF Delivery Table)** 
            # delivery_record = parent_gf_delivery_table.objects.filter(lot_no=fabric_program.lot_no).first()
            # delivered_quantity = delivery_record.total_quantity if delivery_record else Decimal('0.00')
            delivery_records = parent_gf_delivery_table.objects.filter(lot_no=fabric_program.lot_no,status=1)

            # Sum the total_quantity from all matching records
            delivered_quantity = delivery_records.aggregate(total_delivered=Sum('gross_wt'))['total_delivered'] or Decimal('0.00')

            print(f"Total Delivered Quantity for Lot {fabric_program.lot_no}: {delivered_quantity}")
            # **4. Calculate Balance Quantity**
            balance_quantity = inward_total_quantity - delivered_quantity
            print('b-qty:',inward_total_quantity,delivered_quantity,balance_quantity)

            # **Prepare Response Data**
            response_data = {
                'lot_no': fabric_program.lot_no,
                'inward_total_quantity': inward_total_quantity,  # In-house stock
                'program_total_quantity': program_total_quantity,  # Fabric program
                'delivered_quantity': delivered_quantity,  # Delivered stock
                'balance_quantity': balance_quantity,  # Remaining balance
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)





def get_gf_delivery_list(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('supplier_id:', supplier_id)  

        if supplier_id:
            # Fetch parent orders
            parent_orders = gf_inward_table.objects.filter(supplier_id=supplier_id, status=1).values('id')
            print('Parent Orders:', list(parent_orders))

            # Fetch child orders
            child_orders = sub_gf_inward_table.objects.filter(
                tm_id__in=parent_orders
            ).values('tm_id')
            print('Child Orders:', list(child_orders))

            # Fetch order numbers
            order_number = gf_inward_table.objects.filter(
                id__in=[order['tm_id'] for order in child_orders]  # Extracting tm_id values
            ).values('id', 'inward_number').order_by('-id')
            print('Order Numbers:', list(order_number))

            return JsonResponse(list(order_number), safe=False)
    
    return JsonResponse([], safe=False)

 
#

def load_gf_po_id_list_getfrom_gf_delivery(request): 
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')

        if not supplier_id or not po_ids:
            return JsonResponse({'error': 'Supplier ID and Purchase Order ID(s) are required.'}, status=400)

        try:
            parent_pos = gf_delivery_table.objects.filter(id__in=po_ids, knitting_id=supplier_id)
            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                orders = sub_gf_po_table.objects.filter(tm_po_id=po.tm_po_id)

                for order in orders:
                    product = product_table.objects.filter(id=order.product_id).first()
                    count = count_table.objects.filter(id=order.count).first()
                    gauge = gauge_table.objects.filter(id=order.gauge).first()
                    tex = tex_table.objects.filter(id=order.tex).first()

                    # Get values with defaults
                    rolls = po.rolls if po.rolls else 0
                    wt_per_roll = order.wt_per_roll if order.wt_per_roll else 0
                    rate = order.rate if order.rate else 0

                    # ✅ Calculate quantity
                    quantity = rolls * wt_per_roll

                    # ✅ Calculate total_amount
                    total_amount = quantity * rate

                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "Unknown Product", 
                        'count': count.count if count else "Unknown count", 
                        'gauge': gauge.name if gauge else "Unknown gauge", 
                        'tex': tex.name if tex else "Unknown tex", 
                        'tax_value': 5,  
                        'count_id': order.count,
                        'gauge_id': order.gauge,   
                        'tex_id': order.tex,
                        'rolls': rolls,
                        'delivery_date': po.delivery_date,
                        'wt_per_roll': wt_per_roll,
                        'dia': order.dia if order.dia else 0,  # ✅ Default to 0
                        'quantity': quantity,  # ✅ Updated Quantity
                        'rate': rate,
                        'total_amount': total_amount,  # ✅ Updated Total Amount
                        'id': order.id,
                        'tm_id': po.tm_po_id,
                        'tx_id': order.id,
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)




def load_gf_po_id_list(request):
    if request.method == "GET":
        # supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id')  # Get list of selected PO IDs 
        print('po-id:', po_ids)

        if not po_ids:
        # if not supplier_id or not po_ids:
            return JsonResponse({'error': ' Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided supplier and PO IDs
            parent_pos = gf_po_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
             
                orders = sub_gf_po_table.objects.filter(tm_po_id=po.id)

                for order in orders:
                    product = product_table.objects.filter(id=order.product_id).first()
                    count = count_table.objects.filter(id=order.count).first()
                    gauge = gauge_table.objects.filter(id=order.gauge).first()
                    tex = tex_table.objects.filter(id=order.tex).first()

                    # Prepare order details
                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "Unknown Product", 
                        'count': count.count if count else "Unknown count", 
                        'count_id':order.count,
                        'gauge_id':order.gauge,
                        'tex_id':order.tex,
                        'gauge': gauge.name if gauge else "Unknown gauge", 
                        'tex': tex.name if tex else "Unknown tex", 
                        'tax_value': 5,  
                        'rolls': order.rolls,
                        'wt_per_roll': order.wt_per_roll,   
                        'quantity': order.quantity,
                        'rate': order.rate,
                        'amount': order.total_amount, 
                        'id': order.id,
                        'tm_id': order.tm_po_id,
                        'tx_id': order.id,
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

 


def load_gf_inward_detail(request):
    if request.method == "GET":
        po_ids = request.GET.get('po_id', '').split(',')  # Convert to list
        print('po-id:', po_ids)

        if not po_ids or po_ids == ['']:
            return JsonResponse({'error': 'Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided PO IDs
            parent_pos = gf_inward_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                orders = sub_gf_inward_table.objects.filter(tm_id=po.id)

                for order in orders:
                    product = product_table.objects.filter(id=order.product_id).first()
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
                        'lot_no': po.lot_no
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)





def gf_delivery_update_view(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id:  
            try:
                # Fetch child PO data
                child_data = child_gf_delivery_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0 
                    total_gross = child_data.aggregate(Sum('gross_wt'))['gross_wt__sum'] or 0

                    # # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    # parent_data = parent_gf_delivery_table.objects.filter(id=master_id).first()
                    # if parent_data:
                    #     tax_total = parent_data.total_tax or 0
                    #     # round_off = parent_data.round_off or 0
                    #     grand_total = total_amount + tax_total 
                    # else:
                    #     tax_total = grand_total = 0 

                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0
                    for item in data: 
                        index += 1  
                        formatted_data.append({
                            'action': '<button type="button" onclick="gf_delivery_details_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="gf_delivery_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'product': getItemNameById(fabric_program_table, item['product_id']), 
                            'count': getCountNameById(count_table, item['count_id']), 
                            'gauge': getItemNameById(gauge_table, item['gauge_id']), 
                            'tex': getItemNameById(tex_table, item['tex_id']),  
                            'dia': item['dia'] if item['dia'] else '-',
                            'rolls': item['rolls'] if item['rolls'] else '-',
                            'wt_per_roll': item['wt_per_roll'] if item['wt_per_roll'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'gross_wt': item['gross_wt'] if item['gross_wt'] else '-',
                            'rate': item['rate'] if item['rate'] else '-',
                            'total_amount': item['amount'] if item['amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_gross': total_gross,
                        # 'total_amount': total_amount,
                        # 'tax_total': tax_total,
                        # 'round_off': round_off,
                        # 'gra/nd_total': grand_total
                    })
                # else:
                #     return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})




def gf_delivery_detail_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = child_gf_delivery_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
 



def update_delivery(master_id):
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



def add_or_update_gf_delivery_item(request):
    if request.method == 'POST':
        try:
            po_id = request.POST.get('po_id', 0)
            product_id = request.POST.get('fabric_id')
            pr_id = request.POST.get('product_id')
            print('pr-id:',pr_id)
            count = request.POST.get('count_id')
            gauge = request.POST.get('gauge_id')
            tex = request.POST.get('tex_id')
            dia = request.POST.get('dia')
            gsm = request.POST.get('gsm')
            rolls = request.POST.get('rolls')
            wt_per_roll = request.POST.get('wt_per_roll')
            quantity = request.POST.get('quantity')
            gross_wt = request.POST.get('gross_wt')
            lot_no = request.POST.get('lot_no')
            amount = request.POST.get('total_amount')
            edit_id = request.POST.get('edit_id')
            tm_id = request.POST.get('tm_id')
            prg_id = request.POST.get('prg_id')

            # print("Received do_id:", do_id)
            print("Received edit_id:", edit_id)

            # Basic validation 
            if not product_id:
                return JsonResponse({'success': False, 'error_message': 'Missing required fabric_id'})

            if not tm_id or tm_id == 'undefined':
                return JsonResponse({'success': False, 'error_message': 'Invalid master (tm_id)'})

            try:
                # master_id = int(master_id)
                # do_id = int(do_id) if do_id and do_id != 'undefined' else None
                edit_id = int(edit_id) if edit_id and edit_id != 'undefined' else None
            except ValueError:
                return JsonResponse({'success': False, 'error_message': 'Invalid ID(s) format'})

            # Attempt to update if edit_id exists
            if edit_id:
                try:
                    if tm_id:
                        child_item = child_gf_delivery_table.objects.get( id=edit_id,tm_id=tm_id)
                        # child_item = child_gf_delivery_table.objects.get( id=edit_id,tm_id=tm_id,lot_no=lot_no)
                    else:
                        child_item = child_gf_delivery_table.objects.get(id=edit_id)

                    child_item.product_id = product_id
                    child_item.count_id = count
                    child_item.gauge_id = gauge
                    child_item.tex_id = tex  
                    child_item.dia = dia 
                    # child_item.po_id = po_id
                    child_item.gsm = gsm 
                    child_item.rolls = rolls 
                    child_item.wt_per_roll = wt_per_roll
                    child_item.quantity = quantity
                    child_item.gross_wt = gross_wt
                    # child_item.rate = rate
                    # child_item.do_id = do_id
                    # child_item.tm_prg_id = prg_id
                    # child_item.total_amount = amount 
                    child_item.save()
                    message = "GF Inward updated successfully."

                except child_gf_delivery_table.DoesNotExist:
                    # Fallback to creating new record  dia=dia
                    print(f"edit_id {edit_id} with tm_id {tm_id} not found. Creating new record instead.")
                    child_item = child_gf_delivery_table.objects.create(

                        tm_id=tm_id,
                        product_id = product_id,
                        count_id = count,
                        gauge_id = gauge,
                        tex_id = tex , 
                        dia = dia , 
                        gsm = gsm ,
                        rolls = rolls ,
                        wt_per_roll = wt_per_roll,
                        quantity = quantity,
                        gross_wt = gross_wt,
                        status=1, 
                        is_active=1
                    )
                    message = "Record not found. New entry created instead."

            else:
                # No edit_id — create new entry
                child_item = child_gf_delivery_table.objects.create(
                    product_id=product_id,
                    tm_id=tm_id,
                    # do_id=do_id,
                    count_id=count,
                    gauge_id=gauge,
                    tex_id=tex,
                    dia=dia,
                    gsm=gsm,
                    rolls=rolls,
                    wt_per_roll=wt_per_roll,
                    quantity=quantity,
                    gross_wt=gross_wt,
                    status=1,
                    is_active=1
                )
                message = "New knitting entry created successfully."

            # Update totals in parent
            updated_totals = update_knitting(tm_id)

            return JsonResponse({'success': True, 'message': message, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})



def add_or_update_gf_delivery_item_bk_2(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')  # Parent Table ID
        print('master:',master_id)
        po_id = request.POST.get('po_id',0)
        product_id = request.POST.get('fabric_id')
        count = request.POST.get('count_id')
        gauge = request.POST.get('gauge_id')
        tex = request.POST.get('tex_id')  
        dia = request.POST.get('dia')
        gsm = request.POST.get('gsm')
        rolls = request.POST.get('rolls')
        wt_per_roll = request.POST.get('wt_per_roll')
        quantity = request.POST.get('quantity')
        gross_wt = request.POST.get('gross_wt',0.00)
        rate = request.POST.get('rate')
        amount = request.POST.get('total_amount')
        edit_id = request.POST.get('edit_id')  # This determines if it's an update or new entry
        tm_id = request.POST.get('tm_id')  # This determines if it's an update or new entry
    
        color_ids = request.POST.getlist('color_id')  # Get multiple IDs as a list
        color_id_str = ",".join(color_ids)  # Convert to "1,2,3"

        # Ensure required fields are provided
        if not product_id :
            return JsonResponse({'success': False, 'error_message': 'Missing required data'})

        try:
            if edit_id:  # Update existing record
                child_item = child_gf_delivery_table.objects.get(id=edit_id, tm_id=tm_id) 
                print('edit-child:',child_item)
                # child_item.tm_id = tm_id 
                child_item.product_id = product_id 
                child_item.count_id = count
                child_item.gauge_id = gauge 
                # child_itm .color_id = color_id_str
                child_item.tex_id = tex
                child_item.dia = dia
                # child_item.po_id = po_id
                child_item.gsm = gsm
                child_item.rolls = rolls 
                child_item.wt_per_roll = wt_per_roll
                child_item.quantity = quantity 
                child_item.gross_wt = gross_wt 
                # child_item.rate = rate
                # child_item.amount = amount
                child_item.save()
                message = "GF Delivery updated successfully."
            else:  # Create new record
                child_item = child_gf_delivery_table.objects.create( 
                    product_id=product_id,
                    tm_id=master_id, 
                    count_id=count, 
                    gauge_id=gauge,
                    tex_id=tex, 
                    dia=dia,
                    gsm=gsm,
                    rolls=rolls, 
                    wt_per_roll=wt_per_roll,
                    quantity=quantity,
                    gross_wt=gross_wt,
                    # rate=rate,
                    # total_amount=amount,
                    status=1,
                    is_active=1
                )
                message = "New Delivery Entry Added successfully."

            # Update `tm_table` totals
            updated_totals = update_knitting(master_id)

            return JsonResponse({'success': True, 'message': message, **updated_totals})

        except sub_gf_inward_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    
    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})





def gf_delivery_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            child_gf_delivery_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except child_gf_delivery_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})