from .models import *


def general_table():
    batch_count = RefreshBatch.objects.count()
    return Table(
        id="general_table",
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
        id="stats_daterange_table",
        header="Amounts in date range",
        rows=[
            ("Collected batches:", batch_count),
            ("Average server count:",
             Server.count_in_daterange(engine, daterange) / max(1, batch_count)),
            ("Average player count:",
             Player.count_in_daterange(engine, daterange) / max(1, batch_count))
        ])


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
    def cols(self):
        if self.rows:
            return len(self.rows[0])
        return 0


class DateCell(object):
    def __init__(self, date, format):
        self.date = date
        self.format = format

    def __str__(self):
        return self.date.strftime(self.format)
