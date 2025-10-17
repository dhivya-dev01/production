from django.db import models
from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
# from django.utils.translation import gettext_lazy as _
import os

import company

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



class Knitnumber(UppercaseModel):
    knitting_number = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()   
                if last_instance:
                    self.knitting_number = f"KN{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.knitting_number = "KN00001" 
        super().save(*args, **kwargs)  


    class Meta: 
        abstract = True   

  


 
class knitting_table(models.Model):
    knitting_number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    lot_no = models.IntegerField(default=0,null=True,blank=True) 
    program_date = models.DateField(null=False)
    company_id = models.IntegerField()
    is_yarn = models.IntegerField()
    is_grey_fabric = models.IntegerField()
    # knitting_id = models.IntegerField() 
    po_id = models.IntegerField() 
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    total_tax = models.DecimalField(max_digits=20,decimal_places=3)
    round_off = models.CharField(max_length=15) 
    grand_total = models.DecimalField(max_digits=20,decimal_places=3)
    # remarks = models.CharField(max_length=150)
    is_inward = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    class Meta:  
        db_table="tm_knitting"

 
class sub_knitting_table(UppercaseModel):
    tm_id = models.IntegerField()   
    count_id = models.IntegerField() 
    # tx_id = models.IntegerField(default=0)  #child_po_table id
    # tm_po_id = models.IntegerField(default=0) 
    fabric_id = models.IntegerField()
    gauge = models.IntegerField()
    tex = models.IntegerField()
    dia = models.IntegerField()
    gsm = models.IntegerField() 
    rolls = models.IntegerField()
    wt_per_roll = models.DecimalField(max_digits=20,decimal_places=2)
    quantity = models.DecimalField(max_digits=20,decimal_places=2) 
    rate = models.DecimalField(max_digits=20,decimal_places=2)
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:  
        db_table="tx_knitting"
 
  


class outward_lot_table(models.Model):

    out_id = models.IntegerField()
    party_id = models.IntegerField()
    lot_no = models.CharField(max_length=15)
    out_number = models.CharField(max_length=15)
    out_quantity = models.IntegerField()
    out_gross_quantity = models.DecimalField(max_digits=20,decimal_places=2)


    class Meta:
        db_table = "outward_lot"



class dyeing_program_table(UppercaseModel): 
    program_no = models.CharField(max_length=20, null=True,blank=True) 
    program_date = models.DateField()
    name = models.CharField(max_length=50, null=True,blank=True) 
    total_rolls = models.DecimalField(max_digits=20,decimal_places=2)
    total_wt = models.DecimalField(max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=150)
    program_id = models.IntegerField()
    fabric_id = models.IntegerField(default=0)
    is_grey_fabric = models.IntegerField(default=0)
    is_dyed_fabric = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_dyeing_program"


class sub_dyeing_program_table(UppercaseModel):
    tm_id = models.IntegerField()
    fabric_id = models.IntegerField()
    yarn_count_id = models.IntegerField()
    gauge_id = models.IntegerField()
    tex_id = models.IntegerField() 
    gsm = models.IntegerField()
    color_id = models.IntegerField()
    dia_id = models.IntegerField()
    roll = models.DecimalField(max_digits=20,decimal_places=2)
    roll_wt = models.DecimalField(max_digits=20,decimal_places=2) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()    
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_dyeing_program"
 



 
class cutting_program_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    program_date = models.DateField()
    cutting_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15)
    company_id = models.IntegerField()
    quality_id = models.IntegerField(default=0) 
    style_id = models.IntegerField(default=0) 
    fabric_id = models.IntegerField(default=0)
    total_quantity = models.IntegerField()
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_cutting_program"


class sub_cutting_program_table(UppercaseModel):
    tm_id = models.IntegerField()
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    quality_id = models.IntegerField()  
    style_id = models.IntegerField()  
    fabric_id = models.IntegerField()
    size_id = models.IntegerField()  
    color_id = models.IntegerField()
    quantity = models.IntegerField()
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_cutting_program" 



# ```````````` folding program ````````````````````````




class folding_program_table(UppercaseModel):
    program_no = models.CharField(max_length=15)
    company_id = models.IntegerField()
    quality_id = models.IntegerField(default=0) 
    style_id = models.IntegerField(default=0) 
    size_1 = models.DecimalField(max_digits=20,decimal_places=3)
    size_2 = models.DecimalField(max_digits=20,decimal_places=3)
    size_3 = models.DecimalField(max_digits=20,decimal_places=3)
    size_4 = models.DecimalField(max_digits=20,decimal_places=3)
    size_5 = models.DecimalField(max_digits=20,decimal_places=3)
    size_6 = models.DecimalField(max_digits=20,decimal_places=3)
    size_7 = models.DecimalField(max_digits=20,decimal_places=3)
    size_8 = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_folding_program"


# class sub_folding_program_table(UppercaseModel):
#     tm_id = models.IntegerField()
#     quality_id = models.IntegerField()
#     style_id = models.IntegerField()
#     size_id = models.IntegerField()
#     quantity = models.DecimalField(decimal_places=2,max_digits=20)
#     is_active = models.IntegerField(default=1)
#     status = models.IntegerField(default=1)  
#     created_on=models.DateTimeField()
#     updated_on=models.DateTimeField() 
#     created_by=models.IntegerField()  
#     updated_by=models.IntegerField() 
#     class Meta: 
#         db_table="tx_folding_program"  
 


