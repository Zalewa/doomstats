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


def engine(request, name):
    game_engine = get_object_or_404(Engine, name__iexact=name)
    daterange = _daterange_for_query(request)
    data = {
        "name": name,
        "stats": [
            stats_daterange_table(daterange, game_engine),
            players_chart(daterange, game_engine),
            wads_popularity_table(daterange, game_engine)
        ],
    }
    return render(request, "stats/engine.html", data)


def about(request):
    return render(request, "stats/about.html")


def load_site_global_context(request):
    datefrom, dateto = _daterange_from_request(request)
    return {
        "engines": Engine.objects.all().order_by("name"),
        "json": json.dumps({
            "date-from": time.mktime(datefrom.timetuple()),
            "date-to": time.mktime(dateto.timetuple()),
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
