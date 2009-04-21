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
Test suite for repoze.what built-in predicates.

"""

from unittest import TestCase

from repoze.what.predicates.base import Predicate, CompoundPredicate, \
                                        NotAuthorizedError
from repoze.what.predicates.generic import All, Any, Not
from repoze.what.predicates.user import is_user, is_anonymous, not_anonymous

from unit_tests.base import make_environ, FakeLogger


#{ Utilities


class BasePredicateTester(TestCase):
    """Base test case for predicates."""
    
    def eval_met_predicate(self, p, environ):
        """Evaluate a predicate that should be met"""
        self.assertEqual(p.check_authorization(environ), None)
        self.assertEqual(p.is_met(environ), True)
    
    def eval_unmet_predicate(self, p, environ, expected_error):
        """Evaluate a predicate that should not be met"""
        # Testing check_authorization
        try:
            p.check_authorization(environ)
            self.fail('Predicate must not be met; expected error: %s' %
                      expected_error)
        except NotAuthorizedError, error:
            self.assertEqual(unicode(error), expected_error)
        # Testing is_met:
        self.assertEqual(p.is_met(environ), False)


#{ The test suite itself


class TestPredicate(BasePredicateTester):
    
    def test_evaluate_isnt_implemented(self):
        p = MockPredicate()
        self.failUnlessRaises(NotImplementedError, p.evaluate, None, None,
                              None)
    
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
        environ = make_environ(test_number=3)
        self.eval_unmet_predicate(p, environ, unicode_msg)
    
    def test_authorized(self):
        logger = FakeLogger()
        environ = make_environ(test_number=4)
        environ['repoze.what.logger'] = logger
        p = EqualsFour()
        p.check_authorization(environ)
        info = logger.messages['info']
        assert "Authorization granted" == info[0]
    
    def test_unauthorized(self):
        logger = FakeLogger()
        environ = make_environ(logger=logger, test_number=3)
        p = EqualsFour(msg="Go away!")
        try:
            p.check_authorization(environ)
            self.fail('Authorization must have been rejected')
        except NotAuthorizedError, e:
            self.assertEqual(str(e), "Go away!")
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: Go away!" == info[0]
    
    def test_unauthorized_with_unicode_message(self):
        unicode_msg = u'请登陆'
        logger = FakeLogger()
        environ = make_environ(logger=logger, test_number=3)
        p = EqualsFour(msg=unicode_msg)
        try:
            p.check_authorization(environ)
            self.fail('Authorization must have been rejected')
        except NotAuthorizedError, e:
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
        except NotAuthorizedError, e:
            self.assertEqual(unicode(e), message % dict(id_number=id_number))


class TestCompoundPredicate(BasePredicateTester):
    
    def test_one_predicate_works(self):
        p = EqualsTwo()
        cp = CompoundPredicate(p)
        self.assertEqual(cp.predicates, (p,))
        
    def test_two_predicates_work(self):
        p1 = EqualsTwo()
        p2 = MockPredicate()
        cp = CompoundPredicate(p1, p2)
        self.assertEqual(cp.predicates, (p1, p2))


class TestNotAuthorizedError(TestCase):
    """Tests for the NotAuthorizedError exception"""
    
    def test_string_representation(self):
        msg = 'You are not the master of Universe'
        exc = NotAuthorizedError(msg)
        self.assertEqual(msg, str(exc))


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


#{ Mock definitions


class MockPredicate(Predicate):
    message = "I'm a fake predicate"


class EqualsTwo(Predicate):
    message = "Number %(number)s doesn't equal 2"
    
    def evaluate(self, userid, request, helpers):
        number = request.environ.get('test_number')
        if number != 2:
            self.unmet(number=number)


class EqualsFour(Predicate):
    message = "Number %(number)s doesn't equal 4"
    
    def evaluate(self, userid, request, helpers):
        number = request.environ.get('test_number')
        if number != 4:
            self.unmet(number=number)


class GreaterThan(Predicate):
    message = "%(number)s is not greater than %(compared_number)s"
    
    def __init__(self, compared_number, **kwargs):
        super(GreaterThan, self).__init__(**kwargs)
        self.compared_number = compared_number
        
    def evaluate(self, userid, request, helpers):
        number = request.environ.get('test_number')
        if not number > self.compared_number:
            self.unmet(number=number, compared_number=self.compared_number)


#}
