from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
from program_app.models import knitting_table, sub_knitting_table
from yarn.models import *
from company.models import *
from grey_fabric.models import * 
from employee.models import * 

from purchase_app.models import *
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
from common.utils import *


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
from invoice.models import * 
from django.utils.timezone import make_aware




def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 


# Create your views here.

 
def invoices(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1) 
        # party = party_table.objects.filter(status=1,is_supplier=1) 
        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        # party =  party_table.objects.filter(status=1).filter(is_trader=1)
 
        yarn_count = count_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        lot = grey_fabric_po_table.objects.filter(status=1).distinct()

        program = knitting_table.objects.filter(status=1,is_grey_fabric=1)
        return render(request,'invoice_list.html',{'program':program,'supplier':supplier,'party':party,'product':product,'yarn_count':yarn_count,'lot':lot})
    else:
        return HttpResponseRedirect("/admin")
    


def generate_invoice_no():
    last_purchase = parent_invoice_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.invoice_no:
        match = re.search(r'INV-(\d+)', last_purchase.invoice_no)
        if match:
            next_num = int(match.group(1)) + 1
        else: 
            next_num = 1 
    else:
        next_num = 1

    return f"INV-{next_num:03d}"


def invoice_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1) 

        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)

        yarn_count = count_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        lot = grey_fabric_po_table.objects.filter(status=1).distinct()

        invoice_no = generate_invoice_no()
        program = knitting_table.objects.filter(status=1,is_grey_fabric=1)
        quality = quality_table.objects.filter(status=1)
        style   = style_table.objects.filter(status=1)  
        return render(request,'invoice_add.html',{'program':program,'supplier':supplier,'party':party,'product':product,'yarn_count':yarn_count,'lot':lot,
                                                  'invoice_no':invoice_no,'quality':quality,'style':style})
    else: 
        return HttpResponseRedirect("/admin") 