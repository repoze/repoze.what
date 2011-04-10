# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2009, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
# Copyright (c) 2008-2011, Gustavo Narea <me@gustavonarea.net>.
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
Tests for the built-in predicates.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises
from webob import Request

from repoze.what import predicates

from tests import MockPredicate


#{ The test suite itself


class TestPredicate(object):
    
    def test_check_isnt_implemented(self):
        p = predicates.Predicate()
        assert_raises(NotImplementedError, p, {})
    
    def test_request_can_be_webobs(self):
        """
        The predicate checker must not also accept WSGI environments, but also
        WebOb request objects.
        
        """
        p = EqualsTwo()
        req1 = Request({'test_number': 2})
        req2 = Request({'test_number': 3})
        ok_(p(req1))
        assert_false(p(req2))
    
    def test_met_predicate(self):
        environ = {'test_number': 4}
        p = EqualsFour()
        ok_(p(environ))
    
    def test_unmet_predicate(self):
        environ = {'test_number': 3}
        p = EqualsFour()
        assert_false(p(environ))


class TestNotPredicate(object):
    
    def test_failure(self):
        environ = {'test_number': 4}
        # It must NOT equal 4
        p = predicates.Not(EqualsFour())
        # It equals 4!
        assert_false(p(environ))
    
    def test_success(self):
        """``False`` is returned if the wrapped predicate is met."""
        environ = {'test_number': 5}
        # It must not equal 4
        p = predicates.Not(EqualsFour())
        # It doesn't equal 4!
        ok_(p(environ))
    
    def test_no_result(self):
        """
        Nothing should be returned if the negated predicated didn't return
        anything.
        
        """
        predicate = IndecisivePredicate()
        negated_predicate = predicates.Not(predicate)
        eq_(negated_predicate({}), None)
        ok_(predicate.evaluated)


class TestAllPredicate(object):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.All(EqualsTwo())
        ok_(p(environ))
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.All(EqualsTwo())
        assert_false(p(environ))
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        ok_(p(environ))
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        assert_false(p(environ))
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        assert_false(p(environ))
    
    def test_no_results(self):
        """
        The evaluation of All is indeterminate when no result was received.
        
        """
        p1 = IndecisivePredicate()
        p2 = IndecisivePredicate()
        conjunction = predicates.All(p1, p2)
        eq_(conjunction({}), None)
    
    def test_one_missing(self):
        """
        The evaluation of All is indeterminate when there's only one inner
        predicate and it is indeterminate.
        
        """
        indecisive_predicate = IndecisivePredicate()
        conjunction = predicates.All(indecisive_predicate)
        eq_(conjunction({}), None)
    
    def test_one_missing_and_one_true_result(self):
        """
        The evaluation of All is indeterminate when at least one of the results
        is missing (i.e., ``None`` was returned), even if there was one
        positive result.
        
        """
        indecisive_predicate = IndecisivePredicate()
        true_predicate = MockPredicate()
        conjunction = predicates.All(indecisive_predicate, true_predicate)
        eq_(conjunction({}), None)
        # Checking it the other way around:
        reversed_conjunction = predicates.All(true_predicate,
                                              indecisive_predicate)
        eq_(reversed_conjunction({}), None)
    
    def test_one_missing_and_one_false_result(self):
        """
        The evaluation of All is negative if one of the results was negative,
        even if there was an indeterminate result.
        
        """
        indecisive_predicate = IndecisivePredicate()
        false_predicate = MockPredicate(False)
        conjunction = predicates.All(indecisive_predicate, false_predicate)
        eq_(conjunction({}), False)
        # Checking it the other way around:
        reversed_conjunction = predicates.All(false_predicate,
                                              indecisive_predicate)
        eq_(reversed_conjunction({}), False)


