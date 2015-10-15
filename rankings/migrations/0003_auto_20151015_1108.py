# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import rankings.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0002_auto_20150626_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='color',
            field=rankings.fields.ColorField(),
        ),
    ]
