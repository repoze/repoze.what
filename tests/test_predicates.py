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
        p.eval_with_environ(environ)
        self.assertEqual(p.error, p.message % p.__dict__)
    
    def test_errors_arent_added_if_not_required(self):
        p = EqualsTwo()
        environ = {'test_number': 2}
        p.eval_with_environ(environ)
        self.assertEqual(p.error, '')
    
    def test_message_is_changeable(self):
        previous_msg = EqualsTwo.message
        new_msg = 'It does not equal two!'
        p = EqualsTwo(msg=new_msg)
        self.assertEqual(new_msg, p.message)
    
    def test_message_isnt_changed_unless_required(self):
        previous_msg = EqualsTwo.message
        p = EqualsTwo()
        self.assertEqual(previous_msg, p.message)
    
    def test_unicode_messages(self):
        unicode_msg = u'请登陆'
        p = EqualsTwo(msg=unicode_msg)
        environ = {'test_number': 3}
        p.eval_with_environ(environ)
        self.assertEqual(p.error, unicode_msg)


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


class TestNotPredicate(unittest.TestCase):
    
    def test_success(self):
        environ = {'test_number': 4}
        # It must not be greater than 5
        p = predicates.Not(EqualsFour())
        # It's greater than 5!
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The condition must not be met')
    
    def test_failure(self):
        environ = {'test_number': 7}
        # It must not be less than 5
        p = predicates.Not(LessThan(5))
        # It's greater than 5!
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_custom_message(self):
        environ = {'test_number': 4}
        # It must not be greater than 5
        p = predicates.Not(EqualsFour(), msg='It must not equal four')
        # It's greater than 5!
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'It must not equal four')


class TestAllPredicate(unittest.TestCase):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.All(EqualsTwo())
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.All(EqualsTwo())
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, "Number 3 doesn't equal 2")
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, "Number 1 doesn't equal 4")
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, "Number 5 doesn't equal 4")


class TestAnyPredicate(unittest.TestCase):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.Any(EqualsTwo())
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.Any(EqualsTwo())
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         "At least one of the following predicates must be "
                         "met: Number 3 doesn't equal 2")
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         "At least one of the following predicates must be "
                         "met: Number 1 doesn't equal 4, 1 is not greater "
                         "than 3")
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')


class TestIsUserPredicate(unittest.TestCase):
    
    def test_user_without_identity(self):
        environ = {}
        p = predicates.is_user('gustavo')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The current user must be "gustavo"')
    
    def test_user_without_userid(self):
        environ = {'repoze.who.identity': {}}
        p = predicates.is_user('gustavo')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The current user must be "gustavo"')
    
    def test_right_user(self):
        environ = make_environ('gustavo')
        p = predicates.is_user('gustavo')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_wrong_user(self):
        environ = make_environ('andreina')
        p = predicates.is_user('gustavo')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The current user must be "gustavo"')


class TestInGroupPredicate(unittest.TestCase):
    
    def test_user_belongs_to_group(self):
        environ = make_environ('gustavo', ['developers'])
        p = predicates.in_group('developers')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_user_doesnt_belong_to_group(self):
        environ = make_environ('gustavo', ['developers', 'admins'])
        p = predicates.in_group('designers')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         'The current user must belong to the group "designers"')


class TestInAllGroupsPredicate(unittest.TestCase):
    
    def test_user_belongs_to_groups(self):
        environ = make_environ('gustavo', ['developers', 'admins'])
        p = predicates.in_all_groups('developers', 'admins')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_user_doesnt_belong_to_groups(self):
        environ = make_environ('gustavo', ['users', 'admins'])
        p = predicates.in_all_groups('developers', 'designers')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         'The current user must belong to the group "developers"')
    
    def test_user_doesnt_belong_to_one_group(self):
        environ = make_environ('gustavo', ['developers'])
        p = predicates.in_all_groups('developers', 'designers')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         'The current user must belong to the group "designers"')


class TestInAnyGroupsPredicate(unittest.TestCase):
    
    def test_user_belongs_to_groups(self):
        environ = make_environ('gustavo', ['developers',' admins'])
        p = predicates.in_any_group('developers', 'admins')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_user_doesnt_belong_to_groups(self):
        environ = make_environ('gustavo', ['users', 'admins'])
        p = predicates.in_any_group('developers', 'designers')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         'The member must belong to at least one of the '
                         'following groups: developers, designers')
    
    def test_user_doesnt_belong_to_one_group(self):
        environ = make_environ('gustavo', ['designers'])
        p = predicates.in_any_group('developers', 'designers')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')


class TestNotAnonymousPredicate(unittest.TestCase):
    
    def test_authenticated_user(self):
        environ = make_environ('gustavo')
        p = predicates.not_anonymous()
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_anonymous_user(self):
        environ = {}
        p = predicates.not_anonymous()
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         'The current user must have been authenticated')


class TestHasPermissionPredicate(unittest.TestCase):
    
    def test_user_has_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv'])
        p = predicates.has_permission('watch-tv')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_user_doesnt_have_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv'])
        p = predicates.has_permission('eat')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The user must have the "eat" permission')


class TestHasAllPermissionsPredicate(unittest.TestCase):
    
    def test_user_has_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_all_permissions('watch-tv', 'eat')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_user_doesnt_have_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_all_permissions('jump', 'scream')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The user must have the "jump" permission')
    
    def test_user_has_one_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_all_permissions('party', 'scream')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error, 'The user must have the "scream" permission')


class TestUserHasAnyPermissionsPredicate(unittest.TestCase):
    
    def test_user_has_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_any_permission('watch-tv', 'eat')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')
    
    def test_user_doesnt_have_all_permissions(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_any_permission('jump', 'scream')
        self.assertFalse(p.eval_with_environ(environ))
        self.assertEqual(p.error,
                         'The user must have at least one of the following '
                         'permissions: jump, scream')
    
    def test_user_has_one_permission(self):
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        p = predicates.has_any_permission('party', 'scream')
        self.assertTrue(p.eval_with_environ(environ))
        self.assertEqual(p.error, '')


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
    message = "I'm a fake predicate"


class EqualsTwo(predicates.Predicate):
    message = "Number %(number)s doesn't equal 2"
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number == 2


class EqualsFour(predicates.Predicate):
    message = "Number %(number)s doesn't equal 4"
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number == 4


class GreaterThan(predicates.Predicate):
    message = "%(number)s is not greater than %(compared_number)s"
    
    def __init__(self, compared_number, **kwargs):
        super(GreaterThan, self).__init__(**kwargs)
        self.compared_number = compared_number
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number > self.compared_number


class LessThan(predicates.Predicate):
    message = "%(number)s must be less than %(compared_number)s"
    
    def __init__(self, compared_number, **kwargs):
        super(LessThan, self).__init__(**kwargs)
        self.compared_number = compared_number
        
    def _eval_with_environ(self, environ):
        self.number = environ.get('test_number')
        return self.number < self.compared_number


#}
