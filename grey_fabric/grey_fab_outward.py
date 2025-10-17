from os import name
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from cairo import Status
from django.shortcuts import render
from django.shortcuts import render

from django.utils.text import slugify

from accessory.models import *
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

from yarn.models import * 
from program_app.models import * 
from user_auth.models import * 
from company.models import * 
from employee.models import * 
from django.utils.timezone import make_aware

from software_app.views import fabric_program, getItemNameById, getSupplier, is_ajax, knitting_program
from yarn.views import dyeing_program


# `````````````````````````````````````````````````````````````````````````````````


def grey_fab_outward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1) 
        party = party_table.objects.filter(status=1,is_process=1)
        # party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
 
        yarn_count = count_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        dyeing = dyeing_program_table.objects.filter(status=1)

        lot = (
            parent_gf_delivery_table.objects
            .filter(status=1)
            .values('lot_no')  # Group by lot_no
            .annotate(
                total_gross_wt=Sum('gross_wt'),
             
            )
            .order_by('lot_no')
        )

      
        knitting = knitting_table.objects.filter(status=1,is_grey_fabric=1)
        return render(request,'outward/grey_fabric_outward.html',{'supplier':supplier,'party':party,'product':product,'lot':lot,
                                                                  'knitting':knitting,'dyeing':dyeing,'yarn_count':yarn_count})
    else:
        return HttpResponseRedirect("/admin")




# ```````````````````````````` grey fabric inward add ``````````````````



def generate_outward_num_series():
    last_purchase = parent_gf_delivery_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.do_number:
        match = re.search(r'DO-(\d+)', last_purchase.do_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1
        print('new-no:',next_num)
 
    return f"DO-{next_num:03d}"



def grey_fabric_outward_add(request): 
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
       
        product = product_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)

        fabric_program_qs = fabric_program_table.objects.filter(status=1)

        linked_knitting_ids = grey_fabric_po_table.objects.values('program_id')

 
        # ``` dyeing program`````


        # outwards = parent_gf_delivery_table.objects.filter(status=1).values('dyeing_program_id')
        dyeing = dyeing_program_table.objects.filter(status=1)
        # dyeing = dyeing_program_table.objects.filter(status=1).exclude(id__in=outwards)

        # Filter knitting_table
        knitting = knitting_table.objects.filter(status=1, is_grey_fabric=1).exclude(id__in=linked_knitting_ids)
        fabric_program = []
        for fp in fabric_program_qs:
            try:
                fabric_item = fabric_table.objects.get(id=fp.fabric_id)
                print(f"fabric_item: {fabric_item}, ID: {fp.fabric_id}, Name: {getattr(fabric_item, 'name', 'NO NAME')}")
                fabric_program.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': getattr(fabric_item, 'name', 'NO NAME')
                })
            except fabric_table.DoesNotExist:
                print(f"fabric_id {fp.fabric_id} not found in fabric_table")
                fabric_program.append({
                    'id': fp.id,
                    'name': fp.name,
                    'fabric_id': fp.fabric_id,
                    'fabric_name': 'N/A' 
                })
        # party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)
        party = party_table.objects.filter(status=1, is_process=1)
        knitting_party = party_table.objects.filter(status=1,is_knitting=1)
        compact_party = party_table.objects.filter(status=1,is_compacting=1)
        tex = tex_table.objects.filter(status=1)
        gauge = gauge_table.objects.filter(status=1)
        dia = dia_table.objects.filter(status=1)
        do_number = generate_outward_num_series  
 

        program = grey_fab_dyeing_program_balance.objects.filter(
            balance_wt__gt=0
        ).values('program_id', 'fabric_id','dia_id','color_id')

        lot = grey_fabric_available_inward_table.objects.filter(
            available_wt__gt=0
        ).values('lot_no').distinct().order_by('lot_no')

        print('lot:',lot)

        
        program_ids = program.values_list('program_id', flat=True) 

        prg_list = dyeing_program_table.objects.filter(id__in=program_ids, status=1)
        # if prg_list = 

        # print('program',prg_list)
        return render(request, 'outward/grey_fab_outward_add.html', {
            'knitting_party': knitting_party,
            'party': party,
            'compact_party':compact_party,
            'product': product,
            'count':count,
            'fabric_program':fabric_program, 
            'do_number': do_number,
            'tex':tex,
            'gauge':gauge,
            'dia':dia,
            'knitting':knitting,
            'dyeing':dyeing,
            'program':prg_list ,
            'lot':lot,  
                 
        }) 
    else:
        return HttpResponseRedirect("/admin")




def get_party_lists(request):
    party_id = request.POST.get('party_id')
    if not party_id:
        return JsonResponse({'error': 'party_id is required'}, status=400)

    program_ids = set()
    old_program_ids = set()
 
    # Step 1: Get new programs (out_quantity = 0) 
    new_programs = grey_fab_dyeing_program_balance.objects.filter(
        out_wt=0,
        balance_wt__gt=0
 
    ).values_list('program_id', flat=True)

    for program_id in new_programs:
        program_ids.add(program_id)

    # Step 2: Get old programs (out_wt > 0 and balance_wt > 0)
    old_programs_qs = grey_fab_dyeing_program_balance.objects.filter(
        out_wt__gt=0,
        balance_wt__gt=0
    ).values('program_id')

    for row in old_programs_qs:
        program_id = row['program_id']
        count = parent_gf_delivery_table.objects.filter(
            party_id=party_id, 
            program_id=program_id
        ).count()
        if count > 0:
            program_ids.add(program_id)
            old_program_ids.add(program_id)  # Track as old

    # Step 3: Get knitting info
    knitting_qs = knitting_table.objects.filter(id__in=program_ids).values_list('id', 'knitting_number', 'name')
    knitting_map = {row[0]: {'knitting_number': row[1], 'name': row[2]} for row in knitting_qs}

    final_list = []
    for program_id in program_ids:
        knitting_info = knitting_map.get(program_id)
        if not knitting_info:
            continue

        program_entry = {
            'id': program_id,
            'knitting_number': knitting_info['knitting_number'],
            'name': knitting_info['name']
        }

        # Add po_id only for old programs 
        if program_id in old_program_ids:

            po_ids = child_gf_delivery_table.objects.filter(
                program_id=program_id,
                party_id=party_id
            ).values_list('po_id', flat=True).distinct()
            print('po-ids:',po_ids) 

            po = parent_po_table.objects.filter(status=1, id__in=po_ids).values('name')
            program_entry['po_ids'] = [p['name'] for p in po] 

            # po_ids = sub_yarn_deliver_table.objects.filter(
            #     program_id=program_id,
            #     party_id=party_id
            # ).values_list('po_id', flat=True).distinct()
            # po = parent_po_table.objects.filter(status=1, id__in=po_ids).values('name')
            # program_entry['po_ids'] = po #list(po_ids)

        final_list.append(program_entry)

    return JsonResponse(final_list, safe=False)



@csrf_exempt
def get_grey_fab_inward(request):
    if request.method == "POST":
        lot_no = request.POST.get("lot_no")

        # Get unique inward_ids
        inward_ids = grey_fabric_available_inward_table.objects.filter(
            lot_no=lot_no,
            available_wt__gt=0
        ).values_list('inward_id', flat=True).distinct()
        print('available-inw:',inward_ids)
        # Get inward_number for each ID
        inward_qs = gf_inward_table.objects.filter(
            id__in=inward_ids,
            status=1,
            is_active=1,
        ).values('id', 'inward_number','total_gross_wt')
        print('inw:',inward_qs)

        return JsonResponse({
            'status': 'success',
            'inward_list': list(inward_qs)
        })






from django.db import connection
from django.http import JsonResponse
import json



from django.db import connection
from django.http import JsonResponse
from django.db.models import Max


