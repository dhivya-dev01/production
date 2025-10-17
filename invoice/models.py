# from pyexpat import model
# from re import M

from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
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







class parent_invoice_table(UppercaseModel):
    invoice_no = models.CharField(max_length=15)   
    work_order_no = models.CharField(max_length=15)
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField() 
    invoice_date = models.DateField(null=False)
    outward_id = models.IntegerField()
    party_id = models.IntegerField()
    quality_id = models.IntegerField(default=0)   
    style_id = models.IntegerField(default=0)
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
        db_table="tm_invoice"



class child_invoice_table(UppercaseModel):
    cfyear = models.CharField(max_length=15)
    company_id = models.IntegerField()
    tm_id = models.IntegerField()
    outward_id = models.IntegerField()
    size_id = models.IntegerField()   
    quality_id = models.IntegerField(default=0)    
    style_id = models.IntegerField(default=0)
    box = models.IntegerField() 
    pcs = models.IntegerField() 
    price = models.DecimalField(max_digits=20,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=2)
    work_order_no = models.CharField(max_length=20)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_invoice_table"  

