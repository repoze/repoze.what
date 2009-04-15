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
Tests for the user predicate checkers.

"""

from repoze.what.predicates.user import is_user, is_anonymous, not_anonymous

from unit_tests.predicates import BasePredicateTester, make_environ


class TestIsUserPredicate(BasePredicateTester):
    
    def test_right_user(self):
        environ = make_environ('gustavo')
        p = is_user('gustavo')
        self.eval_met_predicate(p, environ)
    
    def test_wrong_user(self):
        environ = make_environ('andreina')
        p = is_user('gustavo')
        self.eval_unmet_predicate(p, environ,
                                  'The current user must be "gustavo"')


class TestIsAnonymousPredicate(BasePredicateTester):
    
    def test_authenticated_user(self):
        environ = make_environ('gustavo')
        p = is_anonymous()
        self.eval_unmet_predicate(p, environ,
                                  'The current user must be anonymous')
    
    def test_anonymous_user(self):
        environ = make_environ()
        p = is_anonymous()
        self.eval_met_predicate(p, environ)


class TestNotAnonymousPredicate(BasePredicateTester):
    
    def test_authenticated_user(self):
        environ = make_environ('gustavo')
        p = not_anonymous()
        self.eval_met_predicate(p, environ)
    
    def test_anonymous_user(self):
        environ = make_environ()
        p = not_anonymous()
        self.eval_unmet_predicate(p, environ,
                         'The current user must have been authenticated')

