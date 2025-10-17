from cairo import Status
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
from django.db import connection


# ```````````````````````````````````````````REPORTS `````````````````````````````




# def stock_summary_report(request):
#     if 'user_id' in request.session: 
#         user_id = request.session['user_id']
#         party = party_table.objects.filter(status=1,is_compacting=1)
#         fabric_program = fabric_program_table.objects.filter(status=1)
#         quality = quality_table.objects.filter(status=1)
#         style = style_table.objects.filter(status=1)

#         lot = (
#             cutting_program_table.objects
#             .filter(status=1)
#             .values('work_order_no')  # Group by work_order_no
#             .annotate(
#                 total_gross_wt=Sum('total_quantity'),  
             
#             )    
#             .order_by('work_order_no')
#         )

#         lot_no_list = (
#             yarn_delivery_table.objects
#             .filter(status=1)
#             .values('lot_no')        # select only lot_no
#             .distinct()              # get unique ones
#         )
#         yarn = count_table.objects.filter(status=1)
#         return render(request,'reports/stock_summary_report.html',{'lot_no':lot_no_list,'party':party,'fabric_program':fabric_program,'lot':lot,'quality':quality,'style':style,'yarn':yarn })
#     else:
#         return HttpResponseRedirect("/admin")
    

def stock_summary_report(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        lot_no_list = (
            yarn_delivery_table.objects
            .filter(status=1) 
            .values('lot_no')        # select only lot_no
            .distinct()              # get unique ones
        )

        yarn = count_table.objects.filter(status=1)
         
        return render(request,'reports/stock_summary_report.html',{'lot_no':lot_no_list,'party':party,'fabric_program':fabric_program,
                                                                #    'lot':lot,
                                                                   'quality':quality,'style':style,'yarn':yarn })
    else:
        return HttpResponseRedirect("/admin")
    


def grey_fabric_stock_report(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        lot_no_list = (
            yarn_delivery_table.objects
            .filter(status=1)
            .values('lot_no')        # select only lot_no
            .distinct()              # get unique ones
        )
        print('lots:',lot_no_list)
        yarn = count_table.objects.filter(status=1)
        return render(request,'reports/grey_fabric_report.html',{'lot_no':lot_no_list,'party':party,'fabric_program':fabric_program,
                                                                #    'lot':lot,
                                                                   'quality':quality,'style':style,'yarn':yarn })
    else:
        return HttpResponseRedirect("/admin")
    




def dyed_fabric_stock_report(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        lot_no_list = (
            yarn_delivery_table.objects
            .filter(status=1)
            .values('lot_no')        # select only lot_no
            .distinct()              # get unique ones
        )
        yarn = count_table.objects.filter(status=1)
        return render(request,'reports/dyed_fabric_report.html',{'lot_no':lot_no_list,'party':party,'fabric_program':fabric_program,
                                                                #    'lot':lot,
                                                                   'quality':quality,'style':style,'yarn':yarn })
    else:
        return HttpResponseRedirect("/admin")
    



def lot_wise_stock_summary_report(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        party = party_table.objects.filter(status=1,is_compacting=1)
        fabric_program = fabric_program_table.objects.filter(status=1)
        quality = quality_table.objects.filter(status=1)
        style = style_table.objects.filter(status=1)

        lot_no_list = (
            yarn_delivery_table.objects
            .filter(status=1)
            .values('lot_no')        # select only lot_no
            .distinct()              # get unique ones
        )
        yarn = count_table.objects.filter(status=1)
        return render(request,'reports/lot_wise_summary_report.html',{'lot_no':lot_no_list,'party':party,'fabric_program':fabric_program,
                                                                #    'lot':lot,
                                                                   'quality':quality,'style':style,'yarn':yarn })
    else:
        return HttpResponseRedirect("/admin")
    





@csrf_exempt
def refresh_data_24_9_2025(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        yarn_count_id = request.POST.get('yarn_count_id')
        party_id = request.POST.get('party_id')
        params = []

        # Base query
        query = """
            SELECT 
                X.po_id AS po_id,
                yp.name AS po_name,
                X.inward_id AS inward_id,
                y_inw.inward_number,
		        y_inw.inward_date,
                X.inward_id AS id,
                Y.po_number AS po_number,
                Y.party_id AS party_id,
                X.out_party_id,
                out_p.name as out_party_name,
                p.name AS party_name,
                X.yarn_count_id AS yarn_count_id,
                X.yarn_count_name,
                Y.po_bag AS po_bag,
                Y.po_bag_wt AS po_bag_wt,
                Y.po_quantity AS po_quantity,
                SUM(X.in_quantity) AS total_in_quantity,
                SUM(X.out_quantity) AS total_out_quantity,
                (SUM(X.in_quantity) - SUM(X.out_quantity)) AS balance_in_quantity
            FROM yarn_in_sum X
            JOIN (
                SELECT 
                    y_po_sum.po_id AS po_id,
                    y_po_sum.po_number AS po_number,
                    y_po_sum.party_id AS party_id,
                    y_po_sum.po_bag AS po_bag,
                    y_po_sum.po_bag_wt AS po_bag_wt,
                    y_po_sum.yarn_count_id AS yarn_count_id,
                    SUM(y_po_sum.po_quantity) AS po_quantity
                FROM y_po_sum
                GROUP BY 
                    y_po_sum.po_id,
                    y_po_sum.party_id,
                    y_po_sum.yarn_count_id,
                    y_po_sum.po_number,
                    y_po_sum.po_bag,
                    y_po_sum.po_bag_wt
            ) Y 
              ON X.po_id = Y.po_id AND X.yarn_count_id = Y.yarn_count_id
            LEFT JOIN party AS p ON Y.party_id = p.id AND p.status = 1
            LEFT JOIN party AS out_p ON X.out_party_id = p.id AND p.status = 1
            LEFT JOIN tm_yarn_inward AS y_inw ON X.inward_id =y_inw.id AND y_inw.status=1
            LEFT JOIN tm_yarn_po AS yp ON  X.po_id =yp.id AND yp.status=1
            WHERE 1=1
        """

        # Apply filters only once
        if yarn_count_id:
            query += " AND X.yarn_count_id = %s"
            params.append(yarn_count_id)

        if party_id:
            query += " AND Y.party_id = %s"
            params.append(party_id)

        query += """
            GROUP BY 
                X.po_id,
                Y.party_id,
                X.yarn_count_id,
                Y.po_quantity,
                Y.po_number
             --   Y.po_bag,
            --   Y.po_bag_wt,
             --   X.inward_id
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                "lot_no": 0,
                "po_id": data["po_id"],
                "po_name":data['po_name'],  
                "out_party_id":data["out_party_id"], 
                "out_party_name":data["out_party_name"],
                "party_name": data["party_name"],
                "yarn_count": data["yarn_count_name"],
                "inward_id": data["inward_id"],
                "inward_no":data['inward_number'],
                "inward_date":data['inward_date'],
                "po_number": data["po_number"],
                "party_id": data["party_id"],
                "yarn_count_id": data["yarn_count_id"],
                "po_bag": data["po_bag"],
                "po_bag_wt": float(data["po_bag_wt"]),
                "po_quantity": float(data["po_quantity"]),
                "total_in_quantity": float(data["total_in_quantity"]),
                "total_out_quantity": float(data["total_out_quantity"]),
                "balance_in_quantity": float(data["balance_in_quantity"]),
            })

        return JsonResponse({"status": "success", "data": result})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)





@csrf_exempt
def refresh_data(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        yarn_count_id = request.POST.get('yarn_count_id')
        party_id = request.POST.get('party_id')
        params = []

        # Base query
        query = """
            SELECT 
                yp.name AS po_name,
                X.yarn_count_id,
                X.yarn_count_name,
                
                SUM(Y.po_bag) AS total_tat_bag,
                SUM(Y.po_bag_wt) AS total_bag_weight,
                SUM(Y.po_quantity) AS total_po_quantity,
                
                SUM(X.in_quantity) AS total_in_quantity, 
                SUM(X.out_quantity) AS total_out_quantity,
                SUM(X.in_quantity) - SUM(X.out_quantity) AS balance_in_quantity

            FROM yarn_in_sum X

            JOIN ( 
                SELECT 
                    po_id,
                    yarn_count_id,
                    SUM(po_quantity) AS po_quantity,
                    SUM(po_bag) AS po_bag,
                    SUM(po_bag_wt) AS po_bag_wt
                FROM y_po_sum
                GROUP BY po_id, yarn_count_id
            ) Y ON X.po_id = Y.po_id AND X.yarn_count_id = Y.yarn_count_id

            LEFT JOIN tm_yarn_po AS yp ON X.po_id = yp.id AND yp.status = 1

            WHERE 1=1
        """

        # Apply filters only once
        if yarn_count_id:
            query += " AND X.yarn_count_id = %s"
            params.append(yarn_count_id)

        if party_id:
            query += " AND Y.party_id = %s"
            params.append(party_id)

        query += """
            GROUP BY 
            --    X.po_id,
             --   Y.party_id,
                yp.name,
                X.yarn_count_id
              --  Y.po_quantity
             --   Y.po_number
             --   Y.po_bag,
            --   Y.po_bag_wt,
             --   X.inward_id
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                "lot_no": 0,
                "po_name":data['po_name'],  
                "yarn_count": data["yarn_count_name"],
                # "inward_id": data["inward_id"],
                # "inward_no":data['inward_number'],
                # "inward_date":data['inward_date'],
                # "po_number": data["po_number"],
                # "party_id": data["party_id"],
                "yarn_count_id": data["yarn_count_id"],
                # "po_bag": data["po_bag"],
                # "po_bag_wt": float(data["po_bag_wt"]),
                # "po_quantity": float(data["po_quantity"]),
                "total_in_quantity": float(data["total_in_quantity"]),
                "total_out_quantity": float(data["total_out_quantity"]),
                "balance_in_quantity": float(data["balance_in_quantity"]),
            })

        return JsonResponse({"status": "success", "data": result})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




@csrf_exempt
def get_yarn_transactions(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    yarn_count = request.POST.get('yarn_count')  # example: "40'S RL"
    po_name = request.POST.get('po_name')        # example: "FANCY"
    txn_type = request.POST.get('type')          # "inward" or "outward"

    if not (yarn_count and po_name and txn_type):
        return JsonResponse({"status": "error", "message": "Missing parameters"}, status=400)

    try:
        if txn_type == 'inward':
            query = """
                SELECT  
                    p.name AS party_name, 
                    tm.inward_number,
                    tm.inward_date,
                    tx.bag,
                    tx.per_bag,
                    tx.quantity
                FROM tx_yarn_inward tx
                JOIN tm_yarn_inward tm ON tx.inward_id = tm.id AND tm.status = 1
                LEFT JOIN party p ON tm.party_id = p.id
                LEFT JOIN tm_yarn_po po ON tm.po_id = po.id 
                WHERE po.name = %s AND tx.yarn_count_name = %s
            """ 
        elif txn_type == 'outward':  
            query = """
                
                SELECT 
                    p.name AS party_name,
                    tm.do_number,
                    tm.delivery_date,
                    tx.bag,
                    tx.per_bag,
                    tx.quantity
                    FROM tx_yarn_outward tx
                    JOIN tm_yarn_outward tm ON tx.tm_id = tm.id AND tm.status = 1
                    LEFT JOIN party p ON tm.party_id = p.id

                WHERE po.name = %s AND tx.yarn_count_name = %s
            """
        else:
            return JsonResponse({"status": "error", "message": "Invalid type"}, status=400)

        params = [po_name, yarn_count]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        data = [dict(zip(columns, row)) for row in rows]

        return JsonResponse({"status": "success", "data": data})
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



@csrf_exempt
def get_yarn_outward_lists(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    yarn_count_id = request.GET.get('yarn_count_id')
    po_name = request.GET.get('po_name')  # Optional

    if not yarn_count_id:
        return JsonResponse({"status": "error", "message": "Missing yarn_count_id"}, status=400)

    try:
        # First: fetch balance_in_quantity and total_in_quantity
        balance_query = """
            SELECT 
                SUM(X.in_quantity) AS total_in_quantity, 
                SUM(X.out_quantity) AS total_out_quantity,
                SUM(X.in_quantity) - SUM(X.out_quantity) AS balance_in_quantity
            FROM yarn_in_sum X
            JOIN (
                SELECT po_id, yarn_count_id
                FROM y_po_sum
                GROUP BY po_id, yarn_count_id
            ) Y ON X.po_id = Y.po_id AND X.yarn_count_id = Y.yarn_count_id
            WHERE X.yarn_count_id = %s 
            --  AND balance_in_quantity >0
        """

        with connection.cursor() as cursor:
            cursor.execute(balance_query, [yarn_count_id])
            balance_row = cursor.fetchone()

        total_in_quantity = float(balance_row[0]) if balance_row and balance_row[0] is not None else 0.00
        total_out_quantity = float(balance_row[0]) if balance_row and balance_row[0] is not None else 0.00
        balance_in_quantity = float(balance_row[2]) if balance_row and balance_row[2] is not None else 0.00

        # Second: fetch outward records
        query = """
            SELECT 
                p.name AS party_name,
                tm.lot_no AS lot_no,
                yp.name AS po_name,
                tm.do_number,
                tm.delivery_date,
                tx.bag,
                tx.per_bag,
                tx.quantity
            FROM tx_yarn_outward tx 
            JOIN tm_yarn_outward tm ON tx.tm_id = tm.id AND tm.status = 1
            LEFT JOIN party p ON tm.party_id = p.id
            LEFT JOIN tm_yarn_po yp ON tx.po_id = yp.id AND yp.status = 1
            WHERE tx.yarn_count_id = %s
        """

        params = [yarn_count_id]

        if po_name:
            query += " AND yp.name = %s"
            params.append(po_name)

        query += " ORDER BY tm.delivery_date DESC"

        with connection.cursor() as cursor:
            cursor.execute(query, params) 
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        data = [dict(zip(columns, row)) for row in rows]

        # Add available quantity & total inward to each record 
        for item in data: 
            item['balance_in_quantity'] = balance_in_quantity
            item['total_in_quantity'] = total_in_quantity
            item['total_out_quantity'] = total_out_quantity
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




@csrf_exempt
def get_yarn_outward_lists_crt(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    yarn_count_id = request.GET.get('yarn_count_id')
    po_name = request.GET.get('po_name')  # Optional

    if not yarn_count_id:
        return JsonResponse({"status": "error", "message": "Missing yarn_count_id"}, status=400)

    try:
        # Base query
        query = """
            SELECT 
                p.name AS party_name,
                tm.lot_no AS lot_no,
                yp.name AS po_name,
                tm.do_number,
                tm.delivery_date,
                tx.bag,
                tx.per_bag,
                tx.quantity
            FROM tx_yarn_outward tx
            JOIN tm_yarn_outward tm ON tx.tm_id = tm.id AND tm.status = 1
            LEFT JOIN party p ON tm.party_id = p.id
            LEFT JOIN tm_yarn_po yp ON tx.po_id = yp.id AND yp.status = 1
            WHERE tx.yarn_count_id = %s
        """

        # Parameters list
        params = [yarn_count_id]

        # If PO Name is provided, add to WHERE clause and params
        if po_name:
            query += " AND yp.name = %s"
            params.append(po_name)

        query += " ORDER BY tm.delivery_date DESC"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        data = [dict(zip(columns, row)) for row in rows]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




@csrf_exempt
def get_yarn_outward_lists_test(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    yarn_count_id = request.GET.get('yarn_count_id')
    po_name = request.GET.get('po_name')

    if not yarn_count_id:
        return JsonResponse({"status": "error", "message": "Missing yarn_count_id"}, status=400)

    try:
        query = """
            SELECT 
                p.name AS party_name,
                tm.lot_no AS lot_no,
                yp.name AS po_name,
                tm.do_number,
                tm.delivery_date,
                tx.bag,
                tx.per_bag,
                tx.quantity
            FROM tx_yarn_outward tx
            JOIN tm_yarn_outward tm ON tx.tm_id = tm.id AND tm.status = 1
            LEFT JOIN party p ON tm.party_id = p.id
            LEFT JOIN tm_yarn_po yp ON tx.po_id = yp.id AND yp.status=1
            WHERE tx.yarn_count_id = %s
            if po_name:
                query += " AND po.name = %s"
                params.append(po_name)
 
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [yarn_count_id])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        data = [dict(zip(columns, row)) for row in rows]

        return JsonResponse(data, safe=False)  # Return raw list to match JS expectation

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



# @csrf_exempt
# def get_yarn_outward_lists(request):
#     if request.method != 'POST':
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

#     yarn_count = request.POST.get('yarn_count')  # Example: "40'S RL"
#     # po_name = request.POST.get('po_name')        # Optional

#     if not yarn_count:
#         return JsonResponse({"status": "error", "message": "Missing yarn_count"}, status=400)

#     try:
#         query = """
#             SELECT 
#                 p.name AS party_name,
#                 tm.do_number,
#                 tm.delivery_date,
#                 tx.bag,
#                 tx.per_bag,
#                 tx.quantity 
#             FROM tx_yarn_outward tx
#             JOIN tm_yarn_outward tm ON tx.tm_id = tm.id AND tm.status = 1
#             LEFT JOIN party p ON tm.party_id = p.id
#             WHERE tx.yarn_count_id = %s

#         """

#         params = [yarn_count]

#         # if po_name:
#         #     query += " AND po.name = %s"
#         #     params.append(po_name)

#         query += " ORDER BY tm.delivery_date DESC"

#         with connection.cursor() as cursor:
#             cursor.execute(query, params)
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]

#         data = [dict(zip(columns, row)) for row in rows]

#         return JsonResponse({"status": "success", "data": data})

#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)



# ````````````````````````````` grey fabric lot summary list ```````````````````````````````````````````````



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# @csrf_exempt
# def get_grey_fabric_lot_summary_list(request):
#     if request.method != 'POST':
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

#     try:
#         party_id = request.POST.get('party_id')
#         program_id = request.POST.get('program_id')
#         lot_no = request.POST.get('lot_no')
# #  SELECT 
#         #         X.out_id AS out_id,
#         #         X.outward_no AS outward_no,
#         #         X.lot_no AS lot_no,
#         #         X.program_id AS program_id,
#         #         X.program_no AS program_no,
#         #      --   # X.party_id AS party_id,
#         #      --   # pr.name AS party,
#         #         SUM(X.total_wt) AS outward_wt,
#         #         SUM(X.inward_wt) AS inward_wt,
#         #         (SUM(X.total_wt) - SUM(X.inward_wt)) AS balance_wt
#         #     FROM grey_outward_available_sum X
#         #   --  left join party AS pr ON X.party_id = pr.id AND pr.status=1 
#         #     WHERE 1=1
#         params = []
#         query = """
#             SELECT  
#                 gf.lot_no,

#                 -- ✅ Total Grey Fabric Outward (from tx_gf_delivery)
#                 COALESCE(SUM(gf.roll_wt), 0) AS total_gf_outward,

#                 -- ✅ Total Dyed Fabric Inward (from tx_dyed_fab_inward)
#                 COALESCE(SUM(di.roll_wt), 0) AS total_dyed_fab_inward,

#                 -- ✅ Pending Outward Calculation
#                 COALESCE(SUM(gf.roll_wt), 0) - COALESCE(SUM(di.roll_wt), 0) AS pending_outward

#             FROM tx_gf_delivery gf
#             LEFT JOIN tx_dyed_fab_inward di 
#                 ON gf.lot_no = di.lot_no
#                 AND gf.company_id = di.company_id

#             WHERE 
#                 gf.is_active = 1
#                 AND (di.is_active = 1 OR di.is_active IS NULL)

#             GROUP BY 
#                 gf.lot_no

#             ORDER BY 
#                 gf.lot_no;
                
#         """

#         # Apply filters if given
#         if lot_no:
#             query += " AND gf.lot_no = %s"
#             params.append(lot_no)
#         # if party_id:
#         #     query += " AND X.party_id = %s"
#         #     params.append(party_id)
#         # if program_id:
#         #     query += " AND X.program_id = %s"
#         #     params.append(program_id)

#         query += """
#             GROUP BY 
#                 X.out_id,
#                 X.outward_no,
#                 X.lot_no,
#                 X.program_id,
#                 X.program_no
#            --     X.party_id
#             ORDER BY X.lot_no
#         """

#         with connection.cursor() as cursor:
#             cursor.execute(query, params)
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]
 
#         result = []
#         for row in rows: 
#             data = dict(zip(columns, row))
#             result.append({
#                 "out_id": data["out_id"], 
#                 "outward_no": data["outward_no"], 
#                 "lot_no": data["lot_no"],
#                 "program_id": data["program_id"],
#                 "program_no": data["program_no"],
#                 # "party_id": data["party_id"],
#                 # "party":data['party'],
#                 "outward_wt": float(data["total_gf_outward"] or 0),
#                 "inward_wt": float(data["total_dyed_fab_inward"] or 0),
#                 "balance_wt": float(data["pending_outward"] or 0),
#             })

#         return JsonResponse({"status": "success", "data": result}, status=200)

#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection

@csrf_exempt
def get_grey_fabric_lot_summary_list(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        lot_no = request.POST.get('lot_no')

        query = """
            SELECT 
                lot_no,
                SUM(out_wt) AS total_out_wt,
                SUM(in_wt) AS total_in_wt,
                SUM(out_wt) - SUM(in_wt) AS pending_outward
            FROM (
                SELECT 
                    tx.lot_no,
                    tx.roll_wt AS out_wt,
                    0 AS in_wt
                FROM 
                    tx_gf_delivery AS tx
                WHERE 
                    tx.status = 1
                    AND tx.is_active = 1
                {gf_lot_filter}

                UNION ALL 

                SELECT 
                    td.lot_no,
                    0 AS out_wt,
                    td.gross_wt AS in_wt
                FROM 
                    tx_dyed_fab_inward AS td
                WHERE 
                    td.status = 1
                    AND td.is_active = 1
                    {dfi_lot_filter}
            ) AS combined
            GROUP BY 
                lot_no
            ORDER BY 
                lot_no
        """

        # Handle dynamic filtering for lot_no
        gf_lot_filter = ""
        dfi_lot_filter = ""
        params = []

        if lot_no:
            gf_lot_filter = "AND tx.lot_no = %s"
            dfi_lot_filter = "AND td.lot_no = %s"
            params.extend([lot_no, lot_no])

        # Format final query with placeholders
        query = query.format(gf_lot_filter=gf_lot_filter, dfi_lot_filter=dfi_lot_filter)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                "lot_no": data["lot_no"],
                "outward_wt": float(data["total_out_wt"] or 0),
                "inward_wt": float(data["total_in_wt"] or 0),
                "balance_wt": float(data["pending_outward"] or 0),
            })

        return JsonResponse({"status": "success", "data": result}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




@csrf_exempt
def get_grey_fabric_lot_summary_list_11_10_2025(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        lot_no = request.POST.get('lot_no')

        query = """
            SELECT 
                gf.lot_no,
                COALESCE(SUM(gf.roll_wt), 0) AS total_gf_outward,
                COALESCE(SUM(di.roll_wt), 0) AS total_dyed_fab_inward,
                COALESCE(SUM(gf.roll_wt), 0) - COALESCE(SUM(di.roll_wt), 0) AS pending_outward
            FROM tx_gf_delivery gf
            LEFT JOIN tx_dyed_fab_inward di 
                ON gf.lot_no = di.lot_no
                AND gf.company_id = di.company_id
            WHERE 
                gf.is_active = 1
                AND (di.is_active = 1 OR di.is_active IS NULL)
        """

        params = []
        if lot_no:
            query += " AND gf.lot_no = %s"
            params.append(lot_no) 

        query += """
            GROUP BY gf.lot_no
            ORDER BY gf.lot_no
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                "lot_no": data["lot_no"],
                "outward_wt": float(data["total_gf_outward"] or 0),
                "inward_wt": float(data["total_dyed_fab_inward"] or 0),
                "balance_wt": float(data["pending_outward"] or 0),
            })

        return JsonResponse({"status": "success", "data": result}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



@csrf_exempt
def get_grey_fabric_lot_summary_list_crt(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        party_id = request.POST.get('party_id')
        program_id = request.POST.get('program_id')
        lot_no = request.POST.get('lot_no')

        params = []
        query = """
            SELECT 
                gf.lot_no,

                COALESCE(SUM(gf.roll_wt), 0) AS total_gf_outward,
                COALESCE(SUM(di.roll_wt), 0) AS total_dyed_fab_inward,
                COALESCE(SUM(gf.roll_wt), 0) - COALESCE(SUM(di.roll_wt), 0) AS pending_outward

            FROM tx_gf_delivery gf
            LEFT JOIN tx_dyed_fab_inward di 
                ON gf.lot_no = di.lot_no
                AND gf.company_id = di.company_id

            WHERE 
                gf.is_active = 1
                AND (di.is_active = 1 OR di.is_active IS NULL)
        """

        # Add filters
        if lot_no:
            query += " AND gf.lot_no = %s"
            params.append(lot_no)
        if program_id:
            query += " AND gf.program_id = %s"
            params.append(program_id)
        if party_id:
            query += " AND gf.party_id = %s"
            params.append(party_id)

        query += """
            GROUP BY gf.lot_no
            ORDER BY gf.lot_no
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                "lot_no": data.get("lot_no"),
                "outward_wt": float(data.get("total_gf_outward", 0)),
                "inward_wt": float(data.get("total_dyed_fab_inward", 0)),
                "balance_wt": float(data.get("pending_outward", 0)),
            })

        return JsonResponse({"status": "success", "data": result}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




@csrf_exempt
def get_grey_fabric_lot_list(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    lot_no = request.GET.get('lot_no')
    txn_type = request.GET.get('type')  # new param: inward or outward

    if not lot_no or not txn_type:
        return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)

    try:
        if txn_type == 'outward':
            # Outward logic (same as you already have)
            ...
            return JsonResponse(data, safe=False)

        elif txn_type == 'inward':
            # ✅ NEW: Inward logic from tm_dyed_fab_inward + tx_dyed_fab_inward
            query = """
                SELECT 
                    tm.inward_number AS inward_no,
                    tm.receive_date,
                    p.name AS party_name,
                    tx.color_id,
                    clr.name AS color,
                    tx.dia_id,
                    d.name AS dia,
                    tx.gross_wt AS inward_qty
                FROM tm_dyed_fab_inward tm
                JOIN tx_dyed_fab_inward tx ON tm.id = tx.tm_id AND tx.status = 1
                LEFT JOIN party p ON tm.party_id = p.id
                LEFT JOIN color clr ON tx.color_id = clr.id AND clr.status=1
                LEFT JOIN dia d ON tx.dia_id = d.id AND d.status=1
                WHERE tx.lot_no = %s
                ORDER BY tm.receive_date DESC
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [lot_no])
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]

            # You can enrich this with color name/dia name if needed using lookups

            return JsonResponse(data, safe=False)

        else:
            return JsonResponse({"status": "error", "message": "Invalid type"}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)





@csrf_exempt
def get_lot_out_list(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    lot_no = request.GET.get('lot_no')
    txn_type = request.GET.get('type')  # new param: inward or outward

    if not lot_no or not txn_type:
        return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)

    try:
        if txn_type == 'inward':
            # Outward logic (same as you already have)
            ...
            return JsonResponse(data, safe=False)

        elif txn_type == 'outward':
            # ✅ NEW: Inward logic from tm_dyed_fab_inward + tx_dyed_fab_inward
            query = """
                SELECT 
                    tm.do_number AS outward_no,
                    tm.delivery_date,
                    p.name AS party_name,
                    tx.color_id,
                    clr.name AS color,
                    tx.dia_id,
                    d.name AS dia,
                    tx.roll_wt AS quantity
                FROM tm_gf_delivery tm
                JOIN tx_gf_delivery tx ON tm.id = tx.tm_id AND tx.status = 1
                LEFT JOIN party p ON tm.party_id = p.id
                LEFT JOIN color clr ON tx.color_id = clr.id AND clr.status=1
                LEFT JOIN dia d ON tx.dia_id = d.id AND d.status=1
                WHERE tx.lot_no = %s
                ORDER BY tm.delivery_date DESC
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [lot_no])
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]

            # You can enrich this with color name/dia name if needed using lookups

            return JsonResponse(data, safe=False)

        else:
            return JsonResponse({"status": "error", "message": "Invalid type"}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)






@csrf_exempt
def get_gf_available_balance(request):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    lot_no = request.GET.get('lot_no')
    txn_type = request.GET.get('type')  # new param: inward or outward

    if not lot_no or not txn_type:
        return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)

    try:
        if txn_type == 'inward':
            # Outward logic (same as you already have)
            ...
            return JsonResponse(data, safe=False)
# SELECT 
#                     tm.do_number AS outward_no,
#                     tm.delivery_date,
#                     p.name AS party_name,
#                     tx.color_id,
#                     clr.name AS color,
#                     tx.dia_id,
#                     d.name AS dia,
#                     tx.roll_wt AS quantity
#                 FROM tm_gf_delivery tm
#                 JOIN tx_gf_delivery tx ON tm.id = tx.tm_id AND tx.status = 1
#                 LEFT JOIN party p ON tm.party_id = p.id
#                 LEFT JOIN color clr ON tx.color_id = clr.id AND clr.status=1
#                 LEFT JOIN dia d ON tx.dia_id = d.id AND d.status=1
#                 WHERE tx.lot_no = %s
#                 ORDER BY tm.delivery_date DESC
        elif txn_type == 'pending':
            # ✅ NEW: Inward logic from tm_dyed_fab_inward + tx_dyed_fab_inward
            query = """
                SELECT 
                    lot_no,
                    party,
                    color_id,
                    color,
                    dia_id,
                    dia,
                    SUM(out_wt) AS total_out_wt,
                    SUM(in_wt) AS total_in_wt,
                    SUM(out_wt) - SUM(in_wt)  AS pending_outward
                FROM (
                    -- Outward (delivery)
                    SELECT 
                        tx.lot_no,
                        pr.name AS party,
                        tx.color_id,
                        clr.name AS color,
                        tx.dia_id,
                        d.name AS dia,
                        tx.roll_wt AS out_wt,
                        0 AS in_wt
                    FROM tx_gf_delivery AS tx
                    LEFT JOIN tm_gf_delivery AS tmg ON tx.tm_id = tmg.id AND tmg.status = 1
                    LEFT JOIN party AS pr ON tmg.party_id = pr.id AND pr.status = 1
                    LEFT JOIN color AS clr ON tx.color_id = clr.id AND clr.status = 1
                    LEFT JOIN dia AS d ON tx.dia_id = d.id AND d.status = 1
                    WHERE tx.status = 1 AND tx.lot_no = %s

                    UNION ALL

                    -- Inward (receive)
                    SELECT 
                        td.lot_no,
                        pr.name AS party,
                        td.color_id,
                        clr.name AS color,
                        td.dia_id,
                        d.name AS dia,
                        0 AS out_wt,
                        td.gross_wt AS in_wt
                    FROM tx_dyed_fab_inward AS td
                    LEFT JOIN tm_dyed_fab_inward AS tm ON td.tm_id = tm.id AND tm.status = 1
                    LEFT JOIN party AS pr ON tm.party_id = pr.id AND pr.status = 1
                    LEFT JOIN color AS clr ON td.color_id = clr.id AND clr.status = 1
                    LEFT JOIN dia AS d ON td.dia_id = d.id AND d.status = 1
                    WHERE td.status = 1 AND td.lot_no = %s
                ) AS combined
                GROUP BY 
                    lot_no,
                    party,
                    color_id,
                    color,
                    dia_id,
                    dia
                ORDER BY 
                    color,
                    dia;


                
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [lot_no,lot_no])
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]

            # You can enrich this with color name/dia name if needed using lookups

            return JsonResponse(data, safe=False)

        else:
            return JsonResponse({"status": "error", "message": "Invalid type"}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



# @csrf_exempt
# def get_grey_fabric_lot_list(request):
#     if request.method != 'GET':
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

#     lot_no = request.GET.get('lot_no')

#     if not lot_no:
#         return JsonResponse({"status": "error", "message": "Missing lot_no"}, status=400)

#     try:
#         # First: fetch balance_in_quantity and total_in_quantity
#         balance_query = """
#             SELECT 
#                 SUM(X.in_quantity) AS total_in_quantity, 
#                 SUM(X.out_quantity) AS total_out_quantity,
#                 SUM(X.in_quantity) - SUM(X.out_quantity) AS balance_in_quantity
#             FROM yarn_in_sum X
#             JOIN (
#                 SELECT po_id, lot_no
#                 FROM y_po_sum
#                 GROUP BY po_id, lot_no
#             ) Y ON X.po_id = Y.po_id AND X.lot_no = Y.lot_no
#             WHERE X.lot_no = %s 
#             --  AND balance_in_quantity >0
#         """

#         with connection.cursor() as cursor:
#             cursor.execute(balance_query, [lot_no])
#             balance_row = cursor.fetchone()

#         total_in_quantity = float(balance_row[0]) if balance_row and balance_row[0] is not None else 0.00
#         total_out_quantity = float(balance_row[0]) if balance_row and balance_row[0] is not None else 0.00
#         balance_in_quantity = float(balance_row[2]) if balance_row and balance_row[2] is not None else 0.00

#         # Second: fetch outward records
#         query = """
#             SELECT 
#                 p.name AS party_name,
#                 tm.lot_no AS lot_no,
#                 yp.name AS po_name,
#                 tm.do_number,
#                 tm.delivery_date,
#                 tx.bag,
#                 tx.per_bag,
#                 tx.quantity
#             FROM tx_yarn_outward tx 
#             JOIN tm_yarn_outward tm ON tx.tm_id = tm.id AND tm.status = 1
#             LEFT JOIN party p ON tm.party_id = p.id
#             LEFT JOIN tm_yarn_po yp ON tx.po_id = yp.id AND yp.status = 1
#             WHERE tx.lot_no = %s
#         """

#         params = [lot_no]

#         # if po_name:
#         #     query += " AND yp.name = %s"
#         #     params.append(po_name)

#         query += " ORDER BY tm.delivery_date DESC"

#         with connection.cursor() as cursor:
#             cursor.execute(query, params) 
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]

#         data = [dict(zip(columns, row)) for row in rows]

#         # Add available quantity & total inward to each record 
#         for item in data: 
#             item['balance_in_quantity'] = balance_in_quantity
#             item['total_in_quantity'] = total_in_quantity
#             item['total_out_quantity'] = total_out_quantity
#         return JsonResponse(data, safe=False)

#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)



# ```````````````````````````````````````` dyed fab inward summary report ````````````````````````````````````````````


@csrf_exempt
def get_dyed_fabric_lot_summary_list(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        lot_no = request.POST.get('lot_no')

        query = """
            SELECT 
                lot_no,
                SUM(out_wt) AS total_out_wt,
                SUM(in_wt) AS total_in_wt,
                SUM(out_wt) - SUM(in_wt) AS pending_outward
            FROM (
                SELECT 
                    tx.lot_no,
                    tx.gross_wt AS out_wt,
                    0 AS in_wt
                FROM 
                    tx_dyed_fab_inward AS tx
                WHERE 
                    tx.status = 1
                    AND tx.is_active = 1
            {gf_lot_filter}
                UNION ALL 

                SELECT 
                    td.lot_no,
                    0 AS out_wt,
                    td.wt AS in_wt
                FROM 
                    tx_cutting_entry AS td
                WHERE 
                    td.status = 1
                    AND td.is_active = 1
                {dfi_lot_filter}  
            ) AS combined
            GROUP BY 
                lot_no
            ORDER BY 
                lot_no
        """

        # Handle dynamic filtering for lot_no
        gf_lot_filter = ""
        dfi_lot_filter = ""
        params = []

        if lot_no:
            gf_lot_filter = "AND tx.lot_no = %s"
            dfi_lot_filter = "AND td.lot_no = %s"
            params.extend([lot_no, lot_no])

        # Format final query with placeholders
        query = query.format(gf_lot_filter=gf_lot_filter, dfi_lot_filter=dfi_lot_filter)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                "lot_no": data["lot_no"],
                "outward_wt": float(data["total_out_wt"] or 0),
                "inward_wt": float(data["total_in_wt"] or 0),
                "balance_wt": float(data["pending_outward"] or 0),
            })

        return JsonResponse({"status": "success", "data": result}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



