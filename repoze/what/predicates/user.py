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
Predicate checkers for the current user.

"""

from repoze.what.predicates.base import Predicate

__all__ = ['is_user', 'is_anonymous', 'not_anonymous']


class is_user(Predicate):
    """
    Check that the authenticated user's identifier is the specified one.
    
    :param userid: The required user identificator.
    :type userid: basestring
    
    Example::
    
        p = is_user('linus')
    
    """
    
    message = u'The current user must be "%(userid)s"'
    
    def __init__(self, userid, **kwargs):
        super(is_user, self).__init__(**kwargs)
        self.userid = userid

    def evaluate(self, userid, request, helpers):
        if userid != self.userid:
            self.unmet()


class is_anonymous(Predicate):
    """
    Check that the current user is anonymous.
    
    Example::
    
        # The user must be anonymous!
        p = is_anonymous()
    
    """
    
    message = u"The current user must be anonymous"

    def evaluate(self, userid, request, helpers):
        if userid:
            self.unmet()


class not_anonymous(Predicate):
    """
    Check that the current user has been authenticated.
    
    Example::
    
        # The user must have been authenticated!
        p = not_anonymous()
    
    """
    
    message = u"The current user must have been authenticated"
    
    def evaluate(self, userid, request, helpers):
        if not userid:
            self.unmet()
