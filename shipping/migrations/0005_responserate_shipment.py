# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0004_auto_20150819_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='responserate',
            name='shipment',
            field=models.ForeignKey(default=None, to='shipping.Shipment', related_name='rates'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='responserate',
            name='shipping_request',
        )
    ]
