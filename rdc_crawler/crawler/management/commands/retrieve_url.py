#!/usr/bin/env python
# -*- Encoding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:class:`Command` --- Very short description
=======================================
:py:class:`Command` long description

.. moduleauthor::  rdc
"""
from django.core.management.base import BaseCommand

import rdc_crawler.crawler.celery.tasks as tasks

class Command(BaseCommand):
    """
    Initialization description
    
    Args.
        arg...
    """
    def handle(self, url, **options):
        tasks.retrieve_page.delay(url)