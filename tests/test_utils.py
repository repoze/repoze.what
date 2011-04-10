# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
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
Tests for the utilities denied at :mod:`repoze.what.utils`.

"""

from nose.tools import eq_
from webob import Request

from repoze.what.exc import NotAuthorizedError
from repoze.what.utils import enforce

from tests import MockPredicate


class TestEnforcer(object):
    """Tests for the enforce() function."""
    
    def setUp(self):
        """Create a fresh request object."""
        self.req = Request({})
    
    def test_with_predicate_met(self):
        enforce(MockPredicate(), self.req)
    
    def test_with_predicate_unmet(self):
        self._check_enforcement(MockPredicate(False), self.req)
    
    def test_with_predicate_unmet_with_message(self):
        self._check_enforcement(MockPredicate(False), self.req,
                                expected_message="Go away")
    
    def test_with_predicate_unmet_with_denial_handler(self):
        self._check_enforcement(MockPredicate(False), self.req,
                                expected_denial_handler=object())
    
    def test_with_predicate_unmet_with_message_and_denial_handler(self):
        self._check_enforcement(MockPredicate(False), self.req,
                                expected_message="Go away",
                                expected_denial_handler=object())
    
    def _check_enforcement(self, predicate, request, expected_message=None,
                           expected_denial_handler=None):
        """Make sure ``predicate`` is not met and enforced as expected."""
        try:
            enforce(predicate, request, expected_message,
                    expected_denial_handler)
        except NotAuthorizedError, authz_denial:
            eq_(unicode(authz_denial), unicode(expected_message))
            eq_(authz_denial.handler, expected_denial_handler)
        else:
            raise AssertionError("Authorization denial not raised")

