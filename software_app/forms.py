from django import forms
from software_app.models import *
from company.models import *



# # forms.py
# from .models import company_table  # Correctly import the model here



class companyform(forms.ModelForm):
    class Meta:
        model = company_table
        fields = ['name','prefix','address_line1','city','state','country','state_code',
        'gstin','phone','mobile','email','opening_balance','logo','logo_small',
        'logo_invoice']

        exclude = ['status','address_line2','phone','contact_person','latitude','longitude','contact_person'
                   ,'cp_phone','cp_mobile','cp_email','report_email','is_active','created_on','updated_on','created_by','updated_by']


#         class companyform(forms.ModelForm):
#     class Meta:
#         model = company_table
#         fields = ['name','prefix','address_line1','address_line2','city','state','country','state_code','pincode',
#         'gstin','phone','mobile','email','contact_person','cp_phone','cp_mobile','cp_email','report_email','opening_balance','latitude','longitude','logo','logo_small',
#         'logo_invoice']
#         exclude = ['status','address_line2','phone','contact_person','latitude','longitude','cp_phone','cp_mobile','cp_email','pincode','report_email','is_active','created_on','updated_on','created_by','updated_by']
# #
    