# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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
Tests for the ACL implementation.

"""

from unittest import TestCase

from nose.tools import eq_, ok_, assert_false, assert_raises

from repoze.what.predicates import Predicate, is_user
from repoze.what.acl import (ACL, ACLCollection, AuthorizationDecision,
                             _BaseAuthorizationControl, _ACE, _MatchTracker,
                             _normalize_path)


#{ Tests for external stuff


class TestACL(TestCase):
    """
    Tests for the Access Control Lists.
    
    """
    
    def test_constructor_without_extra_args(self):
        acl = ACL()
        eq_(acl._base_path, "/")
        eq_(len(acl._aces), 0)
        eq_(acl._default_final_decision, None)
        eq_(acl._default_denial_handler, None)
    
    #{ Testing allows
    
    def test_allow_path_in_global_acl(self):
        predicate = TitletalePredicate()
        acl = ACL()
        acl.allow("/blog", predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/")
        ok_(is_path)
        eq_(denial_handler, None)
        ok_(ace.allow)
        eq_(ace.predicate, predicate)
        eq_(ace.propagate, True)
    
    def test_allow_object_in_global_acl(self):
        predicate = TitletalePredicate()
        protected_object = object()
        acl = ACL()
        acl.allow(protected_object, predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, protected_object)
        assert_false(is_path)
        eq_(denial_handler, None)
        ok_(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_allow_object_in_non_global_acl(self):
        predicate = TitletalePredicate()
        protected_object = object()
        acl = ACL("/blog")
        acl.allow(protected_object, predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, protected_object)
        assert_false(is_path)
        eq_(denial_handler, None)
        ok_(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_allow_path_in_non_global_acl(self):
        predicate = TitletalePredicate()
        acl = ACL("/blog")
        acl.allow("/view_comment", predicate, ("post_id", "comment_id"), 2)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/view_comment/")
        ok_(is_path)
        eq_(denial_handler, None)
        ok_(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_allow_without_predicate(self):
        acl = ACL()
        acl.allow("/blog")
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        ace = acl._aces[0][1]
        ok_(ace.allow)
        eq_(ace.predicate, None)
    
    def test_allow_with_custom_message(self):
        acl = ACL()
        acl.allow("/blog", reason="Everyone can access the blog")
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        ace = acl._aces[0][1]
        ok_(ace.allow)
        eq_(ace.reason, "Everyone can access the blog")
    
    def test_allow_without_propagation(self):
        acl = ACL()
        acl.allow("/blog", propagate=False)
        ace = acl._aces[0][1]
        assert_false(ace.propagate)
    
    def test_allow_with_multiple_acos(self):
        acl = ACL()
        acl.allow(("blog", "forum"))
        eq_(len(acl._aces), 2)
        # Testing the first one:
        eq_(acl._aces[0][0], "/blog/")
        ok_(acl._aces[0][1].allow)
        # Testing the second one:
        eq_(acl._aces[1][0], "/forum/")
        ok_(acl._aces[1][1].allow)
    
    #{ Testing denials
    
    def test_deny_path_in_global_acl(self):
        predicate = TitletalePredicate()
        acl = ACL()
        acl.deny("/blog", predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/")
        ok_(is_path)
        eq_(denial_handler, None)
        assert_false(ace.allow)
        eq_(ace.predicate, predicate)
        eq_(ace.propagate, True)
    
    def test_deny_object_in_global_acl(self):
        predicate = TitletalePredicate()
        protected_object = object()
        acl = ACL()
        acl.deny(protected_object, predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, protected_object)
        assert_false(is_path)
        eq_(denial_handler, None)
        assert_false(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_deny_path_in_non_global_acl(self):
        predicate = TitletalePredicate()
        acl = ACL("/blog")
        acl.deny("/post_new", predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/post_new/")
        ok_(is_path)
        eq_(denial_handler, None)
        assert_false(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_deny_object_in_non_global_acl(self):
        predicate = TitletalePredicate()
        protected_object = object()
        acl = ACL("/blog")
        acl.deny(protected_object, predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, protected_object)
        assert_false(is_path)
        eq_(denial_handler, None)
        assert_false(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_deny_path_in_global_acl_with_denial_handler(self):
        custom_denial_handler = object()
        predicate = TitletalePredicate()
        acl = ACL()
        acl.deny("/blog", predicate, denial_handler=custom_denial_handler)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/")
        ok_(is_path)
        eq_(denial_handler, custom_denial_handler)
        assert_false(ace.allow)
        eq_(ace.predicate, predicate)
    
    def test_deny_without_predicate(self):
        acl = ACL()
        acl.deny("/blog")
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        ace = acl._aces[0][1]
        assert_false(ace.allow)
        eq_(ace.predicate, None)
    
    def test_deny_with_custom_message(self):
        acl = ACL()
        acl.deny("/blog", reason="Noone can access the blog")
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        ace = acl._aces[0][1]
        assert_false(ace.allow)
        eq_(ace.reason, "Noone can access the blog")
    
    def test_deny_without_propagation(self):
        acl = ACL()
        acl.deny("/blog", propagate=False)
        ace = acl._aces[0][1]
        assert_false(ace.propagate)
    
    def test_deny_with_inclusion_forced(self):
        acl = ACL()
        acl.deny("/blog", force_inclusion=True)
        ace = acl._aces[0][1]
        ok_(ace.force_inclusion)
    
    def test_deny_with_multiple_acos(self):
        acl = ACL()
        acl.deny(("blog", "forum"))
        eq_(len(acl._aces), 2)
        # Testing the first one:
        eq_(acl._aces[0][0], "/blog/")
        assert_false(acl._aces[0][1].allow)
        # Testing the second one:
        eq_(acl._aces[1][0], "/forum/")
        assert_false(acl._aces[1][1].allow)
    
    #{ Testing decisions
    
    def test_authorization_with_indeterminate_predicate(self):
        """
        Authorization must always be granted if the predicate is indeterminate.
        
        """
        predicate = TitletalePredicate(None)
        acl = ACL()
        acl.deny("/blog", predicate)
        acl.allow("/contact", predicate)
        # Checking decisions:
        decision1 = acl.decide_authorization({'PATH_INFO': "/blog"}, None)
        decision2 = acl.decide_authorization({'PATH_INFO': "/contact"}, None)
        ok_(decision1.allow)
        ok_(decision1.was_indeterminate)
        ok_(decision2.allow)
        ok_(decision2.was_indeterminate)
    
    def test_authorization_with_less_specific_indeterminate_predicate(self):
        """
        The authorization decider must go on even if it already found an
        indeterminate predicate.
        
        """
        predicate = TitletalePredicate(None)
        acl = ACL()
        acl.allow("/blog", predicate)
        acl.deny("/blog/posts")
        decision = acl.decide_authorization({'PATH_INFO': "/blog/posts"}, None)
        assert_false(decision.allow)
        assert_false(decision.was_indeterminate)
    
    def test_authorization_with_no_matching_ace_and_no_default_decision(self):
        """
        No decision must be made if there's no ACE participating and there's
        no default decision.
        
        """
        predicate = TitletalePredicate()
        acl = ACL()
        acl.deny("/blog", predicate)
        acl.allow(object(), predicate)
        environ = {'PATH_INFO': "/trac"}
        protected_object = object()
        # Checking with just the path:
        eq_(acl.decide_authorization(environ), None)
        # Checking with the object as well:
        eq_(acl.decide_authorization(environ, protected_object), None)
        # The predicate must not have been evaluated:
        assert_false(predicate.evaluated)
    
    def test_authorization_with_matching_ace_but_predicate_not_met(self):
        """
        No decision must be made if the ACE covers the path/object, but the
        predicate is not met.
        
        """
        predicate1 = TitletalePredicate(False)
        predicate2 = TitletalePredicate(False)
        protected_object = object()
        acl = ACL()
        acl.deny("/blog", predicate1)
        acl.deny(protected_object, predicate2)
        environ = {'PATH_INFO': "/blog"}
        # Checking with just the path:
        eq_(acl.decide_authorization(environ), None)
        ok_(predicate1.evaluated)
        # Now with the object:
        eq_(acl.decide_authorization(environ, protected_object), None)
        ok_(predicate2.evaluated)
    
    def test_authorization_with_no_matching_ace_but_a_default_decision(self):
        """If there's no matching ACE, the default decision must be used."""
        acl1 = ACL(allow_by_default=True)
        acl2 = ACL(allow_by_default=False)
        environ = {'PATH_INFO': "/blog"}
        # Checking the first ACL:
        decision1 = acl1.decide_authorization(environ)
        ok_(decision1.allow)
        eq_(decision1.reason, None)
        eq_(decision1.denial_handler, None)
        eq_(decision1.match_tracker.longest_path_match, 0)
        assert_false(decision1.match_tracker.object_ace_found)
        # Checking the second ACL:
        decision2 = acl2.decide_authorization(environ)
        assert_false(decision2.allow)
        eq_(decision2.reason, None)
        eq_(decision2.denial_handler, None)
        eq_(decision2.match_tracker.longest_path_match, 0)
        assert_false(decision2.match_tracker.object_ace_found)
    
    def test_authorization_with_one_matching_ace(self):
        """If there's one matching ACE, it must be used."""
        predicate1 = TitletalePredicate()
        predicate2 = TitletalePredicate()
        protected_object = object()
        acl = ACL()
        acl.allow("/blog", predicate1)
        acl.deny(protected_object, predicate2, reason="Get out")
        # Checking with a path:
        environ1 = {'PATH_INFO': "/blog"}
        decision1 = acl.decide_authorization(environ1)
        ok_(decision1.allow)
        eq_(decision1.reason, None)
        eq_(decision1.denial_handler, None)
        eq_(decision1.match_tracker.longest_path_match, 6)
        assert_false(decision1.match_tracker.object_ace_found)
        # Checking with an object:
        environ2 = {'PATH_INFO': "/trac"}
        decision2 = acl.decide_authorization(environ2, protected_object)
        assert_false(decision2.allow)
        eq_(decision2.reason, "Get out")
        eq_(decision2.denial_handler, None)
        eq_(decision2.match_tracker.longest_path_match, 0)
        ok_(decision2.match_tracker.object_ace_found)
    
    def test_authorization_with_many_matching_aces(self):
        """
        If many ACEs match the request, the most specific one must be picked.
        
        """
        predicate1 = TitletalePredicate()
        predicate2 = TitletalePredicate()
        protected_object1 = object()
        protected_object2 = object()
        acl = ACL(allow_by_default=False)
        acl.allow("/blog", predicate1, reason="You're allowed")
        acl.deny("/blog/post_article", predicate1, reason="Get out")
        acl.deny("/blog/view_comment", predicate1, reason="Deny foo")
        acl.allow("/blog/view_comment", predicate1, reason="Allow foo")
        acl.allow(protected_object1, predicate1, reason="Gotcha")
        acl.allow(protected_object2, predicate1)
        acl.deny(protected_object2, predicate1, reason="Gotcha!")
        acl.deny("/dev", predicate2)
        # ----- No specific ACE, using the default decision:
        environ1 = {'PATH_INFO': "/yet-another/path"}
        decision1 = acl.decide_authorization(environ1)
        assert_false(decision1.allow)
        eq_(decision1.reason, None)
        eq_(decision1.denial_handler, None)
        eq_(decision1.match_tracker.longest_path_match, 0)
        assert_false(decision1.match_tracker.object_ace_found)
        # ----- One ACE covers the current path:
        environ2 = {'PATH_INFO': "/blog"}
        decision2 = acl.decide_authorization(environ2)
        ok_(decision2.allow)
        eq_(decision2.reason, "You're allowed")
        eq_(decision2.denial_handler, None)
        eq_(decision2.match_tracker.longest_path_match, 6)
        assert_false(decision2.match_tracker.object_ace_found)
        # ----- Two ACEs cover the current path; pick the most specific one:
        environ3 = {'PATH_INFO': "/blog/post_article"}
        decision3 = acl.decide_authorization(environ3)
        assert_false(decision3.allow)
        eq_(decision3.reason, "Get out")
        eq_(decision3.denial_handler, None)
        eq_(decision3.match_tracker.longest_path_match, 19)
        assert_false(decision3.match_tracker.object_ace_found)
        # ----- Three ACEs cover the current path and two of them cover the
        # ----- exact same path; pick the latest one:
        environ4 = {'PATH_INFO': "/blog/view_comment"}
        decision4 = acl.decide_authorization(environ4)
        ok_(decision4.allow)
        eq_(decision4.reason, "Allow foo")
        eq_(decision4.denial_handler, None)
        eq_(decision4.match_tracker.longest_path_match, 19)
        assert_false(decision4.match_tracker.object_ace_found)
        # ----- One ACE covers the object itself:
        environ5 = {'PATH_INFO': "/"}
        decision5 = acl.decide_authorization(environ5, protected_object1)
        ok_(decision5.allow)
        eq_(decision5.reason, "Gotcha")
        eq_(decision5.denial_handler, None)
        eq_(decision5.match_tracker.longest_path_match, 0)
        ok_(decision5.match_tracker.object_ace_found)
        # ----- Two ACEs cover the request, but one of them cover covers the
        # ----- object so it must picked:
        environ6 = {'PATH_INFO': "/blog/post_article"}
        decision6 = acl.decide_authorization(environ6, protected_object1)
        ok_(decision6.allow)
        eq_(decision6.reason, "Gotcha")
        eq_(decision6.denial_handler, None)
        eq_(decision6.match_tracker.longest_path_match, 19)
        ok_(decision6.match_tracker.object_ace_found)
        # ----- Two ACEs cover the object itself; pick the latest one:
        environ7 = {'PATH_INFO': "/"}
        decision7 = acl.decide_authorization(environ7, protected_object2)
        assert_false(decision7.allow)
        eq_(decision7.reason, "Gotcha!")
        eq_(decision7.denial_handler, None)
        eq_(decision7.match_tracker.longest_path_match, 0)
        ok_(decision7.match_tracker.object_ace_found)
        # ----- ACE covering paths must be ignored if there's already a match
        # ----- for the object itself:
        environ8 = {'PATH_INFO': "/"}
        decision8 = acl.decide_authorization(environ8, protected_object1)
        ok_(decision8.allow)
        eq_(decision8.reason, "Gotcha")
        eq_(decision8.denial_handler, None)
        eq_(decision8.match_tracker.longest_path_match, 0)
        ok_(decision8.match_tracker.object_ace_found)
        assert_false(predicate2.evaluated)
    
    def test_authorization_denied_with_default_handler(self):
        """
        The default denial handler must be used when available and no custom
        denial is set.
        
        """
        predicate = TitletalePredicate()
        denial_handler = object()
        acl = ACL(default_denial_handler=denial_handler)
        acl.deny("/", predicate)
        environ = {'PATH_INFO': "/",}
        decision = acl.decide_authorization(environ)
        assert_false(decision.allow)
        eq_(decision.denial_handler, denial_handler)
        # If a custom one is set, the default one must not be used:
        custom_handler = object()
        acl.deny("/", predicate, denial_handler=custom_handler)
        decision = acl.decide_authorization(environ)
        assert_false(decision.allow)
        eq_(decision.denial_handler, custom_handler)
    
    def test_authorization_denied_with_custom_handler(self):
        """Custom denial handlers must be used when available."""
        predicate = TitletalePredicate()
        denial_handler = object()
        acl = ACL()
        acl.deny("/", predicate, denial_handler=denial_handler)
        environ = {'PATH_INFO': "/"}
        decision = acl.decide_authorization(environ)
        assert_false(decision.allow)
        eq_(decision.denial_handler, denial_handler)
    
    def test_authorization_without_predicates(self):
        """ACEs which don't have predicates must always be taken into account"""
        acl = ACL()
        acl.allow("/blog")
        acl.deny("/blog/post-new", TitletalePredicate(), reason="Get out")
        acl.deny("/blog/repository")
        acl.allow("/blog/repository/download")
        # ----- Checking just one ACE without predicate:
        environ1 = {'PATH_INFO': "/blog/"}
        decision1 = acl.decide_authorization(environ1)
        ok_(decision1.allow)
        # ----- Checking two ACEs without predicates:
        environ2 = {'PATH_INFO': "/blog/repository"}
        decision2 = acl.decide_authorization(environ2)
        assert_false(decision2.allow)
        # ----- Checking three ACEs without predicates:
        environ3 = {'PATH_INFO': "/blog/repository/download"}
        decision3 = acl.decide_authorization(environ3)
        ok_(decision3.allow)
        # ----- Checking an ACE without predicate, overridden with one which
        # ----- does have a predicate:
        environ4 = {'PATH_INFO': "/blog/post-new"}
        decision4 = acl.decide_authorization(environ4)
        assert_false(decision4.allow)
        eq_(decision4.reason, "Get out")
    
    def test_authorization_with_custom_messages(self):
        acl = ACL("/blog", allow_by_default=True)
        acl.deny("/add-user", reason="Noone can add users")
        acl.allow("/add-user/tomorrow",
                  reason="Everybody can add users tomorrow")
        acl.deny("/add-post", TitletalePredicate(),
                 reason="Noone can add posts")
        acl.allow("/add-post/tomorrow", TitletalePredicate(),
                  reason="Everybody can add posts tomorrow")
        # Checking the message the authz is denied without a predicate:
        environ1 = {'PATH_INFO': "/blog/add-user"}
        decision1 = acl.decide_authorization(environ1)
        assert_false(decision1.allow)
        eq_(decision1.reason, "Noone can add users")
        # Checking the message the authz is denied with a predicate:
        environ2 = {'PATH_INFO': "/blog/add-post"}
        decision2 = acl.decide_authorization(environ2)
        assert_false(decision2.allow)
        eq_(decision2.reason, "Noone can add posts")
        # Checking the message the authz is granted without a predicate:
        environ3 = {'PATH_INFO': "/blog/add-user/tomorrow"}
        decision3 = acl.decide_authorization(environ3)
        ok_(decision3.allow)
        eq_(decision3.reason, "Everybody can add users tomorrow")
        # Checking the message the authz is granted with a predicate:
        environ4 = {'PATH_INFO': "/blog/add-post/tomorrow",}
        decision4 = acl.decide_authorization(environ4)
        ok_(decision4.allow)
        eq_(decision4.reason, "Everybody can add posts tomorrow")
    
    def test_authorization_without_propagation_nor_predicate(self):
        """ACEs must not be propagated when explicitly requested."""
        acl = ACL()
        acl.allow("/blog/", propagate=False)
        environ = {'PATH_INFO': "/blog/posts",}
        decision = acl.decide_authorization(environ)
        eq_(decision, None)
    
    def test_authorization_with_predicate_and_no_propagation(self):
        """
        ACEs must not be propagated when explicitly requested and predicates
        must have not been evaluated.
        
        """
        acl = ACL()
        predicate = TitletalePredicate(True)
        acl.allow("/blog/", predicate=predicate, propagate=False)
        environ = {'PATH_INFO': "/blog/posts",}
        decision = acl.decide_authorization(environ)
        eq_(decision, None)
        assert_false(predicate.evaluated)
    
    def test_authorization_with_inclusion_forced_but_no_predicate(self):
        """ACEs must be enforced when explicitly requested."""
        acl = ACL()
        acl.deny("/blog/", force_inclusion=True)
        acl.allow("/blog/posts")
        environ = {'PATH_INFO': "/blog/posts",}
        decision = acl.decide_authorization(environ)
        assert_false(decision.allow, False)
    
    def test_authorization_with_predicate_and_inclusion_forced(self):
        """
        ACEs must be forced when explicitly requested and their predicates
        are met.
        
        """
        acl = ACL()
        acl.deny("/blog/", TitletalePredicate(True), force_inclusion=True)
        acl.allow("/blog/posts/")
        acl.deny("/forum/", TitletalePredicate(False), force_inclusion=True)
        acl.allow("/forum/posts/")
        
        # Authorization must be denied if the predicate of a forced ACE is met:
        environ1 = {'PATH_INFO': "/blog/posts/",}
        decision1 = acl.decide_authorization(environ1)
        eq_(decision1.allow, False)
        
        # Authorization must be granted if the predicate of a forced ACE is not
        # met:
        environ2 = {'PATH_INFO': "/forum/posts/",}
        decision2 = acl.decide_authorization(environ2)
        eq_(decision2.allow, True)
    
    def test_authorization_with_ace_with_trailing_slash(self):
        """ACEs with a trailing slash should match requests without it."""
        acl = ACL()
        acl.allow("/path/", propagate=False)
        environ = {'PATH_INFO': "/path",}
        decision = acl.decide_authorization(environ)
        ok_(decision.allow)
    
    def test_authorization_with_ace_without_trailing_slash(self):
        """ACEs without a trailing slash should match requests with it."""
        acl = ACL()
        acl.allow("/path", propagate=False)
        environ = {'PATH_INFO': "/path/",}
        decision = acl.decide_authorization(environ)
        ok_(decision.allow)
    
    def test_authorization_with_propagation_and_no_trailing_slash(self):
        """
        ACEs without a trailing slash should not match sibling paths.
        
        This is, paths under the same parent directory.
        
        """
        acl = ACL()
        acl.allow("/path", propagate=True)
        environ = {'PATH_INFO': "/path-brother",}
        decision = acl.decide_authorization(environ)
        eq_(decision, None)
    
    def test_authorization_without_leading_slashes_in_paths(self):
        """Missing leading slashes in the paths must not affect authorization"""
        acl = ACL()
        # ACEs without leading slashes must match right paths:
        acl.allow("foo/")
        environ_with_right_path = {'PATH_INFO': "/foo",}
        decision1 = acl.decide_authorization(environ_with_right_path)
        ok_(decision1.allow)
        # Right ACEs must match paths without leading slashes, although this
        # doesn't seem to make sense:
        acl.allow("/bar/")
        environ_with_wrong_path = {'PATH_INFO': "bar/",}
        decision2 = acl.decide_authorization(environ_with_wrong_path)
        ok_(decision2.allow)
    
    def test_authorization_with_multiple_continuous_slashes_in_paths(self):
        """Multiple continuous slashes in the paths must make no difference."""
        acl = ACL()
        # Checking an ACE with multiple continuous slashes:
        acl.allow("/foo/////bar/")
        environ_with_right_path = {'PATH_INFO': "/foo/bar/",}
        decision1 = acl.decide_authorization(environ_with_right_path)
        ok_(decision1.allow)
        # Checking an PATH_INFO with multiple continuous slashes:
        acl.allow("/bar/foo/")
        environ_with_wrong_path = {'PATH_INFO': "/bar/////foo/",}
        decision2 = acl.decide_authorization(environ_with_wrong_path)
        ok_(decision2.allow)
    
    #}
    
    def test_representation(self):
        acl = ACL()
        acl.allow("foo")
        acl.deny("bar")
        eq_("<ACL base=/ aces=2 at %s>" % hex(id(acl)), repr(acl))


