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

"""Base functionality for spam/moderation queues."""


class _BaseQueue(object):
    def get_all(self):
        pass
    def get_items(self, **known_attributes):
        pass
    def add_item(self, **known_attributes):
        pass
    def remove_items(self, item):
        pass
    def empty_out(self):
        pass


class BaseSpamQueue(_BaseQueue):
    pass


class BaseSpammerQueue(_BaseQueue):
    pass


class PotentialSpam(object):
    """A potential spam message"""
    
    def __init__(self, comment=None, title=None, author=None, email= None,
                 url=None, spam_by=[], ham_by=[], extra_data={}):
        self.comment = comment
        self.title = title
        self.author = author
        self.author_email = email
        self.author_url = url
        self.spam_by = spam_by
        self.ham_by = ham_by
        self.extra_data = extra_data


class PotentialSpammer(object):
    def __init__(self, name=None, email=None, url=None, spam_by=[], ham_by=[],
                 extra_data={}):
        self.name = name
        self.email = email
        self.url = url
        self.spam_by = spam_by
        self.ham_by = ham_by
        self.extra_data = extra_data
