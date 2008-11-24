# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com> and
#                     Gustavo Narea <me@gustavonarea.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
Tests for the authorization mechanisms.

"""

import unittest

from repoze.what import authorize

from test_predicates import make_environ


class TestAuthorizationChecker(unittest.TestCase):
    
    def test_authorized(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = authorize.has_any_permission('party', 'scream')
        authorize.check_authorization(p, environ)
    
    def test_unauthorized(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = authorize.has_any_permission('jump', 'scream')
        try:
            authorize.check_authorization(p, environ)
            self.fail('Authorization must be accepted')
        except authorize.NotAuthorizedError, e:
            self.assertEqual(len(e.errors), 1)
