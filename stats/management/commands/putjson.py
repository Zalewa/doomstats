#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from doomstats.timestuff import parse_rfc3339_stamp
from stats.management import serverdatarefinery
import os
import sys
import datetime


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'files', nargs='+',
            help='paths to JSON files which filenames are rfc-3339 dates')

    def handle(self, *args, **options):
        for filepath in options['files']:
            self._handle_file(filepath)

    def _handle_file(self, filepath):
        stamp = os.path.splitext(os.path.basename(filepath))[0]
        print >>sys.stderr, "File '{0}'".format(stamp)
        date = parse_rfc3339_stamp(stamp, ' ')
        print >>sys.stderr, "Loading batch: ", date
        with open(filepath, "rb") as f:
            data = f.read()
        serverdatarefinery.put_json_to_database(date, data)
