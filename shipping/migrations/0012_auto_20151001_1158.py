# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0011_auto_20150929_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingrequest',
            name='ip',
            field=models.GenericIPAddressField(),
        ),
    ]
