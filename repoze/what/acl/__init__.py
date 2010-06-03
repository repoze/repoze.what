# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, 2degrees Limited <gnarea@tech.2degreesnetwork.com>.
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
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
Basic Access Control Lists implementation.

"""

from repoze.what.predicates import Not, NotAuthorizedError
from repoze.what._utils import normalize_path

__all__ = ("ACL", "ACLCollection", "AuthorizationDecision")


class _BaseAuthorizationControl(object):
    """
    Base class for authorization controls.
    
    """
    
    def __init__(self, allow_by_default=None, default_denial_handler=None):
        """
        
        :param default_final_decision: The default authorization decision.
        :type default_final_decision: :class:`bool`
        :param default_denial_handler: The default authorization denial handler.
        :type default_denial_handler: :class:`object`
        
        """
        self._default_denial_handler = default_denial_handler
        # Let's set a default final decision, if possible:
        if allow_by_default is None:
            self._default_final_decision = None
        else:
            self._default_final_decision = AuthorizationDecision(
                allow_by_default,
                None,
                None,
                )
    
    def decide_authorization(self, environ, object_=None):
        """
        Report whether authorization is granted to the request described by
        ``environ``.
        
        :param environ: The WSGI environment.
        :type environ: :class:`dict`
        :param object_: The object that is to be accessed (usually a controller
            action).
        :return: Whether authorization is granted.
        :rtype: :class:`bool`
        
        """
        raise NotImplementedError


class ACL(_BaseAuthorizationControl):
    """
    Access Control List.
    
    """
    
    def __init__(self, base_path="", allow_by_default=None,
                 default_denial_handler=None):
        """
        Let this ACL cover only ``base_path``.
        
        :param base_path: The path where this ACL is applicable.
        :type base_path: :class:`basestring`
        :param allow_by_default: The default authorization decision.
        :type allow_by_default: :class:`bool`
        :param default_denial_handler: The default authorization denial handler.
        :type default_denial_handler: :class:`object`
        
        If ``base_path`` is an empty string or a slash, that means this ACL
        is global.
        
        When a request in not within the scope of any ACE in the ACL,
        ``allow_by_default`` will be used as the decision (i.e., allow or
        deny: ``True`` or ``False``). By default there's no decision.
        
        When the final decision is to deny authorization but no denial handler
        was set, ``default_denial_handler`` will be used. There's no default
        denial handler.
        
        """
        self._base_path = normalize_path(base_path)
        # The ACEs can't be a dictionary because order matters. It will be a
        # list made of quadruples where the first element is the protected
        # object/path, the second one is its set of ACEs, the third one is
        # a boolean which specifies where it's a path and the fourth one is the
        # denial handler to be used (if authorization is to be denied).
        self._aces = []
        super(ACL, self).__init__(allow_by_default, default_denial_handler)
    
    #{ ACE management
    
    def allow(self, path_or_object, predicate=None, reason=None,
              propagate=True, force_inclusion=False):
        """
        Grant access on ``path_or_object`` if the ``predicate`` is met.
        
        :param path_or_object: The path or the object to be covered by this ACE.
        :type path_or_object: :class:`basestring`, callable or a collection of
            them
        :param predicate: The :mod:`repoze.what` predicate that must be met
            for this ACE to be taken into account.
        :type predicate: :class:`repoze.what.predicates.Predicate`
        :param reason: The reason why authorization is granted.
        :type reason: :class:`basestring`
        :param propagate: Whether this ACE should be propagated to any path
            which begins with this one (as long as this ACE covers a path).
        :type propagate: :class:`bool`
        
        If no ``predicate`` is set, then the ACE will always be taken into
        account.
        
        """
        self._add_ace(path_or_object, predicate, True, None, reason, propagate,
                      force_inclusion)
    
    def deny(self, path_or_object, predicate=None, denial_handler=None,
             reason=None, propagate=True, force_inclusion=False):
        """
        Deny access on ``path_or_object`` if the ``predicate`` is met.
        
        :param path_or_object: The path or the object to be covered by this ACE.
        :type path_or_object: :class:`basestring`, callable or a collection of
            them
        :param predicate: The :mod:`repoze.what` predicate that must be met
            for this ACE to be taken into account.
        :type predicate: :class:`repoze.what.predicates.Predicate`
        :param denial_handler: The denial handler to be used if this is the
            final ACE (i.e., authorization is to be denied).
        :param reason: The reason why authorization is granted.
        :type reason: :class:`basestring`
        :param propagate: Whether this ACE should be propagated to any path
            which begins with this one (as long as this ACE covers a path).
        :type propagate: :class:`bool`
        :param propagate: Whether this ACE should be enforced to any path
            which begins with this one (as long as its predicate is met).
        :type propagate: :class:`bool`
        
        If no ``predicate`` is set, then the ACE will always be taken into
        account.
        
        """
        self._add_ace(path_or_object, predicate, False, denial_handler, reason,
                      propagate, force_inclusion)
    
    def _add_ace(self, path_or_object, predicate, allow, denial_handler, reason,
                 propagate, force_inclusion):
        # If we've been given multiple Access Control Objects at once, we have
        # to add them one by one:
        if hasattr(path_or_object, "__iter__"):
            for aco in path_or_object:
                self._add_ace(aco, predicate, allow, denial_handler, reason,
                              propagate, force_inclusion)
            return
        
        is_path = isinstance(path_or_object, basestring)
        if is_path:
            # We're protecting a path, so we must preppend the base path:
            path_or_object = normalize_path(self._base_path + path_or_object)
        # Adding this ACE:
        ace = _ACE(predicate, allow, reason, propagate, force_inclusion)
        self._aces.append((path_or_object, ace, is_path, denial_handler))
    
    #}
    
    # _BaseAuthorizationControl
    def decide_authorization(self, environ, object_=None):
        """
        Report whether authorization is granted to the request described by
        ``environ``.
        
        :param environ: The WSGI environment.
        :type environ: :class:`dict`
        :param object_: The object that is to be accessed (usually a controller
            action).
        :return: Whether authorization is granted.
        :rtype: :class:`bool`
        
        If there is an ACE for ``object_``, it will be the final decision and
        all the other ACEs will be ignored.
        
        """
        final_decision = self._default_final_decision
        path_info = normalize_path(environ['PATH_INFO'])
        
        # Let's keep track of the longest path match so far, so we can ignore
        # shorter matches:
        tracker = _MatchTracker()
        
        # Let's iterate over every ACE to check which of them are applicable to
        # this request (the one described by ``environ`` and the ``object``).
        for (aco, ace, is_path, denial_handler) in self._aces:
            
            # Checking the scope of the current ACE:
            if (is_path and not
                tracker.is_within_scope(aco, ace.propagate, ace.force_inclusion,
                                        path_info)
                ):
                # This ACE covers a path, but the current request is not
                # within its scope.
                continue
            elif not is_path and aco != object_:
                # This ACE covers an object, but it's not this one.
                continue
            
            # The current path/object IS within the scope of this ACE.
            ace_participates = ace.can_participate(environ)
            if ace_participates is False:
                # However, it cannot participate because other conditions
                # are not met.
                continue
            
            # If the predicate was indeterminate, we cannot take the ACE's
            # .allow value:
            if ace_participates is None:
                allow = None
            else:
                allow = ace.allow
            
            # The current ACE *must* be taken into account:
            final_decision = AuthorizationDecision(allow, ace.reason,
                                                   denial_handler)
            
            # Updating the tracker:
            if is_path:
                # This ACE covered a path. Let's update the longest match so
                # far:
                tracker.set_longest_path(aco)
                
                if ace.force_inclusion:
                    tracker.forced_ace_found = True
                    break
            else:
                # This ACE covered the object itself. We must let the tracker
                # know so from now on we'll only check ACEs applied to this
                # object, ignoring paths.
                tracker.object_ace_found = True
        
        # If there's a decision made and authorization has been denied with no
        # denial handler, let's use the default one (if any). Also let's attach
        # the tracker used:
        if final_decision is not None:
            final_decision.set_denial_handler(self._default_denial_handler)
            final_decision.set_match_tracker(tracker)
        
        return final_decision
    
    def __repr__(self):
        return "<ACL base=%s aces=%s at 0x%x>" % \
               (self._base_path, len(self._aces), id(self))


class ACLCollection(_BaseAuthorizationControl):
    """
    Collection of ACLs.
    
    """
    
    def __init__(self, allow_by_default=None,
                 default_denial_handler=None,
                 *acls):
        """
        Create a collection of ``acls``.
        
        :param allow_by_default: The default authorization decision.
        :type allow_by_default: :class:`bool`
        :param default_denial_handler: The default authorization denial handler.
        :type default_denial_handler: :class:`object`
        
        """
        self._acls = list(acls)
        super(ACLCollection, self).__init__(allow_by_default,
                                            default_denial_handler)
    
    def add_acl(self, acl):
        """
        Add ``acl`` to this collection.
        
        :param acl: The new ACL.
        :type acl: class:`ACL`
        
        """
        self._acls.append(acl)
    
    # _BaseAuthorizationControl
    def decide_authorization(self, environ, object_=None):
        """
        Report whether authorization is granted to the request described by
        ``environ``.
        
        :param environ: The WSGI environment.
        :type environ: :class:`dict`
        :param object_: The object that is to be accessed (usually a controller
            action).
        :return: Whether authorization is granted.
        :rtype: :class:`bool`
        
        """
        final_decision = self._default_final_decision
        path_info = normalize_path(environ['PATH_INFO'])
        
        # Let's keep track of the longest path match so far, so we can ignore
        # shorter matches:
        tracker = _MatchTracker()
        
        # Let's iterate over every ACL to see if any of them knows what to do
        # with this request:
        for acl in self._acls:
            if not tracker.is_within_scope(acl._base_path, True, False,
                                           path_info):
                # This request is out of the scope of this ACL.
                continue
            
            # This path is covered by the ACL, let's see if it can make a
            # decision:
            decision = acl.decide_authorization(environ, object_)
            
            if decision is None:
                # This ACL didn't make a decision:
                continue
            
            # A decision has been made. Let's keep it in case there's anything
            # more specific to this request and also replace the match tracker
            # with the decision's so we can keep track of what we've found:
            final_decision = decision
            tracker = decision.match_tracker
        
        # If there's a decision made and authorization has been denied with no
        # denial handler, let's use the default one (if any):
        if final_decision is not None:
            final_decision.set_denial_handler(self._default_denial_handler)
        
        return final_decision
    
    def __repr__(self):
        return "<ACL-Collection acls=%s at 0x%x>" % (len(self._acls), id(self))


class AuthorizationDecision(object):
    """
    The decision object used when authorization is either granted or denied.
    
    """
    
    def __init__(self, allow, reason, denial_handler):
        self.allow = allow in (True, None)
        self.was_indeterminate = allow is None
        self.reason = reason
        self.denial_handler = denial_handler
        self.match_tracker = None
    
    def set_denial_handler(self, new_denial_handler):
        """If there's no denial handler set yet, use ``new_denial_handler``."""
        if self.denial_handler is None:
            self.denial_handler = new_denial_handler
    
    def set_match_tracker(self, match_tracker):
        """Set the decision's match tracker to ``match_tracker``."""
        self.match_tracker = match_tracker


