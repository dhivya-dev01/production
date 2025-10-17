# from pyexpat import model
# from re import M
from pyexpat import model
from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
# from django.utils.translation import gettext_lazy as _
import os



class UppercaseModel(models.Model):
    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                value = getattr(self, field.name)
                if value is not None:
                    if "email" in field.name:
                        setattr(self, field.name, str(value).lower())
                    elif "password" in field.name:
                        continue
                    else:
                        setattr(self, field.name, str(value).upper())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True



 


class PartyCodeSeries(UppercaseModel):
    party_code = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.party_code = f"P{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.party_code = "P00001" 
        super().save(*args, **kwargs)  
 
    class Meta: 
        abstract = True 

class party_table(UppercaseModel):
    party_code = models.CharField(max_length=15)
    is_supplier = models.IntegerField()
    is_mill = models.IntegerField()
    is_knitting = models.IntegerField() 
    price_list_id = models.IntegerField(default=0)
    is_process = models.IntegerField()
    supply_items = models.CharField(max_length=50,null=True)
    is_compacting = models.IntegerField()
    is_cutting = models.IntegerField()  
    is_stiching = models.IntegerField()  
    is_ironing = models.IntegerField() 
    is_trader = models.IntegerField() 
    is_fabric = models.IntegerField()
    company_id = models.IntegerField()
    udyam_no = models.CharField(max_length=25)  
    phone = models.CharField(max_length=50) 
    mobile = models.CharField(max_length=50) 
    email = models.CharField(max_length=50)  
    nick_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    prefix = models.CharField(max_length=15,unique=True)
    latitude = models.CharField(max_length=50) 
    longitude = models.CharField(max_length=50)
    description = models.CharField(max_length=300)        
    gstin = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    pincode = models.IntegerField()
    state = models.CharField(max_length=50)
    state_code = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)  
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    # primary_technician_id=models.IntegerField(null=True,blank=True)
    class Meta:
        db_table="party" 


class party_ob_table(UppercaseModel):
    customer_id = models.IntegerField()
    year = models.IntegerField()
    opening_balance = models.IntegerField()
    closing_balance = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta: 
        db_table="party_ob"



class party_contact_table(UppercaseModel): 
    party_id = models.IntegerField(null=True)
    cp_name = models.CharField(max_length=50)
    cp_mobile = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    cp_email = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="party_contact"

 

class party_photo_table(UppercaseModel): 
    party_id = models.IntegerField(null=True)
    photo = models.ImageField(max_length=300,upload_to='photo/') 
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="party_photos"



class price_list_table(UppercaseModel):
    name = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="price_list"



class price_list_range_table(UppercaseModel):
    rate = models.DecimalField(max_digits=20,decimal_places=3)
    quality_id = models.IntegerField()
    style_id = models.IntegerField()
    size_id = models.IntegerField()
    price_list_id = models.IntegerField() 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="price_list_value"


class uom_table(UppercaseModel):
    name = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="uom"


class dia_table(UppercaseModel):
    name = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="dia"



class gauge_table(UppercaseModel):
    name = models.CharField(max_length=30)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="gauge"
 


class tex_table(UppercaseModel):
    name = models.CharField(max_length=30)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="tex"


 

class color_table(UppercaseModel):
    name = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="color"



class count_table(UppercaseModel):
    name = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="yarn_count"




class bag_table(UppercaseModel):
    name = models.CharField(max_length=20)
    wt = models.IntegerField()  
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="bag"



class fabric_table(UppercaseModel):
    name = models.CharField(max_length=30)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="fabric"



class fabric_program_table(UppercaseModel):
    name = models.CharField(max_length=20)
    fabric_id = models.IntegerField()  
    count_id = models.IntegerField()  
    gauge_id = models.IntegerField()  
    tex_id = models.IntegerField()   
    gray_gsm = models.IntegerField()  
    color_id = models.CharField(max_length=30)  
    dia_id = models.CharField(max_length=30)  
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="fabric_program"



