# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-07 12:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smart_green_interface', '0008_sitecontact_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecontact',
            name='client_id',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='smart_green_interface.Client'),
        ),
    ]