def get_grey_fab_inward_detail_list(request):
    if request.method == "POST":
        lot_no = request.POST.get("lot_no")
        tm_id = request.POST.get("prg_id")
        outward_tm_id = request.POST.get("outward_tm_id") or '0'
        color_id_raw = request.POST.get('color_id')  # e.g., "1,13" or "1 13"
        prg_id = request.POST.get('program_id')
        print('prg-iddd:',prg_id)
        # Normalize the color IDs to a list of ints
        color_ids = [int(cid.strip()) for cid in color_id_raw.replace(',', ' ').split() if cid.strip().isdigit()]

       

        query = f"""
            SELECT 
                Y.lot_no,
                Y.program_id,
                Y.fabric_id,
                Y.dia_id, 

                MAX(X.pgm_rolls) AS pgm_rolls,
                MAX(X.pgm_wt) AS pgm_wt,
                MAX(X.out_rolls) AS out_rolls, 
                MAX(X.out_wt) AS out_wt,

                
               
                MAX(Y.total_in_rolls) AS tot_in_rolls,
                MAX(Y.total_in_wt) AS tot_in_wt,
                MAX(Y.total_out_roll) AS tot_out_rolls,
                MAX(Y.total_out_wt) AS tot_out_wt,
                (MAX(Y.total_in_rolls) - MAX(Y.total_out_roll)) AS stock_rolls,
                (MAX(Y.total_in_wt) - MAX(Y.total_out_wt)) AS stock_wt


            FROM (
                SELECT 
                    yi.lot_no,
                    yi.program_id,
                    yi.fabric_id,
                    yi.dia_id,
                    0 AS pgm_rolls,
                    0 AS pgm_wt,
                    SUM(yi.roll) AS total_in_rolls,
                    SUM(yi.gross_wt) AS total_in_wt,
                    0 AS total_out_roll,
                    0 AS total_out_wt,
                    0 AS out_rolls,
                    0 AS out_wt
                FROM tx_gf_inward yi
                WHERE yi.status = 1 AND yi.lot_no = %s
                GROUP BY yi.lot_no, yi.program_id, yi.fabric_id, yi.dia_id

                UNION ALL

                SELECT 
                    yo.lot_no,
                    kp.id AS program_id,
                    yo.fabric_id,
                    yo.dia_id,
                    0 AS pgm_rolls,
                    0 AS pgm_wt,
                    0 AS total_in_rolls,
                    0 AS total_in_wt,
                    SUM(yo.roll) AS total_out_roll,
                    SUM(yo.gross_wt) AS total_out_wt,
                    0 AS out_rolls,
                    0 AS out_wt
                FROM tx_gf_delivery yo
                LEFT JOIN tm_dyeing_program dp ON yo.dyeing_program_id = dp.id
                LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
                WHERE yo.status = 1 AND yo.lot_no = %s
                GROUP BY yo.lot_no, kp.id, yo.fabric_id, yo.dia_id
            ) AS Y

            LEFT JOIN (
                SELECT 
                    '' AS lot_no,
                    yip.tm_id AS program_id,
                    yip.fabric_id,
                    yip.dia AS dia_id,
                    SUM(yip.rolls) AS pgm_rolls,
                    SUM(yip.quantity) AS pgm_wt,
                    0 AS total_in_rolls,
                    0 AS total_in_wt,
                    0 AS total_out_roll,
                    0 AS total_out_wt,
                    0 AS out_rolls,
                    0 AS out_wt
                FROM tx_knitting yip
                WHERE yip.status = 1 AND yip.tm_id = %s
                GROUP BY yip.tm_id, yip.fabric_id, yip.dia

                UNION ALL

                SELECT 
                    yod.lot_no,
                    kp.id,
                    yod.fabric_id,
                    yod.dia_id,
                    0 AS pgm_rolls,
                    0 AS pgm_wt,
                    0 AS total_in_rolls,
                    0 AS total_in_wt,
                    0 AS total_out_roll,
                    0 AS total_out_wt,
                    SUM(yod.roll) AS out_rolls,
                    SUM(yod.gross_wt) AS out_wt
                FROM tx_gf_delivery yod
                LEFT JOIN tm_dyeing_program dp ON yod.dyeing_program_id = dp.id
                LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
                WHERE yod.status = 1 AND yod.tm_id = %s
                GROUP BY yod.lot_no, yod.knitting_program_id, yod.fabric_id, yod.dia_id
            ) AS X 
            ON Y.program_id = X.program_id 
            AND Y.fabric_id = X.fabric_id 
            AND Y.dia_id = X.dia_id

            WHERE Y.lot_no IS NOT NULL

            GROUP BY 
                Y.lot_no,
                Y.fabric_id,
                Y.dia_id
               
        """                # Y.program_id,


        with connection.cursor() as cursor:
            cursor.execute(query, [lot_no, lot_no, tm_id, outward_tm_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print('res:',results)
        # Collect unique IDs
        unique_program_ids = {row['program_id'] for row in results}
        unique_fabric_ids = {row['fabric_id'] for row in results}
        unique_dia_ids = {row['dia_id'] for row in results}

        programs = knitting_table.objects.filter(status=1, id__in=unique_program_ids).values('id', 'name')
        fabrics = fabric_program_table.objects.filter(status=1, id__in=unique_fabric_ids).values('id', 'name')
        dias = dia_table.objects.filter(status=1, id__in=unique_dia_ids).values('id', 'name')

        sub_knittings = sub_knitting_table.objects.filter(status=1, tm_id__in=unique_program_ids).values(
            'tm_id', 'fabric_id'
        ).annotate(
            gauge_id=Max('gauge'),
            tex_id=Max('tex'),
            gsm=Max('gsm'),
            count_id=Max('count_id'),
        )

        # Lookup maps
        program_map = {p['id']: p['name'] for p in programs}
        fabric_map = {p['id']: p['name'] for p in fabrics}
        dia_map = {d['id']: d['name'] for d in dias}
        sub_knit_map = {(r['tm_id'], r['fabric_id']): r for r in sub_knittings}

        # Related IDs for gauge, tex, gsm, count
        gauge_ids = [r['gauge_id'] for r in sub_knittings if r.get('gauge_id')]
        tex_ids = [r['tex_id'] for r in sub_knittings if r.get('tex_id')]
        gsm_ids = [r['gsm'] for r in sub_knittings if r.get('gsm')]
        count_ids = [r['count_id'] for r in sub_knittings if r.get('count_id')]

        gauge_map = {g.id: g.name for g in gauge_table.objects.filter(status=1, id__in=gauge_ids)}
        tex_map = {t.id: t.name for t in tex_table.objects.filter(status=1, id__in=tex_ids)}
        count_map = {c.id: c.name for c in count_table.objects.filter(status=1, id__in=count_ids)}

        

       # Fetch all dye program data for relevant combinations
        dye_prgs = sub_dyeing_program_table.objects.filter(
            status=1,
            tm_id=prg_id,
            color_id__in=color_ids,
            dia_id__in=list(unique_dia_ids)
        ).values('color_id', 'dia_id', 'roll', 'roll_wt')
        print('dye-list:',dye_prgs)
        # Build a mapping {(dia_id, color_id): data}
        dye_map = {
            (d['dia_id'], d['color_id']): {
                'roll': float(d['roll'] or 0),
                'roll_wt': float(d['roll_wt'] or 0)
            }
            for d in dye_prgs
        }




        final_results = []

        for row in results:
            row['program_name'] = program_map.get(row['program_id'], '')
            row['fabric_name'] = fabric_map.get(row['fabric_id'], '')
            row['dia_name'] = dia_map.get(row['dia_id'], '')

            key = (row['program_id'], row['fabric_id'])
            sub = sub_knit_map.get(key, {})
            row['gauge_id'] = sub.get('gauge_id')
            row['tex_id'] = sub.get('tex_id')
            row['gsm'] = sub.get('gsm')
            row['count_id'] = sub.get('count_id')

            row['gauge_name'] = gauge_map.get(row['gauge_id'], '')
            row['tex_name'] = tex_map.get(row['tex_id'], '')
            row['yarn_count_name'] = count_map.get(row['count_id'], '')
            row['gsm_name'] = row['gsm'] or ''

            dia_id = row.get('dia_id')


            for color_id in color_ids:
                dye_info = dye_map.get((dia_id, color_id), {'roll': 0, 'roll_wt': 0})

                # ✅ Skip entries where roll and weight are both zero
                if dye_info['roll'] <= 0 and dye_info['roll_wt'] <= 0:
                    continue

                # Create new row per color
                new_row = row.copy()
                new_row['color_id'] = color_id
                new_row['dye_rolls'] = dye_info['roll']
                new_row['dye_roll_wt'] = dye_info['roll_wt']

                final_results.append(new_row)




                # for color_id in color_ids:
                #     dye_info = dye_map.get((dia_id, color_id), {'roll': 0, 'roll_wt': 0})

                #     # Create new row per color
                #     new_row = row.copy()
                #     new_row['color_id'] = color_id
                #     new_row['dye_rolls'] = dye_info['roll']
                #     new_row['dye_roll_wt'] = dye_info['roll_wt']

                #     # ✅ Append each colored row to final results
                #     final_results.append(new_row)

            # color_id = color_ids  # Make sure your SQL result includes this
            # dia_id = row.get('dia_id')
            # dye_info = dye_map.get((dia_id, color_id), {'roll': 0, 'roll_wt': 0})

            # row['dye_rolls'] = dye_info['roll']
            # row['dye_roll_wt'] = dye_info['roll_wt']



        return JsonResponse({
            'status': 'success',
            'stock_summary': final_results, 
            'prg_name': list(programs),
            'fabric_name': list(fabrics),
            'dia_name': list(dias),
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})








# def get_grey_inward_details(request):
#     if request.method == "POST":
#         lot_no = request.POST.get("lot_no")
#         tm_id = request.POST.get("tm_id")
#         outward_tm_id = request.POST.get("outward_tm_id") or '0'
#         color_id_raw = request.POST.get('color_id')  # e.g., "1,13" or "1 13"
#         prg_id = request.POST.get('program_id')

#         # Normalize the color IDs to a list of ints
#         color_ids = [int(cid.strip()) for cid in color_id_raw.replace(',', ' ').split() if cid.strip().isdigit()]

       

#         query = f"""
#             SELECT 
#                 Y.lot_no,
#                 Y.program_id,
#                 Y.fabric_id,
#                 Y.dia_id, 

#                 MAX(X.pgm_rolls) AS pgm_rolls,
#                 MAX(X.pgm_wt) AS pgm_wt,
#                 MAX(X.out_rolls) AS out_rolls, 
#                 MAX(X.out_wt) AS out_wt,

                
               
#                 MAX(Y.total_in_rolls) AS tot_in_rolls,
#                 MAX(Y.total_in_wt) AS tot_in_wt,
#                 MAX(Y.total_out_roll) AS tot_out_rolls,
#                 MAX(Y.total_out_wt) AS tot_out_wt,
#                 (MAX(Y.total_in_rolls) - MAX(Y.total_out_roll)) AS stock_rolls,
#                 (MAX(Y.total_in_wt) - MAX(Y.total_out_wt)) AS stock_wt


#             FROM (
#                 SELECT 
#                     yi.lot_no,
#                     yi.program_id,
#                     yi.fabric_id,
#                     yi.dia_id,
#                     0 AS pgm_rolls,
#                     0 AS pgm_wt,
#                     SUM(yi.roll) AS total_in_rolls,
#                     SUM(yi.gross_wt) AS total_in_wt,
#                     0 AS total_out_roll,
#                     0 AS total_out_wt,
#                     0 AS out_rolls,
#                     0 AS out_wt
#                 FROM tx_gf_inward yi
#                 WHERE yi.status = 1 AND yi.lot_no = %s
#                 GROUP BY yi.lot_no, yi.program_id, yi.fabric_id, yi.dia_id

#                 UNION ALL

#                 SELECT 
#                     yo.lot_no,
#                     kp.id AS program_id,
#                     yo.fabric_id,
#                     yo.dia_id,
#                     0 AS pgm_rolls,
#                     0 AS pgm_wt,
#                     0 AS total_in_rolls,
#                     0 AS total_in_wt,
#                     SUM(yo.roll) AS total_out_roll,
#                     SUM(yo.gross_wt) AS total_out_wt,
#                     0 AS out_rolls,
#                     0 AS out_wt
#                 FROM tx_gf_delivery yo
#                 LEFT JOIN tm_dyeing_program dp ON yo.dyeing_program_id = dp.id
#                 LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
#                 WHERE yo.status = 1 AND yo.lot_no = %s
#                 GROUP BY yo.lot_no, kp.id, yo.fabric_id, yo.dia_id
#             ) AS Y

#             LEFT JOIN (
#                 SELECT 
#                     '' AS lot_no,
#                     yip.tm_id AS program_id,
#                     yip.fabric_id,
#                     yip.dia AS dia_id,
#                     SUM(yip.rolls) AS pgm_rolls,
#                     SUM(yip.quantity) AS pgm_wt,
#                     0 AS total_in_rolls,
#                     0 AS total_in_wt,
#                     0 AS total_out_roll,
#                     0 AS total_out_wt,
#                     0 AS out_rolls,
#                     0 AS out_wt
#                 FROM tx_knitting yip
#                 WHERE yip.status = 1 AND yip.tm_id = %s
#                 GROUP BY yip.tm_id, yip.fabric_id, yip.dia

#                 UNION ALL

#                 SELECT 
#                     yod.lot_no,
#                     kp.id,
#                     yod.fabric_id,
#                     yod.dia_id,
#                     0 AS pgm_rolls,
#                     0 AS pgm_wt,
#                     0 AS total_in_rolls,
#                     0 AS total_in_wt,
#                     0 AS total_out_roll,
#                     0 AS total_out_wt,
#                     SUM(yod.roll) AS out_rolls,
#                     SUM(yod.gross_wt) AS out_wt
#                 FROM tx_gf_delivery yod
#                 LEFT JOIN tm_dyeing_program dp ON yod.dyeing_program_id = dp.id
#                 LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
#                 WHERE yod.status = 1 AND yod.tm_id = %s
#                 GROUP BY yod.lot_no, yod.knitting_program_id, yod.fabric_id, yod.dia_id
#             ) AS X 
#             ON Y.program_id = X.program_id 
#             AND Y.fabric_id = X.fabric_id 
#             AND Y.dia_id = X.dia_id

#             WHERE Y.lot_no IS NOT NULL

#             GROUP BY 
#                 Y.lot_no,
#                 Y.fabric_id,
#                 Y.dia_id
               
#         """                # Y.program_id,




#         with connection.cursor() as cursor:
#             cursor.execute(query, [lot_no, lot_no, tm_id, outward_tm_id])
#             columns = [col[0] for col in cursor.description]
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#             print('res:',results)
#         # Collect unique IDs
#         unique_program_ids = {row['program_id'] for row in results}
#         unique_fabric_ids = {row['fabric_id'] for row in results}
#         unique_dia_ids = {row['dia_id'] for row in results}

#         programs = knitting_table.objects.filter(status=1, id__in=unique_program_ids).values('id', 'name')
#         fabrics = fabric_program_table.objects.filter(status=1, id__in=unique_fabric_ids).values('id', 'name')
#         dias = dia_table.objects.filter(status=1, id__in=unique_dia_ids).values('id', 'name')

#         sub_knittings = sub_knitting_table.objects.filter(status=1, tm_id__in=unique_program_ids).values(
#             'tm_id', 'fabric_id'
#         ).annotate(
#             gauge_id=Max('gauge'),
#             tex_id=Max('tex'),
#             gsm=Max('gsm'),
#             count_id=Max('count_id'),
#         )

#         # Lookup maps
#         program_map = {p['id']: p['name'] for p in programs}
#         fabric_map = {p['id']: p['name'] for p in fabrics}
#         dia_map = {d['id']: d['name'] for d in dias}
#         sub_knit_map = {(r['tm_id'], r['fabric_id']): r for r in sub_knittings}

#         # Related IDs for gauge, tex, gsm, count
#         gauge_ids = [r['gauge_id'] for r in sub_knittings if r.get('gauge_id')]
#         tex_ids = [r['tex_id'] for r in sub_knittings if r.get('tex_id')]
#         gsm_ids = [r['gsm'] for r in sub_knittings if r.get('gsm')]
#         count_ids = [r['count_id'] for r in sub_knittings if r.get('count_id')]

#         gauge_map = {g.id: g.name for g in gauge_table.objects.filter(status=1, id__in=gauge_ids)}
#         tex_map = {t.id: t.name for t in tex_table.objects.filter(status=1, id__in=tex_ids)}
#         count_map = {c.id: c.name for c in count_table.objects.filter(status=1, id__in=count_ids)}

#        # Fetch all dye program data for relevant combinations
#         dye_prgs = sub_dyeing_program_table.objects.filter(
#             status=1,
#             tm_id=prg_id,
#             color_id__in=color_ids,
#             dia_id__in=list(unique_dia_ids)
#         ).values('color_id', 'dia_id', 'roll', 'roll_wt')




#         # Build a mapping {(dia_id, color_id): data}
#         dye_map = {
#             (d['dia_id'], d['color_id']): {
#                 'roll': float(d['roll'] or 0),
#                 'roll_wt': float(d['roll_wt'] or 0)
#             }
#             for d in dye_prgs
#         }


#         inward = child_gf_delivery_table.objects.filter(tm_id=tm_id).values('dia_id', 'color_id', 'roll', 'gross_wt')
#         inward_map = {
#             (row['dia_id'], row['color_id']): {
#                 'delivered_roll': float(row['roll'] or 0),
#                 'delivered_gross_wt': float(row['gross_wt'] or 0)
#             }
#             for row in inward
#         }

#         final_results = []

#         # Step 2: Loop through and build final_results per color/dia combination
#         for row in results:
#             row['program_name'] = program_map.get(row['program_id'], '')
#             row['fabric_name'] = fabric_map.get(row['fabric_id'], '')
#             row['dia_name'] = dia_map.get(row['dia_id'], '')

#             key = (row['program_id'], row['fabric_id'])
#             sub = sub_knit_map.get(key, {})
#             row['gauge_id'] = sub.get('gauge_id')
#             row['tex_id'] = sub.get('tex_id')
#             row['gsm'] = sub.get('gsm')
#             row['count_id'] = sub.get('count_id')

#             row['gauge_name'] = gauge_map.get(row['gauge_id'], '')
#             row['tex_name'] = tex_map.get(row['tex_id'], '')
#             row['yarn_count_name'] = count_map.get(row['count_id'], '')
#             row['gsm_name'] = row['gsm'] or ''

#             dia_id = row.get('dia_id')

#             for color_id in color_ids:
#                 dye_info = dye_map.get((dia_id, color_id), {'roll': 0, 'roll_wt': 0})
#                 inward_info = inward_map.get((dia_id, color_id), {'delivered_roll': 0, 'delivered_gross_wt': 0})

#                 # Build new row with full data
#                 new_row = row.copy()
#                 new_row['color_id'] = color_id
#                 new_row['dye_rolls'] = dye_info['roll']
#                 new_row['dye_roll_wt'] = dye_info['roll_wt']
#                 new_row['delivered_roll'] = inward_info['delivered_roll']
#                 new_row['delivered_gross_wt'] = inward_info['delivered_gross_wt']

#                 final_results.append(new_row)
#                 print('fial-result:',final_results)

    
#         return JsonResponse({
#             'status': 'success',
#             'stock_summary': final_results, 
#             'prg_name': list(programs),
#             'fabric_name': list(fabrics),
#             'dia_name': list(dias),
#         })

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})




from django.http import JsonResponse
from django.db import connection
from collections import defaultdict


