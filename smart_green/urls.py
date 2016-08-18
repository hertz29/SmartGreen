"""smart_green URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from smart_green_interface import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login_temp/$', views.login_view),
    url(r'^verify/$', views.verify_pass),
    url(r'^change_pass/$', views.change_pass),
    url(r'^confirm_pass/$', views.confirm_change_pass),
    url(r'^$', views.login_view),
    url(r'^dashboard/$', views.dashboard),
    url(r'^theme/$', views.theme),
    url(r'^sort_open_hours_by_date/$', views.sort_open_hours_by_date)
]
