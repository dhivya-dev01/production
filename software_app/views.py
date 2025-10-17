import re
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify
from jwt import decode

from accessory.models import *
from accessory.views import getDiaByIds
from software_app.models import *
from yarn.models import *
from user_auth.models import *
from user_roles.models import *
from program_app.models import *
from company.models import *
from employee.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
from software_app.forms import *
import datetime

from datetime import datetime
from datetime import date
from django.utils import timezone

from django.db.models import Count


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from software_app.models import *

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
from common.utils import *
from production_app.models import *
from accessory.models import *
# from .models import *
# ``````````````````````````````````````*************************``````````````````````````````````````````````````````````
# Create your views here.


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



# def signin_admin(request):
#     return render(request,'login.html')


# import hashlib
# from django.http import HttpResponseRedirect
# from django.shortcuts import render


# def get_financial_year(date=None):
#     """Returns the current financial year as a string (e.g., '2024-2025')."""
#     if date is None:
#         date = datetime.today()  # Default to current date

#     year = date.year
#     month = date.month

#     if month < 4:  # Jan, Feb, Mar belong to the previous financial year
#         return f"{year-1}-{year}"
#     else:  # Apr to Dec belong to the current financial year
#         return f"{year}-{year+1}"

# def login(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
#         pwd = request.POST.get('password')

#         print('login:', email, pwd)
        
#         # Hash the password for comparison
#         hashed_pwd = hashlib.md5(pwd.encode()).hexdigest() 
#         print('pwd:', hashed_pwd)
#         # value = '636033734f18216f6084ba415c509164'
#         # print('decode-pwd:',hashlib.md5(value.decode()).hexdigest() )
#         # Check if the user exists in the database
#         if employee_table.objects.filter(email=email, password=hashed_pwd).exists():
#             user = employee_table.objects.get(email=email, password=hashed_pwd)
#             print('login-user:',user)
#             # 🔹 Calculate Financial Year
#             # financial_year = get_financial_year()  # ✅ Now works correctly

#             # Set session data
#             request.session['user_id'] = user.id
#             request.session['employee_role'] = user.employee_role 
#             request.session['company_id'] = user.company_id
#             request.session['user_username'] = user.name
#             request.session['user_email'] = user.email
#             request.session['user_type'] = user.employee_role

#             # print('cfy:', request.session['cfy'])

#             # Redirect to dashboard on successful login
#             return HttpResponseRedirect("/dashboard")
#         else:
#             # If login fails, show error message
#             return render(request, 'login.html', {'error': 'Invalid username or password'})

#     # If it's a GET request, render the login page
#     return render(request, 'login.html')


# def logout(request):
#     if 'user_id' in request.session:
#         request.session.flush() 
#     return HttpResponseRedirect("/signin")



# # ````````````````````````````````````````````````````````````````````````````````````````

# def dashboard(request):
#     if 'user_id' in request.session: 
#         user_id = request.session['user_id']
#         return render(request,'dashboard.html') 
#     else:
#         return HttpResponseRedirect("/signin")



# `````````````````````````````````````````#####################```````````````````````````````````````



# def company(request):
#     if 'user_id' in request.session:
#         user_type = request.session.get('user_type')
#         if user_type == 'superadmin' or user_type == 'Admin':
#             cmpy = company_table.objects.filter(id=1).first()
#             return render(request, 'master/company.html', {'company': cmpy})
#         else:
#             return HttpResponseRedirect("/signin")
#     else:
#         return HttpResponseRedirect("/signin")


# def profile(request):
#     if 'user_id' in request.session:
#         user_type = request.session.get('user_type')
#         if user_type == 'superadmin' or user_type == 'admin':
#             cmpy = company_table.objects.filter(id=1).first()
#             return render(request, 'master/profile.html', {'company': cmpy})
#         else:
#             return HttpResponseRedirect("/signin")
#     else:
#         return HttpResponseRedirect("/signin")




# def update_company(request):
#     if request.method == "POST":
#         company_id = request.POST.get('id')
#         user_id = request.session.get('user_id')
#         user_type = request.session.get('user_type')

#         # has_access, error_message = check_user_access(user_type, "Company", "update")

#         # if not has_access:
#         #     return JsonResponse({'message': 'error', 'error_message': error_message})
 
#         company_instance = get_object_or_404(company_table, id=company_id)
#         form = companyform(request.POST, request.FILES, instance=company_instance)
#         if form.is_valid():
#             # Update only fields that exist in request.POST or request.FILES
#             for field in form.cleaned_data:
#                 if field in request.POST or field in request.FILES:
#                     setattr(company_instance, field, form.cleaned_data[field])

#             # Handle additional fields manually
#             extra_fields = ['phone', 'address_line2', 'latitude', 'longitude','gstin','cin_no','udyam_no']
#             for field in extra_fields:
#                 if field in request.POST:
#                     setattr(company_instance, field, request.POST.get(field) or '')

#             company_instance.updated_by = user_id
#             company_instance.updated_on = timezone.now()
#             company_instance.save()
#         # if form.is_valid():
#         #     company_instance = form.save(commit=False)  # Save form but don't commit to DB
#         #     company_instance.updated_by = user_id
#         #     company_instance.updated_on = timezone.now()
#         #     company_instance.save()
#             return JsonResponse({'message': 'success'})
#         else:
#             errors = form.errors.as_json()
#             return JsonResponse({'message': 'error', 'errors': errors})


  

# ```````````````````````````` PARTY ``````````````````````````````````




def customers(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/customer.html')
    else:
        return HttpResponseRedirect("/signin")

  
from accessory.models import item_table  # Import your model


def customer_entry(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']  
        employee = employee_table.objects.filter(status=1) 
        company = company_table.objects.filter(status=1)
        item_group = item_table.objects.filter(status=1)
        price_list = price_list_table.objects.filter(status=1)
        return render(request,'master/add_customer.html',{'company':company,
                                                          'price_list':price_list,
                                                          'employee':employee,
                                                          'supply':item_group})
    else:
        return HttpResponseRedirect("/signin")


def generate_party_series():
    last_purchase = party_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.party_code:
        match = re.search(r'P(\d+)', last_purchase.party_code)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1 
    else:
        next_num = 1

    return f"P{next_num:05d}"


from django.db import transaction



@csrf_exempt
def customer_add(request):
    user_type = request.session.get('user_type')
    company_id = request.session.get('company_id')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')  # Use .get() to avoid KeyError
        frm = request.POST
        name = frm.get('name')
        password = frm.get('password')
        is_supplier = 1 if frm.get('is_supplier') else 0
        is_knitting = 1 if frm.get('is_knitting') else 0
        is_trader = 1 if frm.get('is_trader') else 0
        is_b_d = 1 if frm.get('is_b_d') else 0
        is_dyeing = 1 if frm.get('is_dyeing') else 0
        is_compacting = 1 if frm.get('is_compacting') else 0
        is_ironing = 1 if frm.get('is_ironing') else 0
        is_stiching = 1 if frm.get('is_stiching') else 0
        is_cutting = 1 if frm.get('is_cutting') else 0
        is_fabric = 1 if frm.get('is_fabric') else 0
        city = frm.get('city')
        state = frm.get('state')
        pincode = frm.get('pincode')
        country = frm.get('country')
        mail = frm.get('email')
        party_list_id = frm.get('party_list')
        # print('mail',mail)
        phone = frm.get('phone')
        mobile = frm.get('mobile')
        prefix = frm.get('prefix')
        person = frm.get('person')
        address = frm.get('address')
        description = frm.get('description')
        cp_name = request.POST.get('cp_name')        
        cp_mobile = request.POST.get('cp_mobile')        
        cp_email = request.POST.get('cp_email')        
        refered_by = request.POST.get('refered_by')        
        latitude = request.POST.get('latitude')        
        longitude = request.POST.get('longitude')        
        map_address = request.POST.get('map_address')        
        zone_id = request.POST.get('zone_id')        
        forum_id = request.POST.get('forum_id')        
        gstin = request.POST.get('gstin')   
        customer_type = request.POST.get('customer_type')      
        nick_name = request.POST.get('nick_name')      
        udyam_no = request.POST.get('udyam_no')   

        supply_id = ','.join(request.POST.getlist('supply_id'))  # Convert list to comma-separated string
        party_code_no = generate_party_series()

        print('supply_id',supply_id)
        try:
            # Save Party (Customer) 
            customer = party_table(
                party_code = party_code_no,
                supply_items = supply_id,
                is_supplier = 1 if frm.get('is_supplier') else 0,
                is_mill = 1 if frm.get('is_mill') else 0,
                is_knitting = is_knitting,
                is_process=is_b_d,
                # is_dyeing=is_dyeing,
                party_list_id=party_list_id,
                is_compacting=is_compacting,
                is_cutting=is_cutting,
                is_stiching=is_stiching,
                is_trader=is_trader,
                is_ironing=is_ironing,
                is_fabric = is_fabric,
                name=name,  
                nick_name=nick_name,
                udyam_no=udyam_no,
                prefix = prefix,
                # party_code=request.POST.get('party_code',0),
                # password=password,
                city=city,
                state=state,
                state_code=request.POST.get('state_code',0),
                pincode=pincode,
                email=mail,
                phone=phone, 
                mobile=mobile,
                # customer_type=customer_type,
                # company_code=123456,
                address=address,
                description=description,
                latitude=latitude,
                longitude=longitude,
                gstin=gstin,
                company_id=1,
                created_on=datetime.now(),
                created_by=user_id,
                updated_on=datetime.now(),
                updated_by=user_id
            )
            customer.save()


            # Get Contact Details from the request
            contacts_json = request.POST.get('contacts')
            print('contcta',contacts_json)

            if contacts_json:
                contacts = json.loads(contacts_json)  # Convert JSON to Python list

                for contact in contacts:
                    # Ignore empty contacts
                    if contact.get("name") or contact.get("email") or contact.get("phone"):
                        party_contact_table.objects.create(
                            party_id=customer.id,
                            cp_name=contact.get("name", ""),
                            cp_email=contact.get("email", ""),
                            cp_mobile=contact.get("phone", ""),
                            designation=contact.get("designation", ""),
                            is_active=1,
                            status=1,
                            created_by=user_id,
                            updated_by=user_id,
                            created_on=timezone.now(), 
                            updated_on=timezone.now(),
                        )


            # current_year = get_object_or_404(company_table, id=company_id)
            party_ob_table.objects.create(
                customer_id=customer.id,
                year=2024, #current_year.cfy,
                opening_balance=0,
                closing_balance=0,
                created_by=user_id,
                created_on=timezone.now()
            )


            return JsonResponse({"status": "Success", "vendor_id": customer.id})

        except ValueError as ve:
            return JsonResponse({"status": "Failed", "message": f"ValueError: {ve}"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "Failed", "message": f"Error adding customer: {e}"}, status=500)

    return JsonResponse({"status": "Failed", "message": "Invalid request method or headers"}, status=405)




def party_list_view(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)
 
    # Fetch data from party_table
    data = list(
        party_table.objects.filter(status=1, company_id=company_id)
        .order_by('-id')
        .values()
    )

    def get_task_badge(status): 
        status_badges = {
            'C': '<span class="badge bg-secondary">Conscientiousness</span>',
            'D': '<span class="badge bg-danger">Dominance</span>',
            'S': '<span class="badge bg-primary">Steadiness</span>',
            'I': '<span class="badge bg-warning">Influence</span>',  
        }
        return status_badges.get(status, '<span class="badge bg-secondary">Unknown</span>')

    formatted = []
    for index, item in enumerate(data):
        # Construct party_type dynamically based on the provided fields
        party_type_list = []

        if item.get('is_supplier', 0) == 1:
            party_type_list.append('Supplier')
        if item.get('is_mill', 0) == 1:
            party_type_list.append('Mill')
        if item.get('is_knitting', 0) == 1:
            party_type_list.append('Knitting')
        if item.get('is_process', 0) == 1:
            party_type_list.append('Process')
        if item.get('is_compacting', 0) == 1:
            party_type_list.append('Compacting')
        if item.get('is_cutting', 0) == 1:
            party_type_list.append('Cutting')
        if item.get('is_stiching', 0) == 1:
            party_type_list.append('Stitching')
        if item.get('is_ironing', 0) == 1: 
            party_type_list.append('Ironing')
        if item.get('is_trader', 0) == 1:
            party_type_list.append('Trader')
        if item.get('is_fabric', 0) == 1:
            party_type_list.append('Fabric')

        # Join the selected party types or return '-'
        party_type = ', '.join(party_type_list) if party_type_list else '-'

        # Fetch the supply items
        supply_item_name = getSupplyItems(item_table, item['supply_items']) if item.get('supply_items') else "-"

        formatted.append({
            'action': '<button type="button" onclick="party_edit(\'{}\')" class="btn btn-primary btn-xs">'
                      '<i class="feather icon-edit"></i></button> '
                      '<button type="button" onclick="party_delete(\'{}\')" class="btn btn-danger btn-xs">'
                      '<i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
            'id': index + 1, 
            'party_type': party_type,  
            'supply_items': supply_item_name,  # Get the supply item names
            'prefix': item['prefix'] if item['prefix'] else '-', 
            'email': item['email'] if item['email'] else '-', 
            'gstin': item['gstin'] if item['gstin'] else '-', 
            'name': item['name'] if item['name'] else '-', 
            'phone': item['phone'] if item['phone'] else '-', 
            'nick_name': item['nick_name'] if item['nick_name'] else '-', 
            'cp_name': getCPName(party_contact_table, item['id']), 
            'cp_mobile': getCPMobile(party_contact_table, item['id']), 
            'customer_type': get_task_badge(item.get('customer_type', '-')),
            'address': item['address'] if item['address'] else '-', 
            'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted})


def getSupplyItems(tbl, dia_id):
    print('Raw supplyitem-id:', dia_id)

    try:
        if not dia_id:
            print("⚠️ supply_items is empty or None")
            return "-"

        dia_ids = [int(d.strip()) for d in str(dia_id).split(',') if d.strip().isdigit()]
        print('Parsed dia_ids:', dia_ids)

        # Optional status=1 if you need only active items
        existing_qs = tbl.objects.filter(id__in=dia_ids)  # or add , status=1
        existing_ids = set(existing_qs.values_list('id', flat=True))
        missing = set(dia_ids) - existing_ids

        if missing:
            print(f"⚠️ These IDs not found in table: {missing}")

        dia_list = list(existing_qs.values_list('name', flat=True))
        print('Matched dia_list:', dia_list)

        if dia_list:
            return ", ".join(map(str, dia_list))
        else:
            return "-"
    except Exception as e:
        print(f"❌ Error fetching dia for dia_id {dia_id}: {e}")
        return "-"



def getCPName(tbl, uom_id):
    try:
        # Get the latest contact for the party_id by ordering descending by 'id'
        UOM = tbl.objects.filter(party_id=uom_id).order_by('-id').first().cp_name
    except AttributeError:
        # This will handle the case when there is no contact entry found for the party
        UOM = "-"
    return UOM

def getCPMobile(tbl, uom_id):
    try:
        # Get the latest contact for the party_id by ordering descending by 'id'
        UOM = tbl.objects.filter(party_id=uom_id).order_by('-id').first().cp_mobile
    except AttributeError:
        # This will handle the case when there is no contact entry found for the party
        UOM = "-"
    return UOM




def party_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "product", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            party_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except party_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})





def contact_list(request):
    contacts = party_contact_table.objects.all()
    return render(request, 'contacts.html', {'contacts': contacts})

def add_contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        designation = request.POST.get("designation")
        customer_id = request.POST.get("customer_id")
        print('customer-id:',customer_id)

        contact = party_contact_table.objects.create(
            cp_name=name,
            cp_email=email,
            cp_mobile=phone,
            designation=designation,
            party_id=customer_id
        ) 

        return JsonResponse({
            "id": contact.id,
            "name": contact.cp_name,
            "email": contact.cp_email,
            "phone": contact.cp_mobile,
            "designation": contact.designation
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


 

def delete_contact(request, contact_id):
    try: 
        contact = party_contact_table.objects.get(id=contact_id)
        contact.delete()
        return JsonResponse({"success": True})
    except party_contact_table.DoesNotExist:
        return JsonResponse({"error": "Contact not found"}, status=404)




import os

def delete_photo(request, photo_id):
    try: 
        photo = get_object_or_404(party_photo_table, id=photo_id)
        
        # Delete the file from the media folder
        if photo.photo:
            if os.path.exists(photo.photo.path):
                os.remove(photo.photo.path)
        
        # Delete the record from the database
        photo.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



def edit_photo_remarks(request, photo_id): 
    if request.method == "POST":
        new_remarks = request.POST.get("remarks")
        
        photo = get_object_or_404(party_photo_table, id=photo_id)
        photo.remarks = new_remarks
        photo.save()
        
        return JsonResponse({"success": True, "remarks": photo.remarks})
    
    return JsonResponse({"error": "Invalid request"}, status=400)




def update_photo(request, photo_id):
    if request.method == "POST":
        photo_obj = get_object_or_404(party_photo_table, id=photo_id)

        # Update remarks
        new_remarks = request.POST.get("remarks", "").strip()
        if new_remarks:
            photo_obj.remarks = new_remarks
  
        # Check if a new photo is uploaded
        if "photo" in request.FILES:
            # Delete old photo if it exists
            if photo_obj.photo:
                if os.path.exists(photo_obj.photo.path):
                    os.remove(photo_obj.photo.path) 

            # Save new photo
            new_photo = request.FILES["photo"]
            photo_obj.photo = new_photo
        
        # Save changes
        photo_obj.save()

        return JsonResponse({
            "success": True, 
            "photo_id": photo_obj.id,
            "photo_url": photo_obj.photo.url if photo_obj.photo else None,
            "remarks": photo_obj.remarks
        })

    return JsonResponse({"error": "Invalid request"}, status=400)




def party_details_edit(request):
    encoded_id = request.GET.get('id') 
    try:
        decoded_id = base64.b64decode(encoded_id).decode('utf-8')  # Decode the ID 
        print('decoded-id:', decoded_id)
        
        customer = get_object_or_404(party_table, id=decoded_id)  # Fetch the customer details
        company = company_table.objects.filter(status=1)
        supply = item_table.objects.filter(status=1)  # Fetch all supply items
        print('customer-price-id:',customer.price_list_id)
        
        # Retrieve the stored comma-separated supply item IDs
        selected_supply_ids = customer.supply_items  # This is a string like "1,2,3"
        
        # Convert it into a list of integers (handling empty or None cases)
        if selected_supply_ids:
            selected_supply_ids = [int(i) for i in selected_supply_ids.split(',') if i.isdigit()]
        else:
            selected_supply_ids = []

        # Fetch selected supply items from item_group_table
        selected_supply_items = item_group_table.objects.filter(id__in=selected_supply_ids)

        contacts = party_contact_table.objects.filter(party_id=decoded_id)  # Retrieve all contact details
        photos = party_photo_table.objects.filter(party_id=decoded_id)
        price_list = price_list_table.objects.filter(status=1)
        return render(request, 'master/party_details_update.html', { 
            'photos': photos, 
            'customer': customer,
            'price_list':price_list, 
            'supply': supply, 
            'selected_supply_ids': selected_supply_ids,  # Pass list of IDs
            'selected_supply_items': selected_supply_items,  # Pass selected items for names
            'contacts': contacts,
            'company': company
        })
    except Exception as e:
        return HttpResponse(f"Error: {e}")  # Handle errors

 


@csrf_exempt
def party_detail_update(request): 
    if request.method == "POST":
        user_id = request.session['user_id']
        customer_id = request.POST.get('customer_id')
        print('customer-id:', customer_id)
        customer_name = request.POST.get('name')
        party_code = request.POST.get('party_code')
        nick_name = request.POST.get('nick_name')
        prefix = request.POST.get('prefix')
        mobile_number = request.POST.get('mobile') 
        customer_type = request.POST.get('customer_type')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        refered_by = request.POST.get('refered_by')
        udyam_no = request.POST.get('udyam_no') 
        price_list_id = request.POST.get('price_list')

        is_knitting = 1 if request.POST.get('is_knitting') else 0
        is_trader = 1 if request.POST.get('is_trader') else 0
        is_b_d = 1 if request.POST.get('is_b_d') else 0
        # is_dyeing = 1 if request.POST.get('is_dyeing') else 0 
        is_compacting = 1 if request.POST.get('is_compacting') else 0
        is_ironing = 1 if request.POST.get('is_ironing') else 0 
        is_stiching = 1 if request.POST.get('is_stiching') else 0
        is_cutting = 1 if request.POST.get('is_cutting') else 0
        is_fabric = 1 if request.POST.get('is_fabric') else 0
        # is_sticker = 1 if request.POST.get('is_sticker') else 0
        # is_label = 1 if request.POST.get('is_label') else 0
        
        remarks = request.POST.get('remarks')
        is_supplier = 1 if request.POST.get('is_supplier') else 0
        is_mill = 1 if request.POST.get('is_mill') else 0
        # Update customer details


        supply_ids = request.POST.getlist('supply_id')  

        supply_id_str = ','.join([str(c) for c in supply_ids if c.isdigit()])  # Filter out non-numeric values
       
        customer = get_object_or_404(party_table, id=customer_id)
        customer.supply_items = supply_id_str
        customer.name = customer_name
        # customer.party_code = party_code
        customer.mobile = mobile_number
        customer.is_supplier = is_supplier
        customer.price_list_id = price_list_id 
        customer.is_mill = is_mill
        customer.is_knitting = is_knitting
        customer.is_process=is_b_d
        # customer.is_dyeing=is_dyeing
        customer.is_compacting=is_compacting
        customer.is_cutting=is_cutting
        # customer.is_sticker=is_sticker
        # customer.is_label=is_label
        customer.is_fabric=is_fabric
        customer.is_stiching=is_stiching
        customer.is_trader=is_trader 
        customer.is_ironing=is_ironing
        customer.phone = phone
        customer.nick_name = nick_name
        customer.prefix = prefix
        customer.email = email
        customer.udyam_no = udyam_no
        customer.address = address
        customer.city = city
        customer.pincode = pincode
        customer.state = state
        customer.latitude = latitude
        customer.longitude = longitude 
        # customer.refered_by = refered_by

        # Store working days as a comma-separated string
       
        customer.description = remarks
        customer.updated_on = timezone.now()
        customer.save()

        # # Process contact data if any
        # contact_data = request.POST.get('contact_data')
        # if contact_data:
        #     contacts = json.loads(contact_data)

        #     # Update or create contacts
        #     for contact in contacts:
        #         # dob = contact.get('dob')
        #         # parsed_dob = parse_date(dob) if dob else None

        #         # if dob and not parsed_dob:
        #         #     return JsonResponse({'result': 'no', 'error': f'Invalid date format for DOB: {dob}'})

        #         existing_contact = party_contact_table.objects.filter(
        #             party_id=customer.id,    
        #             cp_email=contact['ph_email']  # Assuming email is used to identify contacts
        #         ).first()

        #         if existing_contact:
        #             # Update existing contact
        #             existing_contact.cp_name = contact['ph_name']
        #             existing_contact.cp_email = contact['ph_email']
        #             existing_contact.cp_mobile = contact['ph_phone']
        #             existing_contact.designation = contact['designation']
        #             existing_contact.updated_on = timezone.now()
        #             existing_contact.updated_by = user_id
        #             existing_contact.save()
        #         else:
        #             # Create new contact
        #             party_contact_table.objects.create(
        #                 party_id=customer.id,
        #                 cp_name=contact['ph_name'],
        #                 cp_email=contact['ph_email'],
        #                 cp_mobile=contact['ph_phone'],
        #                 designation=contact['designation'],
        #                 is_active=1,
        #                 updated_on=timezone.now(),
        #                 updated_by=user_id
        #             )

        return JsonResponse({'result': 'yes', 'id': customer.id})  

    return JsonResponse({'result': 'no'})



@csrf_exempt
def update_contact(request, contact_id): 
    if request.method == "POST":
        try:
            contact = party_contact_table.objects.get(id=contact_id) 
            contact.cp_name = request.POST.get("name", contact.cp_name)
            contact.cp_email = request.POST.get("email", contact.cp_email)
            contact.cp_mobile = request.POST.get("phone", contact.cp_mobile)
            contact.designation = request.POST.get("designation", contact.designation)
            contact.save()
            return JsonResponse({"status": "success"})
        except party_contact_table.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Contact not found"}, status=404)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def add_party_photo(request):
    if request.method == "POST":
        photo = request.FILES.get("photo") 
        remarks = request.POST.get("remarks")
        party_id = request.POST.get("party_id")

        if not photo or not remarks or not party_id:
            return JsonResponse({"status": "Error", "message": "Missing required fields"})

        new_photo = party_photo_table.objects.create(
            photo=photo, remarks=remarks, party_id=party_id
        )

        return JsonResponse({
            "status": "Success",
            "photo_id": new_photo.id,
            "photo_url": new_photo.photo.url
        })

    return JsonResponse({"status": "Error", "message": "Invalid request"}, status=400)



def add_party_photo_bjk3(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        remarks = request.POST.get("remarks")
        party_id = request.POST.get("party_id")

        if not photo or not remarks or not party_id:
            return JsonResponse({"status": "Error", "message": "Missing required fields"})

        new_photo = party_photo_table.objects.create(
            photo=photo, remarks=remarks, party_id=party_id
        )

        return JsonResponse({
            "status": "Success",
            "photo_id": new_photo.id,
            "photo_url": new_photo.photo.url
        })

    return JsonResponse({"status": "Error", "message": "Invalid request"}, status=400)




def party_photo_view(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    party_id = request.POST.get('party_id')
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(party_photo_table.objects.filter(status=1,party_id=party_id).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="party_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="party_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'photo': item['photo'] if item['photo'] else'-', 
            'remarks': item['remarks'] if item['remarks'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




# ````````````````````````` uom `````````````````````````````````



def uom(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/uom.html')
    else:
        return HttpResponseRedirect("/signin")



def uom_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(uom_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="uom_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="uom_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})



def uom_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = uom_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


# def uom_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "create")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if is_ajax and request.method == "POST":  
#         user_id = request.session['user_id']
#         frm = request.POST
#         uname = frm.get('name')
#         uom = uom_table()
#         uom.name=uname
#         uom.created_on=datetime.now()
#         uom.created_by=user_id
#         uom.updated_on=datetime.now()
#         uom.updated_by=user_id
#         uom.save()
#         res = "Success"
#         return JsonResponse({"data": res})






# def uom_update(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         uom_id = request.POST.get('id')
#         name = request.POST.get('name')
#         is_active = request.POST.get('is_active')
        
#         try:
#             uom = uom_table.objects.get(id=uom_id)
#             uom.name = name
#             uom.is_active = is_active
#             uom.updated_by = user_id
#             uom.updated_on = datetime.now()
#             uom.save()
#             return JsonResponse({'message': 'success'})
#         except uom_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'UOM not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})




def uom_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        raw_name = frm.get('name', '')

        # Normalize the name: strip spaces and uppercase
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check if it already exists
        if uom_table.objects.filter(name__iexact=normalized_name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'UOM with this name already exists.'
            }, status=400)

        # Save cleaned name
        uom = uom_table()
        uom.name = normalized_name
        uom.created_on = datetime.now()
        uom.created_by = user_id
        uom.updated_on = datetime.now()
        uom.updated_by = user_id
        uom.save()

        return JsonResponse({"data": "Success"})



def uom_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        uom_id = request.POST.get('id')
        raw_name = request.POST.get('name', '')
        is_active = request.POST.get('is_active')

        # Normalize the name
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for duplicate name excluding current record
        duplicates = uom_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=uom_id)
        if duplicates.exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'UOM with this name already exists.'
            }, status=400)

        try:
            uom = uom_table.objects.get(id=uom_id)
            uom.name = normalized_name
            uom.is_active = is_active
            uom.updated_by = user_id
            uom.updated_on = datetime.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except uom_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'UOM not found'})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def uom_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            uom_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except uom_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})






# ````````````````````````` DIA `````````````````````````````````



def dia(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/dia.html')
    else:
        return HttpResponseRedirect("/signin")



def dia_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(dia_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="dia_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="dia_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})



def dia_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = dia_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


# def dia_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "create")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if is_ajax and request.method == "POST":  
#         user_id = request.session['user_id']
#         frm = request.POST
#         uname = frm.get('name')
        
#         if dia_table.objects.filter(name__iexact=uname, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Dia with this name already exists.'
#             }, status=400)
        

#         dia = dia_table()
#         dia.name=uname
#         dia.created_on=datetime.now()
#         dia.created_by=user_id
#         dia.updated_on=datetime.now()
#         dia.updated_by=user_id
#         dia.save()
#         res = "Success"
#         return JsonResponse({"data": res})






# def dia_update(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         dia_id = request.POST.get('id')
#         name = request.POST.get('name')
#         is_active = request.POST.get('is_active')
        
