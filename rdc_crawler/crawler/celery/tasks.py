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
from __future__ import division
import re
import urlparse
from celery.decorators import task
import rdc_crawler.crawler.models as models
import rdc_crawler.settings as settings


@task
def retrieve_page(url):
    page = models.Page.get_by_url(url)
    if page is None or page.id is None:
        return

    find_links.delay(page.id)


@task
def find_links(doc_id):
    link_single_re = re.compile(r"<a[^>]+href='([^']+)'")
    link_double_re = re.compile(r'<a[^>]+href="([^"]+)"')

    doc = models.Page.load(settings.DB, doc_id)

    raw_links = []
    
    try:
        for match in link_single_re.finditer(doc.content):
            raw_links.append(match.group(1))
        for match in link_double_re.finditer(doc.content):
            raw_links.append(match.group(1))
    except TypeError:
        # Content is not a string
        pass

    doc.links = []
    parse = urlparse.urlparse(doc['url'])
    for link in raw_links:
        if link.startswith('#'):
            continue
        elif link.startswith('http://') or link.startswith('https://'):
            pass
        elif link.startswith('/'):
            link = parse.scheme + '://' + parse.netloc + link
            
        doc.links.append(urlparse.unquote(link.split("#")[0]))

    doc.store(settings.DB)

    calculate_rank.delay(doc.id)

    for link in doc.links:
        page = models.Page.get_by_url(link, update=False)
        if page is not None:
            calculate_rank.delay(page.id)
        else:
            retrieve_page.delay(link)


@task
def calculate_rank(doc_id):
    page = models.Page.load(settings.DB, doc_id)
    if not page:
        return
    links = models.Page.get_links_to_url(page.url)

    rank = 0
    for link in links:
        # link.value[0] -> doc.rank
        # link.value[1] -> doc.links.length
        rank += link.value[0] / link.value[1]

    old_rank = page.rank
    page.rank = rank * 0.85

    if page.rank == 0:
        page.rank = 1.0/settings.DB.view("page/by_url", limit=0).total_rows

    if abs(old_rank - page.rank) > 0.0001:
        page.store(settings.DB)

        for link in page.links:
            linked_page = models.Page.get_by_url(link, update=False)
            if linked_page is not None:
                calculate_rank.delay(linked_page.id)


if __name__ == '__main__':
    pass
