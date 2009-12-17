# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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
Tests for the ACL implementation.

"""

from unittest import TestCase

from nose.tools import eq_, ok_, assert_false, assert_raises

from repoze.what.predicates import Predicate, is_user
from repoze.what.acl import (ACL, ACLCollection, AuthorizationDecision,
                             _BaseAuthorizationControl, _ACE, _MatchTracker,
                             _normalize_path)
from repoze.what.predicates import NotAuthorizedError


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
    
    def test_allow_path_in_global_acl_without_arguments(self):
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
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
        eq_(ace.propagate, True)
    
    def test_allow_object_in_global_acl_without_arguments(self):
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
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_allow_path_in_global_acl_with_arguments(self):
        predicate = TitletalePredicate()
        acl = ACL()
        acl.allow("/blog", predicate, ("post_id", "comment_id"), 2)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/")
        ok_(is_path)
        eq_(denial_handler, None)
        ok_(ace.allow)
        eq_(ace.predicate, predicate)
        eq_(ace.named_args, set(["post_id", "comment_id"]))
        eq_(ace.positional_args, 2)
    
    def test_allow_path_in_non_global_acl_without_arguments(self):
        predicate = TitletalePredicate()
        acl = ACL("/blog")
        acl.allow("/post_new", predicate)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/post_new/")
        ok_(is_path)
        eq_(denial_handler, None)
        ok_(ace.allow)
        eq_(ace.predicate, predicate)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_allow_object_in_non_global_acl_without_arguments(self):
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
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_allow_path_in_non_global_acl_with_arguments(self):
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
        eq_(ace.named_args, set(["post_id", "comment_id"]))
        eq_(ace.positional_args, 2)
    
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
        acl.allow("/blog", msg="Everyone can access the blog")
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        ace = acl._aces[0][1]
        ok_(ace.allow)
        eq_(ace.message, "Everyone can access the blog")
    
    def test_allow_without_propagation(self):
        acl = ACL()
        acl.allow("/blog", propagate=False)
        ace = acl._aces[0][1]
        assert_false(ace.propagate)
    
    #{ Testing denials
    
    def test_deny_path_in_global_acl_without_arguments(self):
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
        eq_(ace.predicate.predicate, predicate)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
        eq_(ace.propagate, True)
    
    def test_deny_object_in_global_acl_without_arguments(self):
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
        eq_(ace.predicate.predicate, predicate)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_deny_path_in_global_acl_with_arguments(self):
        predicate = TitletalePredicate()
        acl = ACL()
        acl.deny("/blog", predicate, ("post_id", "comment_id"), 2)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/")
        ok_(is_path)
        eq_(denial_handler, None)
        assert_false(ace.allow)
        eq_(ace.predicate.predicate, predicate)
        eq_(ace.named_args, set(["post_id", "comment_id"]))
        eq_(ace.positional_args, 2)
    
    def test_deny_path_in_non_global_acl_without_arguments(self):
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
        eq_(ace.predicate.predicate, predicate)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_deny_object_in_non_global_acl_without_arguments(self):
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
        eq_(ace.predicate.predicate, predicate)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_deny_path_in_non_global_acl_with_arguments(self):
        predicate = TitletalePredicate()
        acl = ACL("/blog")
        acl.deny("/view_comment", predicate, ("post_id", "comment_id"), 2)
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        eq_(len(acl._aces[0]), 4)
        (path_or_object, ace, is_path, denial_handler) = acl._aces[0]
        eq_(path_or_object, "/blog/view_comment/")
        ok_(is_path)
        eq_(denial_handler, None)
        assert_false(ace.allow)
        eq_(ace.predicate.predicate, predicate)
        eq_(ace.named_args, set(["post_id", "comment_id"]))
        eq_(ace.positional_args, 2)
    
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
        eq_(ace.predicate.predicate, predicate)
    
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
        acl.deny("/blog", msg="Noone can access the blog")
        # Checking the new ACE:
        eq_(len(acl._aces), 1)
        ace = acl._aces[0][1]
        assert_false(ace.allow)
        eq_(ace.message, "Noone can access the blog")
    
    def test_deny_without_propagation(self):
        acl = ACL()
        acl.deny("/blog", propagate=False)
        ace = acl._aces[0][1]
        assert_false(ace.propagate)
    
    #{ Testing decisions
    
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
    
    def test_authorization_with_matching_ace_but_no_minimum_arguments(self):
        """
        No decision must be made if the ACE covers the path/object but the
        minimum arguments are not present.
        
        """
        predicate = TitletalePredicate()
        acl = ACL()
        acl.deny("/blog", predicate, named_args=("arg1", ), positional_args=3)
        acl.allow(object(), predicate, named_args=("arg1", ), positional_args=3)
        protected_object = object()
        # ----- Named arguments not present
        environ1 = {
            'PATH_INFO': "/blog",
            # The positional args are OK, but the named ones are not:
            'repoze.what.named_args': set(["arg2"]),
            'repoze.what.positional_args': 4,
            }
        # Checking with just the path:
        eq_(acl.decide_authorization(environ1), None)
        # Checking with the object as well:
        eq_(acl.decide_authorization(environ1, protected_object), None)
        # ----- Positional arguments not present
        environ2 = {
            'PATH_INFO': "/blog",
            # The named args are OK, but the positional ones are not:
            'repoze.what.named_args': set(["arg1"]),
            'repoze.what.positional_args': 0,
            }
        # Checking with just the path:
        eq_(acl.decide_authorization(environ2), None)
        # Checking with the object as well:
        eq_(acl.decide_authorization(environ2, protected_object), None)
        # ----- Named and positional arguments not present
        environ3 = {
            'PATH_INFO': "/blog",
            # Neither named or positional args are OK
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Checking with just the path:
        eq_(acl.decide_authorization(environ3), None)
        # Checking with the object as well:
        eq_(acl.decide_authorization(environ3, protected_object), None)
        # ------ The predicate must not have been evaluated:
        assert_false(predicate.evaluated)
    
    def test_authorization_with_no_matching_ace_but_predicate_not_met(self):
        """
        No decision must be made if the ACE covers the path/object and the
        minimum arguments are present, but the predicate is not met.
        
        """
        predicate1 = TitletalePredicate(False)
        predicate2 = TitletalePredicate(False)
        protected_object = object()
        acl = ACL()
        acl.deny("/blog", predicate1)
        acl.deny(protected_object, predicate2)
        environ = {
            'PATH_INFO': "/blog",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
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
        environ = {
            'PATH_INFO': "/blog",
            'repoze.what.named_args': set(["arg2"]),
            'repoze.what.positional_args': 0,
            }
        # Checking the first ACL:
        decision1 = acl1.decide_authorization(environ)
        ok_(decision1.allow)
        eq_(decision1.message, None)
        eq_(decision1.denial_handler, None)
        eq_(decision1.match_tracker.longest_path_match, 0)
        assert_false(decision1.match_tracker.object_ace_found)
        # Checking the second ACL:
        decision2 = acl2.decide_authorization(environ)
        assert_false(decision2.allow)
        eq_(decision2.message, None)
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
        acl.deny(protected_object, predicate2)
        # Checking with a path:
        environ1 = {
            'PATH_INFO': "/blog",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = acl.decide_authorization(environ1)
        ok_(decision1.allow)
        eq_(decision1.message, None)
        eq_(decision1.denial_handler, None)
        eq_(decision1.match_tracker.longest_path_match, 6)
        assert_false(decision1.match_tracker.object_ace_found)
        # Checking with an object:
        environ2 = {
            'PATH_INFO': "/trac",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = acl.decide_authorization(environ2, protected_object)
        assert_false(decision2.allow)
        eq_(decision2.message, "Titletale predicate")
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
        acl.allow("/blog", predicate1)
        acl.deny("/blog/post_article", predicate1)
        acl.deny("/blog/view_comment", predicate1)
        acl.allow("/blog/view_comment", predicate1)
        acl.allow(protected_object1, predicate1)
        acl.allow(protected_object2, predicate1)
        acl.deny(protected_object2, predicate1)
        acl.deny("/dev", predicate2)
        # ----- No specific ACE, using the default decision:
        environ1 = {
            'PATH_INFO': "/yet-another/path",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = acl.decide_authorization(environ1)
        assert_false(decision1.allow)
        eq_(decision1.message, None)
        eq_(decision1.denial_handler, None)
        eq_(decision1.match_tracker.longest_path_match, 0)
        assert_false(decision1.match_tracker.object_ace_found)
        # ----- One ACE covers the current path:
        environ2 = {
            'PATH_INFO': "/blog",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = acl.decide_authorization(environ2)
        ok_(decision2.allow)
        eq_(decision2.message, None)
        eq_(decision2.denial_handler, None)
        eq_(decision2.match_tracker.longest_path_match, 6)
        assert_false(decision2.match_tracker.object_ace_found)
        # ----- Two ACEs cover the current path; pick the most specific one:
        environ3 = {
            'PATH_INFO': "/blog/post_article",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision3 = acl.decide_authorization(environ3)
        assert_false(decision3.allow)
        eq_(decision3.message, "Titletale predicate")
        eq_(decision3.denial_handler, None)
        eq_(decision3.match_tracker.longest_path_match, 19)
        assert_false(decision3.match_tracker.object_ace_found)
        # ----- Three ACEs cover the current path and two of them cover the
        # ----- exact same path; pick the latest one:
        environ4 = {
            'PATH_INFO': "/blog/view_comment",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision4 = acl.decide_authorization(environ4)
        ok_(decision4.allow)
        eq_(decision4.message, None)
        eq_(decision4.denial_handler, None)
        eq_(decision4.match_tracker.longest_path_match, 19)
        assert_false(decision4.match_tracker.object_ace_found)
        # ----- One ACE covers the object itself:
        environ5 = {
            'PATH_INFO': "/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision5 = acl.decide_authorization(environ5, protected_object1)
        ok_(decision5.allow)
        eq_(decision5.message, None)
        eq_(decision5.denial_handler, None)
        eq_(decision5.match_tracker.longest_path_match, 0)
        ok_(decision5.match_tracker.object_ace_found)
        # ----- Two ACEs cover the request, but one of them cover covers the
        # ----- object so it must picked:
        environ6 = {
            'PATH_INFO': "/blog/post_article",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision6 = acl.decide_authorization(environ6, protected_object1)
        ok_(decision6.allow)
        eq_(decision6.message, None)
        eq_(decision6.denial_handler, None)
        eq_(decision6.match_tracker.longest_path_match, 19)
        ok_(decision6.match_tracker.object_ace_found)
        # ----- Two ACEs cover the object itself; pick the latest one:
        environ7 = {
            'PATH_INFO': "/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision7 = acl.decide_authorization(environ7, protected_object2)
        assert_false(decision7.allow)
        eq_(decision7.message, "Titletale predicate")
        eq_(decision7.denial_handler, None)
        eq_(decision7.match_tracker.longest_path_match, 0)
        ok_(decision7.match_tracker.object_ace_found)
        # ----- ACE covering paths must be ignored if there's already a match
        # ----- for the object itself:
        environ8 = {
            'PATH_INFO': "/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision8 = acl.decide_authorization(environ8, protected_object1)
        ok_(decision8.allow)
        eq_(decision8.message, None)
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
        environ = {
            'PATH_INFO': "/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
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
        environ = {
            'PATH_INFO': "/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = acl.decide_authorization(environ)
        assert_false(decision.allow)
        eq_(decision.denial_handler, denial_handler)
    
    def test_authorization_without_predicates(self):
        """ACEs which don't have predicates must always be taken into account"""
        acl = ACL()
        acl.allow("/blog")
        acl.deny("/blog/post-new", TitletalePredicate())
        acl.deny("/blog/repository")
        acl.allow("/blog/repository/download")
        # ----- Checking just one ACE without predicate:
        environ1 = {
            'PATH_INFO': "/blog/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = acl.decide_authorization(environ1)
        ok_(decision1.allow)
        # ----- Checking two ACEs without predicates:
        environ2 = {
            'PATH_INFO': "/blog/repository",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = acl.decide_authorization(environ2)
        assert_false(decision2.allow)
        # ----- Checking three ACEs without predicates:
        environ3 = {
            'PATH_INFO': "/blog/repository/download",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision3 = acl.decide_authorization(environ3)
        ok_(decision3.allow)
        # ----- Checking an ACE without predicate, overridden with one which
        # ----- does have a predicate:
        environ4 = {
            'PATH_INFO': "/blog/post-new",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision4 = acl.decide_authorization(environ4)
        assert_false(decision4.allow)
        eq_(decision4.message, "Titletale predicate")
    
    def test_authorization_with_custom_messages(self):
        acl = ACL("/blog", allow_by_default=True)
        acl.deny("/add-user", msg="Noone can add users")
        acl.allow("/add-user/tomorrow", msg="Everybody can add users tomorrow")
        acl.deny("/add-post", TitletalePredicate(), msg="Noone can add posts")
        acl.allow("/add-post/tomorrow", TitletalePredicate(),
                  msg="Everybody can add posts tomorrow")
        # Checking the message the authz is denied without a predicate:
        environ1 = {
            'PATH_INFO': "/blog/add-user",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = acl.decide_authorization(environ1)
        assert_false(decision1.allow)
        eq_(decision1.message, "Noone can add users")
        # Checking the message the authz is denied with a predicate:
        environ2 = {
            'PATH_INFO': "/blog/add-post",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = acl.decide_authorization(environ2)
        assert_false(decision2.allow)
        eq_(decision2.message, "Noone can add posts")
        # Checking the message the authz is granted without a predicate:
        environ3 = {
            'PATH_INFO': "/blog/add-user/tomorrow",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision3 = acl.decide_authorization(environ3)
        ok_(decision3.allow)
        eq_(decision3.message, "Everybody can add users tomorrow")
        # Checking the message the authz is granted with a predicate:
        environ4 = {
            'PATH_INFO': "/blog/add-post/tomorrow",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision4 = acl.decide_authorization(environ4)
        ok_(decision4.allow)
        eq_(decision4.message, "Everybody can add posts tomorrow")
    
    def test_authorization_without_propagation_nor_predicate(self):
        """ACEs must not be propagated when explicitly requested."""
        acl = ACL()
        acl.allow("/blog/", propagate=False)
        environ = {
            'PATH_INFO': "/blog/posts",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
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
        environ = {
            'PATH_INFO': "/blog/posts",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = acl.decide_authorization(environ)
        eq_(decision, None)
        assert_false(predicate.evaluated)
    
    def test_authorization_with_ace_with_trailing_slash(self):
        """ACEs with a trailing slash should match requests without it."""
        acl = ACL()
        acl.allow("/path/", propagate=False)
        environ = {
            'PATH_INFO': "/path",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = acl.decide_authorization(environ)
        ok_(decision.allow)
    
    def test_authorization_with_ace_without_trailing_slash(self):
        """ACEs without a trailing slash should match requests with it."""
        acl = ACL()
        acl.allow("/path", propagate=False)
        environ = {
            'PATH_INFO': "/path/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = acl.decide_authorization(environ)
        ok_(decision.allow)
    
    def test_authorization_with_propagation_and_no_trailing_slash(self):
        """
        ACEs without a trailing slash should not match sibling paths.
        
        This is, paths under the same parent directory.
        
        """
        acl = ACL()
        acl.allow("/path", propagate=True)
        environ = {
            'PATH_INFO': "/path-brother",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = acl.decide_authorization(environ)
        eq_(decision, None)
    
    def test_authorization_without_leading_slashes_in_paths(self):
        """Missing leading slashes in the paths must not affect authorization"""
        acl = ACL()
        # ACEs without leading slashes must match right paths:
        acl.allow("foo/")
        environ_with_right_path = {
            'PATH_INFO': "/foo",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = acl.decide_authorization(environ_with_right_path)
        ok_(decision1.allow)
        # Right ACEs must match paths without leading slashes, although this
        # doesn't seem to make sense:
        acl.allow("/bar/")
        environ_with_wrong_path = {
            'PATH_INFO': "bar/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = acl.decide_authorization(environ_with_wrong_path)
        ok_(decision2.allow)
    
    def test_authorization_with_multiple_continuous_slashes_in_paths(self):
        """Multiple continuous slashes in the paths must make no difference."""
        acl = ACL()
        # Checking an ACE with multiple continuous slashes:
        acl.allow("/foo/////bar/")
        environ_with_right_path = {
            'PATH_INFO': "/foo/bar/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = acl.decide_authorization(environ_with_right_path)
        ok_(decision1.allow)
        # Checking an PATH_INFO with multiple continuous slashes:
        acl.allow("/bar/foo/")
        environ_with_wrong_path = {
            'PATH_INFO': "/bar/////foo/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = acl.decide_authorization(environ_with_wrong_path)
        ok_(decision2.allow)
        
    
    #}


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
        environ = {
            'PATH_INFO': "/whatever",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
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
        acl1.deny("/wiki", TitletalePredicate())
        acl2 = ACL("/blog")
        acl3 = ACL("/foo", allow_by_default=False)
        collection = ACLCollection()
        collection.add_acl(acl1)
        collection.add_acl(acl2)
        collection.add_acl(acl3)
        # ----- If there's an ACE, it must be used:
        environ1 = {
            'PATH_INFO': "/trac/wiki/StartPage",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision1 = collection.decide_authorization(environ1)
        assert_false(decision1.allow)
        eq_(decision1.message, "Titletale predicate")
        eq_(decision1.match_tracker.longest_path_match, 11)
        # ----- If there's a default decision, use it:
        environ2 = {
            'PATH_INFO': "/foo/bar",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision2 = collection.decide_authorization(environ2)
        assert_false(decision2.allow)
        eq_(decision2.message, None)
        eq_(decision2.match_tracker.longest_path_match, 0)
        
    def test_authorization_with_many_acls_participating(self):
        """If many ACLs are participating, pick the latest one."""
        acl1 = ACL("/admin", allow_by_default=False)
        acl2 = ACL("/admin/blog")
        acl2.allow("/post", TitletalePredicate())
        acl3 = ACL("/admin/blog/post")
        acl3.deny("", TitletalePredicate(msg="This is something custom"))
        collection = ACLCollection()
        collection.add_acl(acl1)
        collection.add_acl(acl2)
        collection.add_acl(acl3)
        environ = {
            'PATH_INFO': "/admin/blog/post",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = collection.decide_authorization(environ)
        assert_false(decision.allow)
        eq_(decision.message, "This is something custom")
        eq_(decision.match_tracker.longest_path_match, 17)
    
    def test_authorization_with_acl_with_trailing_slash(self):
        """
        ACLs covering a path with a trailing slash must cover requests without
        it.
        
        """
        acl = ACL("/path/", allow_by_default=True)
        collection = ACLCollection()
        collection.add_acl(acl)
        environ = {
            'PATH_INFO': "/path",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
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
        environ = {
            'PATH_INFO': "/path/",
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        decision = collection.decide_authorization(environ)
        ok_(decision.allow)
    
    #}


class TestAuthorizationDecision(TestCase):
    """
    Unit tests for AuthorizationDecision objects.
    
    """
    
    def test_constructor(self):
        denial_handler = object()
        decision = AuthorizationDecision(False, "FooBar", denial_handler)
        eq_(decision.allow, False)
        eq_(decision.message, "FooBar")
        eq_(decision.denial_handler, denial_handler)
        eq_(decision.match_tracker, None)
    
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
    
    def test_constructor_with_no_args(self):
        predicate = is_user("foo")
        ace = _ACE(predicate, True)
        eq_(ace.predicate, predicate)
        eq_(ace.allow, True)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
        eq_(ace.propagate, True)
    
    def test_constructor_with_args(self):
        predicate = is_user("foo")
        ace = _ACE(predicate, True, ("arg1", "arg2"), 3, "Here's a message",
                   False)
        eq_(ace.predicate, predicate)
        eq_(ace.allow, True)
        eq_(ace.named_args, set(["arg1", "arg2"]))
        eq_(ace.positional_args, 3)
        eq_(ace.message, "Here's a message")
        eq_(ace.propagate, False)
    
    def test_denial_ace(self):
        predicate = is_user("foo")
        ace = _ACE(predicate, False)
        #eq_(ace.predicate, predicate)
        eq_(ace.allow, False)
        eq_(ace.named_args, set())
        eq_(ace.positional_args, 0)
    
    def test_denial_ace_without_predicate(self):
        ace = _ACE(None, False)
        eq_(ace.predicate, None)
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        (participation, message) = ace.can_participate(environ)
        ok_(participation)
        eq_(message, None)
    
    def test_denial_ace_without_predicate_and_custom_message(self):
        ace = _ACE(None, False, message="Foo Bar")
        eq_(ace.predicate, None)
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        (participation, message) = ace.can_participate(environ)
        ok_(participation)
        eq_(message, "Foo Bar")
    
    def test_can_participate_without_minimum_args(self):
        """
        The predicate must not be evaluated if the minimum arguments are not
        present.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(["arg1"]),
            'repoze.what.positional_args': 1,
            }
        # Set:
        ace = _ACE(predicate, True, ["arg1", "arg2"], 3)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, False)
        eq_(message, None)
        assert_false(predicate.evaluated)
    
    def test_can_participate_with_wrong_named_args(self):
        """
        The predicate must not be evaluated if the ACE does not cover the named
        arguments present.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(["foo"]),
            'repoze.what.positional_args': 1,
            }
        # Set:
        ace = _ACE(predicate, True, ["arg1", "arg2"])
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, False)
        eq_(message, None)
        assert_false(predicate.evaluated)
    
    def test_can_participate_with_less_positional_args(self):
        """
        The predicate must not be evaluated if the ACE covers a request with
        more positional arguments.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(["arg1"]),
            'repoze.what.positional_args': 2,
            }
        # Set:
        ace = _ACE(predicate, True, ["arg1"], 3)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, False)
        eq_(message, None)
        assert_false(predicate.evaluated)
    
    def test_can_participate_with_exact_args(self):
        """
        The predicate must be evaluated if the ACE covers a request with the
        exact required arguments.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(["arg1", "arg2"]),
            'repoze.what.positional_args': 2,
            }
        # Set:
        ace = _ACE(predicate, True, ["arg1", "arg2"], 2)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, True)
        eq_(message, None)
        ok_(predicate.evaluated)
    
    def test_can_participate_with_more_args(self):
        """
        The predicate must be evaluated if the ACE covers a request with more
        arguments than those required.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(["arg1", "arg2", "arg3"]),
            'repoze.what.positional_args': 4,
            }
        # Set:
        ace = _ACE(predicate, True, ["arg1", "arg2"], 2)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, True)
        eq_(message, None)
        ok_(predicate.evaluated)
    
    def test_predicate_met_and_authz_denied(self):
        """
        The ACE must participate if the predicate is met and authz is denied.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Set:
        ace = _ACE(predicate, False)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, True)
        eq_(message, "Titletale predicate")
        ok_(predicate.evaluated)
    
    def test_predicate_met_and_authz_granted(self):
        """
        The ACE must participate if the predicate is met and authz is granted.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Set:
        ace = _ACE(predicate, True)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, True)
        eq_(message, None)
        ok_(predicate.evaluated)
    
    def test_predicate_met_and_authz_denied_with_custom_message(self):
        """
        The ACE must participate with a custom message if the predicate is met
        and authz is denied.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Set:
        ace = _ACE(predicate, False, message="ABC XYZ")
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, True)
        eq_(message, "ABC XYZ")
        ok_(predicate.evaluated)
    
    def test_predicate_met_and_authz_granted_with_custom_message(self):
        """
        The ACE must participate with a custom message if the predicate is met
        and authz is granted.
        
        """
        # Ready:
        predicate = TitletalePredicate()
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Set:
        ace = _ACE(predicate, True, message="ABC XYZ")
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, True)
        eq_(message, "ABC XYZ")
        ok_(predicate.evaluated)
    
    def test_predicate_unmet_and_authz_denied(self):
        """
        The ACE must not participate if the predicate isn't met and authz is
        denied.
        
        """
        # Ready:
        predicate = TitletalePredicate(False)
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Set:
        ace = _ACE(predicate, False)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, False)
        eq_(message, None)
        ok_(predicate.evaluated)
    
    def test_predicate_unmet_and_authz_granted(self):
        """
        The ACE must not participate if the predicate isn't met and authz is
        granted
        
        """
        # Ready:
        predicate = TitletalePredicate(False)
        environ = {
            'repoze.what.named_args': set(),
            'repoze.what.positional_args': 0,
            }
        # Set:
        ace = _ACE(predicate, True)
        # Go!:
        (participation, message) = ace.can_participate(environ)
        eq_(participation, False)
        eq_(message, "Titletale predicate")
        ok_(predicate.evaluated)


class TestMatchTracker(TestCase):
    """Tests for the internal _MatchTracker."""
    
    def test_constructor(self):
        tracker = _MatchTracker()
        eq_(tracker.longest_path_match, 0)
        eq_(tracker.object_ace_found, False)
    
    def test_scope_check_with_wrong_path(self):
        """
        A request is out of the scope of a protected path if the PATH_INFO
        doesn't start with that protected path.
        
        """
        tracker = _MatchTracker()
        assert_false(tracker.is_within_scope("/admin", True, "/blog/"))
    
    def test_scope_check_with_less_specific_path(self):
        """
        A request is out of the scope of a protected path if we already found
        an ACL/ACE more specific to such a request.
        
        """
        tracker = _MatchTracker()
        tracker.longest_path_match = 3
        assert_false(tracker.is_within_scope("/", True, "/blog"))
    
    def test_scope_check_with_object_protection_found(self):
        """
        A request is out of the scope of a protected path if we already found 
        an ACL/ACE for the object in the request itself.
        
        """
        tracker = _MatchTracker()
        tracker.object_ace_found = True
        assert_false(tracker.is_within_scope("/", True, "/blog/"))
    
    def test_scope_check_with_right_path(self):
        """
        A request is within the scope of a protected path if that path is the
        most specific one so far.
        
        """
        tracker = _MatchTracker()
        ok_(tracker.is_within_scope("/blog", True, "/blog/add_post"))
    
    def test_scope_check_with_equally_specific_path(self):
        """
        A request is within the scope of a protected path if that path is the
        as specific to the request as another one already found.
        
        """
        tracker = _MatchTracker()
        tracker.longest_path_match = 1
        ok_(tracker.is_within_scope("/", True, "/blog"))
    
    def test_scope_check_with_parent_path_but_no_propagation(self):
        """
        A request is not within the scope of a parent path if the later is not
        propagated.
        
        """
        tracker = _MatchTracker()
        assert_false(tracker.is_within_scope("/blog", False, "/blog/add_post"))
    
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
    
    message = "Titletale predicate"
    
    def __init__(self, evaluation_result=True, *args, **kwargs):
        self.evaluation_result = evaluation_result
        self.evaluated = False
        super(TitletalePredicate, self).__init__(*args, **kwargs)
    
    def evaluate(self, environ, credentials):
        self.evaluated = True
        if not self.evaluation_result:
            raise NotAuthorizedError(self.message)


#}
