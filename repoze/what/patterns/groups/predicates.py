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
Predicate checkers for the groups/permissions-based pattern.

"""

from repoze.what.predicates import Predicate, All, Any


__all__ = ['has_all_permissions', 'has_any_permission', 'has_permission', 
           'in_all_groups', 'in_any_group', 'in_group']


#{ Predicates


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


class has_permission(Predicate):
    """
    Check that the current user has the specified permission.
    
    :param permission_name: The name of the permission that must be granted to 
        the user.
    
    Example::
    
        p = has_permission('hire')
    
    """
    
    message = u'The user must have the "%(permission_name)s" permission'

    def __init__(self, permission_name, **kwargs):
        super(has_permission, self).__init__(**kwargs)
        self.permission_name = permission_name

    def evaluate(self, environ, credentials):
        if credentials and \
           self.permission_name in credentials.get('permissions'):
            return
        self.unmet()


class has_all_permissions(All):
    """
    Check that the current user has been granted all of the specified 
    permissions.
    
    :param permissions: The names of all the permissions that must be
        granted to the user.
    
    Example::
    
        p = has_all_permissions('view-users', 'edit-users')
    
    """
    
    def __init__(self, *permissions, **kwargs):
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_all_permissions, self).__init__(*permission_predicates,
                                                  **kwargs)


class has_any_permission(Any):
    """
    Check that the user has at least one of the specified permissions.
    
    :param permissions: The names of any of the permissions that have to be
        granted to the user.
    
    Example::
    
        p = has_any_permission('manage-users', 'edit-users')
    
    """
    
    message = u"The user must have at least one of the following " \
               "permissions: %(permission_list)s"
    
    def __init__(self, *permissions, **kwargs):
        self.permission_list = ", ".join(permissions)
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_any_permission, self).__init__(*permission_predicates,
                                                **kwargs)


#}
