# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
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
Generic utilities for :mod:`repoze.what`.

"""

from repoze.what.exc import NotAuthorizedError

__all__ = ["enforce"]


def enforce(predicate, request, reason=None, denial_handler=None):
    """
    Raise an exception if ``predicate`` is not met within the ``request``.
    
    :param predicate: The :mod:`repoze.what` predicate to be evaluated.
    :type predicate: :class:`repoze.what.predicates.Predicate`
    :param request: The request object.
    :type request: :class:`webob.Request`
    :param reason: The message that explains why authorization would have been
        denied.
    :type reason: :class:`basestring`
    :param denial_handler: The denial handler to be used if authorization is
        denied.
    :raises repoze.what.exc.NotAuthorizedError: If the ``predicate`` is not met.
    
    Sample use::
    
        def do_something(request):
            enforce(InAnyGroup("admins", "dev"), request)
            
            # If reached this point, that means the user belongs to one of the
            # two required groups. Otherwise an exception would've been raised
            # earlier.
            
            return Response("You're an admin and/or a developer!")
    
    """
    if not predicate(request):
        denial = NotAuthorizedError(reason, denial_handler)
        raise denial