# Internal stuff


class _ACE(object):
    """
    Access Control Entry.
    
    """
    
    def __init__(self, predicate, allow, reason=None, propagate=True,
                 force_inclusion=False):
        self.predicate = predicate
        self.allow = allow
        self.reason = reason
        self.propagate = propagate
        self.force_inclusion = force_inclusion
    
    def can_participate(self, environ):
        """
        Report whether this ACE should be taken into account in a request
        described by ``environ``.
        
        :param environ: The WSGI environment dictionary.
        :type environ: :class:`dict`
        :return: Whether this ACE should be taken into account
        :rtype: :class:`bool`
        
        """
        # If there's no predicate, then this ACE should always participate:
        if self.predicate is None:
            return True
        
        return self.predicate(environ)
    
    def __repr__(self):
        return "<ACE allow=%r predicate=%r reason=%r>" % \
               (self.allow, self.predicate, self.reason)


class _MatchTracker(object):
    """
    A match tracker keeps track of what kind of ACEs have participated and
    which ones should be ignored in the future.
    
    """
    
    def __init__(self):
        self.longest_path_match = 0
        self.object_ace_found = False
        self.forced_ace_found = False
    
    def is_within_scope(self, protected_path, propagated, inclusion_forced,
                        path):
        """
        Report whether ``protected_path`` covers the ``path``.
        
        If ``protected_path`` covers the path in the request described by
        ``environ``, but we already found a protected path whose scope is
        more specific, then ``protected_path`` will be out of scope unless
        ``inclusion_forced`` is set to ``True`` (as long as another ACE has
        not been enforced yet).
        
        Likewise, if we already found an ACE/ACL for the object of the requests,
        then ``protected_path`` will be out of scope.
        
        In other words, ``protected_path`` will be within scope if and only if
        ``protected_path`` represents the most specific ACE.
        
        If ``protected_path`` is ``propagated``, then it will affect cover all
        the requests under such a path.
        
        """
        protected_path_length = len(protected_path)
        return (
            path.startswith(protected_path)
            and
            not self.forced_ace_found
            and
            (
                 inclusion_forced
                 or
                 (
                  (propagated or len(path) == protected_path_length) and
                   protected_path_length >= self.longest_path_match and
                   not self.object_ace_found
                 )
            )
        )
    
    def set_longest_path(self, protected_path):
        """Set the longest protected path so far to ``protected_path``."""
        self.longest_path_match = len(protected_path)


#}
