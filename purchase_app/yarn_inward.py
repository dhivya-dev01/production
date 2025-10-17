import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from software_app.models import *
from yarn.models import *
from program_app.models import *
from employee.models import *

from software_app.views import getItemNameById, getSupplier, is_ajax
from django.views.decorators.csrf import csrf_exempt

def yarn_inward(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        # supplier = party_table.objects.filter(Q(is_supplier=1) | Q(is_knitting=1)) 
        supplier = party_table.objects.filter(is_mill=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        last_purchase = yarn_inward_table.objects.order_by('-id').first()
        if last_purchase:
            inward_number = last_purchase.id + 1
        else:  
            inward_number = 1  # Default if no records exist
        po_list = parent_po_table.objects.filter(status=1)  #is_knitting_prg=1,
        program = knitting_table.objects.filter(status=1)
        count = count_table.objects.filter(status=1)
        return render(request,'knitting_deliver/yarn_inward.html',{'inward_number':inward_number,'supplier':supplier,'party':party,'product':product,'po_list':po_list
                                                                   ,'count':count,'program':program})
    else:
        return HttpResponseRedirect("/signin")


def get_knitting_programs(request):
    po_ids = request.GET.getlist('po_ids[]')  # Get selected PO IDs as a list

    programs = knitting_table.objects.filter(po_id__in=po_ids).values('id', 'lot_no')

    return JsonResponse({'programs': list(programs)}, safe=False)



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



@csrf_exempt
def add_yarn_inward(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')

        try:
            supplier_id = request.POST.get('supplier_id')
            lot_name = request.POST.get('lot_name') or '0'
            remarks = request.POST.get('remarks')
            prg_id = request.POST.get('prg_id')
            po_list = request.POST.get('po_list')
            inward_date = request.POST.get('inward_date')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]'))

            # Create Parent Inward Entry
            material_request = yarn_inward_table.objects.create( 
                inward_date=inward_date, 
                party_id=supplier_id, 
                cfyear=2025,
                po_id=po_list,
                # program_id=prg_id or 0, 
                company_id=company_id,
                total_quantity=0,
                gross_quantity=0, 
                remarks=remarks,
                created_by=user_id,
                created_on=timezone.now()
            )

            total_gross = Decimal('0.00')
            total_quantity = Decimal('0.00')
            po_deliver_map = {}
            inward_required = False

            for chemical in chemical_data:
                is_inward_raw = str(chemical.get('is_inward', '1')).strip()
                is_inward = int(is_inward_raw) if is_inward_raw.isdigit() else 1

                # Track if any row needs delivery
                if is_inward == 0:
                    inward_required = True

                tm_po_id = int(chemical.get('po_id') or 0) 
                deliver_id = chemical.get('deliver_id', 0)
                product_id = chemical.get('product_id')
                # receive_date = safe_date(chemical.get('receive_date'))
                raw_date = chemical.get('receive_date')
                print('r-date:', raw_date)
                receive_date = safe_date(raw_date) if raw_date else None


                receive_no = chemical.get('receive_no')
                delivered_bag = safe_decimal(chemical.get('bag'))
                delivered_quantity = safe_decimal(chemical.get('quantity'))
                gross_wt = safe_decimal(chemical.get('gross_wt'))

                # Store in inward table
                sub_yarn_inward_table.objects.create(
                    tm_id=material_request.id,
                    yarn_count_id=product_id,
                    po_id=po_list,
                
                    receive_no=receive_no or 0,
                    cfyear=2025,
                    company_id = company_id,
                    receive_date=receive_date,
                    party_id = supplier_id, 
                    outward_party_id=deliver_id if deliver_id else 0,
                    bag=delivered_bag,
                    per_bag=chemical.get('per_bag'),
                    quantity=delivered_quantity,
                    gross_quantity=gross_wt,
                    created_by=user_id,
                    created_on=datetime.now()
                )

                # # Mark yarn_po_delivery_table as inwarded only if is_inward == 0
                # if is_inward == 0 and deliver_id:
                #     yarn_po_delivery_table.objects.filter(tm_po_id=tm_po_id, id=deliver_id).update(is_inward=1)

                # # Track totals for summary
                total_gross += gross_wt
                total_quantity += delivered_quantity

                # if tm_po_id not in po_deliver_map:
                #     po_deliver_map[tm_po_id] = {'bags': Decimal('0.00'), 'quantity': Decimal('0.00')}
                # po_deliver_map[tm_po_id]['bags'] += delivered_bag
                # po_deliver_map[tm_po_id]['quantity'] += delivered_quantity

            # Update parent inward totals
            material_request.gross_quantity = total_gross
            material_request.total_quantity = total_quantity 
            material_request.save()
 

            # Create knitting delivery only if any entry had is_inward = 0
            if inward_required:
                try:
                    knitting_delivery = yarn_delivery_table.objects.create(
                        po_id=",".join([str(k) for k in po_deliver_map.keys()]),
                        company_id = company_id,
                        cfyear=2025,
                        delivery_date=inward_date,
                        program_id=prg_id,
                        party_id=supplier_id,
                        inward_id=str(material_request.id),
                        lot_no=lot_name,
                        total_quantity=total_quantity,
                        gross_quantity=total_gross,
                        remarks=remarks,
                        created_by=user_id,
                        created_on=datetime.now()
                    )

                    for chemical in chemical_data:
                        is_inward_raw = str(chemical.get('is_inward', '1')).strip()
                        is_inward = int(is_inward_raw) if is_inward_raw.isdigit() else 1

                        if is_inward == 0:
                            sub_yarn_deliver_table.objects.create( 
                                tm_id=knitting_delivery.id,
                                company_id =company_id,
                                cfyear=2025,
                                party_id=supplier_id,
                                lot_no=lot_name,
                                yarn_count_id=chemical.get('product_id'),
                                bag=safe_decimal(chemical.get('bag')),
                                inward_id=material_request.id,
                                per_bag=chemical.get('per_bag'),
                                gross_quantity=safe_decimal(chemical.get('gross_wt')),
                                quantity=safe_decimal(chemical.get('quantity')),
                                created_by=user_id,
                                created_on=datetime.now()
                            )
                except Exception as ke:
                    print(f"❌ Error creating knitting delivery: {ke}")

            return JsonResponse({'status': 'success', 'message': 'Added Successfully!'})

        # except Exception as e:
        #     print(f"❌ Error: {e}")
        #     return JsonResponse('no', safe=False)
        except Exception as e:
            print(f"❌ Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'knitting_deliver/yarn_inward.html')






def yarn_list(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']
        supplier = party_table.objects.filter(is_supplier=1)
        party = party_table.objects.filter(status=1)
        product = product_table.objects.filter(status=1)
        return render(request,'knitting_deliver/yarn_inward_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")
    

def yarn_inward_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read") 

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(yarn_inward_table.objects.filter(status=1).order_by('-id').values())

    formatted = [ 
        {
            'action': '<button type="button" onclick="po_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="yarn_inward_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button> '.format(item['id'],item['id']),
                        # <button type="button" onclick="po_print(\'{}\')" class="btn btn-success btn-xs"><i class="feather icon-printer"></i></button>'.format(item['id'],item['id'], item['id']),
            'id': index + 1, 
            'inward_no': item['inward_number'] if item['inward_number'] else'-', 
            'inward_date': item['inward_date'] if item['inward_date'] else'-', 
            'supplier_id':getSupplier(party_table, item['party_id'] ), 
            # 'yarn_count': get_yarn_count_by_tm_id(item['id']),
            'total_quantity': item['total_quantity'] if item['total_quantity'] else'-', 
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

def yarn_inward_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting 
            # parent_po_table.objects.filter(id=data_id)
            yarn_inward_table.objects.filter(id=data_id).update(status=0,is_active=0)

            sub_yarn_inward_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except yarn_inward_table & sub_yarn_inward_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


import base64

def inward_detail_edit(request):
    try:
        encoded_id = request.GET.get('id') 
        print('encoded-id:', encoded_id)

        if not encoded_id:
            return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'ID is missing.'})

        # Decode the base64-encoded ID
        try: 
            decoded_id = base64.urlsafe_b64decode(encoded_id.encode()).decode() 
            print('decoded-id:', decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'Invalid ID format.'})

        # Convert decoded_id to integer
        material_id = int(decoded_id)
        print('material:', material_id)

        # Fetch the parent stock instance
        parent_stock_instance = yarn_inward_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'Parent stock not found.'})

        print('inw:', parent_stock_instance.id)

        # Fetch all sub-material instances (full list, not just one)
        material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        # material_instances = sub_yarn_inward_table.objects.filter(tm_id=material_id)
        print('material_instances:', material_instances)





        # If no material instances found, you can create a new one if necessary
        if not material_instances.exists() and request.method == 'GET':
            return render(request, 'knitting_deliver/update_yarn_inward.html', {
                'error_message': 'No material details found.',
                'parent_stock_instance': parent_stock_instance,
                'decode_id': parent_stock_instance.id,
            })



        # if not material_instances.exists():
        #     if request.method == 'POST':
        #         product_id = request.POST.get('product_id') 
        #         bag = request.POST.get('bag')
        #         per_bag = request.POST.get('per_bag')
        #         quantity = request.POST.get('quantity')

        #         if product_id and bag and quantity: 
        #             new_material = sub_yarn_inward_table.objects.create(
        #                 tm_id=material_id,
        #                 yarn_count_id=product_id,
        #                 bag=bag,
        #                 per_bag=per_bag,
        #                 quantity=quantity,
        #             )
        #             material_instances = [new_material]  # create a list with the new entry
        #         else:
        #             return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'Product details are incomplete.'})

        # Fetch supplier name using supplier_id
        supplier_name = "-"
        if parent_stock_instance.party_id:
            try: 
                supplier_obj = party_table.objects.get(id=parent_stock_instance.party_id, status=1)
                supplier_name = supplier_obj.name
            except party_table.DoesNotExist:
                supplier_name = "-"

        # Fetch active products, supplier list, party list, and counts
        product = product_table.objects.filter(status=1)
        supplier = party_table.objects.filter(status=1)
        party = party_table.objects.filter(is_knitting=1, status=1)
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)

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
            'po_list': parent_po_table.objects.filter(status=1)
        }

        print('context values:', context)
        return render(request, 'knitting_deliver/update_yarn_inward.html', context)

    except Exception as e:
        print('Exception:', e)
        return render(request, 'knitting_deliver/update_yarn_inward.html', {'error_message': 'An unexpected error occurred: ' + str(e)})


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
                    total_quantity = child_data.aggregate(sum('quantity'))['quantity__sum'] or 0
                    total_gross = child_data.aggregate(sum('gross_quantity'))['gross_quantity__sum'] or 0
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
                            'bag': item['bag'] if item['bag'] else '-',
                            'per_bag': item['per_bag'] if item['per_bag'] else '-',
                            'quantity': item['quantity'] if item['quantity'] else '-',
                            'receive_no': item['receive_no'] if item['receive_no'] else '-',
                            'receive_date': item['receive_date'] if item['receive_date'] else '-',
                            'gross': item['gross_quantity'] if item['gross_quantity'] else '-',
                            # 'rate': item['rate'] if item['rate'] else '-',
                            # 'amount': item['amount'] if item['amount'] else '-',
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

