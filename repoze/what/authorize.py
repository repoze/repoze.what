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
Utilities to implement authorization in TG2.

This is the core module and provides an authorize decorator that reimplements
the functionalities that were present in the original identity framework of 
TurboGears 1.

@todo: The error messages of this module should be translatable.

"""

from pylons import request
from copy import copy
import itertools
from pylons.controllers.util import abort
from tg import flash
from inspect import getargspec, formatargspec
from peak.util.decorators import decorate_assignment

# Inspired by Michele Simionato's decorator library
# http://www.phyast.pitt.edu/~micheles/python/documentation.html

def decorate(func, caller, signature=None):
    """Decorate func with caller."""
    if signature is not None:
        argnames, varargs, kwargs, defaults = signature
    else:
        argnames, varargs, kwargs, defaults = getargspec(func)
    if defaults is None:
        defaults = ()
    parameters = formatargspec(argnames, varargs, kwargs, defaults)[1:-1]
    defval = itertools.count(len(argnames)-len(defaults))
    args = formatargspec(argnames, varargs, kwargs, defaults,
                         formatvalue=lambda value:"=%s" % (
                         argnames[defval.next()]))[1:-1]

    func_str = """
def %s(%s):
  return caller(func, %s)
""" % (func.__name__, parameters, args)

    exec_dict = dict(func=func, caller=caller)
    exec func_str in exec_dict
    newfunc = exec_dict[func.__name__]
    newfunc.__doc__ = func.__doc__
    newfunc.__dict__ = func.__dict__.copy()
    newfunc.__module__ = func.__module__
    if hasattr(func, "__composition__"):
        newfunc.__composition__ = copy(func.__composition__)
    else:
        newfunc.__composition__ = [func]
    newfunc.__composition__.append(newfunc)
    return newfunc


# this code is a direct copy from turbogears1 decorator
# with some small repoze.who adaptations
def weak_signature_decorator(entangler):
    """Decorate function with entangler and change signature to accept
    arbitrary additional arguments.

    Enables alternative decorator syntax for Python 2.3 as seen in PEAK:

        [my_decorator(foo)]
        def baz():
            pass

    Mind, the decorator needs to be a closure for this syntax to work.
    
    """
    def callback(frame, k, v, old_locals):
        return decorate(v, entangler(v), make_weak_signature(v))
    return decorate_assignment(callback, 3)


def make_weak_signature(func):
    """Change signature to accept arbitrary additional arguments."""
    argnames, varargs, kwargs, defaults = getargspec(func)
    if kwargs is None:
        kwargs = "_decorator__kwargs"
    if varargs is None:
        varargs = "_decorator__varargs"
    return argnames, varargs, kwargs, defaults


# this code is a quite complete copy/paste from turbogears 1 identity
class Predicate(object):
    """Generic base class for testing true or false for a condition."""
    def eval_with_object(self, obj, errors=None):
        """Determine whether the predicate is True or False for the given
        object.
        
        """
        raise NotImplementedError

    def append_error_message(self, errors=None):
        if errors is None:
            return
        errors.append(self.error_message % self.__dict__)


class CompoundPredicate(Predicate):
    """A predicate composed of other predicates."""
    def __init__(self, *predicates):
        self.predicates = predicates


class All(CompoundPredicate):
    """A compound predicate that evaluates to true only if all sub-predicates
    evaluate to true for the given input.
    
    """
    def eval_with_object(self, obj, errors=None):
        """Return true if all sub-predicates evaluate to true."""
        for p in self.predicates:
            if not p.eval_with_object(obj, errors):
                return False
        return True


class Any(CompoundPredicate):
    """A compound predicate that evaluates to true if any one of its 
    sub-predicates evaluates to true.
    
    """
    error_message = u"No predicates were able to grant access"

    def eval_with_object(self, obj, errors=None):
        """Return true if any sub-predicate evaluates to true."""
        for p in self.predicates:
            if p.eval_with_object(obj, None):
                return True

        self.append_error_message(errors)
        return False


class IdentityPredicateHelper(object):
    """A mix-in helper class for Identity Predicates."""
    def __nonzero__(self):
        environ = request.environ
        identity = environ.get('repoze.who.identity')
        return self.eval_with_object(identity)


class is_user(Predicate, IdentityPredicateHelper):
    """Predicate for checking if the username matches..."""
    
    error_message = u"Not the good user"

    def __init__(self, user_name):
        self.user_name = user_name

    def eval_with_object(self, obj, errors=None):
        user = None
        identity = request.environ.get('repoze.who.identity')
        if identity:
            userid = identity.get('repoze.who.userid')

        if identity and userid and self.user_name == userid:
            return True

        self.append_error_message(errors)
        return False


class in_group(Predicate, IdentityPredicateHelper):
    """Predicate for requiring a group."""
    
    error_message = u"Not member of group: %(group_name)s"

    def __init__(self, group_name):
        self.group_name = group_name

    def eval_with_object(self, obj, errors=None):
        
        identity = request.environ.get('repoze.who.identity')

        if identity and self.group_name in identity.get('groups'):
            return True

        self.append_error_message(errors)
        return False


class in_all_groups(All, IdentityPredicateHelper):
    """Predicate for requiring membership in a number of groups."""
    
    def __init__(self, *groups):
        group_predicates = [in_group(g) for g in groups]
        super(in_all_groups,self).__init__(*group_predicates)


class in_any_group(Any, IdentityPredicateHelper):
    """Predicate for requiring membership in at least one group"""
    
    error_message = u"Not member of any group: %(group_list)s"

    def __init__(self, *groups):
        self.group_list = ", ".join(groups)
        group_predicates = [in_group(g) for g in groups]
        super(in_any_group,self).__init__(*group_predicates)


class not_anonymous(Predicate, IdentityPredicateHelper):
    """Predicate for checking whether current visitor is anonymous."""
    
    error_message = u"Anonymous access denied"

    def eval_with_object(self, obj, errors=None):
        identity = request.environ.get('repoze.who.identity')

        if not identity:
            self.append_error_message(errors)
            return False

        return True


class has_permission(Predicate, IdentityPredicateHelper):
    """Predicate for checking whether the visitor has a particular 
    permission.
    
    """
    error_message = u"Permission denied: %(permission_name)s"

    def __init__(self, permission_name):
        self.permission_name = permission_name

    def eval_with_object(self, obj, errors=None):
        """Determine whether the visitor has the specified permission."""
        identity = request.environ.get('repoze.who.identity')
        if identity and self.permission_name in identity.get('permissions'):
            return True
        
        self.append_error_message(errors)
        return False


class has_all_permissions(All, IdentityPredicateHelper):
    """Predicate for checking whether the visitor has all permissions."""
    
    def __init__(self, *permissions):
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_all_permissions,self).__init__(*permission_predicates)


class has_any_permission(Any, IdentityPredicateHelper):
    """Predicate for checking whether the visitor has at least one 
    permission.
    
    """
    
    error_message = u"No matching permissions: %(permission_list)s"

    def __init__(self, *permissions):
        self.permission_list = ", ".join(permissions)
        permission_predicates = [has_permission(p) for p in permissions]
        super(has_any_permission,self).__init__(*permission_predicates)


# TODO: does not make sense in a pylons app find some new implementation
#def _remoteHost():
#    try:
#        ips = cherrypy.request.headers.get(
#                "X-Forwarded-For", cherrypy.request.headers.get('Remote-Addr'))
#        return ips.split(",")[-1].strip()
#
#    except:
#        return ""


#def _match_ip(cidr, ip):
#    if not '/' in cidr:
#        return cidr == ip
#
#    else:
#        try:
#            b,m = cidr.split('/')
#            shift = 32 - int(m)
#            a1 = struct.unpack('!L', socket.inet_aton(b))[0] >> shift
#            a2 = struct.unpack('!L', socket.inet_aton(ip))[0] >> shift
#            return a1 == a2
#
#        except:
#            return False


# TODO: reimplement in a pylons context
#class from_host(Predicate, IdentityPredicateHelper):
#    """Predicate for checking whether the visitor's host is an allowed host.
#    Note: We never want to announce what the list of allowed hosts is, because
#    it is way too easy to spoof an IP address in a TCP/IP packet.
#    """
#    error_message = u"Access from this host is not permitted."
#
#    def __init__(self, host):
#        self.host = host
#
#    def eval_with_object(self, obj, errors=None):
#        """Match the visitor's host against the criteria.
#        """
#        ip = _remoteHost()
#        if _match_ip(self.host, ip):
#            return True
#
#        self.append_error_message(errors)
#        return False


# TODO: reimplement in a pylons context
#class from_any_host(Any, IdentityPredicateHelper):
#    """Predicate for checking whether the visitor's host is one of a number of
#    permitted hosts.
#    """
#    error_message = u"Access from this host is not permitted."
#
#    def __init__(self, hosts):
#        host_predicates = [from_host(h) for h in hosts]
#        super(from_any_host, self).__init__(*host_predicates)


def require(predicate, obj=None):
    """Function decorator that checks whether the current user is a member of 
    the groups specified and has the permissions required.
    
    """
    
    def entangle(fn):
        def require(func, self, *args, **kwargs):
            # TODO: populate those errors ... for the moment
            # we don't flash nothing
            errors = []
            environ = request.environ
            identity = environ.get('repoze.who.identity')
            if predicate is None or \
               predicate.eval_with_object(identity, errors):
                return fn(self, *args, **kwargs)

            # if we did not return, then return a 401 to the WSGI stack now
            flash(errors, status="status_warning")
            abort(401)

        fn._require = predicate
        return require

    return weak_signature_decorator(entangle)