class TestACLCollections(TestCase):
    """
    Tests for the collections of Access Control Lists.
    
    """
    
    def test_constructor_without_extra_args(self):
        acl = ACLCollection()
        eq_(len(acl._acls), 0)
        eq_(acl._default_final_decision, None)
        eq_(acl._default_denial_handler, None)
    
    def test_constructor_with_initial_acls(self):
        acl1 = ACL()
        acl2 = ACL()
        acl3 = ACL()
        collection = ACLCollection(None, None, acl1, acl2, acl3)
        eq_(len(collection._acls), 3)
        ok_(acl1 in collection._acls)
        ok_(acl2 in collection._acls)
        ok_(acl3 in collection._acls)
    
    def test_acls_are_added(self):
        acl1 = ACL()
        acl2 = ACL()
        acl3 = ACL()
        collection = ACLCollection()
        collection.add_acl(acl1)
        collection.add_acl(acl2)
        collection.add_acl(acl3)
        eq_(len(collection._acls), 3)
        ok_(acl1 in collection._acls)
        ok_(acl2 in collection._acls)
        ok_(acl3 in collection._acls)
    
    #{ Testing decisions
    
    def test_authorization_with_indeterminate_predicate(self):
        """
        Authorization must always be granted if the predicate is indeterminate.
        
        """
        predicate = TitletalePredicate(None)
        acl = ACL()
        acl.deny("/blog", predicate)
        collection = ACLCollection()
        collection.add_acl(acl)
        # Checking decisions:
        decision = collection.decide_authorization({'PATH_INFO': "/blog"}, None)
        ok_(decision.allow)
        ok_(decision.was_indeterminate)
    
    def test_authorization_with_out_of_scope_acls(self):
        """
        No decision must be made if the request is not within the scope of any
        ACL.
        
        """
        acl1 = ACL("/trac")
        acl2 = ACL("/blog")
        acl3 = ACL("/whatever")
        acl3.allow("", TitletalePredicate(False))
        collection = ACLCollection()
        collection.add_acl(acl1)
        collection.add_acl(acl2)
        collection.add_acl(acl3)
        environ = {'PATH_INFO': "/whatever",}
        protected_object = object()
        # Checking with just the path:
        eq_(collection.decide_authorization(environ), None)
        # Checking with the object as well:
        eq_(collection.decide_authorization(environ, protected_object), None)
    
    def test_authorization_with_one_matching_acl(self):
        """
        If there's just one ACL participating, it must be used.
        
        """
        acl1 = ACL("/trac")
        acl1.deny("/wiki", TitletalePredicate(), reason="Not allowed")
        acl2 = ACL("/blog")
        acl3 = ACL("/foo", allow_by_default=False)
        collection = ACLCollection()
        collection.add_acl(acl1)
        collection.add_acl(acl2)
        collection.add_acl(acl3)
        # ----- If there's an ACE, it must be used:
        environ1 = {'PATH_INFO': "/trac/wiki/StartPage",}
        decision1 = collection.decide_authorization(environ1)
        assert_false(decision1.allow)
        eq_(decision1.reason, "Not allowed")
        eq_(decision1.match_tracker.longest_path_match, 11)
        # ----- If there's a default decision, use it:
        environ2 = {'PATH_INFO': "/foo/bar",}
        decision2 = collection.decide_authorization(environ2)
        assert_false(decision2.allow)
        eq_(decision2.reason, None)
        eq_(decision2.match_tracker.longest_path_match, 0)
        
    def test_authorization_with_many_acls_participating(self):
        """If many ACLs are participating, pick the latest one."""
        acl1 = ACL("/admin", allow_by_default=False)
        acl2 = ACL("/admin/blog")
        acl2.allow("/post", TitletalePredicate())
        acl3 = ACL("/admin/blog/post")
        acl3.deny("", TitletalePredicate(), reason="This is something custom")
        collection = ACLCollection()
        collection.add_acl(acl1)
        collection.add_acl(acl2)
        collection.add_acl(acl3)
        environ = {'PATH_INFO': "/admin/blog/post",}
        decision = collection.decide_authorization(environ)
        assert_false(decision.allow)
        eq_(decision.reason, "This is something custom")
        eq_(decision.match_tracker.longest_path_match, 17)
    
    def test_authorization_with_acl_with_trailing_slash(self):
        """
        ACLs covering a path with a trailing slash must cover requests without
        it.
        
        """
        acl = ACL("/path/", allow_by_default=True)
        collection = ACLCollection()
        collection.add_acl(acl)
        environ = {'PATH_INFO': "/path",}
        decision = collection.decide_authorization(environ)
        ok_(decision.allow)
    
    def test_authorization_with_acl_without_trailing_slash(self):
        """
        ACLs covering a path without a trailing slash must cover requests with
        it.
        
        """
        acl = ACL("/path", allow_by_default=True)
        collection = ACLCollection()
        collection.add_acl(acl)
        environ = {'PATH_INFO': "/path/",}
        decision = collection.decide_authorization(environ)
        ok_(decision.allow)
    
    def test_authorization_with_acl_forcing_ace(self):
        """
        ACEs cannot override enforced ACEs from previous ACLs.
        
        """
        first_acl = ACL()
        first_acl.deny("/blog", force_inclusion=True)
        second_acl = ACL()
        second_acl.allow("/blog/posts")
        collection = ACLCollection()
        collection.add_acl(first_acl)
        collection.add_acl(second_acl)
        
        environ = {'PATH_INFO': "/blog/posts",}
        decision = collection.decide_authorization(environ)
        assert_false(decision.allow)
    
    #}
    
    def test_representation(self):
        collection = ACLCollection(allow_by_default=False)
        collection.add_acl(ACL())
        collection.add_acl(ACL())
        collection.add_acl(ACL())
        eq_("<ACL-Collection acls=3 at %s>" % hex(id(collection)),
            repr(collection))


