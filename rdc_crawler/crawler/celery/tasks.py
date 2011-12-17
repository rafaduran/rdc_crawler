#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


@task
def retrieve_page(url, callback=None):
    page = models.Page.get_by_url(url)
    if page is None or page.id is None:
        return

    if not callback is None:
        subtask(callback).delay(page.id, links_callback=retrieve_page,
                     callback_for_links_callback=find_links,
                     doc_callback=calculate_rank,
                     callback_for_doc_callback=calculate_rank)


@task
def find_links(doc_id,  doc_callback=None, callback_for_doc_callback=None,
               links_callback=None, callback_for_links_callback=None):
    link_single_re = re.compile(r"<a[^>]+href='([^']+)'")
    link_double_re = re.compile(r'<a[^>]+href="([^"]+)"')

    doc = models.Page.load(settings.DB, doc_id)
    if doc is None or not len(doc.content):
        return

    raw_links = set()

    try:
        for match in link_single_re.finditer(doc.content):
            raw_links.add(match.group(1))
        for match in link_double_re.finditer(doc.content):
            raw_links.add(match.group(1))
    except TypeError:
        # Content is not a string
        pass

    doc.links = []
    parseable_links = []
    parse = urlparse.urlparse(doc['url'])

    for link in raw_links:
        possible_paths = []
        if link.startswith('#') or link.startswith("//"):
            continue
        elif link.startswith('http://') or link.startswith('https://'):
            pass
        elif link.startswith('/'):
            possible_paths = parse.path.split('/')[:-1]
        else:
            link = '/' + link
            possible_paths = parse.path.split('/')[:-1]

        link, parseable = check(iri_to_uri(link.split("#")[0]), parse,
                                possible_paths)
        link and doc.links.append(link)
        if parseable:
            parseable_links.append(link)

    doc.store(settings.DB)

    if doc_callback is not None:
        subtask(doc_callback).delay(doc.id, callback=callback_for_doc_callback)

    for link in parseable_links:
        page = models.Page.get_by_url(link, update=False)
        if page is None and not links_callback is None:
            # Do I need a substask or task here?
            links_callback.delay(link, callback=callback_for_links_callback)
        elif not doc_callback is None:
            subtask(doc_callback).delay(page.id,
                callback=callback_for_doc_callback)
    else:
        # Useful for testing
        if links_callback is None:
            return doc.links, parseable_links


def check(link, parse, possible_paths=None):
    if not possible_paths:
        errors = plugins.parseable(link)
        if not errors:
            return link, True
        elif ('invalid' in [error[1] for error in errors] or
            'invalid_link' in [error[1] for error in errors]):
            return None, False
        else:
            return link, False
    else:
        parts = [possible_paths[:i] for i in range(1,len(possible_paths)+1)]
        paths = ['/'.join(part) for part in parts]
        possible_links = ['{scheme}://{netloc}{path}{link}'.format(
                            scheme=parse.scheme, netloc=parse.netloc,
                            path=path, link=link) for path in paths]
        for plink in possible_links:
            errors = plugins.parseable(plink)
            result = plink
            if not errors:
                return plink, True
            else:
                for error in errors:
                    if error[1] == 'invalid' or error[1] == 'invalid_link':
                        result = None
                    elif error[1] == 'not_parseable':
                        break
        logging.error("{errors}, URL: {link}".format(link=link, errors=\
                        ' '.join(['{0}{1}'.format(error[0], error[1]) for\
                            error in errors])))
        logging.error("Links checked:\n {links}".format(links=\
                        '\t'.join([link for link in possible_links])))
        return result, False


@task
def calculate_rank(doc_id, callback=None):
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
            if linked_page is not None and callback is not None:
                subtask(callback).delay(linked_page.id)


if __name__ == '__main__':
    pass
