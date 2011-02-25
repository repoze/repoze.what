# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
# Copyright (c) 2009-2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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
Utilities for :mod:`repoze.what` itself or its plugins.

**They must not be used in the web applications.**

"""

from webob import Request

__all__ = ("setup_request", "forge_request")


def setup_request(environ, userid, group_adapters, permission_adapters,
                  global_control=None):
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
    :param global_control: The global authorization control (e.g., an ACL
        collection).
    :type global_control: :class:`repoze.what.acl._BaseAuthorizationControl`
    
    .. attention::
        This function should only be used in :mod:`repoze.what` itself or
        official/third-party plugins.
    
    """
    original_content_length = environ.get("CONTENT_LENGTH", "-1")
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
    request.environ['repoze.what.positional_args'] = len(request.urlargs)
    request.environ['repoze.what.named_args'] = frozenset(request.urlvars.keys())
    # Injecting the global authorization control, so it can be used by plugins:
    request.environ['repoze.what.global_control'] = global_control
    # Adding a clear request so it can be used to check whether authorization
    # would be granted for a given request, without buiding it from scratch:
    clear_request = request.copy_get()
    clear_request.environ['QUERY_STRING'] = ""
    request.environ['repoze.what.clear_request'] = clear_request
    
    # Before moving on, let's restore the CONTENT_LENGTH reset by WebOb:
    request.environ['CONTENT_LENGTH'] = original_content_length
    return request


def forge_request(environ, path, positional_args, named_args):
    """
    Return a mock request to ``path`` based on ``environ``.
    
    :param environ: The WSGI environment to be used as an starting point.
    :type environ: :class:`dict`
    :param path: The path where the request is supposed to be made; it may
        include the query string.
    :type path: :class:`basestring`
    :param positional_args: The positional arguments to be set in the
        ``wsgiorg.routing_args`` item.
    :type positional_args: :class:`tuple`
    :param named_args: The named arguments to be set in the
        ``wsgiorg.routing_args`` item.
    :type named_args: :class:`dict`
    :return: The new request object.
    :rtype: :class:`webob.Request`
    
    The ``positional_args`` and ``named_args`` must have been given by the
    routing software (e.g., Routes, Selector) for ``path``.
    
    """
    new_request = environ['repoze.what.clear_request'].copy()
    new_request.environ['repoze.what.positional_args'] = len(positional_args)
    new_request.environ['repoze.what.named_args'] = frozenset(named_args)
    new_request.urlargs = positional_args
    new_request.urlvars = named_args
    
    # Extracting the PATH_INFO and the QUERY_STRING (if any):
    if "?" in path:
        (new_request.path_info, new_request.query_string) = path.split("?", 1)
    else:
        new_request.path_info = path
    
    return new_request


class _Credentials(dict):
    """
    The :mod:`repoze.what` credentials dict.
    
    With this kind of objects we'll load the groups and/or permissions only
    when they are necessary, not on every request.
    
    **This must not be used directly outside :mod:`repoze.what` itself.**
    
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
