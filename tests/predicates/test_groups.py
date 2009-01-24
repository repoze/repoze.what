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
Test suite for the predicates of the groups/permissions-based authorization
pattern.

"""

from repoze.what.patterns.groups import in_group, has_permission, \
                                        in_all_groups, has_all_permissions, \
                                        in_any_group, has_any_permission

from tests.predicates import BasePredicateTester, make_environ, \
                                  EqualsTwo, EqualsFour, GreaterThan


class TestInGroupPredicate(BasePredicateTester):
    
    def test_user_belongs_to_group(self):
        environ = make_environ('gustavo', ['developers'])
        p = in_group('developers')
        self.eval_met_predicate(p, environ)
    
    def test_user_doesnt_belong_to_group(self):
        environ = make_environ('gustavo', ['developers', 'admins'])
        p = in_group('designers')
        self.eval_unmet_predicate(p, environ,
                    'The current user must belong to the group "designers"')


class TestInAllGroupsPredicate(BasePredicateTester):
    
    def test_user_belongs_to_groups(self):
        environ = make_environ('gustavo', ['developers', 'admins'])
        p = in_all_groups('developers', 'admins')
        self.eval_met_predicate(p, environ)
    
    def test_user_doesnt_belong_to_groups(self):
        environ = make_environ('gustavo', ['users', 'admins'])
        p = in_all_groups('developers', 'designers')
        self.eval_unmet_predicate(p, environ,
                    'The current user must belong to the group "developers"')
    
    def test_user_doesnt_belong_to_one_group(self):
        environ = make_environ('gustavo', ['developers'])
        p = in_all_groups('developers', 'designers')
        self.eval_unmet_predicate(p, environ,
                    'The current user must belong to the group "designers"')


class TestInAnyGroupsPredicate(BasePredicateTester):
    
    def test_user_belongs_to_groups(self):
        environ = make_environ('gustavo', ['developers',' admins'])
        p = in_any_group('developers', 'admins')
        self.eval_met_predicate(p, environ)
    
    def test_user_doesnt_belong_to_groups(self):
        environ = make_environ('gustavo', ['users', 'admins'])
        p = in_any_group('developers', 'designers')
        self.eval_unmet_predicate(p, environ,
                         'The member must belong to at least one of the '
                         'following groups: developers, designers')
    
    def test_user_doesnt_belong_to_one_group(self):
        environ = make_environ('gustavo', ['designers'])
        p = in_any_group('developers', 'designers')
        self.eval_met_predicate(p, environ)


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

