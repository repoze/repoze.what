# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
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

from nose.tools import eq_, assert_raises, raises

from acl.aco import Target

from repoze.what.exc import MappingError, NoTargetFoundError
from repoze.what.mappers.base import Mapper, CompoundMapper
from repoze.what.mappers.pathinfo import PathInfoMapper
from repoze.what.mappers.routing_args import (PositionalArgsMapper,
                                              NamedArgsMapper, RoutesMapper, 
                                              RoutingArgsMapper)

from tests.base import make_request, FakeLogger


#{ Tests for generic stuff


class TestMapper(object):
    """
    Test case for the base :class:`Mapper`.
    
    """
    
    def test_get_target(self):
        """
        The ``.get_target()`` method must not be implemented by default.
        
        """
        m = Mapper()
        assert_raises(NotImplementedError, m.get_target, None)


class TestCompoundMapper(object):
    """
    Test case for the Compound Mapper.
    
    """
    
    def test_with_zero_mappers(self):
        cm = CompoundMapper()
        eq_(0, len(cm.mappers))
        assert_raises(NoTargetFoundError, cm.get_target, make_request())
    
    def test_with_mappers_but_no_target(self):
        # Set up:
        m1 = MockMapper()
        m2 = MockMapper()
        m3 = MockMapper()
        cm = CompoundMapper(m1, m2, m3)
        # Verifications:
        eq_(3, len(cm.mappers))
        assert_raises(NoTargetFoundError, cm.get_target, make_request())
    
    def test_with_many_mappers_but_first_one_matches(self):
        # Set up:
        m1 = MockMapper('/admin/users', 'add')
        m2 = MockMapper()
        cm = CompoundMapper(m1, m2)
        # Verifications:
        eq_(2, len(cm.mappers))
        target = cm.get_target(make_request())
        eq_(target.resource, '/admin/users')
        eq_(target.operation, 'add')
    
    def test_with_many_mappers_but_last_one_matches(self):
        # Set up:
        m1 = MockMapper()
        m2 = MockMapper('/admin/users', 'add')
        cm = CompoundMapper(m1, m2)
        # Verifications:
        eq_(2, len(cm.mappers))
        target = cm.get_target(make_request())
        eq_(target.resource, '/admin/users')
        eq_(target.operation, 'add')
    
    def test_target_found_with_logger(self):
        # Setup:
        logger = FakeLogger()
        request = make_request(logger=logger)
        m = MockMapper('/blog/posts', 'edit')
        cm = CompoundMapper(m)
        cm.get_target(request)
        # Verifications:
        debug = logger.messages['debug']
        eq_(1, len(debug), debug)
        assert debug[0].startswith('Target aco:/blog/posts#edit found by '
                                    'mapper')
        assert 'MockMapper' in debug[0]


#{ Tests for built-in mappers


class TestPathInfoMapper(object):
    """
    Test case for the built-in PATH_INFO mapper.
    
    """
    
    default_root_target = Target('/my-account', 'login')
    
    def test_constructor_without_default_operation(self):
        mapper = PathInfoMapper(self.default_root_target)
        eq_(mapper.root_target, self.default_root_target)
        eq_(mapper.trailing_slash_operation, None)
    
    def test_constructor_with_default_operation(self):
        mapper = PathInfoMapper(self.default_root_target, 'index')
        eq_(mapper.root_target, self.default_root_target)
        eq_(mapper.trailing_slash_operation, 'index')
    
    def test_root(self):
        """
        The mapper must return the root_target specified in the constructor
        if the root of the application is requested.
        
        """
        # Setup:
        request = make_request()
        mapper = PathInfoMapper(self.default_root_target)
        # --- Testing it:
        # With an empty PATH_INFO
        target = mapper.get_target(request)
        eq_(target, self.default_root_target)
        # With a slash as the PATH_INFO:
        request = make_request(PATH_INFO='/')
        target = mapper.get_target(request)
        eq_(target, self.default_root_target)
        # With ten slashes as the PATH_INFO:
        request = make_request(PATH_INFO='/'*10)
        target = mapper.get_target(request)
        eq_(target, self.default_root_target)
    
    def test_default_operation_with_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/myaccount/')
        mapper = PathInfoMapper(self.default_root_target, 'index')
        # Verifications:
        target = mapper.get_target(request)
        eq_(target.resource, '/myaccount')
        eq_(target.operation, 'index')
    
    def test_default_operation_without_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/myaccount')
        mapper = PathInfoMapper(self.default_root_target, 'index')
        # Verifications:
        target = mapper.get_target(request)
        eq_(target.resource, '/')
        eq_(target.operation, 'myaccount')
    
    def test_root_operation_with_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/view_members/')
        mapper = PathInfoMapper(self.default_root_target)
        # Verifications:
        target = mapper.get_target(request)
        eq_(target.resource, '/')
        eq_(target.operation, 'view_members')
    
    def test_root_operation_without_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/view_members')
        mapper = PathInfoMapper(self.default_root_target)
        # Verifications:
        target = mapper.get_target(request)
        eq_(target.resource, '/')
        eq_(target.operation, 'view_members')
    
    def test_2nd_level_operation(self):
        # Setup:
        request = make_request(PATH_INFO='/admin/accounts/delete')
        mapper = PathInfoMapper(self.default_root_target)
        # Verifications:
        target = mapper.get_target(request)
        eq_(target.resource, '/admin/accounts')
        eq_(target.operation, 'delete')


