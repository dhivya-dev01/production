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




def price_lists(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'price_list.html')
    else:
        return HttpResponseRedirect("/signin")



def price_list_report(request):
    company_id = request.session['company_id']  
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(price_list_table.objects.filter(status=1).order_by('-id').values())
    
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



def price_list_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = price_list_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def price_list_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        raw_name = frm.get('name', '') 

        # Normalize the name: strip spaces and uppercase
        normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check if it already exists
        if price_list_table.objects.filter(name__iexact=normalized_name, status=1).exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'Price list with this name already exists.'
            }, status=400)

        # Save cleaned name
        uom = price_list_table()
        uom.name = normalized_name
        uom.created_on = datetime.now()
        uom.created_by = user_id
        uom.updated_on = datetime.now()
        uom.updated_by = user_id
        uom.save()

        return JsonResponse({"data": "Success"})



def price_list_update(request):
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
        duplicates = price_list_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=uom_id)
        if duplicates.exists():
            return JsonResponse({
                'message': 'error',
                'error_message': 'price List with this name already exists.'
            }, status=400)

        try:
            uom = price_list_table.objects.get(id=uom_id)
            uom.name = normalized_name
            uom.is_active = is_active
            uom.updated_by = user_id
            uom.updated_on = datetime.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except price_list_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Price List not found'})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def price_list_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            price_list_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except price_list_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



# ````````````````````````````````````````````````````` PRICE LIST RANGE `````````````````````````````````````````````




def price_list_range(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        quality = quality_table.objects.filter(status=1)
        style= style_table.objects.filter(status=1)
        price_list = price_list_table.objects.filter(status=1) 
        size = size_table.objects.filter(status=1) 
        return render(request,'price_list_range.html',{'style':style,'quality':quality,'price_list':price_list,'size':size})
    else:
        return HttpResponseRedirect("/signin")
 

def getPriceByID(tbl, cat_id):
    try:
        category = tbl.objects.get(id=cat_id).name
        return category
    except tbl.DoesNotExist:
        return 'NA' 
    except Exception:
        return 'NA' 
 
def price_list_range_report(request):
    company_id = request.session['company_id']  
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(price_list_range_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [ 
        {
            'action': '<button type="button" onclick="price_list_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="price_list_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1,  
            'quality':getItemNameById(quality_table,item['quality_id']),
            'style':getItemNameById(style_table,item['style_id']),
            'size':getItemNameById(size_table,item['size_id']),
            'price_list':getItemNameById(price_list_table,item['price_list_id']),
            'price': item['rate'] if item['rate'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})



def price_list_range_edit(request):
    if is_ajax and request.method == "POST":  
        frm = request.POST
    data = price_list_range_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def price_list_range_add(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if is_ajax and request.method == "POST":  
        user_id = request.session['user_id']
        frm = request.POST
        price = frm.get('price', '') 
        quality_id = frm.get('quality_id', '') 
        style_id = frm.get('style_id', '') 
        price_list_id = frm.get('price_list', '') 
        size_id = frm.get('size_id','')
        # Normalize the name: strip spaces and uppercase
        # normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check if it already exists
        # if price_list_range_table.objects.filter(name__iexact=normalized_name, status=1).exists():
        #     return JsonResponse({
        #         'message': 'error',
        #         'error_message': 'Price list with this name already exists.'
        #     }, status=400)

        # Save cleaned name

        uom = price_list_range_table()
        uom.rate = price
        uom.quality_id = quality_id
        uom.style_id = style_id
        uom.size_id = size_id
        uom.price_list_id = price_list_id
        uom.created_on = datetime.now()
        uom.created_by = user_id
        uom.updated_on = datetime.now()
        uom.updated_by = user_id
        uom.save()

        return JsonResponse({"data": "Success"})



def price_list_range_update(request): 
    user_type = request.session.get('user_type')
    print('user-type:', user_type)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
      
        uom_id = request.POST.get('id')
        price = request.POST.get('price', '')
        quality_id = request.POST.get('quality_id', '')
        style_id = request.POST.get('style_id', '')
        price_list_id = request.POST.get('price_list', '')
        is_active = request.POST.get('is_active')
        size_id = request.POST.get('size_id')
        # Normalize the name 
        # normalized_name = ' '.join(raw_name.strip().upper().split())

        # Check for duplicate name excluding current record
        # duplicates = price_list_range_table.objects.filter(name__iexact=normalized_name, status=1).exclude(id=uom_id)
        # if duplicates.exists():
        #     return JsonResponse({
        #         'message': 'error',
        #         'error_message': 'price List with this name already exists.'
        #     }, status=400)


        try:
            uom = price_list_range_table.objects.get(id=uom_id)
            uom.rate = price  
            uom.quality_id = quality_id
            uom.style_id = style_id
            uom.size_id=size_id
            uom.price_list_id = price_list_id 
            uom.is_active = is_active 
            uom.updated_by = user_id 
            uom.updated_on = datetime.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except price_list_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Price List not found'})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})



def price_list_range_delete(request):
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            price_list_range_table.objects.filter(id=data_id).update(status=0) 
            return JsonResponse({'message': 'yes'})
        except price_list_range_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



