#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from stats.models import *
import sys
import subprocess
import tempfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        _errlog("removing excessive batches")
        date = _startdate()
        now = datetime.now().replace(tzinfo=date.tzinfo)
        while date < now:
            batches = RefreshBatch.objects.filter(
                date__range=(date, _nexthour(date)))
            _errlog("{0}, {1}".format(date, len(batches)))
            if len(batches) > 2:
                _purge_excessive_batches(batches)
            date = _nexthour(date)


def _startdate():
    batch = RefreshBatch.objects.earliest("date")
    d = batch.date
    return datetime(d.year, d.month, d.day, hour=d.hour, tzinfo=d.tzinfo)


def _nexthour(date):
    return date + timedelta(hours=1)


def _purge_excessive_batches(batches):
    batches = list(batches)
    del batches[_find_closest_minute(batches, 20)]
    del batches[_find_closest_minute(batches, 40)]
    _errlog("\twill delete {0} batches".format(len(batches)))
    _delete(batches)


def _find_closest_minute(batches, minute):
    closest = 0
    closest_distance = 99999999
    for i, batch in enumerate(batches):
        distance = abs(batch.date.minute - minute)
        if distance < closest_distance:
            closest = i
            closest_distance = distance
    _errlog("\tclosest to {0} minutes is {1}".format(minute, batches[closest]))
    return closest


@transaction.atomic
def _delete(batches):
    map(_delete_batch, batches)


def _delete_batch(batch):
    _errlog("\t\tdeleting batch {0}".format(batch))
    servers = batch.server_set.all()

    _errlog("\t\t\tdeleting {0} servers".format(len(servers)))
    server_aftermath = map(_delete_server, servers)

    unknown_servers = filter(lambda x: x is None, server_aftermath)
    _errlog("\t\t\tdeleted unknown servers: {0}".format(len(unknown_servers)))
    known_servers = filter(lambda x: x is not None, server_aftermath)
    _errlog("\t\t\tdeleted known servers: {0}".format(len(known_servers)))
    total_object_count = sum(known_servers, _Count())
    _errlog("\t\t\tdeleted objects: {0}".format(total_object_count))

    batch.delete()


def _delete_server(server):
    aftermath = None
    if server.data:
        aftermath = _delete_server_data(server.data)
    server.delete()
    return aftermath


def _delete_server_data(server_data):
    count = _Count()
    count.players = len(map(_delete_obj, server_data.player_set.all()))
    count.dmflagsgroups = len(map(_delete_obj, server_data.serverdmflagsgroup_set.all()))
    count.gamefiles = len(map(_delete_obj, server_data.servergamefile_set.all()))
    count.modifiers = len(map(_delete_obj, server_data.servermodifier_set.all()))
    server_data.delete()
    return count


def _delete_obj(obj):
    obj.delete()


def _errlog(what):
    print >>sys.stderr, "[doomstats] {0}".format(what)


def _now():
    return timezone.localtime(timezone.now())


class _Count(object):
    def __init__(self):
        self.players = 0
        self.dmflagsgroups = 0
        self.gamefiles = 0
        self.modifiers = 0

    def __str__(self):
        return ("players={0.players}, dmflagsgroups={0.dmflagsgroups}, "
                "gamefiles={0.gamefiles}, modifiers={0.modifiers}"
        ).format(self)

    def __add__(self, other):
        return self.__radd__(other)

    def __radd__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError("cannot add {0} to {1}".format(
                other.__class__, self.__class__))
        summed = _Count()
        summed.players = self.players + other.players
        summed.dmflagsgroups = self.dmflagsgroups + other.dmflagsgroups
        summed.gamefiles = self.gamefiles + other.gamefiles
        summed.modifiers = self.modifiers + other.modifiers
        return summed
