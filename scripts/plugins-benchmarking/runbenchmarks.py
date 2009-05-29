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
from sys import exit
from plugins_setup import group_adapters, permission_adapters
from config import iterations_per_action, groups, permissions, group_actions, \
                   permission_actions, mock_items_per_section, mock_sections

from repoze.what.adapters.benchmark import compare_benchmarks

# --- Confirming that the user really wants to override the existing data:

print "***** WARNING *****"
print "The users, groups and permissions in the sources, if any, will be removed!"
confirmation = raw_input("Are you sure you want to continue? [yes/no] ")

if confirmation.lower() != "yes":
    print "Aborted."
    exit()

# --- Running the benchmarks:

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

print "The benchmarks are going to start with the following settings:"
print "Groups:", groups
print "Permissions:", permissions
print
print "Starting the benchmarks!"

group_results = compare_benchmarks(iterations_per_action, groups,
                                   *group_actions, **group_adapters)

permission_results = compare_benchmarks(iterations_per_action, permissions,
                                        *permission_actions, **permission_adapters)

# --- Presenting the results:

print group_results, permission_results