class TestAuthorizationDecision(TestCase):
    """
    Unit tests for AuthorizationDecision objects.
    
    """
    
    #{ Testing the constructor
    
    def test_authz_granted(self):
        denial_handler = object()
        decision = AuthorizationDecision(True, "FooBar", denial_handler)
        ok_(decision.allow)
        assert_false(decision.was_indeterminate)
        eq_(decision.reason, "FooBar")
        eq_(decision.denial_handler, denial_handler)
        eq_(decision.match_tracker, None)
    
    def test_authz_denied(self):
        denial_handler = object()
        decision = AuthorizationDecision(False, "FooBar", denial_handler)
        eq_(decision.allow, False)
        assert_false(decision.was_indeterminate)
        eq_(decision.reason, "FooBar")
        eq_(decision.denial_handler, denial_handler)
        eq_(decision.match_tracker, None)
    
    def test_indetermination(self):
        decision = AuthorizationDecision(None, "FooBar", None)
        ok_(decision.allow)
        ok_(decision.was_indeterminate)
    
    #}
    
    def test_setting_denial_handler_with_existing_one(self):
        """If there's already a denial handler, it must not be replaced."""
        denial_handler = object()
        decision = AuthorizationDecision(False, "FooBar", denial_handler)
        decision.set_denial_handler("something new")
        eq_(decision.denial_handler, denial_handler)
    
    def test_setting_denial_handler_with_no_existing_one(self):
        """If there's no previous a denial handler, it must set."""
        denial_handler = object()
        decision = AuthorizationDecision(False, "FooBar", None)
        decision.set_denial_handler(denial_handler)
        eq_(decision.denial_handler, denial_handler)
    
    def test_setting_match_tracker(self):
        decision = AuthorizationDecision(False, "FooBar", None)
        match_tracker = object()
        decision.set_match_tracker(match_tracker)
        eq_(decision.match_tracker, match_tracker)


