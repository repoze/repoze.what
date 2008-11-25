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
    """Generic base class for testing true or false for a condition."""
    
    def __init__(self, msg=None):
        """
        Create a predicate and use C{msg} as the error message if it fails.
        
        @param msg: The error message.
        @type msg: C{str}
        
        """
        if msg:
            self.error_message = msg
    
    def _eval_with_environ(self, environ):
        """
        Determine whether the predicate is True or False for the given
        object.
        
        @raise NotImplementedError: This must be defined by the predicate
            itself.
        
        """
        raise NotImplementedError
    
    def eval_with_environ(self, environ, errors=None):
        """
        Evaluate the predicate and add the relevant error to C{errors} if
        it's False.
        
        """
        if self._eval_with_environ(environ):
            return True
        else:
            if errors is not None:
                errors.append(self.error_message % self.__dict__)
            return False


class CompoundPredicate(Predicate):
    """A predicate composed of other predicates."""
    
    def __init__(self, *predicates, **kwargs):
        super(CompoundPredicate, self).__init__(**kwargs)
        self.predicates = predicates


class All(CompoundPredicate):
    """A compound predicate that evaluates to true only if all sub-predicates
    evaluate to true for the given input.
    
    """
    def eval_with_environ(self, environ, errors=None):
        """Return true if all sub-predicates evaluate to true."""
        for p in self.predicates:
            if not p.eval_with_environ(environ, errors):
                return False
        return True


class Any(CompoundPredicate):
    """A compound predicate that evaluates to true if any one of its 
    sub-predicates evaluates to true.
    
    """
    error_message = u"No predicates were able to grant access"

    def eval_with_environ(self, environ, errors=None):
        """Return true if any sub-predicate evaluates to true."""
        for p in self.predicates:
            if p.eval_with_environ(environ, None):
                return True
        if errors is not None:
            errors.append(self.error_message)
        return False


class is_user(Predicate):
    """Predicate for checking if the username matches..."""
    
    error_message = u"Not the good user"

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
    """Predicate for requiring a group."""
    
    error_message = u"Not member of group: %(group_name)s"

    def __init__(self, group_name, **kwargs):
        super(in_group, self).__init__(**kwargs)
        self.group_name = group_name

    def _eval_with_environ(self, environ):
        identity = environ.get('repoze.who.identity')
        if identity and self.group_name in identity.get('groups'):
            return True
        return False


class in_all_groups(All):
    """Predicate for requiring membership in a number of groups."""
    
    def __init__(self, *groups, **kwargs):
        group_predicates = [in_group(g) for g in groups]
        super(in_all_groups,self).__init__(*group_predicates, **kwargs)


class in_any_group(Any):
    """Predicate for requiring membership in at least one group"""
    
    error_message = u"Not member of any group: %(group_list)s"

    def __init__(self, *groups, **kwargs):
        self.group_list = ", ".join(groups)
        group_predicates = [in_group(g) for g in groups]
        super(in_any_group,self).__init__(*group_predicates, **kwargs)


class not_anonymous(Predicate):
    """Predicate for checking whether current visitor is anonymous."""
    
    error_message = u"Anonymous access denied"

    def _eval_with_environ(self, environ):
        identity = environ.get('repoze.who.identity')
        if not identity:
            return False
        return True


class has_permission(Predicate):
    """Predicate for checking whether the visitor has a particular 
    permission.
    
    """
    error_message = u"Permission denied: %(permission_name)s"

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
    """Predicate for checking whether the visitor has all permissions."""
    
    def __init__(self, *permissions, **kwargs):
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_all_permissions,self).__init__(*permission_predicates,
                                                 **kwargs)


class has_any_permission(Any):
    """Predicate for checking whether the visitor has at least one 
    permission.
    
    """
    
    error_message = u"No matching permissions: %(permission_list)s"

    def __init__(self, *permissions, **kwargs):
        self.permission_list = ", ".join(permissions)
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_any_permission,self).__init__(*permission_predicates,
                                                **kwargs)