def add_or_update_inward_item(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']

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
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # First, try to get existing record
            existing_item = sub_yarn_inward_table.objects.filter(
                tm_id=master_id,
                party_id=supplier_id,
                po_id=po_id,
                yarn_count_id=product_id
            ).first()

            if existing_item:
                # Update the existing record
                existing_item.bag = bag
                existing_item.per_bag = per_bag
                existing_item.quantity = quantity
                existing_item.gross_quantity = gross_wt
                existing_item.updated_by = user_id
                existing_item.updated_on = datetime.now()
                existing_item.save()
            else:
                # Create a new record
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

            # Update master totals
            updated_totals = update_tm_table_totals_inward(master_id)
            if 'error' in updated_totals:
                return JsonResponse({'success': False, 'error_message': updated_totals['error']})

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


def add_or_update_inward_item_8(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']

        master_id = request.POST.get('tm_id')
        print('tm-id:', master_id)
        product_id = request.POST.get('product_id')
        bag = request.POST.get('bag')
        per_bag = request.POST.get('per_bag')
        quantity = request.POST.get('quantity')
        receive_no = request.POST.get('receive_no')
        receive_date = request.POST.get('receive_date')
        gross_wt = request.POST.get('gross_wt')
        po_id = request.POST.get('po_list', 0)  # Default to 0 if not provided
        deliver_to = request.POST.get('deliver_to', 0)  # Default to 0 if not provided
        edit_deliver_to = request.POST.get('supplier_id', 0)  # Default to 0 if not provided
        print('sup-id:',edit_deliver_to)
        # Ensure po_id and deliver_to are integers, not empty strings
        po_id = int(po_id) if po_id else 0
        deliver_to = int(deliver_to) if deliver_to else 0

        # Convert string values to Decimal
        try:
            bag = Decimal(bag) if bag else Decimal('0') 
            per_bag = Decimal(per_bag) if per_bag else Decimal('0')
            quantity = Decimal(quantity) if quantity else Decimal('0')
            gross_wt = Decimal(gross_wt) if gross_wt else Decimal('0')
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': f"Invalid number format: {str(e)}"})

        if not master_id or not product_id:
            return JsonResponse({'success': False, 'error_message': 'Invalid data submitted'})

        try:
            # Add or update the child table record using tm_id (foreign key), not id
            child_item, created = sub_yarn_inward_table.objects.update_or_create(
                # tm_id=master_id,party_id=edit_deliver_to,receive_no=receive_no,
                tm_id=master_id,po_id=po_id,party_id=edit_deliver_to,
                yarn_count_id=product_id,
                defaults={
                    'company_id':company_id,
                    'cfyear':2025,
                    'bag': bag,
                    'po_id': po_id,  # Assign po_id, defaulting to 0 if empty
                    'party_id': edit_deliver_to,  # Assign deliver_to, defaulting to 0 if empty
                    'per_bag': per_bag,
                    'quantity': quantity,
                    'gross_quantity': gross_wt,
                    # 'receive_no':receive_no,
                    # 'receive_date':receive_date,
                    'status': 1,
                    'is_active': 1,
                    'created_by': user_id,
                    'updated_by': user_id,
                    'created_on': datetime.now(),
                    'updated_on': datetime.now(),
                }
            )

            # Mark the delivery entry as inwarded if po_id is present
            
            # Update master table totals
            updated_totals = update_tm_table_totals_inward(master_id)

            if 'error' in updated_totals:
                return JsonResponse({'success': False, 'error_message': updated_totals['error']})

            return JsonResponse({'success': True, **updated_totals})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
 
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


def update_tm_table_totals_inward(master_id):
    try:
        qs = sub_yarn_inward_table.objects.filter(tm_id=master_id, status=1, is_active=1)

        if not qs.exists():
            return {'error': 'No active inward items found.'}

        total_quantity = qs.aggregate(sum('quantity'))['quantity__sum'] or Decimal('0')
        total_gross = qs.aggregate(sum('gross_quantity'))['gross_quantity__sum'] or Decimal('0')
        tm = qs.first().tm_id

        yarn_inward_table.objects.filter(id=tm).update(
            total_quantity=total_quantity,
            gross_quantity=total_gross,
        )
 
        return {
            'total_quantity': total_quantity,
            'total_gross': total_gross,
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


