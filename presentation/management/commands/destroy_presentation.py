#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    def handle(self, *args, **options):
        app_models = apps.get_app_config('presentation').get_models()
        for model in app_models:
            model.objects.all().delete()
