#!/usr/bin/env python
# -*- Encoding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:mod:`~rdc_crawler.crawler.celery.tasks` --- Very short description
======================================
Long description

.. module:: rdc_crawler.crawler.celery.tasks
    :synopsis: Short description

.. moduleauthor::rdc
"""
from celery.decorators import task
import rdc_crawler.crawler.models as models


@task
def retrieve_page(url):
    page = models.Page.get_by_url(url)
    if page is None:
        return

    find_links.delay(page.id)
    
@task
def find_links(url):
    return url


if __name__ == '__main__':
    pass
