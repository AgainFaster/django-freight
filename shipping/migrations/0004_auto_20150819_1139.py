# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0003_auto_20150819_1045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingrequest',
            name='carrier_request',
        ),
        migrations.RemoveField(
            model_name='shippingrequest',
            name='carrier_response',
        ),
        migrations.AddField(
            model_name='shipment',
            name='carrier_request',
            field=models.TextField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shipment',
            name='carrier_response',
            field=models.TextField(default={}),
            preserve_default=False,
        ),
    ]