class TestAnyPredicate(object):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.Any(EqualsTwo())
        ok_(p(environ))
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.Any(EqualsTwo())
        assert_false(p(environ))
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        ok_(p(environ))
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        assert_false(p(environ))
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        ok_(p(environ))
    
    def test_no_results(self):
        """
        The evaluation of Any is indeterminate when no result was received.
        
        """
        p1 = IndecisivePredicate()
        p2 = IndecisivePredicate()
        disjunction = predicates.Any(p1, p2)
        eq_(disjunction({}), None)
    
    def test_one_missing(self):
        """
        The evaluation of Any is indeterminate when there's only one inner
        predicate and it is indeterminate.
        
        """
        indecisive_predicate = IndecisivePredicate()
        conjunction = predicates.Any(indecisive_predicate)
        eq_(conjunction({}), None)
    
    def test_one_missing_and_one_true_result(self):
        """
        The evaluation of Any is true if any least one of the inner predicates
        evaluates to True, even if one of them was indeterminate.
        
        """
        indecisive_predicate = IndecisivePredicate()
        true_predicate = MockPredicate()
        disjunction = predicates.Any(indecisive_predicate, true_predicate)
        ok_(disjunction({}))
        # Checking it the other way around:
        reversed_disjunction = predicates.Any(true_predicate,
                                              indecisive_predicate)
        ok_(reversed_disjunction({}))
    
    def test_one_missing_and_one_false_result(self):
        """
        The evaluation of Any is indeterminate if none of the inner predicates
        evaluates to False and at least one was indeterminate.
        
        """
        indecisive_predicate = IndecisivePredicate()
        false_predicate = MockPredicate(False)
        disjunction = predicates.Any(indecisive_predicate, false_predicate)
        eq_(disjunction({}), None)
        # Checking it the other way around:
        reversed_disjunction = predicates.Any(false_predicate,
                                              indecisive_predicate)
        eq_(reversed_disjunction({}), None)


