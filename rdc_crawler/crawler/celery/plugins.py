#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
:py:mod:`rdc_crawler.crawler.celery.plugins` --- Very short description
=====================================
Long description

.. module:: rdc_crawler.crawler.celery.plugins 
    :synopsis: Short description
    
.. moduleauthor::rdc
"""
import abc
import os
import urllib2
import platform
#import logging
import django.core.validators as validators
from django.core.exceptions import ValidationError

import rdc_crawler.settings as settings


class PluginMount(abc.ABCMeta):
    def __init__(cls, name, bases, attrs): #@NoSelf
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)


class LinkParseable(object):
    __metaclass__ = PluginMount
    @abc.abstractmethod
    def parseable(self, link):
        pass


class DjangoValidation(LinkParseable):
    def __init__(self):
        self.validator = validators.URLValidator(validator_user_agent=\
                                            settings.USER_AGENT)
    def parseable(self, link):
        self.validator(link)


class VerifyExists(LinkParseable):
    def parseable(self, url):
        """
        This method takes almost all it's code from
        django.core.validators.URLValidator, but it does follow redirects
        """
        headers = {
                "Accept": "text/xml,application/xml,application/xhtml+xml,"
                    "text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection": "close",
                "User-Agent": settings.USER_AGENT,
            }
        req = urllib2.Request(url, None, headers)
        req.get_method = lambda: 'HEAD'
        #Create an opener that does not support local file access
        opener = urllib2.OpenerDirector()

        handlers = [urllib2.UnknownHandler(),
                    urllib2.HTTPHandler(),
                    urllib2.HTTPDefaultErrorHandler(),
                    urllib2.FTPHandler(),
                    urllib2.HTTPErrorProcessor()]
        try:
            import ssl
            handlers.append(urllib2.HTTPSHandler())
        except:
            #Python isn't compiled with SSL support
            pass
        map(opener.add_handler, handlers)
        try:
            if platform.python_version_tuple() >= (2, 6):
                resp =opener.open(req, timeout=10)
            else:
                resp = opener.open(req)
        except ValueError:
            raise ValidationError(u"Invalid URL", code='invalid')
        except: # urllib2.URLError, httplib.InvalidURL, etc.
            raise ValidationError(u'This URL appears to be a broken link.',
                code='invalid_link')
        else:
            content_type = resp.headers.getheader('Content-Type', None)
            if content_type.split(';')[0].lower() not in ("text/xml",
                    "application/xml", "application/xhtml+xml", "text/html"):
                raise ValidationError(u"Content not parseable",
                                      code='not_parseable')


# TODO: review ':' links: /hosting/search?q=label:web -> 'invalid_link'
def parseable(link):
    errors = []
    for plugin in LinkParseable.plugins:
        try:
            plugin().parseable(link)
        except ValidationError, error:
            errors.append((str(error), error.code))
    return errors
