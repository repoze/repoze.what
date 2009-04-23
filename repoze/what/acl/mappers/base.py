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
Base definitions for request-to-target mappers.

"""


#{ Mapping definitions


class Mapper(object):
    """
    Base class for request-to-target mappers.
    
    A mapper extracts the target (ACO and an operation) from the request, 
    independent of its existence.
    
    """
    
    def get_target(self, request):
        """
        Return the target in this request.
        
        :param request: The WebOb ``Resquest`` object for the WSGI environ in
            question.
        :return: The target ACO for the ``request``.
        :rtype: basestring
        :raise NoTargetFoundError: If the target ACO is not found.
        
        """
        raise NotImplementedError


# TODO: Does this actually make sense?
class CompoundMapper(Mapper):
    """
    Container for multiple request-to-target mappers.
    
    This is a meta-mapper which will run a set of mappers until one of them
    finds the target.
    
    """
    
    def __init__(self, *mappers):
        """
        Contain the ``mappers``.
        
        """
        self.mappers = mappers
    
    def get_target(self, request):
        """
        Find the target ACO for the ``request`` in one of the contained 
        mappers.
        
        """
        logger = request.environ['repoze.what.logger']
        
        for mapper in self.mappers:
            try:
                target = mapper.get_target(request)
                logger and logger.debug(u'Target %s found by mapper %s' %
                                        (target, mapper))
                return target
            except NoTargetFoundError:
                pass
        raise NoTargetFoundError("No mapper found target in %s" % request)


class Target(object):
    """
    Represent the target ACO in a request, which may not exist.
    
    """
    
    def __init__(self, resource, operation):
        self.resource = resource
        self.operation = operation
    
    def __unicode__(self):
        """
        Return the URI for the target ACO.
        
        """
        return 'aco:%s#%s' % (self.resource, self.operation)


#{ Exceptions


class MappingError(Exception):
    """
    Generic exception used when something goes wrong while mapping a request
    to an ACO.
    
    """
    pass


class NoTargetFoundError(MappingError):
    """
    Exception raised when the request-to-target mapper can't find the target
    from the request.
    
    """
    pass


#}

