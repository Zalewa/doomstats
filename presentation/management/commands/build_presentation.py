#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from presentation.management import build


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--incremental', '-i', action='store_true',
                            dest='incremental', default=False)

    def handle(self, *args, **options):
        incremental = options["incremental"]
        build.build_presentation(incremental)
