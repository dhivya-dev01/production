

import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from numpy import number
# from software_app.models import count_table, knitting_table, parent_po_table, party_table, product_table, sub_yarn_deliver_table, sub_yarn_inward_table, yarn_delivery_table, yarn_inward_table
from common.utils import *
from software_app.models import *
from employee.models import *
from yarn.models import *
from program_app.models import *
from company.models import *

from software_app.views import getItemNameById, getPONameById, getSupplier, is_ajax, check_user_access
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from decimal import Decimal
from django.db.models import F
from decimal import Decimal, InvalidOperation

import base64
import logging

from django.db.models import Q

logger = logging.getLogger(__name__)  # Use Django logging


from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F
from collections import defaultdict

from django.db.models import Max
from django.db.models import Max, F, Q
import base64
# ````````````````````````````````````````check user roles ````````````````````````````````````````

# ``````````````````````````````````````````````````````````````````````````

def yarn_outward(request):
    if 'user_id' in request.session:  
        user_id = request.session['user_id'] 
        supplier = party_table.objects.filter(is_supplier=1)
        # party = party_table.objects.filter(status=1)
        party = party_table.objects.filter(status=1,is_knitting=1)
        product = product_table.objects.filter(status=1)
        knitting = knitting_table.objects.filter(status=1,is_yarn=1)
        return render(request,'yarn_outward/yarn_outward_list.html',{'supplier':supplier,'party':party,'product':product,'knitting':knitting})
    else:
        return HttpResponseRedirect("/signin")




from django.db.models import Max
import re

