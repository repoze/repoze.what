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
Test suite for the Access Control Objects.

"""

from nose.tools import eq_, assert_raises, raises

from repoze.what.exc import ExistingChildrenError, NoACOMatchError
from repoze.what.acl.aco import *
from repoze.what.acl.mappers.base import Target


class TestACO(object):
    """
    Tests for the base :class:`ACO`.
    
    """
    
    def test_constructor_with_valid_name(self):
        aco = ACO('admin')
        eq_(aco.name, 'admin')
    
    def test_constructor_with_invalid_names(self):
        assert_raises(ValueError, ACO, 'gnu/linux')
        assert_raises(ValueError, ACO, 'abc#xyz')
        assert_raises(ValueError, ACO, 'line1\nline2')
        assert_raises(ValueError, ACO, 'line1\rline2')
    
    def test_retrieving_ancestors(self):
        aco = ACO('admin')
        eq_(aco.get_ancestors(), ())
        eq_(aco.get_ancestors(True), (aco, ))


class TestResource(object):
    """
    Tests for :class:`Resource` ACOs.
    
    """
    
    def test_constructor_without_children(self):
        resource = Resource('blog')
        eq_(resource.name, 'blog')
        eq_(resource._parent, None)
        eq_(resource._resources, {})
        eq_(resource._operations, {})
    
    def test_constructor_with_subresources(self):
        subresource1 = Resource('posts')
        subresource2 = Resource('admin')
        root_resource = Resource('blog', subresource1, subresource2)
        # Checking the root ACO:
        eq_(root_resource.name, 'blog')
        eq_(root_resource._resources,
            {'posts': subresource1, 'admin': subresource2})
        eq_(root_resource._operations, {})
        # Checking its children:
        eq_(subresource1._parent, root_resource)
        eq_(subresource2._parent, root_resource)
    
    def test_constructor_with_operations(self):
        op1 = Operation('enable')
        op2 = Operation('disable')
        root_resource = Resource('blog', op1, op2)
        # Checking the root ACO:
        eq_(root_resource.name, 'blog')
        eq_(root_resource._resources, {})
        eq_(root_resource._operations, {'enable': op1, 'disable': op2})
        # Checking its children:
        eq_(op1._parent, root_resource)
        eq_(op2._parent, root_resource)
    
    def test_constructor_with_2_subresources_and_1_operation(self):
        subresource1 = Resource('posts')
        subresource2 = Resource('admin')
        op = Operation('disable')
        root_resource = Resource('blog', subresource1, op, subresource2)
        # Checking the root ACO:
        eq_(root_resource.name, 'blog')
        eq_(root_resource._resources,
            {'posts': subresource1, 'admin': subresource2})
        eq_(root_resource._operations, {'disable': op})
        # Checking its children:
        eq_(subresource1._parent, root_resource)
        eq_(subresource2._parent, root_resource)
        eq_(op._parent, root_resource)
    
    def test_constructor_with_1_operation_and_2_resources(self):
        op1 = Operation('enable')
        op2 = Operation('disable')
        subresource = Resource('posts')
        root_resource = Resource('blog', op1, subresource, op2)
        # Checking the root ACO:
        eq_(root_resource.name, 'blog')
        eq_(root_resource._resources, {'posts': subresource})
        eq_(root_resource._operations, {'enable': op1, 'disable': op2})
        # Checking its children:
        eq_(op1._parent, root_resource)
        eq_(op2._parent, root_resource)
        eq_(subresource._parent, root_resource)
    
    @raises(ExistingChildrenError)
    def test_constructor_with_existing_subresource(self):
        Resource(
            'blog',
            Resource('admin'),
            Resource('admin', Operation('index')),
        )
    
    @raises(ExistingChildrenError)
    def test_constructor_with_existing_operation(self):
        Resource(
            'blog',
            Operation('disable'),
            Operation('disable'),
        )
    
    def test_retrieving_ancestors(self):
        iii_child = Resource('users')
        ii_child = Resource('admin', iii_child)
        i_child = Resource('blog', ii_child)
        root_resource = Resource('website', i_child)
        # Testing it:
        acos = (root_resource, i_child, ii_child, iii_child)
        eq_(acos, iii_child.get_ancestors(include_myself=True))
        eq_(acos[:-1], iii_child.get_ancestors(include_myself=False))
    
    def test_adding_existing_subresource(self):
        subresource = Resource('admin')
        root_resource = Resource('blog', Resource('admin'))
        assert_raises(ExistingChildrenError, root_resource.add_subresource,
                      subresource)
    
    def test_adding_existing_operation(self):
        op = Operation('disable')
        root_resource = Resource('blog', Operation('disable'))
        assert_raises(ExistingChildrenError, root_resource.add_operation, op)
    
    def test_retrieving_existing_subresource(self):
        subresource1 = Resource('blog', Operation('index'))
        subresource2 = Resource('contact')
        root_resource = Resource('site', subresource1, subresource2)
        # Testing it:
        eq_(root_resource.get_subresource('blog'), subresource1)
        eq_(root_resource.get_subresource('contact'), subresource2)
    
    def test_retrieving_non_existing_subresource(self):
        subresource = Resource('contact')
        root_resource = Resource('site', subresource)
        # Testing it:
        assert_raises(NoACOMatchError, root_resource.get_subresource, 'forum')
    
    def test_retrieving_existing_operation(self):
        op1 = Operation('index')
        op2 = Operation('shutdown')
        root_resource = Resource('site', op1, op2)
        # Testing it:
        eq_(root_resource.get_operation('index'), op1)
        eq_(root_resource.get_operation('shutdown'), op2)
    
    def test_retrieving_non_existing_operation(self):
        op = Operation('contact')
        root_resource = Resource('site', op)
        # Testing it:
        assert_raises(NoACOMatchError, root_resource.get_operation, 'index')
    
    def test_loading_acos_from_existing_target(self):
        target = Target('/contact', 'send_email')
        op = Operation('send_email')
        contact_resource = Resource('contact', op)
        root_aco = Resource('site', contact_resource)
        # Testing it:
        loaded_acos = root_aco.load_acos(target)
        eq_(len(loaded_acos), 3)
        eq_(loaded_acos[0], root_aco)
        eq_(loaded_acos[1], contact_resource)
        eq_(loaded_acos[2], op)
    
    def test_loading_non_existing_resource(self):
        target = Target('/blog', 'send_email')
        op = Operation('send_email')
        contact_resource = Resource('contact', op)
        root_aco = Resource('site', contact_resource)
        # Testing it:
        assert_raises(NoACOMatchError, root_aco.load_acos, target)
    
    def test_loading_non_existing_operation(self):
        target = Target('/contact', 'send_email')
        op = Operation('display_form')
        contact_resource = Resource('contact', op)
        # Testing it:
        assert_raises(NoACOMatchError, contact_resource.load_acos, target)
    
    def test_unicode_representation(self):
        blog_admin = Resource('admin')
        blog = Resource('blog', blog_admin)
        forum = Resource('forum')
        site = Resource('site', blog, forum)
        # Testing it:
        eq_('aco:/blog/admin', unicode(blog_admin))
        eq_('aco:/blog', unicode(blog))
        eq_('aco:/forum', unicode(forum))
        eq_('aco:/', unicode(site))


class TestOperation(object):
    """
    Tests for :class:`Operation` ACOs.
    
    """
    
    def test_unicode_representation(self):
        add_post = Operation('add_post')
        blog = Resource('blog', add_post)
        shutdown = Operation('shutdown')
        site = Resource('site', blog, shutdown)
        # Testing it:
        eq_('aco:/blog#add_post', unicode(add_post))
        eq_('aco:/#shutdown', unicode(shutdown))

