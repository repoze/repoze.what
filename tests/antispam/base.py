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

"""
Utilities to test the anti-spam module.

"""

from repoze.what.antispam.services import BaseAntiSpamService
from repoze.what.antispam.queues import BaseSpamQueue, BaseSpammerQueue


class FakeAntiSpamService(BaseAntiSpamService):
    service_name = 'fake_service'
    
    def __init__(self, is_spam=False, is_spammer=False):
        self.results = {'is_spam': is_spam, 'is_spammer': is_spammer}
    
    def is_spam(self, environ, message=None, title=None, author=None,
                email=None, url=None):
        return self.results['is_spam']
    
    def is_spammer(self, environ, name=None, email=None, url=None):
        return self.results['is_spammer']
    
    def spam_feedback(self, spam):
        pass
    
    def spammer_feedback(self, spammer):
        pass


class FakeSpamQueue(BaseSpamQueue):
    pass