def get_grey_inward_details(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    lot_no = request.POST.get("lot_no")
    tm_id = request.POST.get("tm_id")  # program_id from knitting
    outward_tm_id = request.POST.get("outward_tm_id") or '0'
    prg_id = request.POST.get('program_id')  # dyeing program ID
    color_id_raw = request.POST.get('color_id', '')
    print('tm-:',tm_id)
    # Normalize color_id to list
    color_ids = [int(cid.strip()) for cid in color_id_raw.replace(',', ' ').split() if cid.strip().isdigit()]
    if not color_ids or not lot_no or not prg_id:
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'})

    # ---- STEP 1: Main stock SQL query ----
    query = """
        SELECT 
            Y.lot_no,
            Y.program_id,
            Y.fabric_id,
            Y.dia_id, 

            MAX(X.pgm_rolls) AS pgm_rolls,
            MAX(X.pgm_wt) AS pgm_wt,
            MAX(X.out_rolls) AS out_rolls, 
            MAX(X.out_wt) AS out_wt,

            MAX(Y.total_in_rolls) AS tot_in_rolls,
            MAX(Y.total_in_wt) AS tot_in_wt,
            MAX(Y.total_out_roll) AS tot_out_rolls,
            MAX(Y.total_out_wt) AS tot_out_wt,
            (MAX(Y.total_in_rolls) - MAX(Y.total_out_roll)) AS stock_rolls,
            (MAX(Y.total_in_wt) - MAX(Y.total_out_wt)) AS stock_wt

        FROM (
            SELECT 
                yi.lot_no,
                yi.program_id,
                yi.fabric_id,
                yi.dia_id,
                0 AS pgm_rolls,
                0 AS pgm_wt,
                SUM(yi.roll) AS total_in_rolls,
                SUM(yi.gross_wt) AS total_in_wt,
                0 AS total_out_roll,
                0 AS total_out_wt,
                0 AS out_rolls,
                0 AS out_wt
            FROM tx_gf_inward yi
            WHERE yi.status = 1 AND yi.lot_no = %s
            GROUP BY yi.lot_no, yi.program_id, yi.fabric_id, yi.dia_id

            UNION ALL

            SELECT 
                yo.lot_no,
                kp.id AS program_id,
                yo.fabric_id,
                yo.dia_id,
                0, 0,
                0, 0,
                SUM(yo.roll), SUM(yo.gross_wt),
                0, 0
            FROM tx_gf_delivery yo
            LEFT JOIN tm_dyeing_program dp ON yo.dyeing_program_id = dp.id
            LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
            WHERE yo.status = 1 AND yo.lot_no = %s
            GROUP BY yo.lot_no, kp.id, yo.fabric_id, yo.dia_id
        ) AS Y

        LEFT JOIN (
            SELECT 
                '' AS lot_no,
                yip.tm_id AS program_id,
                yip.fabric_id,
                yip.dia AS dia_id,
                SUM(yip.rolls), SUM(yip.quantity),
                0, 0, 0, 0, 0, 0
            FROM tx_knitting yip
            WHERE yip.status = 1 AND yip.tm_id = %s
            GROUP BY yip.tm_id, yip.fabric_id, yip.dia

            UNION ALL

            SELECT 
                yod.lot_no,
                kp.id,
                yod.fabric_id,
                yod.dia_id,
                0, 0, 0, 0, 0, 0,
                SUM(yod.roll), SUM(yod.gross_wt)
            FROM tx_gf_delivery yod
            LEFT JOIN tm_dyeing_program dp ON yod.dyeing_program_id = dp.id
            LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
            WHERE yod.status = 1 AND yod.tm_id = %s
            GROUP BY yod.lot_no, yod.knitting_program_id, yod.fabric_id, yod.dia_id
        ) AS X 
        ON Y.program_id = X.program_id 
        AND Y.fabric_id = X.fabric_id 
        AND Y.dia_id = X.dia_id

        WHERE Y.lot_no IS NOT NULL

        GROUP BY 
            Y.lot_no,
            Y.fabric_id,
            Y.dia_id
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [lot_no, lot_no, tm_id, outward_tm_id])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ---- STEP 2: Lookup data ----
    program_ids = {row['program_id'] for row in results}
    fabric_ids = {row['fabric_id'] for row in results}
    dia_ids = {row['dia_id'] for row in results}

    programs = knitting_table.objects.filter(id__in=program_ids).values('id', 'name')
    fabrics = fabric_program_table.objects.filter(id__in=fabric_ids).values('id', 'name')
    dias = dia_table.objects.filter(id__in=dia_ids).values('id', 'name')

    sub_knits = sub_knitting_table.objects.filter(tm_id__in=program_ids).values(
        'tm_id', 'fabric_id'
    ).annotate(
        gauge_id=Max('gauge'),
        tex_id=Max('tex'),
        gsm=Max('gsm'),
        count_id=Max('count_id'),
    )

    gauge_map = {g.id: g.name for g in gauge_table.objects.filter(id__in=[r['gauge_id'] for r in sub_knits if r.get('gauge_id')])}
    tex_map = {t.id: t.name for t in tex_table.objects.filter(id__in=[r['tex_id'] for r in sub_knits if r.get('tex_id')])}
    count_map = {c.id: c.name for c in count_table.objects.filter(id__in=[r['count_id'] for r in sub_knits if r.get('count_id')])}

    program_map = {p['id']: p['name'] for p in programs}
    fabric_map = {f['id']: f['name'] for f in fabrics}
    dia_map = {d['id']: d['name'] for d in dias}
    sub_knit_map = {(r['tm_id'], r['fabric_id']): r for r in sub_knits}

    # ---- STEP 3: Dyeing program roll summary ----
    dye_prgs = sub_dyeing_program_table.objects.filter(
        status=1,
        tm_id=prg_id,
        color_id__in=color_ids,
        dia_id__in=list(dia_ids)
    ).values('color_id', 'dia_id', 'roll', 'roll_wt')
    print('dye-prgs:',dye_prgs)
    dye_map = {
        (d['dia_id'], d['color_id']): {
            'roll': float(d['roll'] or 0),
            'roll_wt': float(d['roll_wt'] or 0)
        }
        for d in dye_prgs
    }

    # ---- STEP 4: Delivered info ----
    inward = child_gf_delivery_table.objects.filter(tm_id=tm_id).values('dia_id', 'color_id', 'roll', 'gross_wt')
    inward_map = {
        (row['dia_id'], row['color_id']): {
            'delivered_roll': float(row['roll'] or 0),
            'delivered_gross_wt': float(row['gross_wt'] or 0)
        }
        for row in inward
    }

    # ---- STEP 5: Final data build ----
    final_results = []
    for row in results:
        dia_id = row['dia_id']
        fabric_id = row['fabric_id']
        program_id = row['program_id']

        base_data = {
            'program_id': program_id,
            'program_name': program_map.get(program_id, ''),
            'fabric_id': fabric_id,
            'fabric_name': fabric_map.get(fabric_id, ''),
            'dia_id': dia_id,
            'dia_name': dia_map.get(dia_id, ''),
        }

        sub = sub_knit_map.get((program_id, fabric_id), {})
        base_data.update({
            'gauge_id': sub.get('gauge_id'),
            'tex_id': sub.get('tex_id'),
            'gsm': sub.get('gsm'),
            'count_id': sub.get('count_id'),
            'gauge_name': gauge_map.get(sub.get('gauge_id'), ''),
            'tex_name': tex_map.get(sub.get('tex_id'), ''),
            'yarn_count_name': count_map.get(sub.get('count_id'), ''),
            'gsm_name': sub.get('gsm') or ''
        })

        for color_id in color_ids:
            dye_info = dye_map.get((dia_id, color_id), {'roll': 0, 'roll_wt': 0})
            inward_info = inward_map.get((dia_id, color_id), {'delivered_roll': 0, 'delivered_gross_wt': 0})

            new_row = base_data.copy()
            new_row.update({
                'color_id': color_id,
                'dye_rolls': dye_info['roll'],
                'dye_roll_wt': dye_info['roll_wt'],
                'out_rolls': inward_info['delivered_roll'],
                'out_gross_wt': inward_info['delivered_gross_wt'],
                'stock_rolls': row.get('stock_rolls', 0),
                'stock_wt': row.get('stock_wt', 0),
            })
            final_results.append(new_row)

    return JsonResponse({
        'status': 'success',
        'stock_summary': final_results,
        'prg_name': list(programs),
        'fabric_name': list(fabrics),
        'dia_name': list(dias),
    })



def get_grey_inward_details_23062025(request):
    if request.method == "POST":
        lot_no = request.POST.get("lot_no")
        tm_id = request.POST.get("tm_id")
        outward_tm_id = request.POST.get("outward_tm_id") or '0'
        color_id_raw = request.POST.get('color_id')  # e.g., "1,13" or "1 13"
        prg_id = request.POST.get('program_id')

        # Normalize the color IDs to a list of ints
        color_ids = [int(cid.strip()) for cid in color_id_raw.replace(',', ' ').split() if cid.strip().isdigit()]

       

        query = f"""
            SELECT 
                Y.lot_no,
                Y.program_id,
                Y.fabric_id,
                Y.dia_id, 

                MAX(X.pgm_rolls) AS pgm_rolls,
                MAX(X.pgm_wt) AS pgm_wt,
                MAX(X.out_rolls) AS out_rolls, 
                MAX(X.out_wt) AS out_wt,

                
               
                MAX(Y.total_in_rolls) AS tot_in_rolls,
                MAX(Y.total_in_wt) AS tot_in_wt,
                MAX(Y.total_out_roll) AS tot_out_rolls,
                MAX(Y.total_out_wt) AS tot_out_wt,
                (MAX(Y.total_in_rolls) - MAX(Y.total_out_roll)) AS stock_rolls,
                (MAX(Y.total_in_wt) - MAX(Y.total_out_wt)) AS stock_wt


            FROM (
                SELECT 
                    yi.lot_no,
                    yi.program_id,
                    yi.fabric_id,
                    yi.dia_id,
                    0 AS pgm_rolls,
                    0 AS pgm_wt,
                    SUM(yi.roll) AS total_in_rolls,
                    SUM(yi.gross_wt) AS total_in_wt,
                    0 AS total_out_roll,
                    0 AS total_out_wt,
                    0 AS out_rolls,
                    0 AS out_wt
                FROM tx_gf_inward yi
                WHERE yi.status = 1 AND yi.lot_no = %s
                GROUP BY yi.lot_no, yi.program_id, yi.fabric_id, yi.dia_id

                UNION ALL

                SELECT 
                    yo.lot_no,
                    kp.id AS program_id,
                    yo.fabric_id,
                    yo.dia_id,
                    0 AS pgm_rolls,
                    0 AS pgm_wt,
                    0 AS total_in_rolls,
                    0 AS total_in_wt,
                    SUM(yo.roll) AS total_out_roll,
                    SUM(yo.gross_wt) AS total_out_wt,
                    0 AS out_rolls,
                    0 AS out_wt
                FROM tx_gf_delivery yo
                LEFT JOIN tm_dyeing_program dp ON yo.dyeing_program_id = dp.id
                LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
                WHERE yo.status = 1 AND yo.lot_no = %s
                GROUP BY yo.lot_no, kp.id, yo.fabric_id, yo.dia_id
            ) AS Y

            LEFT JOIN (
                SELECT 
                    '' AS lot_no,
                    yip.tm_id AS program_id,
                    yip.fabric_id,
                    yip.dia AS dia_id,
                    SUM(yip.rolls) AS pgm_rolls,
                    SUM(yip.quantity) AS pgm_wt,
                    0 AS total_in_rolls,
                    0 AS total_in_wt,
                    0 AS total_out_roll,
                    0 AS total_out_wt,
                    0 AS out_rolls,
                    0 AS out_wt
                FROM tx_knitting yip
                WHERE yip.status = 1 AND yip.tm_id = %s
                GROUP BY yip.tm_id, yip.fabric_id, yip.dia

                UNION ALL

                SELECT 
                    yod.lot_no,
                    kp.id,
                    yod.fabric_id,
                    yod.dia_id,
                    0 AS pgm_rolls,
                    0 AS pgm_wt,
                    0 AS total_in_rolls,
                    0 AS total_in_wt,
                    0 AS total_out_roll,
                    0 AS total_out_wt,
                    SUM(yod.roll) AS out_rolls,
                    SUM(yod.gross_wt) AS out_wt
                FROM tx_gf_delivery yod
                LEFT JOIN tm_dyeing_program dp ON yod.dyeing_program_id = dp.id
                LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
                WHERE yod.status = 1 AND yod.tm_id = %s
                GROUP BY yod.lot_no, yod.knitting_program_id, yod.fabric_id, yod.dia_id
            ) AS X 
            ON Y.program_id = X.program_id 
            AND Y.fabric_id = X.fabric_id 
            AND Y.dia_id = X.dia_id

            WHERE Y.lot_no IS NOT NULL

            GROUP BY 
                Y.lot_no,
                Y.fabric_id,
                Y.dia_id
               
        """                # Y.program_id,


        with connection.cursor() as cursor:
            cursor.execute(query, [lot_no, lot_no, tm_id, outward_tm_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print('res:',results)
        # Collect unique IDs
        unique_program_ids = {row['program_id'] for row in results}
        unique_fabric_ids = {row['fabric_id'] for row in results}
        unique_dia_ids = {row['dia_id'] for row in results}

        programs = knitting_table.objects.filter(status=1, id__in=unique_program_ids).values('id', 'name')
        fabrics = fabric_program_table.objects.filter(status=1, id__in=unique_fabric_ids).values('id', 'name')
        dias = dia_table.objects.filter(status=1, id__in=unique_dia_ids).values('id', 'name')

        sub_knittings = sub_knitting_table.objects.filter(status=1, tm_id__in=unique_program_ids).values(
            'tm_id', 'fabric_id'
        ).annotate(
            gauge_id=Max('gauge'),
            tex_id=Max('tex'),
            gsm=Max('gsm'),
            count_id=Max('count_id'),
        )

        # Lookup maps
        program_map = {p['id']: p['name'] for p in programs}
        fabric_map = {p['id']: p['name'] for p in fabrics}
        dia_map = {d['id']: d['name'] for d in dias}
        sub_knit_map = {(r['tm_id'], r['fabric_id']): r for r in sub_knittings}

        # Related IDs for gauge, tex, gsm, count
        gauge_ids = [r['gauge_id'] for r in sub_knittings if r.get('gauge_id')]
        tex_ids = [r['tex_id'] for r in sub_knittings if r.get('tex_id')]
        gsm_ids = [r['gsm'] for r in sub_knittings if r.get('gsm')]
        count_ids = [r['count_id'] for r in sub_knittings if r.get('count_id')]

        gauge_map = {g.id: g.name for g in gauge_table.objects.filter(status=1, id__in=gauge_ids)}
        tex_map = {t.id: t.name for t in tex_table.objects.filter(status=1, id__in=tex_ids)}
        count_map = {c.id: c.name for c in count_table.objects.filter(status=1, id__in=count_ids)}

        
        # # Default rolls
        # dye_roll = 0
        # dye_roll_wt = 0

        # # Fetch all matching dye programs
        # # dye_prgs = sub_dyeing_program_table.objects.filter(status=1, tm_id=prg_id, color_id__in=color_ids,dia_id=unique_dia_ids)
        # dye_prgs = sub_dyeing_program_table.objects.filter(
        #     status=1,
        #     tm_id=prg_id,
        #     color_id__in=color_ids,
        #     dia_id__in=list(unique_dia_ids)  # convert set to list
        # )

        # # Optionally sum them or use only the first one (based on your requirement)
        # for d in dye_prgs:
        #     dye_roll = float(d.roll or 0)
        #     dye_roll_wt = float(d.roll_wt or 0)

        # print('rolls:', dye_roll, dye_roll_wt)


       # Fetch all dye program data for relevant combinations
        dye_prgs = sub_dyeing_program_table.objects.filter(
            status=1,
            tm_id=prg_id,
            color_id__in=color_ids,
            dia_id__in=list(unique_dia_ids)
        ).values('color_id', 'dia_id', 'roll', 'roll_wt')




        # Build a mapping {(dia_id, color_id): data}
        dye_map = {
            (d['dia_id'], d['color_id']): {
                'roll': float(d['roll'] or 0),
                'roll_wt': float(d['roll_wt'] or 0)
            }
            for d in dye_prgs
        }


        # Step 1: Fetch and prepare inward delivery data
        inward = child_gf_delivery_table.objects.filter(tm_id=tm_id).values('dia_id', 'color_id', 'roll', 'gross_wt')
        inward_map = {
            (row['dia_id'], row['color_id']): {
                'delivered_roll': float(row['roll'] or 0),
                'delivered_gross_wt': float(row['gross_wt'] or 0)
            }
            for row in inward
        }

        print('inw:',inward) 
        final_results = []
        print('f-list:',final_results)

        # Step 2: Loop through and build final_results per color/dia combination
        for row in results:
            row['program_name'] = program_map.get(row['program_id'], '')
            row['fabric_name'] = fabric_map.get(row['fabric_id'], '')
            row['dia_name'] = dia_map.get(row['dia_id'], '')

            key = (row['program_id'], row['fabric_id'])
            sub = sub_knit_map.get(key, {})
            row['gauge_id'] = sub.get('gauge_id')
            row['tex_id'] = sub.get('tex_id')
            row['gsm'] = sub.get('gsm')
            row['count_id'] = sub.get('count_id')

            row['gauge_name'] = gauge_map.get(row['gauge_id'], '')
            row['tex_name'] = tex_map.get(row['tex_id'], '')
            row['yarn_count_name'] = count_map.get(row['count_id'], '')
            row['gsm_name'] = row['gsm'] or ''

            dia_id = row.get('dia_id')

            for color_id in color_ids:
                dye_info = dye_map.get((dia_id, color_id), {'roll': 0, 'roll_wt': 0})
                inward_info = inward_map.get((dia_id, color_id), {'delivered_roll': 0, 'delivered_gross_wt': 0})

                # Build new row with full data
                new_row = row.copy()
                new_row['color_id'] = color_id
                new_row['dye_rolls'] = dye_info['roll']
                new_row['dye_roll_wt'] = dye_info['roll_wt']
                new_row['delivered_roll'] = inward_info['delivered_roll']
                new_row['delivered_gross_wt'] = inward_info['delivered_gross_wt']

                final_results.append(new_row)

          
        return JsonResponse({
            'status': 'success',
            'stock_summary': final_results, 
            'prg_name': list(programs),
            'fabric_name': list(fabrics),
            'dia_name': list(dias),
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})







def get_grey_fab_inward_detail_list_16062025(request):
    if request.method == "POST":
        lot_no = request.POST.get("lot_no")
        tm_id = request.POST.get("prg_id")  # Must be passed from frontend for dynamic filtering
        outward_tm_id = request.POST.get("outward_tm_id")  # For optional outward roll data
        print('program-id:',tm_id)
        # Safety check
        if not lot_no or not tm_id:
            return JsonResponse({'status': 'error', 'message': 'lot_no and tm_id are required'})

        # Default outward_tm_id if not provided
        outward_tm_id = outward_tm_id or '0'
#  SELECT 
#             Y.lot_no,
#             Y.program_id,
#             Y.fabric_id,
#             Y.dia_id, 

#             X.pgm_rolls,
#             X.pgm_wt,
#             X.out_rolls,
#             X.out_wt,

#             SUM(Y.total_in_rolls) AS tot_in_rolls,
#             SUM(Y.total_in_wt) AS tot_in_wt,
#             SUM(Y.total_out_roll) AS tot_out_rolls,
#             SUM(Y.total_out_wt) AS tot_out_wt,

#             (SUM(Y.total_in_rolls) - SUM(Y.total_out_roll)) AS stock_rolls,
#             (SUM(Y.total_in_wt) - SUM(Y.total_out_wt)) AS stock_wt

        query = f"""
       SELECT 
            Y.lot_no,
            Y.program_id,
            Y.fabric_id,
            Y.dia_id, 

            SUM(X.pgm_rolls) AS pgm_rolls,
            SUM(X.pgm_wt) AS pgm_wt,
            SUM(X.out_rolls) AS out_rolls,
            SUM(X.out_wt) AS out_wt,

            SUM(Y.total_in_rolls) AS tot_in_rolls,
            SUM(Y.total_in_wt) AS tot_in_wt,
            SUM(Y.total_out_roll) AS tot_out_rolls, 
            SUM(Y.total_out_wt) AS tot_out_wt,

            (SUM(Y.total_in_rolls) - SUM(Y.total_out_roll)) AS stock_rolls,
            (SUM(Y.total_in_wt) - SUM(Y.total_out_wt)) AS stock_wt
        FROM (
            SELECT 
                yi.lot_no,
                yi.program_id,
                yi.fabric_id,
                yi.dia_id,
                0 AS pgm_rolls,
                0 AS pgm_wt,
                SUM(yi.roll) AS total_in_rolls,
                SUM(yi.gross_wt) AS total_in_wt,
                0 AS total_out_roll,
                0 AS total_out_wt,
                0 AS out_rolls,
                0 AS out_wt
            FROM tx_gf_inward yi
            WHERE yi.status = 1 AND yi.lot_no = %s
            GROUP BY yi.lot_no, yi.program_id, yi.fabric_id, yi.dia_id

            UNION ALL

            SELECT 
                yo.lot_no,
                kp.id AS program_id,
                yo.fabric_id,
                yo.dia_id,
                0 AS pgm_rolls,
                0 AS pgm_wt,
                0 AS total_in_rolls,
                0 AS total_in_wt,
                SUM(yo.roll) AS total_out_roll,
                SUM(yo.gross_wt) AS total_out_wt,
                0 AS out_rolls,
                0 AS out_wt
            FROM tx_gf_delivery yo
            LEFT JOIN tm_dyeing_program dp ON yo.program_id = dp.id
            LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
            WHERE yo.status = 1 AND yo.lot_no = %s
            GROUP BY yo.lot_no, kp.id, yo.fabric_id, yo.dia_id
        ) AS Y

        LEFT JOIN (
            SELECT 
                '' AS lot_no,
                yip.tm_id AS program_id,
                yip.fabric_id,
                yip.dia AS dia_id,
                SUM(yip.rolls) AS pgm_rolls,
                SUM(yip.quantity) AS pgm_wt,
                0 AS total_in_rolls,
                0 AS total_in_wt,
                0 AS total_out_roll,
                0 AS total_out_wt,
                0 AS out_rolls,
                0 AS out_wt
            FROM tx_knitting yip
            WHERE yip.status = 1 AND yip.tm_id = %s
            GROUP BY yip.tm_id, yip.fabric_id, yip.dia

            UNION ALL

            SELECT 
                yod.lot_no,
                kp.id,
                yod.fabric_id,
                yod.dia_id,
                0 AS pgm_rolls,
                0 AS pgm_wt,
                0 AS total_in_rolls,
                0 AS total_in_wt,
                0 AS total_out_roll,
                0 AS total_out_wt,
                SUM(yod.roll) AS out_rolls,
                SUM(yod.gross_wt) AS out_wt
            FROM tx_gf_delivery yod
            LEFT JOIN tm_dyeing_program dp ON yod.program_id = dp.id
            LEFT JOIN tm_knitting kp ON dp.program_id = kp.id
            WHERE yod.status = 1 AND yod.tm_id = %s

            GROUP BY yod.lot_no, yod.program_id, yod.fabric_id, yod.dia_id
        ) AS X 
        ON Y.program_id = X.program_id 
        AND Y.fabric_id = X.fabric_id 
        AND Y.dia_id = X.dia_id

        WHERE Y.lot_no IS NOT NULL
            
        GROUP BY 
            Y.lot_no,
            Y.program_id,
            Y.fabric_id,
            Y.dia_id,
            X.out_rolls,
            X.out_wt


    
        """
  # GROUP BY 
        #     Y.lot_no,
        #     Y.program_id,
        #     Y.fabric_id,
        #     Y.dia_id,
        #     X.pgm_rolls,
        #     X.pgm_wt,
        #     X.out_rolls, 
        #     X.out_wt
        with connection.cursor() as cursor:
            cursor.execute(query, [lot_no, lot_no, tm_id, outward_tm_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print('stock:', results)

            # Step 1: Extract unique program_ids
            unique_program_ids = set(row['program_id'] for row in results)
            unique_fabric_ids = set(row['fabric_id'] for row in results)
            unique_dia_ids = set(row['dia_id'] for row in results)

            # Step 2: Get related data in bulk
            programs = knitting_table.objects.filter(status=1,id__in=unique_program_ids).values('id', 'name')
            fabrics = fabric_program_table.objects.filter(status=1,id__in=unique_program_ids).values('id', 'name')
            dias = dia_table.objects.filter(status=1,id__in=unique_dia_ids).values('id', 'name')


            # ✅ Fix this line
            fabrics = fabric_program_table.objects.filter(status=1,id__in=unique_fabric_ids).values('id', 'name')

            # Then this works correctly:
            fabric_map = {p['id']: p['name'] for p in fabrics}


            sub_knittings = sub_knitting_table.objects.filter(status=1,
                tm_id__in=unique_program_ids
            ).values(
                'tm_id', 'fabric_id'
            ).annotate(
                gauge_id=Max('gauge'),
                tex_id=Max('tex'),
                gsm=Max('gsm'),
                count_id=Max('count_id'),
            )

            sub_knit_map = {
                (item['tm_id'], item['fabric_id']): {
                    'gauge_id': item['gauge_id'],
                    'tex_id': item['tex_id'],
                    'gsm': item['gsm'],
                    'count_id': item['count_id'],
                }
                for item in sub_knittings
            }

            # Build fast lookup maps
            program_map = {p['id']: p['name'] for p in programs}
            fabric_map = {p['id']: p['name'] for p in fabrics}
            gauge_ids = [r['gauge_id'] for r in sub_knittings if r.get('gauge_id')]
            tex_ids = [r['tex_id'] for r in sub_knittings if r.get('tex_id')] 
            gsm_ids = [r['gsm'] for r in sub_knittings if r.get('gsm')]
            yarn_ids = [r['count_id'] for r in sub_knittings if r.get('count_id')]

            gauge_map = {g.id: g.name for g in gauge_table.objects.filter(status=1,id__in=gauge_ids)}
            tex_map = {t.id: t.name for t in tex_table.objects.filter(status=1,id__in=tex_ids)}
            # gsm_map = {g.id: g.name for g in gsm_table.objects.filter(status=1,id__in=gsm_ids)}

                    #     #     row['gsm_name'] = gsm_map.get(row.get('gsm'), '')

            yarn_map = {y.id: y.name for y in count_table.objects.filter(status=1,id__in=yarn_ids)}
            fab = {y.id: y.name for y in fabric_program_table.objects.filter(status=1,id__in=fabric_map)}



            for row in results:
                row['program_name'] = program_map.get(row['program_id'], '')
                row['fabric_name'] = fabric_map.get(row['fabric_id'], '')

                key = (row['program_id'], row['fabric_id'])
                sub_data = sub_knit_map.get(key, {})
                row['gauge_id'] = sub_data.get('gauge_id')
                row['tex_id'] = sub_data.get('tex_id')
                row['gsm'] = sub_data.get('gsm')  # Already storing GSM
                row['count_id'] = sub_data.get('count_id')

                row['gauge_name'] = gauge_map.get(row.get('gauge_id'), '')
                row['tex_name'] = tex_map.get(row.get('tex_id'), '')
                row['gsm_name'] = row.get('gsm', '')  # ✅ Use raw GSM
                row['yarn_count_name'] = yarn_map.get(row.get('count_id'), '')
                row['fabric_name'] = fab.get(row.get('fabric_id'), '')  # ✅ Use final resolved name


        return JsonResponse({ 
            'status': 'success',
            'stock_summary': results, 
            'prg_name': list(programs),
            'fabric_name': list(fabrics),
            'dia_name': list(dias),
        })


    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# ``````````````````````````````````````````````````````````````````````````````````````````````````````

from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce

# def fetch_dyeing_program_aggregates(master_id):
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT 
#                 dp.tm_id,
#                 dp.dia_id,
#                 dp.color_id,
#                 dp.fabric_id,
#                 dp.yarn_count_id,
#                 dp.tex_id,
#                 dp.gauge_id,
#                 dp.gsm,
#                 COALESCE(SUM(dp.roll), 0) AS prg_roll,
#                 COALESCE(SUM(dp.roll_wt), 0) AS program_total_weight,
#                 COALESCE(SUM(go.roll), 0) AS outward_roll,
#                 COALESCE(SUM(go.gross_wt), 0) AS outward_total_weight
#             FROM tx_dyeing_program dp
#             LEFT JOIN tm_dyeing_program dm ON dp.tm_id = dm.id
#             LEFT JOIN tx_gf_delivery go 
#                 ON dp.dia_id = go.dia_id 
#                 AND dp.color_id = go.color_id 
#                 AND dp.fabric_id = go.fabric_id 
#                 AND go.status = 1
#             WHERE dp.tm_id = %s AND dp.status = 1
#             GROUP BY dp.tm_id, dp.dia_id, dp.color_id, dp.fabric_id
#         """, [master_id])

