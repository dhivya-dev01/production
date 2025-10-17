from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from software_app.models import *
from common.models import *
from employee.models import *
from user_auth.models import *
from user_roles.models import *
from company.models import *
from yarn.models import *
from masters.models import *
from yarn.models import *
from django.db.models import Max
from django.db.models import Max, F, Q
import base64



from django.template.loader import get_template
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from xhtml2pdf import pisa
import base64
from collections import defaultdict
from django.shortcuts import get_object_or_404
from io import BytesIO
# **************************************************************************************************************************************
# Helper to resolve static files (required by xhtml2pdf)
from django.conf import settings
from django.contrib.staticfiles import finders
import os

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        path = os.path.realpath(result[0])
    else:
        sUrl = settings.STATIC_URL      # Typically /static/
        sRoot = settings.STATIC_ROOT    # e.g. /home/user/app/static
        mUrl = settings.MEDIA_URL       # Typically /media/ 
        mRoot = settings.MEDIA_ROOT     # e.g. /home/user/app/media

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    if not os.path.isfile(path):
        raise Exception(f'Media URI must start with {sUrl} or {mUrl}')
    return path

#```````````````````````````` delete all datas from all table (database) ````````````````````````````````````#

#   python manage.py flush --noinput

# *****************************************************************************************************************************************


def week_of_month(dt):        
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()
    return int((adjusted_dom - 1) / 7) + 1




def selectOrderBy(tbl, whr, order_by, asc):
    # return arraylist here
    return None



def unique_no(tbl, whr):
    # return last row
    return None


def groupItems(tbl, str):
    # return comma seperated ids to names string  here
    return None

def groupItemsByChips(tbl, str):
    # return comma seperated ids to names string  here
    return None

def getUniqueNo(tbl, branch_id, company_id, fyear):
    # return unique number for num_series from here
    return None

# ***************DATE FORMAT***************

def format_datetime(date):
    return date.strftime('%Y-%m-%d %H:%M:%S') if date else None


def format_date(date):
    return date.strftime('%Y-%m-%d') if date else None


def format_time(date):
    return date.strftime('%H:%M:%S') if date else None



# ***************DATE FORMAT***************

def normalize_date(date_str):    
    if not date_str or date_str in ["0000-00-00", "0000-00-00 00:00:00"]:
        return None
    return date_str


# ***************GET NAME BY ID***************
def getItemNameById(tbl, cat_id):
    try:
        category = tbl.objects.get(id=cat_id).name
        return category
    except tbl.DoesNotExist:
        return 'NA' 
    except Exception:
        return 'NA' 



def getStichingDeliveryNoById(tbl,po_id):
    try:
        category = tbl.objects.get(id=po_id).outward_no
        return category
    except tbl.DoesNotExist:
        return '' 
    except Exception as e:
        return ''
    



def getPackingDeliveryNoById(tbl,po_id):
    try:
        category = tbl.objects.get(id=po_id).outward_no
        return category
    except tbl.DoesNotExist:
        return '' 
    except Exception as e:
        return ''

def getCutting_entryNoById(tbl,po_id):
    try:
        category = tbl.objects.get(id=po_id).cutting_no 
        return category
    except tbl.DoesNotExist:
        return '' 
    except Exception as e: 
        return ''


def getInward_entryNoById(tbl,po_id):
    try:
        category = tbl.objects.get(id=po_id).inward_no 
        return category
    except tbl.DoesNotExist:
        return '' 
    except Exception as e: 
        return ''



def getOutward_entryNoById(tbl,po_id):
    try:
        data = tbl.objects.get(id=po_id).outward_no
        return data
    except tbl.DoesNotExist:
        return '' 
    except Exception as e: 
        return ''






def getDyeingDisplayNameById(tbl, supplier_id):
    try:
        obj = tbl.objects.get(id=supplier_id)
        return f"{obj.program_no} - {obj.name}"
    except tbl.DoesNotExist:
        return "-"



def getKnittingDisplayNameById(tbl, supplier_id): 
    try:
        obj = tbl.objects.get(id=supplier_id)
        return f" {obj.knitting_number} - {obj.name}"
    except tbl.DoesNotExist:
        return "-" 



def to_two_decimal_places(value):
    """Convert value to string with 2 decimal places."""
    try:
        return "{:.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00"


def with_rupee_symbol(value):
    """Add Indian Rupees symbol (₹) before the amount."""
    return f"₹ {value}"


def indian_format(value): 
    """Format number in Indian number system (e.g., 202300 -> 2,02,300)."""
    try:
        x = int(value)
        s = str(x)
        # First part (last 3 digits)
        last_three = s[-3:]
        # Remaining part
        remaining = s[:-3]
        # Apply comma after every 2 digits in the remaining part
        if remaining != '':
            remaining = ",".join([remaining[max(i - 2, 0):i] for i in range(len(remaining), 0, -2)][::-1])
            return f"{remaining},{last_three}"
        else:
            return last_three
    except (ValueError, TypeError):
        return "0"


def getPONumberById(tbl,po_id):
    try:
        category = tbl.objects.get(id=po_id).po_number
        return category
    except tbl.DoesNotExist:
        return '' 
    except Exception as e:
        return '' 
 
def getPONumberByInwardID(inward_id):
    try:
        inward = yarn_inward_table.objects.get(id=inward_id)
        po_id = inward.po_id  # assuming there's a po_id field
        return parent_po_table.objects.get(id=po_id).po_number
    except (yarn_inward_table.DoesNotExist, parent_po_table.DoesNotExist):
        return ''
    except Exception as e:
        return ''

