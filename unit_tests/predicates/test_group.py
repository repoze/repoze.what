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
Test suite for the groups-oriented predicate checkers.

"""

from repoze.what.predicates.group import in_group, in_all_groups, \
                                         in_any_group

from unit_tests.predicates import BasePredicateTester, make_environ


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

