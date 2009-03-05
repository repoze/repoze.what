# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>
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
Utilities to restrict access based on predicates.

.. deprecated:: 1.0.4
    This module won't be available in :mod:`repoze.what` v2. See
    :meth:`repoze.what.predicates.Predicate.check_authorization`.

"""

from warnings import warn

# We import the predicates just to make repoze.what backwards compatible
# with tg.ext.repoze.who, but they are actually useless here:
from repoze.what.predicates import *


def check_authorization(predicate, environ):
    """
    Verify if the current user really can access the requested source.
    
    :param predicate: The predicate to be evaluated.
    :param environ: The WSGI environment.
    :raise NotAuthorizedError: If it the predicate is not met.
    
    .. deprecated:: 1.0.4
        Use :meth:`repoze.what.predicates.Predicate.check_authorization`
        instead.
    
    .. versionchanged:: 1.0.4
        :class:`repoze.what.predicates.PredicateError` used to be the exception
        raised.
    
    """
    msg = 'repoze.what.authorize is deprecated for forward compatibility '\
          'with repoze.what v2; use ' \
          'Predicate.check_authorization(environ) instead'
    warn(msg, DeprecationWarning, stacklevel=2)
    if predicate is not None:
        predicate.check_authorization(environ)
