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
Tests for the base predicate checkers.

"""

from unittest import TestCase

from repoze.what.predicates.generic import Predicate, CompoundPredicate, \
                                           NotAuthorizedError

from unit_tests.base import FakeLogger
from unit_tests.predicates import BasePredicateTester, make_environ, \
                                  EqualsTwo, EqualsFour


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


#{ Mock definitions


class MockPredicate(Predicate):
    message = "I'm a fake predicate"


#}