#         columns = [col[0] for col in cursor.description]
#         return [dict(zip(columns, row)) for row in cursor.fetchall()]


# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method != 'POST':
#         return JsonResponse({'message': 'error', 'error': 'Invalid request method'})

#     master_id = request.POST.get('prg_id')
#     if not master_id:
#         return JsonResponse({'message': 'error', 'error': 'Missing prg_id'})

#     try:
#         aggregates = fetch_dyeing_program_aggregates(master_id)

#         grouped_data = defaultdict(lambda: {
#             'dias': {},
#             'outward': {},
#             'fabric_id': None,
#             'color_id': None,
#             'dia_id': None,
#             'tex_id': None,
#             'gauge_id': None,
#             'yarn_count_id': None,
#             'gsm': None,
#             'fabric': '',
#             'color': '',
#         })

#         dia_set = set()

#         for row in aggregates:
#             dia_id = row['dia_id']
#             dia_name = getItemNameById(dia_table, dia_id)
#             color_id = row['color_id']
#             fabric_id = row['fabric_id']
#             dia_id = row['dia_id']
#             tex_id = row['tex_id']
#             gauge_id = row['gauge_id']
#             yarn_count_id = row['yarn_count_id']
#             gsm = row['gsm']
#             key = (fabric_id, color_id,yarn_count_id,tex_id, gauge_id,dia_id,gsm)
#             print('key')
#             dia_set.add((dia_id, dia_name))

#             grouped_data[key]['fabric_id'] = fabric_id
#             grouped_data[key]['color_id'] = color_id
#             grouped_data[key]['dia_id'] = dia_id
#             grouped_data[key]['yarn_count_id'] = yarn_count_id
#             grouped_data[key]['gauge_id'] = gauge_id
#             grouped_data[key]['tex_id'] = tex_id
#             grouped_data[key]['gsm'] = gsm
#             grouped_data[key]['fabric'] = getItemFabNameById(fabric_program_table, fabric_id)
#             grouped_data[key]['color'] = getItemNameById(color_table, color_id)

#             grouped_data[key]['dias'][dia_name] = {
#                 'dia_id': dia_id,
#                 'roll': float(row['prg_roll']),
#                 'roll_wt': float(row['program_total_weight']),
#             }

#             grouped_data[key]['outward'][dia_name] = {
#                 'roll': float(row['outward_roll']),
#                 'roll_wt': float(row['outward_total_weight']),
#             }

#         # Ensure all dias exist in each row
#         for key, data in grouped_data.items():
#             for dia_id, dia_name in dia_set:
#                 if dia_name not in data['dias']:
#                     data['dias'][dia_name] = {'dia_id': dia_id, 'roll': 0, 'roll_wt': 0}
#                 if dia_name not in data['outward']:
#                     data['outward'][dia_name] = {'roll': 0, 'roll_wt': 0}

#         # Prepare rows
#         rows = []

#         for (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, dia_id, gsm), data in grouped_data.items():
#             row = {
#                 'fabric': data['fabric'],
#                 'fabric_id': fabric_id,
#                 'color': data['color'],
#                 'color_id': color_id,
#                 'outward': data['outward'],
#                 'dia_id': dia_id,
#                 'gauge_id': gauge_id,
#                 'tex_id': tex_id,
#                 'yarn_count_id': yarn_count_id,
#                 'gsm': gsm,
#             }
#             for dia_id_item, dia_name in dia_set:
#                 row[dia_name] = data['dias'][dia_name]
#             rows.append(row)


#         fabric_ids = list(set(key[0] for key in grouped_data.keys()))

#         lots = list(
#             grey_fabric_available_inward_table.objects.filter(
#                 available_wt__gt=0,
#                 fabric_id__in=fabric_ids
#             ).values_list('lot_no', flat=True).distinct().order_by('lot_no')
#         )

#         return JsonResponse({
#             'dias': sorted(list(dia_set), key=lambda x: x[1]),
#             'rows': rows,
#             'lots': lots,
#         }) 

#     except Exception as e:
#         return JsonResponse({'message': 'error', 'error': str(e)})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.db import connection



def fetch_dyeing_program_aggregates(master_id, color_ids=None):
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                dp.tm_id,
                dp.dia_id,
                dp.color_id,
                dp.fabric_id,
                dp.yarn_count_id,
                dp.tex_id,
                dp.gauge_id,
                dp.gsm,
                COALESCE(SUM(dp.roll), 0) AS prg_roll,
                COALESCE(SUM(dp.roll_wt), 0) AS program_total_weight,
                COALESCE(SUM(go.roll), 0) AS outward_roll,
                COALESCE(SUM(go.gross_wt), 0) AS outward_total_weight
            FROM tx_dyeing_program dp
            LEFT JOIN tm_dyeing_program dm ON dp.tm_id = dm.id
            LEFT JOIN tx_gf_delivery go 
                ON dp.dia_id = go.dia_id 
                AND dp.color_id = go.color_id 
                AND dp.fabric_id = go.fabric_id 
                AND go.status = 1
            WHERE dp.tm_id = %s AND dp.status = 1
        """
        params = [master_id]

        if color_ids:
            placeholders = ','.join(['%s'] * len(color_ids))
            sql += f" AND dp.color_id IN ({placeholders})"
            params.extend(color_ids)

        sql += """
            GROUP BY dp.tm_id, dp.dia_id, dp.color_id, dp.fabric_id,
                     dp.yarn_count_id, dp.tex_id, dp.gauge_id, dp.gsm
        """

        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]



from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def dyeing_program_list(request): 
    if request.method != 'POST':
        return JsonResponse({'message': 'error', 'error': 'Invalid request method'})

    master_id = request.POST.get('prg_id')
    color_ids = request.POST.getlist('color_id[]')  # Read array from POST

    if not master_id:
        return JsonResponse({'message': 'error', 'error': 'Missing prg_id'})

    try:
        # Convert color_ids to int
        color_ids = list(map(int, color_ids)) if color_ids else None

        aggregates = fetch_dyeing_program_aggregates(master_id, color_ids)

        grouped_data = defaultdict(lambda: {
            'dias': {},
            'outward': {},
            'fabric_id': None,
            'color_id': None,
            'tex_id': None,
            'gauge_id': None,
            'yarn_count_id': None,
            'gsm': None,
            'fabric': '',
            'color': '',
        })

        dia_set = set()

        for row in aggregates:
            dia_id = row['dia_id']
            dia_name = getItemNameById(dia_table, dia_id)
            color_id = row['color_id']
            fabric_id = row['fabric_id']
            tex_id = row['tex_id']
            gauge_id = row['gauge_id']
            yarn_count_id = row['yarn_count_id']
            gsm = row['gsm']

            # Use fabric, color, and specs as key — not dia!
            key = (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, gsm)

            dia_set.add((dia_id, dia_name))

            grouped_data[key].update({
                'fabric_id': fabric_id,
                'color_id': color_id,
                'gsm': gsm,
                'tex_id': tex_id,
                'gauge_id': gauge_id,
                'yarn_count_id': yarn_count_id,
                'fabric': getItemFabNameById(fabric_program_table, fabric_id),
                'color': getItemNameById(color_table, color_id),
            })

            grouped_data[key]['dias'][dia_name] = {
                'dia_id': dia_id,
                'roll': float(row['prg_roll']),
                'roll_wt': float(row['program_total_weight']),
            }

            grouped_data[key]['outward'][dia_name] = {
                'roll': float(row['outward_roll']),
                'roll_wt': float(row['outward_total_weight']),
            }

        # Fill missing dias with 0s for consistency
        for key, data in grouped_data.items():
            for dia_id, dia_name in dia_set:
                data['dias'].setdefault(dia_name, {'dia_id': dia_id, 'roll': 0, 'roll_wt': 0})
                data['outward'].setdefault(dia_name, {'roll': 0, 'roll_wt': 0})

        rows = []
        for (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, gsm), data in grouped_data.items():
            row = {
                'fabric': data['fabric'],
                'fabric_id': fabric_id,
                'color': data['color'],
                'color_id': color_id,
                'outward': data['outward'],
                'gauge_id': gauge_id,
                'tex_id': tex_id,
                'yarn_count_id': yarn_count_id,
                'gsm': gsm,
            }
            for dia_id_item, dia_name in dia_set:
                row[dia_name] = data['dias'][dia_name]
            rows.append(row)

        fabric_ids = list(set(key[0] for key in grouped_data.keys()))
        lots = list(
            grey_fabric_available_inward_table.objects.filter(
                available_wt__gt=0,
                fabric_id__in=fabric_ids
            ).values_list('lot_no', flat=True).distinct().order_by('lot_no')
        )

        return JsonResponse({
            'dias': sorted(list(dia_set), key=lambda x: x[1]),
            'rows': rows,
            'lots': lots,
        }) 

    except Exception as e:
        return JsonResponse({'message': 'error', 'error': str(e)})

# def fetch_dyeing_program_aggregates(master_id, color_id=None):
#     with connection.cursor() as cursor:
#         sql = """
#             SELECT 
#                 dp.tm_id,
#                 dp.dia_id,
#                 dp.color_id,
#                 dp.fabric_id,
#                 dp.yarn_count_id,
#                 dp.tex_id,
#                 dp.gauge_id,
#                 dp.gsm,
#                 COALESCE(SUM(dp.roll), 0) AS prg_roll,
#                 COALESCE(SUM(dp.roll_wt), 0) AS program_total_weight,
#                 COALESCE(SUM(go.roll), 0) AS outward_roll,
#                 COALESCE(SUM(go.gross_wt), 0) AS outward_total_weight
#             FROM tx_dyeing_program dp
#             LEFT JOIN tm_dyeing_program dm ON dp.tm_id = dm.id
#             LEFT JOIN tx_gf_delivery go 
#                 ON dp.dia_id = go.dia_id 
#                 AND dp.color_id = go.color_id 
#                 AND dp.fabric_id = go.fabric_id 
#                 AND go.status = 1
#             WHERE dp.tm_id = %s AND dp.status = 1
#         """
#         params = [master_id]

#         if color_id:
#             sql += " AND dp.color_id = %s"
#             params.append(color_id)

#         sql += """
#             GROUP BY dp.tm_id, dp.dia_id, dp.color_id, dp.fabric_id,
#                      dp.yarn_count_id, dp.tex_id, dp.gauge_id, dp.gsm
#         """

#         cursor.execute(sql, params)
#         columns = [col[0] for col in cursor.description]
#         return [dict(zip(columns, row)) for row in cursor.fetchall()]


# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method != 'POST':
#         return JsonResponse({'message': 'error', 'error': 'Invalid request method'})

#     master_id = request.POST.get('prg_id')
#     color_id = request.POST.get('color_id')

#     if not master_id:
#         return JsonResponse({'message': 'error', 'error': 'Missing prg_id'})

#     try:
#         aggregates = fetch_dyeing_program_aggregates(master_id, color_id)

#         grouped_data = defaultdict(lambda: {
#             'dias': {},
#             'outward': {},
#             'fabric_id': None,
#             'color_id': None,
#             'dia_id': None,
#             'tex_id': None,
#             'gauge_id': None,
#             'yarn_count_id': None,
#             'gsm': None,
#             'fabric': '',
#             'color': '',
#         })

#         dia_set = set()

#         for row in aggregates:
#             dia_id = row['dia_id']
#             dia_name = getItemNameById(dia_table, dia_id)
#             color_id = row['color_id']
#             fabric_id = row['fabric_id']
#             tex_id = row['tex_id']
#             gauge_id = row['gauge_id']
#             yarn_count_id = row['yarn_count_id']
#             gsm = row['gsm']
#             key = (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, gsm)
#             # key = (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, dia_id, gsm)

#             dia_set.add((dia_id, dia_name))

#             grouped_data[key].update({
#                 'fabric_id': fabric_id,
#                 'color_id': color_id,
#                 'dia_id': dia_id,
#                 'yarn_count_id': yarn_count_id,
#                 'gauge_id': gauge_id,
#                 'tex_id': tex_id,
#                 'gsm': gsm,
#                 'fabric': getItemFabNameById(fabric_program_table, fabric_id),
#                 'color': getItemNameById(color_table, color_id),
#             })

#             grouped_data[key]['dias'][dia_name] = {
#                 'dia_id': dia_id,
#                 'roll': float(row['prg_roll']),
#                 'roll_wt': float(row['program_total_weight']),
#             }

