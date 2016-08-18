from __future__ import unicode_literals
from django.db import models
from django.forms import forms


class SgClientLinkage(models.Model):
    sg_index = models.IntegerField(default=9999)
    client_linkage = models.CharField(max_length=30, default='undefined')

    def __str__(self):
        return "Site index: %d linked to %s" % (self.sg_index, self.client_linkage)


class Client(models.Model):
    client_name = models.CharField(max_length=20, default="aaa")
    client_type = models.CharField(max_length=20, default="aaa")
    active = models.IntegerField(default=1)
    client_acronyms = models.CharField(max_length=20, default="false")

    def __str__(self):
        return self.client_name
	

class Site(models.Model):
    site_number = models.IntegerField(default=99999)
    site_name = models.CharField(max_length=20, default="undefined")
    site_type = models.CharField(max_length=20, default="restaurant")
    active = models.IntegerField(default=1)
    client_id = models.ForeignKey(Client)

    def __unicode__(self):
        return self.site_name
	
	
class SiteContact(models.Model):
    email = models.EmailField(default="aaa@aaa.com")
    phone = models.CharField(max_length=12, default="aaa")
    password = models.CharField(default='1234567890', max_length=20)
    site_id = models.ForeignKey(Site, default=999)
    type = models.CharField(max_length=20, default='none')

    def __str__(self):
        return self.email +', '+self.type +', ' + self.site_id.site_name
	

class SiteWorkingHoursDetail(models.Model):
    date = models.DateField(default='0000-00-00')
    time_from = models.TimeField(default='00:00:00')
    time_to = models.TimeField(default='00:00:00')
    site_id = models.ForeignKey(Site, default=9999)
    daily_manager = models.EmailField(default='aaa@aaa.com')
    daily_manager_phone = models.CharField(default='99999999999', max_length=12)

    def __str__(self):
        return self.site_id.site_name + ' date : %s' %self.date

    class Meta:
		ordering = ['-date']

