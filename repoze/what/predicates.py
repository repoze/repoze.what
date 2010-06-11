# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2010, Gustavo Narea <me@gustavonarea.net>.
# Copyright (c) 2009, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
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
Built-in predicate checkers.

"""
from webob import Request


__all__ = ["Predicate", "Not", "All", "Any"]


class Predicate(object):
    """
    Generic predicate checker.
    
    This is the base predicate class. It won't do anything useful for you, 
    unless you subclass it.
    
    """
    
    def __call__(self, request):
        """
        Report whether the predicate is met.
        
        :param request: The WSGI environment or a WebOb request object.
        :type request: :class:`dict` or :class:`webob.Request`
        :return: Whether the predicate is met.
        :rtype: :class:`bool` or ``None``
        
        **Predicate checkers should NOT override this method.**
        
        It returns ``None`` if and only if there was a critical error while
        processing the predicate AND said error will occur **unequivocally** in
        the routine being covered by the predicate.
        
        For example, if you have a blogging system and wrote a predicate which
        checks whether the article requested is hidden, it must return ``None``
        when a non-existing article is requested -- It must be up to your
        controller action to return a 404 response.
        
        """
        if not isinstance(request, Request):
            # It was a WSGI environment dictionary:
            request = Request(request)
        credentials = request.environ.get('repoze.what.credentials', {})
        return self.check(request, credentials)
    
    def check(self, request, credentials):
        """
        Report whether the predicate is met.
        
        :param request: The request object.
        :type request: :class:`webob.Request`
        :param credentials: The repoze.what credentials.
        :type credentials: :class:`repoze.what.internals._Credentials`
        :return: Whether the predicate is met.
        :rtype: :class:`bool` or ``None``
        
        **Predicate checkers MUST override this method.**
        
        It must return ``None`` if and only if there was a critical error while
        processing the predicate AND said error will occur **unequivocally** in
        the routine being covered by the predicate.
        
        For example, if you have a blogging system and wrote a predicate which
        checks whether the article requested is hidden, it must return ``None``
        when a non-existing article is requested -- It's up to your controller
        action to return a 404 response.
        
        On the contrary, if your predicate checks whether the user's IP address
        is a given one, for example, but the ``REMOTE_ADDR`` variable is not
        set, then it must return ``False`` instead of ``None``: No matter what
        his IP address is, the point is that it may not the one we expect and
        the controller action wouldn't necessarily fail because of the absence
        of this value.
        
        """
        raise NotImplementedError("Predicate checker %r must override the "
                                  "check() method" % self.__class__)
    
    #{ Boolean operations
    
    def __invert__(self):
        """
        Return the negation for the current predicate.
        
        :rtype: :class:`Not`
        
        """
        return Not(self)
    
    def __and__(self, other):
        """
        Merge this predicate and ``other`` into a :class:`All` predicate and
        return the result.
        
        :rtype: :class:`All`
        
        """
        return self._make_compound(All, other)
    
    def __or__(self, other):
        """
        Merge this predicate and ``other`` into a :class:`Any` predicate and
        return the result.
        
        :rtype: :class:`Any`
        
        """
        return self._make_compound(Any, other)
    
    def _make_compound(self, klass, other):
        if not isinstance(other, Predicate):
            return NotImplemented
        
        if isinstance(self, klass):
            predicates = self.predicates + [other]
            predicate = klass(*predicates)
        else:
            predicate = klass(self, other)
        
        return predicate
    
    #}


class _CompoundPredicate(Predicate):
    """A predicate composed of other predicates."""
    
    def __init__(self, *predicates):
        self.predicates = list(predicates)
        super(_CompoundPredicate, self).__init__()


class Not(Predicate):
    """
    Negate the specified predicate.
    
    :param predicate: The predicate to be negated.
    
    Example::
    
        # The user *must* be anonymous:
        p = Not(NotAnonymous())
    
    """

    def __init__(self, predicate):
        self.predicate = predicate
        super(Not, self).__init__()
    
    def check(self, request, credentials):
        is_met = self.predicate.check(request, credentials)
        # If the predicate evaluation was undeterminate, leave it as is:
        if is_met is not None:
            is_met = not is_met
        return is_met


class All(_CompoundPredicate):
    """
    Check that all of the specified predicates are met.
    
    :param predicates: All of the predicates that must be met.
    
    Example::
    
        # Grant access if the current month is July and the user belongs to
        # the human resources group.
        p = All(IsMonth(7), InGroup('hr'))
    
    This predicate is met when all the inner predicates are met, unmet when at
    least one of them is unmet and indeterminate for the rest of the situation.
    
    """
    
    def check(self, request, credentials):
        met_predicates = 0
        any_indeterminate = False
        any_unmet = False
        
        for predicate in self.predicates:
            evaluation_result = predicate.check(request, credentials)
            
            if evaluation_result is True:
                met_predicates += 1
            elif evaluation_result is None:
                any_indeterminate = True
            elif evaluation_result is False:
                any_unmet = True
                break
        
        if any_indeterminate and not any_unmet:
            # The predicates were indeterminate, although some of them might
            # have been met -- Which is not enough, they all must be met.
            met = None
        else:
            # Either all the predicates were met, or at least one of them was
            # definitely not met.
            met = len(self.predicates) == met_predicates
        
        return met


class Any(_CompoundPredicate):
    """
    Check that at least one of the specified predicates is met.
    
    :param predicates: Any of the predicates that must be met.
    
    Example::
    
        # Grant access if the currest user is Richard Stallman or Linus
        # Torvalds.
        p = Any(IsUser("rms"), IsUser("linus"))
    
    This predicate is met when at least one of the inner predicates is met and
    unmet when all of the inner predicates are unmet. If none of the predicates
    are met and also there's at least one indeterminate predicate, this
    predicate is indeterminate.
    
    """
    
    def check(self, request, credentials):
        one_met = False
        any_indeterminate = False
        
        for predicate in self.predicates:
            evaluation_result = predicate.check(request, credentials)
            if evaluation_result == True:
                one_met = True
                break
            elif evaluation_result is None:
                any_indeterminate = True
        
        if any_indeterminate and not one_met:
            met = None
        else:
            met = one_met
        
        return met
