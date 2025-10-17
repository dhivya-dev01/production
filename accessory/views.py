

from os import stat
from django.shortcuts import render

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

# from yarn.views import *
from software_app.models import *
from collections import defaultdict





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
# ````````````````````````````````````````````````````````````````````````````

def item_group(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'accessory/item_group.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    


 
def item_group_list(request):
    company_id = request.session['company_id']  
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(acc_item_group_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="item_group_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="item_group_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'group_type': item['group_type'] if item['group_type'] else'-', 
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



def item_group_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST

        uname = frm.get('name') 
        group_type = frm.get('group_type')

        if acc_item_group_table.objects.filter(name__iexact=uname,group_type=group_type, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Item group with this name already exists.'
            }, status=400)



        fabric = acc_item_group_table()
        fabric.name=uname
        fabric.group_type=group_type
        fabric.created_on=datetime.now()
        fabric.created_by=user_id
        fabric.updated_on=datetime.now()
        fabric.updated_by=user_id
        fabric.save()
        res = "Success"
        return JsonResponse({"data": res})




def item_group_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = acc_item_group_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def item_group_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_id = request.POST.get('id')
        name = request.POST.get('name')
        group_type = request.POST.get('group_type')

        is_active = request.POST.get('is_active')
        
        if acc_item_group_table.objects.filter(name__iexact=name,group_type=group_type, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Item group with this name already exists.'
            }, status=400)

        try:
            fabric = acc_item_group_table.objects.get(id=fabric_id)
            fabric.name = name
            fabric.group_type=group_type
            fabric.is_active = is_active
            fabric.updated_by = user_id
            fabric.updated_on = datetime.now()
            fabric.save()
            return JsonResponse({'message': 'success'})
        except acc_item_group_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'fabric not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def item_group_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "fabric", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            acc_item_group_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except acc_item_group_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})

# ``````````````````````````````````````````` accessory quality ```````````````````````````````````````




def accessory_quality(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'accessory/accessory_quality.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    



def accessory_quality_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(accessory_quality_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="accessory_quality_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="accessory_quality_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'po_name': item['po_name'] if item['po_name'] else'-', 
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})

 


def accessory_quality_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('name')
        po_name = frm.get('po_name')

        if accessory_quality_table.objects.filter(name__iexact=uname, status=1).exists():
            return JsonResponse({ 
                'message': 'error',
                'error_message': 'Acc quality with this name already exists.'
            }, status=400)




        fabric = accessory_quality_table()
        fabric.name=uname
        fabric.po_name=po_name
        fabric.created_on=datetime.now()
        fabric.created_by=user_id
        fabric.updated_on=datetime.now()
        fabric.updated_by=user_id
        fabric.save()
        res = "Success"
        return JsonResponse({"data": res})




def accessory_quality_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = accessory_quality_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def accessory_quality_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_id = request.POST.get('id')
        name = request.POST.get('name')
        po_name = request.POST.get('po_name')

        is_active = request.POST.get('is_active')
        

        if accessory_quality_table.objects.filter(name__iexact=name, status=1).exists():
                return JsonResponse({ 
                    'message': 'error',
                    'error_message': 'Acc quality with this name already exists.'
                }, status=400)


        try:
            fabric = accessory_quality_table.objects.get(id=fabric_id)
            fabric.name = name
            fabric.po_name = po_name
            fabric.is_active = is_active
            fabric.updated_by = user_id
            fabric.updated_on = datetime.now()
            fabric.save()
            return JsonResponse({'message': 'success'})
        except accessory_quality_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'fabric not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def accessory_quality_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "fabric", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            accessory_quality_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except accessory_quality_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


# ``````````````````````````````````````````` accessory Size ```````````````````````````````````````




def accessory_size(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'accessory/accessory_size.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    



def accessory_size_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(accessory_size_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="accessory_size_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="accessory_size_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'po_name': item['po_name'] if item['po_name'] else'-', 
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})

 


def accessory_size_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('name')
        po_name = frm.get('po_name')

        if accessory_size_table.objects.filter(name__iexact=uname, status=1).exists():
            return JsonResponse({ 
                'message': 'error',
                'error_message': 'Acc Size with this name already exists.'
            }, status=400)

 


        fabric = accessory_size_table()
        fabric.name=uname
        fabric.po_name=po_name
        fabric.created_on=datetime.now()
        fabric.created_by=user_id
        fabric.updated_on=datetime.now()
        fabric.updated_by=user_id
        fabric.save()
        res = "Success"
        return JsonResponse({"data": res})




def accessory_size_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = accessory_size_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def accessory_size_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_id = request.POST.get('id')
        name = request.POST.get('name')
        po_name = request.POST.get('po_name')

        is_active = request.POST.get('is_active')
        

        if accessory_size_table.objects.filter(name__iexact=name, status=1).exists():
                return JsonResponse({ 
                    'message': 'error',
                    'error_message': 'Acc size with this name already exists.'
                }, status=400)




        try:
            fabric = accessory_size_table.objects.get(id=fabric_id)
            fabric.name = name
            fabric.po_name = po_name
            fabric.is_active = is_active
            fabric.updated_by = user_id
            fabric.updated_on = datetime.now()
            fabric.save()
            return JsonResponse({'message': 'success'})
        except accessory_size_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'fabric not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def accessory_size_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "fabric", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            accessory_size_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except accessory_size_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



# ``````````````````````````````````````````` accessory Color ```````````````````````````````````````




def accessory_color(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'accessory/accessory_color.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")
    



def accessory_color_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(accessory_color_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="accessory_color_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="accessory_color_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})

 


def accessory_color_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('name')

        
        if accessory_color_table.objects.filter(name__iexact=uname, status=1).exists():
                return JsonResponse({ 
                    'message': 'error',
                    'error_message': 'Acc Color with this name already exists.'
                }, status=400)



        fabric = accessory_color_table()
        fabric.name=uname
        fabric.created_on=datetime.now()
        fabric.created_by=user_id
        fabric.updated_on=datetime.now()
        fabric.updated_by=user_id
        fabric.save()
        res = "Success"
        return JsonResponse({"data": res})




def accessory_color_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = accessory_color_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def accessory_color_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        fabric_id = request.POST.get('id')
        name = request.POST.get('name')

        is_active = request.POST.get('is_active')
        

        if accessory_color_table.objects.filter(name__iexact=name, status=1).exists():
            return JsonResponse({ 
                'message': 'error',
                'error_message': 'Acc Color with this name already exists.'
            }, status=400)




        try:
            fabric = accessory_color_table.objects.get(id=fabric_id)
            fabric.name = name
            fabric.is_active = is_active
            fabric.updated_by = user_id
            fabric.updated_on = datetime.now()
            fabric.save()
            return JsonResponse({'message': 'success'})
        except accessory_color_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'fabric not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def accessory_color_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "fabric", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            accessory_color_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})
        except accessory_color_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


