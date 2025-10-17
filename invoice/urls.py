
from django.contrib import admin

from invoice import views

from invoice.views import * 
from django.urls import path, include

urlpatterns = [

 

    # GREY FABRIC PO
    path('invoice',views.invoices), 
    path('invoice-add/',views.invoice_add),
 
] 