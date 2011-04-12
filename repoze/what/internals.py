# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
# Copyright (c) 2009-2011, Gustavo Narea <me@gustavonarea.net>.
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

"""


__all__ = ["setup_request", "forge_request"]


def setup_request(request, global_control, group_adapter):
    """
    Update the ``request`` with the :mod:`repoze.what`-required items.
    
    :param request: The WSGI request object.
    :type request: :class:`webob.Request`
    :param global_control: The global authorization control (e.g., an ACL
        collection).
    :type global_control: :class:`repoze.what.acl._BaseAuthorizationControl` or
        ``None``
    :param group_adapters: The group adapter, if any.
    :type group_adapters: :class:`repoze.what.grooups.BaseGroupAdapter` or
        ``None``
    
    """
    # Injecting the global authorization control and the group adapter, so that
    # they can be used by plugins:
    request.environ['repoze.what.global_control'] = global_control
    request.environ['repoze.what.group_adapter'] = group_adapter
    
    # Adding a clear request so it can be used to check whether authorization
    # would be granted for a given request, without building it from scratch:
    clear_request = request.copy_get()
    clear_request.environ['QUERY_STRING'] = ""
    
    # The routing_args are request-specific, so they should be removed from the
    # clear request:
    if "wsgiorg.routing_args" in clear_request.environ:
        del clear_request.environ['wsgiorg.routing_args']
    
    request.environ['repoze.what.clear_request'] = clear_request


def forge_request(request, path, positional_args, named_args):
    """
    Return a mock request to ``path`` based on ``environ``.
    
    :param request: The request object to be used as an starting point.
    :type request: :class:`webob.Request`
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
    new_request = request.environ['repoze.what.clear_request'].copy()
    new_request.urlargs = positional_args
    new_request.urlvars = named_args
    
    # Extracting the PATH_INFO and the QUERY_STRING (if any):
    if "?" in path:
        (new_request.path_info, new_request.query_string) = path.split("?", 1)
    else:
        new_request.path_info = path
    
    return new_request
