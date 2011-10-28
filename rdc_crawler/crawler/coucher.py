#!/usr/bin/env python
# -*- Encoding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:mod:`~rdc_crawler.crawler.coucher` --- Very short description
======================================
Long description

.. module:: rdc_crawler.crawler.coucher
    :synopsis: Short description

.. moduleauthor::rdc
"""
import couchdb

import rdc_crawler.settings as settings


def set_last_change(last):
    settings.DB.save(last)


def get_last_change():
    try:
        return settings.DB['last_changed']
    except couchdb.http.ResourceNotFound:
        last = settings.DB['last_changed'] = dict(last_seq=0)
        return last
