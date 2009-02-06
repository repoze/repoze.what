# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>
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
Utilities for the test suite of :mod:`repoze.what`.

"""


from repoze.what.middleware import setup_auth
from repoze.what.adapters import BaseSourceAdapter

__all__ = ['FakeAuthenticator', 'FakeGroupSourceAdapter', 
           'FakePermissionSourceAdapter', 'FakeLogger', 
           'encode_multipart_formdata']

class FakeAuthenticator(object):
    """
    Fake :mod:`repoze.who` authenticator plugin.
    
    It will authenticate if you use one of the following credentials (username
    and password):
    
    * ``rms``: ``freedom``
    * ``linus``: ``linux``
    * ``sballmer``: ``developers``
    * ``guido``: ``pythonic``
    * ``rasmus``: ``php``
    
    """
    
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
    """
    Mock group source adapter.
    
    The `fake` source it handles contains the following groups:
    
    * ``admins``: ``rms``
    * ``developers``: ``rms``, ``linus``
    * ``trolls``: ``sballmer``
    * ``python``: `(empty)`
    * ``php``: `(empty)`
    
    """

    def __init__(self, *args, **kwargs):
        super(FakeGroupSourceAdapter, self).__init__(*args, **kwargs)
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

    def _find_sections(self, credentials):
        username = credentials['repoze.what.userid']
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
        return section in self.fake_sections


class FakePermissionSourceAdapter(FakeGroupSourceAdapter):
    """
    `Mock` permissions source adapter.
    
    The `fake` source it handles contains the following permissions:
    
    * ``see-site``: ``trolls``
    * ``edit-site: ``admins``, ``developers``
    * ``commit``: ``developers``
    
    """

    def __init__(self, *args, **kwargs):
        super(FakePermissionSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'see-site': set([u'trolls']),
            u'edit-site': set([u'admins', u'developers']),
            u'commit': set([u'developers'])
            }

    def _find_sections(self, group_name):
        return set([n for (n, p) in self.fake_sections.items()
                    if group_name in p])


class FakeLogger(object):
    """A mock Python logger."""
    
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
    
    def debug(self, msg):
        self.messages['debug'].append(msg)


# This function was stolen from repoze.who.tests:
def encode_multipart_formdata(fields):
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body
