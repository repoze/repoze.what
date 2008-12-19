# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com> and
#                     Gustavo Narea <me@gustavonarea.net>
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

"""
Built-in predicate checkers.

This is module provides the predicate checkers that were present in the 
original "identity" framework of TurboGears 1, plus others.

"""

__all__ = ['Predicate', 'CompoundPredicate', 'All', 'Any', 
           'has_all_permissions', 'has_any_permission', 'has_permission', 
           'in_all_groups', 'in_any_group', 'in_group', 'is_user', 
           'not_anonymous']


class Predicate(object):
    """
    Generic base class for testing true or false for a condition.
    
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
        self.error = ''
    
    def _eval_with_environ(self, environ):
        """
        Determine whether the predicate is True or False for the given
        object.
        
        :param environ: The WSGI environment.
        :return: Whether the predicate is met or not.
        :rtype: bool
        :raise NotImplementedError: This must be defined by the predicate
            itself.
        
        """
        raise NotImplementedError
    
    def eval_with_environ(self, environ, errors=None):
        """
        Evaluate the predicate and add the relevant error to ``errors`` if
        it's ``False``.
        
        :param environ: The WSGI environment.
        :param errors: List of previous authorization errors.
        :type errors: list
        :return: Whether the predicate is met or not.
        :rtype: bool
        
        """
        if self._eval_with_environ(environ):
            return True
        else:
            self.error = self.message % self.__dict__
            if errors is not None:
                errors.append(self.error)
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
    
    def _eval_with_environ(self, environ):
        return not self.predicate.eval_with_environ(environ, None)


class All(CompoundPredicate):
    """
    Check that all of the specified predicates are met.
    
    :param predicates: All of the predicates that must be met.
    
    Example::
    
        # Grant access if the current month is July and the user belongs to
        # the human resources group.
        p = All(is_month(7), in_group('hr'))
    
    """
    def eval_with_environ(self, environ, errors=None):
        """Return true if all sub-predicates evaluate to true."""
        for p in self.predicates:
            if not p.eval_with_environ(environ, errors):
                return False
        return True


class Any(CompoundPredicate):
    """
    Check that at least one of the specified predicates is met.
    
    :param predicates: Any of the predicates that must be met.
    
    Example::
    
        # Grant access if the currest user is Richard Stallman or Linus
        # Torvalds.
        p = Any(is_user('rms'), is_user('linus'))
    
    """
    message = u"At least one predicate must be met"

    def eval_with_environ(self, environ, errors=None):
        """Return true if any sub-predicate evaluates to true."""
        for p in self.predicates:
            if p.eval_with_environ(environ, None):
                return True
        if errors is not None:
            errors.append(self.message)
        return False


class is_user(Predicate):
    """
    Check that the authenticated user's username is the specified one.
    
    :param user_name: The required user name.
    :type user_name: str
    
    Example::
    
        p = is_user('linus')
    
    """
    
    message = u"The current user must be %(user_name)s"

    def __init__(self, user_name, **kwargs):
        super(is_user, self).__init__(**kwargs)
        self.user_name = user_name

    def _eval_with_environ(self, environ):
        user = None
        identity = environ.get('repoze.who.identity')
        if identity:
            userid = identity.get('repoze.who.userid')

        if identity and userid and self.user_name == userid:
            return True

        return False


class in_group(Predicate):
    """
    Check that the user belongs to the specified group.
    
    :param group_name: The name of the group to which the user must belong.
    :type group_name: str
    
    Example::
    
        p = in_group('customers')
    
    """
    
    message = u"The current user must belong to the group %(group_name)s"

    def __init__(self, group_name, **kwargs):
        super(in_group, self).__init__(**kwargs)
        self.group_name = group_name

    def _eval_with_environ(self, environ):
        identity = environ.get('repoze.who.identity')
        if identity and self.group_name in identity.get('groups'):
            return True
        return False


class in_all_groups(All):
    """
    Check that the user belongs to all of the specified groups.
    
    :param groups: The name of all the groups the user must belong to.
    
    Example::
    
        p = in_all_groups('developers', 'designers')
    
    """
    
    
    def __init__(self, *groups, **kwargs):
        group_predicates = [in_group(g) for g in groups]
        super(in_all_groups,self).__init__(*group_predicates, **kwargs)


class in_any_group(Any):
    """
    Check that the user belongs to at least one of the specified groups.
    
    :param groups: The name of any of the groups the user may belong to.
    
    Example::
    
        p = in_any_group('directors', 'hr')
    
    """
    
    message = u"The member must belong to at least one of the following " \
               "groups: %(group_list)s"

    def __init__(self, *groups, **kwargs):
        self.group_list = ", ".join(groups)
        group_predicates = [in_group(g) for g in groups]
        super(in_any_group,self).__init__(*group_predicates, **kwargs)


class not_anonymous(Predicate):
    """
    Check that the current user has been authenticated.
    
    Example::
    
        # The user must have been authenticated!
        p = not_anonymous()
    
    """
    
    message = u"The current user must have been authenticated"

    def _eval_with_environ(self, environ):
        identity = environ.get('repoze.who.identity')
        if not identity:
            return False
        return True


class has_permission(Predicate):
    """
    Check that the current user has the specified permission.
    
    :param permission_name: The name of the permission that must be granted to 
        the user.
    
    Example::
    
        p = has_permission('hire')
    
    """
    message = u'The user must have the "%(permission_name)s" permission'

    def __init__(self, permission_name, **kwargs):
        super(has_permission, self).__init__(**kwargs)
        self.permission_name = permission_name

    def _eval_with_environ(self, environ):
        """Determine whether the visitor has the specified permission."""
        identity = environ.get('repoze.who.identity')
        if identity and self.permission_name in identity.get('permissions'):
            return True
        return False


class has_all_permissions(All):
    """
    Check that the current user has been granted all of the specified 
    permissions.
    
    :param permissions: The names of all the permissions that must be
        granted to the user.
    
    Example::
    
        p = has_all_permissions('view-users', 'edit-users')
    
    """
    
    def __init__(self, *permissions, **kwargs):
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_all_permissions,self).__init__(*permission_predicates,
                                                 **kwargs)


class has_any_permission(Any):
    """
    Check that the user has at least one of the specified permissions.
    
    :param permissions: The names of any of the permissions that have to be
        granted to the user.
    
    Example::
    
        p = has_any_permission('manage-users', 'edit-users')
    
    """
    
    message = u"The user must have at least one of the following " \
               "permissions: %(permission_list)s"

    def __init__(self, *permissions, **kwargs):
        self.permission_list = ", ".join(permissions)
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_any_permission,self).__init__(*permission_predicates,
                                                **kwargs)
