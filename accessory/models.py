from statistics import mode
from django.db import models,transaction
from django.core.exceptions import ValidationError 
# from django.utils.translation import gettext_lazy as _
import os

# class UppercaseModel(models.Model):
#     """Base model to ensure all CharField values are stored in uppercase."""
    
#     def save(self, *args, **kwargs):
#         for field in self._meta.fields:
#             if isinstance(field, models.CharField):
#                 value = getattr(self, field.name)
#                 if value:  # Ensure value is not None
#                     setattr(self, field.name, value.upper())
#         super().save(*args, **kwargs)   

#     class Meta:
#         abstract = True 

class UppercaseModel(models.Model):
    """Base model to ensure CharField and TextField values are stored in uppercase, except emails (lowercase) and passwords (unchanged)."""
    
    # def save(self, *args, **kwargs):
    #     for field in self._meta.fields:
    #         if isinstance(field, (models.CharField, models.TextField)):  # Apply to CharField & TextField
    #             value = getattr(self, field.name)
    #             if value:  # Ensure value is not None
    #                 if "email" in field.name:  # Store emails in lowercase
    #                     setattr(self, field.name, value.lower())
    #                 elif "password" in field.name:  # Keep passwords unchanged
    #                     continue
    #                 else:  # Convert all other text fields to uppercase
    #                     setattr(self, field.name, value.upper())
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                value = getattr(self, field.name)
                if value and isinstance(value, str):  # ✅ Only operate on strings
                    if "email" in field.name:
                        setattr(self, field.name, value.lower())
                    elif "password" in field.name:
                        continue
                    else:
                        setattr(self, field.name, value.upper())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True  # This model will not create a separate database table

 # This model will not create a separate database table



class acc_item_group_table(UppercaseModel): 
    name = models.CharField(max_length=50)
    group_type = models.CharField(max_length=30)
    # company_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "acc_item_group"
 

class accessory_quality_table(UppercaseModel):
    name = models.CharField(max_length=70)
    po_name = models.CharField(max_length=70)
    # company_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "accessory_quality"




class accessory_size_table(UppercaseModel):
    name = models.CharField(max_length=70)
    po_name = models.CharField(max_length=70)
    # company_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "accessory_size"

 

class accessory_color_table(UppercaseModel):
    name = models.CharField(max_length=50)
    # company_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "accessory_color"

        



class AccessoryItem(UppercaseModel):
    acc_item_code = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()  
                if last_instance:
                    self.acc_item_code = f"ACC{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.acc_item_code = "ACC00101" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True 



class item_table(AccessoryItem):
    name = models.CharField(max_length=50)
    item_group_id = models.IntegerField()
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta: 
        db_table = "acc_item"  # accessory-item table


        
        # db_table = "accessory_item"
 



class sub_item_table(UppercaseModel):
    item_id = models.IntegerField()
    quality_id = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "mx_acc_item_quality"   # for quality




class sub_size_table(UppercaseModel):    #for size and color
    item_id = models.IntegerField() 
    quality_id = models.IntegerField(default=0)
    size_id = models.IntegerField()
    color_id = models.CharField(max_length=50)
    m_color_id = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    
    class Meta:
        db_table = "mx_acc_item_size"



class style_table(UppercaseModel):
    name = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "style"


class size_table(UppercaseModel):
    name = models.CharField(max_length=50)
    sort_order_no = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "size"


class quality_table(UppercaseModel):
    name = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "quality"

class quality_program_table(UppercaseModel):
    quality_id = models.IntegerField()
    style_id = models.IntegerField()
    fabric_id = models.CharField(max_length=15)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "quality_program"


class sub_quality_program_table(UppercaseModel):
    tm_id = models.IntegerField()
    size_id = models.IntegerField()
    position = models.IntegerField()
    per_box = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
     
    class Meta:
        db_table = "mx_quality_program_size"




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

 

 
class parent_accessory_po_table(UppercaseModel):
    po_number = models.CharField(max_length=15)
    # po_name = models.CharField(max_length=50,)
    po_date = models.DateField(null=False)
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    party_id = models.IntegerField() 
    total_quantity = models.IntegerField()
    total_tax = models.DecimalField(max_digits=20,decimal_places=2)
    round_off = models.DecimalField(max_digits=20,decimal_places=2)
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    grand_total = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_accessory_po" 


