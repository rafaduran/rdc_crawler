#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
import uuid
from django.test import TestCase
from rdc_crawler.crawler.celery.tasks import find_links
from rdc_crawler.crawler.celery.plugins import parseable
from rdc_crawler.settings import DB

CONTENT = u"""\n\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n  \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n  <head>\n    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />\n    \n    <title>Welcome to Blga’s documentation! &mdash; Blga v1.1.0 documentation</title>\n    <link rel=\"stylesheet\" href=\"_static/default.css\" type=\"text/css\" />\n    <link rel=\"stylesheet\" href=\"_static/pygments.css\" type=\"text/css\" />\n    <script type=\"text/javascript\">\n      var DOCUMENTATION_OPTIONS = {\n        URL_ROOT:    '',\n        VERSION:     '1.1.0',\n        COLLAPSE_INDEX: false,\n        FILE_SUFFIX: '.html',\n        HAS_SOURCE:  true\n      };\n    </script>\n    <script type=\"text/javascript\" src=\"_static/jquery.js\"></script>\n    <script type=\"text/javascript\" src=\"_static/underscore.js\"></script>\n    <script type=\"text/javascript\" src=\"_static/doctools.js\"></script>\n    <link rel=\"top\" title=\"Blga v1.1.0 documentation\" href=\"#\" />\n    <link rel=\"next\" title=\"Classes\" href=\"source/classes.html\" /> \n  </head>\n  <body>\n    <div class=\"related\">\n      <h3>Navigation</h3>\n      <ul>\n        <li class=\"right\" style=\"margin-right: 10px\">\n          <a href=\"genindex.html\" title=\"General Index\"\n             accesskey=\"I\">index</a></li>\n        <li class=\"right\" >\n          <a href=\"source/classes.html\" title=\"Classes\"\n             accesskey=\"N\">next</a> |</li>\n        <li><a href=\"#\">Blga v1.1.0 documentation</a> &raquo;</li> \n      </ul>\n    </div>  \n\n    <div class=\"document\">\n      <div class=\"documentwrapper\">\n        <div class=\"bodywrapper\">\n          <div class=\"body\">\n            \n  <div class=\"section\" id=\"welcome-to-blga-s-documentation\">\n<h1>Welcome to Blga&#8217;s documentation!<a class=\"headerlink\" href=\"#welcome-to-blga-s-documentation\" title=\"Permalink to this headline\">¶</a></h1>\n<p>Binary-coded LGA (BLGA) is a Steady-state GA that\ninserts one single new member into the population (P) in each iteration. It uses\na crowding replacement method (restricted tournament selection (RTS) in\norder to force a member of the current population to perish and to make room\nfor the new oﬀspring. It is important to know that RTS favours the formation\nof niches in P (groups of chromosomes with high quality located in diﬀerent\nand scattered regions of the search space). In addition, the BLGA maintains an\nexternal chromosome, the leader chromosome (C<sub>L</sub>), which is always\nselected as one of the parents for the crossover operation. The following\nsections indicate the main components of the BLGA.</p>\n</div>\n<div class=\"section\" id=\"how-it-works\">\n<h1>How it works?<a class=\"headerlink\" href=\"#how-it-works\" title=\"Permalink to this headline\">¶</a></h1>\n<p>The general BLGA&#8217;s schema is represented in the next image:</p>\n<div class=\"figure align-center\">\n<a class=\"reference internal image-reference\" href=\"_images/schema.png\"><img alt=\"Schema\" src=\"_images/schema.png\" style=\"width: 628.0px; height: 289.0px;\" /></a>\n<p class=\"caption\">BLGA&#8217;s schema</p>\n</div>\n</div>\n<div class=\"section\" id=\"source-code\">\n<h1>Source code<a class=\"headerlink\" href=\"#source-code\" title=\"Permalink to this headline\">¶</a></h1>\n<div class=\"toctree-wrapper compound\">\n<ul>\n<li class=\"toctree-l1\"><a class=\"reference internal\" href=\"source/classes.html\">Classes</a><ul>\n<li class=\"toctree-l2\"><a class=\"reference internal\" href=\"source/classes.html#local-searcher-classes\">Local searcher classes:</a></li>\n<li class=\"toctree-l2\"><a class=\"reference internal\" href=\"source/classes.html#fitness-function-classes\">Fitness function classes</a></li>\n<li class=\"toctree-l2\"><a class=\"reference internal\" href=\"source/classes.html#result-writers-classes\">Result writers classes</a></li>\n<li class=\"toctree-l2\"><a class=\"reference internal\" href=\"source/classes.html#support-classes\">Support classes</a></li>\n</ul>\n</li>\n</ul>\n</div>\n</div>\n<div class=\"section\" id=\"indices-and-tables\">\n<h1>Indices and tables<a class=\"headerlink\" href=\"#indices-and-tables\" title=\"Permalink to this headline\">¶</a></h1>\n<ul class=\"simple\">\n<li><a class=\"reference internal\" href=\"genindex.html\"><em>Index</em></a></li>\n<li><a class=\"reference internal\" href=\"search.html\"><em>Search Page</em></a></li>\n</ul>\n</div>\n\n\n          </div>\n        </div>\n      </div>\n      <div class=\"sphinxsidebar\">\n        <div class=\"sphinxsidebarwrapper\">\n  <h3><a href=\"#\">Table Of Contents</a></h3>\n  <ul>\n<li><a class=\"reference internal\" href=\"#\">Welcome to Blga&#8217;s documentation!</a></li>\n<li><a class=\"reference internal\" href=\"#how-it-works\">How it works?</a></li>\n<li><a class=\"reference internal\" href=\"#source-code\">Source code</a><ul>\n</ul>\n</li>\n<li><a class=\"reference internal\" href=\"#indices-and-tables\">Indices and tables</a></li>\n</ul>\n\n  <h4>Next topic</h4>\n  <p class=\"topless\"><a href=\"source/classes.html\"\n                        title=\"next chapter\">Classes</a></p>\n  <h3>This Page</h3>\n  <ul class=\"this-page-menu\">\n    <li><a href=\"_sources/index.txt\"\n           rel=\"nofollow\">Show Source</a></li>\n  </ul>\n<div id=\"searchbox\" style=\"display: none\">\n  <h3>Quick search</h3>\n    <form class=\"search\" action=\"search.html\" method=\"get\">\n      <input type=\"text\" name=\"q\" size=\"18\" />\n      <input type=\"submit\" value=\"Go\" />\n      <input type=\"hidden\" name=\"check_keywords\" value=\"yes\" />\n      <input type=\"hidden\" name=\"area\" value=\"default\" />\n    </form>\n    <p class=\"searchtip\" style=\"font-size: 90%\">\n    Enter search terms or a module, class or function name.\n    </p>\n</div>\n<script type=\"text/javascript\">$('#searchbox').show(0);</script>\n        </div>\n      </div>\n      <div class=\"clearer\"></div>\n    </div>\n    <div class=\"related\">\n      <h3>Navigation</h3>\n      <ul>\n        <li class=\"right\" style=\"margin-right: 10px\">\n          <a href=\"genindex.html\" title=\"General Index\"\n             >index</a></li>\n        <li class=\"right\" >\n          <a href=\"source/classes.html\" title=\"Classes\"\n             >next</a> |</li>\n        <li><a href=\"#\">Blga v1.1.0 documentation</a> &raquo;</li> \n      </ul>\n    </div>\n    <div class=\"footer\">\n        &copy; Copyright 2011, Rafael Durán Castañeda.\n      Created using <a href=\"http://sphinx.pocoo.org/\">Sphinx</a> 1.0.1.\n    </div>\n  </body>\n</html>""",
URL = u"http://rdc-blga.appspot.com/html/index.html"