def generate_next_do_number():
    last_purchase = yarn_delivery_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.do_number:
        match = re.search(r'DO-(\d+)', last_purchase.do_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"DO-{next_num:03d}"




def yarn_outward_add(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']

        process = process_table.objects.filter(status=1, stage__in=['bleaching', 'dyeing','knitting','inhouse'])
        deliver = party_table.objects.filter(is_knitting=1,)

        last_purchase = yarn_delivery_table.objects.filter(status=1).order_by('-id').first()
        # delivery_number = last_purchase.do_number + 1 if last_purchase else 1

        delivery_number = generate_next_do_number()



        party = party_table.objects.filter(status=1, is_knitting=1) 
        bag = bag_table.objects.filter(status=1) 
        count = count_table.objects.filter(status=1)
    

        program = yarn_program_balance_table.objects.filter(
            balance_quantity__gt=0
        ).values('program_id', 'yarn_count_id')

        
        program_ids = program.values_list('program_id', flat=True)

        prg_list = knitting_table.objects.filter(id__in=program_ids,is_yarn=1, status=1)


 


        return render(request, 'yarn_outward/yarn_outward_add.html', {
            # 'knitting': knitting, 
            'process': process, 
            'party': party,
            'deliver': deliver,
            'delivery_number': delivery_number,
            # 'inward_list': inward_list,
            'bag': bag,
            'count': count, 
            'program': prg_list
        })
    else:
        return HttpResponseRedirect("/signin")


@csrf_exempt
def get_lot_no(request):
    if request.method == "POST":
        party_id = request.POST.get("party_id")
        prg_id = request.POST.get("prg_id") 

        # Get count_id(s) for the selected program
        program_count_ids = list(
            sub_knitting_table.objects.filter(
                tm_id=prg_id,
                status=1
            ).values_list('count_id', flat=True)
        )

        unique_count_ids = set(program_count_ids)
        if len(unique_count_ids) != 1:
            return JsonResponse({'status': 'error', 'message': 'Program has multiple or no count_ids', 'count_ids': program_count_ids})
        
        only_count_id = program_count_ids[0]

        # With-party query
        with_party_qs = yarn_out_balance_table.objects.filter(
            party_id=party_id,
            yarn_count_id=only_count_id,
            available_quantity__gt=0,
            remaining_quantity__gt=0,
        ).values('inward_id', 'yarn_count_id', 'po_id', 'remaining_bags', 'remaining_quantity', 'bag_wt')

        # Without-party query
        without_party_qs = yarn_out_balance_table.objects.filter(
            yarn_count_id=only_count_id,
            available_quantity__gt=0,
            remaining_quantity__gt=0,
        ).values('inward_id', 'yarn_count_id', 'po_id', 'remaining_bags', 'remaining_quantity', 'bag_wt')

        # Convert to lists
        with_party_list = list(with_party_qs)
        without_party_list = list(without_party_qs)

        # Merge without duplicating inward_id already included in with-party list
        with_party_ids = {row['inward_id'] for row in with_party_list}
        merged_list = with_party_list + [row for row in without_party_list if row['inward_id'] not in with_party_ids]

        # Fetch inward numbers
        inward_ids = [row['inward_id'] for row in merged_list]
        inward_qs = yarn_inward_table.objects.filter(
            id__in=inward_ids,
            status=1
        ).values('id', 'inward_number', 'po_id')
        inward_map = {row['id']: row['inward_number'] for row in inward_qs}

        # Merge inward_number into results
        for row in merged_list:
            row['inward_number'] = inward_map.get(row['inward_id'], '')

        return JsonResponse({
            'inward_list': merged_list,
            'count_id': program_count_ids
        })

    return JsonResponse({'status': 'Failed', 'message': 'Invalid request method'})



@csrf_exempt
def get_lot_no_onlywithparty(request):
    if request.method == "POST":
        party_id = request.POST.get("party_id")
        prg_id = request.POST.get("prg_id") 

        # Get count_id(s) for the selected program
        program_count_ids = list(
            sub_knitting_table.objects.filter(
                tm_id=prg_id,
                status=1
            ).values_list('count_id', flat=True)
        )
        print('Program count_id(s):', program_count_ids)

        # Check if all count_ids are the same
        unique_count_ids = set(program_count_ids)  
        if len(unique_count_ids) == 1:
            only_count_id = program_count_ids[0]
            print('Only one unique count_id:', only_count_id)
        else:
            print('Multiple or no unique count_ids:', program_count_ids)

        # Get balance rows from yarn_out_balance_table with-party
        balance_qs = yarn_out_balance_table.objects.filter(   
            party_id=party_id,
            yarn_count_id = only_count_id,
            available_quantity__gt=0,
            remaining_quantity__gt=0,
        ).values('inward_id', 'yarn_count_id', 'po_id','remaining_bags','remaining_quantity','bag_wt')

        # Get balance rows from yarn_out_balance_table with-party
        party_balance_qs = yarn_out_balance_table.objects.filter(   
            yarn_count_id = only_count_id,
            available_quantity__gt=0,
            remaining_quantity__gt=0,
        ).values('inward_id', 'yarn_count_id', 'po_id','remaining_bags','remaining_quantity','bag_wt')

        balance_list = list(balance_qs)
        print('Filtered yarn_out_balance:', balance_list)

        party_balance_list = list(party_balance_qs)
        print('party Filtered yarn_out_balance:', party_balance_list)

        # Extract inward_ids 
        inward_ids = [row['inward_id'] for row in balance_list]

        # Fetch inward_number from yarn_inward_table
        inward_qs = yarn_inward_table.objects.filter(
            id__in=inward_ids,
            status=1
        ).values('id', 'inward_number','po_id')
        inward_map = {row['id']: row['inward_number'] for row in inward_qs}
        print('inwds:',inward_map)
        # Merge inward_number into each balance row
        for row in balance_list:
            row['inward_number'] = inward_map.get(row['inward_id'], '')

        return JsonResponse({
            'inward_list': balance_list,
            'count_id': program_count_ids
        })

    return JsonResponse({'status': 'Failed', 'message': 'Invalid request method'})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from collections import defaultdict


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from collections import defaultdict


@csrf_exempt
def get_inward_details(request): 
    if request.method == 'POST':
        try:
            raw_inward_ids = request.POST.get('inward_id', '[]')
            inward_ids = json.loads(raw_inward_ids)
            inward_ids = [int(i) for i in inward_ids if str(i).isdigit()]
            if not inward_ids:
                return JsonResponse({'error': 'No valid inward_ids provided'}, status=400)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid inward_ids format: {str(e)}'}, status=400)

        party_id = request.POST.get('party_id')
        prg_id = request.POST.get('prg_id')
        po_id = request.POST.get('po_id')

        result = []
        po_ids_set = set()
        knitting_ids_set = set()

        # Get count_id for the selected program
        program_count_ids = list(
            sub_knitting_table.objects.filter(
                tm_id=prg_id,
                status=1
            ).values_list('count_id', flat=True)
        )
        unique_count_ids = set(program_count_ids)
        if len(unique_count_ids) != 1:
            return JsonResponse({'error': 'Multiple or no unique count_ids found'}, status=400)

        count = list(unique_count_ids)[0]

        # Fetch program quantity
        program_balance_map = {}
        prog_balance_qs = yarn_program_balance_table.objects.filter(
            program_id=prg_id,
            yarn_count_id=count
        ).values('yarn_count_id', 'program_quantity')
        for row in prog_balance_qs:
            program_balance_map[row['yarn_count_id']] = row['program_quantity']

        # Step 1: Get balance rows WITH party_id
        with_party_qs = yarn_out_balance_table.objects.filter(  
            party_id=party_id, 
            yarn_count_id=count,
            inward_id__in=inward_ids,
            available_quantity__gt=0,
            remaining_quantity__gt=0
        ).values(
            'inward_id', 'yarn_count_id', 'po_id',
            'remaining_bags', 'remaining_quantity', 'bag_wt', 'available_bags','available_quantity'
        )
        with_party_list = list(with_party_qs)
        with_party_ids = {row['inward_id'] for row in with_party_list}

        # Step 2: Get balance rows WITHOUT party_id but excluding the above
        without_party_qs = yarn_out_balance_table.objects.filter(
            yarn_count_id=count,
            inward_id__in=[i for i in inward_ids if i not in with_party_ids],
            available_quantity__gt=0,
            remaining_quantity__gt=0
        ).values(
            'inward_id', 'yarn_count_id', 'po_id',
            'remaining_bags', 'remaining_quantity', 'bag_wt','available_bags', 'available_quantity'
        )
        without_party_list = list(without_party_qs)

        # Step 3: Merge both lists
        balance_list = with_party_list + without_party_list

        # Get count names
        yarn_count_ids = [row['yarn_count_id'] for row in balance_list]
        count_names = count_table.objects.filter(id__in=yarn_count_ids).values('id', 'name')
        count_name_map = {item['id']: item['name'] for item in count_names}

        # Step 4: Build the result list
        for row in balance_list:
            yarn_id = row['yarn_count_id']
            available_qty = row['available_quantity']
            remaining_qty = row['remaining_quantity']
            program_qty = program_balance_map.get(yarn_id, Decimal('0'))

            selected_qty = min(program_qty, available_qty, remaining_qty)

            result.append({
                'tm_id': row['inward_id'],
                'bag': row['available_bags'],#row['remaining_bags'],
                'per_bag': row['bag_wt'],
                'yarn_count_id': yarn_id,
                'yarn_count': count_name_map.get(yarn_id, ''),
                'quantity': float(selected_qty),
                'available_quantity': float(available_qty),
                'gross_wt': float(selected_qty),
                'po_id': row['po_id'],
                'inward_id': row['inward_id']
            })
            po_ids_set.add(row['po_id'])

        # Optional: Fetch PO deliveries
        po_deliveries = yarn_po_delivery_table.objects.filter(
            tm_po_id__in=po_ids_set
        )
        knitting_ids_set.update(
            po_deliveries.exclude(party_id__isnull=True)
                         .values_list('party_id', flat=True)
                         .distinct()
        )

        return JsonResponse({
            'data': result,
            'deliver_bag': 0,
            'deliver_quantity': 0,
            'knitting_ids': list(knitting_ids_set)
        })

    return JsonResponse({'data': [], 'deliver_bag': 0, 'deliver_quantity': 0, 'knitting_ids': []}, status=400)



@csrf_exempt
def get_inward_details_only_withparty(request): 
    if request.method == 'POST':
        try:
            raw_inward_ids = request.POST.get('inward_id', '[]')
            inward_ids = json.loads(raw_inward_ids)
            inward_ids = [int(i) for i in inward_ids if str(i).isdigit()]
            if not inward_ids:
                return JsonResponse({'error': 'No valid inward_ids provided'}, status=400)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid inward_ids format: {str(e)}'}, status=400)

        party_id = request.POST.get('party_id')
        prg_id = request.POST.get('prg_id')
        po_id = request.POST.get('po_id')

        result = []
        po_ids_set = set()
        knitting_ids_set = set()

        # Get count_id for the selected program
        program_count_ids = list(
            sub_knitting_table.objects.filter(
                tm_id=prg_id,
                status=1
            ).values_list('count_id', flat=True)
        )
        unique_count_ids = set(program_count_ids)
        if len(unique_count_ids) != 1:
            return JsonResponse({'error': 'Multiple or no unique count_ids found'}, status=400)

        count = list(unique_count_ids)[0]

        # Fetch program quantity
        program_balance_map = {}
        prog_balance_qs = yarn_program_balance_table.objects.filter(
            program_id=prg_id,
            yarn_count_id=count
        ).values('yarn_count_id', 'program_quantity')
        for row in prog_balance_qs:
            program_balance_map[row['yarn_count_id']] = row['program_quantity']

        # Fetch inward balance data
        balance_qs = yarn_out_balance_table.objects.filter(  
            party_id=party_id, 
            yarn_count_id=count,
            inward_id__in=inward_ids,  # Filter by multiple inward_ids
            available_quantity__gt=0,
            remaining_quantity__gt=0
        ).values(
            'inward_id', 'yarn_count_id', 'po_id',
            'remaining_bags', 'remaining_quantity', 'bag_wt', 'available_quantity'
        )

        balance_list = list(balance_qs)

        # Get count names
        yarn_count_ids = [row['yarn_count_id'] for row in balance_list]
        count_names = count_table.objects.filter(id__in=yarn_count_ids).values('id', 'name')
        count_name_map = {item['id']: item['name'] for item in count_names}

        # Build the final result
        for row in balance_list:
            yarn_id = row['yarn_count_id']
            available_qty = row['available_quantity']
            remaining_qty = row['remaining_quantity']
            program_qty = program_balance_map.get(yarn_id, Decimal('0'))

            # Take minimum of all three
            selected_qty = min(program_qty, available_qty, remaining_qty)

            result.append({
                'tm_id': row['inward_id'],
                'bag': row['remaining_bags'],
                'per_bag': row['bag_wt'],
                'yarn_count_id': yarn_id,
                'yarn_count': count_name_map.get(yarn_id, ''),
                'quantity': float(selected_qty),
                'available_quantity': float(available_qty),
                'gross_wt': float(selected_qty),
                'po_id': row['po_id'],
                'inward_id': row['inward_id']
            })
            po_ids_set.add(row['po_id'])

        # Fetch PO deliveries (optional usage)
        po_deliveries = yarn_po_delivery_table.objects.filter(
            tm_po_id__in=po_ids_set
        )
        knitting_ids_set.update(
            po_deliveries.exclude(party_id__isnull=True)
                         .values_list('party_id', flat=True)
                         .distinct()
        )

        return JsonResponse({
            'data': result,
            'deliver_bag': 0,
            'deliver_quantity': 0,
            'knitting_ids': list(knitting_ids_set)
        })

    return JsonResponse({'data': [], 'deliver_bag': 0, 'deliver_quantity': 0, 'knitting_ids': []}, status=400)



def get_program_lists(request):
    party_id = request.POST.get('party_id')
    if not party_id:
        return JsonResponse({'error': 'party_id is required'}, status=400)

    program_ids = set()
    old_program_ids = set()

    # Step 1: Get new programs (out_quantity = 0)
    new_programs = yarn_program_balance_table.objects.filter(
        out_quantity=0,
        balance_quantity__gt=0
 
    ).values_list('program_id', flat=True)

    for program_id in new_programs:
        program_ids.add(program_id)

    # Step 2: Get old programs (out_quantity > 0 and balance_quantity > 0)
    old_programs_qs = yarn_program_balance_table.objects.filter(
        out_quantity__gt=0,
        balance_quantity__gt=0
    ).values('program_id')

    for row in old_programs_qs:
        program_id = row['program_id']
        count = yarn_delivery_table.objects.filter(
            party_id=party_id,
            program_id=program_id
        ).count()
        if count > 0:
            program_ids.add(program_id)
            old_program_ids.add(program_id)  # Track as old

    # Step 3: Get knitting info
    knitting_qs = knitting_table.objects.filter(id__in=program_ids,is_yarn=1).values_list('id', 'knitting_number', 'name')
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

            po_ids = sub_yarn_deliver_table.objects.filter(
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

 



def get_program_lists_test(request):
    party_id = request.POST.get('party_id')
    if not party_id:
        return JsonResponse({'error': 'party_id is required'}, status=400)

    program_ids = set()

    # Step 1: Get new programs (out_quantity = 0)
    new_programs = yarn_program_balance_table.objects.filter(
        out_quantity=0
    ).values_list('program_id', flat=True)

    for program_id in new_programs:
        program_ids.add(program_id)

    # Step 2: Get old programs (out_quantity > 0 and balance_quantity > 0)
    old_programs_qs = yarn_program_balance_table.objects.filter(
        out_quantity__gt=0,
        balance_quantity__gt=0
    ).values('program_id')

    for row in old_programs_qs:
        program_id = row['program_id']
        count = yarn_delivery_table.objects.filter(
            party_id=party_id,
            program_id=program_id
        ).count()
        if count > 0:
            program_ids.add(program_id)

    knitting_qs = knitting_table.objects.filter(id__in=program_ids,is_yarn=1).values_list('id', 'knitting_number', 'name')
    knitting_map = {row[0]: {'knitting_number': row[1], 'name': row[2]} for row in knitting_qs}

    final_list = []
    for program_id in program_ids:
        knitting_info = knitting_map.get(program_id)
        if knitting_info:
            final_list.append({
                'id': program_id,
                'knitting_number': knitting_info['knitting_number'],
                'name': knitting_info['name']
            })


    # Step 4: Loop over each program_id for additional yarn_out_balance info
    debug_data = []


    for pid in program_ids:
        try:
            # Fetch a single dictionary with yarn_count_id
            program_row = yarn_program_balance_table.objects.filter(program_id=pid).values('yarn_count_id', 'balance_quantity').first()
            if not program_row:
                continue  # Skip if no record found

            yarn_count_id = program_row['yarn_count_id']
            balance_quantity = program_row['balance_quantity']


            yarn_out_data = yarn_out_balance_table.objects.filter(
                party_id=party_id,
                yarn_count_id=yarn_count_id
            ).values('po_id', 'yarn_count_id')

            for entry in yarn_out_data:
                debug_data.append({
                    'program_id': pid,  
                    'program_quantity': balance_quantity,
                    'po_id': entry['po_id'],
                    'yarn_count_id': entry['yarn_count_id'],
                })
            print('final_list',final_list)

        except Exception as e:
            continue  # Log or handle errors if needed
 
    # Optional: return both final list and debug data
    # return JsonResponse({'programs': final_list, 'debug': debug_data}, safe=False)

    return JsonResponse(final_list, safe=False)

# ````````````````````````````````````````````````````````



@csrf_exempt
def check_duplicate_lot_no(request):
    if request.method == "POST":
        lot_no = request.POST.get('lot_no', '').strip().upper()

        # Check if the item already exists in the same group
        exists = yarn_delivery_table.objects.filter(lot_no=lot_no,status=1).exists()
 
        return JsonResponse({"exists": exists})



# Function to generate knitting number series with a prefix (e.g., PO)
def generate_do_num_series(model, field_name='do_number', padding=3, prefix='DO'):  
    # Get the maximum knitting number, and remove the prefix part to get the number
    # max_value = model.objects.aggregate(max_val=Max(field_name),status=1)['max_val']
    max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']

    try:
        # Extract the number part and increment
        if max_value:
            # Extract the number from the field and increment
            current_number = int(max_value.replace(prefix, '')) if max_value else 0
        else:
            current_number = 0
    except ValueError:
        current_number = 0

    # Generate the next knitting number with prefix and padding
    return f"{prefix}{str(current_number + 1).zfill(padding)}"

def safe_date(value):
    try:
        if value and isinstance(value, str) and value.strip() and value.strip() not in ['-', '–', '—', '“–”']:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        pass
    return None


def add_yarn_outward(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        try: 
            # Extracting data from the request
            do_date = request.POST.get('delivery_date') 
            # receive_date = request.POST.get('receive_date') 
            raw_date = request.POST.get('receive_date')
            receive_date = safe_date(raw_date) if raw_date else None
            receive_no = request.POST.get('receive_no') 
            supplier_id = request.POST.get('party_id') 
            lot_no = request.POST.get('lot_no')
            tx_inward = request.POST.get('inward_id') 
            knitting_prg_id = request.POST.get('prg_id')
            # po_id = request.POST.get('po_id')
            deliver_id = request.POST.get('party_id')
            remarks = request.POST.get('remarks') 
            # quantity = request.POST.get('quantity') 
            process_id = request.POST.get('process_id')
            do_number = request.POST.get('do_number')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 

            print('data:',chemical_data)
            # Get PO IDs 
            # po_ids = request.GET.getlist('po_id[]')  
            # po_ids_str = ",".join(po_ids)
            # tx_inward_str = ",".join([str(i) for i in tx_inward])  # Convert to string

            # Create a new entry in yarn_delivery_table (Parent table)

            # do_number = generate_do_num_series(yarn_delivery_table, 'do_number', padding=3, prefix='DO')
            material_request = yarn_delivery_table.objects.create(
                do_number=do_number,
                company_id=company_id,
                cfyear = 2025,
                receive_no=receive_no,
                receive_date=receive_date,
                delivery_date=do_date, 
                party_id=deliver_id,
                program_id=knitting_prg_id,
                inward_id=tx_inward,
                lot_no=lot_no,
                total_quantity= 0,#request.POST.get('total_quantity',0.0),
                gross_quantity=0, # request.POST.get('sub_total',0.0),
              
                remarks=remarks,
                created_by=user_id,
                # created_on=datetime.now()
            )
            print('material:',material_request)

           
            
            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')  # use Decimal for both if you're working with decimals

            for item in chemical_data:
                inward = item.get('inward_id')
                product_id = item.get('product_id')
                po_id = item.get('po_id') 

                # Create sub yarn delivery entry
                sub_yarn_deliver_table.objects.create(
                    company_id=company_id,
                    cfyear=2025,
                    tm_id=material_request.id,
                    po_id = po_id,
                    program_id = knitting_prg_id,

                    party_id=deliver_id,
                    yarn_count_id=product_id,
                    bag=item.get('bag'),
                    inward_id=inward,
                    per_bag=item.get('per_bag'),
                    quantity=item.get('quantity', 0),
                    gross_quantity=item.get('gross_wt', 0),
                    created_by=user_id,
                    # created_on=datetime.now()
                )

                # Convert and accumulate
                try:
                    gross = Decimal(str(item.get('gross_wt', 0)))
                except (InvalidOperation, TypeError):
                    gross = Decimal('0.00') 

                try:
                    qty = Decimal(str(item.get('quantity', 0)))
                except (InvalidOperation, TypeError):
                    qty = Decimal('0.00')

                total_gross += gross
                total_quantity += qty
                print('tot:', total_gross, total_quantity)

            material_request.gross_quantity = total_gross
            material_request.total_quantity = total_quantity
            material_request.save()   
                            

            # 🔹 **Update Parent PO Table (`po_table`)**
            # print('knt-deliver',True)
            # parent_po_table.objects.filter(id__in=po_ids).update(is_knitting_delivery=1)
            new_do_number = generate_next_do_number()
            return JsonResponse({
                'status': 'success', 
                'message': 'Outward data saved successfully.',  
                "do_number": new_do_number  # e.g., "PO-12345"
            })
            # return JsonResponse('yes', safe=False)  # Indicate success

        except Exception as e:
            print(f"❌ Error: {e}")  # Log error for debugging
            return JsonResponse('no', safe=False)  # Indicate failure

    return render(request, 'yarn_outward/yarn_outward_add.html')





 
import datetime 
from datetime import datetime

#     return JsonResponse({'data': formatted}) 
 
from django.utils.timezone import make_aware


def yarn_outward_list(request):
    company_id = request.session['company_id']
    print('company_id:', company_id)



    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    knitting = request.POST.get('knitting', '')
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Match if either created_on or updated_on falls in range
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


    if knitting:
            query &= Q(program_id=knitting)

    # Apply filters
    queryset = yarn_delivery_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())




    def getInwardNumberById(inward_model, inward_id):
        try:
            entry = inward_model.objects.get(id=inward_id)
            return entry.inward_number
        except inward_model.DoesNotExist:
            return '-'

    # data = list(yarn_delivery_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="yarn_deliver_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="yarn_deliver_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> \
                        <button type="button" onclick="outward_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
                        # <button type="button" onclick="outward_print(\'{}\')" class="btn btn-info btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['program_id']),
            'id': index + 1, 
            'delivery_date': item['delivery_date'].strftime('%d-%m-%Y') if item['delivery_date'] else '-',
            'inward_no': getInwardNumberById(yarn_inward_table, item['inward_id']) if item.get('inward_id') else '-',
            'deliver_no': item['do_number'] if item['do_number'] else '-',
            'total_quantity': item['total_quantity'] if item['total_quantity'] else '-',
            'lot_no': item['lot_no'] if item['lot_no'] else '-',
            'gross_total': item['gross_quantity'] if item['gross_quantity'] else '-',
            'deliver_to': getSupplier(party_table, item['party_id']),
            # 'po_number': getPONumberByInwardID(yarn_inward_table, item['inward_id']),
            'prg': getKnittingDisplayNameById(knitting_table, item['program_id']),
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
        }
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})

