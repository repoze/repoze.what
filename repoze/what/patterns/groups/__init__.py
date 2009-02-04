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

from repoze.what.credentials import BaseCredentialProvider

from repoze.what.patterns.groups.predicates import in_group, has_permission, \
                                                   in_all_groups, \
                                                   has_all_permissions, \
                                                   in_any_group, \
                                                   has_any_permission


__all__ = ['in_group', 'has_permission', 'in_all_groups', 
           'has_all_permissions', 'in_any_group', 'has_any_permission',
           'GroupCredentialsProvider']


class GroupCredentialsProvider(BaseCredentialProvider):
    """
    :mod:`repoze.what` credentials provider for the groups and permissions of
    the current user.
    
    """
    
    provider_name = 'group'
    
    credentials_loaded = ['groups', 'permissions']
    
    def __init__(self, group_adapters, permission_adapters=None):
        """
        Fetch the groups and permissions of the authenticated user.
        
        :param group_adapters: Set of adapters that retrieve the known groups
            of the application, each identified by a keyword.
        :type group_adapters: dict
        :param permission_adapters: Set of adapters that retrieve the
            permissions for the groups, each identified by a keyword.
        :type permission_adapters: dict
        
        """
        self.group_adapters = group_adapters
        self.permission_adapters = permission_adapters
    
    def _find_groups(self, credentials):
        """
        Return the groups to which the authenticated user belongs, as well as
        the permissions granted to such groups (if any).
        
        """
        groups = set()
        permissions = set()
        for grp_fetcher in self.group_adapters.values():
            groups |= set(grp_fetcher.find_sections(credentials))
        if self.permission_adapters:
            # Groups are not granted permissions
            for group in groups:
                for perm_fetcher in self.permission_adapters.values():
                    permissions |= set(perm_fetcher.find_sections(group))
        return tuple(groups), tuple(permissions)
    
    # BaseCredentialProvider
    def load_credentials(self, environ, credentials):
        """
        Load the groups and permissions of the current user.
        
        It will load such data into the :mod:`repoze.what` ``credentials``
        dictionary.
        
        :param environ: The WSGI environment.
        :param credentials: The :mod:`repoze.what`'s ``credentials`` dict.
        
        """
        logger = environ.get('repoze.what.logger')
        # Finding the groups and permissions:
        groups, permissions = self._find_groups(credentials)
        credentials['groups'] = groups
        credentials['permissions'] = permissions
        # TODO: Adapters should not be loaded here. The middleware should
        # load this credentials provider into the environ instead.
        environ['repoze.what.adapters'] = {
            'groups': self.group_adapters,
            'permissions': self.permission_adapters}
        # Logging
        logger and logger.info('User belongs to the following groups: %s' %
                               str(groups))
        logger and logger.info('User has the following permissions: %s' %
                               str(permissions))