class TestBooleanOperations(object):
    """
    Tests for the boolean operations functionality provided pythonically.
    
    """
    
    def test_invalid_operations(self):
        # OR operations:
        try:
            MockPredicate() | "I am just an string"
        except TypeError:
            pass
        else:
            raise AssertionError("Predicates must only support OR "
                                 "operations with other predicates!")
        
        # AND operations:
        try:
            MockPredicate() & "I am just an string"
        except TypeError:
            pass
        else:
            raise AssertionError("Predicates must only support AND "
                                 "operations with other predicates!")
    
    #{ Unary operations
    
    def test_not(self):
        p1 = MockPredicate()
        met_predicate = ~p1
        p2 = MockPredicate(False)
        unmet_predicate = ~p2
        
        ok_(isinstance(met_predicate, predicates.Not))
        ok_(isinstance(unmet_predicate, predicates.Not))
        
        assert_false(met_predicate({}))
        ok_(unmet_predicate({}))
    
    #{ 2 operands
    
    def test_2_and(self):
        """predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p0 = p1 & p2
        
        ok_(isinstance(p0, predicates.All))
        eq_(len(p0.predicates), 2)
        ok_(p1 in p0.predicates)
        ok_(p2 in p0.predicates)
    
    def test_2_or(self):
        """predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p0 = p1 | p2
        
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 2)
        ok_(p1 in p0.predicates)
        ok_(p2 in p0.predicates)
    
    #{ 3 operands
    
    def test_3_and(self):
        """predicate & predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p0 = p1 & p2 & p3
        ok_(isinstance(p0, predicates.All))
        eq_(len(p0.predicates), 3)
        eq_(p1, p0.predicates[0])
        eq_(p2, p0.predicates[1])
        eq_(p3, p0.predicates[2])
    
    def test_3_or(self):
        """predicate | predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p0 = p1 | p2 | p3
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 3)
        eq_(p1, p0.predicates[0])
        eq_(p2, p0.predicates[1])
        eq_(p3, p0.predicates[2])
    
    def test_3_and_or(self):
        """predicate & predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p0 = p1 & p2 | p3
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 2)
        eq_(p3, p0.predicates[1])
        ok_(isinstance(p0.predicates[0], predicates.All))
        eq_(len(p0.predicates[0].predicates), 2)
        eq_(p1, p0.predicates[0].predicates[0])
        eq_(p2, p0.predicates[0].predicates[1])
    
    def test_3_or_and(self):
        """predicate | predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p0 = p1 | p2 & p3
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 2)
        eq_(p1, p0.predicates[0])
        ok_(isinstance(p0.predicates[1], predicates.All))
        eq_(len(p0.predicates[1].predicates), 2)
        eq_(p2, p0.predicates[1].predicates[0])
        eq_(p3, p0.predicates[1].predicates[1])
    
    
    #{ 4 operands
    
    def test_4_and(self):
        """predicate & predicate & predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 & p2 & p3 & p4
        ok_(isinstance(p0, predicates.All))
        eq_(len(p0.predicates), 4)
        eq_(p1, p0.predicates[0])
        eq_(p2, p0.predicates[1])
        eq_(p3, p0.predicates[2])
        eq_(p4, p0.predicates[3])
    
    def test_4_or(self):
        """predicate | predicate | predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 | p2 | p3 | p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 4)
        eq_(p1, p0.predicates[0])
        eq_(p2, p0.predicates[1])
        eq_(p3, p0.predicates[2])
        eq_(p4, p0.predicates[3])
    
    def test_4_or_or_and(self):
        """predicate | predicate | predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 | p2 | p3 & p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 3)
        eq_(p1, p0.predicates[0])
        eq_(p2, p0.predicates[1])
        ok_(isinstance(p0.predicates[2], predicates.All))
        eq_(len(p0.predicates[2].predicates), 2)
        eq_(p3, p0.predicates[2].predicates[0])
        eq_(p4, p0.predicates[2].predicates[1])
    
    def test_4_or_and_or(self):
        """predicate | predicate & predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 | p2 & p3 | p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 3)
        eq_(p1, p0.predicates[0])
        eq_(p4, p0.predicates[2])
        ok_(isinstance(p0.predicates[1], predicates.All))
        eq_(len(p0.predicates[1].predicates), 2)
        eq_(p2, p0.predicates[1].predicates[0])
        eq_(p3, p0.predicates[1].predicates[1])
    
    def test_4_and_or_or(self):
        """predicate & predicate | predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 & p2 | p3 | p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 3)
        eq_(p3, p0.predicates[1])
        eq_(p4, p0.predicates[2])
        ok_(isinstance(p0.predicates[0], predicates.All))
        eq_(len(p0.predicates[0].predicates), 2)
        eq_(p1, p0.predicates[0].predicates[0])
        eq_(p2, p0.predicates[0].predicates[1])
    
    def test_4_and_or_and(self):
        """predicate & predicate | predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 & p2 | p3 & p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 2)
        ok_(isinstance(p0.predicates[0], predicates.All))
        eq_(len(p0.predicates[0].predicates), 2)
        eq_(p1, p0.predicates[0].predicates[0])
        eq_(p2, p0.predicates[0].predicates[1])
        ok_(isinstance(p0.predicates[1], predicates.All))
        eq_(len(p0.predicates[1].predicates), 2)
        eq_(p3, p0.predicates[1].predicates[0])
        eq_(p4, p0.predicates[1].predicates[1])
    
    def test_4_and_and_or(self):
        """predicate & predicate & predicate | predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 & p2 & p3 | p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 2)
        eq_(p4, p0.predicates[1])
        ok_(isinstance(p0.predicates[0], predicates.All))
        eq_(len(p0.predicates[0].predicates), 3)
        eq_(p1, p0.predicates[0].predicates[0])
        eq_(p2, p0.predicates[0].predicates[1])
        eq_(p3, p0.predicates[0].predicates[2])
    
    def test_4_or_and_and(self):
        """predicate | predicate & predicate & predicate"""
        p1 = EqualsFour()
        p2 = EqualsTwo()
        p3 = GreaterThan(2)
        p4 = IndecisivePredicate()
        p0 = p1 | p2 & p3 & p4
        ok_(isinstance(p0, predicates.Any))
        eq_(len(p0.predicates), 2)
        eq_(p1, p0.predicates[0])
        ok_(isinstance(p0.predicates[1], predicates.All))
        eq_(len(p0.predicates[1].predicates), 3)
        eq_(p2, p0.predicates[1].predicates[0])
        eq_(p3, p0.predicates[1].predicates[1])
        eq_(p4, p0.predicates[1].predicates[2])
    
    #}


#{ Mock predicate checkers


class EqualsTwo(MockPredicate):
    
    def check(self, request, credentials):
        number = request.environ.get('test_number')
        return number == 2


class EqualsFour(MockPredicate):
    
    def check(self, request, credentials):
        number = request.environ.get('test_number')
        return number == 4


class GreaterThan(MockPredicate):
    
    def __init__(self, compared_number, **kwargs):
        super(GreaterThan, self).__init__(**kwargs)
        self.compared_number = compared_number
        
    def check(self, request, credentials):
        number = request.environ.get('test_number')
        return number > self.compared_number


class IndecisivePredicate(MockPredicate):
    """Predicate checker which is always indeterminate."""
    
    def check(self, request, credentials):
        self.evaluated = True
        return None


#}
