# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2011, Gustavo Narea <me@gustavonarea.net>
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

from repoze.what.groups import BaseGroupAdapter
from repoze.what.predicates import Predicate


__all__ = ["make_request", "MockLogger", "MockPredicate", "MockGroupAdapter"]


def make_request(user=None, helpers=[], logger=None, **environ_vars):
    """Make a WebOb request in a repoze.what environment"""
    environ = {
        'repoze.what.userid': user,
        'repoze.what.helpers': helpers,
        'repoze.what.logger': logger,
        'wsgi.url_scheme': 'http',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': 80,
        'wsgi.input': StringIO()
    }
    environ.update(environ_vars)
    return Request(environ)


class MockLogger(object):
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


class MockGroupAdapter(BaseGroupAdapter):
    """
    Mock group adapter to be used in the tests.
    
    """
    
    def __init__(self, *groups):
        self.groups = set(groups)
        self.queried_groups = []
    
    def _requester_in_any_group(self, request, groups):
        self.queried_groups.append(("any", groups))
        
        is_present = False
        for group in groups:
            if group in self.groups:
                is_present = True
                break
        
        return is_present
    
    def _requester_in_all_groups(self, request, groups):
        self.queried_groups.append(("all", groups))
        
        return groups and groups.issubset(self.groups)
