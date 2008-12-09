# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008, Gustavo Narea <me@gustavonarea.net>
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

"""Tests for the antispam module."""

import unittest

from zope.interface.verify import verifyClass
from repoze.who.interfaces import IIdentifier

from repoze.what.antispam import AntiSpamManager

from base import FakeAntiSpamService, AnotherFakeAntiSpamService, \
                 FakeSpamQueue, FakeSpammerQueue

from tests.base import FakeLogger

class TestAntiSpamManager(unittest.TestCase):
    """Tests for the basic functionality of the anti-spam manager"""
    
    def test_constructor_with_only_services(self):
        services = [FakeAntiSpamService(), AnotherFakeAntiSpamService()]
        mgr = AntiSpamManager(services)
        services_dict = {'fake_service': services[0],
                         'another_fake_service': services[1]}
        self.assertEqual(mgr.antispam_services, services_dict)
        self.assertEqual(mgr.default_service, None)
        self.assertEqual(mgr.queues['spam'], None)
        self.assertEqual(mgr.queues['spammer'], None)
    
    def test_constructor_with_default_service(self):
        services = [FakeAntiSpamService(), AnotherFakeAntiSpamService()]
        mgr = AntiSpamManager(services, 'fake_service')
        self.assertEqual(mgr.default_service, services[0])
    
    def test_constructor_with_queues(self):
        services = [FakeAntiSpamService(), AnotherFakeAntiSpamService()]
        spam_queue = FakeSpamQueue()
        spammer_queue = FakeSpammerQueue()
        mgr = AntiSpamManager(services, spam_queue=spam_queue,
                              spammer_queue=spammer_queue)
        self.assertEqual(mgr.queues['spam'], spam_queue)
        self.assertEqual(mgr.queues['spammer'], spammer_queue)

    def test_implements(self):
        verifyClass(IIdentifier, AntiSpamManager, tentative=True)
        # Some methods are not used:
        mgr = AntiSpamManager([])
        self.assertEqual(mgr.remember(None, None), None)
        self.assertEqual(mgr.forget(None, None), None)
    
    def test_loads_itself_into_environ(self):
        mgr = AntiSpamManager([FakeAntiSpamService()])
        environ = {}
        mgr.identify(environ)
        self.assertTrue('repoze.what.antispam' in environ)
        self.assertEqual(environ['repoze.what.antispam'], mgr)
    
    def test_configuring_auth_without_existing_identifiers(self):
        auth_args = {}
        mgr = AntiSpamManager([FakeAntiSpamService()])
        mgr.set_auth_settings(auth_args)
        expected_identifiers = ('antispam_mgr', mgr)
        self.assertEqual(auth_args['identifiers'][0], expected_identifiers)
    
    def test_configuring_auth_with_existing_identifiers(self):
        auth_args = {'identifiers': ['I came first']}
        mgr = AntiSpamManager([FakeAntiSpamService()])
        mgr.set_auth_settings(auth_args)
        expected_identifier = ('antispam_mgr', mgr)
        self.assertEqual(auth_args['identifiers'][0], expected_identifier)
        self.assertEqual(auth_args['identifiers'][1], 'I came first')