class fabric_dia_table(UppercaseModel):
    dia = models.IntegerField()
    fabric_prg_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="fabric_dia"



class product_table(UppercaseModel):
    name = models.CharField(max_length=30)
    uom_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="yarn_product"



class tax_table(UppercaseModel):
    display_name = models.CharField(max_length=25)
    tax = models.IntegerField()
    name=models.CharField(max_length=20)
    hsn=models.CharField(max_length=15)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tax"




class item_group_table(UppercaseModel):
    name = models.CharField(max_length=30)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="item_group" 

 
class mx_item_table(UppercaseModel):
    name = models.CharField(max_length=30)
    item_group_id = models.IntegerField()
    hsn_code = models.CharField(max_length=25)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="mx_item"


# ````````````````` TASK ```````````````````````````````


class task_library_table(UppercaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    task_code = models.CharField(max_length=10)
    description = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    
    class Meta:
        db_table = "tasklibrary"




class followup_table(UppercaseModel):
    id = models.AutoField(primary_key=True)
    task_id = models.IntegerField()
    followup_date = models.DateField()
    followup_status = models.CharField(max_length=30)
    remarks = models.CharField(max_length=200)
    followed_by = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "followup"


class remarks_table(UppercaseModel):
    id = models.AutoField(primary_key=True)
    task_library_id = models.IntegerField()
    description = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    
    class Meta:
        db_table = "task_remarks" 




class task_table(UppercaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    task_library_id = models.IntegerField()
    employee_id = models.IntegerField(default=0)
    priority = models.CharField(max_length=30)
    task_status = models.CharField(max_length=50)
    total_count = models.IntegerField(default=1)
    task_date = models.DateField(null=True)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(default=0)
    updated_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    
    class Meta:
        db_table = "task" 




class email_settings_table(UppercaseModel):
    default_email = models.CharField(max_length=30)
    company_id = models.IntegerField()
    email_port=models.CharField(max_length=15)
    email_host=models.CharField(max_length=30)
    email_host_user = models.CharField(max_length=50)
    email_password = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField() 
    class Meta:
        db_table="email_settings"



class sms_table(UppercaseModel):
    company_id = models.IntegerField()
    sms_api_key = models.CharField(max_length=25)
    support_number = models.IntegerField()
    description = models.CharField(max_length=200,null=True,blank=True)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "sms"




class process_table(UppercaseModel):
    stage = models.CharField(max_length=30)
    tolerance = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="process"




class DebitSeries(UppercaseModel):
    debit_number = models.CharField(max_length=15, unique=True)
 
    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic(): 
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.debit_number = f"DR{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.debit_number = "DR00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True  


# class sub_voucher_table(UppercaseModel):
#     class Meta:
#         db_table= 'tx_voucher'


class debit_note_table(DebitSeries):
    voucher_type = models.CharField(max_length=50)
                                    
            # choices=[('debit_note', 'Debit Note'), ('credit_note', 'Credit Note'), ('payment', 'Payment'), ('receipt', 'Receipt')])
    supplier_id = models.IntegerField()  # Supplier or Customer ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Transaction Amount 
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Transaction Amount 
    date = models.DateField()  # Date of the voucher
    cfy = models.IntegerField()  # Financial Year
    company_id = models.IntegerField()
    po_id = models.IntegerField() 
    is_paid = models.IntegerField(default=0) 
    name = models.CharField(max_length=20)  
    process_type = models.CharField(max_length=30)
    is_complete = models.IntegerField()
    # reference_id = models.IntegerField(null=True, blank=True)  # Could be a PO ID, Invoice ID, etc.
    debit_status = models.CharField(max_length=50, default='Pending')  # Voucher status
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on = models.DateTimeField(auto_now_add=True)  # Timestamp
    created_by = models.IntegerField()  # User who created the voucher
    updated_on = models.DateTimeField(auto_now=True)  # Timestamp for last update
    updated_by = models.IntegerField()  # User who last updated the voucher
    class Meta: 
        # db_table="tm_voucher"
        db_table="tm_debit"




class Vouchernumber(UppercaseModel):
    voucher_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.voucher_number = f"V{str(last_instance.id + 1).zfill(6)}"
                else:
                    self.voucher_number = "V000001" 
        super().save(*args, **kwargs) 

    class Meta:
        abstract = True




# Voucher Types Constants
VOUCHER_TYPES = (
    ('receipt', 'Receipt'),        # Customer to Company Payment
    ('payment', 'Payment'),        # Company to Supplier Payment
    ('credit', 'Credit'),          # Company Credits to Customers
    ('debit', 'Debit'),            # Customer/Supplier Debit to Company
)

class Voucher(Vouchernumber):
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPES)  # Type of Voucher
    # customer_id = models.IntegerField()  # Customer (if applicable)
    supplier_id = models.IntegerField()  # Supplier (if applicable)
    company_id = models.IntegerField()  # Company details
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Voucher Amount
    remarks = models.TextField(null=True, blank=True)  # Any Additional Remarks
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)  # Creation Timestamp
    updated_on = models.DateTimeField(auto_now=True)  # Update Timestamp
    created_by = models.IntegerField() # The user who created the voucher
    updated_by = models.IntegerField() # The user who created the voucher
    payment_mode = models.CharField(max_length=50)
    payment_remarks = models.TextField()
    # BANK 
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=50)
    # transaction_reference = models.CharField(max_length=50)
    transaction_date = models.CharField(max_length=50)
    transaction_mode = models.CharField(max_length=50)
    # CHEQUE
    cheque_number = models.CharField(max_length=50) 
    cheque_date = models.DateField()
    class Meta:
        db_table="tm_voucher" 


