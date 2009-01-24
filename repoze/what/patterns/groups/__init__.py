# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
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
Support for the groups/permissions-based authorization pattern.

"""

from repoze.what.patterns.groups.predicates import in_group, has_permission, \
                                                   in_all_groups, \
                                                   has_all_permissions, \
                                                   in_any_group, \
                                                   has_any_permission


__all__ = ['in_group', 'has_permission', 'in_all_groups', 
           'has_all_permissions', 'in_any_group', 'has_any_permission']
