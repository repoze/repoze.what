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
Tests for :mod:`repoze.what.groups`.

"""

from nose.tools import assert_false, eq_, ok_
from webob import Request

from tests.base import MockGroupAdapter


class BaseGroupAdapterTestCase(object):
    """Base test case for group adapters."""
    
    def setup(self):
        self.request = Request.blank("/")
        self.request.environ['repoze.what.groups'] = {
            'membership': set(),
            'no_membership': set(),
            }
    
    def assert_cache(self, membership_groups, no_membership_groups):
        eq_(self.request.environ['repoze.what.groups']['membership'],
            set(membership_groups))
        eq_(self.request.environ['repoze.what.groups']['no_membership'],
            set(no_membership_groups))


class TestAnyGroup(BaseGroupAdapterTestCase):
    """
    Tests for the groups adapter, when the requester belongs to any of the
    groups in question.
    
    """
    
    def test_no_group_queried(self):
        adapter = MockGroupAdapter("admins")
        groups = set()
        
        assert_false(adapter.requester_in_any_group(self.request, groups))
        eq_(len(adapter.queried_groups), 0)
        self.assert_cache([], [])
    
    def test_no_group_matched(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["users", "designers"])
        
        assert_false(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", groups)])
        self.assert_cache([], ["users", "designers"])
    
    def test_group_superset_queried(self):
        adapter = MockGroupAdapter("admins")
        groups = set(["admins", "developers"])
        
        ok_(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", groups)])
        # We don't know for sure which of the required groups were matched,
        # so the cache cannot be updated:
        self.assert_cache([], [])
    
    def test_group_subset_queried(self):
        adapter = MockGroupAdapter("admins", "developers", "designers")
        groups = set(["admins", "designers"])
        
        ok_(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", groups)])
        # We don't know for sure which of the required groups were matched,
        # so the cache cannot be updated:
        self.assert_cache([], [])
    
    def test_exact_groups_queried(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["admins", "developers"])
        
        ok_(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", groups)])
        self.assert_cache([], [])
    
    def test_one_group_queried_and_matched(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["admins"])
        
        ok_(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", groups)])
        self.assert_cache(["admins"], [])
    
    def test_one_group_queried_but_not_matched(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["designers"])
        
        assert_false(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", groups)])
        self.assert_cache([], ["designers"])
    
    #{ Testing the cache
    
    def test_membership_in_cache(self):
        """
        If at least one of the queried groups is present in the membership
        cache, there's a match and no query is performed on the adapter.
        
        """
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["designers", "admins"])
        
        self.request.environ['repoze.what.groups']['membership'].add("users")
        self.request.environ['repoze.what.groups']['membership'].add("admins")
        
        ok_(adapter.requester_in_any_group(self.request, groups))
        eq_(len(adapter.queried_groups), 0)
        # The cache must have not been changed:
        self.assert_cache(["admins", "users"], [])
    
    def test_no_membership_in_cache(self):
        """
        If all of the queried groups are present in the no-membership
        cache, there's no match and no query is performed on the adapter.
        
        """
        adapter = MockGroupAdapter()
        groups = set(["users", "admins"])
        
        self.request.environ['repoze.what.groups']['no_membership'] |= groups
        
        assert_false(adapter.requester_in_any_group(self.request, groups))
        eq_(len(adapter.queried_groups), 0)
        # The cache must have not been changed:
        self.assert_cache([], ["admins", "users"])
    
    def test_insufficient_cache(self):
        """
        If the queried groups are present in the no-membership cache, except
        for one or more groups which aren't present in any cache, a query
        restricted to those non-cached groups is performed.
        
        """
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["users", "admins"])
        
        self.request.environ['repoze.what.groups']['no_membership'].add("users")
        
        ok_(adapter.requester_in_any_group(self.request, groups))
        eq_(adapter.queried_groups, [("any", set(["admins"]))])
        
        # The cache must've been updated to add "admins" to the membership
        # cache:
        self.assert_cache(["admins"], ["users"])
    
    #}


class TestAllGroups(BaseGroupAdapterTestCase):
    """
    Tests for the groups adapter, when the requester belongs to all of the
    groups in question.
    
    """
    
    def test_no_group_queried(self):
        adapter = MockGroupAdapter("admins")
        groups = set()
        
        assert_false(adapter.requester_in_all_groups(self.request, groups))
        eq_(len(adapter.queried_groups), 0)
        self.assert_cache([], [])
    
    def test_no_group_matched(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["users", "designers"])
        
        assert_false(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", groups)])
        self.assert_cache([], [])
    
    def test_group_superset_queried(self):
        adapter = MockGroupAdapter("admins")
        groups = set(["admins", "developers"])
        
        assert_false(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", groups)])
        self.assert_cache([], [])
    
    def test_group_subset_queried(self):
        adapter = MockGroupAdapter("admins", "developers", "designers")
        groups = set(["admins", "designers"])
        
        ok_(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", groups)])
        self.assert_cache(["admins", "designers"], [])
    
    def test_exact_groups_queried(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["admins", "developers"])
        
        ok_(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", groups)])
        self.assert_cache(["admins", "developers"], [])
    
    def test_one_group_queried_and_matched(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["admins"])
        
        ok_(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", groups)])
        self.assert_cache(["admins"], [])
    
    def test_one_group_queried_but_not_matched(self):
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["users"])
        
        assert_false(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", groups)])
        self.assert_cache([], ["users"])
    
    #{ Testing the cache
    
    def test_membership_in_cache(self):
        """
        If all of the queried groups is present in the membership cache, there's
        a match and no query is performed on the adapter.
        
        """
        adapter = MockGroupAdapter("admins", "users", "developers")
        groups = set(["users", "admins"])
        
        self.request.environ['repoze.what.groups']['membership'] |= groups
        
        ok_(adapter.requester_in_all_groups(self.request, groups))
        eq_(len(adapter.queried_groups), 0)
        # The cache must have not been changed:
        self.assert_cache(["admins", "users"], [])
    
    def test_no_membership_in_cache(self):
        """
        If at least one of the queried groups are present in the no-membership
        cache, there's no match and no query is performed on the adapter.
        
        """
        adapter = MockGroupAdapter()
        groups = set(["users", "admins"])
        
        self.request.environ['repoze.what.groups']['no_membership'].add("users")
        
        assert_false(adapter.requester_in_all_groups(self.request, groups))
        eq_(len(adapter.queried_groups), 0)
        # The cache must have not been changed:
        self.assert_cache([], ["users"])
    
    def test_insufficient_cache(self):
        """
        If the queried groups are present in the membership cache, except
        for one or more groups which aren't present in any cache, a query
        restricted to those non-cached groups is performed.
        
        """
        adapter = MockGroupAdapter("admins", "developers")
        groups = set(["users", "admins"])
        
        self.request.environ['repoze.what.groups']['membership'].add("users")
        
        ok_(adapter.requester_in_all_groups(self.request, groups))
        eq_(adapter.queried_groups, [("all", set(["admins"]))])
        
        # The cache must've been updated to add "admins" to the membership
        # cache:
        self.assert_cache(["admins", "users"], [])
    
    #}
