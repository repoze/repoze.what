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
    Exception raised when the subject is not allowed to access the 
    resource.
    
    """
    
    def __init__(self, errors):
        super(NotAuthorizedError, self).__init__()
        self.errors = errors
    
    def __str__(self):
        return 'Subject cannot access resource: %s' % '; '.join(self.errors)


def check_authorization(predicate, environ):
    """
    Verify that the C{predicate} grants access to the subject.
    
    @param predicate: The repoze.what predicate.
    @type predicate: L{Predicate}
    @param environ: The WSGI environment.
    @raise NotAuthorizedError: If the predicate rejects access to the subject.
    
    """
    logger = environ.get('repoze.who.logger')
    errors = []
    if predicate and not predicate.eval_with_environ(environ, errors):
        exc = NotAuthorizedError(errors)
        logger and logger.warning(str(exc))
        raise exc
    logger and logger.info('Subject is granted access')
