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
Benchmark utilities for source adapters.

"""
from sys import platform
from time import clock, time
from threading import Thread

__all__ = ["AdapterBenchmark", "compare_benchmarks", "GroupsRetrievalAction",
           "PermissionsRetrievalAction"]


# http://coreygoldberg.blogspot.com/2008/09/python-timing-timeclock-vs-timetime.html
if platform == "win32": #pragma: no cover
    timer = clock
else:
    timer = time


class AdapterBenchmark(object):
    """
    Adapter benchmark.
    
    Instances of this class represent a benchmark on a :mod:`repoze.what`
    :term:`source adapter`.
    
    The source used by the adapter will be reset on every iteration, so if the
    adapter requires this to be handled in a special way, you should extend
    this class to override :meth:`reset_source` (but don't forget to call the
    original method).
    
    """
    
    def __init__(self, adapter):
        """
        Set up a benchmark for ``adapter``.
        
        :param adapter: The source adapter to be benchmarked.
        
        """
        self.adapter = adapter
    
    def run(self, action, iterations, source=None, threads=None):
        """
        Run read-only ``action`` on the source adapter ``iteration`` times,
        possibly in different threads.
        
        :param action: The action to run on the adapter.
        :param threads: How many threads should run the benchmark independently;
            one by default.
        :type threads: int
        :param iterations: The amount of times ``actions`` must be run.
        :type iterations: int
        :param source: The sections and items the source must contain.
        :type source: dict
        :return: The average time elapsed, in seconds.
        :rtype: float
        
        This method will run the benchmark in different threads (this amount
        is set via ``threads``).
        
        The ``action`` is a callable that receives the adapter as the only
        argument. If ``source`` is ``None``, the source used by the adapter
        won't ever be reset.
        
        The result is the average of the benchmarks' elapsed time in the
        different threads.
        
        .. warning::
        
            When the benchmark is going to be run in two or more threads,
            the ``action`` **must** be a read-only operation. Its source will be
            reset to ``source`` *once*, before running the benchmarks in
            different threads, to avoid modifying the source shared among many
            threads.
            
            When the benchmark is run in a single thread, the ``action`` can
            write on the source because such a source will be reset to
            ``source`` right before each iteration.
        
        """
        if not threads or threads == 1:
            # It's just one thread, then run it in this thread!
            return self._run(action, iterations, source)
        
        self.reset_source(source)
        
        thread_container = []
        for thread_num in range(threads):
            thread_container.append(_BenchmarkThread(self, iterations, action))
        map(_BenchmarkThread.start, thread_container)
        
        # Wait until all the benchmarks are finished:
        while _BenchmarkThread.threads_alive(thread_container):
            continue
        
        # Finding the results:
        time_elapsed = 0
        for thread in thread_container:
            time_elapsed += thread.elapsed_time
        
        average_time = time_elapsed / threads
        
        return average_time
    
    def _run(self, action, iterations, source=None):
        """
        Return the time elapsed when ``action`` is run on the source adapter
        ``iterations`` times, with the adapter's source being reset to
        ``source`` on each iteration.
        
        :param action: The action to run on the adapter.
        :param iterations: The amount of times ``actions`` must be run.
        :type iterations: int
        :param source: The sections and items the source must contain.
        :type source: dict
        :return: The average time elapsed, in seconds.
        :rtype: float
        
        The ``action`` is a callable that receives the adapter as the only
        argument.
        
        If ``source`` is ``None``, the source used by the adapter won't ever
        be reset.
        
        """
        elapsed_time = 0
        
        for iteration in range(iterations):
            self.reset_source(source)
            # Measuring the time:
            start_time = timer()
            action(self.adapter)
            end_time = timer()
            elapsed_time += end_time - start_time
        
        average_time = elapsed_time / iterations
        
        return average_time
    
    def reset_source(self, source=None):
        """
        Reset the source used by the adapter to ``source`` if it's defined.
        
        :param source: The sections and items the source must contain.
        :type source: dict
        
        Either way, it will always reset the adapter's cache.
        
        """
        if source:
            # Emptying the adapter's source:
            sections = self.adapter.get_all_sections().keys()
            for section in sections:
                self.adapter.delete_section(section)
            # Filling the adapter's source:
            for (new_section, items) in source.items():
                self.adapter.create_section(new_section)
                self.adapter.set_section_items(new_section, items)
        # Resetting the adapter's cache:
        self.adapter.loaded_sections = {}
        self.adapter.all_sections_loaded = False


def compare_benchmarks(iterations, source, threads=None, *actions, **adapters):
    """
    Compare all the ``adapters`` using the same benchmarks.
    
    :param iterations: How many times should each action in ``actions`` be
        executed.
    :type iterations: int
    :param source: The contents all the source adapters must have.
    :type source: dict
    :param threads: How many threads should run the benchmarks? One by default.
    :return: The results for each adapter, organized by actions.
    :rtype: list
    :raises AssertionError: If there are no ``actions`` and/or less than 2
        ``adapters``.
    
    ``actions`` represent all the actions to be executed on each adapter.
    
    Adapters in ``adapters`` can be passed as :class:`AdapterBenchmark`
    instances if desired. This will be useful when you need to control the
    reset of the source for such adapters in
    :meth:`AdapterBenchmark.reset_source`.
    
    """
    assert len(actions) >= 1, "At least one action must be run"
    assert len(adapters) >= 2, "At least two adapters must be compared"
    
    # Turning those adapters into benchmarks if required:
    for (adapter_name, adapter) in adapters.items():
        if not isinstance(adapter, AdapterBenchmark):
            adapters[adapter_name] = AdapterBenchmark(adapter)
    
    results = []
    
    for action in actions:
        action_results = {}
        for (adapter_name, adapter) in adapters.items():
            time_elapsed = adapter.run(action, iterations, source, threads)
            action_results[adapter_name] = time_elapsed
        results.append(action_results)
    
    return results


#{ Built-in benchmark actions


class GroupsRetrievalAction(object):
    """
    Benchmark action that retrieves all the groups to which one user belongs.
    
    """
    
    def __init__(self, user_id):
        """Retrieve the groups for the user identified by ``user_id``."""
        self.user_id = user_id
    
    def __call__(self, adapter):
        credentials = {'repoze.what.userid': self.user_id}
        adapter.find_sections(credentials)


class PermissionsRetrievalAction(object):
    """
    Benchmark action that retrieves all the permissions granted to a given
    group.
    
    """
    
    def __init__(self, group_id):
        """Retrieve the permissions for the group identified by ``group_id``."""
        self.group_id = group_id
    
    def __call__(self, adapter):
        adapter.find_sections(self.group_id)


#{ Internal utilities


class _BenchmarkThread(Thread):
    """
    Thread to run a read-only benchmark.
    
    """
    
    def __init__(self, benchmark, iterations, action, *args, **kwargs):
        """
        Run the ``benchmark`` ``iterations`` times in an individual thread.
        
        :param benchmark: The benchmark to be run.
        :type benchmark: AdapterBenchmark
        :param iterations: How many times the benchmark should be run.
        :type iterations: int
        :param action: The action to be performed on the adapter.
        
        """
        self.benchmark = benchmark
        self.iterations = iterations
        self.action = action
        self.elapsed_time = None
        super(_BenchmarkThread, self).__init__(*args, **kwargs)
    
    def run(self): # pragma: no cover
        """
        Run the benchmark in a separate thread and store the elapsed time.
        
        """
        self.elapsed_time = self.benchmark._run(self.action, self.iterations)
    
    @classmethod
    def threads_alive(cls, threads):
        """Checks if at least one of the ``threads`` is alive."""
        for thread in threads:
            if thread.isAlive():
                return True
        return False


#}
