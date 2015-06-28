from .models import *
from googlecharts.collections import Chart
from doomstats.timestuff import daterange_resolution
from datetime import datetime


def general_table():
    batch_count = RefreshBatch.objects.count()
    return Table(
        id="general-table",
        header="All-time stats",
        rows=[
            ("Data collected since:", DateCell(
                _first_batch().date, "%Y-%m-%d %H:%M:%S")),
            ("Collected batches:", batch_count),
            ("Average all-time server count:",
             Server.objects.count() / max(1, batch_count)),
            ("Average all-time player count:",
             Player.objects.count() / max(1, batch_count))
        ])


def stats_daterange_table(daterange, engine=None):
    batch_count = RefreshBatch.objects.filter(date__range=daterange).count()
    return Table(
        id="stats-daterange-table",
        header="Amounts in date range",
        rows=[
            ("Collected batches:", batch_count),
            ("Average server count:",
             Server.count_in_daterange(engine, daterange) / max(1, batch_count)),
            ("Average player count:",
             Player.count_in_daterange(engine, daterange) / max(1, batch_count))
        ])


def players_chart(daterange, engine=None):
    resolution = daterange_resolution(daterange)
    if resolution == "day":
        dateformat = "%Y-%m-%d %a"
    elif resolution == "hour":
        dateformat = "%d %a %H:%M"
    dateslices = RefreshBatch.slice(daterange, resolution)
    rows = []
    for dateslice in dateslices:
        batch_filter = {
            "date__year": dateslice.year,
            "date__month": dateslice.month,
            "date__day": dateslice.day
        }
        if resolution == "hour":
            batch_filter["date__hour"] = dateslice.hour
        batches = RefreshBatch.objects.filter(**batch_filter)
        filter = {
            "server__server__refresh_batch__in": batches
        }
        if engine:
            filter["server__server__engine"] = engine
        count = Player.objects.filter(**filter).count()
        rows.append((dateslice.strftime(dateformat),
                     count / max(1, batches.count())))
    return Chart(
        id="players-chart", kind="LineChart",
        options={'title': 'Players per {0}'.format(resolution),
                 'width': "100%",
                 'height': 300,
                 'legend': 'none'},
        columns=[('string', 'Day'), ('number', 'Players')],
        rows=rows)


def _first_batch():
    return RefreshBatch.objects.order_by("date").first() or \
        RefreshBatch(date=datetime.fromtimestamp(0))


class Table(object):
    def __init__(self, id=None, header=None, rows=None):
        self.id = id
        self.header = header
        self.rows = rows
        if not rows:
            self.rows = []

    @property
    def typeof(self):
        return self.__class__.__name__

    @property
    def num_cols(self):
        if self.rows:
            return len(self.rows[0])
        return 0

class DateCell(object):
    def __init__(self, date, format):
        self.date = date
        self.format = format

    def __str__(self):
        return self.date.strftime(self.format)