#             grouped_data[key]['outward'][dia_name] = {
#                 'roll': float(row['outward_roll']),
#                 'roll_wt': float(row['outward_total_weight']),
#             }

#         for key, data in grouped_data.items():
#             for dia_id, dia_name in dia_set:
#                 data['dias'].setdefault(dia_name, {'dia_id': dia_id, 'roll': 0, 'roll_wt': 0})
#                 data['outward'].setdefault(dia_name, {'roll': 0, 'roll_wt': 0})

#         rows = []
#         # for (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, dia_id, gsm), data in grouped_data.items():
#         #     row = {
#         #         'fabric': data['fabric'],
#         #         'fabric_id': fabric_id,
#         #         'color': data['color'],
#         #         'color_id': color_id,
#         #         'outward': data['outward'],
#         #         'dia_id': dia_id,
#         #         'gauge_id': gauge_id,
#         #         'tex_id': tex_id,
#         #         'yarn_count_id': yarn_count_id,
#         #         'gsm': gsm,
#         #     }

#         for (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, gsm), data in grouped_data.items():
#             row = {
#                 'fabric': data['fabric'],
#                 'fabric_id': fabric_id,
#                 'color': data['color'],
#                 'color_id': color_id,
#                 'outward': data['outward'],
#                 'gauge_id': gauge_id,
#                 'tex_id': tex_id,
#                 'yarn_count_id': yarn_count_id,
#                 'gsm': gsm,
#             }
#             for dia_id_item, dia_name in dia_set:
#                 row[dia_name] = data['dias'][dia_name]
#             rows.append(row)

#             # for dia_id_item, dia_name in dia_set:
#             #     row[dia_name] = data['dias'][dia_name]
#             # rows.append(row)

#         fabric_ids = list(set(key[0] for key in grouped_data.keys()))
#         lots = list(
#             grey_fabric_available_inward_table.objects.filter(
#                 available_wt__gt=0,
#                 fabric_id__in=fabric_ids
#             ).values_list('lot_no', flat=True).distinct().order_by('lot_no')
#         )

#         return JsonResponse({
#             'dias': sorted(list(dia_set), key=lambda x: x[1]),
#             'rows': rows,
#             'lots': lots,
#         }) 

#     except Exception as e:
#         return JsonResponse({'message': 'error', 'error': str(e)})

# ````````````````````````````````````````````````````````
# def fetch_dyeing_program_aggregates(master_id):
#     with connection.cursor() as cursor:
                   
#         cursor.execute("""

#          SELECT 
#             dp.tm_id,
#             dp.dia_id,
#             dp.color_id,
#             dp.fabric_id,
#             dp.roll AS prg_roll,
#             SUM(dp.roll_wt) AS program_total_weight,
           
#             go.roll AS outward_roll,
#         SUM(go.gross_wt) AS outward_total_weight
#         FROM tx_dyeing_program dp
#         LEFT JOIN tm_dyeing_program dm ON dp.tm_id = dm.id
#         LEFT JOIN tx_gf_delivery go 
#             ON dp.dia_id = go.dia_id 
#             AND dp.color_id = go.color_id 
#             AND dp.fabric_id = go.fabric_id
#         WHERE dp.tm_id = %s AND dp.status = 1
#         GROUP BY dp.tm_id, dp.dia_id, dp.color_id, dp.fabric_id
#         """, [master_id])

#         columns = [col[0] for col in cursor.description]
#         return [dict(zip(columns, row)) for row in cursor.fetchall()]

# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method != 'POST':
#         return JsonResponse({'message': 'error', 'error': 'Invalid request method'})

#     master_id = request.POST.get('prg_id')

#     print('tm-id:',master_id)
#     if not master_id:
#         return JsonResponse({'message': 'error', 'error': 'Missing prg_id'})

#     try:
#         aggregates = fetch_dyeing_program_aggregates(master_id)

#         grouped_data = defaultdict(lambda: {
#             'dias': {},
#             'outward': {},
#             'fabric_id': None,
#             'color_id': None,
#             'fabric': '',
#             'color': '',
#         })

#         dia_set = set()

#         for row in aggregates:
#             dia_id = row['dia_id']
#             dia_name = getItemNameById(dia_table, dia_id)
#             color_id = row['color_id']
#             fabric_id = row['fabric_id']
#             key = (fabric_id, color_id)

#             dia_set.add((dia_id, dia_name))

#             grouped_data[key]['fabric_id'] = fabric_id
#             grouped_data[key]['color_id'] = color_id
#             grouped_data[key]['fabric'] = getItemFabNameById(fabric_program_table, fabric_id)
#             grouped_data[key]['color'] = getItemNameById(color_table, color_id)

#             grouped_data[key]['dias'][dia_name] = {
#                 'dia_id': dia_id,
#                 'roll': float(row['prg_roll'] or 0),
#                 'roll_wt': float(row['program_total_weight'] or 0),
#             }

#             grouped_data[key]['outward'][dia_name] = {
#                 'roll': float(row['outward_roll'] or 0),
#                 'roll_wt': float(row['outward_total_weight'] or 0),
#             }

#         # Ensure all dias exist in every row
#         for key, data in grouped_data.items():
#             for dia_id, dia_name in dia_set:
#                 if dia_name not in data['dias']:
#                     data['dias'][dia_name] = {'dia_id': dia_id, 'roll': 0, 'roll_wt': 0}
#                 if dia_name not in data['outward']:
#                     data['outward'][dia_name] = {'roll': 0, 'roll_wt': 0}

#         # Final response rows
#         rows = []
#         for (fabric_id, color_id), data in grouped_data.items():
#             row = {
#                 'fabric': data['fabric'],
#                 'fabric_id': fabric_id,
#                 'color': data['color'],
#                 'color_id': color_id,
#                 'outward': data['outward'],
#             }
#             for dia_id, dia_name in dia_set:
#                 row[dia_name] = data['dias'][dia_name]
#             rows.append(row)

#         # Lot numbers
#         fabric_ids = [fabric_id for (fabric_id, _) in grouped_data.keys()]
#         lots = list(
#             grey_fabric_available_inward_table.objects.filter(
#                 available_wt__gt=0,
#                 fabric_id__in=fabric_ids
#             ).values_list('lot_no', flat=True).distinct().order_by('lot_no')
#         )

#         return JsonResponse({
#             'dias': sorted(list(dia_set), key=lambda x: x[1]),
#             'rows': rows,
#             'lots': lots,
#         })

#     except Exception as e:
#         return JsonResponse({'message': 'error', 'error': str(e)})
# `````````````````````````````````````````23-06-2025`````````````````````````````````````````````
# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method == 'POST':
#         master_id = request.POST.get('prg_id')
#         print('prg-id:',master_id)

#         if not master_id:
#             return JsonResponse({'message': 'error', 'error': 'Missing ID'})

#         try:
#             child_data = sub_dyeing_program_table.objects.filter(
#                 tm_id=master_id, status=1, is_active=1
#             )

#             dia_set = set()
#             grouped_data = defaultdict(lambda: {'dias': {}, 'outward': {}})

#             for item in child_data:
#                 fabric = getItemFabNameById(fabric_program_table, item.fabric_id)
#                 color = getItemNameById(color_table, item.color_id)
#                 dia = getItemNameById(dia_table, item.dia_id)

#                 key = (fabric, color)
#                 dia_set.add((item.dia_id, dia))

#                 grouped_data[key]['fabric'] = fabric
#                 grouped_data[key]['color'] = color
#                 grouped_data[key]['fabric_id'] = item.fabric_id
#                 grouped_data[key]['color_id'] = item.color_id

#                 grouped_data[key]['dias'][dia] = {
#                     'dia_id': item.dia_id,
#                     'roll': item.roll or 0,
#                     'roll_wt': item.roll_wt or 0
#                 }


#             # 🔁 Fetch outward data for each (fabric_id, color_id, dia_id)
#             for (fabric, color), data in grouped_data.items():
#                 fabric_id = data['fabric_id']
#                 color_id = data['color_id']



#                 outward_data = child_gf_delivery_table.objects.filter(
#                     dyeing_program_id=master_id,
#                     fabric_id=fabric_id,
#                     color_id=color_id,
#                     status=1,
#                     is_active=1
#                 ).values('dia_id').annotate(
#                     roll_sum=Coalesce(Sum('roll'), 0, output_field=DecimalField()),
#                     roll_wt_sum=Coalesce(Sum('roll_wt'), 0, output_field=DecimalField())
#                 )
#                 print('g-data:',outward_data)

#                 for out in outward_data:
#                     dia_name = getItemNameById(dia_table, out['dia_id'])
#                     data['outward'][dia_name] = {
#                         'roll': out['roll_sum'],
#                         'roll_wt': out['roll_wt_sum']
#                     }

#                 # for out in outward_data:
#                 #     dia_name = getItemNameById(dia_table, out['dia_id'])
#                 #     data['outward'][dia_name] = {
#                 #         'roll': out['roll'],
#                 #         'roll_wt': out['roll_wt']
#                 #     }

#             rows = []
#             for (fabric, color), data in grouped_data.items():
#                 row = {
#                     'fabric': data['fabric'],
#                     'fabric_id': data['fabric_id'],
#                     'color': data['color'],
#                     'color_id': data['color_id'],
#                     'outward': data['outward']
#                 }
#                 for dia_id, dia_name in dia_set:
#                     row[dia_name] = data['dias'].get(dia_name, {
#                         'dia_id': dia_id,
#                         'roll': 0,
#                         'roll_wt': 0
#                     })
#                 rows.append(row)

#             fabric_ids = child_data.values_list('fabric_id', flat=True).distinct()
#             lots = grey_fabric_available_inward_table.objects.filter(
#                 available_wt__gt=0,
#                 fabric_id__in=fabric_ids
#             ).values_list('lot_no', flat=True).distinct().order_by('lot_no')

#             return JsonResponse({
#                 'dias': sorted(list(dia_set), key=lambda x: x[1]),
#                 'rows': rows,
#                 'lots': list(lots),
#             })

#         except Exception as e:
#             return JsonResponse({'message': 'error', 'error': str(e)})

#     return JsonResponse({'message': 'error', 'error': 'Invalid request method'})



# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method == 'POST':
#         master_id = request.POST.get('prg_id')

#         if not master_id:
#             return JsonResponse({'message': 'error', 'error': 'Missing ID'})

#         try:
#             child_data = sub_dyeing_program_table.objects.filter(
#                 tm_id=master_id, status=1, is_active=1
#             ) 

#             dia_set = set()
#             grouped_data = defaultdict(lambda: {'dias': {}})


#             for item in child_data:
#                 fabric = getItemFabNameById(fabric_program_table, item.fabric_id)
#                 color = getItemNameById(color_table, item.color_id)
#                 dia = getItemNameById(dia_table, item.dia_id)

#                 key = (fabric, color)
#                 dia_set.add((item.dia_id, dia))  # tuple of (id, name)

#                 grouped_data[key]['fabric'] = fabric
#                 grouped_data[key]['color'] = color
#                 grouped_data[key]['fabric_id'] = item.fabric_id
#                 grouped_data[key]['color_id'] = item.color_id
#                 grouped_data[key]['dias'][dia] = {
#                     'dia_id': item.dia_id,
#                     'roll': item.roll or 0,
#                     'roll_wt': item.roll_wt or 0
#                 }

#             rows = []
#             for (fabric, color), data in grouped_data.items():
#                 row = {
#                     'fabric': data['fabric'],
#                     'fabric_id': data['fabric_id'],
#                     'color': data['color'],
#                     'color_id': data['color_id']
#                 }
#                 for dia_id, dia_name in dia_set:
#                     row[dia_name] = data['dias'].get(dia_name, {
#                         'dia_id': dia_id,
#                         'roll': 0,
#                         'roll_wt': 0
#                     })
#                 rows.append(row)

#             fabric_ids = child_data.values_list('fabric_id', flat=True).distinct()
#             print('fab-ids:',fabric_ids)
#             lots = grey_fabric_available_inward_table.objects.filter(
#                 available_wt__gt=0,
#                 fabric_id__in=fabric_ids
#             ).values_list('lot_no', flat=True).distinct().order_by('lot_no')

#             return JsonResponse({
#                 'dias': sorted(list(dia_set), key=lambda x: x[1]),  # sorted by name
#                 'rows': rows,
#                 'lots': list(lots),
#             })



#         except Exception as e:
#             return JsonResponse({'message': 'error', 'error': str(e)})

#     return JsonResponse({'message': 'error', 'error': 'Invalid request method'})


from django.http import JsonResponse




@csrf_exempt
def get_dye_program_fabric_list(request):
    if request.method == 'POST':
        prg_id = request.POST.get('prg_id')
        if not prg_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            prg_details = list(sub_dyeing_program_table.objects.filter(
                tm_id=prg_id, is_active=1, status=1
            ).values('id', 'fabric_id', 'color_id').order_by('color_id'))

            if not prg_details:
                return JsonResponse({'item': [], 'colors': []})

            fabric_ids = set(item['fabric_id'] for item in prg_details)
            # color_ids = set(item['color_id'] for item in prg_details)

            # Optionally fetch fabric names if needed
            fabric_names = fabric_program_table.objects.filter(id__in=fabric_ids).values('id', 'name')
            # color_details = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name')

            return JsonResponse({
                'item': prg_details,
                # 'colors': list(color_details),
                'fabrics': list(fabric_names),
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)






@csrf_exempt
def get_dye_program_colors_list(request):
    if request.method == 'POST':
        prg_id = request.POST.get('prg_id')
        fabric_id = request.POST.get('fabric_id')
        if not prg_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)

        try:
            prg_details = list(sub_dyeing_program_table.objects.filter(
                tm_id=prg_id,fabric_id = fabric_id, is_active=1, status=1
            ).values('id', 'color_id').order_by('color_id'))
            print('details:',prg_details)
            if not prg_details:
                return JsonResponse({'item': [], 'colors': []})
