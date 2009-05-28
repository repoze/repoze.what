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

"""Test suite for the adapters' benchmark utilities."""

from time import sleep
from unittest import TestCase
from nose.tools import eq_, ok_, assert_raises

from repoze.what.adapters.benchmark import (AdapterBenchmark,
    compare_benchmarks, GroupsRetrievalAction, PermissionsRetrievalAction)

from base import FakeGroupSourceAdapter, FakePermissionSourceAdapter


class TestAdapterBenchmark(TestCase):
    """Tests for the :class:`AdapterBenchmark`."""
    
    def test_resetting_with_source(self):
        """
        When the source is reset, it should be overriden with new contents if
        asked so.
        
        """
        source = {
            'parents': set([u"liliana", u"carlos"]),
            'sisters': set([u"lisbeth", u"carla"]),
            'brothers': set([u"oliver"]),
        }
        benchmark = AdapterBenchmark(FakeGroupSourceAdapter())
        benchmark.reset_source(source)
        eq_(benchmark.adapter.get_all_sections(), source)
    
    def test_resetting_without_source(self):
        """
        When the source is reset, it should be overriden with new contents
        unless aked otherwise.
        
        """
        adapter = FakeGroupSourceAdapter()
        original_source = adapter.fake_sections
        benchmark = AdapterBenchmark(adapter)
        benchmark.reset_source(None)
        eq_(benchmark.adapter.get_all_sections(), original_source)
    
    def test_resetting_resets_adapter_cache(self):
        """Source resets must also reset the adapter's cache."""
        adapter = FakeGroupSourceAdapter()
        benchmark = AdapterBenchmark(adapter)
        # Loading some stuff before resetting the benchmark:
        adapter.get_all_sections()
        eq_(adapter.loaded_sections, adapter.fake_sections)
        eq_(adapter.all_sections_loaded, True)
        # Is the adapter's cache reset after resetting from the benchmark?
        benchmark.reset_source(None)
        eq_(len(adapter.loaded_sections), 0)
        eq_(adapter.all_sections_loaded, False)
    
    def test_running_benchmark(self):
        adapter = MockAdapter()
        benchmark = MockBenchmark(adapter)
        action = DelayingAction(0.05)
        iterations = 5
        # Running the benchmark without overriding the source:
        elapsed_time = benchmark.run(action, iterations)
        action.check_elapsed_time(elapsed_time, iterations)
        eq_(adapter.resets, iterations)
        eq_(adapter.actions, iterations)
        # Running the benchmark overriding the source:
        elapsed_time = benchmark.run(action, iterations, {'a': set()})
        action.check_elapsed_time(elapsed_time, iterations)
        eq_(adapter.resets, iterations * 2)
        eq_(adapter.actions, iterations * 2)
        eq_(adapter.get_all_sections(), {'a': set()})


