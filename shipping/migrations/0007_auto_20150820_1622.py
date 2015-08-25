# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0006_fedexraterequest_billing_contact_and_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='carton_qty',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='inner_qty',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
