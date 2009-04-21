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

from unittest import TestCase

from repoze.what.acl.mappers.base import Mapper, CompoundMapper, Target, \
                                         NoTargetFoundError
from repoze.what.acl.mappers.pathinfo import PathInfoMapper

from unit_tests.base import make_request, FakeLogger


#{ The test suite


class TestMapper(TestCase):
    """
    Test case for the base :class:`Mapper`.
    
    """
    
    def test_get_target(self):
        """
        The ``.get_target()`` method must not be implemented by default.
        
        """
        m = Mapper()
        self.assertRaises(NotImplementedError, m.get_target, None)


class TestCompoundMapper(TestCase):
    """
    Test case for the Compound Mapper.
    
    """
    
    def test_with_zero_mappers(self):
        cm = CompoundMapper()
        self.assertEqual(0, len(cm.mappers))
        self.assertRaises(NoTargetFoundError, cm.get_target, make_request())
    
    def test_with_mappers_but_no_target(self):
        # Set up:
        m1 = MockMapper()
        m2 = MockMapper()
        m3 = MockMapper()
        cm = CompoundMapper(m1, m2, m3)
        # Verifications:
        self.assertEqual(3, len(cm.mappers))
        self.assertRaises(NoTargetFoundError, cm.get_target, make_request())
    
    def test_with_many_mappers_but_first_one_matches(self):
        # Set up:
        m1 = MockMapper('/admin/users', 'add')
        m2 = MockMapper()
        cm = CompoundMapper(m1, m2)
        # Verifications:
        self.assertEqual(2, len(cm.mappers))
        target = cm.get_target(make_request())
        self.assertEqual(target.resource, '/admin/users')
        self.assertEqual(target.operation, 'add')
    
    def test_with_many_mappers_but_last_one_matches(self):
        # Set up:
        m1 = MockMapper()
        m2 = MockMapper('/admin/users', 'add')
        cm = CompoundMapper(m1, m2)
        # Verifications:
        self.assertEqual(2, len(cm.mappers))
        target = cm.get_target(make_request())
        self.assertEqual(target.resource, '/admin/users')
        self.assertEqual(target.operation, 'add')
    
    def test_target_found_with_logger(self):
        # Setup:
        logger = FakeLogger()
        request = make_request(logger=logger)
        m = MockMapper('/blog/posts', 'edit')
        cm = CompoundMapper(m)
        cm.get_target(request)
        # Verifications:
        debug = logger.messages['debug']
        self.assertEqual(1, len(debug), debug)
        assert debug[0].startswith('Target aco:/blog/posts#edit found by '
                                    'mapper')
        assert 'MockMapper' in debug[0]


class TestTarget(TestCase):
    """
    Test case for the target ACO class.
    
    """
    
    def test_constructor(self):
        resource = '/myaccount'
        operation = 'logout'
        t = Target(resource, operation)
        self.assertEqual(resource, t.resource)
        self.assertEqual(operation, t.operation)
    
    def test_unicode(self):
        t = Target('/myaccount', 'logout')
        t_as_unicode = unicode(t)
        self.assertEqual(t_as_unicode, 'aco:/myaccount#logout')


class TestNoTargetFoundError(TestCase):
    """
    Test case for the :class:`NoTargetFoundError` exception.
    
    """
    
    def test_it(self):
        request = make_request(PATH_INFO='/myaccount')
        exc = unicode(NoTargetFoundError(request))
        assert exc.startswith('No target found for  /myaccount'), exc


class TestPathInfoMapper(TestCase):
    """
    Test case for the built-in PATH_INFO mapper.
    
    """
    
    default_root_target = Target('/my-account', 'login')
    
    def test_constructor_without_default_operation(self):
        mapper = PathInfoMapper(self.default_root_target)
        self.assertEqual(mapper.root_target, self.default_root_target)
        self.assertEqual(mapper.trailing_slash_operation, None)
    
    def test_constructor_with_default_operation(self):
        mapper = PathInfoMapper(self.default_root_target, 'index')
        self.assertEqual(mapper.root_target, self.default_root_target)
        self.assertEqual(mapper.trailing_slash_operation, 'index')
    
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
        self.assertEqual(target, self.default_root_target)
        # With a slash as the PATH_INFO:
        request = make_request(PATH_INFO='/')
        target = mapper.get_target(request)
        self.assertEqual(target, self.default_root_target)
        # With ten slashes as the PATH_INFO:
        request = make_request(PATH_INFO='/'*10)
        target = mapper.get_target(request)
        self.assertEqual(target, self.default_root_target)
    
    def test_default_operation_with_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/myaccount/')
        mapper = PathInfoMapper(self.default_root_target, 'index')
        # Verifications:
        target = mapper.get_target(request)
        self.assertEqual(target.resource, '/myaccount')
        self.assertEqual(target.operation, 'index')
    
    def test_default_operation_without_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/myaccount')
        mapper = PathInfoMapper(self.default_root_target, 'index')
        # Verifications:
        target = mapper.get_target(request)
        self.assertEqual(target.resource, '/')
        self.assertEqual(target.operation, 'myaccount')
    
    def test_root_operation_with_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/view_members/')
        mapper = PathInfoMapper(self.default_root_target)
        # Verifications:
        target = mapper.get_target(request)
        self.assertEqual(target.resource, '/')
        self.assertEqual(target.operation, 'view_members')
    
    def test_root_operation_without_trailing_slash(self):
        # Setup:
        request = make_request(PATH_INFO='/view_members')
        mapper = PathInfoMapper(self.default_root_target)
        # Verifications:
        target = mapper.get_target(request)
        self.assertEqual(target.resource, '/')
        self.assertEqual(target.operation, 'view_members')
    
    def test_2nd_level_operation(self):
        # Setup:
        request = make_request(PATH_INFO='/admin/accounts/delete')
        mapper = PathInfoMapper(self.default_root_target)
        # Verifications:
        target = mapper.get_target(request)
        self.assertEqual(target.resource, '/admin/accounts')
        self.assertEqual(target.operation, 'delete')


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
