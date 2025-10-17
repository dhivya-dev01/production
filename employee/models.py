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




class EmployeeSeries(UppercaseModel):
    employee_code = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: 
            with transaction.atomic():
                last_instance = self.__class__.objects.last()    
                if last_instance:
                    self.employee_code = f"EM{str(last_instance.id + 1).zfill(5)}"
                else:
                    self.employee_code = "EM00001" 
        super().save(*args, **kwargs)  

    class Meta: 
        abstract = True  



class employee_table(EmployeeSeries):
    name = models.CharField(max_length=20)
    nick_name = models.CharField(max_length=20)
    designation = models.CharField(max_length=20)
    employee_role = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    email = models.CharField(max_length=25)
    password = models.CharField(max_length=25)
    permanent_address = models.TextField()
    current_address = models.TextField()
    alter_mobile_no = models.IntegerField() 
    aadhar_no = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='images/', max_length=255, blank=True, null=True)
    dob = models.DateField()
    join_date = models.DateField()
    company_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField() 
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="employee"



