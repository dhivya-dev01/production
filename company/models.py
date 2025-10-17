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



class company_table(UppercaseModel):
    name = models.CharField(max_length=150)
    prefix = models.CharField(max_length=10)
    address_line1 = models.CharField(max_length=150)
    address_line2 = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state_code = models.CharField(max_length=50)
    gstin = models.CharField(max_length=50)
    cin_no = models.CharField(max_length=50)
    udyam_no = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    mobile = models.CharField(max_length=15)
    email = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    tax_id = models.IntegerField()
    contact_person = models.CharField(max_length=50)
    cp_phone = models.CharField(max_length=15)
    cp_mobile = models.CharField(max_length=15)
    cp_email = models.CharField(max_length=30)
    report_email = models.CharField(max_length=30)
    opening_balance = models.IntegerField()
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='images/', max_length=50)
    logo_small = models.ImageField(upload_to='images/', max_length=50)
    logo_invoice = models.ImageField(upload_to='images/', max_length=50)
    # enc_code = models.CharField(max_length=250)
    company_code = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)  
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="company"
