#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from stats.management import serverdatarefinery
import sys
import subprocess
import tempfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        _errlog("running doomlister {0}".format(_now()))
        with tempfile.TemporaryFile() as f:
            p = subprocess.Popen(['doomlister'], stdout=f)
            if p.wait() != 0:
                raise Exception('doomlister failed')
            _errlog("doomlister completed successfully")
            f.seek(0)
            data = f.read()
        _errlog("putting data to database")
        serverdatarefinery.put_json_to_database(timezone.now(), data)
        _errlog("collecting completed {0}".format(_now()))


def _errlog(what):
    print >>sys.stderr, "[doomstats] {0}".format(what)


def _now():
    return timezone.localtime(timezone.now())
