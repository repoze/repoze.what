# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
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
Test suite for request-to-target mappers.

"""

from nose.tools import assert_raises, eq_

from repoze.what.mappers import Mapper, PathInfoMapper, RoutingArgsMapper

from tests.base import make_request


#{ Tests for generic stuff


class TestMapper(object):
    """
    Test case for the base :class:`Mapper`.
    
    """
    
    def test_get_aco(self):
        """
        The ``.get_aco()`` method must not be implemented by default.
        
        """
        m = Mapper()
        assert_raises(NotImplementedError, m.get_aco, None)


#{ Tests for built-in mappers


class TestPathInfoMapper(object):
    """
    Test case for the built-in PATH_INFO mapper.
    
    There aren't too many tests for this because all it does is use the
    path normalizer under-the-hood.
    
    """
    
    def test_no_path_info(self):
        """The ACO is an slash if the PATH_INFO is empty."""
        mapper = PathInfoMapper()
        
        eq_("/", mapper.get_aco(make_request(PATH_INFO="")))
    
    def test_root(self):
        """The ACO is an slash if the PATH_INFO is an slash too."""
        mapper = PathInfoMapper()
        
        eq_("/", mapper.get_aco(make_request(PATH_INFO="/")))
    
    def test_no_trailing_slash(self):
        """Returned ACOs always have a trailing slash."""
        mapper = PathInfoMapper()
        
        eq_("/foo/", mapper.get_aco(make_request(PATH_INFO="/foo")))


class TestRoutingArgsMapper(object):
    """
    Test case for the ``wsgiorg.routing_args`` mappers.
    
    """
    
    def make_request_with_routing_args(self, positional=(), named=None):
        request = make_request()
        request.environ['wsgiorg.routing_args'] = (positional, named or {})
        return request
    
    def test_resource_formatter(self):
        """The arguments should be concatenated and turned into a path string"""
        # One argument without slashes:
        eq_(RoutingArgsMapper.format_aco(["baz"]), "/baz/")
        # One argument with slashes:
        eq_(RoutingArgsMapper.format_aco(["baz/bar"]), "/baz/bar/")
        # Two arguments without slashes:
        eq_(RoutingArgsMapper.format_aco(["baz", "bar"]), "/baz/bar/")
        # Two arguments with slashes:
        eq_(RoutingArgsMapper.format_aco(["a/b", "c/foo"]), "/a/b/c/foo/")
    
    def test_named_arguments(self):
        """Named arguments can be picked and put into the ACO."""
        # One argument:
        m1 = RoutingArgsMapper(["foo"])
        request1 = self.make_request_with_routing_args(named={'foo': "baz"})
        eq_("/baz/", m1.get_aco(request1))
        
        # Two arguments:
        m2 = RoutingArgsMapper(["foo", "bar"])
        arguments = {'foo': "baz", 'bar': "fox"}
        request2 = self.make_request_with_routing_args(named=arguments)
        eq_("/baz/fox/", m2.get_aco(request2))
    
    def test_positional_arguments(self):
        """Positional arguments can be picked and put into the ACO."""
        # One argument:
        m1 = RoutingArgsMapper([1], named=False)
        request1 = self.make_request_with_routing_args(positional=["a", "baz"])
        eq_("/baz/", m1.get_aco(request1))
        
        # Two arguments:
        m2 = RoutingArgsMapper([0, 2], named=False)
        arguments = ["baz", "foo", "fox"]
        request2 = self.make_request_with_routing_args(positional=arguments)
        eq_("/baz/fox/", m2.get_aco(request2))
    
    def test_not_found_named_argument(self):
        """
        No ACO is returned if one of the required named arguments is not
        present.
        
        """
        # One argument:
        m1 = RoutingArgsMapper(["foo"])
        request1 = self.make_request_with_routing_args(named={'baz': "bar"})
        eq_(None, m1.get_aco(request1))
        
        # Two arguments:
        m2 = RoutingArgsMapper(["foo", "bar"])
        request2 = self.make_request_with_routing_args(named={'foo': "baz"})
        eq_(None, m2.get_aco(request2))
    
    def test_not_found_positional_arguments(self):
        """
        No ACO is returned if one of the required positional arguments is not
        present.
        
        """
        # One argument:
        m1 = RoutingArgsMapper([1], named=False)
        request1 = self.make_request_with_routing_args(positional=["abc"])
        eq_(None, m1.get_aco(request1))
        
        # Two arguments:
        m2 = RoutingArgsMapper([0, 2], named=False)
        arguments = ["baz", "fox"]
        request2 = self.make_request_with_routing_args(positional=arguments)
        eq_(None, m2.get_aco(request2))
    
    def test_no_args_in_url(self):
        """No ACO is returned if there's no arguments in the routing_args."""
        # Named:
        m1 = RoutingArgsMapper(["foo"])
        request1 = self.make_request_with_routing_args(named={})
        eq_(None, m1.get_aco(request1))
        
        # Positional:
        m2 = RoutingArgsMapper([1], named=False)
        request2 = self.make_request_with_routing_args(positional=[])
        eq_(None, m2.get_aco(request2))


#{ Mock definitions


class MockMapper(Mapper):
    """
    Mock mapper which will return the preset ACO.
    
    """
    
    def __init__(self, aco=None):
        self.aco = aco
        self.used = False
    
    def get_aco(self, request):
        self.used = True
        return self.aco


#}