# ````````````````````````````````````````````````` ITEM ```````````````````````````````
def item(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        item_group = acc_item_group_table.objects.filter(status=1).order_by('name')

        size = accessory_size_table.objects.filter(status=1).order_by('name')
        # quality = accessory_quality_table.objects.filter(status=1)
        quality = accessory_quality_table.objects.filter(status=1).order_by('name')

        color = color_table.objects.filter(status=1).order_by('name')
        # color = accessory_color_table.objects.filter(status=1).order_by('name')
        return render(request,'accessory/item.html',{'item_group':item_group,'quality':quality,'size':size,'color':color})
    else:
        return HttpResponseRedirect("/admin")






from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

 
# @csrf_exempt
# def item_list(request):
#     company_id = request.session.get('company_id', None)
#     print('company_id:', company_id)
    
#     items = list(item_table.objects.filter(status=1).order_by('-id').values())

#     formatted = []

#     for item in items:
#         item_id = item['id']

#         # Fetch related sizes and colors
#         sub_size_queryset = sub_size_table.objects.filter(item_id=item_id, status=1)
#         sub_items = sub_item_table.objects.filter(item_id=item_id, status=1)

#         quality_ids = [str(sub_item.quality_id) for sub_item in sub_size_queryset]  
#         quality_ids_str = ",".join(quality_ids) if quality_ids else "-"

#         size_color_map = {}  # Dictionary to store size_id -> list of colors 
#         m_size_color_map = {}  # Dictionary to store size_id -> list of colors 
#         size_names = []  # Store all size names to create a comma-separated string

#         for sub_size in sub_size_queryset:
#             size_id = str(sub_size.size_id) 
#             color_list = sub_size.color_id.split(',') if sub_size.color_id else []
#             master_color_list = sub_size.m_color_id.split(',') if sub_size.m_color_id else []

#             # Fetch size name
#             size_name = getDiaById(accessory_size_table, size_id)
#             if size_name not in size_names:
#                 size_names.append(size_name)

#             # Store colors for this size
#             if size_id in size_color_map:
#                 size_color_map[size_id].extend(color_list)
#             else:
#                 size_color_map[size_id] = color_list

#             if size_id in m_size_color_map:
#                 m_size_color_map[size_id].extend(master_color_list)
#             else:
#                 m_size_color_map[size_id] = master_color_list

#         # Convert collected sizes to a comma-separated string
#         size_names_str = ", ".join(size_names) if size_names else "-"

#         # Convert colors to a unique, comma-separated string
#         all_colors = {color for color_list in size_color_map.values() for color in color_list}  # Get unique colors
#         m_all_colors = {m_color for master_color_list in size_color_map.values() for m_color in master_color_list}  # Get unique colors
#         color_names = getDiaById(accessory_color_table, ','.join(all_colors)) if all_colors else "-"
#         master_color_names = getDiaById(color_table, ','.join(m_all_colors)) if m_all_colors else "-"

#         quality_names = getDiaById(accessory_quality_table, quality_ids_str) if quality_ids else "-"

#         formatted.append({
#             'action': '<button type="button" onclick="item_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
#                       <button type="button" onclick="item_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item_id, item_id),
#             'id': item_id,
#             'item_group': getUOMName(acc_item_group_table, item['item_group_id']), 
#             'quality': quality_names, 
#             'size': size_names_str,  # Comma-separated sizes
#             'color': color_names,  # Unique comma-separated colors
#             'm_color': master_color_names,  # Unique comma-separated colors
#             'name': item['name'] if item['name'] else '-', 
#             'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
#         })

#     return JsonResponse({'data': formatted})

 
@csrf_exempt 
def item_list(request):
    company_id = request.session.get('company_id', None)
    print('company_id:', company_id)
    
    items = list(item_table.objects.filter(status=1).order_by('-id').values())

    formatted = []

    for item in items:
        item_id = item['id']

        # Fetch related sizes and colors
        sub_size_queryset = sub_size_table.objects.filter(item_id=item_id, status=1)
        sub_items = sub_item_table.objects.filter(item_id=item_id, status=1)

        quality_ids = [str(sub_item.quality_id) for sub_item in sub_size_queryset]  
        quality_ids_str = ",".join(quality_ids) if quality_ids else "-"

        size_color_map = {}  # Dictionary to store size_id -> list of colors 
        m_size_color_map = {}  # Dictionary to store size_id -> list of colors 
        size_names = []  # Store all size names to create a comma-separated string

        for sub_size in sub_size_queryset:
            size_id = str(sub_size.size_id) 
            m_size_id = str(sub_size.size_id) 
            color_list = sub_size.color_id.split(',') if sub_size.color_id else []
            master_color_list = sub_size.m_color_id.split(',') if sub_size.m_color_id else []

            # Fetch size name
            size_name = getDiaById(accessory_size_table, size_id)
            if size_name not in size_names:
                size_names.append(size_name)

            # Store colors for this size
            if size_id in size_color_map:
                size_color_map[size_id].extend(color_list)
            else:
                size_color_map[size_id] = color_list

            if m_size_id in m_size_color_map:
                m_size_color_map[m_size_id].extend(master_color_list)
            else:
                m_size_color_map[m_size_id] = master_color_list

        # Convert collected sizes to a comma-separated string
        size_names_str = ", ".join(size_names) if size_names else "-" 
 
        # Convert colors to a unique, comma-separated string
        all_colors = {color for color_list in size_color_map.values() for color in color_list}  # Get unique colors
        m_all_colors = {m_color for master_color_list in m_size_color_map.values() for m_color in master_color_list}  # Get unique colors
        color_names = getDiaById(accessory_color_table, ','.join(all_colors)) if all_colors else "-"
        master_color_names = getDiaById(color_table, ','.join(m_all_colors)) if m_all_colors else "-"

        quality_names = getDiaById(accessory_quality_table, quality_ids_str) if quality_ids else "-"

        formatted.append({
            'action': '<button type="button" onclick="item_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="item_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item_id, item_id),
            'id': item_id,
            'item_group': getUOMName(acc_item_group_table, item['item_group_id']), 
            'quality': quality_names, 
            'size': size_names_str,  # Comma-separated sizes
            'color': color_names,  # Unique comma-separated colors 
            'm_color': master_color_names,  # Unique comma-separated colors
            'name': item['name'] if item['name'] else '-', 
            'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted})


# ````````````````````````````````````````````````````


def item_quality_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)
    
    # Get all active items
    tm_id = request.POST.get('tm_id')

    data = list(sub_item_table.objects.filter(item_id=tm_id,status=1).order_by('-id').values())

    formatted = []
    
    for index, item in enumerate(data):
      
        formatted.append({
            'action': '<button type="button" onclick="quality_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="quality_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': item['id'], 
            'item_id':item['item_id'],
            'quality' : getDiaById(accessory_quality_table,item['quality_id']),
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })
    
    return JsonResponse({'data': formatted})


def item_size_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)
    
    # Get all active items
    tm_id = request.POST.get('tm_id')

    data = list(sub_size_table.objects.filter(item_id=tm_id,status=1).order_by('-id').values())

    formatted = []
    
    for index, item in enumerate(data):
       
        formatted.append({
            'action': '<button type="button" onclick="size_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="size_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': item['id'],  
            'item_id':item['item_id'],
            'quality' : getDiaById(accessory_quality_table,item['quality_id']),
            'size' : getDiaById(accessory_size_table,item['size_id']),
            # 'color' : getDiaById(accessory_color_table,item['color_id']),
            'color' : getDiaById(color_table,item['m_color_id']),
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })
    
    return JsonResponse({'data': formatted})


def edit_quality(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_item_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def delete_quality(request):
    if request.method == "POST":
        quality_id = request.POST.get("id")
        
        try:
            sub_item_table.objects.get(id=quality_id).delete()
            return JsonResponse({"success": True, "message": "Quality deleted successfully"})
        except sub_item_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Quality not found"}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



from django.forms.models import model_to_dict


def edit_size(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST": 
        frm = request.POST
        data = sub_size_table.objects.filter(id=request.POST.get('id')).first()  # Get the first matching record
        # fabric = fabric_table.objects.filter(status=1)  # Assuming you want to return some other data as well
        
        if data:
            # Convert model instance to a dictionary
            data_dict = model_to_dict(data)
            print('datas:',data_dict)
            # fabric_list = list(fabric.values('id', 'name'))

            
            # Return the required data in JSON format
            return JsonResponse({
                'id': data_dict.get('id'),
                'item_id': data_dict.get('item_id'),
                'color_id': data_dict.get('m_color_id'),
                'size_id': data_dict.get('size_id'),
                'quality_id': data_dict.get('quality_id'),
                'is_active': data_dict.get('is_active'),
                # 'fabric': fabric_list 
            })
        else:
            return JsonResponse({'error': 'No matching fabric program found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)





def delete_size(request):
    if request.method == "POST":
        size_id = request.POST.get("id")
        
        try:
            sub_size_table.objects.get(id=size_id).delete()
            return JsonResponse({"success": True, "message": "Size deleted successfully"})
        except sub_size_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Size not found"}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_quality(request):
    if request.method == "POST":
        tm_id = request.POST.get("tm_id")
        quality_id = request.POST.get("quality_id")
        is_active = request.POST.get("is_active")

        if not tm_id or not quality_id:
            return JsonResponse({"success": False, "message": "Missing required fields"})

        # Check if quality already exists with active status
        existing_quality = sub_item_table.objects.filter(item_id=tm_id, quality_id=quality_id, is_active=1).exists()

        if existing_quality:
            return JsonResponse({"success": False, "message": "This quality is already added and active."})

        # Add the new quality
        quality = sub_item_table.objects.create(
            item_id=tm_id,
            quality_id=quality_id,
            is_active=is_active
        )
        return JsonResponse({"success": True, "message": "Quality added successfully", "id": quality.id})

    return JsonResponse({"success": False, "message": "Invalid request"})


@csrf_exempt
def update_quality(request):
    if request.method == "POST":
        quality_id = request.POST.get("id")  # ID of the record being updated
        tm_id = request.POST.get("tm_id")
        new_quality = request.POST.get("quality_id")
        is_active = request.POST.get("is_active")

        try:
            quality = sub_item_table.objects.get(id=quality_id)

            # Check if another record already exists with the same quality_id and active status
            existing_quality = sub_item_table.objects.filter(
                item_id=tm_id,
                quality_id=new_quality,
                is_active=1
            ).exclude(id=quality_id).exists()  # Exclude the current record being updated

            if existing_quality:
                return JsonResponse({"success": False, "message": "This quality already exists and is active."})

            # Update the quality
            quality.quality_id = new_quality
            quality.is_active = is_active
            quality.save()
            return JsonResponse({"success": True, "message": "Quality updated successfully"})

        except sub_item_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Quality not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})




@csrf_exempt
def add_size(request):
    if request.method == "POST":
        tm_id = request.POST.get("tm_id")
        quality_id = request.POST.get("quality_id")
        size_id = request.POST.get("size_id")
        new_color_ids = request.POST.get("color_id")  # Comma-separated colors
        is_active = request.POST.get("is_active", 1)  # Default active if not provided

        if not tm_id or not size_id or not new_color_ids:
            return JsonResponse({"success": False, "message": "Missing required fields"})

        # Get existing entry for this tm_id, quality_id, and size_id
        existing_entry = sub_size_table.objects.filter(
            item_id=tm_id, quality_id=quality_id, size_id=size_id, is_active=1
        ).first()

        if existing_entry:
            # Get already stored colors
            existing_colors = set(existing_entry.color_id.split(',')) if existing_entry.color_id else set()
            new_colors = set(new_color_ids.split(','))

            # Filter out duplicate colors
            unique_new_colors = new_colors - existing_colors


            if not unique_new_colors: 
                return JsonResponse({
                    "success": False,
                    "message": f"All selected colors {', '.join(new_colors)} already exist for this size."
                })

            # Add only the new colors
            updated_colors = existing_colors.union(unique_new_colors)
            existing_entry.color_id = ','.join(updated_colors)
            existing_entry.save()

            return JsonResponse({
                "success": True,
                "message": f"New colors {', '.join(unique_new_colors)} added to existing size.",
                "id": existing_entry.id
            })

        # If no existing entry, create a new record
        size_entry = sub_size_table.objects.create(
            item_id=tm_id, quality_id=quality_id, size_id=size_id, color_id=new_color_ids,m_color_id=new_color_ids, is_active=is_active
        )

        return JsonResponse({"success": True, "message": "Size added successfully", "id": size_entry.id})

    return JsonResponse({"success": False, "message": "Invalid request"})



@csrf_exempt
def update_size_test_2_25(request):
    """
    Update or merge a sub_size_table record.

    Expects POST data:
        id           -> existing sub_size_table PK
        tm_id        -> parent item id
        quality_id   -> related quality id
        size_id      -> new size id
        color_id     -> comma-separated color ids
        is_active    -> optional (defaults to 1)
    """

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    # ---- Extract raw POST data ----
    size_id_raw    = request.POST.get("id")
    tm_id_raw      = request.POST.get("tm_id")
    quality_id_raw = request.POST.get("quality_id")
    new_size_raw   = request.POST.get("size_id")
    new_colors_raw = request.POST.get("color_id")
    
    is_active_raw  = request.POST.get("is_active", "1")  # default is_active to 1

    # ---- Debug logs ----
    print("DEBUG: Received POST data")
    print(f"id: {size_id_raw!r}")
    print(f"tm_id: {tm_id_raw!r}")
    print(f"quality_id: {quality_id_raw!r}")
    print(f"size_id: {new_size_raw!r}")
    print(f"color_id: {new_colors_raw!r}")
    print(f"is_active: {is_active_raw!r}")

    # ---- Validate presence of required fields ----
    missing_fields = []
    if size_id_raw is None: missing_fields.append("id")
    if tm_id_raw is None: missing_fields.append("tm_id")
    if quality_id_raw is None: missing_fields.append("quality_id")
    if new_size_raw is None: missing_fields.append("size_id")
    if new_colors_raw is None: missing_fields.append("color_id")

    if missing_fields:
        return JsonResponse({
            "success": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}",
            "received": {
                "id": size_id_raw,
                "tm_id": tm_id_raw,
                "quality_id": quality_id_raw,
                "size_id": new_size_raw,
                "color_id": new_colors_raw,
                "is_active": is_active_raw,
            }
        })


        # return JsonResponse({
        #     "success": False,
        #     "error": f"Missing required fields: {', '.join(missing_fields)}"
        # })

    # ---- Safe type casting ----
    try:
        size_id    = int(size_id_raw)
        tm_id      = int(tm_id_raw)
        quality_id = int(quality_id_raw)
        new_size   = int(new_size_raw)
        is_active  = int(is_active_raw)
    except (ValueError, TypeError) as e:
        return JsonResponse({
            "success": False,
            "error": f"Invalid numeric value: {str(e)}"
        })

    # ---- Retrieve existing record ----
    try:
        size_record = sub_size_table.objects.get(id=size_id)
    except sub_size_table.DoesNotExist:
        return JsonResponse({"success": False, "message": "Size record not found."})

    # ---- Normalize and clean color IDs ----
    new_colors = {c.strip() for c in new_colors_raw.split(',') if c.strip()}

    # ---- Check for another entry with same tm/quality/size ----
    existing_entry = (
        sub_size_table.objects
        .filter(item_id=tm_id, quality_id=quality_id, size_id=new_size, is_active=1)
        .exclude(id=size_id)
        .first()
    )

    if existing_entry:
        existing_colors = (
            {c.strip() for c in existing_entry.color_id.split(',')}
            if existing_entry.color_id else set()
        )
        duplicate_colors = existing_colors & new_colors

        if duplicate_colors:
            return JsonResponse({
                "success": False,
                "message": f"Colors {', '.join(sorted(duplicate_colors))} already exist for this size."
            })

        # Merge colors into existing record
        merged_colors = existing_colors | new_colors
        color_str = ','.join(sorted(merged_colors))

        existing_entry.color_id = color_str
        existing_entry.m_color_id = color_str
        existing_entry.save()

        return JsonResponse({
            "success": True,
            "message": "Size updated with new colors (merged into existing entry)."
        })

    # ---- Strict duplicate check (same tm/quality/size/colors) ----
    if sub_size_table.objects.filter(
        item_id=tm_id,
        quality_id=quality_id,
        size_id=new_size,
        color_id=new_colors_raw,
        m_color_id=new_colors_raw
    ).exclude(id=size_id).exists():
        return JsonResponse({
            "success": False,
            "message": "Duplicate entry with exact same colors already exists."
        })

    # ---- Proceed with normal update ----
    existing_colors = (
        {c.strip() for c in size_record.m_color_id.split(',')}
        if size_record.m_color_id else set()
    )
    merged_colors = existing_colors | new_colors
    color_str = ','.join(sorted(merged_colors))

    size_record.item_id    = tm_id
    size_record.quality_id = quality_id
    size_record.size_id    = new_size
    size_record.color_id   = color_str
    size_record.m_color_id = color_str
    size_record.is_active  = is_active
    size_record.save()

    return JsonResponse({"success": True, "message": "Size updated successfully."})



@csrf_exempt
def update_size_25(request):
    user_id = request.session.get('user_id')
    """
    Update or merge a sub_size_table record.

    Expects POST data:
        id           -> existing sub_size_table PK
        tm_id        -> parent item id
        quality_id   -> related quality id
        size_id      -> new size id
        color_id     -> comma-separated color ids
        is_active    -> optional (defaults to 1)
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    # ---- Extract raw POST data ----
    # ---- Extract raw POST data with logging ----
    size_id_raw    = request.POST.get("id")
    tm_id_raw      = request.POST.get("tm_id")
    quality_id_raw = request.POST.get("quality_id")
    new_size_raw   = request.POST.get("size_id")
    new_colors_raw = request.POST.get("color_id")
    is_active_raw  = request.POST.get("is_active", "1")

    # DEBUG LOGGING (print to console or log file)
    print("DEBUG: Raw POST values:")
    print(f"id = {size_id_raw!r}") 
    print(f"tm_id = {tm_id_raw!r}")
    print(f"quality_id = {quality_id_raw!r}")
    print(f"size_id = {new_size_raw!r}")
    print(f"color_id = {new_colors_raw!r}")
    print(f"is_active = {is_active_raw!r}")


    # ---- Presence validation ----
    if not all([size_id_raw, tm_id_raw, quality_id_raw, new_size_raw, new_colors_raw]):
        return JsonResponse({
            "success": False,
            "message": "Missing one or more required fields (id, tm_id, quality_id, size_id, color_id)."
        })

    # ---- Safe type casting ----
    try:
        size_id    = int(size_id_raw)
        tm_id      = int(tm_id_raw)
        quality_id = int(quality_id_raw)
        new_size   = int(new_size_raw)
        is_active  = int(is_active_raw)
    except (ValueError, TypeError):
        return JsonResponse({
            "success": False,
            "message": "Numeric fields (id, tm_id, quality_id, size_id, is_active) must be valid integers."
        })

    # ---- Get existing size record ----
    try:
        size_record = sub_size_table.objects.get(id=size_id)
    except sub_size_table.DoesNotExist:
        return JsonResponse({"success": False, "message": "Size record not found."})

    # ---- Normalize color IDs ----
    new_colors = {c.strip() for c in new_colors_raw.split(',') if c.strip()}

    # ---- Check for conflicting entry ----
    existing_entry = (
        sub_size_table.objects
        .filter(item_id=tm_id, quality_id=quality_id, size_id=new_size, is_active=1)
        .exclude(id=size_id)
        .first()
    )

    if existing_entry:
        existing_colors = (
            {c.strip() for c in existing_entry.color_id.split(',')}
            if existing_entry.color_id else set()
        )
        duplicate_colors = existing_colors & new_colors
        if duplicate_colors:
            return JsonResponse({
                "success": False,
                "message": f"Colors {', '.join(sorted(duplicate_colors))} already exist for this size."
            })

        # ---- Merge new unique colors into existing entry ----
        merged = existing_colors | new_colors
        existing_entry.color_id = ','.join(sorted(merged))
        existing_entry.m_color_id = ','.join(sorted(merged))
        existing_entry.save()

        return JsonResponse({
            "success": True,
            "message": "Size updated with new colors (merged into existing entry)."
        })

    # ---- Strict duplicate check ----
    if sub_size_table.objects.filter(
        item_id=tm_id,
        quality_id=quality_id,
        size_id=new_size,
        color_id=new_colors_raw,
        m_color_id=new_colors_raw
    ).exclude(id=size_id).exists():
        return JsonResponse({
            "success": False,
            "message": "Duplicate entry with exact same colors already exists."
        })

    # ---- Proceed with update ----
    existing_colors = (
        {c.strip() for c in size_record.m_color_id.split(',')}
        if size_record.m_color_id else set()
    )
    merged_colors = existing_colors | new_colors

    size_record.item_id    = tm_id
    size_record.quality_id = quality_id
    size_record.size_id    = new_size
    size_record.color_id   = ','.join(sorted(merged_colors))
    size_record.m_color_id = ','.join(sorted(merged_colors))
    size_record.is_active  = is_active  
    size_record.updated_by=user_id
    size_record.updated_on=timezone.now()
    size_record.save()

    return JsonResponse({"success": True, "message": "Size updated successfully."})

 


# @csrf_exempt
# def update_size(request):
#     """
#     Update or merge a sub_size_table record.

#     Expects POST data:
#         id           -> existing sub_size_table PK
#         tm_id        -> parent item id
#         quality_id   -> related quality id
#         size_id      -> new size id
#         color_id     -> comma-separated color ids
#         is_active    -> optional (defaults to 1)
#     """
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Invalid request method."})

#     # ---- Extract raw values ----
#     size_id_raw    = request.POST.get("id")
#     tm_id_raw      = request.POST.get("tm_id")
#     quality_id_raw = request.POST.get("quality_id")
#     new_size_raw   = request.POST.get("size_id")
#     new_colors_raw = request.POST.get("color_id")
#     is_active_raw  = request.POST.get("is_active", "1")   # default string "1"

#     # ---- Basic presence check ----
#     required = [size_id_raw, tm_id_raw, quality_id_raw, new_size_raw, new_colors_raw]
#     if not all(required):
#         return JsonResponse({
#             "success": False,
#             "message": "Missing one or more required fields (id, tm_id, quality_id, size_id, color_id)."
#         })

#     # ---- Safe type casting ----
#     try:
#         size_id    = int(size_id_raw)
#         tm_id      = int(tm_id_raw)
#         quality_id = int(quality_id_raw)
#         new_size   = int(new_size_raw)
#         is_active  = int(is_active_raw)
#     except ValueError:
#         return JsonResponse({"success": False, "message": "Numeric fields contain invalid values."})

#     try:
#         size_record = sub_size_table.objects.get(id=size_id)
#     except sub_size_table.DoesNotExist:
#         return JsonResponse({"success": False, "message": "Size record not found."})

#     # ---- Normalise color ids ----
#     new_colors = {c.strip() for c in new_colors_raw.split(',') if c.strip()}

#     # ---- Check for another entry with same item/quality/size ----
#     existing_entry = (
#         sub_size_table.objects
#         .filter(item_id=tm_id, quality_id=quality_id, size_id=new_size, is_active=1)
#         .exclude(id=size_id)
#         .first()
#     )

#     if existing_entry:
#         existing_colors = (
#             {c.strip() for c in existing_entry.color_id.split(',')}
#             if existing_entry.color_id else set()
#         )
#         duplicate_colors = existing_colors & new_colors
#         if duplicate_colors:
#             return JsonResponse({
#                 "success": False,
#                 "message": f"Colors {', '.join(sorted(duplicate_colors))} already exist for this size."
#             })

#         # merge new unique colors into existing record
#         merged = existing_colors | new_colors
#         existing_entry.color_id = ','.join(sorted(merged))
#         existing_entry.m_color_id = ','.join(sorted(merged))
#         existing_entry.save()
#         return JsonResponse({"success": True, "message": "Size updated with new colors."})

#     # ---- Strict duplicate check for exact match ----
#     if sub_size_table.objects.filter(
#         item_id=tm_id,
#         quality_id=quality_id,
#         size_id=new_size,
#         color_id=new_colors_raw,
#         m_color_id=new_colors_raw
#     ).exclude(id=size_id).exists():
#         return JsonResponse({"success": False, "message": "Duplicate entry not allowed."})

#     # ---- Normal update ----
#     existing_colors = (
#         {c.strip() for c in size_record.m_color_id.split(',')}
#         if size_record.m_color_id else set()
#     )
#     merged_colors = existing_colors | new_colors

#     size_record.item_id    = tm_id
#     size_record.quality_id = quality_id
#     size_record.size_id    = new_size
#     size_record.color_id   = ','.join(sorted(merged_colors))
#     size_record.m_color_id = ','.join(sorted(merged_colors))
#     size_record.is_active  = is_active
#     size_record.save()
 
#     return JsonResponse({"success": True, "message": "Size updated successfully."})

 
@csrf_exempt
def update_sizes(request):
    print('requests')
    if request.method == "POST":
        size_id = request.POST.get("id")  # ID of the record being updated
        print('size-id:',size_id)
        tm_id = request.POST.get("tm_id")
        print('tm-id:',tm_id)

        quality_id = request.POST.get("quality_id")
        print('quality-id:',quality_id)

        new_size = request.POST.get("size_id")
        print('new_size-id:',new_size)  

        new_color_ids = request.POST.get("color_id")  # Comma-separated colors
        print('new_color-id:',new_color_ids)

        is_active = request.POST.get("is_active", 1)

        try:
            size_record = sub_size_table.objects.get(id=size_id)

            # Check if another entry exists with the same quality_id and size_id
            existing_entry = sub_size_table.objects.filter(
                item_id=tm_id, quality_id=quality_id, size_id=new_size, is_active=1
            ).exclude(id=size_id).first()

            new_colors = {color.strip() for color in new_color_ids.split(',')}

            if existing_entry:
                existing_colors = {color.strip() for color in existing_entry.color_id.split(',')} if existing_entry.color_id else set()
                duplicate_colors = existing_colors.intersection(new_colors)

                if duplicate_colors:
                    return JsonResponse({
                        "success": False,
                        "message": f"Colors {', '.join(duplicate_colors)} already exist for this size."
                    })

                # Append new unique colors to the existing entry
                updated_colors = existing_colors.union(new_colors)
                existing_entry.color_id = ','.join(sorted(updated_colors))
                existing_entry.m_color_id = ','.join(sorted(updated_colors))
                existing_entry.save()

                return JsonResponse({"success": True, "message": "Size updated with new colors."})

            # 🚨 STRICT DUPLICATE CHECK: Avoid updating to a duplicate entry
            if sub_size_table.objects.filter(item_id=tm_id, quality_id=quality_id, size_id=new_size, color_id=new_color_ids, m_color_id=new_color_ids).exclude(id=size_id).exists():
                return JsonResponse({"success": False, "message": "Duplicate entry not allowed."})

            # If no conflicting record, update normally
            # existing_colors = {color.strip() for color in size_record.color_id.split(',')} if size_record.color_id else set()
            existing_colors = {color.strip() for color in size_record.m_color_id.split(',')} if size_record.m_color_id else set()
            updated_colors = existing_colors.union(new_colors)

            size_record.quality_id = quality_id
            size_record.size_id = new_size
            size_record.color_id = ','.join(sorted(updated_colors))  # Store in sorted order
            size_record.m_color_id = ','.join(sorted(updated_colors))  # Store in sorted order
            size_record.is_active = is_active
            size_record.save()

            return JsonResponse({"success": True, "message": "Size updated successfully"})

        except sub_size_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Size not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})





