# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rankings.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PlayedGame',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('ranked', models.BooleanField(default=True)),
                ('start_time', models.DateTimeField()),
                ('comment', models.CharField(blank=True, max_length=100000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('color', rankings.fields.ColorField(max_length=6)),
                ('real_name', models.CharField(blank=True, max_length=100)),
                ('ranking_points', models.IntegerField(default=1000)),
                ('pool_points', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('comment', models.CharField(blank=True, max_length=100000)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PointsChanged',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('rp_before', models.IntegerField()),
                ('rp_after', models.IntegerField()),
                ('pp_before', models.IntegerField()),
                ('pp_after', models.IntegerField()),
                ('game', models.ForeignKey(blank=True, null=True, to='rankings.PlayedGame')),
                ('player', models.ForeignKey(to='rankings.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subgame',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('map_played', models.CharField(blank=True, max_length=100)),
                ('pl_lives', models.IntegerField()),
                ('pr_lives', models.IntegerField()),
                ('replay_file', models.FileField(blank=True, upload_to='replays/')),
                ('parent', models.ForeignKey(to='rankings.PlayedGame')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('finished', models.BooleanField(default=False)),
                ('start_time', models.DateTimeField()),
                ('name', models.CharField(blank=True, max_length=100)),
                ('ante', models.IntegerField()),
                ('pool_points', models.IntegerField(default=0)),
                ('total_ante', models.IntegerField()),
                ('comment', models.CharField(blank=True, max_length=100000)),
                ('players', models.ManyToManyField(to='rankings.Player', related_name='tournament_players')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TournamentPlacingAnte',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('placing', models.IntegerField()),
                ('ante', models.IntegerField()),
                ('player', models.ForeignKey(blank=True, null=True, to='rankings.Player')),
                ('tournament', models.ForeignKey(to='rankings.Tournament')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pointschanged',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, to='rankings.Tournament'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='playedgame',
            name='player_left',
            field=models.ForeignKey(to='rankings.Player', related_name='playedgame_player_left'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='playedgame',
            name='player_right',
            field=models.ForeignKey(to='rankings.Player', related_name='playedgame_player_right'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='playedgame',
            name='tournament',
            field=models.ForeignKey(to='rankings.Tournament', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='playedgame',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, to='rankings.Player', related_name='winner'),
            preserve_default=True,
        ),
    ]
