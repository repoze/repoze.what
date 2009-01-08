# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com> and
#                     Gustavo Narea <me@gustavonarea.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
Utilities to setup authorization by configuring repoze.who's middleware to
use repoze.what.

"""

import os

from zope.interface import implements
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_challenge_decider, \
                                   default_request_classifier
from repoze.who.interfaces import IAuthenticator, IMetadataProvider

__all__ = ['AuthorizationMetadata', 'setup_auth']


class AuthorizationMetadata(object):
    """
    repoze.who metadata provider to load groups and permissions data for
    the current user.
    
    There's no need to include this class in the end-user documentation,
    as there's no reason why they may ever need it... It's only by
    :func:`setup_auth`.
    
    """
    
    implements(IMetadataProvider)
    
    def __init__(self, group_adapters=None, permission_adapters=None):
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
    
    def _find_groups(self, identity):
        """
        Return the groups to which the authenticated user belongs, as well as
        the permissions granted to such groups.
        
        """
        groups = set()
        permissions = set()
        if self.group_adapters is not None:
            # It's using groups/permissions-based authorization
            for grp_fetcher in self.group_adapters.values():
                groups |= set(grp_fetcher.find_sections(identity))
            for group in groups:
                for perm_fetcher in self.permission_adapters.values():
                    permissions |= set(perm_fetcher.find_sections(group))
        return tuple(groups), tuple(permissions)
    
    # IMetadataProvider
    def add_metadata(self, environ, identity):
        """
        Load the groups and permissions of the authenticated user.
        
        It will load such data into the :mod:`repoze.who` ``identity`` and 
        the :mod:`repoze.what` ``credentials`` dictionaries.
        
        :param environ: The WSGI environment.
        :param identity: The :mod:`repoze.who`'s identity dictionary.
        
        """
        logger = environ.get('repoze.who.logger')
        # Finding the groups and permissions:
        groups, permissions = self._find_groups(identity)
        identity['groups'] = groups
        identity['permissions'] = permissions
        # Adding the groups and permissions to the repoze.what identity for
        # forward compatibility:
        if 'repoze.what.credentials' not in environ:
            environ['repoze.what.credentials'] = {}
        environ['repoze.what.credentials']['groups'] = groups
        environ['repoze.what.credentials']['permissions'] = permissions
        # Logging
        logger and logger.info('User belongs to the following groups: %s' %
                               str(groups))
        logger and logger.info('User has the following permissions: %s' %
                               str(permissions))


def setup_auth(app, group_adapters=None, permission_adapters=None, **who_args):
    """
    Setup :mod:`repoze.who` with :mod:`repoze.what` support.
    
    :param app: The WSGI application object.
    :param group_adapters: The group source adapters to be used.
    :type group_adapters: dict
    :param permission_adapters: The permission source adapters to be used.
    :type permission_adapters: dict
    :param who_args: Authentication-related keyword arguments to be passed to
        :mod:`repoze.who`.
    :return: The WSGI application with authentication and authorization
        middleware.
    
    .. tip::
        If you are looking for an easier way to get started, you may want to
        use :mod:`the quickstart plugin <repoze.what.plugins.quickstart>` and
        its :func:`setup_sql_auth() 
        <repoze.what.plugins.quickstart.setup_sql_auth>` function.
    
    You must define the ``group_adapters`` and ``permission_adapters``
    keyword arguments if you want to use the groups/permissions-based
    authorization pattern.
    
    Additional keyword arguments will be passed to
    :class:`repoze.who.middleware.PluggableAuthenticationMiddleware` -- and
    among those keyword arguments, you *must* define at least the identifier(s),
    authenticator(s) and challenger(s) to be used. For example::
        
        from repoze.who.plugins.basicauth import BasicAuthPlugin
        from repoze.who.plugins.htpasswd import HTPasswdPlugin, crypt_check
        
        from repoze.what.middleware import setup_auth
        from repoze.what.plugins.xml import XMLGroupsAdapter
        from repoze.what.plugins.ini import INIPermissionAdapter

        # Defining the group adapters; you may add as much as you need:
        groups = {'all_groups': XMLGroupsAdapter('/path/to/groups.xml')}

        # Defining the permission adapters; you may add as much as you need:
        permissions = {'all_perms': INIPermissionAdapter('/path/to/perms.ini')}

        # repoze.who identifiers; you may add as much as you need:
        basicauth = BasicAuthPlugin('Private web site')
        identifiers = [('basicauth', basicauth)]

        # repoze.who authenticators; you may add as much as you need:
        htpasswd_auth = HTPasswdPlugin('/path/to/users.htpasswd', crypt_check)
        authenticators = [('htpasswd', htpasswd_auth)]

        # repoze.who challengers; you may add as much as you need:
        challengers = [('basicauth', basicauth)]

        app_with_auth = setup_auth(
            app,
            groups,
            permissions,
            identifiers=identifiers,
            authenticators=authenticators,
            challengers=challengers)
    
    .. attention::
        Keep in mind that :mod:`repoze.who` must be configured `through`
        :mod:`repoze.what` for authorization to work.
    
    """
    authorization = AuthorizationMetadata(group_adapters,
                                          permission_adapters)
    
    if 'mdproviders' not in who_args:
        who_args['mdproviders'] = []
    
    who_args['mdproviders'].append(('authorization_md', authorization))
    
    if 'classifier' not in who_args:
        who_args['classifier'] = default_request_classifier
    
    if 'challenge_decider' not in who_args:
        who_args['challenge_decider'] = default_challenge_decider
    
    if os.environ.get('AUTH_LOG'):
        import sys
        who_args['log_stream'] = sys.stdout
    
    middleware = PluggableAuthenticationMiddleware(app, **who_args)
    return middleware
