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

from nose.tools import assert_false, eq_, ok_
from webob import Request

from repoze.what.internals import setup_request, forge_request

from tests import MockGroupAdapter


def test_request_setup():
    """
    The global authorization control and the group adapter are stored in a new
    WSGI environment variable, among with other things.
    
    """
    request = Request.blank("/")
    global_authz_control = object()
    adapter = MockGroupAdapter()
    
    setup_request(request, global_authz_control, adapter)
    
    expected_repozewhat_var = {
        'global_control': global_authz_control,
        'group_adapter': adapter,
        'cached_groups': {'membership': set(), 'no_membership': set()},
        }
    
    ok_("repoze.what" in request.environ)
    eq_(request.environ['repoze.what'], expected_repozewhat_var)


class TestForgingRequests(object):
    """Tests for the forge_request() function."""
    
    def setup(self):
        self.request = Request.blank("/this/is/the/path_info")
        setup_request(self.request, None, None)
    
    #{ First forge -- The creation of the "clear" request
    
    def test_clear_request_preserves_path_info(self):
        """
        The PATH_INFO from the original request is kept in the clear request.
        
        """
        forge_request(self.request, "/", (), {})
        clear_request = self.request.environ['repoze.what.clear_request']
        
        eq_(self.request.path_info, clear_request.path_info)
    
    def test_clear_request_includers_environ_var(self):
        """
        The "repoze.what" environment variable is copied to the clear request.
        
        """
        forge_request(self.request, "/", (), {})
        clear_request = self.request.environ['repoze.what.clear_request']
        
        eq_(self.request.environ['repoze.what'],
            clear_request.environ['repoze.what'])
    
    def test_routing_args(self):
        """The routing_args must be excluded from the copy of the request."""
        self.request.urlvars = {'foo': "bar"}
        self.request.urlargs = ("baz", )
        
        forge_request(self.request, "/", (), {})
        clear_request = self.request.environ['repoze.what.clear_request']
        
        assert_false("wsgiorg.routing_args" in clear_request.environ)
    
    def test_request_copy_with_query_string(self):
        """Clear requests have no query string."""
        self.request.query_string = "var=val"
        
        forge_request(self.request, "/", (), {})
        clear_request = self.request.environ['repoze.what.clear_request']
        
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
        
        forge_request(request, "/", (), {})
        clear_request = request.environ['repoze.what.clear_request']
        
        eq_(clear_request.method, "GET")
        eq_(len(clear_request.GET), 0)
        eq_(len(clear_request.POST), 0)
    
    #{ Subsequent forges -- The reuse of the "clear" request
    
    def test_clear_request_is_reused(self):
        """Subsequent request forges are based on the clear request."""
        forge_request(self.request, "/", (), {})
        clear_request = self.request.environ['repoze.what.clear_request']
        
        # Marking this request object so that we can check that it's been used
        # later:
        clear_request.environ['this_is_the_clear_request'] = True
        
        second_forged_request = forge_request(self.request, "/", (), {})
        
        ok_(second_forged_request.environ['this_is_the_clear_request'])
    
    def test_original_clear_request_is_not_modified(self):
        """The clear request is not be modified when it's forged."""
        forge_request(self.request, "/somewhere", (), {})
        original_clear_req = self.request.environ['repoze.what.clear_request']
        
        eq_(original_clear_req.path_info, "/this/is/the/path_info")
    
    def test_with_no_query_string(self):
        forged_request = forge_request(
            self.request,
            "/path",
            ("arg1", "arg2"),
            {'name': "value"},
            )
        
        eq_(forged_request.path_info, "/path")
        eq_(forged_request.query_string, "")
        eq_(forged_request.urlargs, ("arg1", "arg2"))
        eq_(forged_request.urlvars, dict(name="value"))
    
    def test_with_query_string(self):
        """The forged request never contains a query string."""
        forged_request = forge_request(
            self.request,
            "/path?var1=val1&var2=val2",
            ("argA", ),
            {'name': "val"},
            )
        eq_(forged_request.path_info, "/path")
        eq_(forged_request.query_string, "var1=val1&var2=val2")
        eq_(forged_request.urlargs, ("argA", ))
        eq_(forged_request.urlvars, dict(name="val"))
    
    #}
