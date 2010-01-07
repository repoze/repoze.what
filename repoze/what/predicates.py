# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2010, Gustavo Narea <me@gustavonarea.net>.
# Copyright (c) 2009, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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

This is module provides the predicate checkers that were present in the 
original "identity" framework of TurboGears 1, plus others.

"""

from paste.request import parse_formvars, parse_dict_querystring

__all__ = ("Predicate", "CompoundPredicate", "All", "Any", "HasAllPermissions",
    "HasAnyPermission", "HasPermission", "InAllGroups", "InAnyGroup", "InGroup",
    "IsUser", "IsAnonymous", "NotAnonymous", "has_all_permissions",
    "has_any_permission", "has_permission", "in_all_groups", "in_any_group",
    "in_group", "is_user", "is_anonymous", "not_anonymous", "ANONYMOUS",
    "AUTHENTICATED", "PredicateError", "NotAuthorizedError")


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
    
    def __call__(self, request):
        credentials = request.environ.get('repoze.what.credentials', {})
        return self.check(request, credentials)
    
    def check(self, request, credentials):
        return self.is_met(request.environ)
    
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
        :raises NotAuthorizedError: If the predicate is not met (use 
            :meth:`unmet` to raise it).
        
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
        
        .. versionadded:: 1.0.2
        
        .. attention::
            Do not evaluate predicates by yourself using this method. See
            :meth:`check_authorization` and :meth:`is_met`.

        .. warning::
        
            To make your predicates thread-safe, keep in mind that they may
            be instantiated at module-level and then shared among many threads,
            so avoid predicates from being modified after their evaluation. 
            This is, the ``evaluate()`` method should not add, modify or 
            delete any attribute of the predicate.
        
        """
        raise NotImplementedError("Predicate checkers must define their "
                                  "evaluate() method")
    
    def unmet(self, msg=None, **placeholders):
        """
        Raise an exception because this predicate is not met.
        
        :param msg: The error message to be used; overrides the predicate's
            default one.
        :type msg: str
        :raises NotAuthorizedError: If the predicate is not met.
        
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
        
        .. versionadded:: 1.0.2
        
        .. versionchanged:: 1.0.4
            Introduced the ``msg`` argument.
        
        .. attention::
        
            This method should only be called from :meth:`evaluate`.
        
        """
        if msg:
            message = msg
        else:
            message = self.message
        # Let's convert it into unicode because it may be just a class, as a 
        # Pylons' "lazy" translation message:
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
        
        .. versionadded:: 1.0.4
            Backported from :mod:`repoze.what` v2; deprecates
            :func:`repoze.what.authorize.check_authorization`.
        
        """
        logger = environ.get('repoze.who.logger')
        credentials = environ.get('repoze.what.credentials', {})
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
        
        .. versionadded:: 1.0.4
            Backported from :mod:`repoze.what` v2.
        
        """
        credentials = environ.get('repoze.what.credentials', {})
        try:
            self.evaluate(environ, credentials)
            return True
        except NotAuthorizedError:
            return False
    
    def parse_variables(self, environ):
        """
        Return the GET and POST variables in the request, as well as
        ``wsgiorg.routing_args`` arguments.
        
        :param environ: The WSGI environ.
        :return: The GET and POST variables and ``wsgiorg.routing_args``
            arguments.
        :rtype: dict
        
        This is a handy method for request-sensitive predicate checkers.
        
        It will return a dictionary for the POST and GET variables, as well as
        the `wsgiorg.routing_args 
        <http://www.wsgi.org/wsgi/Specifications/routing_args>`_'s 
        ``positional_args`` and ``named_args`` arguments, in the ``post``, 
        ``get``, ``positional_args`` and ``named_args`` items (respectively) of
        the returned dictionary.
        
        For example, if the user submits a form using the POST method to
        ``http://example.com/blog/hello-world/edit_post?wysiwyg_editor=Yes``,
        this method may return::
        
            {
            'post': {'new_post_contents': 'These are the new contents'},
            'get': {'wysiwyg_editor': 'Yes'},
            'named_args': {'post_slug': 'hello-world'},
            'positional_args': (),
            }
        
        But note that the ``named_args`` and ``positional_args`` items depend
        completely on how you configured the dispatcher.
        
        .. versionadded:: 1.0.4
        
        """
        get_vars = parse_dict_querystring(environ) or {}
        try:
            post_vars = parse_formvars(environ, False) or {}
        except KeyError:
            post_vars = {}
        routing_args = environ.get('wsgiorg.routing_args', ([], {}))
        positional_args = routing_args[0] or ()
        named_args = routing_args[1] or {}
        variables = {
            'post': post_vars,
            'get': get_vars,
            'positional_args': positional_args,
            'named_args': named_args}
        return variables
    
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


class CompoundPredicate(Predicate):
    """A predicate composed of other predicates."""
    
    def __init__(self, *predicates, **kwargs):
        super(CompoundPredicate, self).__init__(**kwargs)
        self.predicates = list(predicates)


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
        except NotAuthorizedError:
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


class IsUser(Predicate):
    """
    Check that the authenticated user's username is the specified one.
    
    :param user_name: The required user name.
    :type user_name: str
    
    Example::
    
        p = IsUser('linus')
    
    """
    
    message = u'The current user must be "%(user_name)s"'

    def __init__(self, user_name, **kwargs):
        super(IsUser, self).__init__(**kwargs)
        self.user_name = user_name

    def evaluate(self, environ, credentials):
        if credentials and \
           self.user_name == credentials.get('repoze.what.userid'):
            return
        self.unmet()


