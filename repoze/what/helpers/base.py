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
Base definitions for :mod:`repoze.what` helpers.

Helpers are similar to :mod:`repoze.who` metadata providers and the
:mod:`repoze.what` v1 credentials, but these are more efficient because they're
run only when they're needed.

"""

__all__ = ['Helper']


class Helper(object):
    """
    Base class for :mod:`repoze.what` v2 helpers.
    
    Helpers are used by request-to-target mappers and predicate checkers to
    handle CRUD operations in a given source, to store data or perform **any**
    other operation they may ever need.
    
    Every helper must subclass this class and set its :attr:`name` attribute
    to the string that will identify the helper. For example::
    
        class MyHelper(Helper):
            name = 'my_helper'

    .. attribute:: name
    
        The name of the current helper.
    
    """
    
    @property
    def name(self):
        raise NotImplementedError
    
    @classmethod
    def organize_helpers(cls, *helpers):
        """
        Return the ``helpers`` organized in a dictionary.
        
        It will return a dictionary whose items are the ``helpers``, where the
        key is the helper name and the value is the helper itself.
        
        :return: The ``helpers`` organized.
        :rtype: dict
        :raises IndexError: If the helper is duplicate (i.e., there are at
            least two helpers with the same name).
        
        """
        helpers_organized = {}
        
        for helper in helpers:
            if helper.name in helpers_organized:
                raise IndexError('Helper "%s" is already defined' % helper.name)
            helpers_organized[helper.name] = helper
        
        return helpers_organized