def getKnittingDisplayNameById(tbl, supplier_id):
    try:
        obj = tbl.objects.get(id=supplier_id)
        return f"{obj.name} - {obj.knitting_number}"
    except tbl.DoesNotExist:
        return "-"






from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import base64

@csrf_exempt
def yarn_outward_print(request):
    outward_id = request.GET.get('k')
    try:
        order_id = base64.b64decode(outward_id)
    except Exception:
        return JsonResponse({'error': 'Invalid Order ID'}, status=400)

    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    delivery_data = yarn_delivery_table.objects.filter(status=1, id=order_id).first()
    outward = yarn_delivery_table.objects.filter(id=order_id, status=1).values(
        'id', 'program_id', 'do_number', 'delivery_date', 'lot_no', 'party_id', 'total_quantity', 'gross_quantity'
    )
    
    program_details = []
    delivery_details = []
    total_roll = 0
    total_quantity = 0

    for out in outward:
        total_values = get_object_or_404(knitting_table, id=out['program_id'])
        program = knitting_table.objects.filter(id=out['program_id'], status=1).values(
            'id', 'knitting_number', 'program_date'
        ).first()
        if not program:
            return JsonResponse({'error': 'Program not found'}, status=404)

        details = sub_knitting_table.objects.filter(tm_id=out['program_id'], status=1).values(
            'count_id', 'gauge', 'fabric_id', 'tex', 'dia', 'gsm', 'rolls', 'wt_per_roll', 'quantity'
        )

        previous_outwards = yarn_delivery_table.objects.filter(
            program_id=out['program_id'], status=1, id__lt=out['id']
        ).order_by('-id').values_list('total_quantity', flat=True)
        pre_qty = sum(previous_outwards) if previous_outwards else '-'

        # ✅ Load all Dia objects used in this delivery, sort by name
        dia_ids = list({detail['dia'] for detail in details if detail.get('dia')})
        dia_lookup = {
            dia.id: dia for dia in dia_table.objects.filter(id__in=dia_ids).order_by('name')
        }

        for detail in details:
            dia_obj = dia_lookup.get(detail['dia'])
            if not dia_obj:
                continue  # skip invalid dia
            
            yarn_count = get_object_or_404(count_table, id=detail['count_id'])
            gauge = get_object_or_404(gauge_table, id=detail['gauge'])
            tex = get_object_or_404(tex_table, id=detail['tex'])

            fabric = get_object_or_404(fabric_program_table, id=detail['fabric_id'])
            fabric_obj = get_object_or_404(fabric_table, id=fabric.fabric_id, status=1)
            fabric_display_name = fabric_obj.name

            rolls = detail['rolls'] or 0
            quantity = detail['quantity'] or 0
            total_roll += rolls
            total_quantity += quantity

            program_details.append({
                'name': yarn_count.name,
                'fabric': fabric_display_name,
                'gauge': gauge.name,
                'gsm': detail['gsm'],
                'tex': tex.name,
                'dia': dia_obj.name,
                'dia_sort': dia_obj.name,
                'quantity': quantity,
                'roll': rolls,
                'wt_per_roll': detail['wt_per_roll'],
            })

        # ✅ Sort by Dia name ascending
        program_details = sorted(program_details, key=lambda x: x['dia_sort'])
        for d in program_details:
            d.pop('dia_sort', None)

        tx_yarn = sub_yarn_deliver_table.objects.filter(
            tm_id=out['id'], status=1
        ).values(
            'yarn_count_id', 'party_id', 'po_id', 'bag', 'per_bag', 'quantity', 'gross_quantity'
        ).first()

        po = get_object_or_404(parent_po_table, id=tx_yarn['po_id'])
        mill = get_object_or_404(party_table, status=1, id=po.mill_id)

        yarn_count = get_object_or_404(count_table, id=tx_yarn['yarn_count_id'])

        if tx_yarn:
            party = get_object_or_404(party_table, id=tx_yarn['party_id'])
            delivery_details.append({
                'mill': party.name,
                'name': yarn_count.name,
                'fabric': fabric.name,
                'lot_no': out['lot_no'],
                'do_number': out['do_number'],
                'do_date': out['delivery_date'],
                'bag': tx_yarn['bag'],
                'per_bag': tx_yarn.get('per_bag'),
                'quantity': tx_yarn['quantity'],
                'gross_quantity': tx_yarn['gross_quantity'],
            })

    # image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'
    image_url = 'http://localhost:8000/static/assets/images/mira.png'
    print('image-url:',image_url)
    delivery = yarn_delivery_table.objects.filter(status=1, id=order_id).values('remarks').first()
    remarks = delivery['remarks'] if delivery else ''

    context = {
        'total_values': total_values,
        'mill_name': mill.name,
        'gstin': party.gstin,
        'mobile': party.mobile,
        'program_details': program_details,
        'total_roll': total_roll,
        'total_quantity': total_quantity,
        'delivery_details': delivery_details,
        'company': company_table.objects.filter(status=1).first(),
        'program': program,
        'image_url': image_url,
        'remarks': remarks,
        'previous_no': pre_qty if pre_qty else '-',
    }

    return render(request, 'yarn_outward/outward_print.html', context)


    # template = get_template('yarn_outward/outward_print.html')
    # html = template.render(context) 

    # # Generate PDF
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline; filename="yarn_outward.pdf"'
 
    # result = BytesIO()
    # pdf_status = pisa.CreatePDF(src=html, dest=result, link_callback=link_callback)

    # if not pdf_status.err:
    #     response.write(result.getvalue())
    #     return response
    # else:
    #     return HttpResponse("PDF generation failed", status=500)