class InGroup(Predicate):
    """
    Check that the user belongs to the specified group.
    
    :param group_name: The name of the group to which the user must belong.
    :type group_name: str
    
    Example::
    
        p = InGroup('customers')
    
    """
    
    message = u'The current user must belong to the group "%(group_name)s"'

    def __init__(self, group_name, **kwargs):
        super(InGroup, self).__init__(**kwargs)
        self.group_name = group_name

    def evaluate(self, environ, credentials):
        if credentials and self.group_name in credentials.get('groups'):
            return
        self.unmet()


class InAllGroups(All):
    """
    Check that the user belongs to all of the specified groups.
    
    :param groups: The name of all the groups the user must belong to.
    
    Example::
    
        p = InAllGroups('developers', 'designers')
    
    """
    
    
    def __init__(self, *groups, **kwargs):
        group_predicates = [InGroup(g) for g in groups]
        super(InAllGroups,self).__init__(*group_predicates, **kwargs)


class InAnyGroup(Any):
    """
    Check that the user belongs to at least one of the specified groups.
    
    :param groups: The name of any of the groups the user may belong to.
    
    Example::
    
        p = InAnyGroup('directors', 'hr')
    
    """
    
    message = u"The member must belong to at least one of the following " \
               "groups: %(group_list)s"

    def __init__(self, *groups, **kwargs):
        self.group_list = ", ".join(groups)
        group_predicates = [InGroup(g) for g in groups]
        super(InAnyGroup,self).__init__(*group_predicates, **kwargs)


class IsAnonymous(Predicate):
    """
    Check that the current user is anonymous.
    
    Example::
    
        # The user must be anonymous!
        p = IsAnonymous()
    
    .. versionadded:: 1.0.7
    
    """
    
    message = u"The current user must be anonymous"

    def evaluate(self, environ, credentials):
        if credentials.get("repoze.what.userid"):
            self.unmet()


class NotAnonymous(Predicate):
    """
    Check that the current user has been authenticated.
    
    Example::
    
        # The user must have been authenticated!
        p = NotAnonymous()
    
    """
    
    message = u"The current user must have been authenticated"

    def evaluate(self, environ, credentials):
        if not credentials.get("repoze.what.userid"):
            self.unmet()


class HasPermission(Predicate):
    """
    Check that the current user has the specified permission.
    
    :param permission_name: The name of the permission that must be granted to 
        the user.
    
    Example::
    
        p = HasPermission('hire')
    
    """
    message = u'The user must have the "%(permission_name)s" permission'

    def __init__(self, permission_name, **kwargs):
        super(HasPermission, self).__init__(**kwargs)
        self.permission_name = permission_name

    def evaluate(self, environ, credentials):
        if credentials and \
           self.permission_name in credentials.get('permissions'):
            return
        self.unmet()


class HasAllPermissions(All):
    """
    Check that the current user has been granted all of the specified 
    permissions.
    
    :param permissions: The names of all the permissions that must be
        granted to the user.
    
    Example::
    
        p = HasAllPermissions('view-users', 'edit-users')
    
    """
    
    def __init__(self, *permissions, **kwargs):
        permission_predicates = [HasPermission(p) for p in permissions]
        super(HasAllPermissions, self).__init__(*permission_predicates,
                                                **kwargs)


class HasAnyPermission(Any):
    """
    Check that the user has at least one of the specified permissions.
    
    :param permissions: The names of any of the permissions that have to be
        granted to the user.
    
    Example::
    
        p = HasAnyPermission('manage-users', 'edit-users')
    
    """
    
    message = u"The user must have at least one of the following " \
               "permissions: %(permission_list)s"

    def __init__(self, *permissions, **kwargs):
        self.permission_list = ", ".join(permissions)
        permission_predicates = [HasPermission(p) for p in permissions]
        super(HasAnyPermission,self).__init__(*permission_predicates, **kwargs)


#{ Exceptions


class PredicateError(Exception):
    """
    Former exception raised by a :class:`Predicate` if it's not met.
    
    .. deprecated:: 1.0.4
        Deprecated in favor of :class:`NotAuthorizedError`, for forward
        compatibility with :mod:`repoze.what` v2.
    
    """
    
    # Ugly workaround for Python < 2.6:
    if not hasattr(Exception, '__unicode__'): #pragma: no cover
        def __unicode__(self):
            return unicode(self.args and self.args[0] or '')


class NotAuthorizedError(PredicateError):
    """
    Exception raised by :meth:`Predicate.check_authorization` if the subject 
    is not allowed to access the requested source.
    
    This exception deprecates :class:`PredicateError` as of v1.0.4, but
    extends it to avoid breaking backwards compatibility.
    
    .. versionchanged:: 1.0.4
        This exception was defined at :mod:`repoze.what.authorize` until
        version 1.0.3, but is still imported into that module to keep backwards
        compatibility with v1.X releases -- but it won't work in
        :mod:`repoze.what` v2.
    
    """
    pass


#{ Aliases for nullary predicates


ANONYMOUS = IsAnonymous()
"""
Ready-to-use instance of :class:`IsAnonymous`.

.. versionadded:: 1.1

"""

AUTHENTICATED = NotAnonymous()
"""
Ready-to-use instance of :class:`NotAnonymous`.

.. versionadded:: 1.1

"""


#{ Aliases for backwards compatibility


is_user = IsUser

in_group = InGroup

in_all_groups = InAllGroups

in_any_group = InAnyGroup

is_anonymous = IsAnonymous

not_anonymous = NotAnonymous

has_permission = HasPermission

has_all_permissions = HasAllPermissions

has_any_permission = HasAnyPermission


#}