#{ Unit tests for internal stuff


class TestBaseAuthorizationControl(TestCase):
    """Tests for the base class _BaseAuthorizationControl."""
    
    def test_constructor_with_default_final_decision(self):
        control = _BaseAuthorizationControl(True)
        ok_(isinstance(control._default_final_decision, AuthorizationDecision))
        eq_(control._default_final_decision.allow, True)
    
    def test_constructor_with_default_denial_handler(self):
        denial_handler = object()
        control = _BaseAuthorizationControl(default_denial_handler=denial_handler)
        eq_(control._default_denial_handler, denial_handler)
    
    def test_constructor_with_default_denial_handler_and_final_decision(self):
        denial_handler = object()
        control = _BaseAuthorizationControl(False, denial_handler)
        ok_(isinstance(control._default_final_decision, AuthorizationDecision))
        eq_(control._default_final_decision.allow, False)
        eq_(control._default_denial_handler, denial_handler)
    
    def test_no_authorization_decision_by_default(self):
        control = _BaseAuthorizationControl()
        assert_raises(NotImplementedError, control.decide_authorization, {})


class TestAces(TestCase):
    """
    Tests for the ACEs.
    
    """
    
    def test_constructor(self):
        predicate = is_user("foo")
        # Allow ACE:
        ace1 = _ACE(predicate, True)
        eq_(ace1.predicate, predicate)
        eq_(ace1.allow, True)
        eq_(ace1.propagate, True)
        eq_(ace1.force_inclusion, False)
        # Denial ACE:
        ace2 = _ACE(predicate, False)
        eq_(ace2.predicate, predicate)
        eq_(ace2.allow, False)
        eq_(ace2.propagate, True)
        eq_(ace2.force_inclusion, False)
    
    def test_representation(self):
        predicate = is_user("foo")
        ace1 = _ACE(predicate, True, "No reason")
        ace2 = _ACE(predicate, False, "No reason")
        eq_("<ACE allow=True predicate=%r reason='No reason'>" % predicate,
            repr(ace1))
        eq_("<ACE allow=False predicate=%r reason='No reason'>" % predicate,
            repr(ace2))
    
    def test_denial_ace_without_predicate(self):
        ace = _ACE(None, False)
        eq_(ace.predicate, None)
        participation = ace.can_participate({})
        ok_(participation)
    
    def test_predicate_met_and_authz_denied(self):
        """
        The ACE must participate if the predicate is met and authz is denied.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        # Set:
        ace = _ACE(predicate, False)
        # Go!:
        participation = ace.can_participate({})
        eq_(participation, True)
        ok_(predicate.evaluated)
    
    def test_predicate_met_and_authz_granted(self):
        """
        The ACE must participate if the predicate is met and authz is granted.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        # Set:
        ace = _ACE(predicate, True)
        # Go!:
        participation = ace.can_participate({})
        eq_(participation, True)
        ok_(predicate.evaluated)
    
    def test_predicate_unmet_and_authz_denied(self):
        """
        The ACE must not participate if the predicate isn't met and authz is
        denied.
        
        """
        # Ready:
        predicate = TitletalePredicate(False)
        # Set:
        ace = _ACE(predicate, False)
        # Go!:
        participation = ace.can_participate({})
        eq_(participation, False)
        ok_(predicate.evaluated)
    
    def test_predicate_unmet_and_authz_granted(self):
        """
        The ACE must not participate if the predicate isn't met and authz is
        granted
        
        """
        # Ready:
        predicate = TitletalePredicate(False)
        # Set:
        ace = _ACE(predicate, True)
        # Go!:
        participation = ace.can_participate({})
        eq_(participation, False)
        ok_(predicate.evaluated)


