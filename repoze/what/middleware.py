# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
# Copyright (c) 2009, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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
Utilities to setup authorization by configuring repoze.who's middleware to
use repoze.what.

"""

import os
from logging import getLogger

from webob import Request
from zope.interface import implements
from repoze.who.plugins.testutil import make_middleware
from repoze.who.classifiers import default_challenge_decider, \
                                   default_request_classifier
from repoze.who.interfaces import IMetadataProvider

from repoze.what.predicates import NotAuthorizedError

__all__ = ("AuthorizationMiddleware", "setup_auth", "setup_request")


_LOGGER = getLogger()


class AuthorizationMiddleware(object):
    """
    WSGI middleware for :mod:`repoze.what` authorization.
    
    """
    
    def __init__(self,
                 app,
                 group_adapters=None,
                 permission_adapters=None,
                 remote_user_key="REMOTE_USER",
                 control=None,
                 default_denial_handler=None,
                 ):
        self.app = app
        self.group_adapters = group_adapters
        self.permission_adapters = permission_adapters
        self.remote_user_key = remote_user_key
        self.control = control
        self.default_denial_handler = default_denial_handler
    
    def __call__(self, environ, start_response):
        # TODO: Use all the arguments received in the constructor!
        request = self._setup_request(environ)
        
        return self.app(request.environ, start_response)
    
    def _setup_request(self, environ):
        userid = environ.get(self.remote_user_key)
        return setup_request(environ, userid, self.group_adapters,
                             self.permission_adapters)


class AuthorizationMetadata(object):
    """
    repoze.who metadata provider to load groups and permissions data for
    the current user.
    
    There's no need to include this class in the end-user documentation,
    as there's no reason why they may ever need it... It's only used by
    :func:`setup_auth`.
    
    """
    
    implements(IMetadataProvider)
    
    def __init__(self, group_adapters=None, permission_adapters=None):
        """
        
        :param group_adapters: Set of adapters that retrieve the known groups
            of the application, each identified by a keyword.
        :type group_adapters: dict
        :param permission_adapters: Set of adapters that retrieve the
            permissions for the groups, each identified by a keyword.
        :type permission_adapters: dict
        
        """
        self.group_adapters = group_adapters
        self.permission_adapters = permission_adapters
    
    # IMetadataProvider
    def add_metadata(self, environ, identity):
        """
        Load the groups and permissions of the authenticated user.
        
        It will load such data into the :mod:`repoze.who` ``identity`` and 
        the :mod:`repoze.what` ``credentials`` dictionaries.
        
        :param environ: The WSGI environment.
        :param identity: The :mod:`repoze.who`'s ``identity`` dictionary.
        
        """
        logger = environ.get('repoze.who.logger')
        
        # Setting up the environ for repoze.what:
        userid = identity['repoze.who.userid']
        request = setup_request(environ, userid, self.group_adapters,
                                self.permission_adapters)
        
        # Loading the groups and permissions in the repoze.who identity dict.
        # That's horribly nasty, but still some people insisted on accessing
        # this kind of information directly through repoze.who. But the fact
        # that it's silly is not a reason to break their applications:
        credentials = request.environ['repoze.what.credentials']
        identity['groups'] = credentials['groups']
        identity['permissions'] = credentials['permissions']
        
        # Logging
        logger and logger.info('User belongs to the following groups: %s' %
                               str(credentials['groups']))
        logger and logger.info('User has the following permissions: %s' %
                               str(credentials['permissions']))


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
    :func:`repoze.who.plugins.testutil.make_middleware` -- and
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
    
    .. note::
        If you want to skip authentication while testing your application,
        you should pass the ``skip_authentication`` keyword argument with a
        value that evaluates to ``True``.
    
    .. versionchanged:: 1.0.5
        :class:`repoze.who.middleware.PluggableAuthenticationMiddleware`
        replaced with :func:`repoze.who.plugins.testutil.make_middleware`
        internally.
    
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
    
    skip_authn = who_args.pop('skip_authentication', False)
    middleware = make_middleware(skip_authn, app, **who_args)
    return middleware


def setup_request(environ, userid, group_adapters, permission_adapters):
    """
    Update the WSGI ``environ`` with the :mod:`repoze.what`-required items.
    
    :param environ: The WSGI environ.
    :type environ: :class:`dict`
    :param userid: The user's identificator (if authenticated).
    :type userid: :class:`basestring` or ``None``
    :param group_adapters: The group adapters, if any.
    :type group_adapters: :class:`dict` or ``None``
    :param permission_adapters: The permissions adapters, if any.
    :type permission_adapters: :class:`dict` or ``None``
    
    .. attention::
        This function should only be used in :mod:`repoze.what` itself or
        official/third-party plugins.
    
    """
    request = Request(environ)
    request.environ['repoze.what.credentials'] = _Credentials(
        userid,
        group_adapters,
        permission_adapters,
        )
    request.environ['repoze.what.adapters'] = {
        'groups': group_adapters,
        'permissions': permission_adapters,
        }
    # Setting the arguments:
    routing_args = request.environ.get("wsgiorg.routing_args", ((), {}))
    positional_args = len(routing_args[0])
    named_args = set(routing_args[1].keys() + request.params.keys())
    request.environ['repoze.what.positional_args'] = positional_args
    request.environ['repoze.what.named_args'] = named_args
    
    return request


class _Credentials(dict):
    """
    The :mod:`repoze.what` credentials dict.
    
    With this kind of objects we'll load the groups and/or permissions only
    when they are necessary, not on every request.
    
    """
    
    def __init__(self, userid, group_adapters, permission_adapters):
        self._group_adapters = group_adapters
        self._permission_adapters = permission_adapters
        initial_credentials = {
            'repoze.what.userid': userid,
            'groups': set(),
            'permissions': set(),
            }
        super(_Credentials, self).__init__(**initial_credentials)
        # Keeping track of what has been loaded:
        self._groups_loaded = False
        self._permissions_loaded = False
    
    def __getitem__(self, key):
        if key == "groups" and not self._groups_loaded:
            self._load_groups()
        elif key == "permissions" and not self._permissions_loaded:
            self._load_permissions()
        return super(_Credentials, self).__getitem__(key)
    
    def __setitem__(self, key, value):
        super(_Credentials, self).__setitem__(key, value)
        if key == "groups":
            self._groups_loaded = True
        elif key == "permissions":
            self._permissions_loaded = True
    
    def _load_groups(self):
        groups = set()
        if self._group_adapters:
            for grp_fetcher in self._group_adapters.values():
                groups |= set(grp_fetcher.find_sections(self))
        self['groups'] = groups
    
    def _load_permissions(self):
        permissions = set()
        if self._permission_adapters:
            for group in self['groups']:
                for perm_fetcher in self._permission_adapters.values():
                    permissions |= set(perm_fetcher.find_sections(group))
        self['permissions'] = permissions

