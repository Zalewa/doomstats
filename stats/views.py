from django.shortcuts import render
from django.utils import timezone
from .models import *
from datetime import timedelta, datetime
import json
import time


def front_page(request):
    data = {}
    data["first_batch"] = _first_batch()
    data["num_batches"] = RefreshBatch.objects.count()
    data["average_server_count"] = Server.objects.count() / max(1, data["num_batches"])
    data["average_player_count"] = Player.objects.count() / max(1, data["num_batches"])
    return render(request, "stats/front_page.html", data)


def _first_batch():
    return RefreshBatch.objects.order_by("date").first() or \
        RefreshBatch(date=datetime.fromtimestamp(0))


def engine(request, name):
    data = {
        "name": name,
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
        })
    }


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


def _stddate(date):
    return date.replace(hour=0, minute=0, second=0)