def yarn_outward_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'yarn_outward/yarn_outward_details.html', {'error_message': 'ID is missing.'})

        # Ensure valid Base64 padding before decoding
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id + '=' * (-len(encoded_id) % 4)).decode()
            material_id = int(decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'yarn_outward/yarn_outward_details.html', {'error_message': 'Invalid ID format.'})

        # Fetch material instance
        material_instance = sub_yarn_deliver_table.objects.filter(tm_id=material_id).first()

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
                material_instance = sub_yarn_deliver_table.objects.create(
                    tm_id=material_id,
                    bag=bag,
                    per_bag=per_bag,
                    # amount=amount, 
                    # rate=rate, 
                    quantity=quantity
                )
            else:
                return render(request, 'yarn_outward/yarn_outward_details.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = yarn_delivery_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'yarn_outward/yarn_outward_details.html', {'error_message': 'Parent stock not found.'})

        # Fetch supplier name
        supplier_name = "-"
        if parent_stock_instance.party_id:
            supplier = party_table.objects.filter(id=parent_stock_instance.party_id, status=1).first()
            supplier_name = supplier.name if supplier else "-"
        count = count_table.objects.filter(status=1) 
        # Fetch related data
        context = { 
            'material': material_instance,
            'parent_stock_instance': parent_stock_instance,
            'product': product_table.objects.filter(status=1), 
            'party': party_table.objects.filter(is_knitting=1 ),
            'program': knitting_table.objects.filter(status=1),
            'supplier_id': supplier_name,  
            'supplier': party_table.objects.filter(is_knitting=1), 
            'process': process_table.objects.filter(status=1),
            'stage': process_table.objects.filter(stage='Yarn', status=1).first(), 
            'po': parent_po_table.objects.filter(status=1),
            'count':count,
            'inward_lists':yarn_inward_table.objects.filter(status=1)
        }

        return render(request, 'yarn_outward/yarn_outward_details.html', context)

    except Exception as e:
        logger.error(f"Error in yarn_deliver_edit: {e}") 
        return render(request, 'yarn_outward/yarn_outward_details.html', {'error_message': f'An unexpected error occurred: {str(e)}'})

 



def yarn_outward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        try:
            # First, get the delivery record
            delivery = yarn_delivery_table.objects.filter(id=data_id, is_active=1).first()
            if not delivery:
                return JsonResponse({'message': 'no such delivery record'})

            ## Now check if the corresponding inward record exists and is active
            # inward_exists = yarn_inward_table.objects.filter(id=delivery.inward_id, status=1).exists()
            # if not inward_exists:
                # return JsonResponse({'message': 'inward not active'})

            # Proceed with soft delete
            yarn_delivery_table.objects.filter(id=data_id).update(status=0, is_active=0)
            sub_yarn_deliver_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except Exception as e:
            return JsonResponse({'message': 'error', 'error_message': str(e)})

    return JsonResponse({'message': 'Invalid request method'})



# def yarn_outward_delete(request):
#     user_type = request.session.get('user_type')
#     # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

#     # if not has_access:
#     #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


#     if request.method == 'POST':
#         data_id = request.POST.get('id')
#         try:
#             # Update the status field to 0 instead of deleting 
#             yarn_delivery_table.objects.filter(id=data_id).update(status=0,is_active=0)
#             sub_yarn_deliver_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
#             return JsonResponse({'message': 'yes'})
#         except yarn_delivery_table.DoesNotExist:
#             return JsonResponse({'message': 'no such data'})
#     else:
#         return JsonResponse({'message': 'Invalid request method'})
    
 
 


def tx_yarn_outward_list(request):
    if request.method == 'POST':
        master_id = request.POST.get('tm_id')
        print('deliver-ID:', master_id)

        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_yarn_deliver_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    total_quantity = child_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    gross_total = child_data.aggregate(Sum('gross_quantity'))['gross_quantity__sum'] or 0
                   
                    # Fetch process tolerance value
                    process = process_table.objects.filter(stage='yarn').first()  # Ensure `satge='yarn'` is correct
                    process_tolerance = process.tolerance if process else 0

                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0

                    for item in data:
                        index += 1

                        # Calculate deviation
                        # bag_deviation = abs((item['deviation_bag'] or 0) - original_bag)
                        # per_bag_deviation = abs((item['deviation_per_bag'] or 0) - original_per_bag)

                        # # Check if the deviation exceeds process tolerance
                        # show_debit_note = bag_deviation > process_tolerance or per_bag_deviation > process_tolerance

                        # Prepare action buttons
                        # action_buttons = f'''
                        #     <button type="button" onclick="yarn_deliver_detail_edit('{item['id']}')" class="btn btn-primary btn-xs" >
                        #         <i class="feather icon-edit"></i>
                        #     </button>
                        #    <button type="button" onclick="yarn_deliver_delete({{ item.id }}, {{ item.inward_id }}, {{ item.deliver_id }}, {{ item.product_id }})" class="btn btn-danger btn-xs">
                        #         <i class="feather icon-trash-2"></i>
                        #     </button>

                        # '''


                        action_buttons = f'''
                            <button type="button" onclick="yarn_deliver_detail_edit('{item['id']}')" class="btn btn-primary btn-xs">
                                <i class="feather icon-edit"></i>
                            </button>
                            <button type="button" onclick="yarn_deliver_delete('{item['id']}', '{item['inward_id']}', '{item['party_id']}', '{item['yarn_count_id']}', '{item['bag']}' ,'{item['quantity']}')" class="btn btn-danger btn-xs">
                                <i class="feather icon-trash-2"></i>
                            </button>
                        '''




                         # <button type="button" onclick="yarn_deliver_delete('{item['id'],item['inward_id'],item['deliver_id'],item['product_id']}')" class="btn btn-danger btn-xs">
                            #     <i class="feather icon-trash-2"></i>
                            # </button>
                        # if show_debit_note:
                        #     action_buttons += f'''
                        #         <button type="button" onclick="generate_debit_note('{item['id']}')" class="btn btn-info btn-xs">
                        #             <i class="feather icon-file-text"></i> Debit Note
                        #         </button>
                        #         <script>
                        #             document.getElementById('edit_button_{item['id']}').style.display = 'display';
                        #         </script>
                        #     '''

                        # Append formatted data
                        formatted_data.append({
                            'action': action_buttons,
                            'id': index,
                            
                            # 'po_number': getPODeliveryNameById(knitting_table, item['lot_no'], parent_po_table),
                            'product': getItemNameById(count_table, item['yarn_count_id']),
                            # 'deliver_to': getDeliveryNameById(knitting_table, item['lot_no'],party_table),
                            'bag': item['bag'] if item['bag'] else '-',
                            'per_bag': item['per_bag'] if item['per_bag'] else '-',
                            # 'lot_no': item['lot_no'] if item['lot_no'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'gross_wt': item['gross_quantity'] if item['gross_quantity'] else '-',
                            # 'rate': item['rate'] if item['rate'] else '-',
                            # 'amount': item['amount'] if item['amount'] else '-',
                            'status': '<span class="badge text-bg-success">Active</span>' 
                            if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })
                        print(formatted_data)

                    formatted_data.reverse()

                    # Return data with the totals included
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'gross_total': gross_total,
                        # 'total_amount': total_amount,
                        # 'tax_total': tax_total,
                        # 'grand_total': grand_total
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})
 
        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'}) 
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})



 
def tx_yarn_outward_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        tm_id = request.POST.get('tm_id') 
        product_id = request.POST.get('product_id')
        deliver_id = request.POST.get('deliver_id')
        inward_id = request.POST.get('inward_id') 
        bag = request.POST.get('bag')
        quantity = request.POST.get('quantity')
        try:
            # Update the status field to 0 instead of deleting
            sub_yarn_deliver_table.objects.filter(id=data_id,tm_id=tm_id,inward_id=inward_id,deliver_id=deliver_id,product_id=product_id).update(status=0,is_active=0)
            updated_rows = sub_yarn_inward_table.objects.filter(
                tm_id=inward_id, product_id=product_id, deliver_to=deliver_id
            ).update(
                remaining_bag=F('remaining_bag') + bag,
                remaining_quantity=F('remaining_quantity') + quantity,
            )

            if updated_rows == 0:
                print(f"⚠️ No matching sub_yarn_inward_table record found for tm_id={inward_id}, product_id={product_id}")

            return JsonResponse({'message': 'yes'})
        except sub_yarn_deliver_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    



