# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
Utilities for the test suite of :mod:`repoze.what`.

"""

from StringIO import StringIO

from repoze.what.adapters import BaseSourceAdapter

from webob import Request

__all__ = ['make_environ', 'make_request', 'FakeGroupSourceAdapter', 'FakePermissionSourceAdapter', 
           'FakeLogger']


def make_environ(user=None, helpers=[], logger=None, **kwargs):
    """Make a WSGI enviroment with repoze.what-specific items"""
    
    environ = {
        'repoze.what.userid': user,
        'repoze.what.helpers': helpers,
        'repoze.what.logger': logger,
        'wsgi.url_scheme': 'http',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': 80,
        'wsgi.input': StringIO()
    }
    environ.update(kwargs)
    return environ


def make_request(**environ_vars):
    """Make a WebOb request in a repoze.what environment"""
    environ = make_environ(**environ_vars)
    return Request(environ)


class FakeGroupSourceAdapter(BaseSourceAdapter):
    """
    Mock group source adapter.
    
    The `fake` source it handles contains the following groups:
    
    * ``admins``: ``rms``
    * ``developers``: ``rms``, ``linus``
    * ``trolls``: ``sballmer``
    * ``python``: `(empty)`
    * ``php``: `(empty)`
    
    """

    def __init__(self, *args, **kwargs):
        super(FakeGroupSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'admins': set([u'rms']),
            u'developers': set([u'rms', u'linus']),
            u'trolls': set([u'sballmer']),
            u'python': set(),
            u'php': set()
            }

    def _get_all_sections(self):
        return self.fake_sections

    def _get_section_items(self, section):
        return self.fake_sections[section]

    def _find_sections(self, credentials):
        username = credentials['repoze.what.userid']
        return set([n for (n, g) in self.fake_sections.items()
                    if username in g])

    def _include_items(self, section, items):
        self.fake_sections[section] |= items

    def _exclude_items(self, section, items):
        for item in items:
            self.fake_sections[section].remove(item)

    def _item_is_included(self, section, item):
        return item in self.fake_sections[section]

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        del self.fake_sections[section]

    def _section_exists(self, section):
        return section in self.fake_sections


class FakePermissionSourceAdapter(FakeGroupSourceAdapter):
    """
    `Mock` permissions source adapter.
    
    The `fake` source it handles contains the following permissions:
    
    * ``see-site``: ``trolls``
    * ``edit-site: ``admins``, ``developers``
    * ``commit``: ``developers``
    
    """

    def __init__(self, *args, **kwargs):
        super(FakePermissionSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'see-site': set([u'trolls']),
            u'edit-site': set([u'admins', u'developers']),
            u'commit': set([u'developers'])
            }

    def _find_sections(self, group_name):
        return set([n for (n, p) in self.fake_sections.items()
                    if group_name in p])


class FakeLogger(object):
    """A mock Python logger."""
    
    def __init__(self):
        self.messages = {
            'critical': [],
            'error': [],
            'warning': [],
            'info': [],
            'debug': []
            }
    
    def critical(self, msg):
        self.messages['critical'].append(msg)
    
    def error(self, msg):
        self.messages['error'].append(msg)
    
    def warning(self, msg):
        self.messages['warning'].append(msg)
    
    def info(self, msg):
        self.messages['info'].append(msg)
    
    def debug(self, msg):
        self.messages['debug'].append(msg)
