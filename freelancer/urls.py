"""freelancer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include # new
from django.contrib.auth import views as auth_views
from django.conf import settings

admin.site.site_header = 'Work handy Admin Area'
admin.site.site_title = 'Work handy freelancer'
admin.site.site_url = 'Work handy freelancer'
admin.site.index_title = 'Work handy freelancer administration'
admin.empty_value_display = '**Empty**'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), # new
    path('accounts/', include('django.contrib.auth.urls')), # new
    path('', include('portal.urls'))
]