class TestMatchTracker(TestCase):
    """Tests for the internal _MatchTracker."""
    
    def test_constructor(self):
        tracker = _MatchTracker()
        eq_(tracker.longest_path_match, 0)
        eq_(tracker.object_ace_found, False)
        eq_(tracker.forced_ace_found, False)
    
    def test_scope_check_with_wrong_path(self):
        """
        A request is out of the scope of a protected path if the PATH_INFO
        doesn't start with that protected path.
        
        """
        tracker = _MatchTracker()
        assert_false(tracker.is_within_scope("/admin", True, False, "/blog/"))
    
    def test_scope_check_with_less_specific_path(self):
        """
        A request is out of the scope of a protected path if we already found
        an ACL/ACE more specific to such a request.
        
        """
        tracker = _MatchTracker()
        tracker.longest_path_match = 3
        assert_false(tracker.is_within_scope("/", True, False, "/blog"))
    
    def test_scope_check_with_object_protection_found(self):
        """
        A request is out of the scope of a protected path if we already found 
        an ACL/ACE for the object in the request itself.
        
        """
        tracker = _MatchTracker()
        tracker.object_ace_found = True
        assert_false(tracker.is_within_scope("/", True, False, "/blog/"))
    
    def test_scope_check_with_right_path(self):
        """
        A request is within the scope of a protected path if that path is the
        most specific one so far.
        
        """
        tracker = _MatchTracker()
        ok_(tracker.is_within_scope("/blog", True, False, "/blog/add_post"))
    
    def test_scope_check_with_equally_specific_path(self):
        """
        A request is within the scope of a protected path if that path is the
        as specific to the request as another one already found.
        
        """
        tracker = _MatchTracker()
        tracker.longest_path_match = 1
        ok_(tracker.is_within_scope("/", True, False, "/blog"))
    
    def test_scope_check_with_parent_path_but_no_propagation(self):
        """
        A request is not within the scope of a parent path if the later is not
        propagated.
        
        """
        tracker = _MatchTracker()
        assert_false(tracker.is_within_scope("/blog", False, False,
                                             "/blog/add_post"))
    
    def test_scope_check_with_inclusion_forced_but_not_propagated(self):
        """
        A request is within scope if the parent path's inclusion is forced,
        even if it's not propagated.
        
        """
        tracker = _MatchTracker()
        ok_(tracker.is_within_scope("/", False, True, "/blog/"))
    
    def test_scope_check_with_propagation_and_inclusion_forced(self):
        """
        A request is within scope if the parent path is both propagated and
        its inclusion is forced.
        
        """
        tracker = _MatchTracker()
        ok_(tracker.is_within_scope("/", True, True, "/blog/"))
    
    def test_scope_check_with_inclusion_really_forced(self):
        """
        A request is within scope if the parent path's inclusion is forced,
        no matter if it already found an ACE for the object or it's not the
        most specific match so far.
        
        """
        # With an object ACE found:
        tracker_with_object = _MatchTracker()
        tracker_with_object.object_ace_found = True
        ok_(tracker_with_object.is_within_scope("/", True, True, "/blog/"))
        # With a more specific path found:
        tracker_with_path = _MatchTracker()
        tracker_with_path.longest_path_match = 5
        ok_(tracker_with_path.is_within_scope("/", True, True, "/blog/"))
    
    def test_scope_check_with_inclusion_but_inclusion_already_forced(self):
        """
        A request must not be within the scope of a forced ACE if another ACE
        was already enforced.
        
        """
        tracker = _MatchTracker()
        tracker.forced_ace_found = True
        assert_false(tracker.is_within_scope("/", True, True, "/blog/"))
    
    def test_setting_longest_path(self):
        tracker = _MatchTracker()
        tracker.set_longest_path("/hi/there")
        eq_(tracker.longest_path_match, 9)
        tracker.set_longest_path("/hi")
        eq_(tracker.longest_path_match, 3)


