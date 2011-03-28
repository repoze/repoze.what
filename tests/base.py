# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2010, Gustavo Narea <me@gustavonarea.net>
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

from webob import Request

from repoze.what.predicates import Predicate


__all__ = ["FakeLogger", "MockPredicate", "make_environ", "make_request"]


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


class MockPredicate(Predicate):
    """Base class for mock predicates."""
    
    def __init__(self, result=True):
        self.result = result
        self.evaluated = False
        super(MockPredicate, self).__init__()
    
    def check(self, request, credentials):
        return self.result


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
