#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:class:`Command` --- Very short description
=======================================
:py:class:`Command` long description

.. moduleauthor::  rdc
"""
import os
import glob
try:
    import simplejon as json
except ImportError:
    import json

from django.core.management.base import NoArgsCommand

import rdc_crawler.settings as settings


class Command(NoArgsCommand):
    """
    Docstring
    """
    def handle(self, **options):
        couch_dir = os.path.realpath(os.path.split(__file__)[0] + 
                                    "../../../../../couch_views")
        couch_files = glob.glob('{0}/*.json'.format(couch_dir))
        db = settings.DB
        
        for filename in couch_files:
            doc = json.loads(open(filename,'rt').read())
            db[doc["_id"]] = doc 