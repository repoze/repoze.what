# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
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
Tests for the deprecated :mod:`repoze.what.authorize` module.

"""

import unittest

from repoze.what.authorize import check_authorization
from repoze.what.predicates import has_any_permission, has_permission, \
                                   NotAuthorizedError

from base import FakeLogger
from test_predicates import make_environ


class TestAuthorize(unittest.TestCase):
    """Tests for the repoze.what.authorize module"""
    
    def test_check_authorization(self):
        logger = FakeLogger()
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        environ['repoze.who.logger'] = logger
        p = has_any_permission('party', 'scream')
        check_authorization(p, environ)
        info = logger.messages['info']
        assert "Authorization granted" == info[0]
    
    def test_NotAuthorizedError_is_available(self):
        """
        NotAuthorizedError must subclass PredicateError for backwards
        compatibility.
        
        """
        from repoze.what.authorize import NotAuthorizedError
        from repoze.what.predicates import PredicateError
        assert issubclass(NotAuthorizedError, PredicateError)


class TestAuthorizeWithPredicatesBooleanized(unittest.TestCase):
    """
    Tests for repoze.what-pylons' like "predicates booleanized" misfeatures.
    
    """
    
    def test_check_authorization_granted_with_predicates_booleanized(self):
        """Authorization must be granted as usual."""
        logger = FakeLogger()
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        environ['repoze.who.logger'] = logger
        p = self._get_booleanized_has_permission('party', environ)
        assert bool(p), "Predicate isn't booleanized"
        check_authorization(p, environ)
        info = logger.messages['info']
        assert "Authorization granted" == info[0]
    
    def test_check_authorization_denies_with_predicates_booleanized(self):
        """Authorization must be denied as usual."""
        logger = FakeLogger()
        environ = make_environ('gustavo')
        environ['repoze.who.logger'] = logger
        p = self._get_booleanized_has_permission('party', environ)
        assert not bool(p), "Predicate isn't booleanized"
        try:
            check_authorization(p, environ)
            self.fail('Authorization must have been rejected')
        except NotAuthorizedError, e:
            error_msg = 'The user must have the "party" permission'
            self.assertEqual(str(e), error_msg)
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: %s" % error_msg == info[0]
    
    def _get_booleanized_has_permission(self, permission, environ):
        """Return a has_permission instance, booleanized"""
        class booleanized_has_permission(has_permission):
            def __nonzero__(self):
                return self.is_met(environ)
        return booleanized_has_permission(permission)
