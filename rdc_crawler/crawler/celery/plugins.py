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

EXT_FILE = '{ext_path}/extensions.txt'.format(ext_path=os.path.realpath(
                os.path.split(__file__)[0] + "../../../../tools"))

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


class FilterByExtension(LinkParseable):
    def __init__(self, ext_file=EXT_FILE):
        self.wrong_extensions = set() 
        with open(ext_file, 'rt') as  ext:
            for line in ext:
                self.wrong_extensions.add(line.split()[0])
                
    def parseable(self, link, extensions=None):
        extensions = extensions or self.wrong_extensions
        for extension in extensions:
            if link.endswith('.{extension}'.format(extension=extension)):
                raise ValueError("*.{extension} aren't parseable".format(
                                    extension=extension))


class FilterKnownBadUrls(LinkParseable):
    bad_urls = set(('javascript', 'mailto', '__'))
    def parseable(self, link, bad_urls=bad_urls):
        for url in bad_urls:
            if link.startswith(url):
                raise ValueError('{link} is a known bad URL'.format(link=link))


def parseable(link):
    errors = []
    for plugin in LinkParseable.plugins:
        try:
            plugin().parseable(link)
        except ValueError, e:
            errors.append(str(e))
    return errors