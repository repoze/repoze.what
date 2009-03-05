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
from repoze.what.predicates import has_any_permission, NotAuthorizedError

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
    
    #{ Tests for repoze.what-pylons' like "predicates booleanized" misfeatures
    
    def test_check_authorization_granted_with_predicates_booleanized(self):
        """
        Authorization must be granted as usual even if the predicate was
        booleanized.
        
        """
        logger = FakeLogger()
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        environ['repoze.who.logger'] = logger
        p = has_any_permission('party', 'scream')
        p.__nonzero__ = lambda self: self.is_met(environ)
        # Checking it:
        check_authorization(p, environ)
        info = logger.messages['info']
        assert "Authorization granted" == info[0]
    
    def test_check_authorization_denies_with_predicates_booleanized(self):
        """
        Authorization must be denied as usual even if the predicate was
        booleanized.
        
        """
        logger = FakeLogger()
        environ = make_environ('gustavo')
        environ['repoze.who.logger'] = logger
        p = has_any_permission('party', 'scream')
        p.__nonzero__ = lambda self: self.is_met(environ)
        # Checking it:
        try:
            check_authorization(p, environ)
            self.fail('Authorization must have been rejected')
        except NotAuthorizedError, e:
            error_msg = 'The user must have at least one of the following ' \
                        'permissions: party, scream'
            self.assertEqual(str(e), error_msg)
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: %s" % error_msg == info[0]
    
    #}
