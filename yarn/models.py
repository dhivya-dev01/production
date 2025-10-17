from django.db import models

# Create your models here.

from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
# from django.utils.translation import gettext_lazy as _
import os

from django.forms import IntegerField
from pytz import timezone

from django.utils import timezone


class UppercaseModel(models.Model):
    """Base model to ensure CharField and TextField values are stored in uppercase, except emails (lowercase) and passwords (unchanged)."""
    
    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):  # Apply to CharField & TextField
                value = getattr(self, field.name)
                if value:  # Ensure value is not None
                    if "email" in field.name:  # Store emails in lowercase
                        setattr(self, field.name, value.lower())
                    elif "password" in field.name:  # Keep passwords unchanged
                        continue
                    else:  # Convert all other text fields to uppercase
                        setattr(self, field.name, value.upper())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True  # This model will not create a separate database table





# class Ponumber(UppercaseModel):
#     po_number = models.CharField(max_length=15, unique=True)

#     def save(self, *args, **kwargs):
#         if not self.id: 
#             with transaction.atomic():
#                 last_instance = self.__class__.objects.last()  
#                 if last_instance:
#                     self.po_number = f"PO{str(last_instance.id + 1).zfill(5)}"
#                 else:
#                     self.po_number = "PO00001" 
#         super().save(*args, **kwargs)  

#     class Meta: 
#         abstract = True 



class parent_po_table(models.Model):
    po_number = models.CharField(max_length=15)
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    name = models.CharField(max_length=50)
    po_date = models.DateField(null=False)
    mill_id = models.IntegerField()
    is_delivery = models.IntegerField(default=0) 
    party_id = models.IntegerField() 
    yarn_count_id = models.IntegerField()  
    bag = models.IntegerField()
    per_bag = models.IntegerField()
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    discount = models.DecimalField(max_digits=20,decimal_places=2) 
    net_rate = models.DecimalField(max_digits=20,decimal_places=2) 
    gross_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_yarn_po"



class child_po_table(UppercaseModel):
    tm_po_id = models.IntegerField()
    yarn_count_id = models.IntegerField()  
    bag = models.IntegerField()
    per_bag = models.IntegerField()
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    actual_rate = models.DecimalField(max_digits=20,decimal_places=2) 
    discount = models.DecimalField(max_digits=20,decimal_places=2) 
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    gross_wt = models.DecimalField(max_digits=20,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=3)
    remaining_bag = models.IntegerField()
    remaining_quantity = models.DecimalField(max_digits=20,decimal_places=2) 
    remaining_amount = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_purchase_order" 
 



class yarn_po_delivery_table(UppercaseModel):
    tm_po_id = models.IntegerField() 
    yarn_count_id = models.IntegerField() 
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    party_id = models.IntegerField()   # is_knitting=1
    delivery_date = models.DateField() 
    bag = models.IntegerField() 
    bag_wt = models.DecimalField(max_digits=20,decimal_places=2) 
    quantity = models.DecimalField(max_digits=20,decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="tx_yarn_po"









# `````````````````````` works ``````````````````````````


class yarn_po_delivery_sum_table(models.Model):
    po_id = models.IntegerField()
    tx_id = models.IntegerField()
    delivery_date = models.DateField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=15)
    party_id = models.IntegerField()
    party_name = models.CharField(max_length=50)
    yarn_count_id = models.IntegerField()
    po_bag = models.IntegerField()
    po_bag_wt = models.DecimalField(max_digits=22,decimal_places=2)
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    
    class Meta:
        db_table = "y_po_sum"
 
# ````````````````````````````
class yarn_po_sum_table(models.Model):
    po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=50)
    po_date = models.DateField()
    yarn_count_id = models.IntegerField()
    yarn_count_name = models.CharField(max_length=50)
    party_id = models.IntegerField()
    bags = models.IntegerField()
    bag_wt = models.DecimalField(max_digits=22,decimal_places=2)
    quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_bag = models.IntegerField()
    in_bag_wt = models.DecimalField(max_digits=22,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "yarn_po_sum"

class yarn_po_balance_table(models.Model):
    po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=50)
    yarn_count_id = models.IntegerField()
    yarn_count_name = models.CharField(max_length=50)
    party_id =models.IntegerField()
    ord_bags =models.DecimalField(decimal_places=2,max_digits=20)
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_bag = models.IntegerField()
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "yarn_po_balance"
 
 
# ``````````````````````````````


class yarn_out_sum_table(models.Model): 
    party_id = models.IntegerField() 
    po_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    po_bags =models.DecimalField(max_digits=20,decimal_places=2)
    bag_wt =models.DecimalField(max_digits=20,decimal_places=2)
    out_bags =models.DecimalField(max_digits=20,decimal_places=2)
    remaining_bags = models.DecimalField(max_digits=20,decimal_places=2)
    po_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    out_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    remaining_quantity = models.DecimalField(max_digits=20,decimal_places=2)

    class Meta:
        db_table = "yarn_out_sum"



# ````````````````````````

