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
import logging

from zope.interface import implements
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_challenge_decider, \
                                   default_request_classifier
from repoze.who.interfaces import IAuthenticator, IMetadataProvider
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

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


def setup_auth(app, group_adapters, permission_adapters, authenticators, 
               form_plugin=None, form_identifies=True, identifiers=None, 
               challengers=[], mdproviders=[], request_classifier=None,
               challenge_decider=None, log_level=None):
    """
    Setup repoze.who with repoze.what.
    
    @param app: The WSGI application object.
    @param group_adapters: The group source adapters to be used.
    @type group_adapters: C{dict}
    @param permission_adapters: The permission source adapters to be used.
    @type permission_adapters: C{dict}
    @param authenticators: The repoze.who authenticators to be used.
    @param form_plugin: The main repoze.who IChallenger; this is usually a
        login form.
    @param form_identifies: Whether the C{form_plugin} may and should act as
        an repoze.who identifier.
    @param identifiers: Secondary repoze.who IIdentifier plugins, if any.
    @param challengers: Secondary repoze.who challenger plugins, if any.
    @param mdproviders: Secondary repoze.who metadata plugins, if any.
    @param request_classifier: The repoze.who request classifier.
    @param challenge_decider: The repoze.who challenge decider.
    @param log_level: The log level for repoze.who.
    
    """
    authorization = AuthorizationMetadata(group_adapters,
                                          permission_adapters)
    # The following parameters may be customized by passing a list of
    # IIdentifier plugins
    cookie = AuthTktCookiePlugin('secret', 'authtkt')
    if identifiers is None:
        identifiers = [('cookie', cookie)]
    else:
        identifiers.append(('cookie', cookie))
    
    if form_plugin is None:
        from repoze.who.plugins.form import RedirectingFormPlugin
        form = RedirectingFormPlugin('/login', '/login_handler',
                                     '/logout_handler',
                                     rememberer_name='cookie')
    else:
        form = form_plugin
    
    if form_identifies:
        identifiers.insert(0, ('main_identifier', form))
    
    challengers.append(('form', form))
    mdproviders.append(('authorization_md', authorization))
    
    if request_classifier is None:
        request_classifier = default_request_classifier
    
    if challenge_decider is None:
        challenge_decider = default_challenge_decider
    
    if log_level is None:
        log_level = logging.INFO

    log_stream = None
    
    if os.environ.get('AUTH_LOG'):
        import sys
        log_stream = sys.stdout
    
    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        request_classifier,
        challenge_decider,
        log_stream=log_stream,
        log_level=log_level
        )
    return middleware