def outward_yarn_edit(request):
    if is_ajax and request.method == "POST": 
        try:
            item_id = request.POST.get('id')
            if not item_id:
                return JsonResponse({'error': 'Missing ID'}, status=400)

            # Get the current sub knitting deliver item
            deliver_data = sub_yarn_deliver_table.objects.filter(id=item_id).first()
            if not deliver_data:
                return JsonResponse({'error': 'Data not found'}, status=404)

            response_data = {
                'id': deliver_data.id,
                'bag': deliver_data.bag, 
                'per_bag': deliver_data.per_bag,
                'quantity': deliver_data.quantity,
                'gross_wt': deliver_data.gross_quantity,
                'tm_po_id': 0,
                'inward_id': deliver_data.inward_id,
                'product_id': deliver_data.yarn_count_id,
            }

            # ✅ Fetch the Original Bag and Per Bag from Inward ID
            inward_id = deliver_data.inward_id
            if inward_id:
                inward_data = sub_yarn_deliver_table.objects.filter(tm_id=inward_id).first()
                print('delivery:',inward_data)
                if inward_data:
                    response_data['original_inward_bag'] = inward_data.bag
                    response_data['original_inward_per_bag'] = inward_data.per_bag
                else:
                    response_data['original_inward_bag'] = None
                    response_data['original_inward_per_bag'] = None
            else:
                response_data['original_inward_bag'] = None
                response_data['original_inward_per_bag'] = None

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)




