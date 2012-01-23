#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
from datetime import datetime
import pickle
from robotparser import RobotFileParser
import time
from urlparse import urlparse
from urllib2 import urlopen, Request, HTTPError, URLError
import logging

from django.core.cache import cache
from couchdb.mapping import (TextField, ListField, FloatField, DateTimeField,
            Document, IntegerField)
import couchdb

import rdc_crawler.settings as settings
import functools

# TODO: replace urllib2 by httplib2
class Page(Document):
    doc_type = TextField(default="page")
    url = TextField()
    content = TextField()
    links = ListField(TextField())
    rank = FloatField(default=0)
    last_checked = DateTimeField(default=datetime.now)

    @staticmethod
    def get_by_url(url, update=True):
        result = settings.DB.view("page/by_url", key=url)
        try:
            rows = result.rows
        except (TypeError, KeyError):
            logging.error("Error trying to get doc by url: {url}".format(
                            url=url))
            return
        if len(rows):
            doc = Page.load(settings.DB, rows[0].value)
            if doc is None:
                return None
            if doc.is_valid():
                return doc
        elif not update:
            return None
        else:
            doc = Page(url=url)
        doc.update()
        return doc

    @staticmethod
    def get_links_to_url(url):
        return settings.DB.view("page/links_to_url", key=url).rows

    def update(self):
        parse = urlparse(self.url)
        robotstxt = RobotsTxt.get_by_domain(parse.scheme, parse.netloc)
        if not robotstxt.is_allowed(parse.netloc):
            return False

        while cache.get(parse.netloc) is not None:
            logging.debug("sleeping before updating: {loc}".format(
                            loc=parse.netloc))
            time.sleep(1)

        cache.set(parse.netloc, True, 10)
        req = Request(self.url, None, {"User-Agent": settings.USER_AGENT})

        try:
            resp = urlopen(req)
        except (ValueError, HTTPError, URLError, UnicodeEncodeError), err:
            # If error occurs, link is probably a file that can't be open
            logging.error("Error opening {url}: {error}".format(url=self.url,
                            error=type(err)))
            # Since URL seems not to be valid, clean it
            return

        try:
            if not resp.info()['Content-Type'].startswith("text/html"):
                return
        except KeyError:
            return
        self.content = resp.read().decode('utf-8', 'ignore')
        self.last_checked = datetime.now()

        self.store(settings.DB)

    def is_valid(self):
        return (datetime.now() - self.last_checked).days < 7

    @staticmethod
    def count():
        result = settings.DB.view("page/by_url", limit=0)
        return result.total_rows

    @staticmethod
    def get_top_by_rank(limit=20):
        results = settings.DB.view("page/by_rank", limit=limit,
                                   descending=True)
        return [{'rank': row.key, 'url': row.value} for row in results.rows]


class RobotsTxt(Document):
    doc_type = TextField(default="robotstxt")
    domain = TextField()
    protocol = TextField()
    robot_parser_pickle = TextField()

    def _get_robot_parser(self):
        try:
            return pickle.loads(str(self.robot_parser_pickle))
        except (TypeError, IndexError):
            parser = RobotFileParser()
            parser.set_url(str(self.protocol) + "://" + str(self.domain) + \
                           "/robots.txt")
            self.robot_parser = parser
            return parser

    def _set_robot_parser(self, parser):
        self.robot_parser_pickle = pickle.dumps(parser)

    robot_parser = property(_get_robot_parser, _set_robot_parser)

    def is_valid(self):
        return (time.time() - self.robot_parser.mtime()) < 7 * 24 * 60 * 60

    def update(self):
        while cache.get(self.domain) is not None:
            logging.debug("sleeping before updating: {domain}".format(
                            domain=self.domain))
            time.sleep(1)
        cache.set(self.domain, True, 10)

        parser = self.robot_parser
        logging.debug(parser.url)
        parser.read()
        parser.modified()
        self.robot_parser = parser
        self.store(settings.DB)

    def is_allowed(self, url):
        return self.robot_parser.can_fetch(settings.USER_AGENT, url)

    @staticmethod
    def get_by_domain(protocol, domain):
        result = settings.DB.view("robotstxt/by_domain",
                                  key=[protocol, domain])

        if len(result) > 0:
            doc = RobotsTxt.load(settings.DB, result.rows[0].value)
            if doc.is_valid():
                return doc
        else:
            doc = RobotsTxt(protocol=protocol, domain=domain)
        doc.update()
        return doc


class LastSeen(Document):
    seq = TextField(default=0)
    last_modified = DateTimeField(default=datetime.now)

    def __init__(self, id, **kwargs):
        super(LastSeen, self).__init__(id, **kwargs)
        # Bad hack in order to fix couchdb pip non uniform loading/creating API
        doc = Document.load(id=id, db=settings.DB)
        if doc:
            self._data['_id'] = doc.id
            self._data['_rev'] = doc.rev
            self._data['seq'] = doc['seq']
            self._data['last_modified'] = datetime.strptime(
                doc['last_modified'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def last_seq(self):
        return self.seq

    @last_seq.setter
    def last_seq(self, seq):
        self.seq = seq
        self.store_if_needed()

    def store_if_needed(self):
        if((datetime.now() - self.last_modified).total_seconds()\
                > settings.MAX_TIME):
            self.last_modified = datetime.now()
            self.store(settings.DB)
 
