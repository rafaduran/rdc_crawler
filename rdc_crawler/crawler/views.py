#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
from django.shortcuts import render_to_response
from whoosh.qparser import QueryParser

import rdc_crawler.crawler.models as models
import rdc_crawler.crawler.whoosher as whoosher

def index(req):
    return render_to_response("index.html",
            { "doc_count": models.Page.count(),
                "top_docs": models.Page.get_top_by_rank(limit=20) })

def search(req):
    query = QueryParser("content", schema=whoosher.SCHEMA).parse(req.GET["q"])

    results = whoosher.get_searcher().search(query, limit=100)
    if len(results) > 0:
        max_score = max([res.score for res in results]) or 1
        max_rank = max([res.fields()["rank"] for res in results]) or 1

        combined = []
        for res in results:
            fields = res.fields()
            res.score = res.score/max_score
            res.rank = fields["rank"]/max_rank
            res.combined = res.score + res.rank
            combined.append(res)
        combined.sort(key=lambda x: x.combined, reverse=True)
    else:
        combined = []

    return render_to_response("results.html",
                { "q": req.GET["q"], "results": combined })
