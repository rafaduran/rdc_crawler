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
import logging
from django.utils.encoding import iri_to_uri
from celery.decorators import task
from celery.task.sets import subtask
import rdc_crawler.crawler.models as models
import rdc_crawler.settings as settings
import rdc_crawler.crawler.celery.plugins as plugins

# TODO: Use callbacks on retrieve_page
@task
def retrieve_page(url):
    page = models.Page.get_by_url(url)
    if page is None or page.id is None:
        return

    find_links.delay(page.id, links_callback=retrieve_page,
                     doc_callback=calculate_rank)


@task
def find_links(doc_id, links_callback=None, doc_callback=None):
    link_single_re = re.compile(r"<a[^>]+href='([^']+)'")
    link_double_re = re.compile(r'<a[^>]+href="([^"]+)"')

    doc = models.Page.load(settings.DB, doc_id)
    if doc is None or not len(doc.content):
        return

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
    for index,link in enumerate(raw_links):
        errors = plugins.parseable(link)
        if errors:
            logging.error(errors)
            del raw_links[index]
            continue
        if link.startswith('#') or link.startswith("//"):
            continue
        elif link.startswith('http://') or link.startswith('https://'):
            pass
        elif link.startswith('/'):
            link = parse.scheme + '://' + parse.netloc + link
        else:
            link = parse.scheme + '://' + parse.netloc + '/' + link

        doc.links.append(iri_to_uri(link.split("#")[0]))

    doc.store(settings.DB)

    # TODO: subtask this
    calculate_rank.delay(doc.id)

    for index, link in enumerate(doc.links):
        page = models.Page.get_by_url(link, update=False)
        if page is None and not links_callback is None:
            # Do I need a substask or task here?
            links_callback.delay(link)
        elif not links_callback is None:
            subtask(doc_callback).delay(page.id)
    else:
        # Useful for testing
        if links_callback is None:
            return doc.links


@task
def calculate_rank(doc_id):
    try:
        page = models.Page.load(settings.DB, doc_id)
        if page is None:
            return
    except TypeError:
        return
# I'm getting this error quiet frequently
# File "/opt/rdc-web-crawler/rdc_crawler/crawler/celery/tasks.py", line 85,=
# in calculate_rank
#    page =3D models.Page.load(settings.DB, doc_id)
#  File "/opt/rdc-web-crawler/.crawler-venv/local/lib/python2.7/site-package=
# s/couchdb/mapping.py", line 363, in load
#    doc =3D db.get(id)
#  File "/opt/rdc-web-crawler/.crawler-venv/local/lib/python2.7/site-package=
# s/couchdb/client.py", line 525, in get
#    _, _, data =3D self.resource.get_json(id, **options)
#  File "/opt/rdc-web-crawler/.crawler-venv/local/lib/python2.7/site-package=
# s/couchdb/http.py", line 394, in get_json
#    if 'application/json' in headers.get('content-type'):
# TypeError: argument of type 'NoneType' is not iterable
    links = models.Page.get_links_to_url(page.url)

    rank = 0
    for link in links:
        # link.value[0] -> doc.rank
        # link.value[1] -> doc.links.length
        rank += link.value[0] / link.value[1]

    old_rank = page.rank
    page.rank = rank * 0.85

    if page.rank == 0:
        page.rank = 1.0 / settings.DB.view("page/by_url", limit=0).total_rows

    if abs(old_rank - page.rank) > 0.0001:
        page.store(settings.DB)

        for link in page.links:
            linked_page = models.Page.get_by_url(link, update=False)
            if linked_page is not None:
                calculate_rank.delay(linked_page.id)


if __name__ == '__main__':
    pass
