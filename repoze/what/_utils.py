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
Internal utilities for :mod:`repoze.what`.

"""

from re import compile as compile_regex

__all__ = ["normalize_path"]


_MULTIPLE_PATHS = compile_regex(r"/{2,}")


def normalize_path(path):
    """
    Normalize ``path``.
    
    It returns ``path`` with leading and trailing slashes, and no multiple
    continuous slashes.
    
    """
    if path:
        if path[0] != "/":
            path = "/" + path
        
        if path[-1] != "/":
            path = path + "/"
        
        path = _MULTIPLE_PATHS.sub("/", path)
    else:
        path = "/"
    
    return path

