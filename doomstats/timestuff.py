from datetime import datetime, timedelta
from django.utils import timezone


class ParseError(ValueError):
    pass


def parse_rfc3339_stamp(stamp, splitter='T'):
    stamp, tz = _split_tz(stamp)
    date = datetime.strptime(stamp, '%Y-%m-%d{0}%H:%M:%S'.format(splitter))
    date = date.replace(tzinfo=parse_timezone_offset(tz))
    return date


def parse_batch_stamp(stamp):
    stamp, tz = _split_tz(stamp)
    date = datetime.strptime(stamp, '%Y-%m-%d_%H-%M')
    date = date.replace(tzinfo=parse_timezone_offset(tz))
    return date


def _split_tz(stamp):
    tz_index = _get_tz_offset(stamp)
    tz = stamp[tz_index:]
    stamp = stamp[:tz_index]
    return stamp, tz


def _get_tz_offset(stamp):
    tz_index = stamp.rfind("+")
    if tz_index < 0:
        tz_index = stamp.rfind("-")
    if tz_index < 0:
        raise ParseError("no TZ offset")
    return tz_index


def parse_timezone_offset(offset):
    return timezone.get_fixed_timezone(_timezone_offset(offset))


def day_range(date1, date2):
    date1, date2 = min(date1, date2), max(date1, date2)
    date1 = date1.replace(hour=0, minute=0, second=0, microsecond=0)
    date2 = date2.replace(hour=0, minute=0, second=0, microsecond=0)
    date2 += timedelta(days=1)
    return date1, date2


def daterange_resolution(daterange):
    date1, date2 = min(daterange), max(daterange)
    delta = date2 - date1
    if delta.days > 7:
        return "day"
    else:
        return "hour"


def _timezone_offset(offset):
    if offset[0] == '+':
        modifier = 1
    elif offset[0] == '-':
        modifier = -1
    else:
        raise ParseError('no time offset sign')
    offset = offset[1:]
    if ':' in offset:
        hours, minutes = offset.split(":")
    else:
        hours = offset[:3]
        minutes = offset[3:]
    return modifier * int(hours) * 60 + int(minutes)
