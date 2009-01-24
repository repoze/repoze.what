# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
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
Test suite for repoze.what built-in predicates.

This module also defines utilities and mock objects for the test suite.

"""

import unittest

from repoze.what.predicates import Predicate, PredicateError


#{ Utilities


class BasePredicateTester(unittest.TestCase):
    """Base test case for predicates."""
    
    def eval_met_predicate(self, p, environ):
        """Evaluate a predicate that should be met"""
        credentials = environ.get('repoze.what.credentials')
        self.assertEqual(p.evaluate(environ, credentials), None)
    
    def eval_unmet_predicate(self, p, environ, expected_error):
        """Evaluate a predicate that should not be met"""
        credentials = environ.get('repoze.what.credentials')
        try:
            p.evaluate(environ, credentials)
            self.fail('Predicate must not be met; expected error: %s' %
                      expected_error)
        except PredicateError, error:
            self.assertEqual(unicode(error), expected_error)


def make_environ(user, groups=None, permissions=None):
    """Make a WSGI enviroment with the ``credentials`` dict"""
    
    credentials = {'repoze.what.userid': user}
    if groups:
        credentials['groups'] = groups
    if permissions:
        credentials['permissions'] = permissions
    environ = {'repoze.what.credentials': credentials}
    return environ


#{ Mock definitions


class EqualsTwo(Predicate):
    message = "Number %(number)s doesn't equal 2"
    
    def evaluate(self, environ, credentials):
        number = environ.get('test_number')
        if number != 2:
            self.unmet(number=number)


class EqualsFour(Predicate):
    message = "Number %(number)s doesn't equal 4"
    
    def evaluate(self, environ, credentials):
        number = environ.get('test_number')
        if number != 4:
            self.unmet(number=number)


class GreaterThan(Predicate):
    message = "%(number)s is not greater than %(compared_number)s"
    
    def __init__(self, compared_number, **kwargs):
        super(GreaterThan, self).__init__(**kwargs)
        self.compared_number = compared_number
        
    def evaluate(self, environ, credentials):
        number = environ.get('test_number')
        if not number > self.compared_number:
            self.unmet(number=number, compared_number=self.compared_number)


#}