# 
            # fabric_ids = set(item['fabric_id'] for item in prg_details)
            color_ids = set(item['color_id'] for item in prg_details)

            # Optionally fetch fabric names if needed
            color_details = color_table.objects.filter(status=1, id__in=color_ids).values('id', 'name')
            print('colors:',list(color_details))

            return JsonResponse({
                'item': prg_details,
                'colors': list(color_details),
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)




# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method == 'POST':
#         master_id = request.POST.get('prg_id')
#         print('dyeing-ID:', master_id) 

#         if master_id: 
#             try:
#                 child_data = sub_dyeing_program_table.objects.filter(
#                     tm_id=master_id, status=1, is_active=1
#                 )

#                 dias_set = set()
#                 data_map = {}

#                 for item in child_data:
#                     fabric_name = getItemFabNameById(fabric_program_table, item.fabric_id)
#                     color_name = getItemNameById(color_table, item.color_id)
#                     dia = getItemNameById(dia_table, item.dia_id)

#                     dias_set.add(dia)

#                     key = (fabric_name, color_name)
#                     if key not in data_map:
#                         data_map[key] = {}

#                     data_map[key][dia] = {
#                         "roll": item.roll or 0,
#                         "roll_wt": float(item.roll_wt or 0)
#                     }

#                 dias_list = sorted(dias_set, key=lambda x: int(x))  # e.g., ["24", "26", "30"]

#                 rows = []
#                 for (fabric, color), dia_data in data_map.items():
#                     row = {
#                         "fabric": fabric,
#                         "color": color
#                     }
#                     for dia in dias_list:
#                         row[dia] = dia_data.get(dia, None)
#                     rows.append(row)

#                 return JsonResponse({
#                     "dias": dias_list,
#                     "rows": rows
#                 })

#             except Exception as e:
#                 return JsonResponse({'error': str(e)})

#         else:
#             return JsonResponse({'error': 'Invalid request, missing ID parameter'})
#     else:
#         return JsonResponse({'error': 'Invalid request, POST method expected'})


# @csrf_exempt
# def dyeing_program_list(request): 
#     if request.method == 'POST':
#         master_id = request.POST.get('prg_id')
#         print('dyeing-ID:', master_id) 

#         if master_id: 
#             try:
#                 # Fetch child dyeing program entries
#                 child_data = sub_dyeing_program_table.objects.filter(
#                     tm_id=master_id, status=1, is_active=1
#                 )

#                 formatted_data = []

#                 for index, item in enumerate(child_data, start=1):
#                     formatted_data.append({
#                         'action': f'''
#                             <button type="button" onclick="knitting_prg_detail_edit('{item.id}')" class="btn btn-primary btn-xs">
#                                 <i class="feather icon-edit"></i>
#                             </button>
#                             <button type="button" onclick="knitting_detail_delete('{item.id}')" class="btn btn-danger btn-xs">
#                                 <i class="feather icon-trash-2"></i>
#                             </button>
#                         ''',
#                         'id': index,
#                         'fabric_id': getItemFabNameById(fabric_program_table, item.fabric_id),
#                         'dia': getItemNameById(dia_table, item.dia_id),
#                         'color': getItemNameById(color_table, item.color_id),
#                         'fabric_id_raw': item.fabric_id,
#                         'dia_id_raw': item.dia_id,
#                         'roll': item.roll or '-',
#                         'roll_wt': item.roll_wt or '-',
#                         'status': '<span class="badge text-bg-success">Active</span>' if item.is_active else '<span class="badge text-bg-danger">Inactive</span>'
#                     })

#                 formatted_data.reverse()

#                 return JsonResponse({
#                     'data': formatted_data
#                 })

#             except Exception as e:
#                 return JsonResponse({'error': str(e)})

#         else:
#             return JsonResponse({'error': 'Invalid request, missing ID parameter'})
#     else:
#         return JsonResponse({'error': 'Invalid request, POST method expected'})


# `````````````````````````````````````````````````` add outward ``````````````````````````````````````````

# def insert_grey_fab_outward(request):
#     if request.method == 'POST':
#         user_id = request.session['user_id']
#         company_id = request.session['company_id']

#         try:
#             do_date = request.POST.get('outward_date')
#             lot_no = request.POST.get('lot_no')
#             program_id = request.POST.get('program_id')
#             deliver_id = request.POST.get('party_id')
#             fabric_id = request.POST.get('fabric_id')
#             color_id = request.POST.get('color_id')
#             remarks = request.POST.get('remarks')
#             dye_prg_id = request.POST.get('prg_id')
#             chemical_data = json.loads(request.POST.get('chemical_data', '[]'))


#             for outward_group in chemical_data: 
#                 fabric = outward_group.get('fabric')
#                 color = outward_group.get('color')
#                 items = outward_group.get('items', [])

              
#                 # ➤ Create parent record 
#                 new_do_number = generate_outward_num_series()

#                 parent = parent_gf_delivery_table.objects.create(
#                     do_number=new_do_number,
#                     company_id=company_id,
#                     cfyear=2025,
#                     delivery_date=do_date,
#                     party_id=deliver_id,
#                     knitting_program_id=program_id,
#                     dyeing_program_id=dye_prg_id,
#                     inward_id=0,
#                     lot_no=lot_no,
#                     fabric_id = fabric_id,
#                     color_id = color_id,
#                     total_wt=0,
#                     gross_wt=0,
#                     # fabric_id=None,  # optional if you're using it in child only
#                     # color_id=None,
#                     remarks=remarks,
#                     created_by=user_id
#                 )

#                 total_gross = Decimal('0.00')
#                 total_quantity = Decimal('0.00')

#                 for item in items:
#                     roll = item.get('roll') or 0
#                     roll_wt = item.get('roll_wt') or 0
#                     gross_wt = item.get('gross_wt') or 0

#                     child_gf_delivery_table.objects.create(
#                         company_id=company_id,
#                         cfyear=2025,
#                         tm_id=parent.id,
#                         knitting_program_id=program_id,
#                         dyeing_program_id=dye_prg_id,
#                         lot_no=lot_no,
#                         party_id=deliver_id,
#                         yarn_count_id=item.get('yarn_count_id'),
#                         fabric_id=item.get('fabric_id'),
#                         gauge_id=item.get('gauge_id'),
#                         tex_id=item.get('tex_id'),
#                         gsm=item.get('gsm'),
#                         dia_id=item.get('dia_id'),
#                         color_id=item.get('color_id'),
#                         roll=roll,
#                         roll_wt=roll_wt,
#                         gross_wt=gross_wt,
#                         inward_id=0,
#                         created_by=user_id
#                     )

#                     total_gross += Decimal(str(gross_wt))
#                     total_quantity += Decimal(str(roll_wt))

#                 parent.total_wt = total_quantity
#                 parent.gross_wt = total_gross
#                 parent.save()

#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Outward data saved successfully.',
#                 'do_number': new_do_number
#             })

#         except Exception as e:
#             print(f"❌ Error: {e}")
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return render(request, 'outward/grey_fab_outward_add.html')

# def insert_grey_fab_outward(request):
#     if request.method == 'POST':
#         user_id = request.session['user_id']
#         company_id = request.session['company_id']

#         try:
#             do_date = request.POST.get('outward_date')
#             lot_no = request.POST.get('lot_no')
#             program_id = request.POST.get('program_id')
#             deliver_id = request.POST.get('party_id')
#             fabric_id = request.POST.get('fabric_id')
#             # color_id = request.POST.get('color_id')  # this can remain if it's the selected filter
#             color_ids = request.POST.getlist('color_id[]')  # ⬅ expects multiple <input name="color_id[]">
#             color_id_str = ','.join(color_ids)  # ⬅ e.g., "2,3"
#             remarks = request.POST.get('remarks')
#             dye_prg_id = request.POST.get('prg_id')
#             chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
#             delivery_data_raw = request.POST.get('delivery_data', '[]')
#             delivery_data = json.loads(delivery_data_raw) if delivery_data_raw else []
#             if not delivery_data:
#                 return JsonResponse({'status': 'Failed', 'message': 'Delivery data required.'}, status=400)

#             # ➤ Create parent record just once
#             new_do_number = generate_outward_num_series()

#             parent = parent_gf_delivery_table.objects.create(
#                 do_number=new_do_number,
#                 company_id=company_id,
#                 cfyear=2025,
#                 delivery_date=do_date,
#                 party_id=deliver_id,
#                 knitting_program_id=program_id,
#                 dyeing_program_id=dye_prg_id,
#                 inward_id=0,
#                 lot_no=lot_no,
#                 fabric_id=fabric_id,
#                 color_id=color_id_str,  # you can keep this as the filter color or null if not needed
#                 total_wt=0,
#                 gross_wt=0,
#                 remarks=remarks,
#                 created_by=user_id
#             )

#             total_gross = Decimal('0.00')
#             total_quantity = Decimal('0.00')


#             # Save delivery details
#             for delivery in delivery_data:
#                 sub_child_gf_delivery_detail_table.objects.create(
#                     tm_id=parent.id,
#                     company_id=company_id,
#                     cfyear=2025, 
#                     party_id=int(delivery['delivery_party_id']),
#                     remarks=delivery['remarks'],
#                     is_active=1,
#                     status=1,
#                     created_by=user_id,
#                     created_on=timezone.now(),
#                 )


#             # ➤ Now loop through all color groups and add child records
#             for outward_group in chemical_data:
#                 items = outward_group.get('items', [])
#                 for item in items:
#                     roll = item.get('roll') or 0
#                     roll_wt = item.get('roll_wt') or 0
#                     gross_wt = item.get('gross_wt') or 0

#                     child_gf_delivery_table.objects.create(
#                         company_id=company_id,
#                         cfyear=2025,
#                         tm_id=parent.id,
#                         knitting_program_id=program_id,
#                         dyeing_program_id=dye_prg_id,
#                         lot_no=lot_no,
#                         party_id=deliver_id,
#                         yarn_count_id=item.get('yarn_count_id'),
#                         fabric_id=item.get('fabric_id'),
#                         gauge_id=item.get('gauge_id'),
#                         tex_id=item.get('tex_id'),
#                         gsm=item.get('gsm'),
#                         dia_id=item.get('dia_id'),
#                         color_id=item.get('color_id'),
#                         roll=roll,
#                         roll_wt=roll_wt,
#                         gross_wt=gross_wt,
#                         inward_id=0,
#                         created_by=user_id
#                     )

#                     total_gross += Decimal(str(gross_wt))
#                     total_quantity += Decimal(str(roll_wt))

#             # ➤ Update totals on parent
#             parent.total_wt = total_quantity
#             parent.gross_wt = total_gross
#             parent.save()

#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Outward data saved successfully.',
#                 'do_number': new_do_number
#             })

#         except Exception as e:
#             print(f"❌ Error: {e}")
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return render(request, 'outward/grey_fab_outward_add.html')



@csrf_exempt  # If CSRF token not passed via AJAX 
def insert_grey_fab_outward(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
 
        try: 
            do_date = request.POST.get('outward_date')
            lot_no = request.POST.get('lot_no')
            program_id = request.POST.get('program_id')
            deliver_id = request.POST.get('party_id')
            fabric_id = request.POST.get('fabric_id')
            
            # Get multiple color IDs
            color_ids = request.POST.getlist('color_id[]')  # e.g., ['8', '25']
            color_id_str = ','.join(color_ids)              # e.g., '8,25'
            
            remarks = request.POST.get('remarks')
            dye_prg_id = request.POST.get('prg_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
            delivery_data = json.loads(request.POST.get('delivery_data', '[]'))
            
            if not delivery_data:
                return JsonResponse({'status': 'Failed', 'message': 'Delivery data required.'}, status=400)

            new_do_number = generate_outward_num_series()

            parent = parent_gf_delivery_table.objects.create(
                do_number=new_do_number,
                company_id=company_id,
                cfyear=2025,
                delivery_date=do_date,
                party_id=deliver_id,
                knitting_program_id=program_id,
                dyeing_program_id=dye_prg_id,
                inward_id=0,
                lot_no=lot_no,
                fabric_id=fabric_id,
                color_id=color_id_str,
                total_wt=0,
                gross_wt=0,
                remarks=remarks,
                created_by=user_id
            )

            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')

            # Save sub-delivery
            for delivery in delivery_data:
                sub_child_gf_delivery_detail_table.objects.create(
                    tm_id=parent.id,
                    company_id=company_id,
                    cfyear=2025,
                    party_id=int(delivery['delivery_party_id']),
                    remarks=delivery['remarks'],
                    is_active=1,
                    status=1,
                    created_by=user_id,
                    created_on=timezone.now(),
                )

            # Save child records
            for group in chemical_data:
                for item in group.get('items', []):
                    roll = item.get('roll') or 0
                    roll_wt = item.get('roll_wt') or 0
                    gross_wt = item.get('gross_wt') or 0

                    child_gf_delivery_table.objects.create(
                        company_id=company_id,
                        cfyear=2025,
                        tm_id=parent.id,
                        knitting_program_id=program_id,
                        dyeing_program_id=dye_prg_id,
                        lot_no=lot_no,
                        party_id=deliver_id,
                        yarn_count_id=item.get('yarn_count_id'),
                        fabric_id=item.get('fabric_id'),
                        gauge_id=item.get('gauge_id'),
                        tex_id=item.get('tex_id'),
                        gsm=item.get('gsm'),
                        dia_id=item.get('dia_id'),
                        color_id=item.get('color_id'),
                        roll=roll,
                        roll_wt=roll_wt,
                        gross_wt=gross_wt,
                        inward_id=0,
                        created_by=user_id
                    )

                    total_gross += Decimal(str(gross_wt))
                    total_quantity += Decimal(str(roll_wt))

            parent.total_wt = total_quantity
            parent.gross_wt = total_gross
            parent.save()

            return JsonResponse({'status': 'success', 'message': 'Outward data saved successfully.', 'do_number': new_do_number})

        except Exception as e:
            print(f"❌ Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'outward/grey_fab_outward_add.html')


def insert_grey_fab_outward_bk_27062025(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        try: 
            # Extracting data from the request
            do_date = request.POST.get('outward_date') 
            # receive_date = request.POST.get('receive_date') 
            # raw_date = request.POST.get('receive_date')
            
            lot_no = request.POST.get('lot_no')
            inward_id = request.POST.get('inward_id') 
            program_id = request.POST.get('program_id')
            # po_id = request.POST.get('po_id')
            deliver_id = request.POST.get('party_id')
            remarks = request.POST.get('remarks') 
            dye_prg_id = request.POST.get('prg_id') 
            do_number = request.POST.get('do_number')
            fabric_id = request.POST.get('fabric_id')
            color_id = request.POST.get('color_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 

            print('data:',chemical_data)
          
            # Get PO IDs 
            # po_ids = request.GET.getlist('po_id[]')  
            # po_ids_str = ",".join(po_ids)
            # tx_inward_str = ",".join([str(i) for i in tx_inward])  # Convert to string

            # Create a new entry in yarn_delivery_table (Parent table)

            # do_number = generate_do_num_series(yarn_delivery_table, 'do_number', padding=3, prefix='DO')
            material_request = parent_gf_delivery_table.objects.create(
                do_number=do_number,
                company_id=company_id,
                cfyear = 2025,
              
                delivery_date=do_date, 
                party_id=deliver_id,
                knitting_program_id=program_id, 
                dyeing_program_id=dye_prg_id,
                inward_id= 0, #inward_id or 0,
                lot_no=lot_no,
                total_wt= 0,#request.POST.get('total_wt',0.0),
                gross_wt=0, # request.POST.get('sub_total',0.0),
                fabric_id=fabric_id,
                color_id=color_id,
                remarks=remarks,
                created_by=user_id,
                # created_on=datetime.now()
            )
            print('material:',material_request)

           
            
            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')  # use Decimal for both if you're working with decimals

            for item in chemical_data:
                inward = item.get('inward_id' , 0)
                fabric_id = item.get('fabric_id')
                yarn_count_id = item.get('yarn_count_id')
                gauge_id = item.get('gauge_id')
                tex_id = item.get('tex_id')
                dia_id = item.get('dia_id') 
                color_id = item.get('color_id') 
                gsm = item.get('gsm') 
                roll = item.get('roll') 

                # Create sub yarn delivery entry
                child_gf_delivery_table.objects.create(
                    company_id=company_id,
                    cfyear=2025, 
                    tm_id=material_request.id, 
                   
                    knitting_program_id = program_id,
                    dyeing_program_id=dye_prg_id, 

                    lot_no = lot_no,
                    party_id=deliver_id,
                    yarn_count_id=yarn_count_id,
                    fabric_id=fabric_id,
                    gauge_id=gauge_id,
                    tex_id=tex_id,
                    gsm=gsm,
                    dia_id = dia_id,
                    color_id = color_id,
                    roll=roll, 
                    # inward_id=inward,
                    inward_id =0,  #item.get('inward_id' | 0)



                    roll_wt=item.get('roll_wt'),
                    gross_wt=item.get('gross_wt', 0),
                    created_by=user_id,
                    # created_on=datetime.now()
                )

                # Convert and accumulate
                try:
                    gross = Decimal(str(item.get('gross_wt', 0)))
                except (InvalidOperation, TypeError):
                    gross = Decimal('0.00') 

                try:
                    qty = Decimal(str(item.get('roll_wt', 0)))
                except (InvalidOperation, TypeError):
                    qty = Decimal('0.00')

                total_gross += gross
                total_quantity += qty
                print('tot:', total_gross, total_quantity)

            material_request.total_wt = total_quantity
            material_request.gross_wt = total_gross
            material_request.save()   
                            

            # 🔹 **Update Parent PO Table (`po_table`)**
            # print('knt-deliver',True)
            # parent_po_table.objects.filter(id__in=po_ids).update(is_knitting_delivery=1)
            new_do_number = generate_outward_num_series()
            return JsonResponse({
                'status': 'success', 
                'message': 'Outward data saved successfully.',  
                "do_number": new_do_number  # e.g., "PO-12345"
            })
            # return JsonResponse('yes', safe=False)  # Indicate success

        except Exception as e:
            print(f"❌ Error: {e}")  # Log error for debugging
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'yarn_outward/yarn_outward_add.html')


 

# def grey_fab_outward_ajax_report(request):
#     company_id = request.session['company_id']
#     print('company_id:', company_id)



#     query = Q() 

#     # Date range filter
#     lot_no = request.POST.get('lot_no', '')
#     party = request.POST.get('party', '')
#     k_prg = request.POST.get('k_prg', '')
#     dye_prg = request.POST.get('dye_prg', '')
#     start_date = request.POST.get('from_date', '')
#     end_date = request.POST.get('to_date', '')

#     if start_date and end_date:
#         try:
#             start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
#             end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

#             # Match if either created_on or updated_on falls in range
#             date_filter = Q(delivery_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
#             query &= date_filter
#         except ValueError:
#             return JsonResponse({
#                 'data': [],
#                 'message': 'error',
#                 'error_message': 'Invalid date format. Use YYYY-MM-DD.'
#             })
    
#     if party:
#             query &= Q(party_id=party)


#     if dye_prg:
#             query &= Q(dyeing_program_id=dye_prg)

#     if k_prg:
#             query &= Q(knitting_program_id=dye_prg)

#     if lot_no:
#             query &= Q(lot_no=lot_no)

#     # Apply filters
#     queryset = parent_gf_delivery_table.objects.filter(status=1).filter(query)
#     data = list(queryset.order_by('-id').values())




#     def getInwardNumberById(inward_model, inward_id):
#         try:
#             entry = inward_model.objects.get(id=inward_id)
#             return entry.inward_number
#         except inward_model.DoesNotExist:
#             return '-'

#     child = child_gf_delivery_table.objects.filter(status=1,tm_id=data).filter(query)
#     wt = sum(child['roll_wt'])
#     formatted = [
#         {
#             'action': '<button type="button" onclick="grey_outward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
#                         <button type="button" onclick="grey_outward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
#                         <button type="button" onclick="grey_outward_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
#                         # <button type="button" onclick="outward_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['program_id']),
#             'id': index + 1, 
#             'delivery_date': item['delivery_date'].strftime('%d-%m-%Y') if item['delivery_date'] else '-',
#             'inward_no': getInwardNumberById(gf_inward_table, item['inward_id']) if item.get('inward_id') else '-',
#             'deliver_no': item['do_number'] if item['do_number'] else '-',
#             'total_quantity': item['total_wt'] if item['total_wt'] else '-',
#             'lot_no': item['lot_no'] if item['lot_no'] else '-',
#             'gross_wt': item['gross_wt'] if item['gross_wt'] else '-',
#             'party': getSupplier(party_table, item['party_id']),
#             # 'po_number': getPONumberByInwardID(yarn_inward_table, item['inward_id']),
#             'knit_prg': getKnittingDisplayNameById(knitting_table, item['knitting_program_id']),
#             'prg': getDyeingDisplayNameById(dyeing_program_table, item['dyeing_program_id']),
#             'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
#         }
#         for index, item in enumerate(data)
#     ]

#     return JsonResponse({'data': formatted})




from django.db.models import Sum

@csrf_exempt
def grey_fab_outward_ajax_report(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)

    query = Q()

    # Date range filter
    lot_no = request.POST.get('lot_no', '')
    party = request.POST.get('party', '')
    k_prg = request.POST.get('k_prg', '')
    dye_prg = request.POST.get('dye_prg', '')
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            date_filter = Q(delivery_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })

    if party:
        query &= Q(party_id=party)

    if dye_prg:
        query &= Q(dyeing_program_id=dye_prg)

    if k_prg:
        query &= Q(knitting_program_id=dye_prg)

    if lot_no:
        query &= Q(lot_no=lot_no)

    queryset = parent_gf_delivery_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())

    def getInwardNumberById(inward_model, inward_id):
        try:
            entry = inward_model.objects.get(id=inward_id)
            return entry.inward_number
        except inward_model.DoesNotExist:
            return '-'

    formatted = []
    for index, item in enumerate(data):
        # Sum roll_wt from child table for this tm_id
        child_wt = child_gf_delivery_table.objects.filter(status=1, tm_id=item['id']).aggregate(total_wt=Sum('roll_wt'))['total_wt'] or 0

        formatted.append({
            'action': '<button type="button" onclick="grey_outward_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="grey_outward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="grey_outward_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'], item['id'], item['id']),
            'id': index + 1,
            'delivery_date': item['delivery_date'].strftime('%d-%m-%Y') if item['delivery_date'] else '-',
            'inward_no': getInwardNumberById(gf_inward_table, item['inward_id']) if item.get('inward_id') else '-',
            'deliver_no': item['do_number'] if item['do_number'] else '-',
            'total_quantity': child_wt,
            'lot_no': item['lot_no'] if item['lot_no'] else '-',
            'gross_wt': item['gross_wt'] if item['gross_wt'] else '-',
            'party': getSupplier(party_table, item['party_id']),
            'knit_prg': getKnittingDisplayNameById(knitting_table, item['knitting_program_id']),
            'prg': getDyeingDisplayNameById(dyeing_program_table, item['dyeing_program_id']),
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        })

    return JsonResponse({'data': formatted})
 


@csrf_exempt
def grey_fab_outward_print(request): 
    import base64
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404, render
    from collections import defaultdict
    from decimal import Decimal
 
    outward_id = request.GET.get('k')
    if not outward_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    try:
        order_id = int(base64.b64decode(outward_id))
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    delivery_data = parent_gf_delivery_table.objects.filter(status=1, id=order_id).first()
    outward = parent_gf_delivery_table.objects.filter(id=order_id, status=1).values(
        'id', 'dyeing_program_id', 'do_number', 'delivery_date',
        'lot_no', 'party_id', 'total_wt', 'gross_wt'
    )

    party_name = get_object_or_404(party_table, id=delivery_data.party_id)
    gstin = party_name.gstin
    mobile = party_name.mobile

    # Initialize
    program_details = []
    delivery_details = []
    dias = set() 
    total_out_rolls = 0
    total_out_wt = 0

    delivery_entries_raw = sub_child_gf_delivery_detail_table.objects.filter(
        tm_id=order_id
    ).values('party_id', 'remarks')

    if delivery_entries_raw:
        party_ids = [entry['party_id'] for entry in delivery_entries_raw]
        parties = party_table.objects.filter(id__in=party_ids).values('id', 'name', 'gstin', 'mobile')
        party_map = {p['id']: p for p in parties}

        delivery_entries = [
            {
                'party_name': party_map.get(entry['party_id'], {}).get('name', 'Unknown'),
                'gstin': party_map.get(entry['party_id'], {}).get('gstin', 'Unknown'),
                'mobile': party_map.get(entry['party_id'], {}).get('mobile', 'Unknown'),
                'remarks': entry['remarks']
            } for entry in delivery_entries_raw
        ]
    else:
        delivery_entries = []

    for out in outward:
        total_values = get_object_or_404(dyeing_program_table, id=out['dyeing_program_id'])
        print('out-id:',out['id'])
        program = dyeing_program_table.objects.filter(
            id=out['dyeing_program_id'], status=1
        ).values('id', 'program_no', 'program_date').first()

        previous_outwards = parent_gf_delivery_table.objects.filter(
            dyeing_program_id=out['dyeing_program_id'], status=1, id__lt=out['id']
        ).values_list('total_wt', flat=True)

        pre_qty = sum(previous_outwards) if previous_outwards else '-'

        tx_yarn_entries = child_gf_delivery_table.objects.filter(
            tm_id=out['id'], status=1
        ).values(
            'fabric_id', 'gauge_id', 'tex_id', 'dia_id', 'color_id', 'gsm',
            'yarn_count_id', 'party_id', 'roll', 'roll_wt', 'gross_wt'
        )
        g_wt = 0
        for tx_yarn in tx_yarn_entries:
            total_out_rolls += tx_yarn['roll']
            total_out_wt += tx_yarn['roll_wt']

            party = get_object_or_404(party_table, id=tx_yarn['party_id'])
            yarn_count = get_object_or_404(count_table, id=tx_yarn['yarn_count_id'])
            gauge = get_object_or_404(gauge_table, id=tx_yarn['gauge_id'])
            tex = get_object_or_404(tex_table, id=tx_yarn['tex_id'])
            dia = get_object_or_404(dia_table, id=tx_yarn['dia_id'])
            color = get_object_or_404(color_table, id=tx_yarn['color_id']) 
            print('tx-color-data:',tx_yarn['color_id'])

            fabric = get_object_or_404(fabric_program_table, id=tx_yarn['fabric_id'])
            fabric_name = get_object_or_404(fabric_table, id=fabric.fabric_id).name

            dias.add(dia.name)
            g_wt += tx_yarn['roll_wt']

            # g_wt = sum(tx_yarn['gross_wt'])
            print('g-wt:',g_wt)
            delivery_details.append({
                'mill': party.name,
                'yarn': yarn_count.name,
                'fabric': fabric_name,
                'tex': tex.name,
                'gauge': gauge.name,
                'gsm': tx_yarn['gsm'],
                'dia': dia.name,
                'color': color.name,
                'lot_no': out['lot_no'],
                'do_number': out['do_number'],
                'do_date': out['delivery_date'],
                'roll': tx_yarn['roll'],
                'roll_wt': tx_yarn['roll_wt'],
                'gross_wt': tx_yarn['gross_wt'],
            })

    dias = sorted(dias)
    grouped_by_main_attrs = defaultdict(list)

    for item in delivery_details:
        key = (
            item['fabric'],
            item['yarn'],
            item['gauge'],
            item['tex'],
            item['gsm']
        )
        grouped_by_main_attrs[key].append(item)

    grouped_delivery_details = []
    for key, items in grouped_by_main_attrs.items():
        fabric, yarn, gauge, tex, gsm = key

        color_group = defaultdict(list)
        for item in items:
            color_group[item['color']].append(item)

        color_grouped_list = []
        total_rows = 0

        for color, color_items in color_group.items():
            dia_rows = []
            total_roll = 0
            total_weight = 0
            for i in color_items:
                dia_rows.append({
                    'dia': i['dia'],
                    'roll': i['roll'],
                    'roll_wt': i['roll_wt']
                })
                total_roll += i['roll']
                total_weight += i['roll_wt']

            color_grouped_list.append({
                'color': color,
                'dias': dia_rows,
                'total_roll': total_roll,
                'total_weight': total_weight,
                'rowspan': len(dia_rows)
            })

            total_rows += len(dia_rows)

        grouped_delivery_details.append({
            'fabric': fabric,
            'yarn': yarn,
            'gauge': gauge,
            'tex': tex,
            'gsm': gsm,
            'color_groups': color_grouped_list,
            'rowspan': total_rows
        })

    # ✅ Compute Column-Wise Totals from delivery_details
    dia_totals = {dia: {'roll': 0, 'roll_wt': Decimal('0')} for dia in dias}
    for item in delivery_details:
        dia_name = item.get('dia')
        if dia_name in dia_totals:
            dia_totals[dia_name]['roll'] += item.get('roll', 0)
            dia_totals[dia_name]['roll_wt'] += Decimal(item.get('roll_wt', 0))

    dia_totals_list = [dia_totals[dia] for dia in dias]

    grand_total_roll = sum(item['roll'] for item in delivery_details)
    grand_total_weight = sum(Decimal(item['roll_wt']) for item in delivery_details)

    total_columns = 2 + len(dias) * 2
    remarks = delivery_data.remarks if delivery_data else ''
    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'

    context = {
        'total_values': total_values,
        'gstin': gstin,
        'mobile': mobile,
        'program': program,
        'dias': dias,
        'grouped_delivery_details': grouped_delivery_details,
        'dia_totals_list': dia_totals_list,
        'grand_total_roll': grand_total_roll,
        'grand_total_weight': grand_total_weight,
        'image_url': image_url,
        'remarks': remarks,
        'delivery_entries': delivery_entries,
        'delivery_data': delivery_data,
        'party_name': party_name,
        'total_out_rolls': total_out_rolls,
        'total_out_wt': total_out_wt,
        'total_columns': total_columns,
        'company': company_table.objects.filter(status=1).first(),
    }

    return render(request, 'outward/outward_print.html', context)



def grey_fab_outward_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'outward/grey_fab_outward_details.html', {'error_message': 'ID is missing.'})

        # Ensure valid Base64 padding before decoding
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id + '=' * (-len(encoded_id) % 4)).decode()
            material_id = int(decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'outward/grey_fab_outward_details.html', {'error_message': 'Invalid ID format.'})

        # Fetch material instance
        material_instance = child_gf_delivery_table.objects.filter(tm_id=material_id).first()

        # If no material found and request is POST, create a new one
        if not material_instance and request.method == "POST":
            product_id = request.POST.get('product_id')
            bag = request.POST.get('bag')
            per_bag = request.POST.get('per_bag')
            quantity = request.POST.get('quantity')
            rate = request.POST.get('rate')
            amount = request.POST.get('amount')

            # Validate required fields before saving
            if product_id and quantity:
                material_instance = child_gf_delivery_table.objects.create(
                    tm_id=material_id,
                    bag=bag,
                    per_bag=per_bag,
                    # amount=amount, 
                    # rate=rate, 
                    quantity=quantity
                )
            else:
                return render(request, 'outward/grey_fab_outward_details.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = parent_gf_delivery_table.objects.filter(id=material_id).first()

        print('pt:',parent_stock_instance.lot_no)
        if not parent_stock_instance:
            return render(request, 'outward/grey_fab_outward_details.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name
        supplier_name = "-"
        if parent_stock_instance.party_id:
            supplier = party_table.objects.filter(id=parent_stock_instance.party_id, status=1).first()
            supplier_name = supplier.name if supplier else "-"
        count = count_table.objects.filter(status=1) 
        fabric = fabric_program_table.objects.filter(status=1) 
        gauge = gauge_table.objects.filter(status=1) 
        dia = dia_table.objects.filter(status=1) 
        color = color_table.objects.filter(status=1) 
        # Fetch related data



        # program = grey_fab_dyeing_program_balance.objects.filter(
        #     balance_wt__gt=0
        # ).values('program_id', 'fabric_id','dia_id','color_id')

        # lot = grey_fabric_available_inward_table.objects.filter(
        #     # available_wt__gt=0
        # ).values('lot_no').distinct().order_by('lot_no')

        # print('lot:',lot)

        
        # program_ids = program.values_list('program_id', flat=True)
 
        prg_list = dyeing_program_table.objects.filter( status=1)
        # program = grey_fab_dyeing_program_balance.objects.filter(
        #     balance_wt__gt=0
        # ).values('program_id', 'fabric_id','dia_id','color_id')

        # lot = grey_fabric_available_inward_table.objects.filter(
        #     available_wt__gt=0
        # ).values('lot_no').distinct().order_by('lot_no')

        # print('lot:',lot)

        
        # program_ids = program.values_list('program_id', flat=True) 

        # prg_list = dyeing_program_table.objects.filter(id__in=program_ids, status=1)
        dyeing = dyeing_program_table.objects.filter(status=1)

        program = grey_fab_dyeing_program_balance.objects.filter(
            # balance_wt__gt=0
        ).values('program_id', 'fabric_id','dia_id','color_id')

        lot = grey_fabric_available_inward_table.objects.filter(
            # available_wt__gt=0
        ).values('lot_no').distinct().order_by('lot_no')

        print('lot:',lot) 

        compact_party = party_table.objects.filter(status=1,is_compacting=1)
        context = { 
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'party': party_table.objects.filter(is_process=1 ),
            'program': knitting_table.objects.filter(status=1),
            'yarn_count':count,
            'fabric':fabric,
            'gauge':gauge,
            'color':color,
            'dia':dia,
            'inward_lists':gf_inward_table.objects.filter(status=1),
            'prg_list':prg_list,
            'lot':lot,
            'dyeing':dyeing,
            'compact_party':compact_party,
        }

        return render(request, 'outward/grey_fab_outward_details.html', context)

    except Exception as e:
        # logger.error(f"Error in yarn_deliver_edit: {e}") 
        return render(request, 'outward/grey_fab_outward_details.html', {'error_message': f'An unexpected error occurred: {str(e)}'})

 



def grey_fab_outward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        try:
            # First, get the delivery record
            delivery = parent_gf_delivery_table.objects.filter(id=data_id, is_active=1).first()
            if not delivery:
                return JsonResponse({'message': 'no such delivery record'})

            ## Now check if the corresponding inward record exists and is active
            # inward_exists = yarn_inward_table.objects.filter(id=delivery.inward_id, status=1).exists()
            # if not inward_exists:
                # return JsonResponse({'message': 'inward not active'})

            # Proceed with soft delete
            parent_gf_delivery_table.objects.filter(id=data_id).update(status=0, is_active=0,updated_on=timezone.now())
            child_gf_delivery_table.objects.filter(tm_id=data_id).update(status=0, is_active=0,updated_on=timezone.now())

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'Invalid request method'})






