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

"""Tests for the services of the anti-spam module."""

import unittest

from repoze.what.antispam.services import BaseAntiSpamService

from base import FakeAntiSpamService


class TestBaseAntiSpamService(unittest.TestCase):
    
    def setUp(self):
        self.service = BaseAntiSpamService()
        
    def test_service_name_is_undefined(self):
        self.assertEqual(self.service.service_name, None)
        
    def test_abstract_methods(self):
        self.assertRaises(NotImplementedError, self.service.is_spam, None)
        self.assertRaises(NotImplementedError, self.service.is_spammer, None)
        self.assertRaises(NotImplementedError, self.service.spam_feedback,
                          None)
        self.assertRaises(NotImplementedError, self.service.spammer_feedback,
                          None)


class TestAntiSpamService(unittest.TestCase):
    
    def setUp(self):
        self.service = FakeAntiSpamService()
    
    def test_service_name_is_defined(self):
        self.assertEqual(self.service.service_name, 'fake_service')
