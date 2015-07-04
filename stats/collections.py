from .models import *
from django.db.models import Count
from googlecharts.collections import Chart, Formatter
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
             DecimalCell(
                 Server.objects.count() / float(max(1, batch_count)))),
            ("Average all-time player count:",
             DecimalCell(
                 Player.objects.filter(is_bot=False).count() \
                 / float(max(1, batch_count))))
        ])


def stats_daterange_table(daterange, engine=None):
    batch_count = RefreshBatch.objects.filter(date__range=daterange).count()
    return Table(
        id="stats-daterange-table",
        header="Amounts in date range",
        rows=[
            ("Collected batches:", batch_count),
            ("Average server count:",
             DecimalCell(
                 Server.count_in_daterange(engine, daterange) / \
                 float(max(1, batch_count)))),
            ("Average player count:",
             DecimalCell(
                 Player.count_in_daterange(engine, daterange) / \
                 float(max(1, batch_count))))
        ])


def players_chart(daterange, engine=None):
    resolution = daterange_resolution(daterange)
    dateslices = RefreshBatch.slice(daterange, resolution)
    if resolution == "day":
        dateformat = "%Y-%m-%d %a"
    elif resolution == "hour":
        if dateslices[0].date() == dateslices.last().date():
            dateformat = "%H:%M"
        else:
            dateformat = "%d %a %H:%M"
    rows = []
    for dateslice in dateslices:
        dateslice = timezone.localtime(dateslice, timezone.utc)
        batch_filter = {
            "date__year": dateslice.year,
            "date__month": dateslice.month,
            "date__day": dateslice.day
        }
        if resolution == "hour":
            batch_filter["date__hour"] = dateslice.hour
        batches = RefreshBatch.objects.filter(**batch_filter)
        filter = {
            "server__server__refresh_batch__in": batches,
            "is_bot": False
        }
        if engine:
            filter["server__server__engine"] = engine
        count = Player.objects.filter(**filter).count()
        rows.append((dateslice.strftime(dateformat),
                     count / float(max(1, batches.count()))))
    return Chart(
        id="players-chart", kind="LineChart",
        options={'title': 'Players per {0}'.format(resolution),
                 'width': "100%",
                 'height': 300,
                 'legend': 'none',
                 'hAxis': {
                     'maxTextLines': 1
                 },
                 'vAxis': {
                     'minValue': 0,
                     'format': '#.##'
                 }},
        columns=[('string', 'Day'), ('number', 'Players')],
        rows=rows,
        formatters=[
            Formatter(
                column=1, name="NumberFormat",
                options={
                    "fractionDigits": 2
                })
        ])


def wads_popularity_table(daterange, engine):
    files = GameFile.objects.filter(
        servergamefile__server_data__server__refresh_batch__date__range=daterange,
        servergamefile__server_data__server__engine=engine).annotate(
            total=Count('servergamefile__server_data__player')).filter(
                total__gt=0).order_by('-total')[:20]
    if len(files) == 0:
        return None
    total_players = reduce(lambda a, b: a + b, [ f.total for f in files ], 0)
    rows = []
    for file in files:
        percentage = "{0:.2f}%".format(
            100.0 * file.total / float(max(1, total_players)))
        rows.append((file.name, percentage))
    return Table(
        id="wads-popularity-table",
        header="WADs popularity",
        left_header=False,
        rows=rows)


def _first_batch():
    return RefreshBatch.objects.order_by("date").first() or \
        RefreshBatch(date=datetime.fromtimestamp(0))


class Table(object):
    def __init__(self, id=None, header=None, rows=None, left_header=True):
        self.id = id
        self.header = header
        self.rows = rows
        self.left_header = left_header
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


class DecimalCell(object):
    def __init__(self, number, digits=2):
        self.number = number
        self.digits = digits

    def __str__(self):
        return str("{0:." + str(self.digits) + "f}").format(self.number)
