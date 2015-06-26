# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.TextField()),
                ('port', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Cvar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('command', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DmflagsGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Engine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EngineVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.TextField()),
                ('engine', models.ForeignKey(to='stats.Engine')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GameFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GameMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('is_team_game', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Iwad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('game', models.ForeignKey(to='stats.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_spectating', models.BooleanField()),
                ('is_bot', models.BooleanField()),
                ('score', models.IntegerField()),
                ('ping', models.IntegerField()),
                ('team', models.IntegerField()),
                ('name', models.ForeignKey(to='stats.Name')),
            ],
        ),
        migrations.CreateModel(
            name='RefreshBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.ForeignKey(to='stats.Address')),
            ],
        ),
        migrations.CreateModel(
            name='ServerData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('max_players', models.IntegerField()),
                ('max_clients', models.IntegerField()),
                ('score_limit', models.IntegerField()),
                ('time_limit', models.IntegerField()),
                ('requires_connect_password', models.BooleanField()),
                ('requires_join_password', models.BooleanField()),
                ('is_secure', models.BooleanField()),
                ('engine_version', models.ForeignKey(to='stats.EngineVersion')),
                ('game_mode', models.ForeignKey(to='stats.GameMode')),
                ('iwad', models.ForeignKey(to='stats.Iwad')),
                ('mapname', models.ForeignKey(related_name='stats_serverdata_mapname', to='stats.Name')),
                ('name', models.ForeignKey(related_name='stats_serverdata_name', to='stats.Name')),
            ],
        ),
        migrations.CreateModel(
            name='ServerDmflagsGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('dmflags', models.ForeignKey(to='stats.DmflagsGroup')),
                ('server_data', models.ForeignKey(to='stats.ServerData')),
            ],
        ),
        migrations.CreateModel(
            name='ServerGameFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_optional', models.BooleanField()),
                ('gamefile', models.ForeignKey(to='stats.GameFile')),
                ('server_data', models.ForeignKey(to='stats.ServerData')),
            ],
        ),
        migrations.CreateModel(
            name='ServerModifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True)),
                ('cvar', models.ForeignKey(to='stats.Cvar')),
                ('server_data', models.ForeignKey(to='stats.ServerData')),
            ],
        ),
        migrations.CreateModel(
            name='ServerResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('level', models.IntegerField()),
                ('game', models.ManyToManyField(to='stats.Game')),
            ],
        ),
        migrations.AddField(
            model_name='serverdata',
            name='skill',
            field=models.ForeignKey(to='stats.Skill'),
        ),
        migrations.AddField(
            model_name='server',
            name='data',
            field=models.ForeignKey(to='stats.ServerData', null=True),
        ),
        migrations.AddField(
            model_name='server',
            name='engine',
            field=models.ForeignKey(to='stats.Engine'),
        ),
        migrations.AddField(
            model_name='server',
            name='refresh_batch',
            field=models.ForeignKey(to='stats.RefreshBatch'),
        ),
        migrations.AddField(
            model_name='server',
            name='response',
            field=models.ForeignKey(to='stats.ServerResponse'),
        ),
        migrations.AddField(
            model_name='player',
            name='server',
            field=models.ForeignKey(to='stats.ServerData'),
        ),
    ]
