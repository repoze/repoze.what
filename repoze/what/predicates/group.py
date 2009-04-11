# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
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
Predicate checkers for the groups.

"""

from repoze.what.predicates.generic import Predicate, All, Any


__all__ = ['in_all_groups', 'in_any_group', 'in_group']


class in_group(Predicate):
    """
    Check that the user belongs to the specified group.
    
    :param group_name: The name of the group to which the user must belong.
    :type group_name: str
    
    Example::
    
        p = in_group('customers')
    
    """
    
    message = u'The current user must belong to the group "%(group_name)s"'
    
    def __init__(self, group_name, **kwargs):
        super(in_group, self).__init__(**kwargs)
        self.group_name = group_name

    def evaluate(self, environ, credentials):
        if credentials and self.group_name in credentials.get('groups'):
            return
        self.unmet()


class in_all_groups(All):
    """
    Check that the user belongs to all of the specified groups.
    
    :param groups: The name of all the groups the user must belong to.
    
    Example::
    
        p = in_all_groups('developers', 'designers')
    
    """
    
    def __init__(self, *groups, **kwargs):
        group_predicates = [in_group(g) for g in groups]
        super(in_all_groups,self).__init__(*group_predicates, **kwargs)


class in_any_group(Any):
    """
    Check that the user belongs to at least one of the specified groups.
    
    :param groups: The name of any of the groups the user may belong to.
    
    Example::
    
        p = in_any_group('directors', 'hr')
    
    """
    
    message = u"The member must belong to at least one of the following " \
               "groups: %(group_list)s"
    
    def __init__(self, *groups, **kwargs):
        self.group_list = ", ".join(groups)
        group_predicates = [in_group(g) for g in groups]
        super(in_any_group,self).__init__(*group_predicates, **kwargs)

