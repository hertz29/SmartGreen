# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-18 12:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smart_green_interface', '0013_auto_20160818_1216'),
    ]

    operations = [
        migrations.CreateModel(
            name='SgClientLinkage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sg_index', models.IntegerField(default=9999)),
                ('client_linkage', models.CharField(default='undefined', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SiteWorkingHoursDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default='0000-00-00')),
                ('time_from', models.TimeField(default='00:00:00')),
                ('time_to', models.TimeField(default='00:00:00')),
                ('daily_manager', models.EmailField(default='aaa@aaa.com', max_length=254)),
                ('daily_manager_phone', models.CharField(default='99999999999', max_length=12)),
                ('site_id', models.ForeignKey(default=9999, on_delete=django.db.models.deletion.CASCADE, to='smart_green_interface.Site')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]