class FindLinksTest(TestCase):
    def setUp(self):
        self.doc = DB[str(uuid.uuid1())] = dict(content=CONTENT, url=URL,
                                     last_checked=unicode(datetime.now()),
                                     doc_type=u"page")
        find_links.is_eager = True

    def tearDown(self):
        del DB[self.doc['_id']]

    def test_find_links_ok(self):
        links = find_links(self.doc['_id'])
        self.assertListEqual(links,
            [u'http://rdc-blga.appspot.com/genindex.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/_images/schema.png',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/genindex.html',
             u'http://rdc-blga.appspot.com/search.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://rdc-blga.appspot.com/_sources/index.txt',
             u'http://rdc-blga.appspot.com/genindex.html',
             u'http://rdc-blga.appspot.com/source/classes.html',
             u'http://sphinx.pocoo.org/'])

    def test_parseable_ok(self):
        for link in [u'genindex.html', u'source/classes.html',
            u'source/classes.html', u'source/classes.html',
            u'source/classes.html', u'source/classes.html',
            u'source/classes.html', u'genindex.html', u'search.html',
            u'source/classes.html', u'genindex.html',
            u'source/classes.html', u'http://sphinx.pocoo.org/']:
            errors = parseable(link)
            self.assertListEqual(errors, [],[error for error in errors])

    def test_parseable_fail(self):
        for link in ['test.js' , 'test.css', 'test.zip', 'test.jpg',
            '_images/schema.png', 'javascript:void(0)',
            'mailto:example@example.com',
            "http://rdc-python.googlecode.com/files/eclipse_templates.zip"]:
            errors = parseable(link)
            self.assertFalse([] == errors, "{link} is not parseable, but no"
                             " errors weren't found".format(link=link))
