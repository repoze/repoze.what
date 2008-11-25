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

"""Stuff required to setup the test suite."""


from repoze.what.middleware import setup_auth
from repoze.what.adapters import BaseSourceAdapter


class FakeAuthenticator(object):
    """Fake repoze.who authenticator plugin"""
    credentials = {
        u'rms': u'freedom',
        u'linus': u'linux',
        u'sballmer': u'developers',
        u'guido': u'pythonic',
        u'rasmus': u'php'
        }

    def authenticate(self, environ, identity):
        login = identity['login']
        pass_ = identity['password']
        if login in self.credentials and pass_ == self.credentials[login]:
            return login


class FakeGroupSourceAdapter(BaseSourceAdapter):
    """Mock group source adapter"""

    def __init__(self):
        super(FakeGroupSourceAdapter, self).__init__()
        self.fake_sections = {
            u'admins': set([u'rms']),
            u'developers': set([u'rms', u'linus']),
            u'trolls': set([u'sballmer']),
            u'python': set(),
            u'php': set()
            }

    def _get_all_sections(self):
        return self.fake_sections

    def _get_section_items(self, section):
        return self.fake_sections[section]

    def _find_sections(self, identity):
        username = identity['repoze.who.userid']
        return set([n for (n, g) in self.fake_sections.items()
                    if username in g])

    def _include_items(self, section, items):
        self.fake_sections[section] |= items

    def _exclude_items(self, section, items):
        for item in items:
            self.fake_sections[section].remove(item)

    def _item_is_included(self, section, item):
        return item in self.fake_sections[section]

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        del self.fake_sections[section]

    def _section_exists(self, section):
        return self.fake_sections.has_key(section)


class FakePermissionSourceAdapter(FakeGroupSourceAdapter):
    """Mock permissions source adapter"""

    def __init__(self):
        super(FakePermissionSourceAdapter, self).__init__()
        self.fake_sections = {
            u'see-site': set([u'trolls']),
            u'edit-site': set([u'admins', u'developers']),
            u'commit': set([u'developers'])
            }

    def _find_sections(self, group_name):
        return set([n for (n, p) in self.fake_sections.items()
                    if group_name in p])


class FakeLogger(object):
    
    def __init__(self):
        self.messages = {
            'critical': [],
            'error': [],
            'warning': [],
            'info': [],
            'debug': []
            }
    
    def critical(self, msg):
        self.messages['critical'].append(msg)
    
    def error(self, msg):
        self.messages['error'].append(msg)
    
    def warning(self, msg):
        self.messages['warning'].append(msg)
    
    def info(self, msg):
        self.messages['info'].append(msg)
    
    def error(self, msg):
        self.messages['error'].append(msg)