@csrf_exempt
def update_size(request):
    print('requests')
    if request.method == "POST":
        size_id = request.POST.get("id")  # ID of the record being updated
        print('size-id:',size_id)
        tm_id = request.POST.get("tm_id")
        print('tm-id:',tm_id)

        quality_id = request.POST.get("quality_id")
        print('quality-id:',quality_id)

        new_size = request.POST.get("size_id")
        print('new_size-id:',new_size)  

        new_color_ids = request.POST.get("color_id")  # Comma-separated colors
        print('new_color-id:',new_color_ids)

        is_active = request.POST.get("is_active", 1)

        try:
            size_record = sub_size_table.objects.get(id=size_id)

            # Check if another entry exists with the same quality_id and size_id
            existing_entry = sub_size_table.objects.filter(
                item_id=tm_id, quality_id=quality_id, size_id=new_size, is_active=1
            ).exclude(id=size_id).first()

            new_colors = {color.strip() for color in new_color_ids.split(',')}

            if existing_entry:
                existing_colors = {color.strip() for color in existing_entry.color_id.split(',')} if existing_entry.color_id else set()
                duplicate_colors = existing_colors.intersection(new_colors)

                if duplicate_colors:
                    return JsonResponse({
                        "success": False,
                        "message": f"Colors {', '.join(duplicate_colors)} already exist for this size."
                    })

                # Append new unique colors to the existing entry
                updated_colors = existing_colors.union(new_colors)
                existing_entry.color_id = ','.join(sorted(updated_colors))
                existing_entry.m_color_id = ','.join(sorted(updated_colors))
                existing_entry.save()

                return JsonResponse({"success": True, "message": "Size updated with new colors."})

            # 🚨 STRICT DUPLICATE CHECK: Avoid updating to a duplicate entry
            if sub_size_table.objects.filter(item_id=tm_id, quality_id=quality_id, size_id=new_size, color_id=new_color_ids, m_color_id=new_color_ids).exclude(id=size_id).exists():
                return JsonResponse({"success": False, "message": "Duplicate entry not allowed."})

            # If no conflicting record, update normally
            # existing_colors = {color.strip() for color in size_record.color_id.split(',')} if size_record.color_id else set()
            existing_colors = {color.strip() for color in size_record.m_color_id.split(',')} if size_record.m_color_id else set()
            updated_colors = existing_colors.union(new_colors)

            size_record.quality_id = quality_id
            size_record.size_id = new_size
            size_record.color_id = ','.join(sorted(updated_colors))  # Store in sorted order
            size_record.m_color_id = ','.join(sorted(updated_colors))  # Store in sorted order
            size_record.is_active = is_active
            size_record.save()

            return JsonResponse({"success": True, "message": "Size updated successfully"})

        except sub_size_table.DoesNotExist:
            return JsonResponse({"success": False, "message": "Size not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})



def getDiaById(tbl, dia_id):
    # print('dia-id:', dia_id)
    try:
        # Split the comma-separated string and convert it into a list of integers
        dia_ids = [int(d) for d in str(dia_id).split(',') if d.isdigit()]

        # Fetch dia names for the given list of IDs
        dia_list = tbl.objects.filter(id__in=dia_ids, status=1).values_list('name', flat=True)

        if dia_list:
            return ", ".join(map(str, dia_list))  # Convert list to a comma-separated string
        else:
            return "-"
    except Exception as e:
        # print(f"Error fetching dia for dia_id {dia_id}: {e}")
        return "-"

 

def getUOMName(tbl, uom_id):
    try:
        UOM = tbl.objects.get(id=uom_id).name
    except ObjectDoesNotExist:
        UOM = "-"  # Handle the error by providing a default value or appropriate message
    return UOM


def get_size(request): 
    quality_id = request.GET.get('quality_id')    
    size = size_table.objects.filter(quality_id=quality_id).values('id', 'name')  

    return JsonResponse({"size": list(size)})



@csrf_exempt
def item_add(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        frm = request.POST

        # Normalize name: trim, collapse spaces, uppercase
        def normalize_name(name):
            return ' '.join(name.strip().upper().split())

        raw_name = frm.get('name', '')
        uname = normalize_name(raw_name)
        item_group = frm.get('item_group_id')

        # Check if normalized name already exists in the same item group
        existing_items = item_table.objects.filter(item_group_id=item_group, status=1)
        for item in existing_items:
            if normalize_name(item.name) == uname:
                return JsonResponse({
                    'message': 'error',
                    'error_message': 'Item group with this name already exists.'
                }, status=400)

        # Parse quality and size data
        quality_data = json.loads(frm.get('quality_data', '[]'))
        size_data = json.loads(frm.get('size_data', '[]'))

        # Step 1: Create the item
        fabric = item_table.objects.create(
            name=uname,
            item_group_id=item_group,
            created_on=datetime.now(),
            created_by=user_id
        )

        # Step 2: Add qualities
        for quality in quality_data:
            sub_item_table.objects.create(
                item_id=fabric.id,
                quality_id=quality["id"],
                created_on=datetime.now(),
                created_by=user_id
            )

        # Step 3: Add sizes with merged colors
        size_dict = defaultdict(set)
        for size in size_data:
            size_id = size["size_id"]
            quality_id = size["quality_id"]
            color_id = size["color_id"]
            size_dict[size_id].add(color_id)

        for size_id, color_ids in size_dict.items():
            color_str = ",".join(str(c) for c in color_ids)
            sub_size_table.objects.create(
                item_id=fabric.id,
                quality_id=quality_id,
                size_id=size_id,
                m_color_id=color_str,
                created_on=datetime.now(),
                created_by=user_id
            )

        return JsonResponse({"data": "Success"})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)



def item_edit(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        item_id = request.POST.get('id')

        # Fetch the item from item_table
        item_data = item_table.objects.filter(id=item_id).values().first() 

        # Check if the item_data is not empty
        if not item_data:
            return JsonResponse({'message': 'error', 'error_message': 'Item not found'}, status=404)

        # Initialize variables
        quality_ids = set()  # Using a set to prevent duplicates
        size_ids = []
        color_ids = set()
        quality_names = []
        size_names = []
        color_names = []
        size_color_mapping = {}  # ✅ Fix: To maintain size-color mapping


        sub_item_data = sub_item_table.objects.filter(item_id=item_id)

        # Fetch associated sub_size data (all matching sizes)
        sub_size_data = sub_size_table.objects.filter(item_id=item_id)


        for sub_item in sub_item_data:
            if sub_item.quality_id:
                quality_ids.update(sub_item.quality_id.split(','))  # Collect all quality IDs

        # Process size and color IDs
        for size_entry in sub_size_data:
            size_id = size_entry.size_id
            size_ids.append(size_id)

            if size_entry.color_id:
                color_list = size_entry.m_color_id.split(',')
                color_ids.update(color_list)  # Collect all color IDs

                # ✅ Store mapping between size and colors
                if size_id in size_color_mapping:
                    size_color_mapping[size_id].extend(color_list)
                else:
                    size_color_mapping[size_id] = color_list


        quality_ids = sorted(quality_ids)

        # Convert sets back to sorted lists
        color_ids = sorted(color_ids)

        # Fetch names using the helper function
        quality_names = getDiaByIds(accessory_quality_table, quality_ids) if quality_ids else []

        size_names = getDiaByIds(accessory_size_table, size_ids) if size_ids else []
        color_names = getDiaByIds(color_table, color_ids) if color_ids else []

        # Fetch available size and color data for dropdown
        size = list(accessory_size_table.objects.filter(status=1).order_by('name').values('id', 'name'))
        color = list(color_table.objects.filter(status=1).order_by('name').values('id', 'name'))

        # Prepare the response data
        response_data = {
            'item_id': item_data['id'], 
            'name': item_data['name'],
            'item_group_id': item_data['item_group_id'],
            # 'quality_ids': quality_ids,  # Now correctly lists all quality IDs
            # 'quality_names': quality_names, 
            # 'size_ids': size_ids,
            # 'color_ids': color_ids,
            # 'size_names': size_names,
            # 'color_names': color_names,
            # 'size_color_mapping': size_color_mapping,  # ✅ Fix: Send proper mapping
            'is_active': item_data['is_active'],
            'size': size,
            'color': color
        }

        return JsonResponse(response_data)

# # Helper function to get names by IDs from the relevant table
# def getDiaByIds(model, ids_list):
#     # Convert the ids_list to a list of integers
#     ids = [int(id) for id in ids_list if id.isdigit()]
    
#     # Fetch the objects corresponding to the ids
#     items = model.objects.filter(id__in=ids)
    
#     # Create a dictionary with id as key and name as value
#     id_name_dict = {str(item.id): item.name for item in items}
    
#     # Create a list of names based on the ids
#     names = [id_name_dict.get(id, '-') for id in ids_list]  # Default to '-' if name not found
    
#     return names

def getDiaByIds(model, ids_list):
    ids = []

    for id in ids_list:
        # Convert only if it's a string and isdigit
        if isinstance(id, str) and id.isdigit():
            ids.append(int(id))
        elif isinstance(id, int):
            ids.append(id)
    
    # Fetch the objects corresponding to the ids 
    items = model.objects.filter(id__in=ids)

    # Create a dictionary with id as key and name as value
    id_name_dict = {str(item.id): item.name for item in items}

    # Create a list of names based on the original ids_list (for consistent ordering)
    names = [id_name_dict.get(str(id), '-') for id in ids_list]

    return names


@csrf_exempt
def check_duplicate_item(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip().upper()
        item_group_id = request.POST.get('item_group_id')

        # Check if the item already exists in the same group
        exists = item_table.objects.filter(name=name, item_group_id=item_group_id).exists()
 
        return JsonResponse({"exists": exists})







@csrf_exempt
def item_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        try:
            user_id = request.session.get('user_id')  # Get logged-in user ID
            frm = request.POST

            item_id = frm.get('id')  # Item being updated
            new_name = frm.get('name').strip().upper()  # Convert to uppercase
            item_group = frm.get('item_group_id')  # Accessory Group ID
            is_active = str(frm.get('is_active', "0")).strip() == "1"  # Convert to boolean

            # Fetch the existing item
            fabric = item_table.objects.filter(id=item_id).first()
            if not fabric:
                return JsonResponse({"message": "Item not found"}, status=404)

            old_name = fabric.name.strip().upper()  # Existing name (uppercase)

            # 🔹 **Check for duplicate only if the name has changed**
            if new_name != old_name:
                if item_table.objects.filter(name=new_name, item_group_id=item_group,status=1).exclude(id=item_id).exists():
                    return JsonResponse({"error": "This name already exists in the selected item group."}, status=400)

            # 🔹 **Update item details**
            fabric.name = new_name.upper()
            fabric.item_group_id = item_group
            fabric.is_active = is_active
            fabric.updated_on = datetime.now()
            fabric.updated_by = user_id
            fabric.save()

            return JsonResponse({"message": "success"})

        except Exception as e:
            return JsonResponse({"message": "error", "error": str(e)}, status=500)



def item_delete(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        try: 
            # Update the status field to 0 instead of deleting 
            item_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_size_table.objects.filter(item_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except item_table  & sub_size_table.DoesNotExist: 
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})
 
# ```````````````````````````````````````````` STYLE ````````````````````````````````

def style(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        quality = quality_table.objects.filter(status=1)

        return render(request,'style.html',{'quality':quality})
    else:
        return HttpResponseRedirect("/admin")



def style_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(style_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="style_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="style_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})

from django.utils.timezone import now  # preferred over datetime.now()

from django.http import JsonResponse
from django.utils.timezone import now

def style_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        user_id = request.session.get('user_id')
        uname_raw = request.POST.get('name', '')

        # Normalize name: lowercase, trim spaces, collapse internal spaces
        def normalize_name(name):
            return ' '.join(name.strip().lower().split())

        uname_normalized = normalize_name(uname_raw)

        # Check if a normalized match exists
        existing_styles = style_table.objects.filter(status=1)
        for style in existing_styles:
            if normalize_name(style.name) == uname_normalized:
                return JsonResponse({
                    'message': 'error',
                    'error_message': 'Style with this name already exists.'
                }, status=400)

        # Save with cleaned name
        style = style_table(
            name=uname_raw.strip(),  # Optionally store with original case but trimmed
            created_on=now(),
            created_by=user_id,
            updated_on=now(),
            updated_by=user_id
        )
        style.save()
        return JsonResponse({"data": "Success"})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)


def style_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = style_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def style_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        style_id = request.POST.get('id')
        raw_name = request.POST.get('name', '')
        is_active = request.POST.get('is_active')

        # Normalize name
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for duplicates, excluding the current style record
        if style_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=style_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Style with this name already exists.'
            }, status=400)

        try:
            style = style_table.objects.get(id=style_id)
            style.name = normalized_name
            style.is_active = is_active
            style.updated_by = user_id
            style.updated_on = datetime.now() 
            style.save()
            return JsonResponse({'message': 'success'})
        except style_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Style not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def style_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            style_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except style_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})

 
