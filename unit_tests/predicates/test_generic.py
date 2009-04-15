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
Tests for the generic predicate checkers.

"""

from repoze.what.predicates.generic import All, Any, Not

from unit_tests.predicates import BasePredicateTester, make_environ, \
                                  EqualsTwo, EqualsFour, GreaterThan


class TestNotPredicate(BasePredicateTester):
    
    def test_failure(self):
        environ = make_environ(test_number=4)
        # It must NOT equal 4
        p = Not(EqualsFour())
        # It equals 4!
        self.eval_unmet_predicate(p, environ, 'The condition must not be met')
    
    def test_failure_with_custom_message(self):
        environ = make_environ(test_number=4)
        # It must not equal 4
        p = Not(EqualsFour(), msg='It must not equal four')
        # It equals 4!
        self.eval_unmet_predicate(p, environ, 'It must not equal four')
    
    def test_success(self):
        environ = make_environ(test_number=5)
        # It must not equal 4
        p = Not(EqualsFour())
        # It doesn't equal 4!
        self.eval_met_predicate(p, environ)


class TestAllPredicate(BasePredicateTester):
    
    def test_one_true(self):
        environ = make_environ(test_number=2)
        p = All(EqualsTwo())
        self.eval_met_predicate(p, environ)
        
    def test_one_false(self):
        environ = make_environ(test_number=3)
        p = All(EqualsTwo())
        self.eval_unmet_predicate(p, environ, "Number 3 doesn't equal 2")
    
    def test_two_true(self):
        environ = make_environ(test_number=4)
        p = All(EqualsFour(), GreaterThan(3))
        self.eval_met_predicate(p, environ)
    
    def test_two_false(self):
        environ = make_environ(test_number=1)
        p = All(EqualsFour(), GreaterThan(3))
        self.eval_unmet_predicate(p, environ, "Number 1 doesn't equal 4")
    
    def test_two_mixed(self):
        environ = make_environ(test_number=5)
        p = All(EqualsFour(), GreaterThan(3))
        self.eval_unmet_predicate(p, environ, "Number 5 doesn't equal 4")


class TestAnyPredicate(BasePredicateTester):
    
    def test_one_true(self):
        environ = make_environ(test_number=2)
        p = Any(EqualsTwo())
        self.eval_met_predicate(p, environ)
        
    def test_one_false(self):
        environ = make_environ(test_number=3)
        p = Any(EqualsTwo())
        self.eval_unmet_predicate(p, environ, 
                         "At least one of the following predicates must be "
                         "met: Number 3 doesn't equal 2")
    
    def test_two_true(self):
        environ = make_environ(test_number=4)
        p = Any(EqualsFour(), GreaterThan(3))
        self.eval_met_predicate(p, environ)
    
    def test_two_false(self):
        environ = make_environ(test_number=1)
        p = Any(EqualsFour(), GreaterThan(3))
        self.eval_unmet_predicate(p, environ, 
                         "At least one of the following predicates must be "
                         "met: Number 1 doesn't equal 4, 1 is not greater "
                         "than 3")
    
    def test_two_mixed(self):
        environ = make_environ(test_number=5)
        p = Any(EqualsFour(), GreaterThan(3))
        self.eval_met_predicate(p, environ)
