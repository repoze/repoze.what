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
Base predicate checkers.

"""

__all__ = ['Predicate', 'CompoundPredicate', 'Not', 'All', 'Any', 'is_user', 
           'not_anonymous', 'NotAuthorizedError']


#{ Predicates


class Predicate(object):
    """
    Generic predicate checker.
    
    This is the base predicate class. It won't do anything useful for you, 
    unless you subclass it.
    
    """
    
    def __init__(self, msg=None):
        """
        Create a predicate and use ``msg`` as the error message if it fails.
        
        :param msg: The error message, if you want to override the default one
            defined by the predicate.
        :type msg: str
        
        You may use the ``msg`` keyword argument with any predicate.
        
        """
        if msg:
            self.message = msg
    
    def evaluate(self, environ, credentials):
        """
        Raise an exception if the predicate is not met.
        
        :param environ: The WSGI environment.
        :type environ: dict
        :param credentials: The :mod:`repoze.what` ``credentials`` dictionary
            as a short-cut.
        :type credentials: dict
        :raise NotImplementedError: When the predicate doesn't define this
            method.
        :raises NotAuthorizedError: If the predicate is not met (use :meth:`unmet`
            to raise it).
        
        This is the method that must be overridden by any predicate checker.
        
        For example, if your predicate is "The current month is the specified
        one", you may define the following predicate checker::
        
            from datetime import date
            from repoze.what.predicates import Predicate
            
            class is_month(Predicate):
                message = 'The current month must be %(right_month)s'
                
                def __init__(self, right_month, **kwargs):
                    self.right_month = right_month
                    super(is_month, self).__init__(**kwargs)
                
                def evaluate(self, environ, credentials):
                    today = date.today()
                    if today.month != self.right_month:
                        # Raise an exception because the predicate is not met.
                        self.unmet()
        
        .. attention::
            Do not evaluate predicates by yourself using this method. See
            :func:`repoze.what.authorize.check_authorization`.

        .. warning::
        
            To make your predicates thread-safe, keep in mind that they may
            be instantiated at module-level and then shared among many threads,
            so avoid predicates from being modified after their evaluation. 
            This is, the ``evaluate()`` method should not add, modify or 
            delete any attribute of the predicate.
        
        """
        raise NotImplementedError
    
    def unmet(self, msg=None, **placeholders):
        """
        Raise an exception because this predicate is not met.
        
        :param msg: The error message to be used; overrides the predicate's
            default one.
        :type msg: str
        :raises NotAuthorizedError: All the time.
        
        ``placeholders`` represent the placeholders for the predicate message.
        The predicate's attributes will also be taken into account while
        creating the message with its placeholders.
        
        For example, if you have a predicate that checks that the current
        month is the specified one, where the predicate message is defined with
        two placeholders as in::
        
            The current month must be %(right_month)s and it is %(this_month)s
        
        and the predicate has an attribute called ``right_month`` which
        represents the expected month, then you can use this method as in::
        
            self.unmet(this_month=this_month)
        
        Then :meth:`unmet` will build the message using the ``this_month``
        keyword argument and the ``right_month`` attribute as the placeholders
        for ``this_month`` and ``right_month``, respectively. So, if
        ``this_month`` equals ``3`` and ``right_month`` equals ``5``,
        the message for the exception to be raised will be::
        
            The current month must be 5 and it is 3
        
        If you have a context-sensitive predicate checker and thus you want
        to change the error message on evaluation, you can call :meth:`unmet`
        as::
        
            self.unmet('%(this_month)s is not a good month',
                       this_month=this_month)
        
        The exception raised would contain the following message::
        
            3 is not a good month
        
        """
        if msg:
            message = msg
        else:
            message = self.message
        # Let's convert it into unicode because it may be just a class, as a 
        # Pylon's "lazy" translation message:
        message = unicode(message)
        # Include the predicate attributes in the placeholders:
        all_placeholders = self.__dict__.copy()
        all_placeholders.update(placeholders)
        raise NotAuthorizedError(message % all_placeholders)

    def check_authorization(self, environ):
        """
        Evaluate the predicate and raise an exception if it's not met.
        
        :param environ: The WSGI environment.
        :raise NotAuthorizedError: If it the predicate is not met.
        
        Example::
        
            >>> from repoze.what.predicates import is_user
            >>> environ = gimme_the_environ()
            >>> p = is_user('gustavo')
            >>> p.check_authorization(environ)
            # ...
            repoze.what.predicates.NotAuthorizedError: The current user must be "gustavo"
        
        """
        logger = environ.get('repoze.what.logger')
        credentials = environ.get('repoze.what.credentials')
        try:
            self.evaluate(environ, credentials)
        except NotAuthorizedError, error:
            logger and logger.info(u'Authorization denied: %s' % error)
            raise
        logger and logger.info('Authorization granted')

    def is_met(self, environ):
        """
        Find whether the predicate is met or not.
        
        :param environ: The WSGI environment.
        :return: Whether the predicate is met or not.
        :rtype: bool
        
        Example::
        
            >>> from repoze.what.predicates import is_user
            >>> environ = gimme_the_environ()
            >>> p = is_user('gustavo')
            >>> p.is_met(environ)
            False
        
        """
        credentials = environ.get('repoze.what.credentials')
        try:
            self.evaluate(environ, credentials)
            return True
        except NotAuthorizedError, error:
            return False


class CompoundPredicate(Predicate):
    """A predicate composed of other predicates."""
    
    def __init__(self, *predicates, **kwargs):
        super(CompoundPredicate, self).__init__(**kwargs)
        self.predicates = predicates


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
    
    def evaluate(self, environ, credentials):
        try:
            self.predicate.evaluate(environ, credentials)
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
    
    def evaluate(self, environ, credentials):
        """
        Evaluate all the predicates it contains.
        
        :param environ: The WSGI environment.
        :param credentials: The :mod:`repoze.what` ``credentials``.
        :raises NotAuthorizedError: If one of the predicates is not met.
        
        """
        for p in self.predicates:
            p.evaluate(environ, credentials)


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
    
    def evaluate(self, environ, credentials):
        """
        Evaluate all the predicates it contains.
        
        :param environ: The WSGI environment.
        :param credentials: The :mod:`repoze.what` ``credentials``.
        :raises NotAuthorizedError: If none of the predicates is met.
        
        """
        errors = []
        for p in self.predicates:
            try:
                p.evaluate(environ, credentials)
                return
            except NotAuthorizedError, exc:
                errors.append(unicode(exc))
        failed_predicates = ', '.join(errors)
        self.unmet(failed_predicates=failed_predicates)


class is_user(Predicate):
    """
    Check that the authenticated user's username is the specified one.
    
    :param user_name: The required user name.
    :type user_name: str
    
    Example::
    
        p = is_user('linus')
    
    """
    
    message = u'The current user must be "%(user_name)s"'

    def __init__(self, user_name, **kwargs):
        super(is_user, self).__init__(**kwargs)
        self.user_name = user_name

    def evaluate(self, environ, credentials):
        if credentials and \
           self.user_name == credentials.get('repoze.what.userid'):
            return
        self.unmet()


class not_anonymous(Predicate):
    """
    Check that the current user has been authenticated.
    
    Example::
    
        # The user must have been authenticated!
        p = not_anonymous()
    
    """
    
    message = u"The current user must have been authenticated"

    def evaluate(self, environ, credentials):
        if not credentials:
            self.unmet()


#{ Exceptions


class NotAuthorizedError(Exception):
    """
    Exception raised by :func:`check_authorization` if the subject is not 
    allowed to access the requested source.
    
    """
    pass


#}