# ```````````````````````````````````````````` SIZE ````````````````````````````````

def size(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        return render(request,'size.html',{'quality':quality,'style':style})
    else:
        return HttpResponseRedirect("/admin")



def size_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(size_table.objects.filter(status=1).order_by('sort_order_no').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="size_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="size_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            # 'group': getUOMName(group_table,item['group_id']), 
            # 'style': getUOMName(style_table,item['style_id']),  
            'sort_no': item['sort_order_no'] if item['sort_order_no'] else'-', 
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})

from django.http import JsonResponse
from datetime import datetime

def size_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':  
        user_id = request.session['user_id']
        frm = request.POST
        uname_raw = frm.get('name', '')

        # Normalize name: strip, lower, and collapse multiple spaces
        def normalize_name(name):
            return ' '.join(name.strip().lower().split())

        uname_normalized = normalize_name(uname_raw)
        sort = frm.get('sort')

        # Check for existing size with same normalized name
        existing_sizes = size_table.objects.filter(status=1)
        for size in existing_sizes:
            if normalize_name(size.name) == uname_normalized:
                return JsonResponse({
                    'message': 'error',
                    'error_message': 'Size with this name already exists.'
                }, status=400)

        # Save new size
        size = size_table()
        size.name = uname_raw.strip()  # Optional: store clean original
        size.sort_order_no = sort
        size.created_on = datetime.now()
        size.created_by = user_id
        size.updated_on = datetime.now()
        size.updated_by = user_id
        size.save()

        return JsonResponse({"data": "Success"})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)



