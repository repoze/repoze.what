# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
# Copyright (c) 2009-2011, Gustavo Narea <me@gustavonarea.net>.
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
Tests for the internal utilities.

"""

from StringIO import StringIO

from nose.tools import assert_false, eq_
from webob import Request

from repoze.what.internals import setup_request, forge_request

from tests import MockGroupAdapter


class TestSettingUpRequest(object):
    """Tests for the setup_request() function."""
    
    def test_with_group_adapter_and_global_control(self):
        """
        Both the global authz control and the group adapter must be attached to
        the WSGI environ.
        
        """
        request = Request.blank("/")
        global_authz_control = object()
        adapter = MockGroupAdapter()
        
        setup_request(request, global_authz_control, adapter)
        
        eq_(request.environ['repoze.what.global_control'], global_authz_control)
        eq_(request.environ['repoze.what.group_adapter'], adapter)
    
    #{ Clear requests
    
    def test_routing_args(self):
        """The routing_args must be excluded from the copy of the request."""
        request = Request.blank("/")
        request.urlvars = {'foo': "bar"}
        request.urlargs = ("baz", )
        
        setup_request(request, None, None)
        clear_request = request.environ['repoze.what.clear_request']
        
        assert_false("wsgiorg.routing_args" in clear_request.environ)
    
    def test_request_copy_with_query_string(self):
        """Clear requests have no query string."""
        request = Request.blank("/wiki?var=val")
        
        setup_request(request, None, None)
        clear_request = request.environ['repoze.what.clear_request']
        
        eq_(clear_request.path_info, "/wiki")
        eq_(clear_request.method, "GET")
        eq_(len(clear_request.GET), 0)
    
    def test_post_request_copy(self):
        """
        Clear requests are always GET requests, regardless of the original
        request method.
        
        """
        environ = {
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "POST",
            'CONTENT_LENGTH': "7",
            'wsgi.input': StringIO("var=val"),
            }
        request = Request(environ)
        
        setup_request(request, None, None)
        clear_request = request.environ['repoze.what.clear_request']
        
        eq_(clear_request.method, "GET")
        eq_(len(clear_request.GET), 0)
        eq_(len(clear_request.POST), 0)
    
    #}


class TestForgingRequests(object):
    """Tests for the forge_request() function."""
    
    def setup(self):
        self.request = Request.blank("/this/is/the/path_info")
        setup_request(self.request, None, None)
    
    def test_original_clear_request_is_not_modified(self):
        """The original request must not be modified."""
        forge_request(self.request, "/somewhere", (), {})
        original_clear_req = self.request.environ['repoze.what.clear_request']
        eq_(original_clear_req.path_info, "/this/is/the/path_info")
    
    def test_with_no_query_string(self):
        forged_req = forge_request(
            self.request,
            "/path",
            ("arg1", "arg2"),
            {'name': "value"},
            )
        eq_(forged_req.path_info, "/path")
        eq_(forged_req.query_string, "")
        eq_(forged_req.urlargs, ("arg1", "arg2"))
        eq_(forged_req.urlvars, dict(name="value"))
    
    def test_with_query_string(self):
        """The forged request must not contain a query string."""
        forged_req = forge_request(
            self.request,
            "/path?var1=val1&var2=val2",
            ("argA", ),
            {'name': "val"},
            )
        eq_(forged_req.path_info, "/path")
        eq_(forged_req.query_string, "var1=val1&var2=val2")
        eq_(forged_req.urlargs, ("argA", ))
        eq_(forged_req.urlvars, dict(name="val"))