# ***************GET NAME BY ID (BADGE)***************


def getNameByBadge(tbl, cat_id):
    try:
        name = tbl.objects.get(id=cat_id).name
        return f'<span class="badge text-bg-success">{name}</span>'
    except tbl.DoesNotExist:
        return '<span class="badge text-bg-success">NA</span>'
    except Exception:
        return '<span class="badge text-bg-success">NA</span>'
    

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






def getItemFabNameById(fabric_program_model, fabric_program_id):
    try:
        # Get fabric_program instance
        fabric_program = fabric_program_model.objects.get(id=fabric_program_id)

        # Get related fabric instance using fabric_id
        fabric = fabric_table.objects.get(id=fabric_program.fabric_id)

        # Combine and return names
        return f"{fabric_program.name} - {fabric.name}"
    except fabric_program_model.DoesNotExist:
        return "-"
    except fabric_table.DoesNotExist:
        return f"{fabric_program.name} - -" if 'fabric_program' in locals() else "-"
    except Exception:
        return "-"



# ***************USER PRIVILEGE***************



def check_user_access(role_id, module_id, action_type):
    try:
        module = AdminModules.objects.get(id=module_id, status=1)
    except AdminModules.DoesNotExist:
        return False, "Module not found"

    try:
        privilege = AdminPrivilege.objects.get(
            role_id=role_id,
            module_id=module.id,
            is_active=1,
            status=1
        )
    except AdminPrivilege.DoesNotExist:
        return False, "Access denied"

    action_type = action_type.lower()

    if action_type not in ['create', 'read', 'update', 'delete']: 
        return False, "Invalid action type"

    if action_type == 'create' and not privilege.is_create:
        return False, "Access denied for create"
    
    elif action_type == 'read' and not privilege.is_read:
        return False, "Access denied for read"
    
    elif action_type == 'update' and not privilege.is_update:
        return False, "Access denied for update"
    
    elif action_type == 'delete' and not privilege.is_delete:
        return False, "Access denied for delete"

    return True, "Access granted"


# ***************NUM SERIES***************


def generate_num_series(model, field_name='num_series', padding=6):  

    max_value = model.objects.aggregate(max_val=Max(field_name),status=1)['max_val']
    try:
        current = int(max_value) if max_value else 0
    except ValueError:
        current = 0
    return str(current + 1).zfill(padding)
 

import re
from django.db.models import Max 

def generate_series_hyphen_number(model, field_name, prefix='', padding=4, status_filter=True):
    """
    Generates a sequential number string with a prefix and zero-padding.
    Safely strips all non-digit characters after prefix to handle legacy data.
    """
    query = model.objects
    if status_filter:
        query = query.filter(status=1)

    max_value = query.aggregate(max_val=Max(field_name))['max_val']
    print("Max value from DB:", max_value)

    try:
        if max_value:
            # Remove prefix safely, regardless of hyphen or not
            number_part = max_value.replace(prefix, '')
            number_digits = re.sub(r'\D', '', number_part)  # Keep only digits
            current_number = int(number_digits)
        else:
            current_number = 0
    except (ValueError, AttributeError):
        current_number = 0

    new_number = f"{prefix}{str(current_number + 1).zfill(padding)}"
    print("Generated number:", new_number)
    return new_number
    



# ***************select a single row based on table and where condition***************


def selectList(tbl, whr=None, order_by='-id', status_filter=True, fields=None):
    
    """
    Fetch multiple rows from the table `tbl` based on the condition `whr` (can be dict or Q object),
    and optional `order_by` argument. Always includes condition status=1 by default.
    category = selectList(category_table, {'some_field': some_value}, order_by='name')

    """

    query = Q(status=1) if status_filter else Q()

    if whr: 
        if isinstance(whr, dict):
            query &= Q(**whr)
        elif isinstance(whr, Q):
            query &= whr
        else:
            raise ValueError("Invalid 'whr' argument. Must be dict, Q object, or None.")

    queryset = tbl.objects.filter(query).order_by(order_by)
    
    if fields:
        return queryset.values(*fields)
    
    return queryset


def select_row(tbl, whr=None):
    """
    Fetch a single row from the given table `tbl` with the condition `whr`.
    Always includes condition status=1 by default.
    """
    query = Q(status=1)

    if whr is not None:
        if isinstance(whr, dict):
            query &= Q(**whr)
        elif isinstance(whr, Q):
            query &= whr
        else:
            raise ValueError("Invalid 'whr' argument. Must be dict, Q object, or None.")

    return tbl.objects.filter(query).first()


# ***************DECODE ID***************


def decode_base64_id(encoded_id):   
    try:
        decoded_bytes = base64.b64decode(encoded_id)
        return decoded_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError, AttributeError):
        return None
    

# ***************EMPLOYEE CODE***************


def generate_company_code(company_id):
    prefix = 'EMP'
    
    company = company_table.objects.filter(id=company_id, status=1).first()
    if company and company.company_code:
        prefix = company.company_code

    latest = employee_table.objects.filter(employee_code__startswith=prefix + "-") \
                                   .aggregate(Max('num_series'))

    last_number = latest['num_series__max']
    next_number = int(last_number) + 1 if last_number and last_number.isdigit() else 1

    num_series = str(next_number).zfill(5)
    employee_code = f"{prefix}-{num_series}"

    return employee_code