def size_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = size_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])




def size_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        size_id = request.POST.get('id')
        raw_name = request.POST.get('name', '')
        sort = request.POST.get('sort')
        is_active = request.POST.get('is_active')

        # Normalize name
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for duplicates, excluding the current size record
        if size_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=size_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Size with this name already exists.'
            }, status=400)

        try:
            size = size_table.objects.get(id=size_id)
            size.name = normalized_name
            size.sort_order_no = sort
            size.is_active = is_active
            size.updated_by = user_id
            size.updated_on = datetime.now()
            size.save()
            return JsonResponse({'message': 'success'})
        except size_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Size not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def size_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            size_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except size_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})






# ```````````````````````````````````````````` Group ````````````````````````````````

def group(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'group.html',{'group':group})
    else:
        return HttpResponseRedirect("/admin")



def group_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(group_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="group_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="group_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def group_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "create")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        uname = frm.get('name')
        group = group_table()
        group.name=uname
        group.created_on=datetime.now()
        group.created_by=user_id
        group.updated_on=datetime.now()
        group.updated_by=user_id
        group.save()
        res = "Success"
        return JsonResponse({"data": res})




def group_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = group_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def group_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "update")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        group_id = request.POST.get('id')
        name = request.POST.get('name')
        is_active = request.POST.get('is_active')
        
        try:
            group = group_table.objects.get(id=group_id)
            group.name = name
            group.is_active = is_active
            group.updated_by = user_id
            group.updated_on = datetime.now()
            group.save()
            return JsonResponse({'message': 'success'})
        except group_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'group not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def group_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            group_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except group_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})





