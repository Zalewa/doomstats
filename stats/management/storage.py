from doomstats.settings import cfg
from doomstats.timestuff import parse_batch_stamp
import json
import os
import tarfile


def archive_filename(month_date):
    return "{}.tar.bz2".format(_month_date_str(month_date))


def _month_date_str(month_date):
    return month_date.strftime("%Y-%m")


def batch_file(date):
    return os.path.join(batch_dir(), batch_filename(date))


def batch_filename(date):
    return date.strftime("%Y-%m-%d_%H-%M%z.json")


def date_from_filename(filename):
    stamp, _ = os.path.splitext(filename)
    return parse_batch_stamp(stamp)


def read_batch(date):
    batch_file = os.path.join(batch_dir(), batch_filename(date))
    if os.path.exists(batch_file):
        with open(batch_file, "r") as f:
            return json.load(f)
    archive_file = os.path.join(archive_dir(), archive_filename(date))
    with tarfile.open(archive_file) as tar:
        batch_file_tarballed = "{}/{}".format(_month_date_str(date),
                                              batch_filename(date))
        with tar.extractfile(batch_file_tarballed) as f:
            return json.load(f)


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
