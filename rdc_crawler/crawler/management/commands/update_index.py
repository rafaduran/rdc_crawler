#!/usr/bin/env python
# -*- Encoding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:class:`Command` --- Very short description
=======================================
:py:class:`Command` long description

.. moduleauthor::  rdc
"""
import re

import couchdb
import BeautifulSoup as bsoup
from django.core.management.base import BaseCommand

import rdc_crawler.crawler.whoosher as whoosher
import rdc_crawler.crawler.coucher as coucher
import rdc_crawler.settings as settings


class Command(BaseCommand):
    """
    Initialization description

    Args.
        arg...
    """
    def handle(self, **options):
        desc_re = re.compile(r"^description$", re.I)
        since = coucher.get_last_change()
        writer = whoosher.get_writer()
        try:
            while True:
                changes = settings.DB.changes(since=since['last_seq'])
                since['last_seq'] = changes["last_seq"]
                for changeset in changes["results"]:
                    try:
                        doc = settings.DB[changeset["id"]]
                    except couchdb.http.ResourceNotFound:
                        continue
                if "doc_type" in doc and doc["doc_type"] == "page":
                    soup = bsoup.BeautifulSoup(doc["content"])
                    if soup.body is None:
                        continue
                    desc = soup.findAll("meta", attrs={"name": desc_re})

                    writer.update_document(
                        title=unicode(soup.title(text=True)[0])\
                        if soup.title is not None\
                            and len(soup.title(text=True)) > 0\
                            else doc["url"],
                        url=unicode(doc["url"]),
                        desc=unicode(desc[0]["content"]) if len(desc) > 0\
                            and desc[0]["content"] is not None else u"",
                        rank=doc["rank"],
                        content=unicode(soup.title(text=True)[0] + "\n" +
                            doc["url"] + "\n" + "".join(soup.body(text=True))))
                    writer.commit()
                    writer = whoosher.get_writer()
                coucher.set_last_change(since)
        finally:
            coucher.set_last_change(since)