# ```````````````````````````````````````````` Quality ````````````````````````````````

def quality(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'quality.html')
    else:
        return HttpResponseRedirect("/admin")



def quality_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(quality_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="quality_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="quality_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})



def quality_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_id = request.session.get('user_id')
        frm = request.POST
        uname_raw = frm.get('name', '')

        # Normalize: lowercase, strip, collapse multiple spaces
        def normalize_name(name):
            return ' '.join(name.strip().lower().split())

        uname_normalized = normalize_name(uname_raw)

        # Check for duplicates by normalizing existing names
        existing_qualities = quality_table.objects.filter(status=1)
        for quality in existing_qualities:
            if normalize_name(quality.name) == uname_normalized:
                return JsonResponse({
                    'message': 'error',
                    'error_message': 'Quality with this name already exists.'
                }, status=400)

        # Save new quality (store trimmed version)
        quality = quality_table(
            name=uname_raw.strip(),
            created_on=now(),
            created_by=user_id,
            updated_on=now(),
            updated_by=user_id
        )
        quality.save()

        return JsonResponse({"message": "success", "data": "Quality added successfully."})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)




# def quality_add(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)

#     if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         user_id = request.session.get('user_id')
#         frm = request.POST
#         uname = frm.get('name').strip()

#         # Check for existing active record with same name
#         existing_active = quality_table.objects.filter(name__iexact=uname, status=1).exists()
#         if existing_active:
#             return JsonResponse({'message': 'error', 'error_message': 'Quality with this name already exists.'}, status=400)

#         # Proceed to add new entry
#         quality = quality_table(
#             name=uname,
#             created_on=now(),
#             created_by=user_id,
#             updated_on=now(),
#             updated_by=user_id
#         )
#         quality.save()

#         return JsonResponse({"message": "success", "data": "Quality added successfully."})

#     return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)

 

def quality_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = quality_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])

