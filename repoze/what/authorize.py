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
Utilities to implement authorization in action controllers.

This is the core module and provides an authorize decorator that reimplements
the functionalities that were present in the original identity framework of 
TurboGears 1.

@todo: The error messages of this module should be translatable.

"""


#{ Exceptions


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
#class from_host(Predicate):
#    """Predicate for checking whether the visitor's host is an allowed host.
#    Note: We never want to announce what the list of allowed hosts is, because
#    it is way too easy to spoof an IP address in a TCP/IP packet.
#    """
#    error_message = u"Access from this host is not permitted."
#
#    def __init__(self, host):
#        self.host = host
#
#    def _eval_with_environ(self, environ):
#        """Match the visitor's host against the criteria.
#        """
#        ip = _remoteHost()
#        if _match_ip(self.host, ip):
#            return True
#
#        return False


# TODO: reimplement in a pylons context
#class from_any_host(Any):
#    """Predicate for checking whether the visitor's host is one of a number of
#    permitted hosts.
#    """
#    error_message = u"Access from this host is not permitted."
#
#    def __init__(self, hosts):
#        host_predicates = [from_host(h) for h in hosts]
#        super(from_any_host, self).__init__(*host_predicates)


#{ Utilities


def check_authorization(predicate, environ):
    """
    Verify that the C{predicate} grants access to the subject.
    
    @param predicate: The repoze.what predicate.
    @type predicate: L{Predicate}
    @param environ: The WSGI environment.
    @raise NotAuthorizedError: If the predicate rejects access to the subject.
    
    """
    errors = []
    if predicate and not predicate.eval_with_environ(environ, errors):
        raise NotAuthorizedError(errors)


#}
