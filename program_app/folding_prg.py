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




def folding_program(request):
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
        return render(request,'folding/add_folding_program.html',{'party':party,'fabric_program':fabric_program,'lot':lot,'quality':quality,'style':style
                                                                           })
    else:
        return HttpResponseRedirect("/admin")
    




def generate_folding_num_series():
    last_purchase = folding_program_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.program_no:
        match = re.search(r'FP-(\d+)', last_purchase.program_no)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"FP-{next_num:03d}"




def folding_program_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_cutting=1)  
        fabric_program = fabric_program_table.objects.filter(status=1) 

        prg_number = generate_folding_num_series
 
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)
        size = size_table.objects.filter(status=1)
        color = color_table.objects.filter(status=1)
        return render(request,'folding/add_folding_program.html',{'party':party,'fabric_program':fabric_program,'prg_no':prg_number,'color':color
                                                                  ,'quality':quality,'style':style,'size':size})
    else:
        return HttpResponseRedirect("/admin")
    


def folding_program_report(request):   
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
    queryset = folding_program_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())
    # data = list(cutting_program_table.objects.filter(status=1).order_by('-id').values())
    print('dat:',data)
    formatted = [
        {
            'action': '<button type="button" onclick="folding_prg_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="folding_prg_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
                        # <button type="button" onclick="cutting_prg__print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'prg_no': item['program_no'] if item['program_no'] else'-', 
            'quality':getSupplier(quality_table, item['quality_id'] ), 
            'style':getSupplier(style_table, item['style_id'] ),  
            'size_1': item['size_1'] if item['size_1'] else 0 , 
            'size_2': item['size_2'] if item['size_2'] else 0 , 
            'size_3': item['size_3'] if item['size_3'] else 0 , 
            'size_4': item['size_4'] if item['size_4'] else 0 , 
            'size_5': item['size_5'] if item['size_5'] else 0 , 
            'size_6': item['size_6'] if item['size_6'] else 0 , 
            'size_7': item['size_7'] if item['size_7'] else 0 , 
            'size_8': item['size_8'] if item['size_8'] else 0 , 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 




def folding_program_edit(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        item_id = request.POST.get('id')  # Get the ID from the request
        data = folding_program_table.objects.filter(id=item_id).values() 
 
        if data.exists():  # ✅ Check if data is available
            return JsonResponse(data[0])  # ✅ Return the first matching object
        else:
            return JsonResponse({'error': 'No matching record found'}, status=404)  # ✅ Handle missing data safely

    return JsonResponse({'error': 'Invalid request'}, status=400)  # Handle invalid requests
  



def delete_folding_program(request):
    if request.method == 'POST': 
        data_id = request.POST.get('id')
        print('delete-id:',data_id) 
        try: 
            # Update the status field to 0 instead of deleting 
            folding_program_table.objects.filter(id=data_id).update(status=0,is_active=0)

            return JsonResponse({'message': 'yes'})
        except folding_program_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'}) 
    else:
        return JsonResponse({'message': 'Invalid request method'})





@csrf_exempt
def insert_folding_program(request):
    if request.method == 'POST':    
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        user_id = request.session.get('user_id')  # assuming you store this in session
        company_id = request.session.get('company_id')

        sizes = [float(request.POST.get(f'size_{i}', 0)) for i in range(1, 9)]

        # Insert single row with all size values
        prg_no = generate_folding_num_series()
        folding_program_table.objects.create(

            program_no=prg_no,  # you can generate a program number if needed
            company_id=company_id,
            quality_id=quality_id,
            style_id=style_id,
            size_1=sizes[0],
            size_2=sizes[1],
            size_3=sizes[2],
            size_4=sizes[3],
            size_5=sizes[4],
            size_6=sizes[5],
            size_7=sizes[6],
            size_8=sizes[7],
            remarks='',
            is_active=1,
            status=1,
            created_on=timezone.now(),
            updated_on=timezone.now(),
            created_by=user_id,
            updated_by=user_id,
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'invalid method'}, status=405)



@csrf_exempt 
def update_folding_program(request):
    if request.method == 'POST':
        edit_id = request.POST.get('edit_id')
        quality_id = request.POST.get('quality_id')
        style_id = request.POST.get('style_id')
        user_id = request.session.get('user_id')
        
        try:
            obj = folding_program_table.objects.get(id=edit_id) 
            obj.quality_id = quality_id
            obj.style_id = style_id
            obj.size_1 = float(request.POST.get('size_1', 0))
            obj.size_2 = float(request.POST.get('size_2', 0))
            obj.size_3 = float(request.POST.get('size_3', 0))
            obj.size_4 = float(request.POST.get('size_4', 0))
            obj.size_5 = float(request.POST.get('size_5', 0))
            obj.size_6 = float(request.POST.get('size_6', 0))
            obj.size_7 = float(request.POST.get('size_7', 0))
            obj.size_8 = float(request.POST.get('size_8', 0))
            obj.updated_on = timezone.now()
            obj.updated_by = user_id
            obj.save()
            return JsonResponse({'status': 'success'})
        except folding_program_table.DoesNotExist:
            return JsonResponse({'status': 'not found'}, status=404)
        
    return JsonResponse({'status': 'invalid method'}, status=405)
