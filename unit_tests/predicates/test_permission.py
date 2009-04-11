# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
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
Test suite for the permission-oriented predicate checkers.

"""

from repoze.what.predicates.permission import has_permission, \
                                              has_all_permissions, \
                                              has_any_permission

from unit_tests.predicates import BasePredicateTester, make_environ


class TestHasPermissionPredicate(BasePredicateTester):
    
    def test_user_has_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv'])
        p = has_permission('watch-tv')
        self.eval_met_predicate(p, environ)
    
    def test_user_doesnt_have_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv'])
        p = has_permission('eat')
        self.eval_unmet_predicate(p, environ,
                                  'The user must have the "eat" permission')


class TestHasAllPermissionsPredicate(BasePredicateTester):
    
    def test_user_has_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = has_all_permissions('watch-tv', 'eat')
        self.eval_met_predicate(p, environ)
    
    def test_user_doesnt_have_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = has_all_permissions('jump', 'scream')
        self.eval_unmet_predicate(p, environ,
                                  'The user must have the "jump" permission')
    
    def test_user_has_one_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = has_all_permissions('party', 'scream')
        self.eval_unmet_predicate(p, environ,
                                  'The user must have the "scream" permission')


class TestUserHasAnyPermissionsPredicate(BasePredicateTester):
    
    def test_user_has_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = has_any_permission('watch-tv', 'eat')
        self.eval_met_predicate(p, environ)
    
    def test_user_doesnt_have_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = has_any_permission('jump', 'scream')
        self.eval_unmet_predicate(p, environ,
                         'The user must have at least one of the following '
                         'permissions: jump, scream')
    
    def test_user_has_one_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = has_any_permission('party', 'scream')
        self.eval_met_predicate(p, environ)