class TestSpamCheckingFunctionality(unittest.TestCase):
    """Tests for the spam checking functionality in the anti-spam manager"""
    
    def setUp(self):
        self.logger = FakeLogger()
        self.environ = {'repoze.who.logger': self.logger}
    
    def test_checking_spam_basic(self):
        # ----- Setting up the manager:
        services = [FakeAntiSpamService(is_spam=True),
                    AnotherFakeAntiSpamService(is_spam=True)]
        spam_queue = FakeSpamQueue()
        spammer_queue = FakeSpammerQueue()
        mgr = AntiSpamManager(services, 'fake_service', spam_queue, 
                              spammer_queue)
        # ----- Testing it:
        self.assertTrue(mgr.check('spam', self.environ, {}))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}',
            'Using the available anti-spam services: another_fake_service, '
                'fake_service',
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        info_messages = [
            'Service "another_fake_service" says it is spam',
            'Added spam to the moderation queue'
            ]
        self.assertEqual(info_messages, self.logger.messages['info'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['critical'])
        self.assertEqual([], self.logger.messages['error'])
        self.assertEqual([], self.logger.messages['warning'])
    
    def test_checking_spam_without_queues_and_default_service(self):
        # ----- Setting up the manager:
        services = [FakeAntiSpamService(is_spam=True),
                    AnotherFakeAntiSpamService(is_spam=True)]
        mgr = AntiSpamManager(services)
        # ----- Testing it:
        self.assertTrue(mgr.check('spam', self.environ, {}))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}',
            'Using the available anti-spam services: another_fake_service, '
                'fake_service',
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        info_messages = [
            'Service "another_fake_service" says it is spam'
            ]
        self.assertEqual(info_messages, self.logger.messages['info'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['critical'])
        self.assertEqual([], self.logger.messages['error'])
        self.assertEqual([], self.logger.messages['warning'])
    
    def test_checking_spam_with_services_filter(self):
        # ----- Setting up the manager:
        services = [FakeAntiSpamService(is_spam=True),
                    AnotherFakeAntiSpamService()]
        spam_queue = FakeSpamQueue()
        spammer_queue = FakeSpammerQueue()
        mgr = AntiSpamManager(services, 'fake_service', spam_queue, 
                              spammer_queue)
        # ----- Testing it:
        self.assertTrue(mgr.check('spam', self.environ, {}, 
                                  services=['fake_service']))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}',
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        info_messages = [
            'Service "fake_service" says it is spam',
            'Added spam to the moderation queue'
            ]
        self.assertEqual(info_messages, self.logger.messages['info'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['critical'])
        self.assertEqual([], self.logger.messages['error'])
        self.assertEqual([], self.logger.messages['warning'])
    
    def test_checking_spam_with_unknown_service(self):
        # ----- Setting up the manager:
        services = [FakeAntiSpamService(is_spam=True)]
        mgr = AntiSpamManager(services)
        # ----- Testing it:
        self.assertTrue(mgr.check('spam', self.environ, {}, 
                                  services=['non-existing-service']))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}',
            'Using the default anti-spam service (fake_service)',
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        info_messages = [
            'Service "fake_service" says it is spam',
            ]
        self.assertEqual(info_messages, self.logger.messages['info'])
        error_messages = [
            'Anti-spam service "non-existing-service" is unknown',
            ]
        self.assertEqual(error_messages, self.logger.messages['error'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['critical'])
        self.assertEqual([], self.logger.messages['warning'])
    
    def test_checking_spam_with_no_usable_service(self):
        # ----- Setting up the manager:
        services = []
        mgr = AntiSpamManager(services)
        # ----- Testing it:
        self.assertFalse(mgr.check('spam', self.environ, {}))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}'
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        critical_messages = [
            'No defined anti-spam service has been selected',
            ]
        self.assertEqual(critical_messages, self.logger.messages['critical'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['info'])
        self.assertEqual([], self.logger.messages['error'])
        self.assertEqual([], self.logger.messages['warning'])
    
    def test_checking_spam_and_handling_service_error(self):
        # ----- Setting up the manager:
        services = [FakeAntiSpamService(raise_exception=True)]
        mgr = AntiSpamManager(services)
        # ----- Testing it:
        self.assertTrue(mgr.check('spam', self.environ, {}))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}',
            'Using the available anti-spam services: fake_service',
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        critical_messages = [
            'ServiceError: This is a fake anti-spam service error',
            ]
        self.assertEqual(critical_messages, self.logger.messages['critical'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['error'])
        self.assertEqual([], self.logger.messages['warning'])
        self.assertEqual([], self.logger.messages['info'])
    
    def test_checking_spam_is_actually_ham(self):
        # ----- Setting up the manager:
        services = [FakeAntiSpamService(is_spam=False),
                    AnotherFakeAntiSpamService(is_spam=False)]
        spam_queue = FakeSpamQueue()
        spammer_queue = FakeSpammerQueue()
        mgr = AntiSpamManager(services, 'fake_service', spam_queue, 
                              spammer_queue)
        # ----- Testing it:
        self.assertFalse(mgr.check('spam', self.environ, {}))
        debug_messages = [
            'Verification type: spam',
            'Verification variables: {}',
            'Using the available anti-spam services: another_fake_service, '
                'fake_service',
            ]
        self.assertEqual(debug_messages, self.logger.messages['debug'])
        info_messages = [
            'Service "another_fake_service" says it is not spam',
            'Service "fake_service" says it is not spam',
            ]
        self.assertEqual(info_messages, self.logger.messages['info'])
        # Checking that the others are empty:
        self.assertEqual([], self.logger.messages['critical'])
        self.assertEqual([], self.logger.messages['error'])
        self.assertEqual([], self.logger.messages['warning'])
