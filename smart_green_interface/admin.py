from smart_green_interface.models import Client, Site, SiteWorkingHoursDetail, SiteContact, SgClientLinkage
from django.contrib import admin

admin.site.register(Client)
admin.site.register(Site)
admin.site.register(SiteWorkingHoursDetail)
admin.site.register(SiteContact)
admin.site.register(SgClientLinkage)