def quality_update(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        quality_id = request.POST.get('id') 
        raw_name = request.POST.get('name', '')
        is_active = request.POST.get('is_active')

        # Normalize name
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for existing active record with same name excluding current
        if quality_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=quality_id).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Quality with this name already exists.'
            }, status=400)

        try:
            quality = quality_table.objects.get(id=quality_id)
            quality.name = normalized_name
            quality.is_active = is_active
            quality.updated_by = user_id
            quality.updated_on = datetime.now()
            quality.save()
            return JsonResponse({'message': 'success'})
        except quality_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Quality not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



# def quality_update(request):
#     user_type = request.session.get('user_type')
#     print('user-type:', user_type)
#     # has_access, error_message = check_user_access(user_type, "unit", "update")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
#         user_id = request.session.get('user_id')
#         quality_id = request.POST.get('id') 
#         name = request.POST.get('name')
#         is_active = request.POST.get('is_active')
#          # Check for existing active record with same name
#         existing_active = quality_table.objects.filter(name__iexact=name, status=1).exists()
#         if existing_active:
#             return JsonResponse({'message': 'error', 'error_message': 'Quality with this name already exists.'}, status=400)

#         try:
#             quality = quality_table.objects.get(id=quality_id)
#             quality.name = name
#             quality.is_active = is_active
#             quality.updated_by = user_id
#             quality.updated_on = datetime.now()
#             quality.save()
#             return JsonResponse({'message': 'success'})
#         except quality_table.DoesNotExist:
#             return JsonResponse({'message': 'error', 'error_message': 'quality not found'})
#     else:
#         return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def quality_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            quality_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except quality_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})




# ``````````````````````````````````````````````````````````````````````````````````````````````````````











def getSupplier(tbl, supplier_id):
    try:
        party = tbl.objects.get(id=supplier_id).name
    except ObjectDoesNotExist:
        party = "-"  # Handle the error by providing a default value or appropriate message
    return party






def po_details_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'accessory/purchase_details_update.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode()
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'accessory/purchase_details_update.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer 
        material_id = int(decoded_id)

        # Fetch the material instance using 'tm_id'
        material_instance = child_accessory_po_table.objects.filter(tm_id=material_id).first()
        if not material_instance:
            # If material not found, create a new material instance
            # For example, we assume `product_id` and other fields are provided in the request
            item_group_id = request.POST.get('item_group_id')  # Adjust as per your input structure
            item_id = request.POST.get('item_id')  # Adjust as per your input structure
            quantity = request.POST.get('quantity')  # Adjust as per your input structure
            rate = request.POST.get('rate')  # Adjust as per your input structure
            amount = request.POST.get('amount')  # Adjust as per your input structure

            # Ensure valid data before saving
            if item_group_id and item_id and quantity:
                material_instance = child_accessory_po_table.objects.create(
                    tm_id=material_id,
                    item_group_id=item_group_id,
                    item_id=item_id,
                    rate=rate,
                    quantity=quantity,
                    amount=amount,
                    # Add any other necessary fields here
                )
            else:
                return render(request, 'accessory/purchase_details_update.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = parent_accessory_po_table.objects.filter(id=material_id).first()
        
        if not parent_stock_instance:
            return render(request, 'accessory/purchase_details_update.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name using supplier_id from parent_stock_instance
        supplier_name = "-"

        if parent_stock_instance.supplier_id:
            try:
                supplier = party_table.objects.get(id=parent_stock_instance.supplier_id,status=1)
                supplier_name = supplier.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products and UOM
        item_group = acc_item_group_table.objects.filter(status=1)
        item = item_table.objects.filter(status=1)
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(
            Q(is_trader=1) | Q(is_sticker=1) | Q(is_label=1) | Q(is_packing=1),
            status=1
        )
        # Render the edit page with the material instance and supplier name
        context = {
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'item_group': item_group,
            'item':item,
            'party': party,
            'supplier_id': supplier_name,  # Pass the supplier name to the template
            'supplier': party
        }
        return render(request, 'accessory/purchase_details_update.html', context)

    except Exception as e:
        return render(request, 'accessory/purchase_details_update.html', {'error_message': 'An unexpected error occurred: ' + str(e)})




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
                                        <button type="button" onclick="purchase_order_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'item_group': getItemNameById(acc_item_group_table, item['item_group_id']),
                            'item': getItemNameById(item_table, item['item_id']),
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




def po_detail_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = child_accessory_po_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



from decimal import Decimal





# ``````````````````````````````````````````````````````````````````````````````````````



def accessory_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'accessory/accessory_delivery.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/admin")


# ``````````````````````````````````` quality program `````````````````````````````````````````````````````````````


def quality_program(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        item_group = acc_item_group_table.objects.filter(status=1).order_by('name')

        size = size_table.objects.filter(status=1).order_by('name')
        # quality = accessory_quality_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1).order_by('name')
        fabric = fabric_program_table.objects.filter(status=1).order_by('name')

        style = style_table.objects.filter(status=1).order_by('name')
        return render(request,'quality_prg/quality_program_list.html',{'item_group':item_group,
                                                                       'fabric':fabric,'quality':quality,'size':size,'style':style})
    else:
        return HttpResponseRedirect("/admin")
    



@csrf_exempt
def quality_program_add(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            user_id = request.session['user_id']
            frm = request.POST
            style_id = frm.get('style_id')
            quality_id = frm.get('quality_id')

            # Get fabric_id as comma-separated string
            fabric_id_str = request.POST.get('fabric_id', '')  # e.g., "21,22"
            print('fabric_id:', fabric_id_str)
 
            # Parse size data
            size_data = json.loads(request.POST.get('size_data', '[]'))

            # Create main quality program entry
            quality_entry = quality_program_table.objects.create(
                quality_id=quality_id,
                style_id=style_id,
                fabric_id=fabric_id_str,
                created_on=datetime.now(),
                created_by=user_id,
            )

            # Create size entries
            for size in size_data:
                sub_quality_program_table.objects.create(
                    tm_id=quality_entry.id,
                    size_id=size["id"],
                    position=size["position"],
                    per_box=size["per_box"],
                    created_on=datetime.now(),
                    created_by=user_id,
                )

            return JsonResponse({"data": "Success"})

        except Exception as e:
            return JsonResponse({"data": "Error", "error": str(e)})

    return JsonResponse({"data": "Invalid Request"})



def quality_program_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)
    
    # Get all quality_program_table entries with status=1
    data = list(quality_program_table.objects.filter(status=1).order_by('-id').values())

    formatted = []
    
    for index, item in enumerate(data):
        # Fetch all sub_quality_program_table entries for this tm_id
        # sub_items = list(sub_quality_program_table.objects.filter(tm_id=item['id'], status=1).values_list('size_id', flat=True))
        
        sub_items = list(
            sub_quality_program_table.objects.filter(tm_id=item['id'], status=1)
            .order_by('position')
            .values_list('size_id', flat=True)
        )


        print('sub-items:', sub_items) 

        if sub_items:
            # Convert each size ID to name separately
            size_names = [getSizeName(size_table, size_id) for size_id in sub_items]
            size_names = ", ".join(size_names)  # Combine names into a single string
        else:
            size_names = "-"



        # Add the formatted data to the list
        formatted.append({
            'action': '<button type="button" onclick="quality_prg_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="quality_prg_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            'fabric': getMultipleItemFabNameById(fabric_program_table, item['fabric_id']), 
            'quality': getUOMName(quality_table, item['quality_id']), 
            'style': getUOMName(style_table, item['style_id']), 
            'size': size_names,  # Combined size names
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



# def quality_prg_edit(request):
#     if is_ajax and request.method == "POST":
#         item_id = request.POST.get('id')

#         # Fetch the item from item_table
#         item_data = quality_program_table.objects.filter(id=item_id).values().first()

#         # Check if the item_data is not empty
#         if not item_data:
#             return JsonResponse({'message': 'error', 'error_message': 'Item not found'}, status=404)

#         # Initialize variables to avoid UnboundLocalError
#         size_ids = []
#         size_names = ""

#         # Fetch associated sub_item data
#         sub_item_data = sub_quality_program_table.objects.filter(tm_id=item_id).first()

#         # If the sub_item exists, fetch the associated quality, size, and color
#         if sub_item_data:
#             size_ids = sub_item_data.size_id

#             # Fetch names using the helper function
#             size_names = getUOMName(size_table, size_ids)

#         # Fetch available size, color, and quality data for the dropdown
#         size = accessory_size_table.objects.filter(status=1).order_by('name').values('id','name')
#         # fabric = fabric_program_table.objects.filter(status=1).order_by('name').values('id','name')
#         fabric_program_qs = fabric_program_table.objects.filter(status=1)

#                 # Build fabric_program list with resolved fabric_name from fabric_table
#         fabric_program_with_name = []
#         for fp in fabric_program_qs:
#             try:
#                 fabric_item = fabric_table.objects.get(id=fp.fabric_id)
#                 print(f"fabric_item: {fabric_item}, ID: {fp.fabric_id}, Name: {getattr(fabric_item, 'name', 'NO NAME')}")
#                 fabric_program_with_name.append({
#                     'id': fp.id,
#                     'name': fp.name,
#                     'fabric_id': fp.fabric_id,
#                     'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
#                 })
#             except fabric_table.DoesNotExist:
#                 print(f"fabric_id {fp.fabric_id} not found in fabric_table")
#                 fabric_program_with_name.append({
#                     'id': fp.id,
#                     'name': fp.name,
#                     'fabric_id': fp.fabric_id,
#                     'fabric_name': 'N/A'
#                 })
       
#         print('item-fab:', item_data['fabric_id'])
#         response_data = {
#             'item_id': item_data['id'],
#             'style_id': item_data['style_id'],
#             'quality_id': item_data['quality_id'],
#             'fabric_id': item_data['fabric_id'].split(',') if item_data['fabric_id'] else [],

#             # 'fabric_id': item_data['fabric_id'],  # ✅ ADD THIS LINE
#             'size_id': size_ids,
#             'size_names': size_names,
#             'is_active': item_data['is_active'],
#             'size': list(size),
#             'fabric': fabric_program_with_name,
#         }

#         return JsonResponse(response_data)



from django.http import JsonResponse

def quality_prg_edit(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_id = request.POST.get('id')

        # Fetch the item from item_table
        item_data = quality_program_table.objects.filter(id=item_id).values(
            'id', 'style_id', 'quality_id', 'fabric_id', 'is_active'
        ).first()

        if not item_data:
            return JsonResponse({'message': 'error', 'error_message': 'Item not found'}, status=404)

        # Initialize default values
        size_ids = []
        size_names = ""

        # Fetch associated sub_item data
        sub_item_data = sub_quality_program_table.objects.filter(tm_id=item_id).first()
        if sub_item_data:
            size_ids = sub_item_data.size_id
            size_names = getUOMName(size_table, size_ids)

        # Parse fabric_id from comma-separated string to list
        fabric_ids_raw = item_data.get('fabric_id', '')
        if fabric_ids_raw and isinstance(fabric_ids_raw, str):
            fabric_ids = [x.strip() for x in fabric_ids_raw.split(',') if x.strip()]
        else:
            fabric_ids = []

        # Get fabric list with names
        fabric_program_qs = fabric_program_table.objects.filter(status=1)
        fabric_program_with_name = []
        for fp in fabric_program_qs:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                })
            except fabric_table.DoesNotExist:
                fabric_program_with_name.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': 'N/A'
                })

        # Fetch size list
        size = accessory_size_table.objects.filter(status=1).order_by('name').values('id', 'name')

        # Final JSON response
        response_data = {
            'item_id': item_data['id'],
            'style_id': item_data['style_id'],
            'quality_id': item_data['quality_id'],
            'fabric_id': fabric_ids,  # ✅ Sending list of fabric IDs
            'size_id': size_ids,
            'size_names': size_names,
            'is_active': item_data['is_active'],
            'size': list(size),
            'fabric': fabric_program_with_name,
        }

        return JsonResponse(response_data)

    return JsonResponse({'message': 'Invalid request'}, status=400)


def quality_prg_size_list(request):
    if request.method == "POST":
        tm_id = request.POST.get("tm_id", "").strip()
        
        if not tm_id.isdigit():  # Ensure it's a number
            return JsonResponse({"error": "Invalid tm_id"}, status=400)
        
        # Fetch data normally
        # data = list(sub_quality_program_table.objects.filter(tm_id=tm_id, status=1).values())
        data = list(sub_quality_program_table.objects.filter(tm_id=tm_id, status=1).order_by('position').values())




        formatted = []
        
        for index, item in enumerate(data):
            # Fetch all sub_quality_program_table entries for this tm_id
    

            # Add the formatted data to the list
            formatted.append({
                'action': '<button type="button" onclick="prg_size_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="prg_size_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
                'id': index + 1, 
                'tm_id':item['tm_id'],
                'position':item['position'],
                'per_box':item['per_box'],
                'size': getUOMName(size_table, item['size_id']),
                'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
            })
        
        return JsonResponse({'data': formatted}) 
    return JsonResponse({"error": "Invalid request"}, status=400)






def prg_size_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST 
    data = sub_quality_program_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])
 

