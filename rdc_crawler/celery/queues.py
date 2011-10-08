#!/usr/bin/env python
# -*- Encoding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:mod:`rdc_crawler.celery.queues` --- Very short description
=====================================
Long description

.. module:: rdc_crawler.celery.queues 
    :synopsis: Short description
    
.. moduleauthor::rdc
"""
CELERY_QUEUES = {
    "retrieve": 
        {"exchange": "default", "exchange_type": "direct", 
         "routing_key": "retrieve"},
    "process": 
        {"exchange": "default", "exchange_type": "direct", 
         "routing_key": "process "},
    "celery": {"exchange": "default", "exchange_type": "direct", 
               "routing_key": "celery"}}

class MyRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task == "rdc_crawler.celery.tasks.retrieve_page":
            return { "queue": "retrieve" }
        else:
            return { "queue": "process" }

CELERY_ROUTES = (MyRouter(), )