class child_accessory_po_table(models.Model):
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    tm_id = models.IntegerField()
    item_group_id = models.IntegerField()  
    item_id = models.IntegerField()
    quality_id = models.IntegerField()
    size_id = models.IntegerField()
    color_id = models.IntegerField()
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    amount = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_accessory_po"
 




class accessory_po_balance_table(models.Model):
    po_id = models.IntegerField()
    po_number = models.CharField(max_length=15)
    po_name = models.CharField(max_length=15)
    po_date = models.DateField()
    item_group_id = models.IntegerField()
    item_id = models.IntegerField()
    party_id = models.IntegerField()
    po_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    in_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=3)
    class Meta:
        db_table="accessory_po_balance"
    

# class production_balance_table(models.Model):
#     po_id = models.IntegerField()
#     po_number = models.CharField(max_length=15)
#     po_name = models.CharField(max_length=15)
#     po_date = models.DateField()
#     item_group_id = models.IntegerField()
#     item_id = models.IntegerField()
#     party_id = models.IntegerField()
#     po_quantity = models.DecimalField(max_digits=20,decimal_places=3)
#     in_quantity = models.DecimalField(max_digits=20,decimal_places=3)
#     balance_quantity = models.DecimalField(max_digits=20,decimal_places=3)
#     class Meta:
#         db_table="production_balance"

# ````````````````````````  inward  ``````````````````````````````````



class parent_accessory_inward_table(UppercaseModel):
    inward_number = models.CharField(max_length=15)
    inward_date = models.DateField(null=False)
    receive_no = models.CharField(max_length=15)
    receive_date = models.DateField(null=False)
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    party_id = models.IntegerField() 
    po_id = models.IntegerField() 
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_accessory_inward" 


class child_accessory_inward_table(models.Model):
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    party_id = models.IntegerField()
    po_id = models.IntegerField()
    tm_id = models.IntegerField()
    item_group_id = models.IntegerField()  
    item_id = models.IntegerField()
    quality_id = models.IntegerField()
    size_id = models.IntegerField()
    color_id = models.IntegerField()
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    amount = models.DecimalField(max_digits=20,decimal_places=3)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_accessory_inward"
 






class parent_accessory_outward_table(UppercaseModel): 
    outward_no = models.CharField(max_length=15)
    outward_date = models.DateField(null=False) 
    # receive_no = models.CharField(max_length=15)
    # receive_date = models.DateField(null=False) 
    production_type = models.CharField(max_length=50)
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    party_id = models.IntegerField() 
    po_id = models.IntegerField() 
    packing_outward_id = models.IntegerField() 
    stiching_outward_id = models.IntegerField() 
    dyeing_outward_id = models.IntegerField() 
    sp_id = models.IntegerField(default=0)
    is_sp = models.IntegerField(default=0)
    is_production = models.IntegerField()
    is_direct = models.IntegerField(default=0)
    is_dyeing = models.IntegerField()
    total_quantity = models.IntegerField()
    total_wt = models.DecimalField(max_digits=20,decimal_places=2)
    total_amount = models.DecimalField(max_digits=20,decimal_places=3)
    remarks = models.CharField(max_length=150)
    is_active = models.IntegerField(default=1) 
    status = models.IntegerField(default=1) 
    created_on=models.DateTimeField() 
    updated_on=models.DateTimeField()  
    created_by=models.IntegerField() 
    updated_by=models.IntegerField() 
    class Meta:
        db_table="tm_accessory_outward"  


class child_accessory_outward_table(models.Model):
    company_id = models.IntegerField()
    cfyear = models.CharField(max_length=15)
    party_id = models.IntegerField()
    po_id = models.IntegerField() 
    uom_id = models.IntegerField()
    tm_id = models.IntegerField()  
    item_group_id = models.IntegerField()    
    item_id = models.IntegerField()
    quality_id = models.IntegerField()
    acc_size_id = models.IntegerField() 
    style_id = models.IntegerField()    
    size_id = models.IntegerField()  
    acc_quality_id = models.IntegerField()
    color_id = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    wt = models.DecimalField(max_digits=20,decimal_places=2)
    rate = models.DecimalField(max_digits=20,decimal_places=2) 
    amount = models.DecimalField(max_digits=20,decimal_places=3) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)  
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()  
    updated_by=models.IntegerField() 
    class Meta: 
        db_table="tx_accessory_outward"
 

