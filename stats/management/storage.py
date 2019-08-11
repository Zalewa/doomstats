from doomstats.settings import cfg
from doomstats.timestuff import parse_batch_stamp
import os


def store_filename(month_date):
    return month_date.strftime("%Y-%m.tar.bz2")


def batch_filename(date):
    return date.strftime("%Y-%m-%d_%H-%M%z.json")


def date_from_filename(filename):
    stamp, _ = os.path.splitext(filename)
    return parse_batch_stamp(stamp)


def batch_dir():
    return _get_existing_dir(cfg.get("batch_dir"))


def archive_dir():
    return _get_existing_dir(cfg.get("archive_dir"))


def _get_existing_dir(path):
    if not path:
        raise ValueError("directory unspecified")
    if not os.path.isdir(path):
        raise IOError("path '{}' is not a directory".format(path))
    return path
