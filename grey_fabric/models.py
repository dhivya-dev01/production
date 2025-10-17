from django.db import models
from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
# from django.utils.translation import gettext_lazy as _
import os

# from program_app import program
from software_app.views import fabric

# Create your models here.




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






class grey_fabric_po_table(UppercaseModel): 
    po_number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    lot_no = models.IntegerField(default=0,null=True,blank=True) 
    po_date = models.DateField(null=False)
    # knitting_id = models.IntegerField()
    party_id = models.IntegerField()
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    # fabric_id = models.IntegerField()
    program_id = models.IntegerField()
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    discount = models.DecimalField(max_digits=20,decimal_places=2) 
    net_rate = models.DecimalField(max_digits=20,decimal_places=2) 
    # yarn_count_id = models.IntegerField() 
    # gauge_id = models.IntegerField() 
    # tex_id = models.IntegerField()
    # gsm = models.IntegerField()
    total_roll = models.IntegerField()
    total_roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    # quantity = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_delivery = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tm_grey_fab_po"





class grey_fabric_po_program_table(UppercaseModel):
    
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    program_id = models.IntegerField() 
    po_id = models.IntegerField()
    fabric_id = models.IntegerField()
    yarn_count_id = models.IntegerField() 
    gauge_id = models.IntegerField() 
    tex_id = models.IntegerField()
    dia_id = models.IntegerField()
    gsm = models.IntegerField()
    rolls = models.IntegerField()
    roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tx_grey_fab_po_program"
 
class sub_grey_fabric_po_table(UppercaseModel):
    po_id = models.IntegerField() 
    # fabric_id = models.IntegerField() 
    # dia_id = models.IntegerField() 
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    party_id = models.IntegerField()   # is_process=1
    delivery_date = models.DateField() 
    # roll = models.IntegerField() 
    roll_wt = models.DecimalField(max_digits=20,decimal_places=2) 
    # quantity = models.DecimalField(max_digits=20,decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="tx_grey_fab_po"

# ``````````````````` query ```````````````````````````````````//

class grey_fab_po_sum_table(models.Model):
    tx_id = models.IntegerField()
    po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=15)
    po_date = models.DateField()
    program_id = models.IntegerField()
    program_number = models.CharField(max_length=15)
    party_id = models.IntegerField() 
    party_name = models.CharField(max_length=20)
    fabric_id = models.IntegerField()
    fabric_name = models.CharField(max_length=20)
    rolls = models.IntegerField()
    roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    quantity = models.DecimalField(max_digits=20,decimal_places=3)
    in_roll = models.DecimalField(max_digits=20,decimal_places=3)
    in_roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    in_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    class Meta:
        db_table="grey_fab_po_sum"
    



class grey_fab_po_balance_table(models.Model):
    po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=15)
    po_date = models.DateField()
    program_id = models.IntegerField()
    program_number = models.CharField(max_length=15)
    # fabric_id = models.IntegerField()
    party_id = models.IntegerField()
    ord_roll_wt = models.DecimalField(max_digits=20,decimal_places=3)
    # ord_rolls = models.DecimalField(max_digits=20,decimal_places=3)
    po_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    in_rolls = models.DecimalField(max_digits=20,decimal_places=3)
    in_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    class Meta:
        db_table="grey_fab_po_balance"
    


class grey_fab_program_balance_table(models.Model):
    program_id = models.IntegerField()
    fabric_id = models.IntegerField()
    program_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    out_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    class Meta:
        db_table = "grey_fab_program_balance"




class grey_fab_po_delivery_table(models.Model):
    po_id = models.IntegerField()
    tx_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=15)
    party_id = models.IntegerField()
    fabric_id = models.IntegerField()
    party_name = models.CharField(max_length=50)
    yarn_count_id = models.IntegerField()
    po_roll = models.IntegerField()
    po_roll_wt = models.DecimalField(max_digits=22,decimal_places=2)
    po_quantity = models.DecimalField(max_digits=22,decimal_places=2)
    
    class Meta: 
        db_table = "grey_fab_po_delivery"

# `````````````````````````````` end  query ``````````````````````````````

class gf_inward_table(UppercaseModel):
    inward_number = models.CharField(max_length=15)
    inward_date = models.DateField(null=False)
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    po_id = models.IntegerField() 
    program_id = models.IntegerField()
    outward_id = models.CharField(max_length=15,default=0) 
    party_id = models.IntegerField()  
    receive_no = models.CharField(max_length=15)  
    receive_date = models.DateField()  
    lot_no = models.CharField(max_length=15) 
    total_wt = models.DecimalField(max_digits=20,decimal_places=3)
    total_gross_wt = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_gf_inward"

  
class sub_gf_inward_table(UppercaseModel):
    tm_id = models.IntegerField() 
    party_id = models.IntegerField()
    # outward_party_id = models.IntegerField()
    program_id = models.IntegerField()
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    po_id = models.IntegerField(default=0)  #parent table
    # outward_id = models.IntegerField()
    lot_no = models.CharField(max_length=20) 
    # receive_no = models.IntegerField() 
    # receive_date = models.DateField() 
    fabric_id = models.IntegerField()  
    yarn_count_id = models.IntegerField()
    gauge_id = models.IntegerField() 
    tex_id = models.IntegerField()
    dia_id = models.IntegerField()
    gsm = models.IntegerField()
    roll = models.DecimalField(max_digits=20,decimal_places=3)
    wt_per_roll = models.DecimalField(max_digits=20,decimal_places=3)
    total_wt = models.DecimalField(max_digits=20,decimal_places=2)
    gross_wt = models.DecimalField(max_digits=20,decimal_places=2)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:   
        db_table="tx_gf_inward"