@csrf_exempt
def prg_size_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        try:
            user_id = request.session.get('user_id')
            edit_id = request.POST.get('edit_id')  # ID of the row being edited
            size_id = request.POST.get('size_id')
            # fabric_id = request.POST.get('fabric_id')
            # fabric_ids = request.POST.getlist('fabric_id[]')  # ⬅ expects multiple <input name="fabric_id[]">
            # fabric_id_str = ','.join(fabric_ids)  # ⬅ e.g., "2,3"
            position = request.POST.get('position')
            per_box = request.POST.get('per_box')
            tm_id = request.POST.get('tm_id')
            is_active = request.POST.get('is_active') == "1" 
            # Always update the fabric_id

            fabric_id_str = request.POST.get('fabric_id', '')  # Get string like "1,2,3"           
            print('fab-id:', fabric_id_str) 

            # quality_program_table.objects.filter(id=tm_id).update(fabric_id=fabric_id_str)

            # quality_program_table.objects.filter(id=tm_id).update(fabric_id=fabric_id_str)

            # If size or position is not provided or is "Select", skip further processing
            if not size_id or size_id == "Select" or not position or position == "Select":
                return JsonResponse({'message': 'success', 'updated_fabric_only': True})

            # Proceed with size update logic only if edit_id is provided
            position = int(position)

            if edit_id and edit_id != '0':
                size = sub_quality_program_table.objects.filter(id=edit_id, tm_id=tm_id).first()
                if size:
                    if sub_quality_program_table.objects.filter(tm_id=tm_id, size_id=size_id).exclude(id=edit_id).exists():
                        return JsonResponse({'message': 'error', 'error_message': 'This size is already added for the selected quality program.'})
                    if sub_quality_program_table.objects.filter(tm_id=tm_id, position=position).exclude(id=edit_id).exists():
                        return JsonResponse({'message': 'error', 'error_message': 'This position is already taken. Please choose another position.'})
                    
                    size.size_id = size_id
                    size.position = position
                    size.per_box = per_box
                    size.is_active = is_active
                    size.updated_by = user_id
                    size.updated_on = datetime.now()
                    size.save()
                    return JsonResponse({'message': 'success', 'created': False})

            # Create new entry
            if sub_quality_program_table.objects.filter(tm_id=tm_id, size_id=size_id).exists():
                return JsonResponse({'message': 'error', 'error_message': 'This size is already added for the selected quality program.'})
            if sub_quality_program_table.objects.filter(tm_id=tm_id, position=position).exists():
                return JsonResponse({'message': 'error', 'error_message': 'This position is already taken. Please choose another position.'})

            sub_quality_program_table.objects.create(
                tm_id=tm_id,
                size_id=size_id,
                position=position,
                per_box=per_box,
                is_active=True,
                created_by=user_id,
                created_on=datetime.now()
            )
            return JsonResponse({'message': 'success', 'created': True})

        except IntegrityError as e:
            return JsonResponse({'message': 'error', 'error_message': f'Database integrity error: {str(e)}'})
        except ValueError:
            return JsonResponse({'message': 'error', 'error_message': 'Invalid number format in position.'})
        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


@csrf_exempt
def check_size_id(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        tm_id = request.GET.get('tm_id')
        size_id = request.GET.get('size_id')

        # Check if the size_id already exists for the given tm_id
        size_exists = sub_quality_program_table.objects.filter(tm_id=tm_id, size_id=size_id).exists()

        if size_exists:
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



@csrf_exempt
def prg_size_add(request):
    """Add a new size entry."""
    if request.method == "POST":
        tm_id = request.POST.get('tm_id')
        size_id = request.POST.get('size_id') 
        position = request.POST.get('position')
        per_box = request.POST.get('per_box')

        if sub_quality_program_table.objects.filter(tm_id=tm_id, size_id=size_id).exists():
            return JsonResponse({'message': 'exists'})

        sub_quality_program_table.objects.create(
            tm_id=tm_id,
            size_id=size_id,
            position = position,
            per_box = per_box,
            is_active=1,
            # is_active=request.POST.get('is_active') == "1"
        )
        return JsonResponse({'message': 'success'})

    return JsonResponse({'message': 'error'}, status=400)




def prg_size_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_quality_program_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except sub_quality_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
 

 
 
def quality_prg_delete(request): 
    if request.method == 'POST':
        data_id = request.POST.get('id') 
        try:
            # Update the status field to 0 instead of deleting
            quality_program_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_quality_program_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except quality_program_table  & sub_quality_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