class TestNormalizingPath(object):
    """Tests for :func:`_normalize_path`."""
    
    def test_empty_string(self):
        path_normalized = _normalize_path("")
        eq_(path_normalized, "/")
    
    def test_slash(self):
        path_normalized = _normalize_path("/")
        eq_(path_normalized, "/")
    
    def test_no_leading_slash(self):
        path_normalized = _normalize_path("path/")
        eq_(path_normalized, "/path/")
    
    def test_no_trailing_slash(self):
        path_normalized = _normalize_path("/path")
        eq_(path_normalized, "/path/")
    
    def test_trailing_and_leading_slashes(self):
        path_normalized = _normalize_path("/path/")
        eq_(path_normalized, "/path/")
    
    def test_multiple_leading_slashes(self):
        path_normalized = _normalize_path("////path/")
        eq_(path_normalized, "/path/")
    
    def test_multiple_trailing_slashes(self):
        path_normalized = _normalize_path("/path////")
        eq_(path_normalized, "/path/")
    
    def test_multiple_inner_slashes(self):
        path_normalized = _normalize_path("/path////here/")
        eq_(path_normalized, "/path/here/")
    
    def test_unicode_path(self):
        path_normalized = _normalize_path(u"mañana/aquí")
        eq_(path_normalized, u"/mañana/aquí/")


#{ Mock objects


class TitletalePredicate(Predicate):
    """Mock predicate to check when a predicate is evaluated."""
    
    def __init__(self, evaluation_result=True, *args, **kwargs):
        self.evaluation_result = evaluation_result
        self.evaluated = False
        super(TitletalePredicate, self).__init__(*args, **kwargs)
    
    def check(self, request, credentials):
        self.evaluated = True
        return self.evaluation_result


#}
