# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='pool_points',
        ),
        migrations.RemoveField(
            model_name='player',
            name='ranking_points',
        ),
        migrations.AddField(
            model_name='player',
            name='start_pool_points',
            field=models.IntegerField(default=1000),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='start_ranking_points',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
