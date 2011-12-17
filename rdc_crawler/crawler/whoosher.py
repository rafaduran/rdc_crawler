#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import logging
import time
from traceback import format_exc

from whoosh.fields import TEXT, ID, NUMERIC, Schema
import whoosh.index as windex
from whoosh.store import LockError

import rdc_crawler.settings as settings

SCHEMA = Schema(title=TEXT(stored=True),
                url=ID(stored=True, unique=True),
                desc=ID(stored=True),
                rank=NUMERIC(stored=True, type=float),
                content=TEXT)


def get_index(path):
    """
    Return the current index object if there is one.
    If not attempt to open the index in path.
    If there isn't one in the dir, create one. If there is
    not dir, create the dir.
    """

    if windex.exists_in(path):
        # For now don't trap exceptions, as we don't know what they
        # will be and so we want them to raise destructively.
        index = windex.open_dir(path)
    else:
        try:
            os.makedirs(path)
        except OSError:
            pass
        index = windex.create_in(path, SCHEMA)
    return index


def get_writer(path='{0}/index/'.format(settings.WHOOSH_PATH)):
    """
    Return a writer
    """
    limit = settings.LOCK_ATTEMPTS
    #try:
        #while writer == None and attempts < limit:
    for _ in range(1, limit-1):
#            attempts += 1
        try:
            return get_index(path).writer()
        except LockError, exc:
            logging.error('whoosher: exception getting writer: %s',
                              format_exc(exc))
            time.sleep(1)
        else:
            return get_index(path).writer()

