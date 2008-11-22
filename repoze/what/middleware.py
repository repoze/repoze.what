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

"""WSGI middleware to configure authorization in TG2 applications."""

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
    """repoze.who metadata provider to load groups and permissions data for
    the current user.
    
    """
    
    implements(IMetadataProvider)
    
    def __init__(self, group_fetchers, permission_fetchers):
        """
        Fetch the groups and permissions of the authenticated user.
        
        @param group_fetchers: Set of adapters that retrieve the known groups
            of the application, each identified by a keyword.
        @type group_fetchers: C{dict}
        @param permission_fetchers: Set of adapters that retrieve the
            permissions for the groups, each identified by a keyword.
        @type permission_fetchers: C{dict}
        
        """
        self.group_fetchers = group_fetchers
        self.permission_fetchers = permission_fetchers
    
    def add_metadata(self, environ, identity):
        """
        Load the groups and permissions of the authenticated user into the
        repoze.who identity.
        
        @param environ: The WSGI environment.
        @param identity: The repoze.who's identity dictionary.
        
        """
        groups = set()
        permissions = set()
        for grp_fetcher in self.group_fetchers.values():
            groups |= set(grp_fetcher.find_sections(identity))
        for group in groups:
            for perm_fetcher in self.permission_fetchers.values():
                permissions |= set(perm_fetcher.find_sections(group))
        identity['groups'] = tuple(groups)
        identity['permissions'] = tuple(permissions)


# TODO: Make this IAuthenticator
class AnonymousAuthorization(object):
    """repoze.who IAuthenticator to grant permissions to anonymous users.
    
    
    
    """
    implements(IAuthenticator)


def setup_auth(app, group_adapters, permission_adapters, authenticators, 
               form_plugin=None, form_identifies=True, identifiers=None, 
               challengers=[], mdproviders=[]):
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
    
    identifiers.append(('repozewhatenv', EnvironmentIdentifier()))
    challengers.append(('form', form))
    mdproviders.append(('authorization', authorization))

    log_stream = None
    
    if os.environ.get('WHO_LOG'):
        import sys
        log_stream = sys.stdout
    
    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream=log_stream,
        log_level=logging.DEBUG
        )
    return middleware
