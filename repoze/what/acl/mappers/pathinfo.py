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
The built-in ``PATH_INFO`` request-to-target mapper.

"""

import re

from repoze.what.acl.mappers.base import Mapper, Target

__all__ = ['PathInfoMapper']


class PathInfoMapper(Mapper):
    """
    A request-to-target mapper which finds the target ACO based on the
    ``PATH_INFO`` of the request.
    
    This mapper will always find a target; it will never raise a
    :class:`repoze.what.acl.mappers.base.NoTargetFoundError` exception.
    
    """
    
    multiple_slash_pattern = re.compile(r'/{2,}')
    
    def __init__(self, root_target, trailing_slash_operation=None):
        """
        Set up the ``PATH_INFO`` mapper.
        
        :param root_target: The target to be returned when the root of the
            application is requested.
        :type root_target: Target
        :param trailing_slash_operation: The operation to be assumed by default
            when there's a trailing slash in the ``PATH_INFO``.
        :type trailing_slash_operation: basestring
        
        """
        self.root_target = root_target
        self.trailing_slash_operation = trailing_slash_operation
    
    def get_target(self, request):
        """Return the target ACO based on the ``PATH_INFO``."""
        # First of all, remove multiple slashes:
        path_info = self.multiple_slash_pattern.sub(
            lambda s: '/',
            request.path_info,
        )
        
        if not path_info or path_info == '/':
            return self.root_target
        
        if path_info.endswith('/'):
            path_info = path_info[:-1]
            
            if self.trailing_slash_operation:
                # The trailing slash means that we have to assume that the
                # operation in the current request is that specified in the
                # constructor.
                resource = path_info
                operation = self.trailing_slash_operation
                return Target(resource, operation)
        
        # The directories in the PATH_INFO, without the slash in the beginning:
        path_parts = path_info[1:].split('/')
        
        resource = '/' + '/'.join(path_parts[:-1])
        operation = path_parts[-1]
        
        return Target(resource, operation)
