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
Tests for the predicates.

"""

from unittest import TestCase

from repoze.what import predicates

from unit_tests.base import FakeLogger
from unit_tests.predicates import BasePredicateTester, make_environ, \
                                  EqualsTwo, EqualsFour, GreaterThan


#{ The test suite itself


class TestPredicate(BasePredicateTester):
    
    def test_evaluate_isnt_implemented(self):
        p = MockPredicate()
        self.failUnlessRaises(NotImplementedError, p.evaluate, None, None)
    
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
        self.eval_unmet_predicate(p, environ, unicode_msg)
    
    def test_authorized(self):
        logger = FakeLogger()
        environ = {'test_number': 4}
        environ['repoze.what.logger'] = logger
        p = EqualsFour()
        p.check_authorization(environ)
        info = logger.messages['info']
        assert "Authorization granted" == info[0]
    
    def test_unauthorized(self):
        logger = FakeLogger()
        environ = {'test_number': 3}
        environ['repoze.what.logger'] = logger
        p = EqualsFour(msg="Go away!")
        try:
            p.check_authorization(environ)
            self.fail('Authorization must have been rejected')
        except predicates.NotAuthorizedError, e:
            self.assertEqual(str(e), "Go away!")
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: Go away!" == info[0]
    
    def test_unauthorized_with_unicode_message(self):
        # This test is broken on Python 2.4 and 2.5 because the unicode()
        # function doesn't work when converting an exception into an unicode
        # string (this is, to extract its message).
        unicode_msg = u'请登陆'
        logger = FakeLogger()
        environ = {'test_number': 3}
        environ['repoze.what.logger'] = logger
        p = EqualsFour(msg=unicode_msg)
        try:
            p.check_authorization(environ)
            self.fail('Authorization must have been rejected')
        except predicates.NotAuthorizedError, e:
            self.assertEqual(unicode(e), unicode_msg)
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: %s" % unicode_msg == info[0]
    
    def test_custom_failure_message(self):
        message = u'This is a custom message whose id is: %(id_number)s'
        id_number = 23
        p = EqualsFour(msg=message)
        try:
            p.unmet(message, id_number=id_number)
            self.fail('An exception must have been raised')
        except predicates.NotAuthorizedError, e:
            self.assertEqual(unicode(e), message % dict(id_number=id_number))


class TestCompoundPredicate(BasePredicateTester):
    
    def test_one_predicate_works(self):
        p = EqualsTwo()
        cp = predicates.CompoundPredicate(p)
        self.assertEqual(cp.predicates, (p,))
        
    def test_two_predicates_work(self):
        p1 = EqualsTwo()
        p2 = MockPredicate()
        cp = predicates.CompoundPredicate(p1, p2)
        self.assertEqual(cp.predicates, (p1, p2))


class TestNotAuthorizedError(TestCase):
    """Tests for the NotAuthorizedError exception"""
    
    def test_string_representation(self):
        msg = 'You are not the master of Universe'
        exc = predicates.NotAuthorizedError(msg)
        self.assertEqual(msg, str(exc))


class TestNotPredicate(BasePredicateTester):
    
    def test_failure(self):
        environ = {'test_number': 4}
        # It must NOT equal 4
        p = predicates.Not(EqualsFour())
        # It equals 4!
        self.eval_unmet_predicate(p, environ, 'The condition must not be met')
    
    def test_failure_with_custom_message(self):
        environ = {'test_number': 4}
        # It must not equal 4
        p = predicates.Not(EqualsFour(), msg='It must not equal four')
        # It equals 4!
        self.eval_unmet_predicate(p, environ, 'It must not equal four')
    
    def test_success(self):
        environ = {'test_number': 5}
        # It must not equal 4
        p = predicates.Not(EqualsFour())
        # It doesn't equal 4!
        self.eval_met_predicate(p, environ)


class TestAllPredicate(BasePredicateTester):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.All(EqualsTwo())
        self.eval_met_predicate(p, environ)
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.All(EqualsTwo())
        self.eval_unmet_predicate(p, environ, "Number 3 doesn't equal 2")
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.eval_met_predicate(p, environ)
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.eval_unmet_predicate(p, environ, "Number 1 doesn't equal 4")
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.All(EqualsFour(), GreaterThan(3))
        self.eval_unmet_predicate(p, environ, "Number 5 doesn't equal 4")


class TestAnyPredicate(BasePredicateTester):
    
    def test_one_true(self):
        environ = {'test_number': 2}
        p = predicates.Any(EqualsTwo())
        self.eval_met_predicate(p, environ)
        
    def test_one_false(self):
        environ = {'test_number': 3}
        p = predicates.Any(EqualsTwo())
        self.eval_unmet_predicate(p, environ, 
                         "At least one of the following predicates must be "
                         "met: Number 3 doesn't equal 2")
    
    def test_two_true(self):
        environ = {'test_number': 4}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.eval_met_predicate(p, environ)
    
    def test_two_false(self):
        environ = {'test_number': 1}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.eval_unmet_predicate(p, environ, 
                         "At least one of the following predicates must be "
                         "met: Number 1 doesn't equal 4, 1 is not greater "
                         "than 3")
    
    def test_two_mixed(self):
        environ = {'test_number': 5}
        p = predicates.Any(EqualsFour(), GreaterThan(3))
        self.eval_met_predicate(p, environ)


class TestIsUserPredicate(BasePredicateTester):
    
    def test_user_without_credentials(self):
        environ = {}
        p = predicates.is_user('gustavo')
        self.eval_unmet_predicate(p, environ,
                                  'The current user must be "gustavo"')
    
    def test_user_without_userid(self):
        environ = {'repoze.what.credentials': {}}
        p = predicates.is_user('gustavo')
        self.eval_unmet_predicate(p, environ,
                                  'The current user must be "gustavo"')
    
    def test_right_user(self):
        environ = make_environ('gustavo')
        p = predicates.is_user('gustavo')
        self.eval_met_predicate(p, environ)
    
    def test_wrong_user(self):
        environ = make_environ('andreina')
        p = predicates.is_user('gustavo')
        self.eval_unmet_predicate(p, environ,
                                  'The current user must be "gustavo"')


class TestNotAnonymousPredicate(BasePredicateTester):
    
    def test_authenticated_user(self):
        environ = make_environ('gustavo')
        p = predicates.not_anonymous()
        self.eval_met_predicate(p, environ)
    
    def test_anonymous_user(self):
        environ = {}
        p = predicates.not_anonymous()
        self.eval_unmet_predicate(p, environ,
                         'The current user must have been authenticated')


#{ Mock definitions


class MockPredicate(predicates.Predicate):
    message = "I'm a fake predicate"


#}