class child_voucher_table(UppercaseModel):
    tm_voucher_id = models.IntegerField() #tm_voucher.id
    order_number = models.CharField(max_length=50)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2) 
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2) 
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(default=0) 
    updated_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    
    class Meta: 
        db_table = "tx_voucher"




class GFOrderNumber(UppercaseModel):
    po_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.po_number = f"PO{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.po_number = "PO00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True 




class gf_po_table(GFOrderNumber):
    purchase_date = models.DateField(null=False)
    company_id = models.IntegerField()
    supplier_id = models.IntegerField() 
    is_inward=models.IntegerField(default=0)
    is_deliver=models.IntegerField(default=0)
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    tax_total = models.DecimalField(max_digits=20,decimal_places=3)
    round_off = models.DecimalField(max_digits=20,decimal_places=3)
    grand_total = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    price_list = models.CharField(max_length=50)
    is_complete = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()    
    class Meta:
        db_table="tm_gf_po" 


class sub_gf_po_table(UppercaseModel):
    tm_po_id = models.IntegerField()  
    product_id = models.IntegerField()
    bag = models.IntegerField()
    bag_wt = models.IntegerField()
    cfy = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    total_amount = models.DecimalField(max_digits=20,decimal_places=2) 
    quantity = models.DecimalField(max_digits=20,decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_gf_po" 
 


class gf_delivery_table(UppercaseModel):
    tm_po_id = models.IntegerField() 
    company_name = models.CharField(max_length=30)
    knitting_id = models.IntegerField()
    # fabric_id = models.IntegerField()
    delivery_date = models.DateField() 
    bags = models.IntegerField() 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta:
        db_table="gf_delivery"



class GCFOrderNumber(UppercaseModel):
    po_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.po_number = f"PO{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.po_number = "PO00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True 




class gcf_po_table(GCFOrderNumber):
    purchase_date = models.DateField(null=False)
    company_id = models.IntegerField()
    supplier_id = models.IntegerField() 
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    tax_total = models.DecimalField(max_digits=20,decimal_places=3)
    round_off = models.DecimalField(max_digits=20,decimal_places=3)
    grand_total = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    price_list = models.CharField(max_length=50)
    is_complete = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()    
    class Meta:
        db_table="tm_gcf_po" 


class sub_gcf_po_table(UppercaseModel):
    tm_po_id = models.IntegerField() 
    product_id = models.IntegerField()
    count = models.IntegerField()
    gauge = models.IntegerField()
    dia = models.IntegerField()
    tex = models.IntegerField()
    rolls = models.IntegerField() 
    wt_per_roll = models.DecimalField(max_digits=20,decimal_places=2) 
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    total_amount = models.DecimalField(max_digits=20,decimal_places=2) 
    quantity = models.DecimalField(max_digits=20,decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_gcf_po" 
 


class gcf_delivery_table(UppercaseModel):
    tm_po_id = models.IntegerField() 
    company_name = models.CharField(max_length=30)
    knitting_id = models.IntegerField()
    fabric_id = models.IntegerField()
    delivery_date = models.DateField() 
    rolls = models.IntegerField() 
    wt_per_roll = models.IntegerField() 
    total_amount = models.DecimalField(max_digits=20,decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta:
        db_table="gcf_delivery"


 

class GCFPINumber(UppercaseModel):
    inward_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs): 
        if not self.id: 
            with transaction.atomic(): 
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.inward_number = f"IN{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.inward_number = "IN00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True  




class gcf_inward_table(GCFPINumber):
    inward_date = models.DateField(null=False)
    company_id = models.IntegerField() 
    supplier_id = models.IntegerField() 
    order_through_id = models.IntegerField(null=True) 
    lot_no = models.IntegerField(null=True) 
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    tax_total = models.DecimalField(max_digits=20,decimal_places=3)
    round_off = models.DecimalField(max_digits=20,decimal_places=3)
    grand_total = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    # price_list = models.CharField(max_length=150)
    is_complete = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta:
        db_table="tm_gcf_inward"


class sub_gcf_inward_table(UppercaseModel):
    tm_id = models.IntegerField() 
    po_id = models.IntegerField()  #parent table
    lot_no = models.IntegerField()
    product_id = models.IntegerField()  
    color_id = models.CharField(max_length=30)  
    count = models.IntegerField()
    gauge = models.IntegerField()
    tex = models.IntegerField() 
    gsm = models.IntegerField()
    dia = models.IntegerField() 
    rolls = models.DecimalField(max_digits=20,decimal_places=3)
    wt_per_roll = models.DecimalField(max_digits=20,decimal_places=3)
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    total_amount = models.DecimalField(max_digits=20,decimal_places=3) 
    rate = models.DecimalField(max_digits=20,decimal_places=3) 
    # price_list = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:   
        db_table="tx_gcf_inward" 



class DeliveryGCFNumberSeries(UppercaseModel):
    do_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic(): 
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.do_number = f"DO{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.do_number = "DO00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True 

 

class parent_gcf_delivery_table(DeliveryGCFNumberSeries): 
    delivery_date=models.DateField()  
    supplier_id = models.IntegerField()
    is_paid = models.IntegerField(default=0) 
    paid_amount = models.IntegerField(default=0) 
    is_inward = models.IntegerField(default=0) 
    lot_no=models.IntegerField() 
    po_id = models.CharField(max_length=15)
    quantity = models.IntegerField() 
    process_id=models.IntegerField(null=True)
    deliver_to = models.IntegerField()
    price_list = models.CharField(max_length=100)
    remarks = models.CharField(max_length=100)
    total_quantity = models.BigIntegerField()
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    total_tax = models.DecimalField(max_digits=20,decimal_places=3)
    grand_total = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="tm_gcf_delivery"

 

class child_gcf_delivery_table(UppercaseModel):
    tm_id = models.IntegerField() 
    lot_no = models.IntegerField()
    product_id = models.IntegerField()
    tm_po_id = models.IntegerField() 
    count_id = models.IntegerField()
    color_id = models.CharField(max_length=50) 
    gauge_id = models.IntegerField()
    tex_id = models.IntegerField()
    dia = models.IntegerField()
    rolls = models.DecimalField(max_digits=20,decimal_places=2)
    wt_per_roll = models.DecimalField(max_digits=20,decimal_places=2)
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    rate = models.DecimalField(max_digits=20,decimal_places=3)
    amount = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:  
        db_table="tx_gcf_delivery"



 



class cutting_entry_table(UppercaseModel):
    cutting_no = models.CharField(max_length=15)
    lot_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    inward_date = models.DateField(null=False)
    party_id = models.IntegerField()
    tm_cutting_prg_id = models.IntegerField()
    # prg_quantity = models.IntegerField() 
    quality_id = models.IntegerField(default=0)    
    style_id = models.IntegerField(default=0)
    fabric_id = models.IntegerField()
    total_wt = models.DecimalField(max_digits=20,decimal_places=3)

    total_pcs = models.DecimalField(max_digits=20,decimal_places=2)
    total_bundles = models.DecimalField(max_digits=20,decimal_places=2)
    total_dozen = models.DecimalField(max_digits=20,decimal_places=2)
    bundle_wt = models.DecimalField(max_digits=20,decimal_places=2)
    cutting_waste = models.DecimalField(max_digits=20,decimal_places=2)
    malai_waste = models.DecimalField(max_digits=20,decimal_places=2)
    damages = models.DecimalField(max_digits=20,decimal_places=2)
    folding_waste = models.DecimalField(max_digits=20,decimal_places=2)
    air_loss = models.DecimalField(max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta:
        db_table="tm_cutting_entry"
 

class sub_cutting_entry_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField()
    size_id = models.IntegerField()  
    # fabric_id = models.IntegerField()
    color_id = models.IntegerField()
    quantity = models.IntegerField()
    lot_no = models.CharField(max_length=20)
    work_order_no = models.CharField(max_length=20)
    # balance_qty = models.IntegerField()
    # original_qty = models.IntegerField()
    wt = models.DecimalField(max_digits=20, decimal_places=3)
    cutter = models.CharField(max_length=50)
    # barcode = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_cutting_entry" 
 

# accessory program





class AccessoryNumber(UppercaseModel):
    accessory_no = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs): 
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.accessory_no = f"AC{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.accessory_no = "AC00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True  



 
class accessory_program_table(AccessoryNumber):
    is_entry = models.IntegerField(default=0)
    company_id = models.IntegerField()
    quality_id = models.IntegerField(default=0) 
    style_id = models.IntegerField(default=0) 
    total_quantity = models.IntegerField()
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_accessory_program"


class sub_accessory_program_table(UppercaseModel):
    tm_id = models.IntegerField()
    program_type = models.CharField(max_length=50) 
    item_id = models.IntegerField()
    item_group_id = models.IntegerField()
    uom_id = models.IntegerField()
    product_pieces = models.IntegerField()
    acc_quality_id = models.IntegerField()
    acc_size_id = models.IntegerField()
    size_id = models.IntegerField()
    position = models.IntegerField()
    quantity = models.DecimalField(decimal_places=2,max_digits=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_accessory_program"  
 




class yarn_po_inward_table(UppercaseModel):
    tm_po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    yarn_count_id = models.IntegerField()
    supplier_name = models.CharField(max_length=50)
    tx_inward_id = models.IntegerField()
    tm_inward_id = models.IntegerField()
    is_inward = models.IntegerField()
    
    class Meta:
        db_table="yarn_inward"


 

class package_table(UppercaseModel):
    quality_id = models.IntegerField()
    style_id = models.IntegerField()
    size_id = models.CharField(max_length=15)
    per_box = models.IntegerField()
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "package"
