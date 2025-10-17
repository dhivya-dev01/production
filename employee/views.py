from django.shortcuts import render

# Create your views here.


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

import hashlib

logger = logging.getLogger(__name__)  # Use Django logging

# Create your views here.



# ``````````````````````````` Employee`````````````````````````````````````````````````





def employee(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        company = company_table.objects.filter(status=1)
        return render(request,'employee/employee.html',{'company':company})
    else:
        return HttpResponseRedirect("/signin")



def employee_list(request):
    company_id = request.session['company_id'] 
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(employee_table.objects.filter(status=1,company_id=company_id).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="employee_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                      <button type="button" onclick="employee_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'], item['id']),
            'id': index + 1, 
            
            'name': item['name'] if item['name'] else'-', 
            'email': item['email'] if item['email'] else'-', 
            'mobile': item['mobile'] if item['mobile'] else'-', 
            'employee_code': item['employee_code'] if item['employee_code'] else'-', 
            'employee_role': item['employee_role'] if item['employee_role'] else'-', 
            'nick_name': item['nick_name'] if item['nick_name'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})







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


def generate_employee_code(name):
    """Generates an employee code based on name initials and financial year."""
    initials = ''.join([word[0] for word in name.split()]).upper()  # Extract initials
    # financial_year = get_financial_year().split('-')[0]  # Get '24' from '24-25'

    # Get the last assigned employee code for this financial year
    last_employee = employee_table.objects.filter(employee_code__startswith=initials ).order_by('-employee_code').first()

    if last_employee:
        last_code = int(last_employee.employee_code[-4:]) + 1
    else:
        last_code = 1

    new_code = f"{initials}{last_code:04d}"  # Format JD240001
    return new_code 

def employee_add(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id', None)
        frm = request.POST
        img = request.FILES.get('photo')  # Get the uploaded file

        # Save employee data
        employee = employee_table(
            name=frm.get('name'),
            nick_name=frm.get('nick_name'),
            email=frm.get('email'),
            mobile=frm.get('mobile'),
            employee_role=frm.get('employee_role'),
            designation=frm.get('designation'),
            permanent_address=frm.get('permanent_address'),
            current_address=frm.get('current_address'),
            alter_mobile_no=frm.get('alter_mobile_no'),
            aadhar_no=frm.get('aadhar_no'),
            dob=frm.get('dob') if frm.get('dob') else None,
            join_date=frm.get('join_date') if frm.get('join_date') else None,
            password=hashlib.md5(frm.get('password').encode()).hexdigest(),
            company_id=1,
            created_on=datetime.now(),
            created_by=user_id,
            updated_on=datetime.now(),
            updated_by=user_id,
            photo=img if img else None  # Save the image only if uploaded
        )

        employee.save()
        return JsonResponse({"data": "Success"})

    return JsonResponse({"error": "Invalid request"}, status=400)


def employee_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = employee_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


import hashlib
from datetime import datetime
from django.http import JsonResponse
from .models import employee_table



from django.http import JsonResponse
from django.core.files.storage import default_storage
from datetime import datetime
import hashlib

def employee_update(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session.get('user_id')
        employee_id = request.POST.get('id')

        # Fetch employee
        try:
            employee = employee_table.objects.get(id=employee_id)
        except employee_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'Employee not found'}, status=404)

        # Get form data
        name = request.POST.get('name')
        nick_name = request.POST.get('nick_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        employee_role = request.POST.get('employee_role')
        dob = request.POST.get('dob')  
        password = request.POST.get('password') 
        join_date = request.POST.get('join_date')
        designation = request.POST.get('designation')
        is_active = request.POST.get('is_active') # Convert string to boolean
        permanent_address = request.POST.get('permanent_address')
        current_address = request.POST.get('current_address')
        alter_mobile_no = request.POST.get('alter_mobile_no')
        aadhar_no = request.POST.get('aadhar_no')
        img = request.FILES.get('photo')  # Get the uploaded image

        # Update employee fields
        employee.name = name
        employee.nick_name = nick_name
        employee.email = email
        employee.mobile = mobile
        employee.permanent_address = permanent_address
        employee.current_address = current_address
        employee.alter_mobile_no = alter_mobile_no
        employee.aadhar_no = aadhar_no
        employee.employee_role = employee_role
        employee.designation = designation
        employee.is_active = is_active
        employee.updated_by = user_id
        employee.updated_on = datetime.now()

        # # Update password only if provided
        # if password:
        #     employee.password = hashlib.md5(password.encode()).hexdigest()

        # Update password only if a new password is provided and it's different from the old one
        # Hash the new password for comparison

        # Update password only if a new one is provided and different from the stored one
        if password and password.strip():  # Check if not empty or just spaces
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            
            if hashed_password != employee.password:  # Only update if different
                employee.password = hashed_password

        # Handle image update
        if img:
            if employee.photo:  # Delete old photo if exists 
                default_storage.delete(employee.photo.path) 
            employee.photo = img  # Save new image 

        # Handle date fields safely 
        try:
            employee.dob = datetime.strptime(dob, "%Y-%m-%d").date() if dob else None
        except ValueError:
            return JsonResponse({'message': 'error', 'error_message': 'Invalid DOB format. Use YYYY-MM-DD'}, status=400)

        try:
            employee.join_date = datetime.strptime(join_date, "%Y-%m-%d").date() if join_date else None
        except ValueError:
            return JsonResponse({'message': 'error', 'error_message': 'Invalid Join Date format. Use YYYY-MM-DD'}, status=400)

        # Save changes
        employee.save()

        return JsonResponse({'message': 'success'})

    return JsonResponse({'message': 'error', 'error_message': 'Invalid request'}, status=400)




def employee_delete(request): 
    user_type = request.session.get('user_type')
    print('user-type:', user_type)
    # has_access, error_message = check_user_access(user_type, "unit", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)

    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            employee_table.objects.filter(id=data_id).delete()
            return JsonResponse({'message': 'yes'})  
        except employee_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
