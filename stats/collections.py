from .models import *
from googlecharts.collections import Chart, Formatter
from doomstats.timestuff import daterange_resolution
from datetime import datetime, timedelta
from presentation.models import BatchStatistics, GameFileStatistics, \
    IwadPopularity, ServerPopularity


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
    counters = BatchStatistics.avg_in_daterange(engine, daterange)
    return Table(
        id="stats-daterange-table",
        header="Amounts in date range",
        rows=[
            ("Collected batches:", RefreshBatch.objects.filter(date__range=daterange).count()),
            ("Average server count:", DecimalCell(counters.server_count)),
            ("Average player count:", DecimalCell(counters.human_player_count))
        ])


def players_chart(daterange, engine=None):
    resolution = daterange_resolution(daterange)
    rows = _build_players_chart_data(daterange, engine)
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


def _build_players_chart_data(daterange, engine):
    resolution = daterange_resolution(daterange)
    dateslices = RefreshBatch.slice(daterange, resolution)
    if not dateslices:
        return []
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
        if resolution == "day":
            nextdate = dateslice + timedelta(days=1)
        elif resolution == "hour":
            nextdate = dateslice + timedelta(hours=1)
        count = BatchStatistics.avg_in_daterange(engine, (dateslice, nextdate))
        rows.append((dateslice.strftime(dateformat), count.human_player_count))
    return rows


def wads_popularity_table(daterange, engine):
    files = GameFileStatistics.top(engine, daterange, amount=20)
    total_players = reduce(lambda a, b: a + b, [ f['human_player_count'] for f in files ], 0)
    rows = []
    if len(files) > 0:
        for file in files:
            rows.append((file['gamefile__name'],
                         PercentageCell(file['human_player_count'], total_players)))
    else:
        rows.append(("No PWADs were played in given time range.",))
    return Table(
        id="wads-popularity-table",
        header="WADs popularity",
        left_header=False,
        rows=rows,
        body_css_class="listing")


def servers_popularity_table(daterange, engine):
    servers = ServerPopularity.top(engine, daterange, amount=20)
    total_players = reduce(lambda a, b: a + b, [ s["human_player_count"] for s in servers ], 0)
    rows = []
    if len(servers) > 0:
        for server in servers:
            rows.append(
                (server["server__data__name__name"],
                 PercentageCell(server["human_player_count"], total_players)))
    else:
        rows.append(("No servers had players in given time range.",))
    return Table(
        id="servers-popularity-table",
        header="Servers popularity",
        left_header=False,
        rows=rows,
        body_css_class="listing")


def iwad_popularity_chart(daterange, engine):
    iwads = IwadPopularity.top(engine, daterange)
    total_players = sum([iwad["human_player_count"] for iwad in iwads], 0)
    if not total_players:
        return None
    rows = []
    for iwad in iwads:
        rows.append((iwad["iwad__name"],
                     _to_percent(iwad["human_player_count"], total_players)))
    # Some magic. Maybe there's a better way to
    # appease Google Charts? If some margin is not
    # left between the Chart/height and Chart/chartArea/height
    # then horizontal axis label will not appear.
    MIN_HEIGHT = 40
    ROW_HEIGHT = 25
    AXIS_LABEL_HEIGHT_MARGIN = ROW_HEIGHT
    height = ROW_HEIGHT * len(rows)
    return Chart(
        id="iwad-popularity-chart", kind="BarChart",
        options={
            'title': 'IWAD popularity',
            'width': '100%',
            'height': height + MIN_HEIGHT + AXIS_LABEL_HEIGHT_MARGIN,
            'legend': 'none',
            'vAxis': {
                'maxTextLines': 1,
            },
            'chartArea': {
                'left': 100,
                'top': 20,
                'height': max(MIN_HEIGHT, height - AXIS_LABEL_HEIGHT_MARGIN),
                'width': '75%'
            }
        },
        columns=[('string', 'IWAD'), ('number', 'Players')],
        rows=rows,
        formatters=[
            Formatter(
                column=1, name="NumberFormat",
                options={
                    "fractionDigits": 2,
                    "suffix": "%"
                })
        ])


def _first_batch():
    return RefreshBatch.objects.order_by("date").first() or \
        RefreshBatch(date=datetime.fromtimestamp(0))


class Table(object):
    def __init__(self, id=None, header=None, rows=None, left_header=True,
                 body_css_class=""):
        self.id = id
        self.header = header
        self.rows = rows
        self.left_header = left_header
        self.body_css_class = body_css_class
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
        number = self.number
        if number is None:
            number = 0.0
        return str("{0:." + str(self.digits) + "f}").format(number)


class PercentageCell(object):
    def __init__(self, number, total, digits=2):
        self.number = number
        self.total = total
        self.digits = digits

    def __str__(self):
        return _to_percent_str(self.number, self.total, self.digits)


def _to_percent_str(value, total, digits=2):
    if total == 0:
        return "N/A"
    return str("{0:." + str(digits) + "f}%").format(_to_percent(value, total))


def _to_percent(value, total):
    return (float(value) / total) * 100.0