def update_yarn_outward(request):
    if request.method == 'POST':
        try:
            master_id = request.POST.get('tm_po_id')
            product_id = request.POST.get('product_id')
            lot = request.POST.get('lot_no')
            inward_id = request.POST.get('tx_inward_id')
            deliver_to = request.POST.get('party_id')
            print('values:',master_id, product_id, lot, inward_id, deliver_to)
            if not master_id or not product_id or not inward_id or not deliver_to:
                return JsonResponse({'success': False, 'error_message': 'Missing required fields'})

            bag = int(request.POST.get('bag', 0) or 0)
            per_bag = Decimal(request.POST.get('per_bag', 0) or 0)
            quantity = Decimal(request.POST.get('quantity', 0) or 0)
            gross_wt = Decimal(request.POST.get('gross_wt', 0) or 0)

            print(f"Received data: master_id={master_id}, product_id={product_id}, inward_id={inward_id}, party_id={deliver_to}")

            child_item = sub_yarn_deliver_table.objects.filter(
                tm_id=master_id, yarn_count_id=product_id, inward_id=inward_id, party_id=deliver_to
            ).first()


            if child_item:
                child_item.bag += bag
                child_item.per_bag = per_bag
                child_item.quantity = Decimal(child_item.quantity or 0) + quantity
                child_item.gross_quantity = Decimal(child_item.gross_quantity or 0) + gross_wt
                child_item.status = 1
                child_item.is_active = 1
                child_item.save()




            else:
                # Create new record
                sub_yarn_deliver_table.objects.create(
                    tm_id=master_id,
                    lot_no=lot,
                    yarn_count_id=product_id,
                    inward_id=inward_id,
                    party_id=deliver_to,
                    bag=bag,
                    per_bag=per_bag,
                    quantity=quantity,
                    gross_quantity=gross_wt,
                    status=1,
                    is_active=1,
                )


            # Update totals
            updated_totals = update_tm_table_totals(master_id)

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_tm_table_totals(master_id): 
    """
    Recalculates total values and updates them in parent_po_table.
    """
    try:
        # Fetch all child records linked to the given master_id
        tx = sub_yarn_deliver_table.objects.filter(tm_po_id=master_id, status=1, is_active=1)

        # Aggregate totals (ensuring Decimal type)
        total_quantity = tx.aggregate(Sum('quantity'))['quantity__sum']
        gross_quantity = tx.aggregate(Sum('gross_quantity'))['gross_quantity__sum'] or Decimal('0.00')

        # Update values in parent_po_table
        yarn_delivery_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            gross_quantity=gross_quantity   
        )

        # Return updated values for frontend update 
        return {
            'total_quantity': total_quantity,
            'gross_quantity':gross_quantity,
        
        }

    except Exception as e:
        return {'error': str(e)}



