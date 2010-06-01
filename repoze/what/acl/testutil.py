# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, Gustavo Narea <me@gustavonarea.net>.
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
Test utilities for the ACLs.

"""


class GetAbetterName(object):
    
    def __init__(self, global_control):
        self._global_control = global_control
    
    def get_decision(self, path):
        


class AssertableDecision(object):
    
    def assert_allows(self):
        assert self._allow, "The decision is to grant authorization"
    
    def assert_denies(self):
        assert self._allow is False, "The decision is to deny authorization"
    
    def assert_no_decision(self):
        assert self._allow is None, "There was no authorization decision"
