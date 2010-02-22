# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
# Copyright (c) 2009-2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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
import unittest

from webob import Request

from repoze.what.internals import _Credentials, setup_request, forge_request

from tests.base import FakeGroupSourceAdapter, FakePermissionSourceAdapter


class TestSettingUpRequest(unittest.TestCase):
    """Tests for the setup_request() function."""
    
    def test_no_userid_and_no_adapters(self):
        environ = {}
        req = setup_request(environ, None, None, None)
        assert len(req.environ) >= 4
        # Checking the credentials:
        assert len(req.environ['repoze.what.credentials']) == 3
        assert req.environ['repoze.what.credentials']['repoze.what.userid'] is None
        assert len(req.environ['repoze.what.credentials']['groups']) == 0
        assert len(req.environ['repoze.what.credentials']['permissions']) == 0
        # Checking the adapters:
        assert len(req.environ['repoze.what.adapters']) == 2
        assert req.environ['repoze.what.adapters']['groups'] is None
        assert req.environ['repoze.what.adapters']['permissions'] is None
    
    def test_with_userid_and_adapters(self):
        group_adapters = {'my_group': FakeGroupSourceAdapter()}
        permission_adapters = {'my_perm': FakePermissionSourceAdapter()}
        environ = {}
        req = setup_request(environ, "rms", group_adapters, permission_adapters)
        assert len(req.environ) >= 4
        # Checking the credentials:
        assert len(req.environ['repoze.what.credentials']) == 3
        assert (req.environ['repoze.what.credentials']['repoze.what.userid'] ==
                "rms")
        assert len(req.environ['repoze.what.credentials']['groups']) == 2
        assert len(req.environ['repoze.what.credentials']['permissions']) == 2
        # Checking the adapters:
        assert len(req.environ['repoze.what.adapters']) == 2
        assert req.environ['repoze.what.adapters']['groups'] is group_adapters
        assert (req.environ['repoze.what.adapters']['permissions'] is
                permission_adapters)
    
    def test_with_global_authz_control(self):
        global_authz_control = object()
        req = setup_request({}, None, None, None, global_authz_control)
        assert "repoze.what.global_control" in req.environ
        assert req.environ['repoze.what.global_control'] == global_authz_control
    
    def test_without_global_authz_control(self):
        req = setup_request({}, None, None, None, None)
        assert "repoze.what.global_control" in req.environ
        assert req.environ['repoze.what.global_control'] is None
    
    def test_request_copy(self):
        """
        A clear copy of the environ must be set in the environment, so it won't
        have to be built many times to verify authorization.
        
        """
        # Checking with a GET request:
        environ1 = {
            'SCRIPT_NAME': "/trac",
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "GET",
            'QUERY_STRING': "var=val",
            }
        req1 = setup_request(environ1, None, None, None)
        assert "repoze.what.clear_request" in req1.environ
        clear_request1 = req1.environ['repoze.what.clear_request']
        assert clear_request1.script_name == "/trac"
        assert clear_request1.path_info == "/wiki"
        assert clear_request1.method == "GET"
        assert len(clear_request1.GET) == 0
        # Checking with a POST request:
        environ2 = {
            'SCRIPT_NAME': "/trac",
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "POST",
            'CONTENT_LENGTH': "7",
            'wsgi.input': StringIO("var=val"),
            }
        req2 = setup_request(environ2, None, None, None)
        assert environ2['CONTENT_LENGTH'] == "7"
        assert "repoze.what.clear_request" in req2.environ
        clear_request2 = req2.environ['repoze.what.clear_request']
        assert clear_request2.script_name == "/trac"
        assert clear_request2.path_info == "/wiki"
        assert clear_request2.method == "GET"
        assert len(clear_request2.GET) == 0
        assert len(clear_request2.POST) == 0
        # Checking with a POST request and a query string:
        environ3 = {
            'SCRIPT_NAME': "/trac",
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "POST",
            'CONTENT_LENGTH': "7",
            'QUERY_STRING': "foo=bar",
            'wsgi.input': StringIO("var=val"),
            }
        req3 = setup_request(environ3, None, None, None)
        assert environ3['CONTENT_LENGTH'] == "7"
        assert "repoze.what.clear_request" in req3.environ
        clear_request3 = req3.environ['repoze.what.clear_request']
        assert clear_request3.script_name == "/trac"
        assert clear_request3.path_info == "/wiki"
        assert clear_request3.method == "GET"
        assert len(clear_request3.GET) == 0
        assert len(clear_request3.POST) == 0


class TestForgingRequests(unittest.TestCase):
    """Tests for the forge_request() function."""
    
    def setUp(self):
        req = Request.blank("/this/is/the/path_info")
        req = setup_request(req.environ, None, None, None)
        self.original_environ = req.environ
    
    def test_original_clear_request_is_not_modified(self):
        forge_request(self.original_environ, "/somewhere", (), {})
        original_clear_req = self.original_environ['repoze.what.clear_request']
        assert original_clear_req.path_info == "/this/is/the/path_info"
    
    def test_with_no_query_string(self):
        forged_req = forge_request(
            self.original_environ,
            "/path",
            ("arg1", "arg2"),
            {'name': "value"},
            )
        assert forged_req.path_info == "/path"
        assert forged_req.query_string == ""
        assert forged_req.urlargs == ("arg1", "arg2")
        assert forged_req.urlvars == dict(name="value")
    
    def test_with_query_string(self):
        forged_req = forge_request(
            self.original_environ,
            "/path?var1=val1&var2=val2",
            ("argA", ),
            {'name': "val"},
            )
        assert forged_req.path_info == "/path"
        assert forged_req.query_string == "var1=val1&var2=val2"
        assert forged_req.urlargs == ("argA", )
        assert forged_req.urlvars == dict(name="val")


class TestCredentials(unittest.TestCase):
    """Tests for the repoze.what credentials dict."""
    
    def test_constructor(self):
        # Setup:
        group_adapters = object()
        permission_adapters = object()
        credentials = _Credentials("foo", group_adapters, permission_adapters)
        # Tests:
        assert len(credentials) == 3
        assert credentials['repoze.what.userid'] == "foo"
        assert "groups" in credentials
        assert "permissions" in credentials
        assert not credentials._groups_loaded
        assert not credentials._permissions_loaded
    
    def test_setting_groups_and_permissions(self):
        # Setup:
        group_adapters = object()
        permission_adapters = object()
        credentials = _Credentials("foo", group_adapters, permission_adapters)
        # Tests:
        groups = ("g1", "g2", "g3")
        permissions = ("p1", "p2")
        credentials['groups'] = groups
        credentials['permissions'] = permissions
        assert credentials._groups_loaded
        assert credentials._permissions_loaded
    
    def test_getting_groups_and_permissions(self):
        group_adapters = {'my_group': FakeGroupSourceAdapter()}
        permission_adapters = {'my_perm': FakePermissionSourceAdapter()}
        credentials = _Credentials("rms", group_adapters, permission_adapters)
        assert credentials['groups'] == set(["admins", "developers"])
        assert credentials['permissions'] == set(["edit-site", "commit"])
        assert credentials._groups_loaded
        assert credentials._permissions_loaded
    
    def test_getting_groups_and_permissions_for_non_existing_user(self):
        credentials = _Credentials("foo", None, None)
        assert credentials['groups'] == set()
        assert credentials['permissions'] == set()
        assert credentials._groups_loaded
        assert credentials._permissions_loaded