#         if dia_table.objects.filter(name__iexact=name, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',  
#                 'error_message': 'Dia with this name already exists.'
#             }, status=400)
        


#         try:
#             dia = dia_table.objects.get(id=dia_id)
#             dia.name = name
#             dia.is_active = is_active
#             dia.updated_by = user_id
#             dia.updated_on = datetime.now()
#             dia.save()
#             return JsonResponse({'message': 'success'})
#         except dia_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'dia not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def normalize_name(name):
    return ' '.join(name.strip().upper().split())


def dia_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        raw_name = frm.get('name')
        normalized_name = normalize_name(raw_name)

        if dia_table.objects.filter(name__iexact=normalized_name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Dia with this name already exists.'
            }, status=400)

        dia = dia_table()
        dia.name = normalized_name
        dia.created_on = datetime.now()
        dia.created_by = user_id
        dia.updated_on = datetime.now()
        dia.updated_by = user_id
        dia.save()
        return JsonResponse({"data": "Success"})


def dia_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        dia_id = request.POST.get('id')
        raw_name = request.POST.get('name')
        is_active = request.POST.get('is_active')
        normalized_name = normalize_name(raw_name)

        if dia_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=dia_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Dia with this name already exists.'
            }, status=400)

        try:
            dia = dia_table.objects.get(id=dia_id)
            dia.name = normalized_name
            dia.is_active = is_active
            dia.updated_by = user_id
            dia.updated_on = datetime.now()
            dia.save()
            return JsonResponse({'message': 'success'})
        except dia_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Dia not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



 
def delete_dia(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            dia_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except dia_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})






# ````````````````````````` gauge `````````````````````````````````



def gauge(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/gauge.html')
    else:
        return HttpResponseRedirect("/signin")



def gauge_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(gauge_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="gauge_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="gauge_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})





def gauge_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = gauge_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



# def gauge_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "create")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if is_ajax and request.method == "POST":  
#         user_id = request.session['user_id']
#         frm = request.POST
#         uname = frm.get('name')
#         if gauge_table.objects.filter(name__iexact=uname, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Gauge with this name already exists.'
#             }, status=400)
        


#         gauge = gauge_table()
#         gauge.name=uname
#         gauge.created_on=datetime.now()
#         gauge.created_by=user_id
#         gauge.updated_on=datetime.now()
#         gauge.updated_by=user_id
#         gauge.save()
#         res = "Success"
#         return JsonResponse({"data": res})



# def gauge_update(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         gauge_id = request.POST.get('id')
#         name = request.POST.get('name')
#         is_active = request.POST.get('is_active')
        

#         if gauge_table.objects.filter(name__iexact=name, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Gauge  with this name already exists.'
#             }, status=400)
        


#         try:
#             gauge = gauge_table.objects.get(id=gauge_id)
#             gauge.name = name
#             gauge.is_active = is_active
#             gauge.updated_by = user_id
#             gauge.updated_on = datetime.now()
#             gauge.save()
#             return JsonResponse({'message': 'success'})
#         except gauge_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'gauge not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def gauge_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        raw_name = frm.get('name', '')

        # Normalize: trim, collapse spaces, and uppercase
        normalized_name = ' '.join(raw_name.strip().upper().split())

        if gauge_table.objects.filter(name__iexact=normalized_name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Gauge with this name already exists.'
            }, status=400)

        gauge = gauge_table()
        gauge.name = normalized_name
        gauge.created_on = datetime.now()
        gauge.created_by = user_id
        gauge.updated_on = datetime.now()
        gauge.updated_by = user_id
        gauge.save()
        return JsonResponse({"data": "Success"})


def gauge_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        gauge_id = request.POST.get('id')
        raw_name = request.POST.get('name', '')
        is_active = request.POST.get('is_active')

        # Normalize input name
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for duplicates excluding the current record
        if gauge_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=gauge_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Gauge with this name already exists.'
            }, status=400)

        try:
            gauge = gauge_table.objects.get(id=gauge_id)
            gauge.name = normalized_name
            gauge.is_active = is_active
            gauge.updated_by = user_id
            gauge.updated_on = datetime.now()
            gauge.save()
            return JsonResponse({'message': 'success'})
        except gauge_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Gauge not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})




def gauge_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            gauge_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except gauge_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})






# ````````````````````````` tex `````````````````````````````````



def tex(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/tex.html')
    else:
        return HttpResponseRedirect("/signin")



def tex_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(tex_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="tex_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="tex_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})





def tex_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = tex_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def tex_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        raw_name = request.POST.get('name')
        normalized_name = normalize_name(raw_name)

        if tex_table.objects.filter(name__iexact=normalized_name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Tex with this name already exists.'
            }, status=400)

        tex = tex_table()
        tex.name = normalized_name
        tex.created_on = datetime.now()
        tex.created_by = user_id
        tex.updated_on = datetime.now()
        tex.updated_by = user_id
        tex.save()
        return JsonResponse({"data": "Success"})



def tex_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        tex_id = request.POST.get('id')
        raw_name = request.POST.get('name')
        is_active = request.POST.get('is_active')
        normalized_name = normalize_name(raw_name)

        if tex_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=tex_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Tex with this name already exists.'
            }, status=400)

        try:
            tex = tex_table.objects.get(id=tex_id) 
            tex.name = normalized_name
            tex.is_active = is_active
            tex.updated_by = user_id
            tex.updated_on = datetime.now()
            tex.save()
            return JsonResponse({'message': 'success'})
        except tex_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Tex not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


# def tex_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "create")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if is_ajax and request.method == "POST":  
#         user_id = request.session['user_id']
#         frm = request.POST
#         uname = frm.get('name')
        
#         if tex_table.objects.filter(name__iexact=uname, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Tex with this name already exists.'
#             }, status=400)

 

#         tex = tex_table()
#         tex.name=uname
#         tex.created_on=datetime.now()
#         tex.created_by=user_id
#         tex.updated_on=datetime.now()
#         tex.updated_by=user_id
#         tex.save()
#         res = "Success"
#         return JsonResponse({"data": res})




# def tex_update(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         tex_id = request.POST.get('id')
#         name = request.POST.get('name')
#         is_active = request.POST.get('is_active')
    
            
#         if tex_table.objects.filter(name__iexact=name, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Tex with this name already exists.'
#             }, status=400)

#         try:
#             tex = tex_table.objects.get(id=tex_id)
#             tex.name = name
#             tex.is_active = is_active
#             tex.updated_by = user_id
#             tex.updated_on = datetime.now()
#             tex.save()
#             return JsonResponse({'message': 'success'})
#         except tex_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'tex not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def tex_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            tex_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except tex_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



# ``````````````````````````` COlOR`````````````````````````````````````````````````





def color(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/color.html')
    else:
        return HttpResponseRedirect("/signin")



def color_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access: 
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(color_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="color_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="color_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'color': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})



def color_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = color_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



 

# def color_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "create")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if is_ajax and request.method == "POST":  
#         user_id = request.session['user_id']
#         frm = request.POST
#         uname = frm.get('name')

#         if color_table.objects.filter(name__iexact=uname, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Color with this name already exists.'
#             }, status=400)
        


#         color = color_table()
#         color.name=uname
#         color.created_on=datetime.now()
#         color.created_by=user_id
#         color.updated_on=datetime.now()
#         color.updated_by=user_id
#         color.save()
#         res = "Success"
#         return JsonResponse({"data": res})



# def color_update(request):
#     user_type = request.session.get('user_type') 
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         color_id = request.POST.get('id')
#         name = request.POST.get('name')
#         is_active = request.POST.get('is_active')

#         if color_table.objects.filter(name__iexact=name, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Color with this name already exists.'
#             }, status=400)
        
        
#         try:
#             color = color_table.objects.get(id=color_id)
#             color.name = name
#             color.is_active = is_active
#             color.updated_by = user_id
#             color.updated_on = datetime.now()
#             color.save()
#             return JsonResponse({'message': 'success'})
#         except color_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'color not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})




def color_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        raw_name = frm.get('name', '')

        # Normalize the color name (trim + uppercase + collapse spaces)
        normalized_name = ' '.join(raw_name.strip().upper().split())

        if color_table.objects.filter(name__iexact=normalized_name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Color with this name already exists.'
            }, status=400)

        color = color_table()
        color.name = normalized_name
        color.created_on = datetime.now()
        color.created_by = user_id
        color.updated_on = datetime.now()
        color.updated_by = user_id 
        color.save()

        return JsonResponse({"data": "Success"})




def color_update(request):
    user_type = request.session.get('user_type') 
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        color_id = request.POST.get('id')
        raw_name = request.POST.get('name', '')
        is_active = request.POST.get('is_active')

        # Normalize input
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for duplicates excluding current color
        if color_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=color_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Color with this name already exists.'
            }, status=400)

        try:
            color = color_table.objects.get(id=color_id)
            color.name = normalized_name
            color.is_active = is_active
            color.updated_by = user_id
            color.updated_on = datetime.now()
            color.save()
            return JsonResponse({'message': 'success'})
        except color_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Color not found'})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def color_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            color_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except color_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




# ````````````````````````` Count `````````````````````````````````



def count(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/count.html')
    else:
        return HttpResponseRedirect("/signin")



def count_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(count_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="count_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="count_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'count': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def count_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('count')

        if count_table.objects.filter(name__iexact=uname, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Count with this name already exists.'
            }, status=400)
        
        count = count_table()
        count.name=uname
        count.created_on=datetime.now()
        count.created_by=user_id
        count.updated_on=datetime.now()
        count.updated_by=user_id
        count.save()
        res = "Success"
        return JsonResponse({"data": res})




def count_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = count_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def count_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        count_id = request.POST.get('id')
        name = request.POST.get('count')
        is_active = request.POST.get('is_active')
        
        if count_table.objects.filter(name__iexact=uname, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Count with this name already exists.'
            }, status=400)
        


        try:
            count = count_table.objects.get(id=count_id)
            count.name = name
            count.is_active = is_active
            count.updated_by = user_id
            count.updated_on = datetime.now()
            count.save()
            return JsonResponse({'message': 'success'})
        except count_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'count not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def count_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            count_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except count_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


# ````````````````````````` Bag `````````````````````````````````



def bag(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/bag.html')
    else:
        return HttpResponseRedirect("/signin")



def bag_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(bag_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="bag_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="bag_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1,  
            
            'bag_wt': item['name'] if item['name'] else'-', 
            'wt': item['wt'] if item['wt'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def bag_add(request):
    user_type = request.session.get('user_type') 
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('bag')
        wt = frm.get('wt')
        bag = bag_table()
        bag.name=uname
        bag.wt=wt
        bag.created_on=datetime.now()
        bag.created_by=user_id
        bag.updated_on=datetime.now()
        bag.updated_by=user_id
        bag.save()
        res = "Success"
        return JsonResponse({"data": res})




def bag_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = bag_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def bag_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        bag_id = request.POST.get('id')
        name = request.POST.get('name')
        wt = request.POST.get('wt')
        is_active = request.POST.get('is_active')
        
        try:
            bag = bag_table.objects.get(id=bag_id)
            bag.name = name 
            bag.wt = wt
            bag.is_active = is_active
            bag.updated_by = user_id
            bag.updated_on = datetime.now()
            bag.save()
            return JsonResponse({'message': 'success'})
        except bag_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'bag not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def bag_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting 
            bag_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except bag_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})





# ````````````````````````` Fabric `````````````````````````````````



def fabric(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        uom = uom_table.objects.filter(status=1)
        return render(request,'master/fabric.html',{'uom':uom})
    else:
        return HttpResponseRedirect("/signin")



def fabric_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(fabric_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="fabric_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="fabric_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def getUOMName(tbl, uom_id):
    try:
        UOM = tbl.objects.get(id=uom_id).name
    except ObjectDoesNotExist:
        UOM = "-"  # Handle the error by providing a default value or appropriate message
    return UOM



# def fabric_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "create")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if is_ajax and request.method == "POST":  
#         user_id = request.session['user_id']
#         frm = request.POST
#         uname = frm.get('name')
#         uom = frm.get('uom_id')
        
#         if fabric_table.objects.filter(name__iexact=uname, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Fabric with this name already exists.'
#             }, status=400)

#         fabric = fabric_table()
#         fabric.name=uname
#         fabric.created_on=datetime.now()
#         fabric.created_by=user_id
#         fabric.updated_on=datetime.now()
#         fabric.updated_by=user_id
#         fabric.save()
#         res = "Success"
#         return JsonResponse({"data": res})


def fabric_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        user_id = request.session.get('user_id')
        frm = request.POST
        raw_name = frm.get('name', '')
        uom = frm.get('uom_id')

        # Normalize name: trim, collapse internal spaces, uppercase
        def normalize_name(name):
            return ' '.join(name.strip().upper().split())

        uname_normalized = normalize_name(raw_name)

        # Check for existing fabric with normalized name
        existing_fabrics = fabric_table.objects.filter(status=1)
        for fabric in existing_fabrics:
            if normalize_name(fabric.name) == uname_normalized:
                return JsonResponse({
                    'message': 'error',
                    'error_message': 'Fabric with this name already exists.'
                }, status=400)

        # Save new fabric with trimmed name
        fabric = fabric_table(
            name=raw_name.strip(),
            created_on=datetime.now(),
            created_by=user_id,
            updated_on=datetime.now(),
            updated_by=user_id
        )
        fabric.save()
        return JsonResponse({"data": "Success"})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)


def fabric_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = fabric_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



# def fabric_update(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         fabric_id = request.POST.get('id')
#         name = request.POST.get('name')

#         is_active = request.POST.get('is_active')

#         if fabric_table.objects.filter(name__iexact=name, status=1).exists():
#             return JsonResponse({
#                 'message': 'error',
#                 'error_message': 'Fabric with this name already exists.'
#             }, status=400)
#         try:
#             fabric = fabric_table.objects.get(id=fabric_id)
#             fabric.name = name
#             fabric.is_active = is_active
#             fabric.updated_by = user_id
#             fabric.updated_on = datetime.now()
#             fabric.save()
#             return JsonResponse({'message': 'success'})
#         except fabric_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'fabric not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def fabric_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_id = request.POST.get('id')
        raw_name = request.POST.get('name', '')
        is_active = request.POST.get('is_active')

        # Normalize name: trim, collapse spaces, uppercase
        def normalize_name(name):
            return ' '.join(name.strip().upper().split())

        new_name_normalized = normalize_name(raw_name)

        # Check for duplicates excluding the current record
        existing_fabrics = fabric_table.objects.filter(status=1).exclude(id=fabric_id)
        for fabric in existing_fabrics:
            if normalize_name(fabric.name) == new_name_normalized:
                return JsonResponse({
                    'message': 'error',
                    'error_message': 'Fabric with this name already exists.'
                }, status=400)

        try:
            fabric = fabric_table.objects.get(id=fabric_id)
            fabric.name = raw_name.strip()  # Save trimmed name
            fabric.is_active = is_active
            fabric.updated_by = user_id
            fabric.updated_on = datetime.now()
            fabric.save()
            return JsonResponse({'message': 'success'})
        except fabric_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Fabric not found'})
    
    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)


def fabric_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "fabric", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            fabric_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except fabric_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


 
# ````````````````````````` Fabric Program `````````````````````````````````



def fabric_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        count = count_table.objects.filter(status=1) 
        gauge = gauge_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1).order_by('name')
        fabric = fabric_table.objects.filter(status=1).order_by('name')
        color = color_table.objects.filter(status=1).order_by('name')
        dia = dia_table.objects.filter(status=1).order_by('name')
        return render(request,'master/fabric_program.html',{'count':count,'fabric':fabric,'dia':dia,
                                                        'color':color,'gauge':gauge,'tex':tex})
    else:
        return HttpResponseRedirect("/signin") 



def fabric_prg_list(request):
    company_id = request.session['company_id'] 
    print('company_id:', company_id)

    data = list(fabric_program_table.objects.filter(status=1).order_by('-id').values())

    formatted = [ 
        {
            'action': '<button type="button" onclick="prg_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                    <button type="button" onclick="prg_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id'], ),
                        #  <button type="button" onclick="prg_dia_edit(\'{}\')" class="btn btn-info btn-xs">Dia</button>  '.format(item['id'], item['id'], item['id']),
            'id': index + 1,  
            'name': item['name'] if item['name'] else '-',  
            'gray_gsm': item['gray_gsm'] if item['gray_gsm'] else '-',  
            'fabric': getIdByName(fabric_table, item['fabric_id']), 
            'count': getCountByName(count_table, item['count_id']), 
            'gauge': getIdByName(gauge_table, item['gauge_id']), 
            'tex': getIdByName(tex_table, item['tex_id']), 
            'dia': getDiaById(dia_table, item['dia_id']),  # ✅ Now returns comma-separated values
            'color': getDiaById(color_table, item['color_id']),  # ✅ Now returns comma-separated values
            'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        } 
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})


def getDiaById(tbl, dia_id):
    print('supplyitem-id:', dia_id)
    try:
        # Split the comma-separated string and convert it into a list of integers
        dia_ids = [int(d) for d in str(dia_id).split(',') if d.isdigit()]

        # Fetch dia names for the given list of IDs
        dia_list = tbl.objects.filter(id__in=dia_ids).values_list('name', flat=True)

        if dia_list:
            return ", ".join(map(str, dia_list))  # Convert list to a comma-separated string
        else:
            return "-"
    except Exception as e:
        print(f"Error fetching dia for dia_id {dia_id}: {e}")
        return "-"





# def getDiaById(tbl, dia_id):
#     print('dia-id:',dia_id)
#     try:
#         dia_list = tbl.objects.filter(id=dia_id, status=1).values_list('name', flat=True)
#         if dia_list:
#             return ", ".join(map(str, dia_list))  # Convert list of numbers to comma-separated string
#         else:
#             return "-"
#     except Exception as e:
#         print(f"Error fetching dia for dia_id {dia_id}: {e}")
#         return "-"


def getCountByName(tbl, count_id):
    try:
        party = tbl.objects.get(id=count_id).name 
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message 
    return party