#    var formData = new FormData(this);
#     formData.append('tm_id', $('#tm_prg_id').val());
#     formData.append('receive_date', $('#receive_date').val());
#     formData.append('receive_no', $('#receive_no').val());
#     formData.append('lot_no', $('#lot_no').val());
#     formData.append('delivery_date', $('#delivery_date').val());


from django.db import IntegrityError

def tm_outward_details_update(request):
    if request.method == 'POST':
        tm_id = request.POST.get('tm_id')
        receive_date_str = request.POST.get('receive_date')
        delivery_date_str = request.POST.get('delivery_date')
        receive_no = request.POST.get('receive_no')  # 'yarn' or 'grey'
        lot_no = request.POST.get('lot_no')  # 'yarn' or 'grey'
        remarks = request.POST.get('remarks')  # 'yarn' or 'grey'
      
        if not tm_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            parent_item = yarn_delivery_table.objects.get(id=tm_id)
            parent_item.receive_no = receive_no
            parent_item.lot_no = lot_no
            parent_item.remarks = remarks
         
            if delivery_date_str: 
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
                parent_item.delivery_date = delivery_date

            if receive_date_str:
                receive_date = datetime.strptime(receive_date_str, '%Y-%m-%d').date()
                parent_item.receive_date = receive_date

            parent_item.save()

            return JsonResponse({'success': True, 'message': 'Master Details updated successfully'})

        except knitting_table.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Master details not found'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error_message': f'Database integrity error: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
