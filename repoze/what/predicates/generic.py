# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
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
Generic predicate checkers.

"""

from repoze.what.predicates.base import Predicate, CompoundPredicate, \
                                        NotAuthorizedError

__all__ = ['Not', 'All', 'Any']


class Not(Predicate):
    """
    Negate the specified predicate.
    
    :param predicate: The predicate to be negated.
    
    Example::
    
        # The user *must* be anonymous:
        p = Not(not_anonymous())
    
    """
    message = u"The condition must not be met"

    def __init__(self, predicate, **kwargs):
        super(Not, self).__init__(**kwargs)
        self.predicate = predicate
    
    def evaluate(self, userid, request, helpers):
        try:
            self.predicate.evaluate(userid, request, helpers)
        except NotAuthorizedError, error:
            return
        self.unmet()


class All(CompoundPredicate):
    """
    Check that all of the specified predicates are met.
    
    :param predicates: All of the predicates that must be met.
    
    Example::
    
        # Grant access if the current month is July and the user belongs to
        # the human resources group.
        p = All(is_month(7), in_group('hr'))
    
    """
    
    def evaluate(self, userid, request, helpers):
        """Evaluate all the predicates it contains."""
        for p in self.predicates:
            p.evaluate(userid, request, helpers)


class Any(CompoundPredicate):
    """
    Check that at least one of the specified predicates is met.
    
    :param predicates: Any of the predicates that must be met.
    
    Example::
    
        # Grant access if the currest user is Richard Stallman or Linus
        # Torvalds.
        p = Any(is_user('rms'), is_user('linus'))
    
    """
    message = u"At least one of the following predicates must be met: " \
               "%(failed_predicates)s"
    
    def evaluate(self, userid, request, helpers):
        """Evaluate all the predicates it contains."""
        errors = []
        for p in self.predicates:
            try:
                p.evaluate(userid, request, helpers)
                return
            except NotAuthorizedError, exc:
                errors.append(unicode(exc))
        failed_predicates = ', '.join(errors)
        self.unmet(failed_predicates=failed_predicates)
