# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
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
The built-in ``wsgiorg.routing_args``-based request-to-target mapper.

"""
from repoze.what.exc import MappingError, NoTargetFoundError
from repoze.what.acl.mappers.base import Mapper, Target

__all__ = ['PositionalArgsMapper', 'NamedArgsMapper', 'RoutesMapper']


#{ Generic mappers


class RoutingArgsMapper(Mapper):
    """
    Base class for ``wsgiorg.routing_args``-based mappers.
    
    These mappers should be used when the resource is set in one of the items
    of ``wsgiorg.routing_args`` *and* also the action is set in of the items
    of said variable.
    
    """
    
    def __init__(self, resource_key, operation_key):
        """
        
        :param resource_key: The key for the item that contains the resource.
        :type resource_key: basestring or int
        :param operation_key: The key for the item that contains the operation.
        :type operation_key: basestring or int
        
        """
        self.resource_key = resource_key
        self.operation_key = operation_key
    
    def format_resource(self, resource):
        """
        Prepend a forward slash to ``resource``.
        
        :param resource: The resource string.
        :type resource: basestring
        :return: ``resource`` with a slash prepended.
        :rtype: basestring
        
        """
        return "/%s" % resource
    
    def get_target(self, request):
        """
        Extract the target from the ``wsgiorg.routing_args`` variable.
        
        :param request: The WebOb Request object for the WSGI environ.
        :return: The target ACO.
        :raises MappingError: If the ``wsgiorg.routing_args`` variable isn't
            available or the routing argument in question (positional or
            named) is not available.
        :raises NotTargetFoundError: If the key for the resource or the
            operation is not available.
        
        Once the resource has been found, it will be filtered with
        :meth:`format_resource`.
        
        """
        # Checking the routing arguments:
        routing_args = request.environ.get('wsgiorg.routing_args')
        if not routing_args or self.arg_key > len(routing_args):
            raise MappingError('The "wsgiorg.routing_args" variable is not '
                               'set properly')
        
        # Retrieving the resource and the operation
        args = routing_args[self.arg_key]
        try:
            resource = args[self.resource_key]
            operation = args[self.operation_key]
        except (IndexError, KeyError):
            raise NoTargetFoundError('Target not found in routing args: %s' %
                                     unicode(args))
        
        resource = self.format_resource(resource)
        
        return Target(resource, operation)


class PositionalArgsMapper(RoutingArgsMapper):
    """
    Mapper that extracts the target from the positional arguments.
    
    This mapper should be used when the resource and the operation are defined
    in the positional arguments available in the ``wsgiorg.routing_args``
    variable.
    
    This mapper may seem useless, but given that it's easy to implement, why
    not do it?
    
    """
    
    arg_key = 0


class NamedArgsMapper(RoutingArgsMapper):
    """
    Mapper that extracts the target from the named arguments.
    
    This mapper should be used when the resource and the operation are defined
    in the named arguments available in the ``wsgiorg.routing_args`` variable.
    
    """
    
    arg_key = 1


#{ Specific mappers


# TODO: Maybe this should be defined in a separate distribution. I'm not sure,
# because it's pretty trivial and Routes is not a dependency, strictly speaking
class RoutesMapper(NamedArgsMapper):
    """
    Mapper for `Routes <http://routes.groovie.org/>`_.
    
    It takes the ``controller`` and ``action`` named arguments as the 
    ``resource`` and ``operation``, respectively.
    
    """
    
    def __init__(self):
        """
        Use ``'controller'`` and ``'action'`` as the resource and operation
        keys, respectively.
        
        """
        super(RoutesMapper, self).__init__('controller', 'action')
    
    def format_resource(self, resource):
        """
        Replace the dots with forward slashes and prepend a slash in
        ``resource``.
        
        """
        resource = resource.replace('.', '/')
        return super(RoutesMapper, self).format_resource(resource)


#}