class TestBenchmarkComparison(TestCase):
    """
    Tests for the benchmark comparisons (the compare_benchmarks() function).
    
    """
    
    def test_no_actions(self):
        benchmark = AdapterBenchmark(MockAdapter())
        assert_raises(AssertionError, compare_benchmarks, 2, None,
                      mock_adapter=benchmark, mock_adapter2=benchmark)
    
    def test_no_benchmarks(self):
        assert_raises(AssertionError, compare_benchmarks, 2, None, None)
    
    def test_one_benchmark(self):
        benchmark = AdapterBenchmark(MockAdapter())
        assert_raises(AssertionError, compare_benchmarks, 2, None,
                      mock_adapter=benchmark)
    
    def test_comparing_with_benchmarks(self):
        """Comparisons should work when given benchmarks instead of adapters."""
        adapter1 = MockAdapter()
        adapter2 = MockAdapter()
        benchmark1 = MockBenchmark(adapter1)
        benchmark2 = MockBenchmark(adapter2)
        action1 = DelayingAction(0.1)
        action2 = DelayingAction(0.07)
        action3 = DelayingAction(0.05)
        iterations = 4
        source = {'section1': set([u"item1"]), 'section2': set()}
        # Running the benchmark:
        results = compare_benchmarks(iterations, source, action1, action2,
                                     action3, adapter1=benchmark1,
                                     adapter2=benchmark2)
        eq_(len(results), 3)
        result1, result2, result3 = results
        ok_(result1.keys() == result2.keys() == result3.keys() \
            == ["adapter2", "adapter1"])
        # Checking the results for the first action:
        action1.check_elapsed_time(result1['adapter1'], iterations)
        action1.check_elapsed_time(result1['adapter2'], iterations)
        # Checking the results for the second action:
        action2.check_elapsed_time(result2['adapter1'], iterations)
        action2.check_elapsed_time(result2['adapter2'], iterations)
        # Checking the results for the third action:
        action3.check_elapsed_time(result3['adapter1'], iterations)
        action3.check_elapsed_time(result3['adapter2'], iterations)
        # Finally, some general tests to make sure the benchmarks were used
        # equally
        eq_(adapter1.resets, adapter1.actions)
        eq_(adapter2.resets, adapter2.resets)
        eq_(adapter1.resets, adapter2.resets)
        eq_(adapter1.resets, iterations * len(results))
    
    def test_comparing_with_adapters(self):
        """When given adapters, they must be turned into benchmarks."""
        adapter1 = MockAdapter()
        adapter2 = MockAdapter()
        action1 = DelayingAction(0.1)
        action2 = DelayingAction(0.07)
        action3 = DelayingAction(0.05)
        iterations = 4
        source = {'section1': set([u"item1"]), 'section2': set()}
        # Running the benchmark:
        results = compare_benchmarks(iterations, source, action1, action2,
                                     action3, adapter1=adapter1,
                                     adapter2=adapter2)
        eq_(len(results), 3)
        result1, result2, result3 = results
        ok_(result1.keys() == result2.keys() == result3.keys() \
            == ["adapter2", "adapter1"])
        # Checking the results for the first action:
        action1.check_elapsed_time(result1['adapter1'], iterations)
        action1.check_elapsed_time(result1['adapter2'], iterations)
        # Checking the results for the second action:
        action2.check_elapsed_time(result2['adapter1'], iterations)
        action2.check_elapsed_time(result2['adapter2'], iterations)
        # Checking the results for the third action:
        action3.check_elapsed_time(result3['adapter1'], iterations)
        action3.check_elapsed_time(result3['adapter2'], iterations)
        # Finally, some general tests to make sure the benchmarks were used
        # equally
        eq_(adapter1.actions, adapter2.actions)


class TestBuiltinActions(TestCase):
    """
    Tests for the built-in actions (i.e., GroupsRetrievalAction and
    PermissionsRetrievalAction.
    
    """
    
    def test_groups_retrieval(self):
        """GroupsRetrievalAction must call group_adapter.find_sections()."""
        class GroupAdapter(FakeGroupSourceAdapter):
            def __init__(self):
                super(GroupAdapter, self).__init__()
                self.groups_retrieval_counter = 0
            
            def _find_sections(self, credentials):
                self.groups_retrieval_counter += 1
                super(GroupAdapter, self)._find_sections(credentials)
        
        adapter = GroupAdapter()
        benchmark = AdapterBenchmark(adapter)
        action = GroupsRetrievalAction(u"rms")
        iterations = 4
        benchmark.run(action, iterations)
        eq_(adapter.groups_retrieval_counter, iterations)
    
    def test_permissions_retrieval(self):
        """PermissionsRetrievalAction must call perm_adapter.find_sections()."""
        class PermissionAdapter(FakePermissionSourceAdapter):
            def __init__(self):
                super(PermissionAdapter, self).__init__()
                self.permissions_retrieval_counter = 0
            
            def _find_sections(self, group_name):
                self.permissions_retrieval_counter += 1
                super(PermissionAdapter, self)._find_sections(group_name)
        
        adapter = PermissionAdapter()
        benchmark = AdapterBenchmark(adapter)
        action = PermissionsRetrievalAction(u"developers")
        iterations = 4
        benchmark.run(action, iterations)
        eq_(adapter.permissions_retrieval_counter, iterations)


#{ Mock objects


class MockAdapter(FakeGroupSourceAdapter):
    def __init__(self, *args, **kwargs):
        super(MockAdapter, self).__init__(*args, **kwargs)
        self.resets = 0
        self.actions = 0

class MockBenchmark(AdapterBenchmark):
    def reset_source(self, source):
        super(MockBenchmark, self).reset_source(source)
        self.adapter.resets += 1


class DelayingAction(object):
    def __init__(self, seconds):
        self.seconds = seconds
    
    def __call__(self, adapter):
        adapter.actions += 1
        sleep(self.seconds)
    
    def check_elapsed_time(self, elapsed_time, iterations):
        exact_time = self.seconds * iterations
        margin_of_error = self.seconds / 10
        # Taking into account the margin of error:
        more_time = exact_time + margin_of_error
        less_time = exact_time - margin_of_error
        ok_(elapsed_time < more_time and elapsed_time > less_time,
            "The benchmark took %s seconds, which is out of the valid range" %
            elapsed_time)


#}
