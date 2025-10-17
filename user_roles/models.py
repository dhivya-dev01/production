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



# Create your models here.




class login_table(UppercaseModel):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50) 
    password = models.CharField(max_length=50)
    user_type = models.CharField(max_length=50)
    company_id = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField() 
    updated_by=models.IntegerField()
    
    class Meta:
        db_table = "login"

class AdminModules(UppercaseModel):
    name = models.CharField(max_length=50)
    # module_name = models.CharField(max_length=50)
    sort_order_no = models.IntegerField()
    is_create = models.IntegerField(default=1)
    is_read = models.IntegerField(default=1)
    is_update = models.IntegerField(default=1)
    is_delete = models.IntegerField(default=1)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    # created_on = models.DateTimeField()
    # updated_on = models.DateTimeField()
    created_by = models.IntegerField() 
    updated_by = models.IntegerField()

    class Meta:
        db_table = "admin_module"   

class AdminPrivilege(UppercaseModel): 
    role_id = models.IntegerField()
    module = models.CharField(max_length=150)
    is_create = models.IntegerField(default=0) 
    is_read = models.IntegerField(default=0)
    is_update = models.IntegerField(default=0)
    is_delete = models.IntegerField(default=0) 
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "admin_privilege"



class AdminRoles(UppercaseModel):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=150)
    status = models.IntegerField(default=1)
    sort_order_no = models.IntegerField() 
    is_active = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "admin_roles"



class UserRoles(UppercaseModel):
    name = models.CharField(max_length=150)
    descriptions = models.CharField(max_length=150) 
    status = models.IntegerField(default=1)
    is_active = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "user_roles"



class UserModules(UppercaseModel):
    name = models.CharField(max_length=150)
    sort_order_no = models.IntegerField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "user_module"

 


class UserPrivilege(UppercaseModel):
    role_id = models.IntegerField()
    module = models.CharField(max_length=150)
    is_create = models.IntegerField(default=0)
    is_read = models.IntegerField(default=0)
    is_update = models.IntegerField(default=0)
    is_delete = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "user_privilege"
 