def getIdByName(tbl, count_id):
    try:
        party = tbl.objects.get(id=count_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message 
    return party


def fabric_dia_list(request):
    fabric = request.POST.get('fabric')

    data = list(fabric_dia_table.objects.filter(status=1,fabric_prg_id=fabric).order_by('-id').values())

    formatted = [ 
        {
            'action': '<button type="button" onclick="dia_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                    <button type="button" onclick="dia_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format( item['id'], item['id']),
            'id': index + 1,  
            'dia': item['dia'] if item['dia'] else '-',  
        
            'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        } 
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})



def fabric_dia_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = fabric_dia_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



from django.http import JsonResponse
from .models import fabric_dia_table  # Import your model
from django.views.decorators.csrf import csrf_exempt



from django.http import JsonResponse
from .models import fabric_dia_table  # Import your model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Allows POST without CSRF token in testing (not recommended for production)
def update_dia(request):
    if request.method == "POST":
        dia_id = request.POST.get('id')  
        dia_value = request.POST.get('dia')  
        fabric_prg_id = request.POST.get('fabric_prg_id')  

        # Check if Dia value is provided
        if not dia_value:
            return JsonResponse({'error': 'Dia value cannot be empty'}, status=400)

        try:
            if dia_id:  
                # If ID exists, update the record
                dia_record = fabric_dia_table.objects.get(id=dia_id)
                dia_record.dia = dia_value
                dia_record.fabric_prg_id = fabric_prg_id  # Ensure this field exists in the model
                dia_record.save()

                return JsonResponse({'success': True, 'message': 'Dia updated successfully'})
            
            else:
                # If ID is empty, create a new record
                new_dia = fabric_dia_table.objects.create(
                    dia=dia_value,
                    fabric_prg_id=fabric_prg_id
                )
                return JsonResponse({'success': True, 'message': 'Dia added successfully', 'new_id': new_dia.id})

        except fabric_dia_table.DoesNotExist:
            return JsonResponse({'error': 'Dia record not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)




@csrf_exempt  # Allows POST without CSRF token in testing (not recommended for production)
def update_dia_test(request):
    if request.method == "POST":
        dia_id = request.POST.get('id')  
        dia_value = request.POST.get('dia')  
        fabric_prg_id = request.POST.get('fabric_prg_id')  

        # Check if Dia value is provided
        if not dia_value:
            return JsonResponse({'error': 'Dia value cannot be empty'}, status=400)

        try:
            # Fetch the existing Dia record
            dia_record = fabric_dia_table.objects.get(id=dia_id)

            # Update the fields
            dia_record.dia = dia_value
            dia_record.fabric_prg_id = fabric_prg_id  # Ensure this field exists in the model
            dia_record.save()

            return JsonResponse({'success': True, 'message': 'Dia updated successfully'})

        except fabric_dia_table.DoesNotExist:
            return JsonResponse({'error': 'Dia record not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)







def fabric_prg_add(request):
    user_type = request.session.get('user_type') 
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        name = frm.get('name')
        fabric = frm.get('fabric')
        count = frm.get('count') 
        gauge = frm.get('gauge')
        tex = frm.get('tex')
        gray_gsm = frm.get('gray_gsm')

        # Handling multiple selected color IDs
        color_id = ','.join(request.POST.getlist('color_id'))  # Convert list to comma-separated string
        dia_id = ','.join(request.POST.getlist('dia_id'))  # Convert list to comma-separated string

        # Handling multiple dia values from tags input field
        # dia_values = request.POST.get('dia', '')  # Get dia values as a single string
        # dia_list = [d.strip() for d in dia_values.split(',') if d.strip()]  # Split and clean empty values

        # Creating fabric program entry
        fabric_prg = fabric_program_table()
        fabric_prg.name = name
        fabric_prg.fabric_id = fabric 
        fabric_prg.count_id = count
        fabric_prg.gauge_id = gauge 
        fabric_prg.tex_id = tex
        fabric_prg.gray_gsm = gray_gsm
        fabric_prg.color_id = color_id  # Storing multiple colors as a comma-separated string
        fabric_prg.dia_id = dia_id  # Storing multiple colors as a comma-separated string
        fabric_prg.created_on = datetime.now()
        fabric_prg.created_by = user_id
        fabric_prg.updated_on = datetime.now()
        fabric_prg.updated_by = user_id 
        fabric_prg.save()

        # Storing each dia as a separate entry in fabric_dia_table
        # for dia in dia_list: 
        #     try:
        #         dia_numeric = float(dia)  # Convert dia value to a number
        #         fabric_dia_table.objects.create(
        #             fabric_prg_id=fabric_prg.id,
        #             dia=dia_numeric , # Store as a number
        #             created_on = datetime.now(),
        #             created_by = user_id,
        #         )
        #     except ValueError:
        #         print(f"Skipping invalid dia value: {dia}")  # Log invalid values

        return JsonResponse({"data": "Success"})





def fabric_prg_add_bk(request):
    user_type = request.session.get('user_type') 
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        name = frm.get('name')
        fabric = frm.get('fabric')
        count = frm.get('count') 
        gauge = frm.get('gauge')
        tex = frm.get('tex')
        gray_gsm = frm.get('gray_gsm')
        
        # Handling multiple selected color IDs
        color_id = ','.join(request.POST.getlist('color_id'))  # Convert list to comma-separated string
        print('color-id:',color_id)
        dia = frm.get('dia')  

        fabric_prg = fabric_program_table()
        fabric_prg.name = name
        fabric_prg.fabric_id = fabric
        fabric_prg.count_id = count
        fabric_prg.gauge_id = gauge 
        fabric_prg.tex_id = tex
        fabric_prg.gray_gsm = gray_gsm
        fabric_prg.color_id = color_id  # Storing multiple colors as a comma-separated string
        fabric_prg.created_on = datetime.now()
        fabric_prg.created_by = user_id
        # fabric_prg.updated_on = datetime.now()
        # fabric_prg.updated_by = user_id
        fabric_prg.save()
        res = "Success"

        dia_entry = fabric_dia_table()
        dia_entry.fabric_prg_id = fabric_prg.id
        dia_entry.dia = dia  # Storing dia properly
        dia_entry.created_on = datetime.now()
        dia_entry.created_by = user_id

        dia_entry.save()

        success = 'success'
        return JsonResponse({"data": res})




def fabric_prg_add_bk_25_02_25(request):
    user_type = request.session.get('user_type') 
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        name = frm.get('name')
        fabric = frm.get('fabric')
        count = frm.get('count')  
        gauge = frm.get('gauge')
        tex = frm.get('tex')
        gray_gsm = frm.get('gray_gsm')
        color_id = frm.get('color_id')

        # dia = [value.strip() for value in request.POST.get('dia', '').split(',') if value.strip()]
        # print('dia-value:',dia)
        # dia = frm.get('dia')

        dia_values = request.POST.get('dia', '')  # Get dia values as a single string
        dia_list = [d.strip() for d in dia_values.split(',') if d.strip()]  # Split and clean empty values



        fabric_prg = fabric_program_table()
        fabric_prg.name=name
        fabric_prg.fabric_id=fabric
        fabric_prg.count_id=count
        fabric_prg.gauge_id=gauge 
        fabric_prg.tex_id=tex
        fabric_prg.gray_gsm=gray_gsm
        fabric_prg.color_id= color_id
        fabric_prg.created_on=datetime.now()
        fabric_prg.created_by=user_id
        fabric_prg.updated_on=datetime.now()
        fabric_prg.updated_by=user_id
        fabric_prg.save()

        for dia in dia_list:
            fabric_dia_table.objects.create(
                fabric_prg_id=fabric_prg.id,
                dia=dia
            )


        res = "Success"

        return JsonResponse({"data": res})


from django.http import JsonResponse
from django.forms.models import model_to_dict

def fabric_prg_edit(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST": 
        frm = request.POST
        data = fabric_program_table.objects.filter(id=request.POST.get('id')).first()  # Get the first matching record
        fabric = fabric_table.objects.filter(status=1)  # Assuming you want to return some other data as well
        
        if data:
            # Convert model instance to a dictionary
            data_dict = model_to_dict(data)
            fabric_list = list(fabric.values('id', 'name'))

            
            # Return the required data in JSON format
            return JsonResponse({
                'id': data_dict.get('id'),
                'name': data_dict.get('name'),
                'gray_gsm': data_dict.get('gray_gsm'),
                'fabric_id': data_dict.get('fabric_id'),
                'count_id': data_dict.get('count_id'),
                'gauge_id': data_dict.get('gauge_id'),
                'color_id': data_dict.get('color_id'),
                'dia_id': data_dict.get('dia_id'),
                'tex_id': data_dict.get('tex_id'),
                'is_active': data_dict.get('is_active'),
                'fabric': fabric_list 
            })
        else:
            return JsonResponse({'error': 'No matching fabric program found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)




from django.http import JsonResponse
from django.forms.models import model_to_dict
from .models import fabric_dia_table

# def fabric_prg_dia_edit(request):
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
#         fabric_prg_id = request.POST.get('id')
        
#         # Fetch all dia values for the given fabric_prg_id
#         data = fabric_dia_table.objects.filter(fabric_prg_id=fabric_prg_id).values_list('dia', flat=True)

#         if data:
#             return JsonResponse({
#                 'fabric_prg_id': fabric_prg_id,
#                 'dia_list': list(data),  # Convert QuerySet to list
#             })
#         else:
#             return JsonResponse({'error': 'No matching fabric program found'}, status=404)

#     return JsonResponse({'error': 'Invalid request'}, status=400)



from django.http import JsonResponse

def fabric_prg_dia_edit(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
        fabric_prg_id = request.POST.get('id')

        # Fetch all dia values for the given fabric_prg_id
        data = fabric_dia_table.objects.filter(fabric_prg_id=fabric_prg_id).values_list('dia', flat=True)

        return JsonResponse({
            'fabric_prg_id': fabric_prg_id,
            'dia_list': list(data) if data else [],  # Return empty list instead of error
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

# def fabric_prg_dia_edit(request):
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST": 
#         frm = request.POST
#         data = fabric_dia_table.objects.filter(fabric_prg_id=request.POST.get('id')).first()  # Get the first matching record
        
#         if data:
#             # Convert model instance to a dictionary
#             data_dict = model_to_dict(data)

            
#             # Return the required data in JSON format
#             return JsonResponse({
#                 'id': data_dict.get('id'),
#                 'dia': data_dict.get('dia'),
#                 'fabric_id': data_dict.get('fabric_prg_id'),
#                 'is_active': data_dict.get('is_active'),
#             })
#         else:
#             return JsonResponse({'error': 'No matching fabric program found'}, status=404)

#     return JsonResponse({'error': 'Invalid request'}, status=400)



def fabric_prg_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_prg_id = request.POST.get('id')
        fabric = request.POST.get('fabric')
        count = request.POST.get('count')
        name = request.POST.get('name')
        gauge = request.POST.get('gauge')
        tex = request.POST.get('tex') 
        gray_gsm = request.POST.get('gray_gsm')
        is_active = request.POST.get('is_active') 
        
        # 🔹 Ensure multiple colors are captured
        color_ids = request.POST.getlist('color_id')  
        
        color_id_str = ','.join(color_ids)  # Convert list to comma-separated string

        # dia = request.POST.get('dia')  
        dia_ids = request.POST.getlist('dia_id')  
        
        dia_id_str = ','.join(dia_ids)  # Convert list to comma-separated string

        try:
            fabric_prg = fabric_program_table.objects.get(id=fabric_prg_id)
            fabric_prg.fabric_id = fabric 
            fabric_prg.count_id = count
            fabric_prg.name = name
            fabric_prg.gauge_id = gauge
            fabric_prg.tex_id = tex
            fabric_prg.gray_gsm = gray_gsm
            fabric_prg.color_id = color_id_str  # Store as CSV string
            fabric_prg.dia_id = dia_id_str  # Store as CSV string
            fabric_prg.is_active = is_active
            fabric_prg.updated_by = user_id
            fabric_prg.updated_on = datetime.now()
            fabric_prg.save()

            return JsonResponse({'message': 'success'})

        except fabric_program_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Fabric Program not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def fabric_prg_update_bk_26(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_prg_id = request.POST.get('id')
        fabric = request.POST.get('fabric')
        count = request.POST.get('count')
        name = request.POST.get('name')
        gauge = request.POST.get('gauge')
        tex = request.POST.get('tex') 
        gray_gsm = request.POST.get('gray_gsm')
        is_active = request.POST.get('is_active') 
        # color_id = ','.join(request.POST.getlist('color_id'))  # Convert list to comma-separated string
        # print('color-id:',color_id)

        color_ids = request.POST.getlist('color_id[]')  # Get multiple selected values
        color_id_str = ','.join(color_ids)  # Convert list to comma-separated string



        dia = request.POST.get('dia')  

        
        try:
            fabric_prg = fabric_program_table.objects.get(id=fabric_prg_id)
            fabric_prg.fabric_id = fabric 
            fabric_prg.count_id=count
            fabric_prg.name=name
            fabric_prg.gauge_id=gauge
            fabric_prg.tex_id=tex
            fabric_prg.gray_gsm=gray_gsm
            fabric_prg.color_id = color_id_str
            fabric_prg.is_active = is_active
            fabric_prg.updated_by = user_id
            fabric_prg.updated_on = datetime.now()
            fabric_prg.save()
            return JsonResponse({'message': 'success'})
        

        except fabric_program_table.DoesNotExist:
 



            return JsonResponse({'message': 'error', 'error_message': 'fabric_prg not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})






def dia_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "product", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            fabric_dia_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except fabric_dia_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    





def fabric_prg_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "product", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            fabric_program_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except fabric_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    


# ````````````````````````` Tax `````````````````````````````````



def tax(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/tax.html')
    else:
        return HttpResponseRedirect("/signin")



def tax_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(tax_table.objects.filter(status=1).order_by('-id').values())
     
    formatted = [
        {
            'action': '<button type="button" onclick="tax_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="tax_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'display_name': item['display_name'] if item['display_name'] else'-', 
            'name': item['name'] if item['name'] else'-', 
            'hsn': item['hsn'] if item['hsn'] else'-', 
            'tax': item['tax'] if item['tax'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})


from django.db import IntegrityError


def tax_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        user_id = request.session.get('user_id')
        frm = request.POST
        name = frm.get('name')
        tax_value = frm.get('tax')
        display_name= frm.get('display_name')
        hsn = frm.get('hsn')

        try:
            tax_value = float(tax_value)
        except (TypeError, ValueError):
            return JsonResponse({"message": "error", "error_message": "Invalid tax value"}, status=400)


        
        if tax_table.objects.filter(name__iexact=name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Tax with this name already exists.'
            }, status=400)



         # Check for existing active record with same name
        # existing_active = tax_table.objects.filter(name__iexact=name,tax__iexact=tax_value,hsn__iexact=hsn, status=1).exists()
        # if existing_active:
        #     return JsonResponse({'message': 'error', 'error_message': 'Tax with this name already exists.'}, status=400)

        try:
            tax_instance = tax_table()
            tax_instance.tax = tax_value
            tax_instance.display_name = display_name
            tax_instance.name = name
            tax_instance.hsn = hsn
            tax_instance.created_on = datetime.now()
            tax_instance.created_by = user_id
            tax_instance.updated_on = datetime.now()
            tax_instance.updated_by = user_id
            tax_instance.save()

            return JsonResponse({"data": "Success"})

        except IntegrityError as e:
            return JsonResponse({
                "message": "error",
                "error_message": f"Duplicate entry for tax name '{name}'. Please use a unique name."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "message": "error",
                "error_message": f"An unexpected error occurred: {str(e)}"
            }, status=500)

    return JsonResponse({"message": "error", "error_message": "Invalid request"}, status=400)




def tax_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = tax_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


from django.db import IntegrityError

def tax_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        tax_id = request.POST.get('id')
        tax_value = request.POST.get('tax')
        name = request.POST.get('name')
        display_name = request.POST.get('display_name')
        hsn = request.POST.get('hsn')
        is_active = request.POST.get('is_active')

        try:
            tax = tax_table.objects.get(id=tax_id)
            tax.tax = tax_value
            tax.display_name = display_name
            tax.name = name
            tax.hsn = hsn
            tax.is_active = is_active
            tax.updated_by = user_id
            tax.updated_on = datetime.now()
            tax.save()
            return JsonResponse({'message': 'success'})

        except tax_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Tax record not found.'}, status=404)

        except IntegrityError:
            return JsonResponse({
                'message': 'error',
                'error_message': f"Duplicate entry for tax name '{name}'. Please add a unique name."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'message': 'error',
                'error_message': f"Unexpected error: {str(e)}"
            }, status=500)

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)




def tax_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            tax_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except tax_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




# ````````````````````````` Item Group `````````````````````````````````



def item_group(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'master/item_group.html')
    else:
        return HttpResponseRedirect("/signin")



def item_group_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(item_group_table.objects.filter(status=1).order_by('-id').values())
     
    formatted = [
        {
            'action': '<button type="button" onclick="item_group_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="item_group_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def item_group_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        user_id = request.session.get('user_id')
        frm = request.POST
        name = frm.get('name')
  
    
        
        if item_group_table.objects.filter(name__iexact=name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'item_group with this name already exists.'
            }, status=400)

        try:
            item_group_instance = item_group_table()
            item_group_instance.name = name
            item_group_instance.created_on = datetime.now() 
            item_group_instance.created_by = user_id
            item_group_instance.updated_on = datetime.now()
            item_group_instance.updated_by = user_id
            item_group_instance.save()

            return JsonResponse({"data": "Success"})

        except IntegrityError as e:
            return JsonResponse({
                "message": "error",
                "error_message": f"Duplicate entry for item_group name '{name}'. Please use a unique name."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "message": "error",
                "error_message": f"An unexpected error occurred: {str(e)}"
            }, status=500)

    return JsonResponse({"message": "error", "error_message": "Invalid request"}, status=400)




def item_group_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = item_group_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])




def item_group_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        item_group_id = request.POST.get('id')
        name = request.POST.get('name')
      
        is_active = request.POST.get('is_active')

        try:
            item_group = item_group_table.objects.get(id=item_group_id)
     
            item_group.name = name
            item_group.is_active = is_active
            item_group.updated_by = user_id
            item_group.updated_on = datetime.now()
            item_group.save()
            return JsonResponse({'message': 'success'})

        except item_group_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'item_group record not found.'}, status=404)

        except IntegrityError:
            return JsonResponse({
                'message': 'error',
                'error_message': f"Duplicate entry for item_group name '{name}'. Please add a unique name."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'message': 'error',
                'error_message': f"Unexpected error: {str(e)}"
            }, status=500)

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)




def item_group_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            item_group_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except item_group_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



# ````````````````````````````````````` ITEM ```````````````````````````````````````````````



def mx_item(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        print('user-id:',user_id)
        item_group = item_group_table.objects.filter(status=1)
        print('mx-data:',item_group) 
        return render(request,'master/master_item.html',{'item_group':item_group}) 
    else:
        return HttpResponseRedirect("/signin") 

 
 
def item_list(request): 
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(mx_item_table.objects.filter(status=1).order_by('-id').values())
     
    formatted = [
        {
            'action': '<button type="button" onclick="item_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="item_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            'name': item['name'] if item['name'] else'-', 
            'hsn_code': item['hsn_code'] if item['hsn_code'] else'-', 
            'item_group': getItemNameById(item_group_table, item['item_group_id']),
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        }  
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})





def item_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        user_id = request.session.get('user_id')
        frm = request.POST
        name = frm.get('name')
        hsn_code = frm.get('hsn_code')
        item_group_id = frm.get('item_group_id')

        
        if mx_item_table.objects.filter(name__iexact=name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'item with this name already exists.'
            }, status=400)

        try:
            item_instance = mx_item_table()
            item_instance.name = name
            item_instance.item_group_id= item_group_id
            item_instance.hsn_code = hsn_code
            item_instance.created_on = datetime.now()
            item_instance.created_by = user_id
            item_instance.updated_on = datetime.now()
            item_instance.updated_by = user_id
            item_instance.save()

            return JsonResponse({"data": "Success"})

        except IntegrityError as e:
            return JsonResponse({
                "message": "error",
                "error_message": f"Duplicate entry for item name '{name}'. Please use a unique name."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "message": "error",
                "error_message": f"An unexpected error occurred: {str(e)}"
            }, status=500)

    return JsonResponse({"message": "error", "error_message": "Invalid request"}, status=400)




def item_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = mx_item_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def item_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        item_id = request.POST.get('id')
        name = request.POST.get('name')
        item_group_id = request.POST.get('item_group_id')
        hsn_code = request.POST.get('hsn_code')
        

        is_active = request.POST.get('is_active') 

        try:
            item = mx_item_table.objects.get(id=item_id)
     
            item.name = name
            item.item_group_id=item_group_id
            item.hsn_code=hsn_code
            item.is_active = is_active
            item.updated_by = user_id
            item.updated_on = datetime.now()
            item.save()
            return JsonResponse({'message': 'success'})

        except mx_item_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'item record not found.'}, status=404)

        except IntegrityError:
            return JsonResponse({
                'message': 'error',
                'error_message': f"Duplicate entry for item name '{name}'. Please add a unique name."
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'message': 'error',
                'error_message': f"Unexpected error: {str(e)}"
            }, status=500)

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)




def item_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting
            mx_item_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except mx_item_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'}) 



# ````````````````````````` product `````````````````````````````````



def product(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        uom = uom_table.objects.filter(status=1)
        return render(request,'master/product.html',{'uom':uom})
    else:
        return HttpResponseRedirect("/signin")



def product_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(product_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="product_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="product_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'uom_id':getUOMName(uom_table,item['uom_id']),
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def getUOMName(tbl, uom_id):
    try:
        UOM = tbl.objects.get(id=uom_id).name
    except ObjectDoesNotExist:
        UOM = "-"  # Handle the error by providing a default value or appropriate message
    return UOM



def product_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('name')
        uom = frm.get('uom_id')
        product = product_table()
        product.name=uname
        product.uom_id=uom
        product.created_on=datetime.now()
        product.created_by=user_id
        product.updated_on=datetime.now()
        product.updated_by=user_id
        product.save()
        res = "Success"
        return JsonResponse({"data": res})




def product_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = product_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def product_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        product_id = request.POST.get('id')
        name = request.POST.get('name')
        uom = request.POST.get('uom_id')
        is_active = request.POST.get('is_active')
        
        try:
            product = product_table.objects.get(id=product_id)
            product.name = name
            product.uom_id = uom
            product.is_active = is_active
            product.updated_by = user_id
            product.updated_on = datetime.now()
            product.save()
            return JsonResponse({'message': 'success'})
        except product_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'product not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def product_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "product", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            product_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except product_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



# ``````````````````````````` Employee`````````````````````````````````````````````````








from datetime import datetime

def get_financial_year(date=None):
    """Returns the financial year in the format '24-25' based on a given date or today."""
    if date is None:
        date = datetime.today()  # Use today's date if no argument is provided

    if isinstance(date, str):  # Convert string date to datetime
        date = datetime.strptime(date, "%Y-%m-%d")

    if date.month >= 4:
        start_year = date.year
        end_year = date.year + 1
    else:
        start_year = date.year - 1
        end_year = date.year

    return f"{str(start_year)[-2:]}-{str(end_year)[-2:]}"  # Example: '24-25'



# ```````````` TASK ````````````````````````````````````````````````



def task_library(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        # if user_type == 'Staff' or user_type == 'Admin' :
        return render(request, 'task/task_library.html')   
        # else:
        #     return HttpResponseRedirect('/signin')    
    else:
        return HttpResponseRedirect("/signin")




def library_add(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)
  
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
        user_id = request.session.get('user_id') 
        frm = request.POST
        name = frm.get('name')
        code = frm.get('code')
        description = frm.get('description')

        task = task_library_table()
        task.name = name
        task.task_code = code
        task.description = description
        task.created_by = user_id  
        task.updated_by = user_id
        task.created_on = timezone.now() 
        task.save()

        # Send success response
        return JsonResponse({'data': 'Success'}, status=200)
    
    # Handle non-AJAX requests or invalid methods
    return JsonResponse({'data': 'Invalid request'}, status=400)





def library_report(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(task_library_table.objects.filter(status=1).values()) 
    formatted = [
        {
            'id': index + 1, 
            'action':  '<button type="button" onclick="library_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button>'.format(item['id']) + \
                      '<button type="button" onclick="library_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id']) ,
            'name': item['name'] if item['name'] else '-',
            'code': item['task_code'] if item['task_code'] else '-',
            'remarks': '<button type="button" onclick="remarks_page(\'{}\')" class="btn btn-secondary btn-xs">Remarks</button>'.format(item['id']),
            'description': item['description'] if item['description'] else '-',
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
        }
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})



def library_edit(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
         frm = request.POST
    data = task_library_table.objects.filter(id=request.POST.get('id'))    
    return JsonResponse(data.values()[0])


def library_update(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
        user_id = request.session.get('user_id')
        edit_id = request.POST.get('id')
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active')
        
        try:
            task = task_library_table.objects.get(id=edit_id)
            task.name = name
            task.task_code = code
            task.description = description
            task.is_active = is_active
            task.updated_by = user_id
            task.updated_on = timezone.now()
            task.save()
            return JsonResponse({'message': 'success'})
        except task_library_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'UOM not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def library_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            task_library_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except task_library_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})





# `````````````````````````````` REMARKS ````````````````````````````````````````


def remarks_page(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        # if user_type == 'Staff' or user_type == 'Admin' :
        encoded_id = request.GET.get('id', None)
        if encoded_id:
            plan_id = request.GET.get('id')
            decoded_id = base64.b64decode(encoded_id).decode('utf-8')
            task = task_library_table.objects.filter(id=decoded_id).first()
            task_name = task.name
        
            return render(request, 'task/task_remarks.html', {'id': decoded_id,'task_name':task_name})
        else:
            return HttpResponse("ID parameter is missing")  
        # else:
        #     return HttpResponseRedirect('/signin')     
    else:
        return HttpResponseRedirect("/signin")




def remarks_add(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
        user_id = request.session.get('user_id')  # Access user_id from session
        frm = request.POST
        task = frm.get('task_id')
        description = frm.get('description')

        remarks = remarks_table()
        remarks.task_library_id = task
        remarks.description = description
        remarks.created_by = user_id  
        remarks.updated_by = user_id
        remarks.created_on = timezone.now() 
        remarks.save()

        # Send success response
        return JsonResponse({'data': 'Success'}, status=200)
    
    # Handle non-AJAX requests or invalid methods
    return JsonResponse({'data': 'Invalid request'}, status=400)
 




def remarks_report(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    task_id = request.POST.get('task')
    data = list(remarks_table.objects.filter(task_library_id=task_id,status=1).values()) 
    formatted = [
        {
            'id': index + 1,
            'action':  '<button type="button" onclick="remarks_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button>'.format(item['id']) + \
                      '<button type="button" onclick="remarks_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id']) ,
            'description': item['description'] if item['description'] else '-',
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
        }
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})



def remarks_edit(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
         frm = request.POST
    data = remarks_table.objects.filter(id=request.POST.get('id'))    
    return JsonResponse(data.values()[0])


def remarks_update(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
        user_id = request.session.get('user_id')
        edit_id = request.POST.get('id')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active')
        
        try:
            remarks = remarks_table.objects.get(id=edit_id)
            remarks.description = description
            remarks.is_active = is_active
            remarks.updated_by = user_id
            remarks.updated_on = timezone.now()
            remarks.save()
            return JsonResponse({'message': 'success'})
        except remarks_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'UOM not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def remarks_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            remarks_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except remarks_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    



def task(request):
    if 'user_id' in request.session: 
        user_type = request.session.get('user_type')
        user_type = request.session.get('user_type')
        # if user_type == 'Staff' or user_type == 'Admin' :
        library = task_library_table.objects.filter(status=1)
        employee = employee_table.objects.filter(status=1)
        customer = party_table.objects.filter(status=1)
        return render(request, 'task/task.html',{'library':library,'employee':employee,'customer':customer})      
        # else:
        #     return HttpResponseRedirect('/signin') 
    else:
        return HttpResponseRedirect("/signin") 


def get_remarks_list(request):
    """
    Handles the AJAX request to fetch remarks for a specific task library.
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        task_library_id = request.GET.get('task_library_id')

        if not task_library_id:
            return JsonResponse({'error': 'Task library ID is required'}, status=400)

        # Fetch the task library
        task_library = get_object_or_404(task_library_table, id=task_library_id)

        # Fetch remarks associated with the task library
        remarks = remarks_table.objects.filter(task_library_id=task_library.id).values('id', 'description')

        # Convert QuerySet to a list of dictionaries
        remarks_list = list(remarks)

        return JsonResponse({'remarks': remarks_list}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)




def task_add(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
        try:
            user_id = request.session.get('user_id')  # Access user_id from session
            frm = request.POST
            library = frm.get('library')
            agent = frm.get('employee')  # Ensure conversion to integer
            name = frm.get('name')
            priority = frm.get('priority')
            status = frm.get('status')
            print(status)
            start = frm.get('start') 
            followup = frm.get('followup') 
            description = frm.get('description')
            followup_status = frm.get('followup_status')

            start_date = timezone.datetime.strptime(start, '%Y-%m-%d') if start else None
            followup_date = timezone.datetime.strptime(followup, '%Y-%m-%d') if followup else None
            print('followup_date',followup_date)

            # Create and save the task
            task = task_table(
                name=name,
                task_library_id=library,
                employee_id=agent,
                priority=priority,
                task_date=start_date,
                total_count=1,  
                task_status = 'Pending',
                created_by=user_id,
                updated_by=user_id,
                created_on=timezone.now(),
                updated_on=timezone.now()
            )
            task.save()

            # Create and save the followup
            followup_entry = followup_table(
                task_id=task.id,  
                followup_date=followup_date, 
                followup_status=followup_status,
                remarks=description,
                followed_by='-',  # If this is a placeholder, ensure it's intentional
                created_by=user_id,
                updated_by=user_id,
                created_on=timezone.now(),  
                updated_on=timezone.now()
            )
            followup_entry.save()

            # Update task with the total count of follow-ups
            total_followups = followup_table.objects.filter(task_id=task.id).count()
            task.total_count = total_followups
            task.save()

            # Send success response
            return JsonResponse({'data': 'Success'}, status=200)

        except Exception as e:
            # Handle any unexpected errors
            return JsonResponse({'data': f'Error: {str(e)}'}, status=400)
    
    # Handle non-AJAX requests or invalid methods
    return JsonResponse({'data': 'Invalid request'}, status=400)





def task_report(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(task_table.objects.filter(status=1).values()) 
    agents = {agent.id: agent.name for agent in employee_table.objects.filter(is_active=1)} 
    library = {task.id: task.name for task in task_library_table.objects.filter(status=1)} 

    def get_task_badge(status): 
        status_badges = {
            'Pending': '<span class="badge bg-primary">Pending</span>',
            'Hold': '<span class="badge bg-info">Hold</span>',
            'In Progress': '<span class="badge bg-warning">In Progress</span>',
            'Completed': '<span class="badge bg-success">Completed</span>',
        }
        return status_badges.get(status, '<span class="badge bg-secondary">Unknown</span>') 

    formatted = [ 
        {
            'id': index + 1,
            'action':  '<button type="button" onclick="task_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button>'.format(item['id']) + \
                       '<button type="button" onclick="task_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id']) + \
                       '<button type="button" onclick="task_followup(\'{}\')" class="btn btn-secondary btn-xs me-0">Followup</button>'.format(item['id']),
            'name': item['name'] if item['name'] else '-',
            'library':getlibraryNameById(task_library_table, item['task_library_id']), #library.get(item['task_library_id'], '-') if item['task_library_id'] else '-',  # Corrected lookup for library
            'agent': agents.get(item['employee_id'], '-') if item['employee_id'] else '-',  # Get agent name using agent_id
            'priority': item['priority'] if item['priority'] else '-',
            'status': get_task_badge(item.get('task_status', 'Unknown')),  # Corrected task_status lookup
        }
        for index, item in enumerate(data)
    ] 
    
    return JsonResponse({'data': formatted})

def getlibraryNameById(tbl, task_library_id): 
    try:
        category = tbl.objects.get(id=task_library_id).name
    except ObjectDoesNotExist:
        category = "-"  # Handle the error by providing a default value or appropriate message
    return category



def task_edit(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        enquiry_id = request.POST.get('id')
        print('enquiry_id',enquiry_id)
        
        enquiry = get_object_or_404(task_table, id=enquiry_id)
        print('enquiry',enquiry)
        
        followup = followup_table.objects.filter(task_id=enquiry_id).first()
        
        data = {
            'id': enquiry.id,
            'task_library': enquiry.task_library_id,
            'employee_id': enquiry.employee_id,
            'name': enquiry.name,
            'priority': enquiry.priority,
            'start_date': enquiry.task_date.strftime('%d-%m-%Y'), 
            'followup_date': followup.followup_date.strftime('%d-%m-%Y') if followup and followup.followup_date else '-',
            'descriptions': followup.remarks if followup else None,
            'followup_status': followup.followup_status if followup.followup_status else '',
            'is_active': enquiry.is_active,
            'task_status':enquiry.task_status
        }
        print(data)
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'})


def task_update(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        edit_id = request.POST.get('id')
        task = get_object_or_404(task_table, id=edit_id)       
        user_id = request.session.get('user_id')

        library = request.POST.get('library')
        agent = request.POST.get('agent')
        name = request.POST.get('name')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        start = request.POST.get('start')
        followup_date = request.POST.get('followup')  # Change this variable name for clarity
        desc = request.POST.get('description')
        is_active = request.POST.get('is_active')

        # Update task details
        task.name = name
        task.task_library_id = library
        task.employee_id = agent
        task.priority = priority
        task.task_status = status
        task.task_date = start
        task.is_active = is_active
        
        task.updated_on = timezone.now()
        task.updated_by = user_id
        task.save()
        
        # Get or create the followup entry
        followup, created = followup_table.objects.get_or_create(task_id=edit_id).first()

        # Update followup details
        followup.followup_date = followup_date  # Correct assignment of the followup date
        followup.followup_status = status
        followup.remarks = desc
        followup.updated_on = timezone.now()
        followup.updated_by = user_id
        
        followup.save()
        
        # Update total follow-ups count in the task
        total_followups = followup_table.objects.filter(task_id=task.id).count()
        task.total_count = total_followups
        task.save()
        
        return JsonResponse({"data": "Success"})
    else:
        return JsonResponse({"data": "Failed"})



def task_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            task_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except task_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




def task_followup(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  

        enquiry_id = request.POST.get('id')
        
        enquiry = get_object_or_404(task_table, id=enquiry_id)

        followup = followup_table.objects.filter(task_id=enquiry_id).first()
        followup = followup_table.objects.filter(task_id=enquiry_id).order_by('-followup_date').first()

        data = {
            'id': enquiry.id,
            'task_library': enquiry.task_library_id,
            'agent': enquiry.employee_id,
            'name': enquiry.name,
            'count': enquiry.total_count,
            'priority': enquiry.priority,
            'start_date': enquiry.task_date.strftime('%d-%m-%y'), 
            'followup_date': followup.followup_date.strftime('%d-%m-%Y'),  
            'descriptions': followup.remarks if followup else None,
            'followup_status': followup.followup_status,
            'is_active': enquiry.is_active,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'})




def followup_add(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Task", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":  
        user_id = request.session.get('user_id')

        task = request.POST.get('task_id')
        status = request.POST.get('followup_status')
        date = request.POST.get('task_followup')
        print(date)
        desc = request.POST.get('task_description')


        follow = followup_table()
        follow.task_id = task  
        follow.followup_date = date  
        follow.followup_status = status  
        follow.remarks = desc  
        follow.created_on = timezone.now()
        follow.created_by = user_id
        follow.updated_on = timezone.now()
        follow.updated_by = user_id
        follow.save()

        enquiry = get_object_or_404(task_table, id=task)
        enquiry.total_count = followup_table.objects.filter(task_id=task).count()
        enquiry.updated_on = timezone.now()
        enquiry.updated_by = user_id
        enquiry.save()

        res = "Success"
        return JsonResponse({"data": res})
    else:
        return JsonResponse({"data": "Failed"})




def followup_report(request):
    historiy_id = request.POST.get('history')
    print('historiy_id:', historiy_id) 

    # Fetch agent_id from the task_table
    enquiries = task_table.objects.filter(id=historiy_id, status=1).values('employee_id', 'task_library_id', 'task_date').order_by('-id')
    print('enquiries:', enquiries)

    formatted = []

    if enquiries.exists():
        enquiry = enquiries.first()
        agent_id = enquiry['employee_id']
        print('agent',agent_id)
        task_library_id = enquiry['task_library_id']
        task_date = enquiry['task_date']


        agent = employee_table.objects.filter(id=agent_id).first()
        agent_name = agent.name if agent else '-'
        
        # Fetch the task library name using task_library_id
        task_library = task_library_table.objects.filter(id=task_library_id).first()
        task_library_name = task_library.name if task_library else '-'

        # Fetch all followups related to the current task
        followups = followup_table.objects.filter(task_id=historiy_id).order_by('-followup_date')

        # Format the followups data for response
        for followup in followups:
            formatted.append({
                'date': task_date.strftime('%d-%m-%Y') if task_date else '-',  # Format task date
                'followup': followup.followup_date.strftime('%d-%m-%Y') if followup.followup_date else '-',  # Format follow-up date
                'name': agent_name,  # Agent name
                'library': task_library_name,  # Task library name
                'status': followup.followup_status if followup.followup_status else '-',  # Display follow-up status
                'followed': followup.followed_by if followup.followed_by else '-',  # Display who followed up
                'remarks': followup.remarks if followup.remarks else '-',  # Display follow-up descriptions
            })
    else:
        # Handle case where no enquiries were found
        return JsonResponse({'data': 'No enquiries found'}, status=404) 

    return JsonResponse({'data': formatted})
 

# ``````````````````````````` settings ``````````````````````````````````````` 




def email_settings_page(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        company_id = request.session['company_id'] 
        print('email-company:',company_id)
        email = email_settings_table.objects.filter(status=1,company_id=company_id)
        sms = sms_table.objects.filter(status=1,company_id=company_id)
        process = process_table.objects.filter(status=1)
        return render(request,'settings/email_settings.html',{'email':email,'sms':sms,'process':process})
    else:
        return HttpResponseRedirect("/signin")
    


def add_email_settings(request): 
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        email = frm.get('default_email')
        port = frm.get('email_port')
        host_user = frm.get('email_host_user')
        host = frm.get('email_host')
        password = frm.get('email_password')
        des = frm.get('description')
        settings = email_settings_table()
        settings.default_email=email
        settings.email_port=port
        settings.email_host_user=host_user
        settings.email_password=password
        settings.email_host=host
        settings.description = des

        settings.created_on=datetime.now()
        settings.created_by=user_id
        # settings.updated_on=datetime.now()
        # settings.updated_by=user_id
        settings.save()
        res = "Success"
        return JsonResponse({"data": res})




def email_list(request): 
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access: 
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(email_settings_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="email_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="email_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'default_email': item['default_email'] if item['default_email'] else'-', 
            'email_host': item['email_host'] if item['email_host'] else'-',  
            'email_host_user': item['email_host_user'] if item['email_host_user'] else'-', 
            'email_password': item['email_password'] if item['email_password'] else'-',  
            'email_port': item['email_port'] if item['email_port'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})

 
def email_edit(request): 
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = email_settings_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


# ````````````````````` sms `````````````````````````````````````````





def update_sms(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        edit_id = request.POST.get('edit_id')
        sms_api = request.POST.get('sms_api_key')
        support_number = request.POST.get('support_number')
        is_active = request.POST.get('is_active')
        des = request.POST.get('description')
        try:
            sms = sms_table.objects.get(id=edit_id) 
            sms.sms_api_key = sms_api
            sms.support_number=support_number
            sms.description = des
            sms.is_active = is_active
            sms.updated_by = user_id
            sms.updated_on = datetime.now()
            sms.save()
            return JsonResponse({'message': 'success'})
        except sms_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'sms not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})
    




def knitting(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1) 
        product = fabric_program_table.objects.filter(status=1)
        return render(request,'knitting/knitting_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import fabric_program_table, count_table, gauge_table, tex_table, fabric_dia_table

# @csrf_exempt  # Use this only if necessary
# def get_fabric_lists(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')

#         if not product_id:
#             return JsonResponse({'error': 'Product ID is required'}, status=400)

#         try:
#             # Retrieve the fabric program
#             fabric_program = get_object_or_404(fabric_program_table, id=product_id)

#             # Fetch related data
#             count = get_object_or_404(count_table, id=fabric_program.count_id)
#             gauge = get_object_or_404(gauge_table, id=fabric_program.gauge_id)
#             dia = get_object_or_404(dia_table, id=fabric_program.dia_id)
#             tex = get_object_or_404(tex_table, id=fabric_program.tex_id)

#             # Fetch all dia values related to the fabric program
#             # dia_list = list(fabric_dia_table.objects.filter(fabric_prg_id=fabric_program.id,status=1).values('id', 'dia'))

#             response_data = {
#                 'count': {'id': count.id, 'count': count.name},
#                 'dia': {'id': dia.id, 'dia': dia.name},
#                 # 'dia': dia_list,  # Return a list of dia objects
#                 'gauge': {'id': gauge.id, 'name': gauge.name},
#                 'tex': {'id': tex.id, 'name': tex.name},
#                 'gsm': {'id': fabric_program.id, 'gray_gsm': fabric_program.gray_gsm}
#             }

#             return JsonResponse(response_data)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@csrf_exempt  # Use only if required
def get_fabric_lists(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)

        try:
            # Retrieve the fabric program
            fabric_program = get_object_or_404(fabric_program_table, id=product_id)

            # Fetch related data
            count = get_object_or_404(count_table, id=fabric_program.count_id)
            gauge = get_object_or_404(gauge_table, id=fabric_program.gauge_id)
            tex = get_object_or_404(tex_table, id=fabric_program.tex_id)

            # Handle multiple dia IDs
            dia_ids = [int(d) for d in str(fabric_program.dia_id).split(',') if d.isdigit()]
            dia_list = list(dia_table.objects.filter(id__in=dia_ids).values('id', 'name'))

            response_data = {
                'count': {'id': count.id, 'count': count.name},
                'dia': dia_list,  # Return list of dia objects
                'gauge': {'id': gauge.id, 'name': gauge.name},
                'tex': {'id': tex.id, 'name': tex.name},
                'gsm': {'id': fabric_program.id, 'gray_gsm': fabric_program.gray_gsm}
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



# @csrf_exempt  # Use this only if necessary
# def get_fabric_lists(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')

#         if not product_id:
#             return JsonResponse({'error': 'Product ID is required'}, status=400)

#         try:
#             # Retrieve the fabric program
#             fabric_program = get_object_or_404(fabric_program_table, id=product_id)

#             # Fetch related data
#             count = get_object_or_404(count_table, id=fabric_program.count_id)
#             gauge = get_object_or_404(gauge_table, id=fabric_program.gauge_id)
#             tex = get_object_or_404(tex_table, id=fabric_program.tex_id)
#             dia = get_object_or_404(fabric_dia_table, fabric_prg_id=fabric_program.id)

#             response_data = {
#                 'count': {'id': count.id, 'count': count.name},
#                 'dia': {'id': dia.id, 'dia': dia.dia},
#                 'gauge': {'id': gauge.id, 'name': gauge.name},
#                 'tex': {'id': tex.id, 'name': tex.name},
#                 'gsm': {'id': fabric_program.id, 'gray_gsm': fabric_program.gray_gsm}
#             }

#             return JsonResponse(response_data)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)





@csrf_exempt  # Use this only if necessary
def get_bag_wt(request):
    if request.method == 'POST':
        bag = request.POST.get('bag')

        if not bag:
            return JsonResponse({'error': 'Product ID is required'}, status=400)

        try:
            # Retrieve the fabric program
            bag = get_object_or_404(bag_table, id=bag)

            # Fetch related data
           
            response_data = {
                'bag': {'id': bag.id, 'wt': bag.wt}
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def knitting_program_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access: 
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})
 
    data = list(knitting_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="knitting_edit(\'{}\' )" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                       <button type="button" onclick="knitting_delete(\'{}\' )" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(str(item['id']), str(item['id'])),

            # 'action': '<button type="button" onclick="knitting_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
            #           <button type="button" onclick="knitting_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            'prg_date': item['program_date'].strftime('%d-%m-%Y') if isinstance(item.get('program_date'), date) else '-',
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            'total_tax': item['total_tax'] if item['total_tax'] else'-', 
            'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            # 'supplier_id':getSupplier(party_table, item['knitting_id'] ), 
            'lot_no': item['lot_no'] if item['lot_no'] else'-', 
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

 

# ```````````````````````PROGRAM ````````````````````````````````````````````



def knitting_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1, is_knitting=1)
        product = fabric_program_table.objects.filter(status=1)
        purchase = parent_po_table.objects.filter(status=1, is_knitting_prg=0) 

        last_purchase = knitting_table.objects.order_by('-id').first()
        delivery_number = last_purchase.id + 1 if last_purchase else 1

        last_series = knitting_table.objects.order_by('-id').first()
        lot_no = last_series.lot_no + 1 if last_series else 1

        gauge = gauge_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)

        fabric_program_qs = fabric_program_table.objects.filter(status=1)

        # Build fabric_program list with resolved fabric_name from fabric_table
        fabric_program_with_name = []
        # for fp in fabric_program_qs:
        #     try:
        #         fabric_item = fabric_table.objects.get(id=fp.fabric_id)
        #         print(f"Found fabric: id={fp.fabric_id}, name={fabric_item.name}")  # Debug
        #         fabric_program_with_name.append({
        #             'id': fp.id,
        #             'name': fp.name,
        #             'fabric_id': fp.fabric_id,
        #             'fabric_name': fabric_item.name  # make sure 'name' exists in fabric_table
        #         })
        #     except fabric_table.DoesNotExist:
        #         print(f"fabric_id {fp.fabric_id} not found in fabric_table")  # Debug
        #         fabric_program_with_name.append({
        #             'id': fp.id,
        #             'name': fp.name,
        #             'fabric_id': fp.fabric_id,
        #             'fabric_name': 'N/A'
        #         })


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


        return render(request, 'knitting/knitting.html', {
            'purchase': purchase,
            'supplier': supplier,
            'fabric_programs': fabric_program_with_name,
            'lot_no': lot_no,
            'party': party,
            'product': product,
            'delivery_number': delivery_number,
            'gauge': gauge, 
            'count': count,
            'tex': tex
        })
    else:
        return HttpResponseRedirect("/signin")



def knitting_program_test0305(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1,is_knitting=1)
        product = fabric_program_table.objects.filter(status=1)
        purchase = parent_po_table.objects.filter(status=1,is_knitting_prg=0) 

        last_purchase = knitting_table.objects.order_by('-id').first()
        if last_purchase:
            delivery_number = last_purchase.id + 1 
        else: 
            delivery_number = 1  # Default if no records exist

        last_series = knitting_table.objects.order_by('-id').first()
        if last_series:
            lot_no = last_series.lot_no + 1 
        else:   
            lot_no = 1  # Default if no records exist
        # lot_no = 1002

        gauge = gauge_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        tex = tex_table.objects.filter(status=1)
        # fabric_program = fabric_program_table.objects.filter(status=1)


        fabric_program = fabric_program_table.objects.filter(status=1)

        # Create a list with fabric name from item_table
        fabric_program_with_name = []
        for fp in fabric_program:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_name': fabric_item.name
                })
            except fabric_table.DoesNotExist:
                fabric_program_with_name.append({
                    'id': fp.id, 
                    'name': fp.name,
                    'fabric_name': 'N/A'
                })

        print('fab-name:',fabric_program_with_name)
         
        # if fabric_program:
        #     fab = fabric_program.fabric_id
        return render(request,'knitting/knitting.html',{'purchase':purchase,'supplier':supplier,'fabric_program':fabric_program,'lot_no':lot_no,
                                                        'fabric_program': fabric_program_with_name,'party':party,'product':product,'delivery_number':delivery_number,'gauge':gauge,'count':count,'tex':tex})
    else:
        return HttpResponseRedirect("/signin")


  
from django.http import JsonResponse
from datetime import datetime
import json
from decimal import Decimal

@csrf_exempt
def add_knitting(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            # Extracting data from request
            prg_date = request.POST.get('program_date') 
            name = request.POST.get('name') 
            print('prg-date:',prg_date)
            supplier_id = request.POST.get('supplier_id') 
            lot_no = request.POST.get('lot_no')
            print('lot:',lot_no)
            po_id = request.POST.get('po_id',0)
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            print('k-data:',chemical_data)
            # Create knitting_table entry (Parent)
            material_request = knitting_table.objects.create(
                lot_no=0,
                name = name,
                program_date=prg_date, 
                knitting_id=supplier_id,
                company_id=company_id, 
                po_id=po_id if po_id else 0, 
                total_quantity=request.POST.get('total_quantity') or 0,
                total_amount=request.POST.get('sub_total') or 0,
                round_off=request.POST.get('round_off') or 0,
                total_tax=request.POST.get('tax_total') or 0, 
                grand_total=request.POST.get('total_payable') or 0,
                created_by=user_id,
                # created_on=datetime.now() 
            )

          
            for chemical in chemical_data:
                if chemical and chemical.get('product_id') and chemical.get('quantity') not in [None, 'undefined']:
                    try:
                        quantity = int(float(chemical.get('quantity', 0)))  # Ensure proper conversion
                        total_amount = Decimal(chemical.get('total_amount') or 0)
                        
                        # Debug print to check values
                        print(f"Creating sub_knitting_table entry with: product_id={chemical.get('product_id')}, quantity={quantity}, total_amount={total_amount}")
                        tm_po = chemical.get('tm_po_id', 0)
                        sub_knitting_table.objects.create(
                            tm_id=material_request.id,
                            tm_po_id= 0,
                            tx_id =0,
                            fabric_id=chemical.get('product_id'),  
                            count=chemical.get('count_id'), 
                            gauge=chemical.get('gauge_id'), 
                            tex=chemical.get('tex_id'), 
                            dia=chemical.get('dia'),
                            gsm=chemical.get('gsm'),  
                            rolls=chemical.get('rolls'),
                            wt_per_roll=chemical.get('wt_per_roll'),
                            rate=chemical.get('rate'),
                            quantity=quantity,
                            total_amount=total_amount,
                            created_by=user_id,
                            created_on=datetime.now(),
                            updated_by=user_id,
                            updated_on=datetime.now()
                        )

                    except ValueError as ve:
                        print(f"Invalid data for product {chemical.get('product_id')}: {ve}")
                else:
                    print("Invalid entry found:", chemical)

  


            # ✅ Update `is_knitting_prg=1` where `po_id` matches
            parent_po_table.objects.filter(id=po_id).update(is_knitting_prg=1)

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
                    count=count,
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
        if not parent_stock_instance:
            return render(request, 'knitting/update_knitting_program.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"
        if parent_stock_instance.knitting_id:
            try:
                supplier = party_table.objects.get(id=parent_stock_instance.knitting_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"
        # inward_no = "-"
    

        # Fetch active products and UOM
        product = fabric_program_table.objects.filter(status=1)
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(is_knitting=1,status=1)

        count=count_table.objects.filter(status=1)
        gauge=gauge_table.objects.filter(status=1)
        tex=tex_table.objects.filter(status=1)
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
        }
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
                            'fabric_id': getItemNameById(fabric_program_table, item['fabric_id']),
                            'count': getCountNameById(count_table, item['count']),
                            'gauge': getItemNameById(gauge_table, item['gauge']),
                            'tex': getItemNameById(tex_table, item['tex']),
                            'dia': item['dia'] or '-',
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


from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse

from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse

def knitting_prg_lists(request):
    if request.method == 'POST':
        master_id = request.POST.get('prg_id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data without using select_related on non-ForeignKey fields
                child_data = sub_knitting_table.objects.filter(tm_id=master_id, status=1, is_active=1)

                # Check if there's any child data
                if child_data.exists():
                    # Aggregate child data totals
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch parent data with related fields for tax and round_off
                    parent_data = knitting_table.objects.filter(id=master_id).first()
                    if parent_data:
                        total_tax = Decimal(parent_data.total_tax or 0)
                        try:
                            round_off = Decimal(parent_data.round_off) if parent_data.round_off else Decimal(0)
                        except (ValueError, TypeError):
                            round_off = Decimal(0)
                        grand_total = total_amount + total_tax + round_off
                    else:
                        total_tax = round_off = grand_total = Decimal(0)

                    # Manually fetch related data (using your existing methods or manual queries)
                    count_data = {count.id: count.name for count in count_table.objects.all()}
                    fabric_data = {fabric.id: fabric.name for fabric in fabric_program_table.objects.all()}
                    gauge_data = {gauge.id: gauge.name for gauge in gauge_table.objects.all()}
                    tex_data = {tex.id: tex.name for tex in tex_table.objects.all()}
                    dia_data = {dia.id: dia.name for dia in dia_table.objects.all()}

                    # Format child PO data for response
                    formatted_data = []
                    for index, item in enumerate(child_data, start=1):
                        formatted_data.append({
                            'action': f'''
                                <button type="button" onclick="knitting_prg_detail_edit('{item.id}')" class="btn btn-primary btn-xs">
                                    <i class="feather icon-edit"></i>
                                </button>
                                <button type="button" onclick="knitting_detail_delete('{item.id}')" class="btn btn-danger btn-xs">
                                    <i class="feather icon-trash-2"></i>
                                </button>
                            ''',
                            'id': index,
                            'fabric_id': fabric_data.get(item.fabric_id, 'N/A'),  # Get fabric name manually
                            'count': getCountNameById(count_table, item.count_id),  # Use your custom method for count_id
                            'gauge': gauge_data.get(item.gauge, 'N/A'),  # Get gauge name manually
                            'tex': tex_data.get(item.tex, 'N/A'),  # Get tex name manually
                            'dia': dia_data.get(item.dia, 'N/A'),  # Get dia name manually
                            'fabric_id_raw': item.fabric_id,
                            'count_id_raw': item.count_id,  # Use count_id directly
                            'gauge_id_raw': item.gauge,
                            'gsm': item.gsm,
                            'tex_id_raw': item.tex,
                            'dia_id_raw': item.dia,
                            'rolls': item.rolls or '-',
                            'wt_per_roll': item.wt_per_roll or '-',
                            'quantity': item.quantity or '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item.is_active else '<span class="badge text-bg-danger">Inactive</span>'
                        })

                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': float(total_quantity),
                        'total_amount': float(total_amount),
                        'total_tax': float(total_tax),
                        'round_off': float(round_off),
                        'grand_total': float(grand_total),
                    })
                else:
                    return JsonResponse({'error': 'No child data found for the given master ID.'})

            except Exception as e:
                return JsonResponse({'error': f"An error occurred: {str(e)}"})

        else:
            return JsonResponse({'error': 'Master ID is missing in the request.'})

    return JsonResponse({'error': 'Invalid request method. POST method expected.'})




def knitting_prg_lists_24_9(request):
    if request.method == 'POST':
        master_id = request.POST.get('prg_id')
        print('MASTER-ID:', master_id)

        if master_id:
            try:
                # Fetch child PO data with related lookups to optimize database queries
                child_data = sub_knitting_table.objects.filter(tm_id=master_id, status=1, is_active=1).select_related(
                    'fabric_id', 'count_id', 'gauge', 'tex', 'dia'
                )
                if child_data.exists():
                    # Aggregate child data totals
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

                    # Fetch parent data with related fields for tax and round_off
                    parent_data = knitting_table.objects.filter(id=master_id).first()
                    if parent_data:
                        total_tax = Decimal(parent_data.total_tax or 0)
                        try:
                            round_off = Decimal(parent_data.round_off) if parent_data.round_off else Decimal(0)
                        except (ValueError, TypeError):
                            round_off = Decimal(0)
                        grand_total = total_amount + total_tax + round_off
                    else:
                        total_tax = round_off = grand_total = Decimal(0)

                    # Format child PO data for response
                    formatted_data = []
                    for index, item in enumerate(child_data, start=1):
                        formatted_data.append({
                            'action': f'''
                                <button type="button" onclick="knitting_prg_detail_edit('{item.id}')" class="btn btn-primary btn-xs">
                                    <i class="feather icon-edit"></i>
                                </button>
                                <button type="button" onclick="knitting_detail_delete('{item.id}')" class="btn btn-danger btn-xs">
                                    <i class="feather icon-trash-2"></i>
                                </button>
                            ''',
                            'id': index,
                            'fabric_id': item.fabric_id.name,
                            'count': getCountNameById(count_table,item.count_id),
                            # 'count': item.count_id.name,
                            'gauge': item.gauge.name,
                            'tex': item.tex.name,
                            'dia': item.dia.name,
                            'fabric_id_raw': item.fabric_id.id,
                            'count_id_raw': item.count_id.id,
                            'gauge_id_raw': item.gauge.id,
                            'gsm': item.gsm,
                            'tex_id_raw': item.tex.id,
                            'dia_id_raw': item.dia.id,
                            'rolls': item.rolls or '-',
                            'wt_per_roll': item.wt_per_roll or '-',
                            'quantity': item.quantity or '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item.is_active else '<span class="badge text-bg-danger">Inactive</span>'
                        })

                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': float(total_quantity),
                        'total_amount': float(total_amount),
                        'total_tax': float(total_tax),
                        'round_off': float(round_off),
                        'grand_total': float(grand_total),
                    })
                else:
                    return JsonResponse({'error': 'No child data found for the given master ID.'})

            except Exception as e:
                return JsonResponse({'error': f"An error occurred: {str(e)}"})

        else:
            return JsonResponse({'error': 'Master ID is missing in the request.'})

    return JsonResponse({'error': 'Invalid request method. POST method expected.'})


def knitting_prg_lists_bk_972025(request): 
    if request.method == 'POST':
        master_id = request.POST.get('prg_id')
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

                             # Raw IDs (hidden in table or used in JS only)
                            'fabric_id_raw': item['fabric_id'],
                            'count_id_raw': item['count_id'],
                            'gauge_id_raw': item['gauge'],
                            'gsm': item['gsm'],
                            'tex_id_raw': item['tex'],
                            'dia_id_raw': item['dia'],



                            'rolls': item['rolls'] or '-',
                            'wt_per_roll': item['wt_per_roll'] or '-',
                            # 'rate': item['rate'] or '-',
                            'quantity': item['quantity'] or '-',
                            # 'total_amount': item['total_amount'] or '-',
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

def getItemNameById(tbl, product_id):
    try:
        party = tbl.objects.get(id=product_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message 
    return party


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


# def update_knitting_program(request): 

 
# def update_knitting_program(request):
#     user_id = request.session.get('user_id')
#     if request.method == 'POST':
#         master_id = request.POST.get('tm_id') 
#         product_id = request.POST.get('fabric_id')
#         count = request.POST.get('count')
#         gauge = request.POST.get('gauge')
#         quantity = request.POST.get('quantity')
#         tex = request.POST.get('tex')
#         dia = request.POST.get('dia')
#         rolls = request.POST.get('rolls')
#         wt_per_role = request.POST.get('wt_per_roll')
#         total_amount = request.POST.get('total_amount')
#         print('wt:',wt_per_role)

#         if not master_id or not product_id:
#             return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

#         try:
#             # Add or update the child table record
#             child_item, created = sub_knitting_table.objects.update_or_create(
#                 tm_id=master_id, fabric_id=product_id,
#                 defaults={
#                     'count': count, 
#                     'gauge': gauge,
#                     'quantity': quantity,
#                     'rolls': rolls,
#                     'tex': tex,
#                     'dia':dia,
#                     'wt_per_roll':wt_per_role,
#                     'total_amount':total_amount,
#                     'status': 1,
#                     'is_active': 1,
#                     'created_by':user_id,
#                     'updated_by':user_id,
#                     'created_on':datetime.now(),
#                     'updated_on':datetime.now(),
#                 }
#             )

#             # Update `tm_table` with new totals
#             # updated_totals = update_tm_table_totals(master_id)

#             return JsonResponse({'success': True})

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


def update_knitting_program(request):
    if request.method == 'POST':
        master_id = request.POST.get('parent_id')  # Parent Table ID
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
        edit_id = request.POST.get('edit_id')  # This determines if it's an update or new entry

        # Ensure required fields are provided
        if not product_id or not po_id:
            return JsonResponse({'success': False, 'error_message': 'Missing required data'})

        try:
            if edit_id:  # Update existing record
                child_item = sub_knitting_table.objects.get(id=edit_id)
                child_item.fabric_id = product_id
                child_item.count = count
                child_item.gauge = gauge
                child_item.tex = tex
                child_item.dia = dia
                child_item.tm_po_id = po_id
                child_item.gsm = gsm
                child_item.rolls = rolls
                child_item.wt_per_roll = wt_per_roll
                child_item.quantity = quantity
                child_item.rate = rate
                child_item.total_amount = amount
                child_item.save()
                message = "Knitting program updated successfully."
            else:  # Create new record
                child_item = sub_knitting_table.objects.create(
                    fabric_id=product_id,
                    tm_id=master_id,
                    count=count,
                    gauge=gauge,
                    tex=tex,
                    dia=dia,
                    tm_po_id=po_id,
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

            # Update `tm_table` totals
            updated_totals = update_knitting(master_id)

            return JsonResponse({'success': True, 'message': message, **updated_totals})

        except sub_knitting_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Record not found for update.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    
    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_knitting_program_test(request):
    if request.method == 'POST':
        master_id = request.POST.get('parent_id')  # Could be empty
        po_id = request.POST.get('po_id')  # Used for creating a new entry
        product_id = request.POST.get('fabric_id')
        count = request.POST.get('count')
        gauge = request.POST.get('gauge')
        tex = request.POST.get('tex')
        dia = request.POST.get('dia')
        gsm = request.POST.get('gsm')
        rolls = request.POST.get('rolls')
        wt_per_roll = request.POST.get('wt_per_roll')
        
        # Convert numeric fields safely
        try:
            quantity = Decimal(request.POST.get('quantity', 0))
            rate = Decimal(request.POST.get('rate', 0))
            amount = Decimal(request.POST.get('total_amount', 0))
        except:
            return JsonResponse({'success': False, 'error_message': 'Invalid numeric values'})

        # Ensure at least `po_id` or `master_id` is present
        if not master_id and not po_id:
            return JsonResponse({'success': False, 'error_message': 'Missing PO ID or Master ID'})

        try:
            # If `master_id` exists, update; otherwise, create a new record using `po_id`
            if master_id:
                child_item, created = sub_knitting_table.objects.update_or_create(
                    id=master_id,
                    defaults={
                        'fabric_id': product_id,
                        'count': count,
                        'gauge': gauge,
                        'tex': tex,
                        'dia': dia,
                        'tm_po_id': po_id,
                        'gsm': gsm,
                        'rolls': rolls,
                        'wt_per_roll': wt_per_roll,
                        'quantity': quantity,
                        'rate': rate,
                        'total_amount': amount,
                        'status': 1,
                        'is_active': 1
                    }
                )
            else:
                # Create a new entry if only `po_id` is provided
                child_item = sub_knitting_table.objects.create(
                    tm_po_id=po_id,
                    fabric_id=product_id,
                    count=count,
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
                created = True

            # Update `tm_table` totals if `master_id` is available
            updated_totals = update_knitting(master_id) if master_id else {}

            return JsonResponse({'success': True, 'created': created, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

# `````````````````````````` KNITTING DELIVER ````````````````````````````````````````````


from django.shortcuts import render, HttpResponseRedirect


 
# def knitting_delivery(request):
#     if 'user_id' in request.session: 
#         user_id = request.session['user_id']
        
       
#         process = process_table.objects.filter(status=1, stage__in=['bleaching', 'dyeing','knitting','inhouse'])
#         deliver = party_table.objects.filter(is_knitting=1,status=1)
        
#         last_purchase = gf_delivery_table.objects.order_by('-id').first()
#         if last_purchase:
#             delivery_number = last_purchase.id + 1 
#         else:
#             delivery_number = 1  # Default if no records exist 
#         # Pass both supplier and knitting data to the template
#         party = party_table.objects.filter(status=1,is_knitting=1) 
#         bag = bag_table.objects.filter(status=1) 
#         count = count_table.objects.filter(status=1)

#         program = knitting_table.objects.filter(status=1)   
        
#         inward_list = yarn_inward_table.objects.filter(status=1)

#         return render(request, 'knitting_deliver/add_knitting_deliver.html', {
#             # 'supplier': supplier,
#             'knitting': knitting, 
#             'process':process, 
#             'party':party,
#             'deliver':deliver,
#             'delivery_number':delivery_number,
#             'inward_list':inward_list,
#             'bag':bag,
#             'count':count,
#             'program':program
#         })
#     else:
#         return HttpResponseRedirect("/signin")






from django.db import connection


def knitting_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']

        process = process_table.objects.filter(status=1, stage__in=['bleaching', 'dyeing','knitting','inhouse'])
        deliver = party_table.objects.filter(is_knitting=1, status=1)

        last_purchase = gf_delivery_table.objects.order_by('-id').first()
        delivery_number = last_purchase.id + 1 if last_purchase else 1

        party = party_table.objects.filter(status=1, is_knitting=1) 
        bag = bag_table.objects.filter(status=1) 
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)   

        # # --- Execute custom SQL to get filtered inward_list ---
        # with connection.cursor() as cursor:
        #     cursor.execute("""
        #         SELECT y.* 
        #         FROM tm_yarn_inward y
        #         LEFT JOIN (
        #             SELECT inward_id, SUM(total_quantity) AS delivered_quantity
        #             FROM tm_yarn_deliver
        #             WHERE inward_id IS NOT NULL
        #             GROUP BY inward_id
        #         ) kd ON y.id = kd.inward_id
        #         WHERE y.status = 1
        #         AND (
        #             kd.inward_id IS NULL
        #             OR kd.delivered_quantity < y.total_quantity
        #         )
        #     """)
        #     columns = [col[0] for col in cursor.description]
        #     inward_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render(request, 'knitting_deliver/add_knitting_deliver.html', {
            'knitting': knitting, 
            'process': process, 
            'party': party,
            'deliver': deliver,
            'delivery_number': delivery_number,
            # 'inward_list': inward_list,
            'bag': bag,
            'count': count,
            'program': program
        })
    else:
        return HttpResponseRedirect("/signin")




# from django.http import JsonResponse

# def get_inward_lists(request):
#     if request.method == 'POST' and 'supplier_id' in request.POST:
#         supplier_id = request.POST['supplier_id']
#         print('inward-supplier:', supplier_id)

#         if supplier_id:
#             # Fetch all inward orders for this supplier
#             parent_orders = yarn_inward_table.objects.filter(
#                 supplier_id=supplier_id,
#                 status=1
#             ).values_list('id', flat=True) 

#             print('Parent Orders:', list(parent_orders))  # Debugging output

#             if not parent_orders:
#                 return JsonResponse([], safe=False)

#             # Get all child orders linked to these inward orders
#             child_orders = sub_yarn_inward_table.objects.filter(
#                 tm_id__in=parent_orders
#             ).values('po_id', 'product_id')

#             print('Child Orders:', child_orders)  # Debugging output
#             print('Child Orders:', list(child_orders))  # Debugging output

#             if not child_orders:
#                 return JsonResponse([], safe=False)

#             # Extract unique PO IDs
#             po_ids = set(order['po_id'] for order in child_orders)
#             print('PO IDs:', po_ids)

#             # Get corresponding inward numbers
#             order_numbers = yarn_inward_table.objects.filter(
#                 id__in=po_ids
#             ).values('id', 'inward_number').order_by('-id') 

#             print('Order Numbers:', list(order_numbers))  # Debugging output

#             data = []
#             for order in order_numbers:
#                 # Get all products linked to this PO ID
#                 product_ids = [item['product_id'] for item in child_orders if item['po_id'] == order['id']]
#                 print(f"Products for PO {order['id']}:", product_ids)  # Debugging output

#                 product_details = list(product_table.objects.filter(
#                     id__in=product_ids
#                 ).values('id', 'name'))

#                 data.append({
#                     'id': order['id'],
#                     'inward_number': order['inward_number'],
#                     'products': product_details
#                 })

#             return JsonResponse(data, safe=False)

#     return JsonResponse([], safe=False)

 

from django.db.models import Sum


def get_po_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']

        if supplier_id:
            child_orders = yarn_po_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).values_list('po_id', flat=True)

            orders = list(parent_po_table.objects.filter(
                id__in=child_orders,
                status=1
            ).values('id', 'po_number', 'name', 'mill_id').order_by('-id'))

            # Get mill names manually
            mill_ids = set(order['mill_id'] for order in orders if order['mill_id'])
            mill_map = {
                party.id: party.name for party in party_table.objects.filter(id__in=mill_ids)
            }

            for order in orders:
                order['mill_name'] = mill_map.get(order['mill_id'], '')

            totals = yarn_po_balance_table.objects.filter(
                party_id=supplier_id,
                balance_quantity__gt=0
            ).aggregate(
                po_bag=Sum('ord_bags'),
                po_quantity=Sum('po_quantity'),
                inward_bag=Sum('in_bag'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity')
            )

            balance_bag = (totals['po_bag'] or 0) - (totals['inward_bag'] or 0)

            return JsonResponse({
                'orders': orders,
                'po_bag': balance_bag,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0)
            })

    return JsonResponse({'orders': []})






def get_inward_lists(request):
    if request.method == 'POST' and 'supplier_id' in request.POST:
        supplier_id = request.POST['supplier_id']
        print('supplier_id:', supplier_id)

        if supplier_id:
            # Fetch all child purchase orders for the given supplier_id where is_assigned=0
            # child_orders = sub_yarn_inward_table.objects.filter(
            #     tm_po_id__in=yarn_inward_table.objects.filter(supplier_id=supplier_id, status=1, is_inward=0).values('id'),
            # ).values('tm_po_id')  # Get the IDs of the parent orders

            # child_orders = sub_yarn_inward_table.objects.filter(deliver_to=supplier_id,status=1, is_inward=0).values('deliver_to','po_id','tm_id')
            # child_orders = sub_yarn_inward_table.objects.filter(deliver_to=supplier_id,status=1).values('tm_id')
            child_orders = sub_yarn_inward_table.objects.filter(
                party_id=supplier_id,
                status=1
            ).filter(
                Q(bag__gt=0) | Q(quantity__gt=0)
            ).values('tm_id')




            # Now filter parent purchase orders based on these IDs
            order_numbers = yarn_inward_table.objects.filter( 
                id__in=child_orders, status=1 
            ).values('id', 'inward_number').order_by('-id') 

            # Calculate total bags and total quantity 
            total_bag_sum = 0
            total_quantity_sum = 0
            for order in order_numbers:
                parent_order = yarn_inward_table.objects.get(id=order['id'])
                # prg = parent_order.program_id
                
                # Calculate total bags and total quantity for each order
                # child_order = sub_yarn_inward_table.objects.filter(tm_id=parent_order.id,deliver_to=supplier_id )
                

                child_order = sub_yarn_inward_table.objects.filter(
                    tm_id=parent_order.id,
                    party_id=supplier_id
                ).filter(
                    Q(bag__gt=0) | Q(quantity__gt=0)
                )



                for child in child_order:
                    total_bag_sum += child.bag
                    total_quantity_sum += child.quantity  # Assuming remaining_quantity is the quantity

            # Convert the queryset to a list
            data = list(order_numbers)
            
            # Add total bags and total quantity to the response
            return JsonResponse({
                'orders': data,
                # 'program_id':prg,
                'total_bagss': total_bag_sum,
                'total_quantity': total_quantity_sum
            }, safe=False)
         
    return JsonResponse([], safe=False)




import json

@csrf_exempt
def get_lot_no(request):
    if request.method == "POST":
        party_id = request.POST.get("party_id")
        prg_id = request.POST.get("prg_id") 

        # Get count_id(s) for the selected program
        program_count_ids = list(sub_knitting_table.objects.filter(
            tm_id=prg_id,
            status=1
        ).values_list('count_id', flat=True))
        print('Program count_id(s):', program_count_ids)

        balance_qs = yarn_out_sum_table.objects.filter(
            party_id=party_id,  
            # program_id=prg_id,
            remaining_quantity__gt=0
        ).values( 'yarn_count_id', 'po_id','po_bags','po_quantity','bag_wt',)

        print('values:',balance_qs)
        # ).values('inward_id', 'yarn_count_id', 'po_id','po_bags','po_quantity','po_bag_wt',)
 


        # # Get balance rows from yarn_out_balance_table
        # balance_qs = yarn_out_balance_table.objects.filter( 
        #     party_id=party_id,
        #     program_id=prg_id,
        #     available_quantity__gt=0
        # ).values('inward_id', 'yarn_count_id', 'po_id','po_bags','po_quantity','po_bag_wt',)

        balance_list = list(balance_qs)
        print('Filtered yarn_out_balance:', balance_list)

        # Extract inward_ids
        # inward_ids = [row['inward_id'] for row in balance_list]
        po_ids = [row['po_id'] for row in balance_list]

        # Fetch inward_number from yarn_inward_table
        inward_qs = yarn_inward_table.objects.filter( 
            # id__in=inward_ids,
            po_id__in=po_ids,
            status=1
        ).values('id', 'inward_number','po_id')
        inward_map = {row['id']: row['inward_number'] for row in inward_qs}
        print('inwds:',inward_map)
        # Merge inward_number into each balance row
        # for row in balance_list:
        #     row['inward_number'] = inward_map.get(row['inward_id'], '')

        return JsonResponse({
            'inward_list': inward_map,
            # 'inward_list': balance_list,
            'count_id': program_count_ids 
        })

    return JsonResponse({'status': 'Failed', 'message': 'Invalid request method'})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from collections import defaultdict
@csrf_exempt
def get_inward_details(request): 
    if request.method == 'POST':
        try:
            # Parse and validate inward_ids
            raw_inward_ids = request.POST.get('inward_id', '[]')
            inward_ids = json.loads(raw_inward_ids)

            # Ensure all inward_ids are integers
            inward_ids = [int(i) for i in inward_ids if str(i).isdigit()]
            if not inward_ids:
                return JsonResponse({'error': 'No valid inward_ids provided'}, status=400)

            print('id-inw:', inward_ids)

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid inward_ids format: {str(e)}'}, status=400)

        party_id = request.POST.get('party_id')
        prg_id = request.POST.get('prg_id')
        po_id = request.POST.get('po_id')
        print('po-ids:',po_id)
        print('party-ids:', party_id, prg_id, inward_ids)

        result = []
        po_ids_set = set()
        knitting_ids_set = set()

        for inward_id in inward_ids:
            parent_inward = yarn_inward_table.objects.filter(id=inward_id).first()
            if not parent_inward:
                print(f'No parent inward found for inward_id: {inward_id}')
                continue

            print('inw-parent:', parent_inward.party_id)
 
            # Query child entries
            # child_entries = yarn_out_balance_table.objects.filter(
            #     inward_id=inward_id,
            #     party_id=party_id, 
            #     program_id=prg_id,
            #     balance_in_quantity__gt=0
            # ).values('inward_id', 'yarn_count_id', 'po_id','po_bags','po_quantity','po_bag_wt',)

            # inward_data = yarn_out_balance_table.objects.filter(
            #     inward_id=inward_id,
            #     party_id=party_id, 
            #     program_id=prg_id,
            #     available_quantity__gt=0
            # ).values('inward_id', 'yarn_count_id', 'po_id','po_bags','po_quantity','po_bag_wt',)

            program_count_ids = list(
                sub_knitting_table.objects.filter(
                    tm_id=prg_id,
                    status=1
                ).values_list('count_id', flat=True)
            )
            print('Program count_id(s):', program_count_ids)

            # Check if all count_ids are the same
            unique_count_ids = set(program_count_ids)
            if len(unique_count_ids) == 1:
                only_count_id = program_count_ids[0]
                print('Only one unique count_id:', only_count_id)
            else:
                print('Multiple or no unique count_ids:', program_count_ids)


            inward_data  = yarn_out_balance_table.objects.filter(  
                party_id=party_id,
                yarn_count_id = only_count_id,
                available_quantity__gt=0
            ).values('inward_id', 'yarn_count_id', 'po_id','remaining_bags','remaining_quantity','bag_wt')
            # ).values('inward_id', 'yarn_count_id', 'po_id','po_bags','po_quantity','po_bag_wt',)


            child_entries = yarn_out_sum_table.objects.filter(
                # inward_id=inward_id,
                party_id=party_id,
                po_id=po_id,
                remaining_quantity__gt=0
            ).values( 'yarn_count_id', 'po_id','po_bags','remaining_quantity','remaining_bags','po_quantity','bag_wt',)




            balance_list = list(child_entries)
            inward_ids = list(inward_data)
            print('inward-lists:', inward_ids)
            print('Filtered yarn_out_balance:', balance_list)

            # Extract inward_ids
            inward_ids = [row['inward_id'] for row in inward_ids]
            yarn_count = [row['yarn_count_id'] for row in balance_list]
            po_id = [row['po_id'] for row in balance_list]
            po_bags = [row['po_bags'] for row in balance_list]
            po_quantity = [row['po_quantity'] for row in balance_list]
            po_bag_wt = [row['bag_wt'] for row in balance_list]


            # Get all yarn_count_ids from balance_list
            yarn_count_ids = [row['yarn_count_id'] for row in balance_list]

            # Fetch the names from count_table
            count_names = count_table.objects.filter(id__in=yarn_count_ids).values('id', 'name')

            # Create a mapping of id to name
            count_name_map = {item['id']: item['name'] for item in count_names}

            # Now build the result list with yarn_count names
            result = []
            for row in balance_list:
                yarn_id = row['yarn_count_id']
                result.append({
                    'tm_id': inward_ids,#row['inward_id'],
                    # 'bag': row['po_bags'], 
                    'bag': row['remaining_bags'], 
                    'per_bag': row['bag_wt'],
                    'yarn_count_id': yarn_id,
                    'yarn_count': count_name_map.get(yarn_id, ''),
                    'quantity': row['remaining_quantity'],
                    'gross_wt': row['remaining_quantity'],
                    'po_id': row['po_id'],
                    'inward_id': inward_ids,#row['inward_id']
                })


        # Fetch PO deliveries related to the POs found in the results
        po_deliveries = yarn_po_delivery_table.objects.filter(
            tm_po_id__in=po_ids_set
        )

        print('po-deli:', po_deliveries)

        # Fetch knitting ids
        knitting_ids_set.update(
            po_deliveries.exclude(party_id__isnull=True)
                         .values_list('party_id', flat=True)
                         .distinct()
        )

        return JsonResponse({
            'data': result,
            'deliver_bag': 0, 
            'deliver_quantity': 0,
            'knitting_ids': list(knitting_ids_set)
        })

    return JsonResponse({'data': [], 'deliver_bag': 0, 'deliver_quantity': 0, 'knitting_ids': []}, status=400)




def get_po_fabric_lists(request):
    if request.method == 'POST' and 'po_id' in request.POST: 
        po_id = request.POST['po_id']
        print('po_id:', po_id)

        if po_id:
            # Get child PO details linked to the parent PO
            order_details = child_po_table.objects.filter(tm_po_id=po_id).values('yarn_count_id', 'quantity', 'tm_po_id', 'id')

            # Get the product IDs
            product_ids = [order['yarn_count_id'] for order in order_details] 

            # Fetch corresponding product details
            products = count_table.objects.filter(id__in=product_ids).values('id', 'name')

            # Merge PO quantity with product data
            product_data = []
            for order in order_details:
                product = next((p for p in products if p['id'] == order['yarn_count_id']), None)
                if product:
                    product_data.append({
                        'id': product['id'],
                        'name': product['name'],
                        'po_quantity': order['quantity'],  # Include PO quantity
                        'tm_po_id': order['tm_po_id'],  # Accessing as a dictionary key
                        'tx_id': order['id'],  # Accessing as a dictionary key
                    })

            return JsonResponse(product_data, safe=False)

    return JsonResponse([], safe=False)






def get_fabric_details(request): 
    if request.method == 'POST' and 'fabric_id' in request.POST:
        fabric_id = request.POST['fabric_id']
        print('fabric:',fabric_id)
        uom_details = product_table.objects.filter(id=fabric_id).values('id', 'name')

        return JsonResponse({"uom": list(uom_details)}, safe=False)

    return JsonResponse({"uom": []}, safe=False)



# ``````````````````````````end get lot no``````````````````````````````


@csrf_exempt
def get_delivery_details(request):  
    if request.method == "POST":
        lot_no = request.POST.get("lot_no")  # Get the lot number from AJAX request 
 
        if lot_no:
            # Get Total Quantity from KnittingTable
            total_program_qty = knitting_table.objects.filter(lot_no=lot_no,status=1).aggregate(Sum("total_quantity"))["total_quantity__sum"] or 0

            # Get Delivered Quantity from KnittingDeliveryTable
            total_delivered_qty = yarn_delivery_table.objects.filter(lot_no=lot_no,status=1).aggregate(Sum("total_quantity"))["total_quantity__sum"] or 0

            # Compute Balance (Total - Delivered)
            balance_qty = total_program_qty - total_delivered_qty
        
            # Get program-wise data
            program = knitting_table.objects.filter(lot_no=lot_no,status=1).values("total_quantity").distinct()
            deliveries = yarn_delivery_table.objects.filter(lot_no=lot_no,status=1).values("total_quantity").distinct()

            data = []
            for delivery in program:
                program = delivery["total_quantity"]
                program_total = knitting_table.objects.filter(lot_no=lot_no).aggregate(Sum("total_quantity"))["total_quantity__sum"] or 0
                # program_g_total = knitting_table.objects.filter(lot_no=lot_no).aggregate(Sum("gross_wt"))["gross_wt__sum"] or 0
                delivered_total = yarn_delivery_table.objects.filter(lot_no=lot_no).aggregate(Sum("total_quantity"))["total_quantity__sum"] or 0
                # delivered_g_total = yarn_delivery_table.objects.filter(lot_no=lot_no).aggregate(Sum("total_quantity"))["total_quantity__sum"] or 0
                balance = program_total - delivered_total
 
                data.append({
                    "program": program,
                    "total_quantity": program_total,
                    "delivered": delivered_total,
                    "balance": balance
                })

            return JsonResponse({
                "data": data,
                "total_program_quantity": total_program_qty,
                "total_delivered_quantity": total_delivered_qty,
                "gross_total": balance_qty
            })

    return JsonResponse({"data": [], "total_program_quantity": 0, "total_delivered_quantity": 0, "gross_total": 0})  # Default empty response




@csrf_exempt
def get_po_delivery_details(request):
    if request.method == 'POST':
        inward_id = request.POST.get('inward_id')
        deliver_id = request.POST.get('party_id')

        print('ids:',inward_id, deliver_id)
        try:
            inward = sub_yarn_inward_table.objects.filter(tm_id=inward_id,deliver_to = deliver_id).first()
            if not inward:
                return JsonResponse({'data': [], 'message': 'Inward not found'}, status=404)

            po_id = inward.po_id

            # All deliveries for that PO
            deliveries = yarn_po_delivery_table.objects.filter(tm_po_id=po_id,knitting=deliver_id, status=1)

            delivery_data = []
            total_program_qty = 0
            total_weight = 0

            for delivery in deliveries:
                # Total bags already inwarded against this delivery
                inwarded_bags = sub_yarn_inward_table.objects.filter(deliver_to=delivery.id).aggregate(
                    total=Sum('remaining_bag')
                )['total'] or 0

                remaining_bags = (delivery.bag or 0) - inwarded_bags
                if remaining_bags <= 0:
                    continue  # Skip if nothing remaining

                child = child_po_table.objects.filter(tm_po_id=po_id).first()
                parent_po = parent_po_table.objects.filter(id=po_id).first()
                po_number = parent_po.po_number
                product = count_table.objects.filter(id=child.yarn_count_id).first()
                party = party_table.objects.filter(id=deliver_id).first()
                party_name = party.name

                delivery_data.append({
                    'po_number': po_number,
                    'po_name': parent_po.name,
                    'deliver_to_id': delivery.knitting if delivery.knitting and delivery.knitting else '',
                    'deliver_to': party_name if party_name else '',
                    'yarn_count': product.name if product else '',
                    'bag': remaining_bags,
                    'per_bag': child.per_bag if child else 0,
                    'quantity': remaining_bags * (child.per_bag if child else 0),
                })

                total_program_qty += remaining_bags * (child.per_bag if child else 0)
                total_weight += remaining_bags * (child.gross_wt if child else 0)

            return JsonResponse({
                'data': delivery_data,
                'total_program_quantity': total_program_qty,
                'total_weight': total_weight
            })

        except Exception as e:
            print("Error in get_po_delivery_details:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)





@csrf_exempt 
def get_knitting_details(request):  
    if request.method == "POST":
        lot_no = request.POST.get("lot_no")  # Get the lot number from AJAX request 
        print('lot:',lot_no)
        if lot_no:
            # Get knitting details for the provided lot_no
            knitting = knitting_table.objects.filter(lot_no=lot_no, status=1).first()
            knitting_details = sub_knitting_table.objects.filter(tm_id=knitting.id, status=1)

            # Prepare data to send in the response
            data = [] 

            for detail in knitting_details:
                fabric = fabric_program_table.objects.filter(id=detail.fabric_id).first()
                fabric_name = fabric.name if fabric else "N/A"

                count = count_table.objects.filter(id=detail.count).first()
                count_name = count.name if count else "N/A"

                data.append({
                    "program": knitting.name,
                    "fabric": fabric_name,
                    "fabric_id": detail.fabric_id,
                    "yarn_count_id": detail.count,
                    "yarn_count": count_name,
                    "rolls": detail.rolls,
                    "roll_weight": detail.wt_per_roll,
                    "quantity": detail.quantity
                })



            # for detail in knitting_details:
            #     fabric = fabric_table.objects.filter(id=detail.fabric_id).first()
            #     fabric_name = fabric.name

            #     count = count_table.objects.filter(id=detail.count)
            #     count_name = count.name


            #     data.append({
            #         "program": knitting.name,#detail.tm_id,  # Assuming tm_id is the program identifier
            #         "fabric":fabric_name,
            #         "fabric_id":detail.fabric_id,
            #         "yarn_count_id": detail.count,  # Replace with actual yarn count if available
            #         "yarn_count": count_name,  # Replace with actual yarn count if available
            #         "rolls": detail.rolls,  # Assuming bag represents rolls
            #         "roll_weight": detail.wt_per_roll,  # Assuming gross_wt represents roll weight
            #         "quantity": detail.quantity  # Quantity from knitting details
            #     }) 

            # Return the data in JSON response
            return JsonResponse({
                "data": data,
                "total_program_quantity": sum([item["quantity"] for item in data]),
                "total_weight": sum([item["roll_weight"] for item in data]),
            })

    return JsonResponse({"data": [], "total_program_quantity": 0, "total_weight": 0})  # Default empty response





def load_knitting_program_detail(request):
    if request.method == "GET":
        party_id = request.GET.get('party_id')
        po_ids = request.GET.getlist('prg_id[]')  # Get list of selected PO IDs
        print('po-id:', po_ids)

        if not po_ids:
        # if not supplier_id or not po_ids:
            return JsonResponse({'error': 'Supplier ID and Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided supplier and PO IDs
            parent_pos = knitting_table.objects.filter(id__in=po_ids,knitting_id=party_id)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                # Retrieve child orders linked to each parent PO
                program = knitting_table.objects.filter(po_id=po.id).first()
                if program:

                    program_lot = program.lot_no if program.lot_no else 0
                    print('lot-no:',program_lot)
                else:
                    program_lot = 0
                orders = sub_knitting_table.objects.filter(tm_id=po.id)
                print('tm-order:',orders)

                for order in orders:
                    product = product_table.objects.filter(id=order.fabric_id).first()
                    count = count_table.objects.filter(id=order.count).first()
                    gauge = gauge_table.objects.filter(id=order.gauge).first()
                    tex = tex_table.objects.filter(id=order.tex).first()

                    # # Get remaining values
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
                        'count_id': order.count,
                        'count': count.count if count else "Unknown count", 
                        'gauge_id': order.gauge,
                        'gauge': gauge.name if gauge else "Unknown gauge", 
                        'tex_id': order.tex,
                        'tex': tex.name if tex else "Unknown tex", 
                        'dia':order.dia,
                        'gsm':order.gsm,
                        'rolls':order.rolls,
                        'wt_per_roll':order.wt_per_roll,
                        'quantity':order.quantity,
                        'rate':order.rate,
                        'amount':order.total_amount,
                        'id': order.id,
                        'po_id': order.tm_po_id,
                        'tm_id': order.tm_po_id,
                        'tx_id': order.id,
                        'program_lot':program_lot ,
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)




def get_po_fabric_lists_12(request):
    if request.method == 'POST' and 'po_id' in request.POST:
        po_id = request.POST['po_id']
        print('po_id:', po_id)

        if po_id:
            # Get child PO details linked to the parent PO
            order_details = child_po_table.objects.filter(tm_po_id=po_id).values('product_id', 'quantity','tm_po_id','id')

            # Get the product IDs
            product_ids = [order['product_id'] for order in order_details]

            # Fetch corresponding product details
            products = product_table.objects.filter(id__in=product_ids).values('id', 'name')

            # Merge PO quantity with product data
            product_data = []
            for order in order_details:
                product = next((p for p in products if p['id'] == order['product_id']), None)
                if product:
                    product_data.append({
                        'id': product['id'],
                        'name': product['name'],
                        'po_quantity': order['quantity'],  # Include PO quantity
                        'tm_po_id':order.tm_po_id,
                        'tx_id':order.id,
                    })

            return JsonResponse(product_data, safe=False)

    return JsonResponse([], safe=False)



def load_po_details_inward_crtbk_25(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')  # Selected PO IDs
        deliver_ids = request.GET.getlist('deliver_to')  # Selected delivery IDs (could be multiple)

        if not po_ids or not deliver_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) and Delivery ID(s) are required.'}, status=400)

        try:
            parent_pos = parent_po_table.objects.filter(id__in=po_ids, supplier_id=supplier_id)
            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                total_quantity = po.quantity
                # Get delivery record for the selected deliver_id(s)
                deliveries = yarn_po_delivery_table.objects.filter(tm_po_id=po.id, knitting__in=deliver_ids, status=1)

                # Program lot
                program = knitting_table.objects.filter(po_id=po.id).first()
                program_lot = program.lot_no if program and program.lot_no else 0

                for delivery in deliveries:
                    child = child_po_table.objects.filter(tm_po_id=po.id, is_active=1).first()
                    if not child:
                        continue

                    product = count_table.objects.filter(id=child.yarn_count_id).first()
                    
                    total_bag = child.bag
                    remaining_bag = delivery.bag or 0
                    remaining_quantity = child.remaining_quantity or 0
                    remaining_amount = delivery.amount or 0

                    # Skip fully delivered entries
                    if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
                        continue
                    total_bag_sum = sum([child_po_table.objects.filter(tm_po_id=po.id, is_active=1).first().bag or 0 for po in parent_pos])
                    total_quantity_sum = sum([po.total_quantity or 0 for po in parent_pos])
                    order_data.append({
                        'product_id': child.yarn_count_id,
                        'product': product.name if product else "Unknown Product", 
                        'tax_value': 5,
                        'bag': delivery.bag,
                        'per_bag': child.per_bag,
                        'quantity': remaining_quantity,
                        'rate': child.rate,
                        'actual_rate': child.actual_rate,
                        'discount': child.discount,
                        'gross_wt': child.gross_wt,
                        'id': child.id,
                        'po_id': po.id,
                        'tm_id': po.id,
                        'tx_id': delivery.id,
                        'program_lot': program_lot,
                        'total_quantity':total_quantity_sum,
                        'total_bag':total_bag_sum
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


# from django.db.models import Sum

# @csrf_exempt
# def load_po_details_inward(request):
#     if request.method == "GET":
#         supplier_id = request.GET.get('supplier_id')
#         po_ids = request.GET.getlist('po_id[]')  # Selected PO IDs
#         deliver_ids = request.GET.getlist('deliver_to')  # Selected delivery IDs (could be multiple)

#         if not po_ids or not deliver_ids:
#             return JsonResponse({'error': 'Purchase Order ID(s) and Delivery ID(s) are required.'}, status=400)

#         try:
#             parent_pos = parent_po_table.objects.filter(id__in=po_ids, supplier_id=supplier_id)
#             if not parent_pos.exists():
#                 return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

#             order_data = []
#             total_bag_sum = 0
#             total_quantity_sum = 0

#             for po in parent_pos:
#                 total_quantity = po.total_quantity or 0
#                 total_quantity_sum += total_quantity

#                 # Get delivery records matching the selected delivery IDs
#                 deliveries = yarn_po_delivery_table.objects.filter(
#                     tm_po_id=po.id, knitting__in=deliver_ids, status=1
#                 )

#                 for delivery in deliveries:
#                     # Find already inwarded bag quantity against this delivery
#                     inward_bag_data = sub_yarn_inward_table.objects.filter(
#                         po_id=po.id,
#                         deliver_to=delivery.knitting,
#                         # tx_id=delivery.id,  # Assuming you store the delivery_id as tx_id in sub_inward
#                         status=1
#                     ).aggregate(total_inward_bags=Sum('bag'))

#                     inwarded_bag = inward_bag_data['total_inward_bags'] or 0

#                     # Calculate remaining bag
#                     remaining_bag = (delivery.bag or 0) - inwarded_bag

#                     # Skip if no remaining bag
#                     if remaining_bag <= 0:
#                         continue

#                     child = child_po_table.objects.filter(tm_po_id=po.id, is_active=1).first()
#                     if not child:
#                         continue

#                     product = count_table.objects.filter(id=child.yarn_count_id).first()

#                     total_bag_sum += remaining_bag


#                     order_data.append({ 
#                         'product_id': child.yarn_count_id,
#                         'product_name': product.name if product else "Unknown Product",  # Required by JS
#                         'tax_value': 5,
                
#                         'bag': remaining_bag,
#                         'per_bag': child.per_bag,
#                         'quantity': child.remaining_quantity or 0,
#                         'rate': child.rate,
#                         'actual_rate': child.actual_rate,
#                         'discount': child.discount,
#                         'gross_wt': child.gross_wt,
#                         'id': child.id,
#                         'po_id': po.id,
#                         'tm_id': po.id,
#                         'tx_id': delivery.id or 0,
#                         'program_lot': knitting_table.objects.filter(po_id=po.id).first().lot_no if knitting_table.objects.filter(po_id=po.id).exists() else 0,
#                     })

                  

#             return JsonResponse({'orders': order_data, 'total_bag': total_bag_sum, 'total_quantity': total_quantity_sum})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method.'}, status=400)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Sum


@csrf_exempt
def load_po_details_inward(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')
        deliver_ids = request.GET.getlist('deliver_to')

        if not po_ids or not deliver_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) and Delivery ID(s) are required.'}, status=400)

        try:
            parent_pos = parent_po_table.objects.filter(id__in=po_ids, party_id=supplier_id)
            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            total_bag_sum = 0
            total_quantity_sum = 0

            for po in parent_pos:
                total_quantity = po.quantity or 0
                total_quantity_sum += total_quantity

                deliveries = yarn_po_delivery_table.objects.filter(
                    tm_po_id=po.id, party_id__in=deliver_ids, status=1
                )

                for delivery in deliveries:
                    inward_bag_data = sub_yarn_inward_table.objects.filter(
                        po_id=po.id,
                        deliver_to=delivery.party_id,
                        status=1
                    ).aggregate(total_inward_bags=Sum('bag'))

                    inwarded_bag = inward_bag_data['total_inward_bags'] or 0
                    remaining_bag = (delivery.bag or 0) - inwarded_bag

                    if remaining_bag <= 0:
                        continue

                    child = parent_po_table.objects.filter(id=po.id, is_active=1).first()
                    if not child:
                        continue

                    product = count_table.objects.filter(id=child.yarn_count_id).first()
                    total_bag_sum += remaining_bag

                    order_data.append({ 
                        'product_id': child.yarn_count_id,
                        'product_name': product.name if product else "Unknown Product",
                        'tax_value': 5,
                        'bag': remaining_bag,
                        'per_bag': child.per_bag,
                        'quantity': child.quantity or 0,
                        'rate': child.rate,
                        'actual_rate': child.rate,
                        'discount': child.discount,
                        'gross_wt': child.gross_quantity,
                        'id': child.id,
                        'po_id': po.id,
                        'tm_id': po.id,
                        'tx_id': delivery.id or 0,
                        'program_lot': knitting_table.objects.filter(po_id=po.id).first().lot_no if knitting_table.objects.filter(po_id=po.id).exists() else 0,
                    })

            # ---- Add raw SQL for unmatched po deliveries ---- #
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        y.tm_po_id, y.bag_wt, SUM(y.bag) AS total_bags
                    FROM 
                        po_delivery y
                    WHERE 
                        NOT EXISTS (
                            SELECT 1 
                            FROM tx_yarn_inward s
                            WHERE 
                                s.po_id = y.tm_po_id 
                                AND s.deliver_to = y.party_id
                        )
                    GROUP BY 
                        y.tm_po_id, y.bag_wt
                """)
                unmatched_data = cursor.fetchall()

            # Add to response if needed
            unmatched_pos = [
                {'tm_po_id': row[0], 'bag_wt': row[1], 'total_bags': row[2]}
                for row in unmatched_data
            ]

            return JsonResponse({
                'orders': order_data,
                'total_bag': total_bag_sum,
                'total_quantity': total_quantity_sum,
                'unmatched_deliveries': unmatched_pos
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

 


def load_po_details(request):
    if request.method == "GET":
        po_ids = request.GET.getlist('po_id')  # Get list of selected PO IDs
        print('po-id:', po_ids)

        if not po_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders
            parent_pos = parent_po_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            missing_po_ids = []  # Track POs that don't have a knitting program

            for po in parent_pos:
                # Check if a knitting program exists for this PO
                program = knitting_table.objects.filter(po_id=po.id).first()
                
                if program:
                    program_lot = program.lot_no if program.lot_no else 0
                else:
                    program_lot = 0
                    missing_po_ids.append(po.id)  # Track missing POs

                orders = child_po_table.objects.filter(tm_po_id=po.id)

                for order in orders:
                    product = count_table.objects.filter(id=order.yarn_count_id).first()

                    remaining_bag = order.remaining_bag or 0
                    remaining_quantity = order.remaining_quantity or 0
                    remaining_amount = order.remaining_amount or 0

                    # Omit entries where all three values are zero
                    if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
                        continue

                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "Unknown Product",
                        'tax_value': 5,
                        'bag': remaining_bag,
                        'per_bag': order.per_bag,
                        'quantity': remaining_quantity,
                        'rate': order.rate,
                        'amount': remaining_amount,
                        'id': order.id,
                        'tm_id': order.tm_po_id,
                        'tx_id': order.id,
                        'program_lot': program_lot,
                    })
 
            # If some POs don't have a knitting program, return an error message
            if missing_po_ids:
                return JsonResponse({
                    'error': f'Please create a knitting program for Purchase Order(s): {", ".join(map(str, missing_po_ids))}',
                    'missing_po_ids': missing_po_ids,
                    'orders': order_data
                }, status=400)

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
 
    return JsonResponse({'error': 'Invalid request method.'}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # If using POST requests
def load_yarn_inward_details(request):
    if request.method == "GET":
        po_ids = request.GET.getlist('po_id')  # Correct key format 
        print('PO-IDs:', po_ids)

        if not po_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) are required.'}, status=400)

        try:
            parent_pos = yarn_inward_table.objects.filter(id__in=po_ids)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                orders = sub_yarn_inward_table.objects.filter(tm_id=po.id)
                print('order:',orders)
                for order in orders: 
                    product = product_table.objects.filter(id=order.product_id).first()
                    
                    # # Remaining values
                    # remaining_bag = order.bag 
                    # remaining_quantity = order.quantity 
                    # remaining_amount = order.amount 

                    # if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
                    #     continue  # Skip empty records
                    
                    # amount = remaining_quantity * order.rate  # Fix amount calculation 
                    print('lot-no:',order.lot_no)
                    order_data.append({
                        'product_id': order.product_id,
                        'product': product.name if product else "Unknown Product", 
                        'tax_value': 5,  
                        'bag': order.bag,
                        'per_bag': order.per_bag,   
                        'quantity': order.quantity, 
                        'rate': order.rate,
                        'amount': order.amount,
                        'id': order.id, 
                        'tm_id': order.tm_id,  # Corrected field name
                        'tx_id': order.id,
                        'lot_no':order.lot_no,
                    })

            return JsonResponse({'orders': order_data}, safe=False)  # `safe=False` allows lists

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import OuterRef, Subquery, Q



# @csrf_exempt
# def get_deliver_lists(request):
#     if request.method == 'POST':
#         po_id = request.POST.get('po_list')
#         deliver_ids = request.POST.getlist('deliver_ids[]')  # Accept list of delivery IDs from frontend
#         deliver_ids_json = request.POST.get('deliver_ids', '[]')


#         try:
#             used_deliver_ids = json.loads(deliver_ids_json)
#         except json.JSONDecodeError:
#             used_deliver_ids = []



#         if not po_id:
#             return JsonResponse({"error": "PO ID not provided"}, status=400)


        
#         try:
#             # Basic PO summary from yarn_po_balance_table
#             child_orders = yarn_po_balance_table.objects.filter(
#                 po_id=po_id,
#                 balance_quantity__gt=0
#             ).values('po_id')

#             order_number = parent_po_table.objects.filter(
#                 id__in=child_orders,
#                 status=1
#             ).values('id', 'po_number', 'name').order_by('-id')
#             print('deliver:',child_orders,order_number)


#             totals = yarn_po_balance_table.objects.filter(
#                 po_id=po_id,
#                 balance_quantity__gt=0
#             ).aggregate(
#                 po_bag=Sum('ord_bags'),
#                 po_quantity=Sum('po_quantity'),
#                 inward_bag=Sum('in_bag'),
#                 inward_quantity=Sum('in_quantity'),
#                 balance_quantity=Sum('balance_quantity'),
#                 yarn_count_id=Sum('yarn_count_id')
#             )

#             yarn_count_id = totals['yarn_count_id']
#             balance_bag = (totals['po_bag'] or 0) - (totals['inward_bag'] or 0)
#             sub_po = parent_po_table.objects.filter(id=po_id, status=1).first()


            
#             # excluded = sub_yarn_deliver_table.objects.filter(
#             #     po_id=po_id, status=1
#             # ).values_list('party_id', flat=True)
 
#             # delivery_to = yarn_po_delivery_sum_table.objects.filter(
#             #     po_id=po_id
#             # ).exclude(
#             #     party_id__in=excluded
#             # ).values('party_id', 'party_name', 'yarn_count_id','tx_id')

#             delivery_to_qs = yarn_po_delivery_sum_table.objects.filter( 
#                 po_id=po_id
#             # ).exclude( 
#             #     party_id__in=used_deliver_ids
#             ).values('party_id', 'party_name', 'yarn_count_id', 'tx_id')

#             delivery_to = list(delivery_to_qs)


#             yarn_count_ids = [d['yarn_count_id'] for d in delivery_to if d['yarn_count_id']]
#             program_qs = yarn_program_balance_table.objects.filter(
#                 balance_quantity__gt=0,
#                 yarn_count_id__in=yarn_count_ids
#             ).values_list('program_id', flat=True) 

#             prg_list = list(knitting_table.objects.filter( 
#                 id__in=program_qs, status=1 
#             ).values('id', 'knitting_number', 'name','total_quantity')) 
 
#             # 🧠 Include detailed delivery items if deliver_ids are provided
#             order_data = []
#             if deliver_ids:
#                 parent_pos = parent_po_table.objects.filter(id=po_id, mill_id=sub_po.mill_id)
#                 for po in parent_pos:
#                     deliveries = yarn_po_delivery_table.objects.filter(
#                         tm_po_id=po.id,
#                         party_id__in=deliver_ids,
#                         status=1
#                     )
#                     print('delivery-data:',deliveries)

#                     program = knitting_table.objects.filter(po_id=po.id).first()
#                     program_lot = program.lot_no if program and program.lot_no else 0

#                     for delivery in deliveries:
#                         child = parent_po_table.objects.filter(id=po.id, is_active=1).first()
#                         if not child:
#                             continue

#                         product = count_table.objects.filter(id=child.yarn_count_id).first()

#                         total_bag = child.bag or 0
#                         remaining_bag = delivery.bag or 0
#                         qty = delivery.quantity or 0
#                         remaining_quantity = child.quantity or 0
#                         total_quantity = child.quantity or 0

#                         if remaining_bag == 0 and remaining_quantity == 0:
#                             continue

#                         inward_totals = sub_yarn_inward_table.objects.filter(
#                             po_id=po.id,
#                             party_id=delivery.party_id,
#                             is_active=1
#                         ).aggregate(
#                             inward_bag=Sum('bag'),
#                             inward_quantity=Sum('quantity')
#                         )

#                         inward_bag = inward_totals.get('inward_bag') or 0
#                         inward_quantity = inward_totals.get('inward_quantity') or 0

#                         balance_bag = remaining_bag - inward_bag
#                         balance_quantity = qty - inward_quantity

#                         order_data.append({
#                             'po_bag': child.bag,
#                             'po_quantity': remaining_quantity,
#                             'inward_bag': inward_bag,
#                             'inward_quantity': inward_quantity,
#                             'balance_bag': balance_bag,
#                             'balance_quantity': balance_quantity,
#                             'product_id': child.yarn_count_id,
#                             'product_name': product.name if product else "Unknown Product",
#                             'tax_value': 5,
#                             'bag': remaining_bag,
#                             'per_bag': child.per_bag,
#                             'tx_quantity': qty,
#                             'quantity': remaining_quantity,
#                             'rate': child.rate,
#                             'actual_rate': child.net_rate,
#                             'discount': child.discount,
#                             'gross_wt': child.gross_quantity,
#                             'id': child.id,
#                             'po_id': po.id,
#                             'tm_id': po.id,
#                             'tx_id': delivery.id,
#                             'program_lot': program_lot,
#                             'total_quantity': total_quantity,
#                             'total_bag': total_bag,
#                         })

#             # Final combined response
#             return JsonResponse({
#                 'orders': list(order_number),
#                 'po_bag': balance_bag,
#                 'balance_quantity': float(totals['balance_quantity'] or 0),
#                 'po_quantity': float(totals['balance_quantity'] or 0),
#                 'inward_bag': float(totals['inward_bag'] or 0),
#                 'inward_quantity': float(totals['inward_quantity'] or 0),
#                 'yarn': yarn_count_id,
#                 'bag': balance_bag,
#                 'per_bag': sub_po.per_bag,
#                 'delivery_to': list(delivery_to),
#                 'quantity': float(totals['balance_quantity']),
#                 'program': prg_list,
#                 'order_data': order_data  # <-- merged detailed delivery info
#             })

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({"error": "Invalid request method"}, status=405)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
import json

@csrf_exempt
def get_deliver_lists(request):
    if request.method == 'POST':
        po_id = request.POST.get('po_list')
        deliver_ids = request.POST.getlist('deliver_ids[]')
        deliver_ids_json = request.POST.get('deliver_ids', '[]')

        try:
            used_deliver_ids = json.loads(deliver_ids_json)
        except json.JSONDecodeError:
            used_deliver_ids = []

        if not po_id:
            return JsonResponse({"error": "PO ID not provided"}, status=400)

        try:
            # Basic PO summary
            child_orders = yarn_po_balance_table.objects.filter(
                po_id=po_id, balance_quantity__gt=0
            ).values('po_id')

            order_number = parent_po_table.objects.filter(
                id__in=child_orders, status=1
            ).values('id', 'po_number', 'name').order_by('-id')

            totals = yarn_po_balance_table.objects.filter(
                po_id=po_id, balance_quantity__gt=0
            ).aggregate(
                po_bag=Sum('ord_bags'),
                po_quantity=Sum('po_quantity'),
                inward_bag=Sum('in_bag'),
                inward_quantity=Sum('in_quantity'),
                balance_quantity=Sum('balance_quantity'),
                yarn_count_id=Sum('yarn_count_id')
            )

            po_total_bag = totals['po_bag'] or 0
            yarn_count_id = totals['yarn_count_id']
            balance_bag = (totals['po_bag'] or 0) - (totals['inward_bag'] or 0)
            sub_po = parent_po_table.objects.filter(id=po_id, status=1).first()

            # ✅ Group and sum bags & quantities by party
            delivery_to_qs = yarn_po_delivery_sum_table.objects.filter(
                po_id=po_id
            ).values(
                'party_id', 'party_name', 'yarn_count_id'
            ).annotate(
                total_bag=Sum('po_bag'),
                total_quantity=Sum('po_quantity')
            )

            delivery_to = list(delivery_to_qs)

            yarn_count_ids = [d['yarn_count_id'] for d in delivery_to if d['yarn_count_id']]
            program_qs = yarn_program_balance_table.objects.filter(
                balance_quantity__gt=0,
                yarn_count_id__in=yarn_count_ids
            ).values_list('program_id', flat=True)

            prg_list = list(knitting_table.objects.filter(
                id__in=program_qs, status=1
            ).values('id', 'knitting_number', 'name', 'total_quantity'))

            # Load detailed deliveries if deliver_ids provided
            order_data = []
            if deliver_ids:
                parent_pos = parent_po_table.objects.filter(id=po_id, mill_id=sub_po.mill_id)
                for po in parent_pos:
                    deliveries = yarn_po_delivery_table.objects.filter(
                        tm_po_id=po.id,
                        party_id__in=deliver_ids,
                        status=1
                    )

                    program = knitting_table.objects.filter(po_id=po.id).first()
                    program_lot = program.lot_no if program and program.lot_no else 0

                    for delivery in deliveries:
                        child = parent_po_table.objects.filter(id=po.id, is_active=1).first()
                        if not child:
                            continue

                        product = count_table.objects.filter(id=child.yarn_count_id).first()

                        total_bag = child.bag or 0
                        remaining_bag = delivery.bag or 0
                        qty = delivery.quantity or 0
                        remaining_quantity = child.quantity or 0
                        total_quantity = child.quantity or 0

                        if remaining_bag == 0 and remaining_quantity == 0:
                            continue

                        inward_totals = sub_yarn_inward_table.objects.filter(
                            po_id=po.id,
                            party_id=delivery.party_id,
                            is_active=1
                        ).aggregate(
                            inward_bag=Sum('bag'),
                            inward_quantity=Sum('quantity')
                        )

                        inward_bag = inward_totals.get('inward_bag') or 0
                        inward_quantity = inward_totals.get('inward_quantity') or 0

                        balance_bag = remaining_bag - inward_bag
                        balance_quantity = qty - inward_quantity

                        order_data.append({
                            'po_bag': child.bag,
                            'po_quantity': remaining_quantity,
                            'inward_bag': inward_bag,
                            'inward_quantity': inward_quantity,
                            'balance_bag': balance_bag,
                            'balance_quantity': balance_quantity,
                            'product_id': child.yarn_count_id,
                            'product_name': product.name if product else "Unknown Product",
                            'tax_value': 5,
                            'bag': remaining_bag,
                            'per_bag': child.per_bag,
                            'tx_quantity': qty,
                            'quantity': remaining_quantity,
                            'rate': child.rate,
                            'actual_rate': child.net_rate,
                            'discount': child.discount,
                            'gross_wt': child.gross_quantity,
                            'id': child.id,
                            'po_id': po.id,
                            'tm_id': po.id,
                            'tx_id': delivery.id,
                            'program_lot': program_lot,
                            'total_quantity': total_quantity,
                            'total_bag': total_bag,
                        })

            return JsonResponse({
                'orders': list(order_number),
                'po_bag': po_total_bag,
                'balance_bag': balance_bag,
                'balance_quantity': float(totals['balance_quantity'] or 0),
                'po_quantity': float(totals['balance_quantity'] or 0),
                'inward_bag': float(totals['inward_bag'] or 0),
                'inward_quantity': float(totals['inward_quantity'] or 0),
                'yarn': yarn_count_id,
                'bag': balance_bag,
                'per_bag': sub_po.per_bag,
                'delivery_to': delivery_to,
                'quantity': float(totals['balance_quantity']),
                'program': prg_list,
                'order_data': order_data
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from software_app.models import process_table, party_table  # Ensure models are imported

@csrf_exempt  
def get_process_deliver_lists(request):
    if request.method == "POST":
        process_id = request.POST.get("process_id")
        print("Process-ID:", process_id)  

        if not process_id:
            return JsonResponse({"error": "Process ID is required."}, status=400)

        try:
            process = process_table.objects.filter(id=process_id).first()

            if not process:
                return JsonResponse({"error": "Invalid Process ID."}, status=404)

            # Determine filtering condition
            if process.stage.lower() == "bleaching":
                deliveries = party_table.objects.filter(is_bleaching=1, status=1).values("id", "name")
            elif process.stage.lower() == "knitting":
                deliveries = party_table.objects.filter(is_knitting=1, status=1).values("id", "name")
            elif process.stage.lower() == "dyeing":
                deliveries = party_table.objects.filter(is_dyeing=1, status=1).values("id", "name")
            else:
                deliveries = party_table.objects.none()

            delivery = list(deliveries)  
            print('delivery:',delivery)

            # Ensure response is always JSON for AJAX requests
            return JsonResponse({"deliveries": list(deliveries)}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Only POST is allowed."}, status=400)




from django.db.models import F
from decimal import Decimal



from django.db.models import F
import json
from decimal import Decimal
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render


@csrf_exempt
def check_duplicate_lot_no(request):
    if request.method == "POST":
        lot_no = request.POST.get('lot_no', '').strip().upper()

        # Check if the item already exists in the same group
        exists = yarn_delivery_table.objects.filter(lot_no=lot_no,status=1).exists()
 
        return JsonResponse({"exists": exists})




def add_knitting_delivery(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        try: 
            # Extracting data from the request
            do_date = request.POST.get('delivery_date') 
            supplier_id = request.POST.get('party_id') 
            lot_no = request.POST.get('lot_no')
            tx_inward = request.POST.get('inward_id')
            knitting_prg_id = request.POST.get('prg_id')
            # po_id = request.POST.get('po_id')
            deliver_id = request.POST.get('party_id')
            remarks = request.POST.get('remarks')
            # quantity = request.POST.get('quantity') 
            process_id = request.POST.get('process_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 

            print('data:',chemical_data)
            # Get PO IDs
            po_ids = request.GET.getlist('po_id[]')  
            po_ids_str = ",".join(po_ids)
            tx_inward_str = ",".join([str(i) for i in tx_inward])  # Convert to string

            # Create a new entry in yarn_delivery_table (Parent table)
            material_request = yarn_delivery_table.objects.create(
                company_id=company_id,
                cfyear = 2025,
                delivery_date=do_date,
                party_id=deliver_id,
                program_id=knitting_prg_id,
                inward_id=tx_inward_str,
                lot_no=lot_no,
                total_quantity= 0,#request.POST.get('total_quantity',0.0),
                gross_quantity=0, # request.POST.get('sub_total',0.0),
              
                remarks=remarks,
                created_by=user_id,
                created_on=datetime.now()
            )
            print('material:',material_request)

           
            
            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')  # use Decimal for both if you're working with decimals

            for item in chemical_data:
                inward = item.get('inward_id')
                product_id = item.get('product_id')
                po_id = item.get('po_id')

                # Create sub yarn delivery entry
                sub_yarn_deliver_table.objects.create(
                    company_id=company_id,
                    cfyear=2025,
                    tm_id=material_request.id,
                    po_id = po_id,
                    program_id = knitting_prg_id,

                    party_id=deliver_id,
                    yarn_count_id=product_id,
                    bag=item.get('bag'),
                    inward_id=inward,
                    per_bag=item.get('per_bag'),
                    quantity=item.get('quantity', 0),
                    gross_quantity=item.get('gross_wt', 0),
                    created_by=user_id,
                    created_on=datetime.now()
                )

                # Convert and accumulate
                try:
                    gross = Decimal(str(item.get('gross_wt', 0)))
                except (InvalidOperation, TypeError):
                    gross = Decimal('0.00') 

                try:
                    qty = Decimal(str(item.get('quantity', 0)))
                except (InvalidOperation, TypeError):
                    qty = Decimal('0.00')

                total_gross += gross
                total_quantity += qty
                print('tot:', total_gross, total_quantity)

            material_request.gross_quantity = total_gross
            material_request.total_quantity = total_quantity
            material_request.save()   
                            

            # 🔹 **Update Parent PO Table (`po_table`)**
            print('knt-deliver',True)
            # parent_po_table.objects.filter(id__in=po_ids).update(is_knitting_delivery=1)

            return JsonResponse('yes', safe=False)  # Indicate success

        except Exception as e:
            print(f"❌ Error: {e}")  # Log error for debugging
            return JsonResponse('no', safe=False)  # Indicate failure

    return render(request, 'knitting_deliver/add_knitting_deliver.html')




def add_knitting_delivery_crt(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)



    if request.method == 'POST':
        user_id = request.session['user_id']
        try:
            # Extracting data from the request 
            do_date = request.POST.get('delivery_date') 
            supplier_id = request.POST.get('supplier_id')
            lot_no = request.POST.get('lot_no')
            deliver_id = request.POST.get('deliver_id')
            remarks = request.POST.get('remarks')
            quantity = request.POST.get('quantity')
            process_id = request.POST.get('process_id')
            # chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            print('Decoded chemical_data:', chemical_data)
            
            # Additional debug for other fields
            print('Delivery date:', request.POST.get('delivery_date'))
            print('Supplier ID:', request.POST.get('supplier_id'))
            print('PO IDs:', request.GET.getlist('po_id[]'))

            # Create a new parent_po_table instance
            po_ids = request.GET.getlist('po_id[]')  # Accept multiple PO IDs

            # Convert the list of PO IDs to a comma-separated string
            po_ids_str = ",".join(po_ids)

       

            material_request = yarn_delivery_table.objects.create(
                po_id=po_ids_str, 
                delivery_date = do_date, 
                deliver_to = deliver_id,
                supplier_id=supplier_id,
                quantity=quantity,
                process_id = process_id,
                lot_no=request.POST.get('lot_no'),
                total_quantity=request.POST.get('total_quantity'),
                total_amount=request.POST.get('sub_total'),
                # round_off=request.POST.get('round_off'),
                total_tax=request.POST.get('tax_total'),
                grand_total=request.POST.get('total_payable'),
                remarks=remarks, 
                created_by=user_id,
                created_on=datetime.now()
            ) 
            
            # Iterate through chemical_data and create child_po_table entries
            for chemical in chemical_data:
                # Check if essential fields are present and valid
                if chemical and chemical.get('product_id') and chemical.get('quantity') != 'undefined':
                    print('DATA:', chemical.get('product_id'), chemical.get('quantity'))
                    sub_yarn_deliver_table.objects.create(
                        tm_id=material_request.id,  # ForeignKey to parent_po_table
                        product_id=chemical.get('product_id'),
                        tm_po_id=chemical.get('tm_id'), 
                        bag=chemical.get('bag'),
                        per_bag=chemical.get('per_bag'),
                        quantity=chemical.get('quantity'),  
                        rate=chemical.get('rate'),
                        amount=chemical.get('amount'),

                        created_by=user_id,
                        created_on=datetime.now()
                    )
                else:
                    print('Invalid entry found:', chemical)

            return JsonResponse('yes', safe=False)  # Indicate success
        except Exception as e:
            print(f"Error: {e}")  # Log error for debugging
            return JsonResponse('no', safe=False)  # Indicate failure

    return render(request, 'knitting_deliver/add_knitting_deliver.html')
 
 



def yarn_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        supplier = party_table.objects.filter(is_supplier=1)
        # party = party_table.objects.filter(status=1)
        party = party_table.objects.filter(status=1,is_knitting=1)
        product = product_table.objects.filter(status=1)
        return render(request,'knitting_deliver/delivery_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")


def yarn_delivery_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message}) 



                        # <button type="button" onclick="knitting_print(\'{}\')" class="btn btn-dark btn-xs"><i class="feather icon-printer"></i></button> 
    data = list(yarn_delivery_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="yarn_deliver_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="yarn_deliver_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
            'id': index + 1, 
            'deliver_date': item['delivery_date'].strftime('%d-%m-%Y') if isinstance(item.get('delivery_date'), date) else '-',
            'deliver_no': item['do_number'] if item['do_number'] else'-', 
            'quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'lot_no': item['lot_no'] if item['lot_no'] else'-', 
            'gross_total': item['gross_quantity'] if item['gross_quantity'] else'-', 
            # 'total_tax': item['total_tax'] if item['total_tax'] else'-', 
            # 'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'deliver_to': getSupplier(party_table, item['party_id'] ), 
            'prg':getSupplier(knitting_table, item['program_id'] ), 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
 
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 



@require_POST 
def knitting_print(request):  
    order_id = request.POST.get('id')
    print('print-id:',order_id)
    
    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    total_values = get_object_or_404(yarn_delivery_table, id=order_id)
    customer_value = get_object_or_404(party_table, status=1, id=total_values.deliver_to)
    # customer_value = get_object_or_404(party_table, status=1, id=total_values.supplier_id)
    
    details = (
        sub_yarn_deliver_table.objects.filter(tm_po_id=order_id) 
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
    total_tax = total_values.total_tax

    for detail in details:
        product = get_object_or_404(product_table, id=detail['product_id'])
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
            'rate': detail['rate'],
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
        'total_quantity':total_values.total_quantity,
        'cgst_amount':cgst_amount,
        'sgst_amount':sgst_amount,
        'output_cgst_value': output_cgst,
        'output_sgst_value': output_sgst,
        'total_amount':(total_amount + total_tax), 
        'amount': total_amount,
        'rounded_off' : rounding_difference,
        # 'rounded_off': (total_amount + total_tax).quantize(Decimal('1.00')),
        # 'amount_in_words': num2words((total_amount + total_tax).quantize(Decimal('1.00')), lang='en_IN'),
        # 'total_tax_amount_in_words': num2words(total_tax.quantize(Decimal('1.00')), lang='en_IN'),
    }

    return render(request, 'knitting_deliver/knitting_print.html', context)




import base64
import logging
from django.shortcuts import render, get_object_or_404


logger = logging.getLogger(__name__)  # Use Django logging



def yarn_deliver_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'ID is missing.'})

        # Ensure valid Base64 padding before decoding
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id + '=' * (-len(encoded_id) % 4)).decode()
            material_id = int(decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'Invalid ID format.'})

        # Fetch material instance
        material_instance = sub_yarn_deliver_table.objects.filter(tm_id=material_id).first()

        # If no material found and request is POST, create a new one
        if not material_instance and request.method == "POST":
            product_id = request.POST.get('product_id')
            bag = request.POST.get('bag')
            per_bag = request.POST.get('per_bag')
            quantity = request.POST.get('quantity')
            rate = request.POST.get('rate')
            amount = request.POST.get('amount')

            # Validate required fields before saving
            if product_id and quantity:
                material_instance = sub_yarn_deliver_table.objects.create(
                    tm_id=material_id,
                    bag=bag,
                    per_bag=per_bag,
                    # amount=amount, 
                    # rate=rate, 
                    quantity=quantity
                )
            else:
                return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = yarn_delivery_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name
        supplier_name = "-"
        if parent_stock_instance.party_id:
            supplier = party_table.objects.filter(id=parent_stock_instance.party_id, status=1).first()
            supplier_name = supplier.name if supplier else "-"
        count = count_table.objects.filter(status=1) 
        # Fetch related data
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'product': product_table.objects.filter(status=1), 
            'party': party_table.objects.filter(is_knitting=1, status=1),
            'program': knitting_table.objects.filter(status=1),
            'supplier_id': supplier_name,  
            'supplier': party_table.objects.filter(status=1), 
            'process': process_table.objects.filter(status=1),
            'stage': process_table.objects.filter(stage='Yarn', status=1).first(), 
            'po': parent_po_table.objects.filter(status=1),
            'count':count,
            'inward_lists':yarn_inward_table.objects.filter(status=1)
        }

        return render(request, 'knitting_deliver/update_deliver.html', context)

    except Exception as e:
        logger.error(f"Error in yarn_deliver_edit: {e}") 
        return render(request, 'knitting_deliver/update_deliver.html', {'error_message': f'An unexpected error occurred: {str(e)}'})

 


from django.db.models import Sum




def tx_yarn_deliver_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('deliver-ID:', master_id)

        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_yarn_deliver_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    gross_total = child_data.aggregate(Sum('gross_quantity'))['gross_quantity__sum'] or 0
                   
                    # Fetch process tolerance value
                    process = process_table.objects.filter(stage='yarn').first()  # Ensure `satge='yarn'` is correct
                    process_tolerance = process.tolerance if process else 0

                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0

                    for item in data:
                        index += 1

                        # Calculate deviation
                        # bag_deviation = abs((item['deviation_bag'] or 0) - original_bag)
                        # per_bag_deviation = abs((item['deviation_per_bag'] or 0) - original_per_bag)

                        # # Check if the deviation exceeds process tolerance
                        # show_debit_note = bag_deviation > process_tolerance or per_bag_deviation > process_tolerance

                        # Prepare action buttons
                        # action_buttons = f'''
                        #     <button type="button" onclick="yarn_deliver_detail_edit('{item['id']}')" class="btn btn-primary btn-xs" >
                        #         <i class="feather icon-edit"></i>
                        #     </button>
                        #    <button type="button" onclick="yarn_deliver_delete({{ item.id }}, {{ item.inward_id }}, {{ item.deliver_id }}, {{ item.product_id }})" class="btn btn-danger btn-xs">
                        #         <i class="feather icon-trash-2"></i>
                        #     </button>

                        # '''


                        action_buttons = f'''
                            <button type="button" onclick="yarn_deliver_detail_edit('{item['id']}')" class="btn btn-primary btn-xs">
                                <i class="feather icon-edit"></i>
                            </button>
                            <button type="button" onclick="yarn_deliver_delete('{item['id']}', '{item['inward_id']}', '{item['party_id']}', '{item['yarn_count_id']}', '{item['bag']}' ,'{item['quantity']}')" class="btn btn-danger btn-xs">
                                <i class="feather icon-trash-2"></i>
                            </button>
                        '''




                         # <button type="button" onclick="yarn_deliver_delete('{item['id'],item['inward_id'],item['deliver_id'],item['product_id']}')" class="btn btn-danger btn-xs">
                            #     <i class="feather icon-trash-2"></i>
                            # </button>
                        # if show_debit_note:
                        #     action_buttons += f'''
                        #         <button type="button" onclick="generate_debit_note('{item['id']}')" class="btn btn-info btn-xs">
                        #             <i class="feather icon-file-text"></i> Debit Note
                        #         </button>
                        #         <script>
                        #             document.getElementById('edit_button_{item['id']}').style.display = 'display';
                        #         </script>
                        #     '''

                        # Append formatted data
                        formatted_data.append({
                            'action': action_buttons,
                            'id': index,
                            
                            # 'po_number': getPODeliveryNameById(knitting_table, item['lot_no'], parent_po_table),
                            'product': getItemNameById(count_table, item['yarn_count_id']),
                            # 'deliver_to': getDeliveryNameById(knitting_table, item['lot_no'],party_table),
                            'bag': item['bag'] if item['bag'] else '-',
                            'per_bag': item['per_bag'] if item['per_bag'] else '-',
                            # 'lot_no': item['lot_no'] if item['lot_no'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'gross_wt': item['gross_quantity'] if item['gross_quantity'] else '-',
                            # 'rate': item['rate'] if item['rate'] else '-',
                            # 'amount': item['amount'] if item['amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' 
                            if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                        print(formatted_data)

                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'gross_total': gross_total,
                        # 'total_amount': total_amount,
                        # 'tax_total': tax_total,
                        # 'grand_total': grand_total
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})
 
        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'}) 
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})



 
def tx_yarn_deliver_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        tm_id = request.POST.get('tm_id') 
        product_id = request.POST.get('product_id')
        deliver_id = request.POST.get('deliver_id')
        inward_id = request.POST.get('inward_id') 
        bag = request.POST.get('bag')
        quantity = request.POST.get('quantity')
        try:
            # Update the status field to 0 instead of deleting
            sub_yarn_deliver_table.objects.filter(id=data_id,tm_id=tm_id,inward_id=inward_id,deliver_id=deliver_id,product_id=product_id).update(status=0,is_active=0)
            updated_rows = sub_yarn_inward_table.objects.filter(
                tm_id=inward_id, product_id=product_id, deliver_to=deliver_id
            ).update(
                remaining_bag=F('remaining_bag') + bag,
                remaining_quantity=F('remaining_quantity') + quantity,
            )

            if updated_rows == 0:
                print(f"⚠️ No matching sub_yarn_inward_table record found for tm_id={inward_id}, product_id={product_id}")

            return JsonResponse({'message': 'yes'})
        except sub_yarn_deliver_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    

    

# def getPODeliveryNameById(tbl, lot_no):
#     try:
#         party = tbl.objects.get(lot_no=lot_no).po_id
#     except ObjectDoesNotExist:
#         party = "-"  # Handle the error by providing a default value or appropriate message 
#     return party
 

from django.core.exceptions import ObjectDoesNotExist


def getDeliveryNameById(tbl, lot_no, party_table):
    try:
        # Get the po_id using lot_no from the given table
        po_id = tbl.objects.get(lot_no=lot_no).knitting_id

        # Fetch the po_number from parent_po_table using po_id
        party_name = party_table.objects.get(id=po_id).name
    except ObjectDoesNotExist:
        party_name = "-"  # Default value if not found
        print('party-name:',party_name)
    return party_name



def getPODeliveryNameById(tbl, lot_no, parent_po_table):
    try:
        # Get the po_id using lot_no from the given table
        po_id = tbl.objects.get(lot_no=lot_no).po_id

        # Fetch the po_number from parent_po_table using po_id
        po_number = parent_po_table.objects.get(id=po_id).po_number
    except ObjectDoesNotExist:
        po_number = "-"  # Default value if not found

    return po_number 


def tx_yarn_deliver_list_crt(request):
    if request.method == 'POST':
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)

        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_yarn_deliver_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_amount = child_data.aggregate(Sum('amount'))['amount__sum'] or 0

                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                    parent_data = yarn_delivery_table.objects.filter(id=master_id).first()
                    if parent_data:
                        tax_total = parent_data.total_tax or 0
                        # round_off = parent_data.round_off or 0 
                        grand_total = total_amount + tax_total 
                    else:
                        tax_total  = grand_total = 0
 
                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0
                    for item in data:
                        index += 1
                        # process = process_table.objects.filter(stage__in='yarn').first()
                        # process_tolerance = process.tolerance

                        formatted_data.append({
                            'action': '<button type="button" onclick="yarn_deliver_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="yarn_deliver_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'po_number': getPONameById(parent_po_table, item['tm_po_id']),
                            'product': getItemNameById(product_table, item['product_id']),
                            'bag': item['bag'] if item['bag'] else '-',
                            'per_bag': item['per_bag'] if item['per_bag'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            # 'rate': item['rate'] if item['rate'] else '-',
                            # 'amount': item['amount'] if item['amount'] else '-',
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



def getPONameById(tbl, tm_po_id):
    try:
        party = tbl.objects.get(id=tm_po_id).po_number
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message 
    return party
 


def yarn_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            yarn_delivery_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_yarn_deliver_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except yarn_delivery_table  & sub_yarn_deliver_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


def knitting_delete(request):
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



def yarn_deliver_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            yarn_delivery_table.objects.filter(id=data_id).update(status=0,is_active=0)
            sub_yarn_deliver_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except yarn_delivery_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    

# def delivered_yarn_edit(request):
#     if is_ajax and request.method == "POST": 
#          frm = request.POST
#     data = sub_yarn_deliver_table.objects.filter(id=request.POST.get('id'))
    
#     return JsonResponse(data.values()[0])

from django.http import JsonResponse

def delivered_yarn_edit(request):
    if is_ajax and request.method == "POST": 
        try:
            item_id = request.POST.get('id')
            if not item_id:
                return JsonResponse({'error': 'Missing ID'}, status=400)

            # Get the current sub knitting deliver item
            deliver_data = sub_yarn_deliver_table.objects.filter(id=item_id).first()
            if not deliver_data:
                return JsonResponse({'error': 'Data not found'}, status=404)

            response_data = {
                'id': deliver_data.id,
                'bag': deliver_data.bag, 
                'per_bag': deliver_data.per_bag,
                'quantity': deliver_data.quantity,
                'gross_wt': deliver_data.gross_quantity,
                'tm_po_id': 0,
                'inward_id': deliver_data.inward_id,
                'product_id': deliver_data.yarn_count_id,
            }

            # ✅ Fetch the Original Bag and Per Bag from Inward ID
            inward_id = deliver_data.inward_id
            if inward_id:
                inward_data = sub_yarn_deliver_table.objects.filter(tm_id=inward_id).first()
                print('delivery:',inward_data)
                if inward_data:
                    response_data['original_inward_bag'] = inward_data.bag
                    response_data['original_inward_per_bag'] = inward_data.per_bag
                else:
                    response_data['original_inward_bag'] = None
                    response_data['original_inward_per_bag'] = None
            else:
                response_data['original_inward_bag'] = None
                response_data['original_inward_per_bag'] = None

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def update_knitting_delivery_test26(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_po_id')
        print('update-po-id:', master_id)
 
        product_id = request.POST.get('product_id')
        bag = request.POST.get('bag')
        per_bag = request.POST.get('per_bag')
        quantity = request.POST.get('quantity')
        rate = request.POST.get('rate')
        amount = request.POST.get('amount')
        inward_id = request.POST.get('inward_id')
        deliver_to = request.POST.get('party_id')
 
        # Validate Required Fields
        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Check if the record exists before updating
            child_item = sub_yarn_deliver_table.objects.filter(
                tm_id=master_id, product_id=product_id, inward_id=inward_id,deliver_id=deliver_to
            ).first()
            print('child-:',child_item)

            if child_item: 
                # Update Existing Record
                child_item.bag += bag
                child_item.per_bag = per_bag
                child_item.deviation_bag += bag
                child_item.deviation_per_bag = per_bag
                child_item.quantity += quantity
                # child_item.rate = rate
                # child_item.amount = amount
                child_item.status = 1
                child_item.is_active = 1
                child_item.save()
            else:
                return JsonResponse({'success': False, 'error_message': 'Record not found for update'})

            # ✅ Update `tm_table` with new totals 
            updated_totals = update_tm_table_totals(master_id)

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

 

# def update_knitting_delivery(request):
#     if request.method == 'POST':
#         master_id = request.POST.get('tm_id')
#         print('update-tm-id:', master_id)

#         product_id = request.POST.get('product_id') 
#         lot = request.POST.get('lot_no')

#         # Convert and extract fields safely
#         bag = int(request.POST.get('bag', 0) or 0)
#         per_bag = Decimal(request.POST.get('per_bag', 0) or 0)
#         quantity = Decimal(request.POST.get('quantity', 0) or 0)
#         gross_wt = Decimal(request.POST.get('gross_wt', 0) or 0)
#         rate = Decimal(request.POST.get('rate', 0) or 0)
#         amount = Decimal(request.POST.get('amount', 0) or 0)
#         inward_id = request.POST.get('tx_inward_id')
#         deliver_to = request.POST.get('party_id')
#         # edit_deliver_to = request.POST.get('edit_deliver_to'),
#         print('inward:', inward_id, deliver_to)

#         if not master_id or not product_id:
#             return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

#         try:
#             child_item = sub_yarn_deliver_table.objects.filter(
#                 tm_id=master_id, product_id=product_id, inward_id=inward_id, deliver_id=deliver_to
#             ).first()
#             print('child-:', child_item)

#             if child_item:
#                 # # Update existing
#                 child_item.bag += bag
#                 child_item.per_bag = per_bag
#                 child_item.deviation_bag += bag
#                 child_item.deviation_per_bag = per_bag
#                 child_item.quantity += quantity
#                 child_item.gross_wt += gross_wt
#                 child_item.status = 1
#                 child_item.is_active = 1
#                 child_item.save()

#                  # Update existing
#                 # child_item.bag = bag
#                 # child_item.per_bag = per_bag
#                 # child_item.deviation_bag = bag
#                 # child_item.deviation_per_bag = per_bag
#                 # child_item.quantity = quantity
#                 # child_item.gross_wt = gross_wt
#                 # child_item.status = 1
#                 # child_item.is_active = 1
#                 # child_item.save()


#             else:
#                 # Create new
#                 sub_yarn_deliver_table.objects.create(
                    
#                     tm_id=master_id, 
#                     lot_no=lot,
#                     product_id=product_id,
#                     inward_id=inward_id,
#                     deliver_id=deliver_to,
#                     bag=bag,
#                     per_bag=per_bag,
#                     deviation_bag=bag,
#                     deviation_per_bag=per_bag,
#                     quantity=quantity,
#                     gross_wt=gross_wt,
                    
#                     status=1,
#                     is_active=1,
#                 )
#                 print('✅ New record created')

#             # Update inward stock (handle multiple inward IDs if comma-separated)
#             inward_ids = [int(i) for i in str(inward_id).split(',') if i]

#             for inward in inward_ids:
#                 updated_rows = sub_yarn_inward_table.objects.filter(
#                     tm_id=inward, product_id=product_id, deliver_to=deliver_to
#                 ).update(
#                     remaining_bag=F('remaining_bag') - bag,
#                     remaining_quantity=F('remaining_quantity') - quantity,
#                 )

#                 if updated_rows == 0:
#                     print(f"⚠️ No matching sub_yarn_inward_table record found for tm_id={inward}, product_id={product_id}")

#             # Update totals
#             updated_totals = update_tm_table_totals(master_id)
#             return JsonResponse({'success': True, **updated_totals})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})

#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




from django.http import JsonResponse
from decimal import Decimal
from django.db.models import F

def update_knitting_delivery(request):
    if request.method == 'POST':
        try:
            master_id = request.POST.get('tm_po_id')
            product_id = request.POST.get('product_id')
            lot = request.POST.get('lot_no')
            inward_id = request.POST.get('tx_inward_id')
            deliver_to = request.POST.get('party_id')
            print('values:',master_id, product_id, lot, inward_id, deliver_to)
            if not master_id or not product_id or not inward_id or not deliver_to:
                return JsonResponse({'success': False, 'error_message': 'Missing required fields'})

            bag = int(request.POST.get('bag', 0) or 0)
            per_bag = Decimal(request.POST.get('per_bag', 0) or 0)
            quantity = Decimal(request.POST.get('quantity', 0) or 0)
            gross_wt = Decimal(request.POST.get('gross_wt', 0) or 0)
            # rate = Decimal(request.POST.get('rate', 0) or 0)
            # amount = Decimal(request.POST.get('amount', 0) or 0)

            print(f"Received data: master_id={master_id}, product_id={product_id}, inward_id={inward_id}, party_id={deliver_to}")

            child_item = sub_yarn_deliver_table.objects.filter(
                tm_id=master_id, yarn_count_id=product_id, inward_id=inward_id, party_id=deliver_to
            ).first()

            # if child_item:
            #     # Update existing record
            #     child_item.bag += bag
            #     child_item.per_bag = per_bag
            #     child_item.quantity += quantity
            #     child_item.gross_quantity += gross_wt
            #     child_item.status = 1
            #     child_item.is_active = 1
            #     child_item.save()

            if child_item:
                child_item.bag += bag
                child_item.per_bag = per_bag
                child_item.quantity = Decimal(child_item.quantity or 0) + quantity
                child_item.gross_quantity = Decimal(child_item.gross_quantity or 0) + gross_wt
                child_item.status = 1
                child_item.is_active = 1
                child_item.save()




            else:
                # Create new record
                sub_yarn_deliver_table.objects.create(
                    tm_id=master_id,
                    lot_no=lot,
                    yarn_count_id=product_id,
                    inward_id=inward_id,
                    party_id=deliver_to,
                    bag=bag,
                    per_bag=per_bag,
                    quantity=quantity,
                    gross_quantity=gross_wt,
                    status=1,
                    is_active=1,
                )

            # Update inward stock
            # inward_ids = [int(i) for i in str(inward_id).split(',') if i]
            # for inward in inward_ids:
            #     updated = sub_yarn_inward_table.objects.filter(
            #         tm_id=inward, yarn_count_id=product_id, party_id=deliver_to
            #     ).update(
            #         remaining_bag=F('remaining_bag') - bag,
            #         remaining_quantity=F('remaining_quantity') - quantity,
            #     )
            #     if updated == 0:
            #         print(f"⚠️ No match found in inward table for tm_id={inward}, product_id={product_id}")

            # Update totals
            updated_totals = update_tm_table_totals(master_id)

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_tm_table_totals(master_id): 
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = sub_yarn_deliver_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum']
        gross_quantity = tx.aggregate(Sum('gross_quantity'))['gross_quantity__sum'] or Decimal('0.00')
        # total_amount = tx.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # Convert tax rate to Decimal and perform multiplication safely
        # tax_rate = Decimal('0.05')  # 5% tax
        # tax_total = (total_amount * tax_rate).quantize(Decimal('0.01'))  # Ensure 2 decimal places

        # # Calculate raw total before rounding
        # raw_total = total_amount + tax_total

        # Compute round_off and grand_total
        # rounded_total = Decimal(round(raw_total))  # Ensure Decimal type
        # round_off = (rounded_total - raw_total).quantize(Decimal('0.01'))  # Ensure 2 decimal places
        # grand_total = rounded_total  # Final rounded total

        # Update values in parent_po_table
        yarn_delivery_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            # total_amount=total_amount.quantize(Decimal('0.01')),
            # total_tax=tax_total,
            # round_off=round_off,
            gross_quantity=gross_quantity   
        )

        # Return updated values for frontend update 
        return {
            'total_quantity': total_quantity,
            'gross_quantity':gross_quantity,
            # 'total_amount': total_amount.quantize(Decimal('0.01')),
            # 'tax_total': tax_total,
            # 'round_off': round_off,
            # 'grand_total': grand_total
        }

    except Exception as e:
        return {'error': str(e)}



def debit_note(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        # Get POST data from the request
        frm = request.POST
        
        # Get the 'id' from the POST request to filter the data
        data_id = frm.get('id')
        
        # Query the sub_yarn_deliver_table using the provided ID
        data = sub_yarn_deliver_table.objects.filter(id=data_id).first()  # Use .first() to get the first record or None
        
        if data:
            # If data is found, get associated supplier from the yarn_delivery_table
            supplier = yarn_delivery_table.objects.filter(id=data.tm_id).first()  # Use .first() for safe retrieval
            supplier_id = supplier.supplier_id
            supplier_name = party_table.objects.get(id=supplier_id).name

            # Prepare the response data (you can adjust this based on your actual model fields)
            response_data = {
                'id': data.id, 
                'name':supplier_name,
                'supplier_id': supplier_id,  # Assuming 'name' field exists in supplier model
                'po_id': data.inward_id, 
                'bag':data.bag,
                'per_bag':data.per_bag,
                
            }
            
            # Return the data as a JSON response
            return JsonResponse(response_data, safe=False)
        else:
            return JsonResponse({'error': 'Data not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)





from datetime import datetime
from django.http import JsonResponse
 
def get_financial_year(date):
    """Return the financial year (e.g., 2024 for 2024-25)."""
    if isinstance(date, datetime):  # Ensure it's a datetime object
        return date.year - 1 if date.month < 4 else date.year
    return None  # If date is invalid

def create_debit_note(request):
    if request.method == "POST":  
        user_id = request.session.get('user_id') 
        company_id = request.session.get('company_id') 
        frm = request.POST

        supplier_name = frm.get('name')
        date_str = frm.get('date')  # Date from the form
        supplier_id = frm.get('supplier_id')
        amt = frm.get('amount')
        po_id = frm.get('po_id')
        process = frm.get('process_type')


        if not date_str or not isinstance(date_str, str):
            return JsonResponse({"error": "Invalid date format: Date is missing or not a string"}, status=400)

        try:
            date = datetime.strptime(date_str.strip(), "%d-%m-%y")  # Convert string to datetime
        except ValueError:
            return JsonResponse({"error": "Invalid date format: Expected YYYY-MM-DD"}, status=400)

        #  Get the financial year for `cfy` 
        cfy = get_financial_year(date)

        print('cfy:',cfy)
        if cfy is None:
            return JsonResponse({"error": "Error determining financial year"}, status=400)

        #  Save debit note to the database
        debit = debit_note_table()
        debit.voucher_type='debit'
        debit.supplier_id = supplier_id
        debit.name = supplier_name
        debit.po_id = po_id
        debit.amount = amt
        debit.company_id = company_id
        debit.date = date  # Correctly formatted date
        debit.cfy = 2024  # Store only the financial year
        debit.process_type = process
        debit.debit_status = 'Pending'
        debit.is_complete = 0 
        debit.created_on = datetime.now()
        debit.created_by = user_id
        debit.updated_on = datetime.now()
        debit.updated_by = user_id
        debit.save()

        return JsonResponse({"data": "Success"})
    


def view_voucher(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'voucher/voucher_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")


from django.http import JsonResponse
from datetime import date

def voucher_list_view(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)
    
    # Get the voucher_type from the request
    voucher_type = request.POST.get('voucher_type')
 
    # Build the query based on voucher_type if it's provided
    if voucher_type:
        data = list(debit_note_table.objects.filter(status=1, company_id=company_id,voucher_type=voucher_type).order_by('-id').values())
    else:
        data = list(debit_note_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="voucher_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="voucher_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            'date': item['date'].strftime('%d-%m-%Y') if isinstance(item.get('date'), date) else '-',
            'cfy': item['cfy'] if item['cfy'] else '-', 
            'po_number': getPOValue(parent_po_table, item['po_id']), 
            'supplier_id': getSupplier(party_table, item['supplier_id']), 
            'amount': item['amount'] if item['amount'] else '-', 
            'voucher_type': item['voucher_type'] if item['voucher_type'] else '-', 
            'process': item['process_type'] if item['process_type'] else '-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        } 
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})


def getPOValue(tbl, po_id): 
    print('po-id',po_id)
    try: 
        party = tbl.objects.get(id=po_id).po_number
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message 
    return party
 

def voucher_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = debit_note_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])




def voucher(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'voucher/add_voucher.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")
    


from decimal import Decimal  # For precise financial calculations



# def get_supplier_payable_amount(request):
#     supplier_id = request.GET.get('supplier_id')
#     voucher_type = request.GET.get('voucher_type')
#     po_ids = request.GET.getlist('po_ids[]')  # Get multiple PO selections
     
#     print('Supplier ID:', supplier_id)
#     print('Voucher Type:', voucher_type)
#     print('Selected POs:', po_ids)

#     if voucher_type == 'debit_note':
#         debit = debit_note_table.objects.filter(status=1, supplier_id=supplier_id, is_paid=0)
#         print('Debit Notes:', debit)

#     payable_amount = 0  # Default

#     if supplier_id:
#         orders = yarn_delivery_table.objects.filter(supplier_id=supplier_id, status=1, is_paid=0)

#         # If specific POs are selected, filter by PO IDs
#         if po_ids:
#             orders = orders.filter(po_id__in=po_ids)

#         total_amount = orders.aggregate(grand_total_sum=Sum('grand_total'))['grand_total_sum'] or 0
#         total_paid = orders.aggregate(paid_amount_sum=Sum('paid_amount'))['paid_amount_sum'] or 0
#         payable_amount = max(total_amount - total_paid, 0)

#         print('Total Amount:', total_amount)
#         print('Total Paid:', total_paid)
#         print('Payable Amount:', payable_amount)

#     return JsonResponse({'payable_amount': payable_amount})




# ``````````````` if same tm-id get single time `````````````````

def get_supplier_payable_amount(request):
    supplier_id = request.GET.get('supplier_id')
    voucher_type = request.GET.get('voucher_type')
    po_ids = request.GET.getlist('po_ids[]')  # Selected PO IDs

    print('Supplier ID:', supplier_id)
    print('Voucher Type:', voucher_type)
    print('Selected POs:', po_ids)

    payable_amount = 0  # Default
    tm_ids = []  # Store tm_id values

    if supplier_id:
        # Find matching tm_ids in sub_yarn_deliver_table
        sub_po_ids = sub_yarn_deliver_table.objects.filter(
            tm_po_id__in=po_ids
        ).values_list('tm_id', flat=True)

        tm_ids = sub_po_ids  # Convert queryset to list for JSON response
        print('tm-ids:', tm_ids)  # Debugging
 
        # Get payable orders from yarn_delivery_table
        orders = yarn_delivery_table.objects.filter(
            supplier_id=supplier_id, status=1, is_paid=0
        )
 
        print('sub-value:', orders)

        if tm_ids:
            orders = orders.filter(id__in=tm_ids)  # ✅ Correct filtering

        total_amount = orders.aggregate(grand_total_sum=Sum('grand_total'))['grand_total_sum'] or 0
        total_paid = orders.aggregate(paid_amount_sum=Sum('paid_amount'))['paid_amount_sum'] or 0
        payable_amount = max(total_amount - total_paid, 0)

        print('Total Amount:', total_amount)
        print('Total Paid:', total_paid)
        print('Payable Amount:', payable_amount)

    # ✅ Returning both payable_amount & tm_ids in JSON
    return JsonResponse({'payable_amount': payable_amount, 'tm_ids': tm_ids})




def get_supplier_payable_amount_bk_31last(request):
    supplier_id = request.GET.get('supplier_id')
    voucher_type = request.GET.get('voucher_type')
    po_ids = request.GET.getlist('po_ids[]')  # Selected PO IDs

    print('Supplier ID:', supplier_id)
    print('Voucher Type:', voucher_type)
    print('Selected POs:', po_ids)

    payable_amount = 0  # Default
 
    if supplier_id:
        # Find matching tm_po_ids in sub_yarn_deliver_table
        sub_po_ids = sub_yarn_deliver_table.objects.filter(tm_po_id__in=po_ids).values_list('tm_id', flat=True)
        # tm = sub_yarn_deliver_table.objects.get(tm_po_id__in=po_ids)
        print('tm-id:',sub_po_ids.tm_id)
        # Get payable orders from yarn_delivery_table
        orders = yarn_delivery_table.objects.filter(supplier_id=supplier_id, status=1, is_paid=0)
        # print('orders-id:',orders.id)
        print('sub-value:',orders)
        if sub_po_ids:
            orders = orders.filter(id__in=sub_po_ids)  # Filter by linked POs
            print('orders:',orders)
        total_amount = orders.aggregate(grand_total_sum=Sum('grand_total'))['grand_total_sum'] or 0
        total_paid = orders.aggregate(paid_amount_sum=Sum('paid_amount'))['paid_amount_sum'] or 0
        payable_amount = max(total_amount - total_paid, 0)

        print('Total Amount:', total_amount)
        print('Total Paid:', total_paid)
        print('Payable Amount:', payable_amount)

    return JsonResponse({'payable_amount': payable_amount}) 





def add_voucher_details(request): 
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Voucher", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        user_id = request.session['user_id']
        voucher_type = request.POST.get('type') 
        # po_ids[]
        po = request.POST.get('po_ids')
        print('po-ids',po)
        supplier_id = request.POST.get('supplier')
        check_date_str = request.POST.get('check_date')
        check_number = request.POST.get('check_number')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code') 
        transaction_date = request.POST.get('transaction_date')
        transaction_mode = request.POST.get('transaction_mode')
        amount = request.POST.get('amount')
        payment_mode = request.POST.get('payment_mode')
        remarks = request.POST.get('remarks')
        payment_remarks = request.POST.get('payment_remarks')
        bills = json.loads(request.POST.get('bills', '[]'))

        # Convert amount to Decimal
        try:
            amount = Decimal(amount) if amount else Decimal(0)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid amount provided.'}, status=400)
        try:
            check_date = datetime.fromisoformat(check_date_str) if check_date_str else None
        except ValueError:
            return JsonResponse({'error': 'Invalid check_date format.'}, status=400)


        try:
            company = company_table.objects.get(id=1)
            with transaction.atomic():
                # Create the main voucher
                voucher = Voucher.objects.create(
                    voucher_type=voucher_type,
                    supplier_id=supplier_id if supplier_id else 0,
                    cheque_date=check_date,
                    cheque_number=check_number if check_number else 0,
                    bank_name=bank_name if bank_name else 0,
                    account_number=account_number if account_number else 0,
                    ifsc_code=ifsc_code if ifsc_code else 0,
                    transaction_date=transaction_date if transaction_date else 0,
                    transaction_mode=transaction_mode if transaction_mode else 0,
                    company_id=company.id,
                    amount=amount,
                    payment_mode=payment_mode,
                    remarks=remarks,
                    payment_remarks=payment_remarks,
                    created_by=user_id,
                    created_on=datetime.now(),
                )
                remaining_amount = amount

                print('voucher:',voucher,'amt:',remaining_amount)
                for bill in bills:
                    bill_id = bill.get('bill_id')
                    bill_amount = Decimal(bill.get('bill_amount', 0) or 0)
                    deducted_amount = Decimal(bill.get('deducted_amount', 0) or 0)
                    balance_amount = Decimal(bill.get('balance_amount', 0) or 0)
                    
                    # Deduct the paid amount from the remaining amount
                    remaining_amount -= deducted_amount

                    # Save the child voucher entry
                    child_voucher_table.objects.create(
                        tm_voucher_id=voucher.id,
                        order_number=bill_id,
                        bill_amount=bill_amount,
                        paid_amount=deducted_amount,
                        balance_amount=balance_amount,
                        created_by=user_id,
                        created_on=datetime.now(),
                    )
                    print(child_voucher_table)

                    # Update the correct table based on customer_id or supplier_id
                    # if customer_id:
                    #     # Update sales_order_table
                    #     order_id = bill.get('bill_id')
                    #     if order_id:
                    #         try:
                    #             # Fetch and update the specific order
                    #             order = sales_order_table.objects.get(id=order_id, customer_id=customer_id)
                    #             updated_paid_amount = order.paid_amount + deducted_amount
                    #             is_paid = 1 if updated_paid_amount >= order.total_amount else 0
                    #             order.paid_amount = updated_paid_amount
                    #             order.is_paid = is_paid
                    #             order.updated_by = user_id
                    #             order.updated_on = datetime.now()
                    #             order.save()
                    #         except sales_order_table.DoesNotExist:
                    #             print(f"No order found with id {order_id} for customer {customer_id}")
                    #         except Exception as e:
                    #             print(f"Error updating sales_order_table for order_id {order_id}: {e}")
                    if supplier_id:
                        # Update parent_product_stock_table
                        stock_id =bill.get('bill_id')
                        if stock_id:
                            try:
                                # Fetch and update the specific stock entry
                                stock = yarn_delivery_table.objects.get(id=stock_id, supplier_id=supplier_id)
                                updated_paid_amount = stock.paid_amount + deducted_amount
                                is_paid = 1 if updated_paid_amount >= stock.grand_total else 0
                                stock.paid_amount = updated_paid_amount
                                stock.is_paid = is_paid
                                stock.updated_by = user_id
                                stock.updated_on = datetime.now()
                                stock.save()
                            except yarn_delivery_table.DoesNotExist:
                                print(f"No stock found with id {stock_id} for supplier {supplier_id}")
                            except Exception as e:
                                print(f"Error updating yarn_delivery_table for stock_id {stock_id}: {e}")

                # Create advance entry if remaining amount is positive
                # if remaining_amount > 0:
                #     advance_table.objects.create(
                #         supplier_id=supplier_id,
                #         tm_voucher_id=voucher.id,
                #         advance_amount=remaining_amount,
                #         created_by=user_id,
                #         created_on=datetime.now(),
                #     )

                return JsonResponse({'message': 'Voucher added successfully!'}, status=200)

        except company_table.DoesNotExist:
            return JsonResponse({'error': 'Company record not found.'}, status=404)
        except Exception as e:
            print("Error adding voucher:", e)
            return JsonResponse({'error': 'Failed to add the voucher.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)




def production_delivery_page(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id'] 
        company_id = request.session['company_id'] 
        print('email-company:',company_id)
        email = email_settings_table.objects.filter(status=1,company_id=company_id)
        knitting = yarn_delivery_table.objects.filter(status=1)
        process = process_table.objects.filter(status=1 , stage__in=['bleaching', 'dyeing','inhouse'])
        supplier = party_table.objects.filter(status=1,is_supplier=1)
        return render(request,'production/production_delivery.html',{'email':email,'knitting':knitting,'process':process,'supplier':supplier})
    else:
        return HttpResponseRedirect("/signin") 
    


 
def get_knitting_program_list(request):
    if request.method == 'POST' and 'supplier_id' in request.POST: 
        supplier_id = request.POST['supplier_id'] 
        print('supplier_id:', supplier_id)    

        if supplier_id:
            # Fetch all child purchase orders for the given supplier_id where is_assigned=0
            child_orders = sub_knitting_table.objects.filter(
                tm_id__in=knitting_table.objects.filter(supplier_id=supplier_id,status=1).values('id'),
               
            ).values('tm_id')  # Get the IDs of the parent orders
 
            # Now filter parent purchase orders based on these IDs 
            order_number = knitting_table.objects.filter( 
                id__in=child_orders   
            ).values('id', 'knitting_number').order_by('-id')

            
            # Convert the queryset to a list
            data = list(order_number)
            # print('PO Numbers:', data)
            return JsonResponse(data, safe=False)  # Return the list of purchase orders
         
    return JsonResponse([], safe=False) 



 
def load_knitting_deliver(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')  # Accept multiple PO IDs
        print('po-id:', po_ids)

        if not supplier_id or not po_ids:
            return JsonResponse({'error': 'Supplier ID and Purchase Order ID(s) are required.'}, status=400)

        try:
            # Fetch parent purchase orders for the provided supplier and PO IDs
            parent_pos = knitting_table.objects.filter(id__in=po_ids, supplier_id=supplier_id)

            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            for po in parent_pos:
                # Retrieve child orders linked to each parent PO
                orders = sub_knitting_table.objects.filter(tm_id=po.id)

                for order in orders:
                    product = product_table.objects.filter(id=order.fabric_id).first()
 
                    # Get remaining values
                    # remaining_bag = order.remaining_bag or 0
                    # remaining_quantity = order.remaining_quantity or 0
                    # remaining_amount = order.remaining_amount or 0

                    # 🔹 **Omit entries where all three values are zero**
                    # if remaining_bag == 0 and remaining_quantity == 0 and remaining_amount == 0:
                    #     continue  # Skip this record

                    # Prepare order details
                    order_data.append({
                        'fabric_id': order.fabric_id,
                        'fabric': product.name if product else "Unknown Product", 
                        'tax_value': 5,  
                        'count':order.count,
                        'guage':order.gauge,
                        'dia':order.dia,
                        'tex':order.tex,
                        'rolls':order.rolls,
                        'wt_per_roll':order.wt_per_roll,
                        'quantity':order.quantity, 
                        'total_amount':order.total_amount,
                        'id': order.id, 
                        'tm_id': order.tm_id,
                        'tx_id': order.id,
                    })

            return JsonResponse({'orders': order_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import party_table  # Ensure this is your actual model

@csrf_exempt
def get_supplier_list(request):
    if request.method == 'POST' and 'process_id' in request.POST:
        process_id = request.POST['process_id'].strip().lower()  # Normalize input
        print('Received process_id:', process_id)

        # Mapping process names to their corresponding filter fields
        process_filter_map = {
            "knitting": "is_knitting",
            "bleaching": "is_bleaching",
            "dyeing": "is_dyeing",
            "compacting": "is_compacting",
            "cutting": "is_cutting",
            "stitching": "is_stitching",
            "ironing": "is_ironing"

        }

        # Check if process_id is valid and get the corresponding field name
        if process_id in process_filter_map:
            filter_field = {process_filter_map[process_id]: True}  # Example: {'is_knitting': True}

            # Filter the party_table based on the process
            party = party_table.objects.filter(**filter_field).values('id', 'name').order_by('-id')

            # Convert the queryset to a list and return as JSON response
            return JsonResponse(list(party), safe=False)

        else:
            return JsonResponse({"error": "Invalid process_id"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)






# ```````````````````````````````````` YARN INWARD ```````````````````````````````````` 

def yarn_inward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        # supplier = party_table.objects.filter(Q(is_supplier=1) | Q(is_knitting=1)) 
        supplier = party_table.objects.filter(is_mill=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        last_purchase = yarn_inward_table.objects.order_by('-id').first()
        if last_purchase:
            inward_number = last_purchase.id + 1
        else:  
            inward_number = 1  # Default if no records exist
        po_list = parent_po_table.objects.filter(status=1)  #is_knitting_prg=1,
        program = knitting_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        return render(request,'knitting_deliver/yarn_inward.html',{'inward_number':inward_number,'supplier':supplier,'party':party,'product':product,'po_list':po_list
                                                                   ,'count':count,'program':program})
    else:
        return HttpResponseRedirect("/signin")


def get_knitting_programs(request):
    po_ids = request.GET.getlist('po_ids[]')  # Get selected PO IDs as a list

    programs = knitting_table.objects.filter(po_id__in=po_ids).values('id', 'lot_no')

    return JsonResponse({'programs': list(programs)}, safe=False)



from decimal import Decimal, InvalidOperation


# Safe Decimal conversion function
def safe_decimal(value, default='0.00'):
    try:
        value = str(value).strip()
        return Decimal(value) if value else Decimal(default)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)




def safe_date(value):
    try:
        if value and isinstance(value, str) and value.strip() and value.strip() not in ['-', '–', '—', '“–”']:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        pass
    return None



@csrf_exempt
def add_yarn_inward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            supplier_id = request.POST.get('supplier_id')
            lot_name = request.POST.get('lot_name') or '0'
            remarks = request.POST.get('remarks')
            prg_id = request.POST.get('prg_id')
            po_list = request.POST.get('po_list')
            inward_date = request.POST.get('inward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            # Create Parent Inward Entry
            material_request = yarn_inward_table.objects.create( 
                inward_date=inward_date, 
                party_id=supplier_id, 
                cfyear=2025,
                po_id=po_list,
                # program_id=prg_id or 0, 
                company_id=company_id,
                total_quantity=0,
                gross_quantity=0, 
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')
            po_deliver_map = {}
            inward_required = False

            for chemical in chemical_data:
                is_inward_raw = str(chemical.get('is_inward', '1')).strip()
                is_inward = int(is_inward_raw) if is_inward_raw.isdigit() else 1

                # Track if any row needs delivery
                if is_inward == 0:
                    inward_required = True

                tm_po_id = int(chemical.get('po_id') or 0) 
                deliver_id = chemical.get('deliver_id', 0)
                product_id = chemical.get('product_id')
                # receive_date = safe_date(chemical.get('receive_date'))
                raw_date = chemical.get('receive_date')
                print('r-date:', raw_date)
                receive_date = safe_date(raw_date) if raw_date else None


                receive_no = chemical.get('receive_no')
                delivered_bag = safe_decimal(chemical.get('bag'))
                delivered_quantity = safe_decimal(chemical.get('quantity'))
                gross_wt = safe_decimal(chemical.get('gross_wt'))

                # Store in inward table
                sub_yarn_inward_table.objects.create(
                    tm_id=material_request.id,
                    yarn_count_id=product_id,
                    po_id=po_list,
                
                    receive_no=receive_no or 0,
                    cfyear=2025,
                    company_id = company_id,
                    receive_date=receive_date,
                    party_id = supplier_id, 
                    outward_party_id=deliver_id if deliver_id else 0,
                    bag=delivered_bag,
                    per_bag=chemical.get('per_bag'),
                    quantity=delivered_quantity,
                    gross_quantity=gross_wt,
                    created_by=user_id,
                    created_on=datetime.now()
                )

                # # Mark yarn_po_delivery_table as inwarded only if is_inward == 0
                # if is_inward == 0 and deliver_id:
                #     yarn_po_delivery_table.objects.filter(tm_po_id=tm_po_id, id=deliver_id).update(is_inward=1)

                # # Track totals for summary
                total_gross += gross_wt
                total_quantity += delivered_quantity

                # if tm_po_id not in po_deliver_map:
                #     po_deliver_map[tm_po_id] = {'bags': Decimal('0.00'), 'quantity': Decimal('0.00')}
                # po_deliver_map[tm_po_id]['bags'] += delivered_bag
                # po_deliver_map[tm_po_id]['quantity'] += delivered_quantity

            # Update parent inward totals
            material_request.gross_quantity = total_gross
            material_request.total_quantity = total_quantity 
            material_request.save()
 

            # Create knitting delivery only if any entry had is_inward = 0
            if inward_required:
                try:
                    knitting_delivery = yarn_delivery_table.objects.create(
                        po_id=",".join([str(k) for k in po_deliver_map.keys()]),
                        company_id = company_id,
                        cfyear=2025,
                        delivery_date=inward_date,
                        program_id=prg_id,
                        party_id=supplier_id,
                        inward_id=str(material_request.id),
                        lot_no=lot_name,
                        total_quantity=total_quantity,
                        gross_quantity=total_gross,
                        remarks=remarks,
                        created_by=user_id,
                        created_on=datetime.now()
                    )

                    for chemical in chemical_data:
                        is_inward_raw = str(chemical.get('is_inward', '1')).strip()
                        is_inward = int(is_inward_raw) if is_inward_raw.isdigit() else 1

                        if is_inward == 0:
                            sub_yarn_deliver_table.objects.create( 
                                tm_id=knitting_delivery.id,
                                company_id =company_id,
                                cfyear=2025,
                                party_id=supplier_id,
                                lot_no=lot_name,
                                yarn_count_id=chemical.get('product_id'),
                                bag=safe_decimal(chemical.get('bag')),
                                inward_id=material_request.id,
                                per_bag=chemical.get('per_bag'),
                                gross_quantity=safe_decimal(chemical.get('gross_wt')),
                                quantity=safe_decimal(chemical.get('quantity')),
                                created_by=user_id,
                                created_on=datetime.now()
                            )
                except Exception as ke:
                    print(f"❌ Error creating knitting delivery: {ke}")

            return JsonResponse({'status': 'success', 'message': 'Added Successfully!'})

        # except Exception as e:
        #     print(f"❌ Error: {e}")
        #     return JsonResponse('no', safe=False)
        except Exception as e:
            print(f"❌ Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'knitting_deliver/yarn_inward.html')






def yarn_list(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'knitting_deliver/yarn_inward_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")
    

 

def yarn_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(yarn_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [ 
        {
            'action': '<button type="button" onclick="po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="yarn_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'],item['id']),
                        # <button type="button" onclick="po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_no': item['inward_number'] if item['inward_number'] else'-', 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'supplier_id':getSupplier(party_table, item['party_id'] ), 
            # 'yarn_count': get_yarn_count_by_tm_id(item['id']),
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'total_gross': item['gross_quantity'] if item['gross_quantity'] else'-', 
            # 'tax_total': item['tax_total'] if item['tax_total'] else'-', 
            # 'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            # 'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 
def get_yarn_count_by_tm_id(tm_id):
    try:
        yarn_obj = sub_yarn_inward_table.objects.get(tm_id=tm_id)
        count_obj = count_table.objects.get(id=yarn_obj.yarn_count_id)
        return count_obj.name
    except (sub_yarn_inward_table.DoesNotExist, count_table.DoesNotExist):
        return '-'



def yarn_inward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting 
            # parent_po_table.objects.filter(id=data_id)
            yarn_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_yarn_inward_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except yarn_inward_table & sub_yarn_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




import base64

# def inward_detail_edit(request):
#     try:
#         encoded_id = request.GET.get('id')
#         print('encoded-id:', encoded_id)

#         if not encoded_id:
#             return render(request, 'knitting_deliver/update_yarn_inward.html', {
#                 'error_message': 'ID is missing.'
#             })

#         # Decode the base64-encoded ID 
#         try:
#             decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
#             print('decoded-id:', decoded_id)
#         except (ValueError, TypeError, base64.binascii.Error):
#             return render(request, 'knitting_deliver/update_yarn_inward.html', {
#                 'error_message': 'Invalid ID format.'
#             })

#         # Convert decoded_id to integer
#         material_id = int(decoded_id)
#         print('material:', material_id)

#         # Fetch the parent stock instance
#         parent_stock_instance = yarn_inward_table.objects.filter(id=material_id).first()
#         if not parent_stock_instance:
#             return render(request, 'knitting_deliver/update_yarn_inward.html', {
#                 'error_message': 'Parent stock not found.'
#             })

#         print('inw:', parent_stock_instance.id)

#         # Fetch sub-material instances
#         material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
#         if not material_instances.exists() and request.method == 'GET':
#             return render(request, 'knitting_deliver/update_yarn_inward.html', {
#                 'error_message': 'No material details found.',
#                 'parent_stock_instance': parent_stock_instance,
#                 'decode_id': parent_stock_instance.id,
#             })

#         # Fetch supplier name if available
#         supplier_name = "-"
#         if parent_stock_instance.party_id:
#             supplier_obj = party_table.objects.filter(
#                 id=parent_stock_instance.party_id, status=1
#             ).first()
#             if supplier_obj:
#                 supplier_name = supplier_obj.name

#         # Fetch related dropdown data
#         context = {
#             'material_instances': material_instances,
#             'parent_stock_instance': parent_stock_instance,
#             'party': party_table.objects.filter(is_knitting=1, status=1),
#             'supplier': party_table.objects.filter(status=1),
#             'supplier_id': supplier_name,
#             'count': count_table.objects.filter(status=1),
#             'program': knitting_table.objects.filter(status=1),
#             'decode_id': parent_stock_instance.id,
#         }

#         print('context values:', context)
#         return render(request, 'knitting_deliver/update_yarn_inward.html', context)

#     except Exception as e:
#         print('Exception:', e)
#         return render(request, 'knitting_deliver/update_yarn_inward.html', {
#             'error_message': 'An unexpected error occurred: ' + str(e)
#         })




def inward_detail_edit(request):
    try:
        encoded_id = request.GET.get('id') 
        print('encoded-id:', encoded_id)

        if not encoded_id:
            return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode() 
            print('decoded-id:', decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
        print('material:', material_id)

        # Fetch the parent stock instance
        parent_stock_instance = yarn_inward_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'Parent stock not found.'})

        print('inw:', parent_stock_instance.id)

        # Fetch all sub-material instances (full list, not just one)
        material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        # material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        print('material_instances:', material_instances)





        # If no material instances found, you can create a new one if necessary
        if not material_instances.exists() and request.method == 'GET':
            return render(request, 'knitting_deliver/update_yarn_inward.html', {
                'error_message': 'No material details found.',
                'parent_stock_instance': parent_stock_instance,
                'decode_id': parent_stock_instance.id,
            })



        # if not material_instances.exists():
        #     if request.method == 'POST':
        #         product_id = request.POST.get('product_id') 
        #         bag = request.POST.get('bag')
        #         per_bag = request.POST.get('per_bag')
        #         quantity = request.POST.get('quantity')

        #         if product_id and bag and quantity: 
        #             new_material = sub_yarn_inward_table.objects.create(
        #                 tm_id=material_id,
        #                 yarn_count_id=product_id,
        #                 bag=bag,
        #                 per_bag=per_bag,
        #                 quantity=quantity,
        #             )
        #             material_instances = [new_material]  # create a list with the new entry
        #         else:
        #             return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'Product details are incomplete.'})

        # Fetch supplier name using supplier_id
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try: 
                supplier_obj = party_table.objects.get(id=parent_stock_instance.party_id, status=1)
                supplier_name = supplier_obj.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products, supplier list, party list, and counts
        product = product_table.objects.filter(status=1)
        supplier = party_table.objects.filter(status=1)
        party = party_table.objects.filter(is_knitting=1, status=1)
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)

        # Prepare context for template
        context = {
            'material_instances': material_instances,
            'parent_stock_instance': parent_stock_instance,
            'product': product,
            'party': party,
            'supplier_id': supplier_name,
            'supplier': supplier,
            'count': count,
            'decode_id': parent_stock_instance.id,
            'program':program,
            'po_list': parent_po_table.objects.filter(status=1)
        }

        print('context values:', context)
        return render(request, 'knitting_deliver/update_yarn_inward.html', context)

    except Exception as e:
        print('Exception:', e)
        return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




def update_yarn_inward_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id) 
 
        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_yarn_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    total_gross = child_data.aggregate(Sum('gross_quantity'))['gross_quantity__sum'] or 0
                    print('tot-grs:',total_gross)
                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                  
 
                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0
                    for item in data: 
                        index += 1  
                        formatted_data.append({
                            'action': '<button type="button" onclick="inward_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="inward_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'deliver_to': getItemNameById(party_table, item['party_id']), 
                            'product': getItemNameById(count_table, item['yarn_count_id']), 
                            'bag': item['bag'] if item['bag'] else '-',
                            'per_bag': item['per_bag'] if item['per_bag'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'receive_no': item['receive_no'] if item['receive_no'] else '-',
                            'receive_date': item['receive_date'] if item['receive_date'] else '-',
                            'gross': item['gross_quantity'] if item['gross_quantity'] else '-',
                            # 'rate': item['rate'] if item['rate'] else '-',
                            # 'amount': item['amount'] if item['amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_gross': total_gross,
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})




# def add_or_update_inward_item(request):
#     if request.method == 'POST':
#         user_id = request.session['user_id']
#         company_id = request.session['company_id']

#         master_id = request.POST.get('tm_id')
#         print('tm-id:', master_id)
#         product_id = request.POST.get('product_id')
#         bag = request.POST.get('bag') 
#         per_bag = request.POST.get('per_bag')
#         quantity = request.POST.get('quantity')
#         receive_no = request.POST.get('receive_no')
#         receive_date = request.POST.get('receive_date')
#         gross_wt = request.POST.get('gross_wt')
#         po_id = request.POST.get('po_list', 0)  # Default to 0 if not provided
#         deliver_to = request.POST.get('deliver_to', 0)  # Default to 0 if not provided
#         edit_deliver_to = request.POST.get('supplier_id', 0)  # Default to 0 if not provided
#         print('sup-id:',edit_deliver_to)
#         # Ensure po_id and deliver_to are integers, not empty strings
#         po_id = int(po_id) if po_id else 0
#         deliver_to = int(deliver_to) if deliver_to else 0

#         # Convert string values to Decimal
#         try:
#             bag = Decimal(bag) if bag else Decimal('0') 
#             per_bag = Decimal(per_bag) if per_bag else Decimal('0')
#             quantity = Decimal(quantity) if quantity else Decimal('0')
#             gross_wt = Decimal(gross_wt) if gross_wt else Decimal('0')
#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': f"Invalid number format: {str(e)}"})

#         if not master_id or not product_id:
#             return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

#         try:
#             # Add or update the child table record using tm_id (foreign key), not id
#             child_item, created = sub_yarn_inward_table.objects.update_or_create(
#                 # tm_id=master_id,party_id=edit_deliver_to,receive_no=receive_no,
#                 tm_id=master_id,po_id=po_id,party_id=edit_deliver_to,
#                 yarn_count_id=product_id,
#                 defaults={
#                     'company_id':company_id,
#                     'cfyear':2025,
#                     'bag': bag,
#                     'po_id': po_id,  # Assign po_id, defaulting to 0 if empty
#                     'party_id': edit_deliver_to,  # Assign deliver_to, defaulting to 0 if empty
#                     'per_bag': per_bag,
#                     'quantity': quantity,
#                     'gross_quantity': gross_wt,
#                     # 'receive_no':receive_no,
#                     # 'receive_date':receive_date,
#                     'status': 1,
#                     'is_active': 1,
#                     'created_by': user_id,
#                     'updated_by': user_id,
#                     'created_on': datetime.now(),
#                     'updated_on': datetime.now(),
#                 }
#             )

#             # Mark the delivery entry as inwarded if po_id is present
            
#             # Update master table totals
#             updated_totals = update_tm_table_totals_inward(master_id)

#             if 'error' in updated_totals:
#                 return JsonResponse({'success': False, 'error_message': updated_totals['error']})

#             return JsonResponse({'success': True, **updated_totals})

#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})
 
#     else:
#         return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

from django.db.models import Q

def add_or_update_inward_item(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']

        master_id = request.POST.get('tm_id')
        product_id = request.POST.get('product_id')
        bag = request.POST.get('bag') 
        per_bag = request.POST.get('per_bag')
        quantity = request.POST.get('quantity')
        receive_no = request.POST.get('receive_no')
        receive_date = request.POST.get('receive_date')
        gross_wt = request.POST.get('gross_wt')
        po_id = int(request.POST.get('po_id', 0) or 0)
        deliver_to = int(request.POST.get('deliver_to', 0) or 0)
        supplier_id = int(request.POST.get('supplier_id', 0) or 0)

        try:
            bag = Decimal(bag or '0')
            per_bag = Decimal(per_bag or '0')
            quantity = Decimal(quantity or '0')
            gross_wt = Decimal(gross_wt or '0')
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': f"Invalid number format: {str(e)}"})

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # First, try to get existing record
            existing_item = sub_yarn_inward_table.objects.filter(
                tm_id=master_id,
                party_id=supplier_id,
                po_id=po_id,
                yarn_count_id=product_id
            ).first()

            if existing_item:
                # Update the existing record
                existing_item.bag = bag
                existing_item.per_bag = per_bag
                existing_item.quantity = quantity
                existing_item.gross_quantity = gross_wt
                existing_item.updated_by = user_id
                existing_item.updated_on = datetime.now()
                existing_item.save()
            else:
                # Create a new record
                sub_yarn_inward_table.objects.create(
                    tm_id=master_id,
                    company_id=company_id,
                    cfyear=2025,
                    bag=bag,
                    per_bag=per_bag,
                    quantity=quantity,
                    gross_quantity=gross_wt,
                    po_id=po_id,
                    party_id=supplier_id,
                    yarn_count_id=product_id,
                    status=1,
                    is_active=1,
                    created_by=user_id,
                    updated_by=user_id,
                    created_on=datetime.now(),
                    updated_on=datetime.now(),
                )

            # Update master totals
            updated_totals = update_tm_table_totals_inward(master_id)
            if 'error' in updated_totals:
                return JsonResponse({'success': False, 'error_message': updated_totals['error']})

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

def update_tm_table_totals_inward(master_id):
    try:
        qs = sub_yarn_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        if not qs.exists():
            return {'error': 'No active inward items found.'}

        total_quantity = qs.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
        total_gross = qs.aggregate(Sum('gross_quantity'))['gross_quantity__sum'] or Decimal('0')
        tm = qs.first().tm_id

        yarn_inward_table.objects.filter(id=tm).update(
            total_quantity=total_quantity,
            gross_quantity=total_gross,
        )
 
        return {
            'total_quantity': total_quantity,
            'total_gross': total_gross,
        }

    except Exception as e:
        return {'error': str(e)}


 
def inward_details_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_yarn_inward_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])




def inward_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_yarn_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_yarn_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


# ```````````````````````` package ````````````````````````````````


def package(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        item_group = item_group_table.objects.filter(status=1).order_by('name')

        size = size_table.objects.filter(status=1).order_by('name')
        # quality = accessory_quality_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1).order_by('name')
        fabric = fabric_program_table.objects.filter(status=1).order_by('name')

        style = style_table.objects.filter(status=1).order_by('name')
        return render(request,'master/package.html',{'item_group':item_group,
                                                                       'fabric':fabric,'quality':quality,'size':size,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    




@csrf_exempt
def package_add(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            user_id = request.session['user_id']
            frm = request.POST
            style_id = frm.get('style_id')
            quality_id = frm.get('quality_id')
            size_id = frm.get('size_id')
            per_box = frm.get('per_box')

            # Get fabric_id as comma-separated string
            # fabric_id_str = request.POST.get('fabric_id', '')  # e.g., "21,22"
            # print('fabric_id:', fabric_id_str)
 
            # Parse size data
            # size_data = json.loads(request.POST.get('size_data', '[]'))

            # Create main quality program entry
            quality_entry = quality_program_table.objects.create(
                quality_id=quality_id,
                style_id=style_id,
                size_id=size_id, 
                per_box=per_box,
                created_on=datetime.now(),
                created_by=user_id,
            )

            # # Create size entries
            # for size in size_data:
            #     sub_quality_program_table.objects.create(
            #         tm_id=quality_entry.id,
            #         size_id=size["id"],
            #         position=size["position"],
            #         created_on=datetime.now(),
            #         created_by=user_id,
            #     )

            return JsonResponse({"data": "Success"})

        except Exception as e:
            return JsonResponse({"data": "Error", "error": str(e)})

    return JsonResponse({"data": "Invalid Request"})




def package_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)
    
    # Get all quality_program_table entries with status=1
    data = list(package_table.objects.filter(status=1).order_by('-id').values())

    formatted = []
    
    for index, item in enumerate(data):
        # Fetch all sub_quality_program_table entries for this tm_id
        # sub_items = list(sub_quality_program_table.objects.filter(tm_id=item['id'], status=1).values_list('size_id', flat=True))
        # sub_items = list(
        #     sub_quality_program_table.objects.filter(tm_id=item['id'], status=1)
        #     .order_by('position')
        #     .values_list('size_id', flat=True)
        # )


        # print('sub-items:', sub_items)

        # if sub_items:
        #     # Convert each size ID to name separately
        #     size_names = [getSizeName(size_table, size_id) for size_id in sub_items]
        #     size_names = ", ".join(size_names)  # Combine names into a single string
        # else:
        #     size_names = "-"
             

        # Add the formatted data to the list
        formatted.append({
            'action': '<button type="button" onclick="quality_prg_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="quality_prg_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            'quality': getUOMName(quality_table, item['quality_id']), 
            'style': getUOMName(style_table, item['style_id']), 
            'size': getUOMName(size_table, item['size_id']), 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })
     
    return JsonResponse({'data': formatted}) 




def getMultipleItemFabNameById(fabric_program_model, fabric_id_str):
    if not fabric_id_str:
        return "-"

    ids = [int(fid) for fid in fabric_id_str.split(',') if fid.strip().isdigit()]
    fabric_names = []

    for fabric_program_id in ids:
        try:
            fabric_program = fabric_program_model.objects.get(id=fabric_program_id)
            fabric = fabric_table.objects.get(id=fabric_program.fabric_id)
            fabric_names.append(f"{fabric_program.name} - {fabric.name}")
        except fabric_program_model.DoesNotExist:
            continue 
        except fabric_table.DoesNotExist:
            fabric_names.append(f"{fabric_program.name} - -")
        except Exception:
            continue

    return ", ".join(fabric_names) if fabric_names else "-"



def getSizeName(tbl, uom_id):
    try:
        UOM = tbl.objects.get(id=uom_id).name
    except ObjectDoesNotExist:
        UOM = "-"  # Handle the error by providing a default value or appropriate message
    return UOM


