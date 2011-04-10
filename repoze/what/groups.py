# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011, Gustavo Narea <me@gustavonarea.net>.
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
Interface to query the collection of groups to which users belong.

"""


__all__ = ["BaseGroupAdapter"]


class BaseGroupAdapter(object):
    """
    Interface to query the collection of groups to which users belong.
    
    The check is performed with the request object rather than with the
    user Id to support complex scenarios like:
    
    - All the groups to which the user belongs are already loaded in the
      request.
    - The request contains an object required to retrieve the groups. For
      example, a SQLAlchemy session.
    - The groups may be determined based on request elements other than the
      ``REMOTE_USER``.
    
    This is an abstract base class and subclasses must override the following
    methods without calling them:
    
    - :meth:`_requester_in_any_group`.
    - :meth:`_requester_in_all_groups`.
    
    """
    
    def requester_in_any_group(self, request, groups):
        """
        Report whether the subject making the ``request`` belongs to at least
        one of the ``groups``.
        
        :param request: The WSGI request object.
        :param groups: The set of groups to check whether the requester belongs.
        :type groups: :class:`set`
        :rtype: :class:`bool`
        
        This is a proxy to :meth:`_requester_in_any_group` in other to cache its
        results and avoid calling it when the cache is sufficient to compute
        the result. The cache is only valid within the same request.
        
        An empty set of ``groups`` returns ``False``.
        
        """
        if not groups:
            return False
        
        cached_groups = request.environ['repoze.what.groups']
        
        # If the requester is already known to belong to at least one of the
        # "groups", it's not necessary to query the adapter:
        if groups & cached_groups['membership']:
            return True
        
        # Likewise, if the requester is already known not to belong to all of
        # the "groups", it's not necessary to query the adapter:
        if groups.issubset(cached_groups['no_membership']):
            return False
        
        # It's necessary to query the adapter, but the query will be restricted
        # to those groups that have not (yet) been cached:
        uncached_groups = groups - cached_groups['membership'] - \
            cached_groups['no_membership']
        
        in_any_group = self._requester_in_any_group(request, uncached_groups)
        
        # Cache the groups to which the requester is known to belong or not,
        # unless it's ambiguous (i.e., two or more groups were queried and
        # the requester belongs to at least one of them):
        if len(uncached_groups) == 1 or \
           (len(uncached_groups) > 1 and not in_any_group):
            
            cache_key = "membership" if in_any_group else "no_membership"
            cached_groups[cache_key] |= uncached_groups
        
        return in_any_group
    
    def requester_in_all_groups(self, request, groups):
        """
        Report whether the subject making the ``request`` belongs to all of the
        ``groups``.
        
        :param request: The WSGI request object.
        :param groups: The set of groups to check whether the requester belongs.
        :type groups: :class:`set`
        :rtype: :class:`bool`
        
        This is a proxy to :meth:`_requester_in_all_groups` in other to cache
        its results and avoid calling it when the cache is sufficient to compute
        the result. The cache is only valid within the same request.
        
        An empty set of ``groups`` returns ``False``.
        
        """
        if not groups:
            return False
        
        cached_groups = request.environ['repoze.what.groups']
        
        # If the requester is already known to belong to all of the "groups",
        # it's not necessary to query the adapter:
        if groups.issubset(cached_groups['membership']):
            return True
        
        # Likewise, if the requester is already known not to belong to at least
        # one of the groups, it's not necessary to query the adapter:
        if groups & cached_groups['no_membership']:
            return False
        
        # It's necessary to query the adapter, but the query will be restricted
        # to those groups that have not (yet) been cached:
        uncached_groups = groups - cached_groups['membership'] - \
            cached_groups['no_membership']
        
        in_all_groups = self._requester_in_all_groups(request, uncached_groups)
        
        # Cache the groups to which the requester is known to belong or not,
        # unless it's ambiguous (i.e., two or more groups were queried and
        # the requester doesn't belongs to at least one of them):
        if len(uncached_groups) == 1 or \
           (len(uncached_groups) > 1 and in_all_groups):
            
            cache_key = "membership" if in_all_groups else "no_membership"
            cached_groups[cache_key] |= uncached_groups
        
        return in_all_groups
    
    #{ Abstract methods
    
    def _requester_in_any_group(self, request, groups):
        """
        Report whether the subject making the ``request`` belongs to at least
        one of the ``groups`` by querying the source of groups directly.
        
        :param request: The WSGI request object.
        :param groups: The set of groups to check whether the requester belongs.
        :type groups: :class:`set`
        :rtype: :class:`bool`
        
        **This method must be overridden in subclasses.**
        
        """
        raise NotImplementedError    #pragma:no cover
    
    def _requester_in_all_groups(self, request, groups):
        """
        Report whether the subject making the ``request`` belongs to all of the
        ``groups`` by querying the source of groups directly.
        
        :param request: The WSGI request object.
        :param groups: The set of groups to check whether the requester belongs.
        :type groups: :class:`set`
        :rtype: :class:`bool`
        
        **This method must be overridden in subclasses.**
        
        """
        raise NotImplementedError    #pragma:no cover
    
    #}

