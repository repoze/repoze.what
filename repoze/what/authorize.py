# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008, Gustavo Narea <me@gustavonarea.net>
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

"""Utilities to restrict access based on predicates."""

# We import the predicates just to make repoze.what backwards compatible
# with tg.ext.repoze.who, but they are actually useless here:
from repoze.what.predicates import *


class NotAuthorizedError(Exception):
    """
    Exception raised by :func:`check_authorization` if the subject is not 
    allowed to access the request source.
    
    :param errors: The error messages for the predicates that were not met.
    
    """
    
    def __init__(self, errors):
        super(NotAuthorizedError, self).__init__()
        self.errors = errors
    
    def __str__(self):
        return 'Subject cannot access resource: %s' % '; '.join(self.errors)


def check_authorization(predicate, environ):
    """
    Verify if the current user really can access the requested source.

    :param predicate: The predicate to be evaluated.
    :param environ: The WSGI environment.
    :raise NotAuthorizedError: If it the predicate is not met.
    
    """
    logger = environ.get('repoze.who.logger')
    errors = []
    if predicate and not predicate.eval_with_environ(environ, errors):
        exc = NotAuthorizedError(errors)
        logger and logger.warning(str(exc))
        raise exc
    logger and logger.info('Subject is granted access')
