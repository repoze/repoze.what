# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011, Gustavo Narea <me@gustavonarea.net>.
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
Tests for the built-in Access Request Objects.

"""

from nose.tools import assert_false, ok_
from webob import Request

from repoze.what.aros import *


class TestAnonymous(object):
    """Tests for the ANONYMOUS ARO."""
    
    def test_anonymous(self):
        """There's a match if and only if there's no REMOTE_USER"""
        request = Request.blank("/")
        ok_(ANONYMOUS(request))
    
    def test_authenticated(self):
        """There's no match in authenticated requests."""
        request = Request.blank("/", {'REMOTE_USER': "andreina"})
        assert_false(ANONYMOUS(request))


class TestAuthenticated(object):
    """Tests for the AUTHENTICATED ARO."""
    
    def test_anonymous(self):
        """There's no match in authenticated requests."""
        request = Request.blank("/")
        assert_false(AUTHENTICATED(request))
    
    def test_authenticated(self):
        """There's a match if and only if there's no REMOTE_USER"""
        request = Request.blank("/", {'REMOTE_USER': "andreina"})
        ok_(AUTHENTICATED(request))


class TestUserId(object):
    """Tests for the :class:`UserId` ARO."""
    
    def test_anonymous(self):
        """There's no match in anonymous requests."""
        aro = UserId("carla")
        request = Request.blank("/")
        assert_false(aro(request))
    
    def test_authenticated_but_not_right_user(self):
        """There's no match in authenticated requests from a different user."""
        aro = UserId("carla")
        request = Request.blank("/", {'REMOTE_USER': "andreina"})
        assert_false(aro(request))
    
    def test_authenticated_and_right_user(self):
        """There's a match if and only if the expected user made the request."""
        aro = UserId("carla")
        request = Request.blank("/", {'REMOTE_USER': "carla"})
        ok_(aro(request))


class TestGroupId(object):
    """Tests for the :class:`GroupId` ARO."""
    
    def test_membership(self):
        pass
    
    def test_no_membership(self):
        pass
