# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, Gustavo Narea <me@gustavonarea.net>.
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
Exceptions raised by :mod:`repoze.what`.

"""


class RepozeWhatException(Exception):
    """Base class for exceptions raised by :mod:`repoze.what`."""
    
    # Ugly workaround for Python < 2.6:
    if not hasattr(Exception, '__unicode__'): #pragma: no cover
        def __unicode__(self):
            return unicode(self.args and self.args[0] or '')


class NotAuthorizedError(RepozeWhatException):
    """
    Exception raised by :meth:`Predicate.check_authorization` if the subject 
    is not allowed to access the requested source.
    
    .. versionchanged:: 1.1.0
        Moved to the newly created :mod:`repoze.what.exc` module, but still
        available from :mod:`repoze.what.predicates`.
    
    """
    
    def __init__(self, reason, handler=None):
        """
        
        :param reason: The reason why authorization was denied.
        :type reason: :class:`basestring`
        :param handler: The **custom** authorization denial to be used.
        :type handler: callable
        
        .. versionchanged:: 1.1.0
            Added the ``handler``.
        
        """
        super(NotAuthorizedError, self).__init__(reason)
        self.handler = handler

