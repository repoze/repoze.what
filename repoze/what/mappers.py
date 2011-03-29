# -*- coding: utf-8 -*-
##############################################################################
#
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
Request-to-ACO mappers.

"""

from repoze.what._utils import normalize_path

__all__ = ["Mapper", "PathInfoMapper", "RoutingArgsMapper"]


class Mapper(object):
    """
    Base class for request-to-ACO mappers.
    
    A mapper extracts the target (ACO and an operation) from the request, 
    independent of its existence.
    
    """
    
    def get_aco(self, request):
        """
        Return the target in this request.
        
        :param request: The WebOb ``Resquest`` object for the WSGI environ in
            question.
        :return: The target ACO for the ``request``.
        :rtype: basestring
        :raise NoTargetFoundError: If the target ACO is not found.
        
        """
        raise NotImplementedError


class PathInfoMapper(Mapper):
    """
    Request-to-ACO mapper which finds reports the ACO as the **normalized**
    ``PATH_INFO``.
    
    """
    
    def get_aco(self, request):
        """Return the target ACO as the ``PATH_INFO``."""
        return normalize_path(request.path_info)


class RoutingArgsMapper(Mapper):
    """
    ``wsgiorg.routing_args``-based mapper.
    
    The resulting ACO will be the concatenation of arguments in the URL.
    
    """
    
    def __init__(self, argument_keys, named=True):
        """
        
        :param argument_keys: The collection of arguments in ``routing_args``
            that are used to build the ACO path.
        :type argument_keys: Iterable of :class:`basestring` or :class:`int`
            objects
        :param named: Whether the arguments are named; otherwise they're
            positional.
        :type named: :class:`bool`
        
        """
        self._argument_keys = argument_keys
        # The named arguments are in the 2nd position, and the positional ones
        # in the 1st:
        self._routing_args_key = 1 if named else 0
    
    @classmethod
    def format_aco(cls, arguments):
        """
        Build an ACO path from the ``arguments``.
        
        :param arguments: The collection of arguments that make up the ACO.
        :type arguments: Iterable of :class:`basestring` objects
        :return: The ACO formed by the ``arguments``.
        :rtype: basestring
        
        """
        return normalize_path("/".join(arguments))
    
    def get_aco(self, request):
        """
        Extract the target from the ``wsgiorg.routing_args`` variable.
        
        :param request: The WebOb Request object for the WSGI environ.
        :return: The target ACO.
        
        Once the resource has been found, it will be turned into a path with
        :meth:`format_aco`.
        
        """
        routing_args = request.environ.get('wsgiorg.routing_args', ((), {}))
        arguments = routing_args[self._routing_args_key]
        
        aco_parts = []
        
        try:
            for required_arg in self._argument_keys:
                aco_parts.append(arguments[required_arg])
        except (KeyError, IndexError):
            aco = None
        else:
            aco = self.format_aco(aco_parts)
        
        return aco