class yarn_outward_available_wt_table(models.Model):
    fabric_id = models.IntegerField()
    dia_id = models.IntegerField()
    program_id = models.IntegerField()
    pg_roll = models.DecimalField(max_digits=20,decimal_places=2)
    pg_wt = models.DecimalField(max_digits=20,decimal_places=2)
    in_rolls = models.DecimalField(max_digits=20,decimal_places=2)
    in_wt = models.DecimalField(max_digits=20,decimal_places=2)
    balance_roll = models.DecimalField(max_digits=20,decimal_places=2)
    balance_wt = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table = 'yarn_outward_available_wt'






class grey_fab_dyeing_program_balance(models.Model):
    program_id = models.IntegerField()
    fabric_id = models.IntegerField()
    dia_id = models.IntegerField()
    color_id = models.IntegerField()
    program_wt = models.DecimalField(max_digits=20,decimal_places=2)
    out_wt = models.DecimalField(max_digits=20,decimal_places=2)
    balance_wt = models.DecimalField(max_digits=20,decimal_places=2)
    class Meta:
        db_table="grey_fab_dyeing_program_balance"


class grey_fabric_available_inward_table(models.Model):
    fabric_id = models.IntegerField()
    dia_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    tex_id = models.IntegerField()
    gauge_id = models.IntegerField()
    gsm = models.IntegerField()
    inward_id = models.IntegerField() 
    inward_number = models.CharField(max_length=15) 
    lot_no = models.CharField(max_length=15)
    in_rolls = models.DecimalField(decimal_places=2,max_digits=20)
    in_wt = models.DecimalField(decimal_places=2,max_digits=20)
    out_rolls = models.DecimalField(decimal_places=2,max_digits=20)
    out_wt = models.DecimalField(decimal_places=2,max_digits=20)
    available_rolls = models.DecimalField(decimal_places=2,max_digits=20)
    available_wt = models.DecimalField(decimal_places=2,max_digits=20)

    class Meta:
        db_table ="grey_fab_available_inward"



class parent_gf_delivery_table(UppercaseModel): 
    do_number = models.CharField(max_length=15)
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    delivery_date=models.DateField()   
    lot_no=models.CharField(max_length=15,default=0) 
    party_id = models.IntegerField() 
    knitting_program_id = models.IntegerField()
    dyeing_program_id = models.IntegerField()
    fabric_id = models.IntegerField()
    color_id = models.CharField(max_length=15)
    inward_id=models.IntegerField(null=True)
    remarks = models.CharField(max_length=100)
    total_wt = models.BigIntegerField() 
    gross_wt = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tm_gf_delivery"


class child_gf_delivery_table(UppercaseModel):
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    tm_id = models.IntegerField() 
    knitting_program_id = models.IntegerField()
    dyeing_program_id = models.IntegerField()
    color_id = models.IntegerField()
    party_id = models.IntegerField()
    inward_id = models.IntegerField()
    fabric_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    gauge_id = models.IntegerField()
    tex_id = models.IntegerField()
    gsm = models.IntegerField()
    dia_id = models.IntegerField()
    lot_no = models.CharField(max_length=15)
    roll = models.DecimalField(max_digits=20,decimal_places=2)
    roll_wt = models.DecimalField(max_digits=20,decimal_places=2)
    gross_wt = models.DecimalField(max_digits=20,decimal_places=2)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tx_gf_delivery"



class sub_child_gf_delivery_detail_table(UppercaseModel):
    company_id = models.IntegerField()
    cfyear = models.IntegerField()
    tm_id = models.IntegerField() 
    
    party_id = models.IntegerField()
    remarks = models.CharField(max_length=15)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta: 
        db_table="tx_gf_delivery_party"



class grey_outward_available_sum_table(models.Model):
    out_id = models.IntegerField()
    outward_no = models.CharField(max_length=20)
    lot_no = models.CharField(max_length=25)
    program_id = models.IntegerField()
    program_no = models.IntegerField()
    party_id = models.IntegerField()
    outward_wt = models.IntegerField()
    inward_wt = models.IntegerField()
    balance_wt = models.IntegerField() 
    class Meta:
        db_table = "grey_outward_available_sum"



class yarn_out_available_balance_table(models.Model):
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
        db_table ="yarn_outward_available_balance"



class yarn_out_available_sum_table(models.Model):
    out_id = models.IntegerField()
    outward_no = models.CharField(max_length=15)
    lot_no = models.CharField(max_length=15)
    program_id = models.IntegerField()
    program_no = models.CharField(max_length=15)
    party_id = models.IntegerField()
    total_wt = models.IntegerField()
    inward_wt = models.DecimalField(max_digits=32,decimal_places=2)
    class Meta:
        db_table ="yarn_outward_available_sum"

