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
Tests for the authorization mechanisms.

"""

import unittest

from base import FakeLogger
from test_predicates import make_environ


class TestAuthorize(unittest.TestCase):
    """Tests for the repoze.what.authorize module"""
    
    def test_check_authorization(self):
        from repoze.what.authorize import check_authorization
        from repoze.what.predicates import has_any_permission
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
