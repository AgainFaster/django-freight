# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0008_auto_20150821_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='carton',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='inner',
            field=models.CharField(max_length=255),
        ),
    ]
