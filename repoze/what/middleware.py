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

__all__ = ['AuthorizationMetadata', 'AnonymousAuthorization', 'setup_auth']


class AuthorizationMetadata(object):
    """
    repoze.who metadata provider to load groups and permissions data for
    the current user.
    
    """
    
    implements(IMetadataProvider)
    
    def __init__(self, group_adapters, permission_adapters):
        """
        Fetch the groups and permissions of the authenticated user.
        
        @param group_adapters: Set of adapters that retrieve the known groups
            of the application, each identified by a keyword.
        @type group_adapters: C{dict}
        @param permission_adapters: Set of adapters that retrieve the
            permissions for the groups, each identified by a keyword.
        @type permission_adapters: C{dict}
        
        """
        self.group_adapters = group_adapters
        self.permission_adapters = permission_adapters
    
    def add_metadata(self, environ, identity):
        """
        Load the groups and permissions of the authenticated user into the
        repoze.who identity.
        
        @param environ: The WSGI environment.
        @param identity: The repoze.who's identity dictionary.
        
        """
        logger = environ.get('repoze.who.logger')
        # Finding the groups and permissions:
        groups = set()
        permissions = set()
        for grp_fetcher in self.group_adapters.values():
            groups |= set(grp_fetcher.find_sections(identity))
        for group in groups:
            for perm_fetcher in self.permission_adapters.values():
                permissions |= set(perm_fetcher.find_sections(group))
        identity['groups'] = tuple(groups)
        identity['permissions'] = tuple(permissions)
        # Logging
        logger and logger.info('User belongs to the following groups: %s' %
                               str(groups))
        logger and logger.info('User has the following permissions: %s' %
                               str(permissions))


# TODO: Make this IAuthenticator
class AnonymousAuthorization(object):
    """repoze.who IAuthenticator to grant permissions to anonymous users.
    
    
    
    """
    implements(IAuthenticator)


def setup_auth(app, group_adapters, permission_adapters, **who_args):
    """
    Setup repoze.who with repoze.what.
    
    Additional keyword arguments will be passed to repoze.who's
    PluggableAuthenticationMiddleware.
    
    @param app: The WSGI application object.
    @param group_adapters: The group source adapters to be used.
    @type group_adapters: C{dict}
    @param permission_adapters: The permission source adapters to be used.
    @type permission_adapters: C{dict}
    
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
