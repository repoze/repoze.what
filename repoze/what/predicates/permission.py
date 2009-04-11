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
Predicate checkers for the permissions.

"""

from repoze.what.predicates.generic import Predicate, All, Any


__all__ = ['has_all_permissions', 'has_any_permission', 'has_permission']


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