class yarn_inward_available(models.Model):
    po_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    inward_id = models.IntegerField()
    inward_number = models.CharField(max_length=15)
    in_bags = models.DecimalField(max_digits=20,decimal_places=2)
    out_bags = models.DecimalField(max_digits=20,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    out_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    available_bags = models.DecimalField(max_digits=20,decimal_places=2)
    available_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table="yarn_inward_available"




class yarn_out_balance_table(models.Model):
    party_id = models.IntegerField()
    po_id = models.IntegerField() 
    yarn_count_id = models.IntegerField()
    po_bags = models.DecimalField(max_digits=20,decimal_places=2)  
    bag_wt = models.DecimalField(max_digits=20,decimal_places=2)
    remaining_bags = models.DecimalField(max_digits=20,decimal_places=2)
    po_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    out_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    remaining_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    inward_id = models.IntegerField()  
    inward_number = models.CharField(max_length=15)
    available_bags = models.DecimalField(max_digits=20,decimal_places=2)
    available_quantity = models.DecimalField(max_digits=20,decimal_places=2)


    class Meta:
        db_table = "yarn_out_balance"
 
# ````````````````````````

# without any views
class yarn_program_balance_table(models.Model):
    program_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    program_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    out_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table="yarn_program_balance"




# `````````````````````````````````` end views models ``````````````````````````````````

class yarn_inward_balance_table(models.Model):
    inward_id = models.IntegerField()
    inward_number = models.CharField(max_length=15)
    yarn_count_id = models.IntegerField()
    yarn_count_name = models.CharField(max_length=50)
    party_id =models.IntegerField()
    knitting_id =models.IntegerField()
    knitting_number =models.CharField(max_length=15)
    knit_yarn_count_id =models.IntegerField()
    in_bags =models.DecimalField(decimal_places=2,max_digits=20)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    out_bag = models.IntegerField()
    out_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_bags = models.DecimalField(max_digits=22,decimal_places=2)
    knitting_balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "yarn_inward_balance"
 

class yarn_in_balance_table(models.Model): 
    # id = models.IntegerField()
    po_id = models.IntegerField()
    inward_id = models.IntegerField() 
    po_number = models.CharField(max_length=15)
    party_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    po_bag = models.IntegerField()
    po_bag_wt = models.DecimalField(max_digits=20,decimal_places=2)
    po_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    total_in_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    total_out_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    balance_in_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table = "yarn_in_balance"






 



class program_sum_table(models.Model): 
    po_id = models.IntegerField()
    inward_id = models.IntegerField()
    knitting_id = models.IntegerField() 
    knitting_number = models.CharField(max_length=15)
    party_id = models.IntegerField()
    count_id = models.IntegerField()
    balance_knit_quantity = models.DecimalField(max_digits=20,decimal_places=2)

    # yarn_count_id = models.IntegerField()

    class Meta:
        db_table = "program_sum"





class PINumber(UppercaseModel):
    inward_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.inward_number = f"PI{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.inward_number = "PI00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True 




class yarn_inward_table(models.Model):
    inward_number = models.CharField(max_length=15)
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    inward_date = models.DateField(null=False)
    company_id = models.IntegerField()
    party_id = models.IntegerField() # is_mill=1
    po_id = models.IntegerField()
    total_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    gross_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_yarn_inward" 

  
class sub_yarn_inward_table(UppercaseModel):
    company_id = models.IntegerField()
    cfyear = models.IntegerField() 
    tm_id = models.IntegerField() 
    po_id = models.IntegerField()  #parent table
    party_id = models.IntegerField()  # is_mill=1
    outward_party_id = models.IntegerField()  # is_knitting=1
    program_id = models.IntegerField()
    lot_no = models.CharField(max_length=15)
    yarn_count_id = models.IntegerField()  
    bag = models.IntegerField()
    per_bag = models.DecimalField(max_digits=20,decimal_places=3) 
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    gross_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    receive_no = models.CharField(max_length=20)
    receive_date = models.DateField()
    # lot_name = models.CharField(max_length=50)
    
    class Meta: 
        db_table="tx_yarn_inward"


# yarn deliver


class yarn_delivery_table(UppercaseModel): 
    do_number = models.CharField(max_length=15)
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    receive_date=models.DateField()  
    receive_no = models.CharField(max_length=20)
    delivery_date=models.DateField()  
    lot_no=models.CharField(max_length=15,default=0) 
    # lot_no = models.IntegerField(default=0,null=True,blank=True)
    inward_id = models.CharField(max_length=20) 
    program_id = models.IntegerField() 
    party_id = models.IntegerField()
    remarks = models.CharField(max_length=100)
    total_quantity = models.IntegerField()
    gross_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField(default=timezone.now)
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="tm_yarn_outward"

   

class sub_yarn_deliver_table(UppercaseModel): 
    company_id = models.IntegerField() 
    cfyear = models.IntegerField()
    tm_id = models.IntegerField()
    yarn_count_id = models.IntegerField()  # <= yarn count id (from count_table)
    program_id = models.IntegerField()
    inward_id = models.IntegerField()
    po_id = models.IntegerField()
    po_tx_id = models.IntegerField()
    # receive_date = models.DateField()
    party_id = models.IntegerField()
    bag = models.DecimalField(max_digits=20,decimal_places=2)
    per_bag = models.DecimalField(max_digits=20,decimal_places=2)
    quantity = models.IntegerField()
    gross_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField(default=timezone.now)
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta:   
        db_table="tx_yarn_outward" 






# ``````````````````````````````````````````````````````````````