import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from software_app.models import *
from yarn.models import *
from employee.models import *
from grey_fabric.models import *
from common.utils import *
from program_app.models import *
from django.db.models import Q

from software_app.views import getItemNameById, getSupplier, is_ajax
from django.views.decorators.csrf import csrf_exempt


# def generate_next_inw_number():
#     last_purchase = yarn_inward_table.objects.filter(status=1).order_by('-id').first()
#     if last_purchase and last_purchase.inward_number:
#         # Extract the numeric part after 'DO'
#         last_num_str = last_purchase.inward_number.replace('PI', '')
#         try:
#             next_num = int(last_num_str) + 1
#         except ValueError:
#             next_num = 1
#     else:
#         next_num = 1

#     # Format with leading zeros and prefix
#     return f"PI{next_num:03d}"


import re

def generate_next_inw_number():
    last_purchase = yarn_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_number:
        match = re.search(r'INW-(\d+)', last_purchase.inward_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"INW-{next_num:03d}"


def yarn_inward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        # supplier = party_table.objects.filter(Q(is_supplier=1) | Q(is_knitting=1)) 
        supplier = party_table.objects.filter(is_mill=1) 
        # party = party_table.objects.filter(status=1,is_mill=1)
        party = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)

        product = product_table.objects.filter(status=1)
        last_purchase = yarn_inward_table.objects.order_by('-id').first()
        inward_number = generate_next_inw_number 
        # if last_purchase:  
        #     inward_number = last_purchase.id + 1 
        # else:  
        #     inward_number = 1  # Default if no records exist
        po_list = parent_po_table.objects.filter(status=1)  #is_knitting_prg=1,
        program = knitting_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        return render(request,'yarn_inward/yarn_inward_add.html',{'inward_number':inward_number,'supplier':supplier,'party':party,'product':product,'po_list':po_list
                                                                   ,'count':count,'program':program})
    else:
        return HttpResponseRedirect("/signin")


def get_knitting_programs(request):
    po_ids = request.GET.getlist('po_ids[]')  # Get selected PO IDs as a list

    programs = knitting_table.objects.filter(po_id__in=po_ids).values('id', 'lot_no')

    return JsonResponse({'programs': list(programs)}, safe=False)



from decimal import Decimal, InvalidOperation




def generate_inward_num_series(model, field_name='inward_number', padding=3, prefix='PI'):
    full_prefix = f"{prefix}-"
    
    # Only fetch rows starting with the prefix to avoid errors
    max_value = (
        model.objects
        .filter(**{f"{field_name}__startswith": full_prefix})
        .aggregate(max_val=Max(field_name))
        ['max_val']
    )

    current_number = 0
    if max_value:
        match = re.search(rf"{re.escape(full_prefix)}(\d+)", max_value)
        if match:
            current_number = int(match.group(1))

    return f"{full_prefix}{str(current_number + 1).zfill(padding)}"




# def generate_do_num_series(model, field_name='  ', padding=3, prefix='DO'):
#     full_prefix = f"{prefix}-"
#     max_value = model.objects.filter(status=1).aggregate(max_val=Max(field_name))['max_val']
    
#     current_number = 0  
#     if max_value and max_value.startswith(full_prefix):
#         try:
#             current_number = int(max_value.replace(full_prefix, ''))
#         except ValueError:
#             current_number = 0

#     return f"{full_prefix}{str(current_number + 1).zfill(padding)}"



def generate_do_num_series():
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


from collections import defaultdict


def generate_inw_num_series():
    last_purchase = yarn_inward_table.objects.filter(status=1).order_by('-id').first()
    if last_purchase and last_purchase.inward_number:
        match = re.search(r'INW-(\d+)', last_purchase.inward_number)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f"INW-{next_num:03d}"


