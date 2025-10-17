from django.db import models
from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
# from django.utils.translation import gettext_lazy as _
import os


# Create your models here.



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





class dyed_fabric_po_table(UppercaseModel): 
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=50)
    lot_no = models.IntegerField(default=0,null=True,blank=True) 
    po_date = models.DateField(null=False)
    party_id = models.IntegerField()
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    program_id = models.IntegerField()
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    discount = models.DecimalField(max_digits=20,decimal_places=2) 
    net_rate = models.DecimalField(max_digits=20,decimal_places=2) 
   
    total_rolls = models.IntegerField()
    total_wt = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tm_dyed_fab_po"


class sub_dyed_fab_po_table(UppercaseModel):
    
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    dyeing_program_id = models.IntegerField() 
    knitting_program_id = models.IntegerField() 
    tm_id = models.IntegerField()
    fabric_id = models.IntegerField()
   
    color_id = models.IntegerField()
    dia_id = models.IntegerField()
    roll = models.IntegerField()
    roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tx_dyed_fab_po"
 



class grey_out_available_balance_table(models.Model):
    out_id = models.IntegerField()
    outward_no = models.CharField(max_length=15)
    lot_no = models.CharField(max_length=15)
    program_no = models.CharField(max_length=15) 
    program_id = models.IntegerField()
    party_id = models.IntegerField() 
    outward_wt = models.DecimalField(max_digits=20,decimal_places=2)
    inward_wt = models.DecimalField(max_digits=20,decimal_places=2)
    balance_wt = models.DecimalField(max_digits=20,decimal_places=2)

    class Meta:
        db_table ="grey_outward_available_balance"



# ```````````````` inward``````````````````



class dyed_fabric_inward_table(models.Model):
    inward_number = models.CharField(max_length=20)
    inward_date = models.DateField()
    dye_receive_no = models.CharField(max_length=20)
    dye_receive_date = models.DateField()
    lot_no = models.CharField(max_length=20)
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    outward_id = models.CharField(max_length=15,default=0)
    po_id = models.CharField(max_length=15,default=0)
    is_grey_fabric = models.IntegerField(default=0)
    is_dyed_fabric = models.IntegerField(default=0)
    party_id = models.IntegerField() 
    order_through_id = models.IntegerField() 
    program_id = models.IntegerField()
    total_roll = models.IntegerField()
    receive_no = models.CharField(max_length=20)
    receive_date = models.DateField()
    total_wt = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tm_dyed_fab_inward"
 



class sub_dyed_fabric_inward_table(models.Model):
    
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    tm_id = models.IntegerField()
    po_id = models.CharField(max_length=15)
    program_id = models.IntegerField()
    lot_no = models.CharField(max_length=15)
    fabric_id = models.IntegerField()
    dia_id = models.IntegerField()
    color_id = models.IntegerField()
    roll = models.IntegerField()
    roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    gross_wt = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tx_dyed_fab_inward"
 


class dyed_fab_po_balance_table(models.Model):
    po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_date = models.DateField()
    program_id = models.IntegerField()
    program_number = models.CharField(max_length=15)
    party_id = models.IntegerField()
    ord_roll_wt = models.DecimalField(max_digits=20,decimal_places=3) 
    po_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    in_quantity = models.DecimalField(max_digits=20,decimal_places=3) 
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    class Meta:
        db_table = "dyed_fab_po_balance"


class dyed_fab_program_balance_table(models.Model):
    program_id = models.IntegerField()
    fabric_id = models.IntegerField()
    color_id = models.IntegerField()
    program_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    in_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    class Meta:
        db_table = "dyed_fab_program_balance"




class dyed_fab_inw_available_wt_table(models.Model):
    fabric_id = models.IntegerField()
    dia_id = models.IntegerField()
    color_id = models.IntegerField()
    program_id = models.IntegerField()
    pg_roll = models.DecimalField(max_digits=20,decimal_places=2)
    pg_wt = models.DecimalField(max_digits=20,decimal_places=2)
    in_rolls = models.DecimalField(max_digits=20,decimal_places=2)
    in_wt = models.DecimalField(max_digits=20,decimal_places=2)
    in_gross_wt = models.DecimalField(max_digits=20,decimal_places=2)
    out_rolls = models.DecimalField(max_digits=20,decimal_places=2)
    out_wt = models.DecimalField(max_digits=20,decimal_places=2)
    balance_roll = models.DecimalField(max_digits=20,decimal_places=2)
    balance_wt = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table = 'dyed_fab_inward_available_wt'



 
class dyed_po_inward_balance_table(models.Model):
    fabric_id = models.IntegerField()
    dia_id = models.IntegerField()
    color_id = models.IntegerField()
    program_id = models.IntegerField()
    pg_roll = models.DecimalField(max_digits=20,decimal_places=2)
    pg_wt = models.DecimalField(max_digits=20,decimal_places=2)
    in_rolls = models.DecimalField(max_digits=20,decimal_places=2)
    in_wt = models.DecimalField(max_digits=20,decimal_places=2)
    out_rolls = models.DecimalField(max_digits=20,decimal_places=2)
    out_wt = models.DecimalField(max_digits=20,decimal_places=2)
    balance_roll = models.DecimalField(max_digits=20,decimal_places=2)
    balance_wt = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table = 'dyed_po_inward_balance'