def outward_detail_lists(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('po-out-tmid:',master_id)
        if master_id:
            try:
                child_data = child_gf_delivery_table.objects.filter(tm_id=master_id, status=1)

                if not child_data.exists():
                    return JsonResponse({'success': True, 'data': []})  # still return success with empty data

                formatted_data = []
                for index, item in enumerate(child_data, start=1):
                    formatted_data.append({
                        'action': f'''
                            <button type="button" onclick="inward_detail_edit('{item.id}')" class="btn btn-primary btn-xs">
                                <i class="feather icon-edit"></i>
                            </button>
                            <button type="button" onclick="inward_detail_delete('{item.id}')" class="btn btn-danger btn-xs">
                                <i class="feather icon-trash-2"></i>
                            </button>
                        ''',
                        'fabric': getItemFabNameById(fabric_program_table, item.fabric_id),
                        'yarn_count': getItemNameById(count_table, item.yarn_count_id),
                        'tex': getItemNameById(tex_table, item.tex_id),
                        'gauge': getItemNameById(gauge_table, item.gauge_id),
                        'gsm': item.gsm,
                        'dia': getItemNameById(dia_table, item.dia_id),
                        'roll': item.roll or 0,
                        'total_wt': item.roll_wt or 0,
                        'gross_wt': item.gross_wt or 0,
                        'received_roll': 0,
                        'received_roll_wt': 0,
                        'fabric_id': item.fabric_id or '-',
                        'yarn_count_id': item.yarn_count_id or '-',
                        'tex_id': item.tex_id or '-',
                        'gauge_id': item.gauge_id or '-',
                        'dia_id': item.dia_id or '-',
                    })

                return JsonResponse({'success': True, 'data': formatted_data})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request, missing ID parameter'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ````````````````````````````````````````````````````````````````````````````````





# def fetch_dyeing_program_gf_outward(master_id,tm_id, color_ids=None):
#     with connection.cursor() as cursor:
#         sql = """
#             SELECT 
#                 dp.tm_id,
#                 dp.dia_id,
#                 dp.color_id,
#                 dp.fabric_id, 
#                 dp.yarn_count_id,
#                 dp.tex_id,
#                 dp.gauge_id,
#                 dp.gsm,
#                 COALESCE(SUM(dp.roll), 0) AS prg_roll,
#                 COALESCE(SUM(dp.roll_wt), 0) AS program_total_weight,
#                 COALESCE(SUM(go.roll), 0) AS outward_roll,
#                 COALESCE(SUM(go.roll_wt), 0) AS outward_total_weight
#             FROM tx_dyeing_program dp
#             LEFT JOIN tm_dyeing_program dm ON dp.tm_id = dm.id
#             LEFT JOIN tx_gf_delivery go 
#                 ON dp.dia_id = go.dia_id 
#                 AND dp.color_id = go.color_id 
#                 AND dp.fabric_id = go.fabric_id 
#                 AND go.status = 1
#             WHERE go.dyeing_program_id = %s AND go.tm_id=%s AND dp.status = 1
#         """
#         params = [master_id,tm_id]

#         if color_ids:
#             placeholders = ','.join(['%s'] * len(color_ids))
#             sql += f" AND dp.color_id IN ({placeholders})"
#             params.extend(color_ids)

#         sql += """
#             GROUP BY dp.tm_id, dp.dia_id, dp.color_id, dp.fabric_id,
#                      dp.yarn_count_id, dp.tex_id, dp.gauge_id, dp.gsm
#         """

#         cursor.execute(sql, params)
#         columns = [col[0] for col in cursor.description]
#         return [dict(zip(columns, row)) for row in cursor.fetchall()]
 


def fetch_dyeing_program_gf_outward(master_id, tm_id, color_ids=None): 
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                dp.tm_id,
                dp.dia_id,
                dp.color_id,
                dp.fabric_id, 
                dp.yarn_count_id,
                dp.tex_id,
                dp.gauge_id,
                dp.gsm,
                COALESCE(SUM(dp.roll), 0) AS prg_roll,
                COALESCE(SUM(dp.roll_wt), 0) AS program_total_weight,
                COALESCE(SUM(go.roll), 0) AS outward_roll,
                COALESCE(SUM(go.roll_wt), 0) AS outward_total_weight
            FROM tx_dyeing_program dp
            LEFT JOIN tm_dyeing_program dm ON dp.tm_id = dm.id
            LEFT JOIN tx_gf_delivery go 
                ON dp.dia_id = go.dia_id 
                AND dp.color_id = go.color_id 
                AND dp.fabric_id = go.fabric_id 
                AND go.status = 1
                AND go.tm_id = %s
        """
        params = [tm_id, master_id]  # <-- reorder for clarity

        sql += " WHERE dp.tm_id = %s AND dp.status = 1"

        if color_ids:
            placeholders = ','.join(['%s'] * len(color_ids))
            sql += f" AND dp.color_id IN ({placeholders})"
            params.extend(color_ids)

        sql += """
            GROUP BY dp.tm_id, dp.dia_id, dp.color_id, dp.fabric_id,
                     dp.yarn_count_id, dp.tex_id, dp.gauge_id, dp.gsm
        """

        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from collections import defaultdict
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def dyeing_program_list_update_gf(request): 
    if request.method != 'POST':
        return JsonResponse({'message': 'error', 'error': 'Invalid request method'})

    master_id = request.POST.get('prg_id')
    tm_id = request.POST.get('tm_id')
    # color_ids = request.POST.getlist('color_id[]')  # From AJAX array


    posted_color_ids = request.POST.getlist('color_id[]')
    posted_color_ids = list(map(int, posted_color_ids)) if posted_color_ids else []

    # Get existing color_ids from tx_gf_delivery table for this tm_id
    existing_color_ids = list(
        child_gf_delivery_table.objects.filter(tm_id=tm_id, status=1)
        .values_list('color_id', flat=True)
    )

    # Merge and deduplicate
    color_ids = list(set(posted_color_ids + existing_color_ids)) if (posted_color_ids or existing_color_ids) else None



    if not master_id:
        return JsonResponse({'message': 'error', 'error': 'Missing prg_id'})

    try:
        color_ids = list(map(int, color_ids)) if color_ids else None

        # 🔍 Query aggregation data
        aggregates = fetch_dyeing_program_gf_outward(master_id, tm_id, color_ids)

        grouped_data = defaultdict(lambda: {
            'dias': {},
            'outward': {},
            'fabric_id': None,
            'color_id': None,
            'tex_id': None,
            'gauge_id': None, 
            'yarn_count_id': None,
            'gsm': None,
            'fabric': '',
            'color': '',
        })
        print('g-data:',grouped_data)

        dia_set = set()

        for row in aggregates:
            dia_id = row['dia_id']
            dia_name = getItemNameById(dia_table, dia_id)
            color_id = row['color_id']
            fabric_id = row['fabric_id']
            tex_id = row['tex_id']
            gauge_id = row['gauge_id']
            yarn_count_id = row['yarn_count_id']
            gsm = row['gsm']

            key = (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, gsm)
            dia_set.add((dia_id, dia_name))

            grouped_data[key].update({
                'fabric_id': fabric_id,
                'color_id': color_id,
                'gsm': gsm,
                'tex_id': tex_id,
                'gauge_id': gauge_id,
                'yarn_count_id': yarn_count_id,
                'fabric': getItemFabNameById(fabric_program_table, fabric_id),
                'color': getItemNameById(color_table, color_id),
            })

            # Ensure safe float conversion
            grouped_data[key]['dias'][dia_name] = {
                'dia_id': dia_id,
                'roll': float(row.get('prg_roll') or 0),
                'roll_wt': float(row.get('program_total_weight') or 0),
            }

            grouped_data[key]['outward'][dia_name] = {
                'roll': float(row.get('outward_roll') or 0),
                'roll_wt': float(row.get('outward_total_weight') or 0),
            }

        # ➕ Fill missing dias with zeros
        for key, data in grouped_data.items():
            for dia_id, dia_name in dia_set:
                data['dias'].setdefault(dia_name, {'dia_id': dia_id, 'roll': 0, 'roll_wt': 0})
                data['outward'].setdefault(dia_name, {'roll': 0, 'roll_wt': 0})

        # 🧾 Prepare final rows
        rows = []
        for (fabric_id, color_id, yarn_count_id, tex_id, gauge_id, gsm), data in grouped_data.items():
            row = {
                'fabric': data['fabric'],
                'fabric_id': fabric_id,
                'color': data['color'],
                'color_id': color_id,
                'outward': data['outward'],
                'gauge_id': gauge_id,
                'tex_id': tex_id,
                'yarn_count_id': yarn_count_id,
                'gsm': gsm,
            }
            for dia_id, dia_name in dia_set:
                row[dia_name] = data['dias'][dia_name]
            rows.append(row)

        # 🧺 Fetch lot numbers for these fabrics
        fabric_ids = list(set(key[0] for key in grouped_data.keys()))
        lots = list(
            grey_fabric_available_inward_table.objects.filter(
                available_wt__gt=0,
                fabric_id__in=fabric_ids
            ).values_list('lot_no', flat=True).distinct().order_by('lot_no')
        )

        return JsonResponse({
            'dias': sorted(dia_set, key=lambda x: x[1]),  # sort by dia_name
            'rows': rows,
            'lots': lots,
        })

    except Exception as e:
        return JsonResponse({'message': 'error', 'error': str(e)})





from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.http import JsonResponse
import json

# def update_grey_outward(request):
#     if request.method == 'POST':
#         user_id = request.session['user_id']
#         company_id = request.session['company_id']

#         try:
#             do_date = request.POST.get('outward_date')
#             lot_no = request.POST.get('lot_no')
#             tm_id = request.POST.get('tm_id')  # ✅ Corrected
#             program_id = request.POST.get('program_id')
#             deliver_id = request.POST.get('party_id')
#             fabric_id = request.POST.get('fabric_id')
#             # color_id = request.POST.get('color_id')
#             remarks = request.POST.get('remarks')
#             dye_prg_id = request.POST.get('prg_id')
#             chemical_data = json.loads(request.POST.get('chemical_data', '[]'))
#             color_ids = request.POST.getlist('color_id[]')  # ⬅ expects multiple <input name="color_id[]">
#             color_id_str = ','.join(color_ids)  # ⬅ e.g., "2,3"
#             # ➤ Fetch or create new parent
#             if tm_id:
#                 parent = get_object_or_404(parent_gf_delivery_table, id=tm_id)
#                 new_do_number = parent.do_number  # Reuse existing DO number 
#                 knit_id = parent.knitting_program_id  # Reuse existing DO number 
#                 # Clear existing child rows
#                 # child_gf_delivery_table.objects.filter(tm_id=tm_id).delete()
#                 child_gf_delivery_table.objects.filter(tm_id=tm_id).update(status=0,is_active=0)
#             else:
#                 new_do_number = generate_outward_num_series()
#                 parent = parent_gf_delivery_table(
#                     do_number=new_do_number,
#                     company_id=company_id,
#                     cfyear=2025,
#                     created_by=user_id
#                 ) 

#             # Update or set parent fields
#             parent.delivery_date = do_date
#             parent.party_id = deliver_id
#             # parent.knitting_program_id = program_id
#             parent.dyeing_program_id = dye_prg_id
#             parent.inward_id = 0
#             parent.lot_no = lot_no
#             parent.fabric_id = fabric_id
#             parent.color_id = color_id_str
#             parent.total_wt = 0
#             parent.gross_wt = 0
#             parent.remarks = remarks
#             parent.save()

#             total_gross = Decimal('0.00')
#             total_quantity = Decimal('0.00')

#             for outward_group in chemical_data:
#                 items = outward_group.get('items', [])

#                 for item in items:
#                     roll = item.get('roll') or 0 
#                     roll_wt = item.get('roll_wt') or 0

#                     child_gf_delivery_table.objects.create(
#                         company_id=company_id,
#                         cfyear=2025,
#                         tm_id=tm_id,
#                         knitting_program_id=knit_id,
#                         dyeing_program_id=dye_prg_id,
#                         lot_no=lot_no,
#                         party_id=deliver_id,
#                         yarn_count_id=item.get('yarn_count_id'),
#                         fabric_id=item.get('fabric_id'),
#                         gauge_id=item.get('gauge_id'),
#                         tex_id=item.get('tex_id'),
#                         gsm=item.get('gsm'),
#                         dia_id=item.get('dia_id'),
#                         color_id=item.get('color_id'),
#                         roll=roll,
#                         roll_wt=roll_wt,
#                         gross_wt=roll_wt,
#                         inward_id=0,
#                         created_by=user_id
#                     )
 
#                     total_gross += Decimal(str(roll_wt))
#                     total_quantity += Decimal(str(roll_wt))

#             # Update totals after all inserts
#             parent.total_wt = total_quantity
#             parent.gross_wt = total_gross
#             parent.save()

#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Outward data saved successfully.',
#                 'do_number': new_do_number
#             })

#         except Exception as e:
#             print(f"❌ Error: {e}")
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return render(request, 'outward/grey_fab_outward_add.html')
    

@csrf_exempt
def update_grey_outward(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']

        try:
            do_date = request.POST.get('outward_date')
            lot_no = request.POST.get('lot_no')
            tm_id = request.POST.get('tm_id')
            program_id = request.POST.get('program_id')
            deliver_id = request.POST.get('party_id')
            fabric_id = request.POST.get('fabric_id')
            remarks = request.POST.get('remarks')
            dye_prg_id = request.POST.get('prg_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            # ✅ Handle multiple color_id[] values
            color_ids = request.POST.getlist('color_id')
            color_id_str = ','.join(color_ids)

            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')

            # Check if updating existing record
            if tm_id:
                parent = get_object_or_404(parent_gf_delivery_table, id=tm_id)
                new_do_number = parent.do_number
                knit_id = parent.knitting_program_id

                # Soft delete existing child records
                child_gf_delivery_table.objects.filter(tm_id=tm_id).update(status=0, is_active=0)
            else:
                new_do_number = generate_outward_num_series()
                parent = parent_gf_delivery_table(
                    do_number=new_do_number,
                    company_id=company_id,
                    cfyear=2025,
                    created_by=user_id
                )
                parent.save()  # Save first to get ID
                tm_id = parent.id
                knit_id = 0  # In case no knit_id available in new creation

            # Update or overwrite parent fields
            parent.delivery_date = do_date
            parent.party_id = deliver_id
            parent.dyeing_program_id = dye_prg_id
            parent.inward_id = 0
            parent.lot_no = lot_no
            parent.fabric_id = fabric_id
            parent.color_id = color_id_str  # ✅ Save as comma-separated string
            parent.total_wt = 0
            parent.gross_wt = 0
            parent.remarks = remarks
            parent.save()

            for outward_group in chemical_data:
                items = outward_group.get('items', [])

                for item in items:
                    roll = item.get('roll') or 0
                    roll_wt = item.get('roll_wt') or 0

                    child_gf_delivery_table.objects.create(
                        company_id=company_id,
                        cfyear=2025,
                        tm_id=tm_id,
                        knitting_program_id=knit_id,
                        dyeing_program_id=dye_prg_id,
                        lot_no=lot_no,
                        party_id=deliver_id,
                        yarn_count_id=item.get('yarn_count_id'), 
                        fabric_id=item.get('fabric_id'),
                        gauge_id=item.get('gauge_id'),
                        tex_id=item.get('tex_id'),
                        gsm=item.get('gsm'),
                        dia_id=item.get('dia_id'),
                        color_id=item.get('color_id'),
                        roll=roll,
                        roll_wt=roll_wt,
                        gross_wt=roll_wt,
                        inward_id=0,
                        created_by=user_id,
                        updated_on = datetime.now()
                    )

                    total_gross += Decimal(str(roll_wt))
                    total_quantity += Decimal(str(roll_wt))

            # Finalize parent totals
            # parent.total_wt = total_quantity
            # parent.gross_wt = total_gross
            # parent.save()

            # Aggregate total rolls and roll weight after insertion
            # totals = child_gf_delivery_table.objects.filter(tm_id=tm_id).aggregate(
            #     total_rolls=Sum('roll'), total_wt=Sum('roll_wt')
            # )

            # Update the parent dyeing_program_table
            parent_gf_delivery_table.objects.filter(id=tm_id).update( 
                total_wt=total_gross or 0,
                total_gross=total_gross or 0
            )



            return JsonResponse({
                'status': 'success',
                'message': 'Outward data saved successfully.',
                'do_number': new_do_number
            })

        except Exception as e:
            print(f"❌ Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'outward/grey_fab_outward_add.html')




def gf_delivery_details_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id)
 
        if master_id:
            try:
                # Fetch child PO data
                child_data = sub_child_gf_delivery_detail_table.objects.filter(tm_id=master_id, status=1, is_active=1)
           
                # Format child PO data for response
                data = list(child_data.values())
                formatted_data = []
                index = 0
                for item in data: 
                    index += 1  
                    formatted_data.append({
                        'action': '<button type="button" onclick="outward_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                    <button type="button" onclick="outward_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                        'id': index,
                        'party': getItemNameById(party_table, item['party_id']),

                        'remarks': item['remarks'] if item['remarks'] else '-',
                        'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                    })
                formatted_data.reverse() 

                # ✅ Add return statement to return JSON response
                return JsonResponse({'status': 'Success', 'data': formatted_data})

            except Exception as e:
                return JsonResponse({'status': 'Failed', 'error': str(e)}, status=500)

        else:
            return JsonResponse({'status': 'Failed', 'error': 'Invalid request, missing ID parameter'}, status=400)

    return JsonResponse({'status': 'Failed', 'error': 'Invalid request, POST method expected'}, status=400)




def gf_delivery_details_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_child_gf_delivery_detail_table.objects.filter(id=request.POST.get('id'))
    print('po-data:',data)
    return JsonResponse(data.values()[0])





@csrf_exempt
def gfdelivery_update(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        tm_id = request.POST.get('tm_id')
        edit_id = request.POST.get('edit_id')
        party_id = request.POST.get('delivery_party_id')
        remarks = request.POST.get('remarks')

        if not tm_id or not party_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            if edit_id and edit_id != "0":
                # Try updating existing
                parent_item = sub_child_gf_delivery_detail_table.objects.get(tm_id=tm_id, id=edit_id)
                parent_item.party_id = party_id
                parent_item.remarks = remarks
                parent_item.save()
                return JsonResponse({'success': True, 'message': 'Delivery updated successfully'})
            else:
                # Create new if edit_id is empty or zero
                sub_child_gf_delivery_detail_table.objects.create(
                    tm_id=tm_id,
                    party_id=party_id,
                    remarks=remarks,
                    created_on=datetime.now(),
                    created_by=request.session.get('user_id')  # optional if tracking creator
                )
                return JsonResponse({'success': True, 'message': 'Delivery created successfully'})

        except sub_child_gf_delivery_detail_table.DoesNotExist:
            # Create new if not found (extra fallback)
            sub_child_gf_delivery_detail_table.objects.create(
                tm_id=tm_id,
                party_id=party_id,
                remarks=remarks,
                created_on=datetime.now(),
                created_by=request.session.get('user_id')
            )


            
            return JsonResponse({'success': True, 'message': 'Delivery created (not found on update)'})

        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})



# def gfdelivery_update(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         tm_id = request.POST.get('tm_id')
#         edit_id = request.POST.get('edit_id')
#         party_id = request.POST.get('delivery_party_id')
       
#         remarks = request.POST.get('remarks')

#         if not tm_id or not party_id:
#             return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

#         try:
#             parent_item = sub_child_gf_delivery_detail_table.objects.get(tm_id=tm_id,id=edit_id)
#             parent_item.party_id = party_id
#             parent_item.remarks = remarks
            
 
#             parent_item.save()

#             return JsonResponse({'success': True, 'message': 'PO item updated successfully'})

#         except sub_child_gf_delivery_detail_table.DoesNotExist:
#             return JsonResponse({'success': False, 'error_message': 'Parent PO not found'})
#         except IntegrityError as e:
#             return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error_message': str(e)})

#     return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
