
import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
# from software_app.models import count_table, knitting_table, parent_po_table, party_table, product_table, sub_yarn_deliver_table, sub_yarn_inward_table, yarn_delivery_table, yarn_inward_table
from software_app.models import *

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

# Create your views here.





def dashboard(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        return render(request,'dashboard.html') 
    else:
        return HttpResponseRedirect("/signin")

