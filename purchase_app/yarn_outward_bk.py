

import datetime
import json
from time import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
# from software_app.models import count_table, knitting_table, parent_po_table, party_table, product_table, sub_yarn_deliver_table, sub_yarn_inward_table, yarn_delivery_table, yarn_inward_table
from software_app.models import *

from software_app.views import getItemNameById, getSupplier, is_ajax
from django.views.decorators.csrf import csrf_exempt



def yarn_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id'] 
        supplier = party_table.objects.filter(is_supplier=1)
        # party = party_table.objects.filter(status=1)
        party = party_table.objects.filter(status=1,is_knitting=1)
        product = product_table.objects.filter(status=1)
        return render(request,'yarn_outward/yarn_outward_list.html',{'supplier':supplier,'party':party,'product':product})
    else:
        return HttpResponseRedirect("/signin")


def yarn_delivery_list(request):
    company_id = request.session['company_id']
    print('company_id:',company_id)
    # user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "customer", "read")

    # if not has_access:
    #     return JsonResponse({'data':[],'message': 'error', 'error_message': error_message}) 



                        # <button type="button" onclick="knitting_print(\'{}\')" class="btn btn-dark btn-xs"><i class="feather icon-printer"></i></button> 
    data = list(yarn_delivery_table.objects.filter(status=1).order_by('-id').values())
    
    formatted = [
        {
            'action': '<button type="button" onclick="yarn_deliver_edit(\'{}\')" class="btn btn-primary btn-xs"><i class="feather icon-edit"></i></button> \
                        <button type="button" onclick="yarn_deliver_delete(\'{}\')" class="btn btn-danger btn-xs"><i class="feather icon-trash-2"></i></button>'.format(item['id'], item['id']),
            'id': index + 1, 
            'deliver_date': item['delivery_date'].strftime('%d-%m-%Y') if isinstance(item.get('delivery_date'), date) else '-',
            'deliver_no': item['do_number'] if item['do_number'] else'-', 
            'quantity': item['total_quantity'] if item['total_quantity'] else'-', 
            'lot_no': item['lot_no'] if item['lot_no'] else'-', 
            'gross_total': item['gross_quantity'] if item['gross_quantity'] else'-', 
            # 'total_tax': item['total_tax'] if item['total_tax'] else'-', 
            # 'grand_total': item['grand_total'] if item['grand_total'] else'-', 
            'deliver_to': getSupplier(party_table, item['party_id'] ), 
            'prg':getSupplier(knitting_table, item['program_id'] ), 
            'status': '<span class="badge bg-success">active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>',
 
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted}) 
 


def knitting_delivery(request):
    if 'user_id' in request.session: 
        user_id = request.session['user_id']

        process = process_table.objects.filter(status=1, stage__in=['bleaching', 'dyeing','knitting','inhouse'])
        deliver = party_table.objects.filter(is_knitting=1, status=1)

        last_purchase = gf_delivery_table.objects.order_by('-id').first()
        delivery_number = last_purchase.id + 1 if last_purchase else 1

        party = party_table.objects.filter(status=1, is_knitting=1) 
        bag = bag_table.objects.filter(status=1) 
        count = count_table.objects.filter(status=1)
        program = knitting_table.objects.filter(status=1)   

        # # --- Execute custom SQL to get filtered inward_list ---
        # with connection.cursor() as cursor:
        #     cursor.execute("""
        #         SELECT y.* 
        #         FROM tm_yarn_inward y
        #         LEFT JOIN (
        #             SELECT inward_id, SUM(total_quantity) AS delivered_quantity
        #             FROM tm_yarn_deliver
        #             WHERE inward_id IS NOT NULL
        #             GROUP BY inward_id
        #         ) kd ON y.id = kd.inward_id
        #         WHERE y.status = 1
        #         AND (
        #             kd.inward_id IS NULL
        #             OR kd.delivered_quantity < y.total_quantity
        #         )
        #     """)
        #     columns = [col[0] for col in cursor.description]
        #     inward_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render(request, 'knitting_deliver/add_knitting_deliver.html', {
            'knitting': knitting, 
            'process': process, 
            'party': party,
            'deliver': deliver,
            'delivery_number': delivery_number,
            # 'inward_list': inward_list,
            'bag': bag,
            'count': count,
            'program': program
        })
    else:
        return HttpResponseRedirect("/signin")








