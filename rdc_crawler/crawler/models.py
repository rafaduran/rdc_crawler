#!/usr/bin/env python
# -*- Encoding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
from datetime import datetime
import pickle
from robotparser import RobotFileParser
import time

from django.core.cache import cache

from couchdb.mapping import (TextField, ListField, FloatField, DateTimeField,
            Document)

import rdc_crawler.settings as settings
# Create your models here.

class Page(Document):
    type = TextField(default="page")
    
    url = TextField()
    
    content = TextField()
    
    links = ListField(TextField())
    
    rank = FloatField(default=0)
    
    last_checked = DateTimeField(default=datetime.now)
    
    
class RobotsTxt(Document):
    type = TextField(default="robotstxt")
    
    domain = TextField()
    
    protocol = TextField()
    
    robot_parser_pickle = TextField()
    
    
    def _get_robot_parser(self):
        try:
            return pickle.loads(self.robot_parser_pickle)
        except TypeError:
            parser = RobotFileParser()
            parser.set_url(str(self.protocol) + "://" + str(self.domain) + \
                           "/robots.txt")
            self.robot_parser = parser
            return parser
    
    
    def _set_robot_parser(self, parser):
        self.robot_parser_pickle = pickle.dumps(parser)
        
    robot_parser = property(_get_robot_parser, _set_robot_parser)
    
    
    def is_valid(self):
        return (time.time() - self.robot_parser.mtime() < 7*24*60*60)
    
    
    def update(self):
        while cache.get(self.domain) is not None:
            time.sleep(1)
        cache.set(self.domain, True, 10)
        
        parser = self.robot_parser
        print parser.url
        parser.read()
        parser.modified()
        self.robot_parser = parser
        
        self.store(settings.db)
        
    
    def is_allowed(self, url):
        return self.robot_parser.can_fetch(settings.USER_AGENT, url)
    
    
    @staticmethod
    def get_by_domain(protocol, domain):
        result = settings.db.view("robotstxt/by_domain", Key=[protocol, domain])
        
        if len(result) > 0:
            doc = RobotsTxt.load(settings.db, result.rows[0].value)
            if doc.is_valid():
                return doc
        else:
            doc = RobotsTxt(protocol=protocol, domain=domain)
        doc.update()
        return doc
    