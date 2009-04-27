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


#{ Mapping-related exceptions


class MappingError(WhatException):
    """
    Generic exception used when something goes wrong while mapping a request
    to an ACO.
    
    """
    pass


class NoTargetFoundError(MappingError):
    """
    Exception raised when the request-to-target mapper can't find the target
    from the request.
    
    """
    pass


#}
