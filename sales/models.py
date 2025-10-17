
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




 
class parent_sales_order_table(UppercaseModel):
    order_no = models.CharField(max_length=15)
    work_order_no = models.CharField(max_length=15,default=0)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField() 
    order_date = models.DateField(null=False)
    packing_received_id = models.IntegerField() 
    party_id = models.IntegerField()  
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    fabric_id = models.IntegerField(default=0) 
    total_box = models.IntegerField()
    total_pcs = models.DecimalField(max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()    
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta: 
        db_table="tm_sales_order"



class child_sales_order_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField()
    packing_received_id = models.IntegerField()
    size_id = models.IntegerField()  
    quality_id = models.IntegerField(default=0)    
    style_id = models.IntegerField(default=0)
    box = models.IntegerField() 
    rate= models.DecimalField(max_digits=20,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=2)
    box_pcs = models.IntegerField() 
    pcs_per_box = models.IntegerField()
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)   
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_sales_order"  




class parent_sales_table(UppercaseModel):
    order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField() 
    order_date = models.DateField(null=False)
    sales_order_id = models.IntegerField() 
    party_id = models.IntegerField()  
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
    fabric_id = models.IntegerField(default=0)  
    total_box = models.IntegerField()
    total_pcs = models.DecimalField(max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()    
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()  
    class Meta: 
        db_table="tm_sales"



class child_sales_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField()
    sales_order_id = models.IntegerField()
    size_id = models.IntegerField()  
    quality_id = models.IntegerField(default=0)     
    style_id = models.IntegerField(default=0)
    box = models.IntegerField() 
    rate= models.DecimalField(max_digits=20,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=2)
    box_pcs = models.IntegerField() 
    pcs_per_box = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)   
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_sales"  