@csrf_exempt
def add_yarn_inward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id') 
        company_id = request.session.get('company_id')

        try:
            supplier_id = request.POST.get('supplier_id')
            # lot_name = request.POST.get('lot_name') or '0'yarn_inward_add
            remarks = request.POST.get('remarks')
            inward_no = request.POST.get('inward_no')
            print('in-no:',inward_no)
            po_list = request.POST.get('po_list')
            inward_date = request.POST.get('inward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            inward_no = generate_inw_num_series()
            # inward_no = generate_inward_num_series(yarn_inward_table, 'inward_number', prefix='PI')
            # print('inw-no:',inward_no)
            # Create parent inward entry
            material_request = yarn_inward_table.objects.create(
                inward_number=inward_no,
                inward_date=inward_date,
                party_id=supplier_id,
                cfyear=2025,
                po_id=po_list,
                company_id=company_id,
                total_quantity=0,
                gross_quantity=0,
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_gross = Decimal('0.00')   
            total_quantity = Decimal('0.00')
            inward_required = False

            for chemical in chemical_data:
                is_inward_raw = str(chemical.get('is_inward', '1')).strip().lower()
                is_inward = 1 if is_inward_raw in ['1', 'on', 'true'] else 0

                if is_inward == 0: 
                    inward_required = True

                tx_id = chemical.get('tx_id', 0)
                program_id = chemical.get('program_id', 0)
                deliver_id = chemical.get('deliver_id', 0)
                lot_no = chemical.get('lot_no')
                product_id = chemical.get('product_id')
                raw_date = chemical.get('receive_date')
                receive_date = safe_date(raw_date) if raw_date else None
                receive_no = chemical.get('receive_no')

                delivered_bag = safe_decimal(chemical.get('bag'))
                delivered_quantity = safe_decimal(chemical.get('quantity'))
                gross_wt = safe_decimal(chemical.get('gross_wt'))

                sub_yarn_inward_table.objects.create(
                    tm_id=material_request.id,
                    yarn_count_id=product_id,
                    po_id=po_list,
                    receive_date=receive_date,
                    receive_no=receive_no if receive_no else 0,
                    cfyear=2025,
                    company_id=company_id,
                    program_id=program_id or 0,
                    party_id=supplier_id,
                    outward_party_id=deliver_id if deliver_id else 0,
                    bag=delivered_bag,
                    per_bag=chemical.get('per_bag'),
                    quantity=delivered_quantity,
                    gross_quantity=gross_wt,
                    created_by=user_id,
                    created_on=timezone.now()
                )

                total_gross += gross_wt
                total_quantity += delivered_quantity

            material_request.gross_quantity = total_gross
            material_request.total_quantity = total_quantity
            material_request.save()

            if not inward_required:  # means all are inward = 1
                try:
                    # Group by (deliver_id, program_id)
                    delivery_groups = defaultdict(list)
                    for chem in chemical_data:
                        if str(chem.get('is_inward', '1')).strip().lower() in ['1', 'on', 'true']:
                            key = (chem.get('deliver_id'), chem.get('program_id'))
                            delivery_groups[key].append(chem)

                    for (deliver_id, program_id), delivery_data in delivery_groups.items():
                        group_total_quantity = sum(safe_decimal(item.get('quantity')) for item in delivery_data)
                        group_total_gross = sum(safe_decimal(item.get('gross_wt')) for item in delivery_data)
                        group_receive_date = safe_date(delivery_data[0].get('receive_date')) if delivery_data[0].get('receive_date') else None
                        group_receive_no = delivery_data[0].get('receive_no') or 0
                        lot_no = delivery_data[0].get('lot_no')  # Get the lot_no from the first item

                        do_number = generate_do_num_series()
                        # do_number = generate_do_num_series(yarn_delivery_table, 'do_number', padding=3, prefix='DO')
                        delivery_entry = yarn_delivery_table.objects.create(
                            do_number=do_number,
                            receive_date=group_receive_date,
                            receive_no=group_receive_no,
                            company_id=company_id,
                            cfyear=2025,
                            delivery_date=group_receive_date,
                            program_id=program_id,
                            party_id=deliver_id,
                            inward_id=str(material_request.id),
                            lot_no=lot_no,
                            total_quantity=group_total_quantity,
                            gross_quantity=group_total_gross,
                            remarks=remarks,
                            created_by=user_id,
                            created_on=timezone.now()
                        )

                        for item in delivery_data:
                            sub_yarn_deliver_table.objects.create(
                                tm_id=delivery_entry.id,
                                company_id=company_id,
                                cfyear=2025,
                                party_id=deliver_id,
                                program_id=program_id,
                                po_tx_id = tx_id,
                                po_id=po_list,
                                yarn_count_id=item.get('product_id'), 
                                bag=safe_decimal(item.get('bag')),
                                inward_id=material_request.id,
                                per_bag=item.get('per_bag'),
                                gross_quantity=safe_decimal(item.get('gross_wt')), 
                                quantity=safe_decimal(item.get('quantity')),
                                created_by=user_id,
                                created_on=timezone.now()
                            )

                except Exception as ke:
                    print(f"❌ Error creating grouped deliveries: {ke}")



            next_number = generate_next_inw_number()

            return JsonResponse({
                'status': 'success', 
                'message': 'Added Successfully!',
                'inward_number':next_number})

        except Exception as e:
            print(f"❌ Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'knitting_deliver/yarn_inward.html')


from django.db.models import Sum

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
from decimal import Decimal



@csrf_exempt
def tx_load_po_details_inward(request):
    if request.method == "GET":
        supplier_id = request.GET.get('supplier_id')
        po_ids = request.GET.getlist('po_id[]')
        deliver_ids = request.GET.getlist('deliver_to')

        if not po_ids or not deliver_ids:
            return JsonResponse({'error': 'Purchase Order ID(s) and Delivery ID(s) are required.'}, status=400)

        try:
            parent_pos = parent_po_table.objects.filter(id__in=po_ids, mill_id=supplier_id)
            if not parent_pos.exists():
                return JsonResponse({'error': 'Purchase orders not found.'}, status=404)

            order_data = []
            total_po_bag = Decimal('0.00')
            total_po_quantity = Decimal('0.00')
            total_inward_bag = Decimal('0.00')
            total_inward_quantity = Decimal('0.00')

            for po in parent_pos:
                # Group by party_id and sum bag and quantity
                deliveries = yarn_po_delivery_table.objects.filter(
                    tm_po_id=po.id,
                    party_id__in=deliver_ids,
                    status=1
                ).values('party_id').annotate(
                    total_bag=Sum('bag'),
                    total_quantity=Sum('quantity')
                )

                program = knitting_table.objects.filter(po_id=po.id).first()
                program_lot = program.lot_no if program and program.lot_no else 0

                child = parent_po_table.objects.filter(id=po.id, is_active=1).first()
                if not child:
                    continue

                product = count_table.objects.filter(id=child.yarn_count_id).first()
                total_bag = Decimal(child.bag or 0)
                total_quantity = Decimal(child.quantity or 0)

                for delivery in deliveries:
                    party_id = delivery['party_id']
                    po_bag = Decimal(delivery['total_bag'] or 0)
                    po_quantity = Decimal(delivery['total_quantity'] or 0)

                    inward_totals = sub_yarn_inward_table.objects.filter(
                        po_id=po.id,
                        outward_party_id=party_id,
                        is_active=1
                    ).aggregate(
                        inward_bag=Sum('bag'),
                        inward_quantity=Sum('quantity')
                    )

                    inward_bag = Decimal(inward_totals.get('inward_bag') or 0)
                    inward_quantity = Decimal(inward_totals.get('inward_quantity') or 0)

                    balance_bag = po_bag - inward_bag
                    balance_quantity = po_quantity - inward_quantity

                    if balance_bag <= 0 and balance_quantity <= 0:
                        continue

                    total_po_bag += po_bag
                    total_po_quantity += po_quantity
                    total_inward_bag += inward_bag
                    total_inward_quantity += inward_quantity

                    order_data.append({
                        'party_id': party_id,
                        'po_bag': float(po_bag),
                        'po_quantity': float(po_quantity),
                        'inward_bag': float(inward_bag),
                        'inward_quantity': float(inward_quantity),
                        'balance_bag': float(balance_bag),
                        'balance_quantity': float(balance_quantity),
                        'product_id': child.yarn_count_id,
                        'product_name': product.name if product else "Unknown Product",
                        'tax_value': 5,
                        'bag': float(balance_bag),
                        'per_bag': float(child.per_bag or 0),
                        'tx_quantity': float(po_quantity),
                        'quantity': float(total_quantity),
                        'rate': float(child.rate or 0),
                        'actual_rate': float(child.net_rate or 0),
                        'discount': float(child.discount or 0),
                        'gross_wt': float(child.gross_quantity or 0),
                        'id': child.id,
                        'po_id': po.id,
                        'tm_id': po.id,
                        'program_lot': program_lot,
                        'total_quantity': float(total_quantity),
                        'total_bag': float(total_bag)
                    })

            balance_bag = total_po_bag - total_inward_bag
            balance_quantity = total_po_quantity - total_inward_quantity

            return JsonResponse({
                'orders': order_data,
                'po_bags': float(total_po_bag),
                'po_quantitys': float(total_po_quantity),
                'inward_bag': float(total_inward_bag),
                'inward_quantity': float(total_inward_quantity),
                'balance_bag': float(balance_bag),
                'balance_quantity': float(balance_quantity),
                'per_bag': order_data[0]['per_bag'] if order_data else 0
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)






def yarn_list(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        po = parent_po_table.objects.filter(status=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'yarn_inward/yarn_inward.html',{'supplier':supplier,'party':party,'product':product,'po':po})
    else:
        return HttpResponseRedirect("/signin")
    
from django.utils.timezone import make_aware

def yarn_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    query = Q() 

    # Date range filter
    party = request.POST.get('party', '')
    po_id = request.POST.get('po_id', '')
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')

    if start_date and end_date:
        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Match if either created_on or updated_on falls in range
            date_filter = Q(inward_date__range=(start_date, end_date)) | Q(updated_on__range=(start_date, end_date))
            query &= date_filter
        except ValueError:
            return JsonResponse({
                'data': [],
                'message': 'error',
                'error_message': 'Invalid date format. Use YYYY-MM-DD.'
            })
    
    if party:
            query &= Q(party_id=party) 

    if po_id:
            query &= Q(po_id=po_id) 


    # Apply filters
    queryset = yarn_inward_table.objects.filter(status=1).filter(query)
    data = list(queryset.order_by('-id').values())
    ids = [item['id'] for item in data]
    # available = yarn_inward_available.objects.filter(inward_id__in=ids).values('available_quantity')


    available_qs = yarn_inward_available.objects.filter(inward_id__in=ids).values('inward_id', 'available_quantity')

    available_dict = {}
    for entry in available_qs:
        inward_id = entry['inward_id']
        qty = entry['available_quantity']
        # If multiple entries per inward_id, you can sum or decide logic here
        available_dict[inward_id] = qty


    # available = yarn_inward_available.objects.filter(inward_id__in=data.id).values('available_quantity')
    # print('avail-qty:',available)

    # data = list(yarn_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [ 
        {
            'action': '<button type="button" onclick="po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="yarn_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>\
                        <button type="button" onclick="inward_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_no': item['inward_number'] if item['inward_number'] else'-', 
            'inward_date': item['inward_date'].strftime('%d-%m-%Y') if item['inward_date'] else '-',
            'po_number':getPONumberById(parent_po_table, item['po_id'] ), 
            'supplier_id':getSupplier(party_table, item['party_id'] ), 
            # 'yarn_count': get_yarn_count_by_tm_id(item['id']),
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'available_quantity': available_dict.get(item['id'], 0),  # get available qty or 0
            'total_gross': item['gross_quantity'] if item['gross_quantity'] else'-', 
            # 'tax_total': item['tax_total'] if item['tax_total'] else'-', 
            # 'total_amount': item['total_amount'] if item['total_amount'] else'-', 
            # 'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',

        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 
def get_yarn_count_by_tm_id(tm_id):
    try:
        yarn_obj = sub_yarn_inward_table.objects.get(tm_id=tm_id)
        count_obj = count_table.objects.get(id=yarn_obj.yarn_count_id)
        return count_obj.name
    except (sub_yarn_inward_table.DoesNotExist, count_table.DoesNotExist):
        return '-'




@csrf_exempt
def print_yarn_inward(request):
    outward_id = request.GET.get('k')
    order_id = base64.b64decode(outward_id)
    print('print-id:',order_id)
    
    if not order_id:
        return JsonResponse({'error': 'Order ID not provided'}, status=400)

    delivery_data = yarn_inward_table.objects.filter(status=1, id=order_id) 
    
    inwards = yarn_inward_table.objects.filter(status=1, id=order_id).first()

    # outward_id_raw = inwards.outward_id or ''  # Might be '1,2,3'
    po_id = inwards.po_id or 0
   

# Process PO number
    if po_id:
        po_obj = parent_po_table.objects.filter(status=1, id=po_id).values('po_number').first()
        po_number = po_obj['po_number'] if po_obj else '-'
    else:
        po_number = '-'
        print('po-no:',po_number)


    print('delivery:',outward_id,   po_id)
    outward = yarn_inward_table.objects.filter(id = order_id,status=1).values('id','inward_number','inward_date','party_id', 'total_quantity', 'gross_quantity')
    print('out:',outward)


    program_details = []
    delivery_details = []
    # ✅ Initialize totals here
    # total_bag = 0
    # total_quantity = 0

    
    # Then build the delivery details (independent of above)
    for out in outward:

        total_gross = 0
        total_bag = 0

        tx_yarn_qs = sub_yarn_inward_table.objects.filter(
            tm_id=out['id'],
            status=1
        ).values(
            'yarn_count_id','bag','per_bag','quantity','gross_quantity','receive_no','receive_date',
        )
        
        
        
        # ).values(
        #     'yarn_count_id', 'fabric_id', 'gauge_id', 'tex_id',
        #     'gsm', 'dia_id', 'po_id', 'program_id',
        #     'lot_no', 'roll', 'total_wt', 'gross_wt'
        # )

        print('tx-yarns:',tx_yarn_qs)

        party = get_object_or_404(party_table, id=out['party_id'])
        gstin = party.gstin
        mobile = party.mobile
        party_name = party.name

        for tx_yarn in tx_yarn_qs:
            if not tx_yarn['bag'] or tx_yarn['bag'] == 0:
                continue  # Skip this entry if roll is 0

            yarn_count = get_object_or_404(count_table, id=tx_yarn['yarn_count_id'])
    
            delivery_details.append({
                'mill': party.name,
                'yarn_count': yarn_count.name,
               
                'inward_number': out['inward_number'],
                'inward_date': out['inward_date'],
                'bag': tx_yarn['bag'],
                'per_bag': tx_yarn.get('per_bag'),
                'quantity': tx_yarn['quantity'],
                'gross_quantity': tx_yarn['gross_quantity'],  
                'receive_no': tx_yarn['receive_no'],
                'receive_date': tx_yarn['receive_date'], 
                
            })
            print('deli-details:',delivery_details)

            # Accumulate totals 
            total_bag += tx_yarn['bag'] or 0
            total_gross += tx_yarn['gross_quantity'] or 0



  
    # image_url = 'http://localhost:8000/static/assets/images/mira.png'
    image_url = 'http://mpms.ideapro.in:7026/static/assets/images/mira.png'
    # total_gross +=  tx_yarn['gross_wt'] 

    delivery = yarn_inward_table.objects.filter(status=1, id=order_id).values('remarks').first()
    remarks = delivery['remarks'] if delivery else ''
    print('image_url:',image_url)
    # total_roll +=  tx_yarn['roll'] 
    # pre_no = previous_outward['do_number']

    print('deli-data:',delivery_data)
    context = { 
        # 'inward_number': outward['inward_number'],
        # 'inward_date': outward['inward_date'],
        # 'inward_values':delivery_data,
        'inward_values':inwards,

       

        'gstin':gstin,
        'mobile':mobile,
        'customer_name':party_name,
        'program_details': program_details,
        'total_roll': total_bag,
        'total_quantity': total_gross,

        'inward_details': delivery_details,
        'company':company_table.objects.filter(status=1).first(),

        # 'program':program,
        'image_url':image_url,
        'remarks':remarks,
        # 'outward':outward_display,
        'po_number':po_number,
        # 'lot_no':lot_no,
        # 'previous_no':pre_qty if pre_qty else '-',


    } 

    return render(request, 'yarn_inward/inward_print.html', context)
# # Render template as HTML string
#     template = get_template('yarn_inward/inward_print.html')
#     html = template.render(context)

#     # Generate PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'inline; filename="yarn_inward.pdf"'
 
#     result = BytesIO()
#     pdf_status = pisa.CreatePDF(src=html, dest=result, link_callback=link_callback)

#     if not pdf_status.err:
#         response.write(result.getvalue())
#         return response
#     else:
#         return HttpResponse("PDF generation failed", status=500)






@csrf_exempt
def yarn_inward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        if not data_id:
            return JsonResponse({'message': 'Inward ID is required.'})

        try:
            # Get the inward entry
            inward = yarn_inward_table.objects.get(id=data_id)
            po_id = inward.po_id  # Can be None

            # Check for active delivery entries
            has_active_delivery = sub_yarn_deliver_table.objects.filter(
                inward_id=data_id
            ).exclude(status=0).exists()

            if has_active_delivery:
                return JsonResponse({
                    'message': 'Cannot delete: This inward is linked to an active delivery. Please delete the delivery first.'
                })

            # Check for active PO linkage
            # if po_id and parent_po_table.objects.filter(id=po_id, status=1, is_active=1).exists():
            #     return JsonResponse({
            #         'message': 'Cannot delete: This inward is linked to an active PO. Please delete the PO first.'
            #     })

            # Safe to soft-delete
            yarn_inward_table.objects.filter(id=data_id).update(status=0, is_active=0)
            sub_yarn_inward_table.objects.filter(tm_id=data_id).update(status=0, is_active=0)

            return JsonResponse({'message': 'yes'})

        except yarn_inward_table.DoesNotExist:
            return JsonResponse({'message': 'Inward entry not found.'})
        except Exception as e:
            print("Error during inward deletion:", e)
            return JsonResponse({'message': 'Error occurred during inward deletion.'})

    return JsonResponse({'message': 'Invalid request method'})


import base64

def inward_detail_edit(request):
    try:
        encoded_id = request.GET.get('id') 
        print('encoded-id:', encoded_id)

        if not encoded_id:
            return render(request, 'yarn_inward/yarn_inward_details.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID 
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode() 
            print('decoded-id:', decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'yarn_inward/yarn_inward_details.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
        print('material:', material_id)

        # Fetch the parent stock instance
        parent_stock_instance = yarn_inward_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'yarn_inward/yarn_inward_details.html', {'error_message': 'Parent stock not found.'})

        print('inw:', parent_stock_instance.id)

        # Fetch all sub-material instances (full list, not just one)
        material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        # material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        print('material_instances:', material_instances)





        # If no material instances found, you can create a new one if necessary
        if not material_instances.exists() and request.method == 'GET':
            return render(request, 'yarn_inward/yarn_inward_details.html', {
                'error_message': 'No material details found.',
                'parent_stock_instance': parent_stock_instance,
                'decode_id': parent_stock_instance.id,
            })



      
        # Fetch supplier name using supplier_id
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try: 
                supplier_obj = party_table.objects.get(id=parent_stock_instance.party_id, status=1)
                supplier_name = supplier_obj.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        if parent_stock_instance.po_id:
            try: 
                parent_po = parent_po_table.objects.get(id=parent_stock_instance.po_id, status=1)
                po_mill = parent_po.mill_id
                mill = party_table.objects.get(id=po_mill, status=1)

                mill_name = mill.name
            except party_table.DoesNotExist:
                mill_name = "-"

        # Fetch active products, supplier list, party list, and counts
        product = product_table.objects.filter(status=1)
        supplier = party_table.objects.filter(status=1)
        party = party_table.objects.filter(is_knitting=1, status=1)
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)
        mill_list = party_table.objects.filter(status=1).filter(is_mill=1) | party_table.objects.filter(status=1).filter(is_trader=1)

        # Prepare context for template
        context = {
            'material_instances': material_instances,
            'parent_stock_instance': parent_stock_instance,
            'product': product,
            'party': party,
            'supplier_id': supplier_name,
            'supplier': supplier,
            'count': count,
            'decode_id': parent_stock_instance.id,
            'program':program,
            'mill':po_mill,
            'mill_list':mill_list,
            'po_list': parent_po_table.objects.filter(status=1)
        }

        print('context values:', context)
        return render(request, 'yarn_inward/yarn_inward_details.html', context)

    except Exception as e:
        print('Exception:', e)
        return render(request, 'yarn_inward/yarn_inward_details.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


def update_yarn_inward_list(request):
    if request.method == 'POST': 
        master_id = request.POST.get('id')
        print('MASTER-ID:', master_id) 
 
        if master_id: 
            try:
                # Fetch child PO data
                child_data = sub_yarn_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)
                if child_data.exists():
                    # Calculate totals from child PO data
                    # total_quantity = child_data.aggregate(sum('quantity'))['quantity__sum'] or 0
                    # total_gross = child_data.aggregate(sum('gross_quantity'))['gross_quantity__sum'] or 0
                    
                    
                    from django.db.models import Sum

                    total_quantity = child_data.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                    total_gross = child_data.aggregate(total_gross=Sum('gross_quantity'))['total_gross'] or 0



                    print('tot-grs:',total_gross)
                    # Fetch data from parent PO table for tax_total, round_off, and grand_total
                  
 
                    # Format child PO data for response
                    data = list(child_data.values())
                    formatted_data = []
                    index = 0
                    for item in data: 
                        index += 1  
                    

                        formatted_data.append({
                            'action': '<button type="button" onclick="inward_detail_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit "></i></button> \
                                        <button type="button" onclick="inward_detail_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2 "></i></button>'.format(item['id'], item['id']),
                            'id': index,
                            'deliver_to': getItemNameById(party_table, item['party_id']), 
                            'product': getItemNameById(count_table, item['yarn_count_id']), 
                            'bag': item['bag'] if item['bag'] is not None else 0,
                            'per_bag': item['per_bag'] if item['per_bag'] is not None else 0,
                            'quantity': item['quantity'] if item['quantity'] is not None else 0,
                            'receive_no': item['receive_no'] or '-',
                            'receive_date': item['receive_date'] or '-',
                            'gross': item['gross_quantity'] if item['gross_quantity'] is not None else 0,
                            'status': '<span class="badge text-bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
                        })



                    formatted_data.reverse()

                    # Return data with the totals included 
                    return JsonResponse({
                        'data': formatted_data,
                        'total_quantity': total_quantity,
                        'total_gross': total_gross,
                    })
                else:
                    return JsonResponse({'error': 'Master purchase does not hold any data related to the child table'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Invalid request, missing ID parameter'})
    else:
        return JsonResponse({'error': 'Invalid request, POST method expected'})



from django.db.models import Q


from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime

def update_inward_item(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        master_id = request.POST.get('tm_id')
        product_id = request.POST.get('product_id')
        bag = request.POST.get('bag')
        per_bag = request.POST.get('per_bag')
        quantity = request.POST.get('quantity')
        receive_no = request.POST.get('receive_no')
        receive_date = request.POST.get('receive_date')
        gross_wt = request.POST.get('gross_wt')
        po_id = int(request.POST.get('po_id', 0) or 0)
        deliver_to = int(request.POST.get('deliver_to', 0) or 0)
        supplier_id = int(request.POST.get('supplier_id', 0) or 0)

        try:
            bag = Decimal(bag or '0')
            per_bag = Decimal(per_bag or '0')
            quantity = Decimal(quantity or '0')
            gross_wt = Decimal(gross_wt or '0')
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': f"Invalid number format: {str(e)}"})

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Missing master_id or product_id'})

        try:
            # Try updating existing record
            existing_item = sub_yarn_inward_table.objects.filter(
                tm_id=master_id,
                party_id=supplier_id,
                po_id=po_id,
                yarn_count_id=product_id
            ).first()

            if existing_item:
                existing_item.bag = bag
                existing_item.per_bag = per_bag
                existing_item.quantity = quantity
                existing_item.gross_quantity = gross_wt
                existing_item.updated_by = user_id
                existing_item.updated_on = datetime.now()
                existing_item.save()
            else:
                sub_yarn_inward_table.objects.create(
                    tm_id=master_id,
                    company_id=company_id,
                    cfyear=2025,
                    bag=bag,
                    per_bag=per_bag,
                    quantity=quantity,
                    gross_quantity=gross_wt,
                    po_id=po_id,
                    party_id=supplier_id,
                    yarn_count_id=product_id,
                    status=1,
                    is_active=1,
                    created_by=user_id,
                    updated_by=user_id,
                    created_on=datetime.now(),
                    updated_on=datetime.now(),
                )

            # Safely update master totals
            updated_totals = update_tm_table_totals_inward(master_id)
            if 'error' in updated_totals:
                return JsonResponse({'success': False, 'error_message': updated_totals['error']})

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def update_tm_table_totals_inward(master_id):
    try:
        qs = sub_yarn_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        if not qs.exists():
            return {'error': 'No active inward items found.'}

        # Use Django ORM's Sum aggregation
        totals = qs.aggregate(
            total_quantity=Sum('quantity'),
            total_gross=Sum('gross_quantity')
        )

        total_quantity = totals['total_quantity'] or Decimal('0')
        total_gross = totals['total_gross'] or Decimal('0')

        yarn_inward_table.objects.filter(id=master_id).update(
            total_quantity=total_quantity,
            gross_quantity=total_gross,
            updated_on=datetime.now()
        )

        return {
            'total_quantity': str(total_quantity),
            'total_gross': str(total_gross),
        }

    except Exception as e:
        return {'error': str(e)}
    

 
def inward_details_edit(request):
    if is_ajax and request.method == "POST": 
         frm = request.POST
    data = sub_yarn_inward_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])




def inward_detail_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            sub_yarn_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except sub_yarn_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


