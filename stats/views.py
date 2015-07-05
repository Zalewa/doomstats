from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *
from .collections import *
from datetime import timedelta, datetime
from doomstats.timestuff import day_range
import json
import time


def front_page(request):
    data = {}
    daterange = _daterange_for_query(request)
    data["tables"] = [
        general_table(),
        stats_daterange_table(daterange)
    ]
    return render(request, "stats/front_page.html", data)


def engine_players(request, name):
    return _Engine(request, name).players()


def engine_wads(request, name):
    return _Engine(request, name).wads()


def engine_servers(request, name):
    return _Engine(request, name).servers()


class _Engine(object):
    def __init__(self, request, name):
        self._request = request
        self._name = name
        self._game_engine = get_object_or_404(Engine, name__iexact=name)
        self._daterange = _daterange_for_query(request)

    def players(self):
        data = {
            "cur_engine": self._game_engine,
            "stats": [
                stats_daterange_table(self._daterange, self._game_engine),
                players_chart(self._daterange, self._game_engine)
            ],
        }
        return self._render(data)

    def wads(self):
        data = {
            "cur_engine": self._game_engine,
            "stats": [
                wads_popularity_table(self._daterange, self._game_engine)
            ],
        }
        return self._render(data)

    def servers(self):
        data = {
            "cur_engine": self._game_engine,
            "stats": [
                servers_popularity_table(self._daterange, self._game_engine)
            ],
        }
        return self._render(data)

    def _render(self, data):
        return render(self._request, "stats/engine.html", data)


def about(request):
    return render(request, "stats/about.html")


def load_site_global_context(request):
    datefrom, dateto = _daterange_from_request(request)
    return {
        "engines": Engine.objects.all().order_by("name"),
        "json": json.dumps({
            "date-from": _dateformat(datefrom),
            "date-to": _dateformat(dateto),
        }),
        "dates": {
            "today": _dateformat(timezone.now()),
            "yesterday": _dateformat(timezone.now() - timedelta(days=1)),
            "7days": _dateformat(timezone.now() - timedelta(days=7))
        }
    }


def _daterange_for_query(request):
    datefrom, dateto = _daterange_from_request(request)
    return day_range(datefrom, dateto)


def _daterange_from_request(request):
    datefrom = _date_from_request(request, "datefrom") or (timezone.now() - timedelta(days=1))
    dateto = _date_from_request(request, "dateto") or timezone.now()
    if dateto < datefrom:
        datefrom, dateto = dateto, datefrom  # Obviously, it's that simple.
    return _stddate(datefrom), _stddate(dateto)


def _date_from_request(request, fieldname):
    stamp = request.GET.get(fieldname)
    if stamp is None:
        stamp = request.session.get(fieldname)
        if stamp is None:
            return None
    request.session[fieldname] = stamp
    try:
        date = datetime.strptime(stamp, "%Y-%m-%d")
    except ValueError:
        return timezone.now()
    date = date.replace(tzinfo=timezone.utc)
    return date


def _dateformat(date):
    return date.strftime("%Y-%m-%d")


def _stddate(date):
    try:
        earliest = RefreshBatch.objects.earliest('date').date
        latest = RefreshBatch.objects.latest('date').date
    except RefreshBatch.DoesNotExist:
        earliest = latest = date
    date = max(earliest, min(latest, date))
    return date.replace(hour=0, minute=0, second=0)
