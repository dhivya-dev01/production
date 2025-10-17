import re
# from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify
from jwt import decode

from accessory.models import *
from accessory.views import getDiaByIds 
from software_app.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest
import bcrypt
from django.db.models import Q
from software_app.forms import *
from employee.models import *
from company.models import *
import datetime

from datetime import datetime
# from datetime import date2
from django.utils import timezone

from django.db.models import Count


from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from software_app.models import *
from company.models import *
from employee.models import *
from user_roles.models import *

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
from software_app.views import getItemNameById, getSupplier, is_ajax, check_user_access

# Create your views here.







def user_roles(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        if user_type == 'Sales Staff' or user_type == 'Admin' or user_type == 'Sales Manager' or user_type == 'Service Manager' or user_type == 'Service Staff' or user_type == 'Operator':
            employee = employee_table.objects.filter(status=1)
            return render(request, 'master/user_roles.html',{'employee':employee})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")



def get_roles(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type') 
        
        if user_type == 'Sales Staff' or user_type == 'Admin' or user_type == 'Sales Manager' or user_type == 'Service Manager' or user_type == 'Service Staff' or user_type == 'Operator':
            roles = AdminRoles.objects.filter(status=1).order_by('sort_order_no')
            print('get-roles:',roles)

        elif user_type == 'technician':           
            roles = AdminRoles.objects.filter(status=1).exclude(name='admin,technician').order_by('sort_order_no')
            print('roles',roles)

        else:
            return JsonResponse({'error': 'Invalid user type'}, status=400)
        
        # Prepare roles data
        # roles_data = [{'id': role.id, 'name': role.module_name} for role in roles]
        roles_data = [{'id': role.id, 'name': role.name} for role in roles]
        print('roles-data:',roles_data)
        return JsonResponse(roles_data, safe=False)

    else:
        return HttpResponseRedirect("/signin")


def view_roles(request):
    role_id = request.POST.get('role_id')  # Getting the role_id from the request 
    print(f"role-id: {role_id}")

    # Fetch all active modules
    all_modules = AdminModules.objects.filter(status=1).values(
        'id', 'name', 'is_create', 'is_read', 'is_update', 'is_delete'
    ).distinct().order_by('sort_order_no')

    formatted = []

    if role_id:  # If a role_id is provided
        privileges = AdminPrivilege.objects.filter(role_id=role_id).values(
            'module', 'is_create', 'is_read', 'is_update', 'is_delete'
        )

        if not privileges.exists():
            print(f"No privileges found for role_id: {role_id}")  # Added this to avoid indentation error

        # Create a dictionary with the privilege data for fast lookup
        privilege_dict = {int(priv['module']): priv for priv in privileges}

        for module in all_modules:
            module_id = module['id']
            # Check if the current module has privileges
            privilege_info = privilege_dict.get(module_id, {})

            formatted.append({
                'module_id': module_id,
                'module': module['name'],
                'is_create': module['is_create'],
                'is_read': module['is_read'],
                'is_update': module['is_update'],
                'is_delete': module['is_delete'],
                # Ensure checkboxes are unchecked by default unless privileges exist
                'create_checked': privilege_info.get('is_create', False),
                'read_checked': privilege_info.get('is_read', False),
                'update_checked': privilege_info.get('is_update', False),
                'delete_checked': privilege_info.get('is_delete', False),
            })

    else:
        # Fallback to default modules when no role is selected, ensure checkboxes are unchecked
        formatted = [
            { 
                'module_id': module['id'],
                'module': module['name'],
                'is_create': module['is_create'],
                'is_read': module['is_read'],
                'is_update': module['is_update'],
                'is_delete': module['is_delete'],
                # Default to unchecked checkboxes when no privileges
                'create_checked': False,
                'read_checked': False,
                'update_checked': False,
                'delete_checked': False,
            }
            for module in all_modules
        ]

    return JsonResponse({'data': formatted})




def add_roles(request):
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "User-privilege", "create")

    if not has_access:
        return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session['user_id']
        user_type = request.session['user_type']
        frm = request.POST
        cid = frm.get('id')
        nm = frm.get('role')
        desc = frm.get('description')
        
        # has_access, error_message = check_user_access(user_type, "Master/User Privilege", "create")

        # if not has_access:
        #     print(f"Access check failed: {error_message}")
        #     return JsonResponse({'message': 'error', 'error_message': error_message})

        role = AdminRoles()
        role.name=nm
        role.descriptions=desc
        role.created_on=timezone.now()
        role.created_by=user_id
        role.updated_on=timezone.now()
        role.updated_by=user_id
        role.save()
        res = "Success"
        return JsonResponse({"data": res})



def privileges_update(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "User-privilege", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        user_type = request.session.get('user_type')
        role_id = request.POST.get('role_id')
        privileges_json = request.POST.get('privileges')
        user_id = request.session['user_id']
        employee = get_object_or_404(employee_table, id=user_id)
        # vendor_id = employee.id 

        privileges = json.loads(privileges_json)

        # has_access, error_message = check_user_access(user_type, "Master/User Privilege", "update")

        # if not has_access:
        #     print(f"Access check failed: {error_message}")
        #     return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            role = AdminRoles.objects.get(id=role_id)
            print('roles:',role)
        except AdminRoles.DoesNotExist:
            return JsonResponse({'error': 'Role with ID {} does not exist'.format(role_id)}, status=404)

        # Clear existing privileges for the role
        AdminPrivilege.objects.filter(role_id=role.id).delete()

        for privilege_data in privileges:
            module_id = str(privilege_data.get('module_id'))  # Convert to string
            is_create = privilege_data.get('create', 0)
            is_read = privilege_data.get('read', 0)
            is_update = privilege_data.get('update', 0)
            is_delete = privilege_data.get('delete', 0)

            privilege = AdminPrivilege.objects.create(
                role_id=role.id,
                module=module_id,
                is_create=is_create,
                is_read=is_read,
                is_update=is_update,
                is_delete=is_delete,
                created_on=timezone.now(),
                updated_on=timezone.now(),
                created_by=user_id,
                updated_by=user_id
            )

        # for privilege_data in privileges:
        #     module_id = privilege_data.get('module_id')  # Get module_id
        #     is_create = privilege_data.get('create', 0)
        #     is_read = privilege_data.get('read', 0)
        #     is_update = privilege_data.get('update', 0)
        #     is_delete = privilege_data.get('delete', 0)

        #     privilege = AdminPrivilege.objects.create(
        #         role_id=role.id,
        #         module=module_id,
        #         is_create=is_create,
        #         is_read=is_read,
        #         is_update=is_update,
        #         is_delete=is_delete,
        #         created_on=timezone.now(),
        #         updated_on=timezone.now(),
        #         created_by=user_id,
        #         updated_by=user_id
        #     )    

            privilege.save()

        response_data = {
            'message': 'Privileges updated successfully for role ID: {}'.format(role_id)
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)



def edit_roles(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
         frm = request.POST
    data = AdminRoles.objects.filter(id=request.POST.get('id'))
    return JsonResponse(data.values()[0])



def update_roles(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "User-privilege", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session['user_id']
        user_type = request.session['user_type']
        
        frm = request.POST
        cid = frm.get('id')
        nm = frm.get('role')
        desc = frm.get('description')

        # has_access, error_message = check_user_access(user_type, "Master/User Privilege", "update")

        # if not has_access:
        #     print(f"Access check failed: {error_message}")
        #     return JsonResponse({'message': 'error', 'error_message': error_message})

        role = AdminRoles.objects.get(id=cid)
        role.name=nm
        role.descriptions=desc
        role.updated_on=timezone.now()
        role.updated_by=user_id
        role.save()
        res = "Success"
        return JsonResponse({"data": res})


def duplicate_add(request):
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
         frm = request.POST
    data = AdminRoles.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def role_duplicate(request):
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "User-privilege", "update")

    if not has_access:
        return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        form_data = request.POST
        original_role_id = form_data.get('duplicate_id')
        new_role_name = form_data.get('role')
        new_role_desc = form_data.get('description')

        # has_access, error_message = check_user_access(user_type, "Master/User Privilege", "update")

        # if not has_access:
        #     print(f"Access check failed: {error_message}")
        #     return JsonResponse({'message': 'error', 'error_message': error_message})
        
        try:
            with transaction.atomic():
                original_role = AdminRoles.objects.get(id=original_role_id)
                
                new_role = AdminRoles.objects.create(
                    name=new_role_name,
                    descriptions=new_role_desc,
                    created_on=original_role.created_on,
                    created_by=original_role.created_by,
                    updated_on=timezone.now(),
                    updated_by=user_id 
                )
                
                original_privileges = AdminPrivilege.objects.filter(role_id=original_role.id)
                for privilege in original_privileges:
                    new_privilege = AdminPrivilege.objects.create(
                        role_id=new_role.id,  # Use new_role.id instead of new_role
                        module=privilege.module,
                        is_create=privilege.is_create,
                        is_read=privilege.is_read,
                        is_update=privilege.is_update,
                        is_delete=privilege.is_delete,
                        created_on=timezone.now(),
                        updated_on=timezone.now(),
                        created_by=user_id,
                        updated_by=user_id
                    )
                
                return JsonResponse({"data": "Success"})
        
        except Exception as e:
            return JsonResponse({"error": str(e)})
    else:
        return JsonResponse({"error": "Invalid request method or not AJAX request"})





def delete_roles(request):
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "User-privilege", "delete")

    if not has_access:
        return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        # has_access, error_message = check_user_access(user_type, "Master/User Privilege", "delete")

        # if not has_access:
        #     print(f"Access check failed: {error_message}")
        #     return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            AdminRoles.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except AdminRoles.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


def refresh_privileges(request):
    if request.method == 'POST':
        role_id = request.POST.get('role_id')

        # Get all active modules
        modules = AdminModules.objects.filter(status=1).values('id')

        # Fetch existing privileges for the given role
        existing_privileges = AdminPrivilege.objects.filter(role_id=role_id).values_list('module', flat=True)
        existing_privileges_set = set(existing_privileges)  # Use a set for efficient look-up

        # Prepare to insert missing privileges
        new_privileges = []
        for module in modules:
            module_id = module['id']
            if module_id not in existing_privileges_set:
                new_privileges.append(AdminPrivilege(
                    role_id=role_id,
                    module_id=module_id,
                    vendor_id=0,  # Set default vendor_id, modify if needed
                    is_create=0,
                    is_read=0,
                    is_update=0,
                    is_delete=0,
                    is_active=1, 
                    status=1,
                    created_on=timezone.now(),
                    updated_on=timezone.now(),
                    created_by=request.session['user_id'],  # Ensure user_id is in the session
                    updated_by=request.session['user_id']
                ))

        # Bulk create missing privileges if any
        if new_privileges:
            AdminPrivilege.objects.bulk_create(new_privileges)

        return JsonResponse({'message': 'Privileges refreshed successfully.'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
