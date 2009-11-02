#!/usr/bin/env python
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
from time import clock, time
from sys import exit, platform

from plugins_setup import group_adapters, permission_adapters
from config import iterations_per_action, groups, permissions, group_actions, \
                   permission_actions, mock_items_per_section, mock_sections, \
                   threads_per_benchmark

from repoze.what.adapters.benchmark import compare_benchmarks

# --- Confirming that the user really wants to override the existing data:


print "***** WARNING *****"
print "The users, groups and permissions in the sources, if any, will be removed!"
confirmation = raw_input("Are you sure you want to continue? [yes/no] ")

if confirmation.lower() != "yes":
    print "Aborted."
    exit()


# --- Running the benchmarks:


if platform == "win32":
    timer = clock
else:
    timer = time

# Filling the sources with mock data:
for section_number in range(mock_sections):
    section_name = u"mock_section_%s" % section_number
    groups[section_name] = []
    permissions[section_name] = []
mock_items = [u"mock_item_%s" % item_number for item_number
              in range(mock_items_per_section)]
for group in groups.keys():
    groups[group].extend(mock_items)
for permission in permissions.keys():
    permissions[permission].extend(mock_items)

# Reporting how the benchmark will be run:
group_adapters_names = ", ".join([name for name in group_adapters.keys()])
perms_adapters_names = ", ".join([name for name in permission_adapters.keys()])
benchmarks_amount = len(group_adapters) * len(group_actions) + \
                    len(permission_adapters) * len(permission_actions)

print
print "The benchmarks are going to start with the following settings:"
print " * %s groups, with %s mock users per group." % (len(groups),
                                                       mock_items_per_section)
print " * %s permissions, with %s mock groups per permission." % (
      len(permissions), mock_items_per_section)
print " * %s group adapters: %s." % (len(group_adapters), group_adapters_names)
print " * %s permission adapters: %s." % (len(permission_adapters),
                                         perms_adapters_names)
print " * %s and %s actions to be performed on the group and permission " \
      "adapters above, respectively, %s times each." % (len(group_actions),
                                                        len(permission_actions),
                                                        iterations_per_action)
print
print "Starting %s benchmarks in %s threads!" % (benchmarks_amount,
                                                 threads_per_benchmark)

start_time = timer()

group_results = compare_benchmarks(iterations_per_action, groups,
                                   threads_per_benchmark, *group_actions,
                                   **group_adapters)

permission_results = compare_benchmarks(iterations_per_action, permissions,
                                        threads_per_benchmark,
                                        *permission_actions,
                                        **permission_adapters)

end_time = timer()
elapsed_time = end_time - start_time

print "End of benchmarks (%s minutes)." % (elapsed_time/60)
print


# --- Presenting the results:


def sort_fastest(results):
    """Sort the ``results``, from the fastest to the slowest."""
    sorted_results = sorted(results.iteritems(), key=lambda (k, v):(v, k))
    return sorted_results

def print_action_results(results):
    results = sort_fastest(results)
    counter = 1
    for (adapter, average) in results:
        print "   %s.- %s: %s seconds average." % (
              counter, adapter, average)
        counter += 1

def print_results(results):
    for action_number in range(len(results)):
        action_results = results[action_number]
        print " * Results for action #%s, starting by the fastest adapters:" \
              % (action_number + 1)
        print_action_results(action_results)

print "***** Benchmark results *****"

print "Group results:"
print_results(group_results)
print
print "Permission results:"
print_results(permission_results)
