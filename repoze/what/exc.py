# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
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
:mod:`repoze.what` exceptions.

"""


class WhatException(Exception):
    """
    Base class for the exceptions raised by :mod:`repoze.what` and its
    plugins.
    
    """
    pass


class NotAuthorizedError(WhatException):
    """
    Exception raised when a subject is not allowed to access the requested 
    source.
    
    """
    pass


#{ ACL-related exceptions


class MappingError(WhatException):
    """
    Generic exception used when something goes wrong while mapping a request
    to an ACO.
    
    """
    pass


class NoTargetFoundError(WhatException):
    """
    Exception raised when the request-to-target mapper can't find the target
    from the request.
    
    """
    pass


class ExistingChildrenError(WhatException):
    """
    Exception raised when trying to add an existing subresource or operation
    in a resource.
    
    """
    pass


class NoACOMatchError(WhatException):
    """
    Exception raised when a non-existing subresource or operation is requested
    to a resource.
    
    """
    pass


#{ Source adapters-related exceptions


class AdapterError(WhatException):
    """
    Base exception for problems the source adapters.
    
    It's never raised directly.
    
    """
    pass


class SourceError(AdapterError):
    """
    Exception for problems with the source itself.
    
    .. attention::
        If you are creating a :term:`source adapter`, this is the only
        exception you should raise.
    
    """
    pass


class ExistingSectionError(AdapterError):
    """Exception raised when trying to add an existing group."""
    pass


class NonExistingSectionError(AdapterError):
    """Exception raised when trying to use a non-existing group."""
    pass


class ItemPresentError(AdapterError):
    """
    Exception raised when trying to add an item to a group that already
    contains it.
    
    """
    pass


class ItemNotPresentError(AdapterError):
    """
    Exception raised when trying to remove an item from a group that doesn't
    contain it.
    
    """
    pass


#}
