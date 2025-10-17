# from pyexpat import model
# from re import M
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




# ```````````````````````` folding delivery ``````````````````````````

class parent_folding_delivery_table(UppercaseModel):
    outward_no = models.CharField(max_length=15)
    lot_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    outward_date = models.DateField(null=False)
    party_id = models.IntegerField()
    stitching_outward_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    fabric_id= models.IntegerField()
    total_quantity = models.DecimalField(max_digits=20,decimal_places=3)
  
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta:
        db_table="tm_folding_outward"
 

class child_folding_delivery_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField() 
    # size_id = models.IntegerField()  
    color_id = models.IntegerField() 
    # quantity = models.IntegerField()
    party_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    stitching_outward_id = models.IntegerField()
    wt = models.DecimalField(max_digits=20,decimal_places=3) 
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_folding_outward" 


# `````````````````` stiching ``````````````````````



class parent_stiching_outward_table(UppercaseModel):
    outward_no = models.CharField(max_length=15)
    receive_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    is_packing = models.IntegerField() 
    company_id = models.IntegerField()
    outward_date = models.DateField(null=False)
    receive_date = models.DateField(null=False) 
    party_id = models.IntegerField()
    cutting_entry_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)  
    size_id = models.CharField(max_length=50)
    fabric_id= models.IntegerField()
    total_quantity = models.DecimalField(max_digits=20,decimal_places=2)
  
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta:
        db_table="tm_stiching_outward"  
 

class child_stiching_outward_table(UppercaseModel): 
    cfyear = models.CharField(max_length=15) 
    company_id = models.IntegerField()
    tm_id = models.IntegerField() 
    size_id = models.IntegerField()  
    color_id = models.IntegerField()
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    # dozen = models.DecimalField(max_digits=20,decimal_places=2)
    # pieces = models.DecimalField(max_digits=20,decimal_places=2) 
    party_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)    
    style_id = models.IntegerField(default=0)
    entry_id = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_stiching_outward" 
 



class cutting_entry_balance_table(models.Model):
    entry_id = models.IntegerField()
    inward_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    quality_id = models.IntegerField()
    quality_name = models.CharField(max_length=50)
    party_id =models.IntegerField()
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "cutting_entry_available_balance" 
 
 
class stiching_delivery_balance_table(models.Model):
    outward_id = models.IntegerField()
    outward_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    quality_id = models.IntegerField()
    style_id = models.IntegerField()
    quality_name = models.CharField(max_length=50) 
    party_id =models.IntegerField()
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "stiching_delivery_available_balance"
 
 


 
class stiching_folding_delivery_balance_table(models.Model):
    outward_id = models.IntegerField()
    outward_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    quality_id = models.IntegerField()
    style_id = models.IntegerField()
    quality_name = models.CharField(max_length=50) 
    party_id =models.IntegerField()
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "stitching_folding_outward_available_balance"
 
 


class parent_packing_outward_table(UppercaseModel):
    outward_no = models.CharField(max_length=15)
    # receive_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15) 
    company_id = models.IntegerField() 
    outward_date = models.DateField(null=False)
    # receive_date = models.DateField(null=False) 
    party_id = models.IntegerField()
    stiching_outward_id = models.IntegerField()
    inward_id = models.CharField(max_length=50)
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    fabric_id = models.IntegerField(default=0)
    total_quantity = models.DecimalField(max_digits=20,decimal_places=2)
  
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()   
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta:
        db_table="tm_packing_outward"
  

class child_packing_outward_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField()
    stiching_outward_id = models.IntegerField()
    inward_id = models.IntegerField()
    work_order_no = models.CharField(max_length=15)
    size_id = models.IntegerField()  
    color_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    quantity = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_packing_outward" 
 

class stiching_received_balance_table(models.Model):
    inward_id = models.IntegerField()
    inward_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    quality_id = models.IntegerField()
    quality_name = models.CharField(max_length=50)
    party_id =models.IntegerField() 
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "stiching_received_available_balance"

#  ````````````````````````````` received `````````````````````````````````````
 


class parent_stiching_inward_table(UppercaseModel):
    inward_no = models.CharField(max_length=15)
    dc_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    inward_date = models.DateField(null=False) 
    dc_date = models.DateField(null=False) 
    party_id = models.IntegerField()
    outward_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    fabric_id = models.IntegerField(default=0)
    style_id = models.IntegerField(default=0)
    total_quantity = models.DecimalField(max_digits=20,decimal_places=2)
  
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta:
        db_table="tm_stiching_inward"
 

class child_stiching_inward_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField() 
    quality_id = models.DecimalField(max_digits=20,decimal_places=2)  
    style_id = models.IntegerField()   
    size_id = models.IntegerField()  
    color_id = models.IntegerField()
    quantity = models.IntegerField()  
    # party_id = models.IntegerField()
    outward_id = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_stiching_inward" 
 




 
class parent_packing_inward_table(UppercaseModel):
    inward_no = models.CharField(max_length=15)
    dc_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField() 
    inward_date = models.DateField(null=False)
    dc_date = models.DateField(null=False)
    outward_id = models.IntegerField()
    party_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    fabric_id = models.IntegerField(default=0) 
    total_box = models.IntegerField()
    total_pcs = models.DecimalField(max_digits=20,decimal_places=2)
    per_box = models.IntegerField()
    # box_pcs = models.IntegerField()
    loose_pcs = models.IntegerField() 
    seconds_pcs = models.IntegerField()
    shortage_pcs = models.IntegerField()
    balance_pcs = models.DecimalField(max_digits=20,decimal_places=2)
    delivery_from = models.CharField(max_length=50)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()    
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta: 
        db_table="tm_packing_inward"



class child_packing_inward_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField()
    outward_id = models.IntegerField()
    size_id = models.IntegerField()  
    quality_id = models.IntegerField(default=0)    
    style_id = models.IntegerField(default=0)
    box = models.IntegerField() 
    box_pcs = models.IntegerField() 
    pcs_per_box = models.IntegerField()
    loose_pcs = models.IntegerField()
    seconds_pcs = models.IntegerField()
    shortage_pcs = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_packing_inward"  




class child_packing_inward_loose_pcs_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField() 
    outward_id = models.IntegerField()
    size_id = models.IntegerField()  
    # party_id = models.IntegerField() 
    color_id = models.IntegerField()
    quantity = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta:  
        db_table="tx_packing_inward_loose_pcs"  
 

#  ````````````````````````````````` LOOSE PIECE ENTRY ```````````````````````````````````


class parent_lp_entry_table(UppercaseModel):
    inward_no = models.CharField(max_length=15)
    inward_date = models.DateField(null=False)
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    party_id = models.IntegerField()
    packing_id = models.IntegerField() 
    is_damage = models.IntegerField()
    is_stitching = models.IntegerField()
    is_packing = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    fabric_id = models.IntegerField(default=0)
    total_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta:
        db_table="tm_lp_entry"
 


class child_lp_entry_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField() 
    tm_id = models.IntegerField() 
    size_id = models.IntegerField()  
    quality_id = models.IntegerField() 
    style_id = models.IntegerField() 
    color_id = models.IntegerField()
    quantity = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_lp_entry"
 


class packing_deivery_balance_table(models.Model):
    outward_id = models.IntegerField()
    outward_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    quality_id = models.IntegerField()
    quality_name = models.CharField(max_length=50)
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    in_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    class Meta:
        db_table = "packing_delivery_avaialble_balance"
 