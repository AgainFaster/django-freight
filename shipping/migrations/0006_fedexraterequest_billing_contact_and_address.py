# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0005_responserate_shipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='fedexraterequest',
            name='billing_contact_and_address',
            field=models.TextField(default={}),
            preserve_default=False,
        ),
    ]
