# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>
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
Ensure :mod:`repoze.what` is thread-safe when some components are instantiated
at module-level and shared among threads.

Thanks to Alberto Valverde for helping me write these tests!

"""

import sys, time
from threading import Thread, Event, Timer
from string import ascii_letters
from unittest import TestCase

from repoze.what.predicates import *
from repoze.what.authorize import check_authorization, NotAuthorizedError


#{ The test cases


class TestPredicateErrors(TestCase):
    """
    Test that all the built-in predicates are thread-safe.
    
    Alberto Valverde found that "All"-based predicates were not thread-safe 
    because if they are instantiated at module-level and used among many 
    threads, their error message of a predicate that failed on one thread would
    override the message of a failed predicate on another thread -- that's
    because there'd be only one predicate, not one per thread.
    
    So this test case would ensure this won't happen again, on any other
    predicate, "All"-based or not.
    
    """
    
    def setUp(self):
        self.found_error = Event()
        self.threads = []
        self.threads_stopped = False
    
    def tearDown(self):
        self._stop_threads()
    
    def _share_predicate_among_threads(self, shared_predicate, scenarios):
        """
        Share predicate ``shared_predicate`` among many threads (one per
        scenario).
        
        """
        # First define the scenarios to be run in one thread
        for scenario in scenarios:
            thread = DaPredicateThread(scenario['credentials'],
                                       shared_predicate, scenario['error'],
                                       self.found_error)
            self.threads.append(thread)
        # Configuring the timer that is going to stop threads when the
        # predicate in question IS thread-safe.
        t = Timer(2, self._stop_threads)
        t.start()
        # Running the threads:
        map(Thread.start, self.threads)
        if self.found_error.isSet():
            predicate_class = shared_predicate.__class__.__name__
            self.fail('Predicate %s is not thread-safe' % predicate_class)
    
    def _stop_threads(self):
        """Stop all the threads"""
        if self.threads_stopped:
            return
        for thread in self.threads:
            thread.stop = True
        self.threads_stopped = True
    
    def test_is_user(self):
        """The is_user predicate is thread-safe."""
        # Building the shared predicate:
        users = set(ascii_letters)
        shared_predicate = is_user('foo')
        error = 'The current user must be "foo"'
        # Building the test scenarios that will share the predicate above:
        scenarios = []
        for u in users:
            credentials = {'repoze.what.userid': u}
            scenario = {'credentials': credentials, 'error': error}
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_in_group(self):
        """The in_group predicate is thread-safe."""
        # Building the shared predicate:
        groups = set(ascii_letters)
        shared_predicate = in_group('foo')
        error = 'The current user must belong to the group "foo"'
        # Building the test scenarios that will share the predicate above:
        scenarios = []
        for g in groups:
            credentials = {'groups': groups.copy()}
            scenario = {'credentials': credentials, 'error': error}
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_in_all_groups(self):
        """The in_all_groups predicate is thread-safe."""
        # Building the shared predicate:
        all_groups = set(ascii_letters)
        shared_predicate = in_all_groups(*all_groups)
        # Building the test scenarios that will share the predicate above:
        scenarios = []
        for g in all_groups:
            error = 'The current user must belong to the group "%s"' % g
            scenario = {
                'credentials': {'groups': all_groups - set([g])},
                'error': error,
                }
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_in_any_group(self):
        """The in_any_group predicate is thread-safe."""
        # Building the shared predicate:
        all_groups = set(ascii_letters)
        shared_predicate = in_any_group(*all_groups)
        error = "The member must belong to at least one of the following "\
                "groups: "
        error = error + ', '.join(all_groups)
        # Building the test scenarios that will share the predicate above:
        credentials = {'groups': set([u"ñ", u"é"])}
        scenarios = []
        for g in all_groups:
            scenario = {'credentials': credentials, 'error': error}
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_has_permission(self):
        """The has_permission predicate is thread-safe."""
        # Building the shared predicate:
        perms = set(ascii_letters)
        shared_predicate = has_permission('foo')
        error = 'The user must have the "foo" permission'
        # Building the test scenarios that will share the predicate above:
        scenarios = []
        for p in perms:
            credentials = {'permissions': perms.copy()}
            scenario = {'credentials': credentials, 'error': error}
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_has_all_permissions(self):
        """The has_all_permissions predicate is thread-safe."""
        # Building the shared predicate:
        all_perms = set(ascii_letters)
        shared_predicate = has_all_permissions(*all_perms)
        # Building the test scenarios that will share the predicate above:
        scenarios = []
        for p in all_perms:
            error = 'The user must have the "%s" permission' % p
            scenario = {
                'credentials': {'permissions': all_perms - set([p])},
                'error': error,
                }
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_has_any_permission(self):
        """The has_any_permission predicate is thread-safe."""
        # Building the shared predicate:
        all_perms = set(ascii_letters)
        shared_predicate = has_any_permission(*all_perms)
        error = "The user must have at least one of the following "\
                "permissions: "
        error = error + ', '.join(all_perms)
        # Building the test scenarios that will share the predicate above:
        credentials = {'permissions': set([u"ñ", u"é"])}
        scenarios = []
        for p in all_perms:
            scenario = {'credentials': credentials, 'error': error}
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_All(self):
        """The All predicate is thread-safe."""
        # Building the shared predicate:
        all_groups = set(ascii_letters)
        shared_predicate = All(*map(in_group, all_groups))
        # Building the test scenarios that will share the predicate above:
        scenarios = []
        for g in all_groups:
            error = 'The current user must belong to the group "%s"' % g
            scenario = {
                'credentials': {'groups': all_groups - set([g])},
                'error': error,
                }
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)
    
    def test_Any(self):
        """The Any predicate is thread-safe."""
        # Building the shared predicate:
        expected_users = set(ascii_letters)
        shared_predicate = Any(*map(is_user, expected_users))
        error = "At least one of the following predicates must be met:"
        for u in expected_users:
            error = error + ' The current user must be "%s",' % u
        error = error[:-1]
        # Building the test scenarios that will share the predicate above:
        credentials = {'repoze.what.userid': None}
        scenarios = []
        for u in expected_users:
            scenario = {'credentials': credentials, 'error': error}
            scenarios.append(scenario)
        self._share_predicate_among_threads(shared_predicate, scenarios)


#{ Test utilities


class DaPredicateThread(Thread):
    def __init__(self, credentials, shared_predicate, expected_error,
                 found_error, *args, **kwargs):
        super(DaPredicateThread, self).__init__(*args, **kwargs)
        self.credentials = credentials
        self.shared_predicate = shared_predicate
        self.expected_error = expected_error
        self.found_error = found_error
        self.stop = False

    def run(self):
        while not self.found_error.isSet() and not self.stop:
            # Create a new environ simulating the fresh environ each request gets
            environ = {'repoze.what.credentials': self.credentials.copy()}
            try:
                check_authorization(self.shared_predicate, environ)
            except NotAuthorizedError, exc:
                if unicode(exc) != self.expected_error:
                    self.found_error.set()


#}