@csrf_exempt
def check_duplicate_lot_no(request):
    if request.method == "POST":
        lot_no = request.POST.get('lot_no', '').strip().upper()

        # Check if the item already exists in the same group
        exists = yarn_delivery_table.objects.filter(lot_no=lot_no,status=1).exists()
 
        return JsonResponse({"exists": exists})




def add_knitting_delivery(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        try: 
            # Extracting data from the request
            do_date = request.POST.get('delivery_date') 
            supplier_id = request.POST.get('party_id') 
            lot_no = request.POST.get('lot_no')
            tx_inward = request.POST.get('inward_id')
            knitting_prg_id = request.POST.get('prg_id')
            # po_id = request.POST.get('po_id')
            deliver_id = request.POST.get('party_id')
            remarks = request.POST.get('remarks')
            # quantity = request.POST.get('quantity') 
            process_id = request.POST.get('process_id')
            chemical_data = json.loads(request.POST.get('chemical_data', '[]')) 

            print('data:',chemical_data)
            # Get PO IDs
            po_ids = request.GET.getlist('po_id[]')  
            po_ids_str = ",".join(po_ids)
            tx_inward_str = ",".join([str(i) for i in tx_inward])  # Convert to string

            # Create a new entry in yarn_delivery_table (Parent table)
            material_request = yarn_delivery_table.objects.create(
                company_id=company_id,
                cfyear = 2025,
                delivery_date=do_date,
                party_id=deliver_id,
                program_id=knitting_prg_id,
                inward_id=tx_inward_str,
                lot_no=lot_no,
                total_quantity= 0,#request.POST.get('total_quantity',0.0),
                gross_quantity=0, # request.POST.get('sub_total',0.0),
              
                remarks=remarks,
                created_by=user_id,
                created_on=datetime.now()
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
                    created_on=datetime.now()
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
            print('knt-deliver',True)
            # parent_po_table.objects.filter(id__in=po_ids).update(is_knitting_delivery=1)

            return JsonResponse('yes', safe=False)  # Indicate success

        except Exception as e:
            print(f"❌ Error: {e}")  # Log error for debugging
            return JsonResponse('no', safe=False)  # Indicate failure

    return render(request, 'knitting_deliver/add_knitting_deliver.html')



def yarn_deliver_edit(request):
    try:
        encoded_id = request.GET.get('id')
        if not encoded_id:
            return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'ID is missing.'})

        # Ensure valid Base64 padding before decoding
        try:
            decoded_id = base64.urlsafe_b64decode(encoded_id + '=' * (-len(encoded_id) % 4)).decode()
            material_id = int(decoded_id)
        except (ValueError, TypeError, base64.binascii.Error):
            return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'Invalid ID format.'})

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
                return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'Product details are incomplete.'})

        # Fetch the parent stock instance
        parent_stock_instance = yarn_delivery_table.objects.filter(id=material_id).first()
        if not parent_stock_instance:
            return render(request, 'knitting_deliver/update_deliver.html', {'error_message': 'Parent stock not found.'})

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
            'party': party_table.objects.filter(is_knitting=1, status=1),
            'program': knitting_table.objects.filter(status=1),
            'supplier_id': supplier_name,  
            'supplier': party_table.objects.filter(status=1), 
            'process': process_table.objects.filter(status=1),
            'stage': process_table.objects.filter(stage='Yarn', status=1).first(), 
            'po': parent_po_table.objects.filter(status=1),
            'count':count,
            'inward_lists':yarn_inward_table.objects.filter(status=1)
        }

        return render(request, 'knitting_deliver/update_deliver.html', context)

    except Exception as e:
        logger.error(f"Error in yarn_deliver_edit: {e}") 
        return render(request, 'knitting_deliver/update_deliver.html', {'error_message': f'An unexpected error occurred: {str(e)}'})

 




def yarn_deliver_delete(request):
    user_type = request.session.get('user_type')
    # has_access, error_message = check_user_access(user_type, "Purchase-order", "delete")

    # if not has_access:
    #     return JsonResponse({'message': 'error', 'error_message': error_message}, status=403)


    if request.method == 'POST':
        data_id = request.POST.get('id')
        try:
            # Update the status field to 0 instead of deleting
            yarn_delivery_table.objects.filter(id=data_id).update(status=0,is_active=0)
            sub_yarn_deliver_table.objects.filter(tm_id=data_id).update(status=0,is_active=0)
            return JsonResponse({'message': 'yes'})
        except yarn_delivery_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    




def tx_yarn_deliver_list(request):
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



 
def tx_yarn_deliver_delete(request):
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
    
