
import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
# from software_app.models import count_table, knitting_table, parent_po_table, party_table, product_table, sub_yarn_deliver_table, sub_yarn_inward_table, yarn_delivery_table, yarn_inward_table
from software_app.models import *
from employee.models import *
from company.models import *

from software_app.views import getItemNameById, getSupplier, is_ajax, check_user_access
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from decimal import Decimal
from django.db.models import F
from decimal import Decimal, InvalidOperation

import base64
import logging

import hashlib

logger = logging.getLogger(__name__)  # Use Django logging

# Create your views here.





def signin_admin(request):
    return render(request,'login.html')




def login(request):
    if request.method == "POST":
        email = request.POST.get('email') 
        pwd = request.POST.get('password')

        print('login:', email, pwd)
         
        # Hash the password for comparison
        hashed_pwd = hashlib.md5(pwd.encode()).hexdigest() 
        print('pwd:', hashed_pwd)
        # value = '636033734f18216f6084ba415c509164'
        # print('decode-pwd:',hashlib.md5(value.decode()).hexdigest() )
        # Check if the user exists in the database
        if employee_table.objects.filter(email=email, password=hashed_pwd).exists():
            user = employee_table.objects.get(email=email, password=hashed_pwd)
            print('login-user:',user)
            # 🔹 Calculate Financial Year
            # financial_year = get_financial_year()  # ✅ Now works correctly

            # Set session data
            request.session['user_id'] = user.id
            request.session['employee_role'] = user.employee_role 
            request.session['company_id'] = user.company_id
            request.session['user_username'] = user.name
            request.session['user_email'] = user.email
            request.session['user_type'] = user.employee_role

            company = company_table.objects.filter(id=user.company_id).first()

            # f_id = fyf_table.objects.filter(id=company.fyf_id).first()
            # fyf = f_id.name if f_id else None
            # request.session['fyf'] = fyf  # Store full "2024-2025"

            # # Optionally split and store parts 
            # if fyf and '-' in fyf: 
            #     fyf_start, fyf_end = fyf.split('-')
            #     request.session['fyf_start'] = fyf_start.strip() 
            #     request.session['fyf_end'] = fyf_end.strip()

            # print('cfy:', request.session['cfy'])

            # Redirect to dashboard on successful login
            return HttpResponseRedirect("/dashboard")
        else:
            # If login fails, show error message
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    # If it's a GET request, render the login page
    return render(request, 'login.html')




def logout(request):
    if 'user_id' in request.session:
        request.session.flush() 
    return HttpResponseRedirect("/signin")