class TestRoutingArgsMapper(object):
    """
    Test case for the ``wsgiorg.routing_args`` mappers.
    
    """
    
    def make_request_with_routing_args(self, positional=(), named={}):
        request = make_request()
        request.environ['wsgiorg.routing_args'] = (positional, named)
        return request
    
    #{ Tests for the base mapper
    
    def test_constructor(self):
        m = RoutingArgsMapper(0, 1)
        eq_(0, m.resource_key)
        eq_(1, m.operation_key)
    
    def test_resource_formatter(self):
        m = RoutingArgsMapper(None, None)
        eq_(m.format_resource('something'), '/something')
    
    @raises(MappingError)
    def test_no_routing_args(self):
        m = RoutingArgsMapper(None, None)
        m.get_target(make_request())
    
    @raises(MappingError)
    def test_wrong_argument_key_in_mapper(self):
        class BadMapper(RoutingArgsMapper):
            arg_key = 4
        m = BadMapper(None, None)
        m.get_target(self.make_request_with_routing_args())
    
    #{ Tests for the positional and named mappers
    
    def test_non_existing_positional_key(self):
        # With a non-existing resource key:
        m1 = PositionalArgsMapper(2, 3)
        request1 = self.make_request_with_routing_args(('foo',))
        assert_raises(NoTargetFoundError, m1.get_target, request1)
        # With a non-existing operation key:
        m2 = PositionalArgsMapper(0, 3)
        request2 = self.make_request_with_routing_args(('foo', 'bar'))
        assert_raises(NoTargetFoundError, m2.get_target, request2)
    
    def test_non_existing_named_key(self):
        # With a non-existing resource key:
        m1 = NamedArgsMapper('resource', 'op')
        request1 = self.make_request_with_routing_args(named=dict(op='foo'))
        assert_raises(NoTargetFoundError, m1.get_target, request1)
        # With a non-existing operation key:
        m2 = NamedArgsMapper('resource', 'operation')
        request2 = self.make_request_with_routing_args(named=dict(resource='a'))
        assert_raises(NoTargetFoundError, m2.get_target, request2)
    
    def test_found_positional_keys(self):
        m = PositionalArgsMapper(1, 3)
        args = ('zero', 'myaccount/friends', 'two', 'add_friend', 'four')
        request = self.make_request_with_routing_args(args)
        target = m.get_target(request)
        eq_(target.resource, '/myaccount/friends')
        eq_(target.operation, 'add_friend')
    
    def test_found_named_keys(self):
        m = NamedArgsMapper('object', 'permission')
        args = dict(object='myaccount/friends', permission='add_friend')
        request = self.make_request_with_routing_args(named=args)
        target = m.get_target(request)
        eq_(target.resource, '/myaccount/friends')
        eq_(target.operation, 'add_friend')
    
    #{ Tests for the Routes mapper
    
    def test_routes_mapper_constructor(self):
        m = RoutesMapper()
        eq_(m.resource_key, 'controller')
        eq_(m.operation_key, 'action')
    
    def test_routes_found_target(self):
        m = RoutesMapper()
        args = dict(controller='myaccount.friends', action='add_friend')
        request = self.make_request_with_routing_args(named=args)
        target = m.get_target(request)
        eq_(target.resource, '/myaccount/friends')
        eq_(target.operation, 'add_friend')
    
    #}


#{ Mock definitions


class MockMapper(Mapper):
    """
    Mock mapper which will return the target described by the arguments passed
    to the constructor.
    
    If there's no mapper described, a :class:`NoTargetFoundError` exception
    will be raised.
    
    """
    
    def __init__(self, resource=None, operation=None):
        if resource and operation:
            self.target = Target(resource, operation)
        else:
            self.target = None
    
    def get_target(self, request):
        if self.target:
            return self.target
        raise NoTargetFoundError(request)


#}
