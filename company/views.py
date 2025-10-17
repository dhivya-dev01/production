
import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
# from software_app.models import count_table, knitting_table, parent_po_table, party_table, product_table, sub_yarn_deliver_table, sub_yarn_inward_table, yarn_delivery_table, yarn_inward_table
from software_app.models import *
from company.models import *
from employee.models import *

from software_app.views import getItemNameById, getSupplier, is_ajax, check_user_access
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from decimal import Decimal
from django.db.models import F
from decimal import Decimal, InvalidOperation

import base64
import logging
from django.shortcuts import get_object_or_404
from company.forms import *

import hashlib

logger = logging.getLogger(__name__)  # Use Django logging

# Create your views here.


def company(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        cmpy = company_table.objects.filter(id=1).first()
        return render(request, 'company.html', {'company': cmpy})
      
    else:
        return HttpResponseRedirect("/signin")


def profile(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type') 
        cmpy = company_table.objects.filter(id=1).first()
        return render(request, 'master/profile.html', {'company': cmpy})
       
    else:
        return HttpResponseRedirect("/signin")

from datetime import datetime

def update_company(request): 
    if request.method == "POST":
        company_id = request.POST.get('id')
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')

        # has_access, error_message = check_user_access(user_type, "Company", "update")

        # if not has_access:
        #     return JsonResponse({'message': 'error', 'error_message': error_message})
 
        company_instance = get_object_or_404(company_table, id=company_id)
        form = companyform(request.POST, request.FILES, instance=company_instance) 
        if form.is_valid():
            # Update only fields that exist in request.POST or request.FILES
            for field in form.cleaned_data: 
                if field in request.POST or field in request.FILES: 
                    setattr(company_instance, field, form.cleaned_data[field])

            # Handle additional fields manually
            extra_fields = ['phone', 'address_line2', 'latitude', 'longitude','gstin','cin_no','udyam_no']
            for field in extra_fields:
                if field in request.POST:
                    setattr(company_instance, field, request.POST.get(field) or '')

            company_instance.updated_by = user_id
            company_instance.updated_on = datetime.now()
            company_instance.save()

            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})


  