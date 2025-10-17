"""
URL configuration for Genplus_Production project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.contrib import admin 
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [ 
    # path('admin/', admin.site.urls),   
    path('', include('user_auth.urls')),   # login, logout
    path('', include('common.urls')),      # dashboard
    path('', include('company.urls')),     #company
    path('', include('employee.urls')),     #employee
    path('', include('masters.urls')),     #master modules(category,uom,etc...)
    path('', include('user_roles.urls')),  #user roles

    path('', include('software_app.urls')), 
    path('', include('program_app.urls')),  #programs 
    path('', include('purchase_app.urls')),
    path('', include('yarn.urls')),         #yarn
    path('', include('grey_fabric.urls')),
    path('', include('colored_fabric.urls')),  #dyed fabric
    path('', include('accessory.urls')),   

    path('', include('cutting_entry.urls')),  
    path('', include('production_app.urls')), 
    path('', include('reports.urls')),  
    path('', include('invoice.urls')),  

    path('',include('sales.urls')), 
 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
