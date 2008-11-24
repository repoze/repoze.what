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
Tests for the predicates.

"""

import unittest

from repoze.what import predicates


#{ The test suite itself


class TestPredicate(unittest.TestCase):
    
    def test_eval_with_environ_isnt_implemented(self):
        p = MockPredicate()
        self.failUnlessRaises(NotImplementedError, p.eval_with_environ, None)
    
    def test_errors_are_added_if_required(self):
        p = EqualsTwo()
        environ = {'test_number': 3}
        errors = []
        p.eval_with_environ(environ, errors)
        self.assertEqual(errors, [p.error_message % p.__dict__])
    
    def test_errors_arent_added_if_not_required(self):
        p = EqualsTwo()
        environ = {'test_number': 4}
        errors = None
        p.eval_with_environ(environ, errors)
        self.assertEqual(errors, None)
    
    def test_error_message_is_changeable(self):
        previous_msg = EqualsTwo.error_message
        new_msg = 'It does not equal two!'
        p = EqualsTwo(msg=new_msg)
        self.assertEqual(new_msg, p.error_message)
    
    def test_error_message_isnt_changed_unless_required(self):
        previous_msg = EqualsTwo.error_message
        p = EqualsTwo()
        self.assertEqual(previous_msg, p.error_message)


class TestCompoundPredicate(unittest.TestCase):
    
    def test_one_predicate_works(self):
        p = EqualsTwo()
        cp = predicates.CompoundPredicate(p)
        self.assertEqual(cp.predicates, (p,))
        
    def test_two_predicates_work(self):
        p1 = EqualsTwo()
        p2 = MockPredicate()
        cp = predicates.CompoundPredicate(p1, p2)
        self.assertEqual(cp.predicates, (p1, p2))


class TestAllPredicate(unittest.TestCase):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.All(EqualsTwo())
        self.assertTrue(p.eval_with_environ(environ, None))
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.All(EqualsTwo())
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.assertTrue(p.eval_with_environ(environ, None))
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestAnyPredicate(unittest.TestCase):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.Any(EqualsTwo())
        self.assertTrue(p.eval_with_environ(environ, None))
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.Any(EqualsTwo())
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.assertTrue(p.eval_with_environ(environ, None))
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.assertTrue(p.eval_with_environ(environ, None))


class TestIsUserPredicate(unittest.TestCase):
    
    def test_user_without_identity(self):
        environ = {}
        p = predicates.is_user('gustavo')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_user_without_userid(self):
        environ = {'repoze.who.identity': {}}
        p = predicates.is_user('gustavo')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_right_user(self):
        environ = make_environ('gustavo')
        p = predicates.is_user('gustavo')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_wrong_user(self):
        environ = make_environ('andreina')
        p = predicates.is_user('gustavo')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestInGroupPredicate(unittest.TestCase):
    
    def test_user_belongs_to_group(self):
        environ = make_environ('gustavo', ['developers'])
        p = predicates.in_group('developers')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_user_doesnt_belong_to_group(self):
        environ = make_environ('gustavo', ['developers', 'admins'])
        p = predicates.in_group('designers')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestInAllGroupsPredicate(unittest.TestCase):
    
    def test_user_belongs_to_groups(self):
        environ = make_environ('gustavo', ['developers', 'admins'])
        p = predicates.in_all_groups('developers', 'admins')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_user_doesnt_belong_to_groups(self):
        environ = make_environ('gustavo', ['users', 'admins'])
        p = predicates.in_all_groups('developers', 'designers')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_user_doesnt_belong_to_one_group(self):
        environ = make_environ('gustavo', ['developers'])
        p = predicates.in_all_groups('developers', 'designers')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestInAnyGroupsPredicate(unittest.TestCase):
    
    def test_user_belongs_to_groups(self):
        environ = make_environ('gustavo', ['developers',' admins'])
        p = predicates.in_any_group('developers', 'admins')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_user_doesnt_belong_to_groups(self):
        environ = make_environ('gustavo', ['users', 'admins'])
        p = predicates.in_any_group('developers', 'designers')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_user_doesnt_belong_to_one_group(self):
        environ = make_environ('gustavo', ['designers'])
        p = predicates.in_any_group('developers', 'designers')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)


class TestNotAnonymousPredicate(unittest.TestCase):
    
    def test_authenticated_user(self):
        environ = make_environ('gustavo')
        p = predicates.not_anonymous()
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_anonymous_user(self):
        environ = {}
        p = predicates.not_anonymous()
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestHasPermissionPredicate(unittest.TestCase):
    
    def test_user_has_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv'])
        p = predicates.has_permission('watch-tv')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_user_doesnt_have_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv'])
        p = predicates.has_permission('eat')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestHasAllPermissionsPredicate(unittest.TestCase):
    
    def test_user_has_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_all_permissions('watch-tv', 'eat')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_user_doesnt_have_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_all_permissions('jump', 'scream')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_user_has_one_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_all_permissions('party', 'scream')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)


class TestUserHasAnyPermissionsPredicate(unittest.TestCase):
    
    def test_user_has_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_any_permission('watch-tv', 'eat')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)
    
    def test_user_doesnt_have_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_any_permission('jump', 'scream')
        errors = []
        self.assertFalse(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 1)
    
    def test_user_has_one_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_any_permission('party', 'scream')
        errors = []
        self.assertTrue(p.eval_with_environ(environ, errors))
        self.assertEqual(len(errors), 0)


#{ Test utilities


def make_environ(user, groups=None, permissions=None):
    """Make a WSGI enviroment with the identity dict"""
    identity = {'repoze.who.userid': user}
    if groups:
        identity['groups'] = groups
    if permissions:
        identity['permissions'] = permissions
    environ = {'repoze.who.identity': identity}
    return environ

#{ Mock definitions


class MockPredicate(predicates.Predicate):
    error_message = "I'm a fake predicate"


class EqualsTwo(predicates.Predicate):
    error_message = "Number %(number)s doesn't equal 2"
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number == 2


class EqualsFour(predicates.Predicate):
    error_message = "Number %(number)s doesn't equal 4"
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number == 4


class GreaterThan(predicates.Predicate):
    error_message = "%(number)s is not greater than %(compared_number)s"
    
    def __init__(self, compared_number):
        self.compared_number = compared_number
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number > self.compared_number


class LessThan(predicates.Predicate):
    error_message = "%(number)s is not less than %(compared_number)s"
    
    def __init__(self, compared_number):
        self.compared_number = compared_number
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number < self.compared_number


#}
