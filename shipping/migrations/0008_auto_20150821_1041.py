# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0007_auto_20150820_1622'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='carton_qty',
        ),
        migrations.RemoveField(
            model_name='item',
            name='inner_qty',
        ),
        migrations.AddField(
            model_name='item',
            name='carton',
            field=models.TextField(default={}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='inner',
            field=models.TextField(default={}),
            preserve_default=False,
        ),
    ]
