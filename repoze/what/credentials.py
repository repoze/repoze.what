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
:mod:`repoze.what`'s ``credentials`` handling.

"""

__all__ = ['BaseCredentialProvider', 'Credentials']


class BaseCredentialProvider(object):
    """
    Base class for credential providers.
    
    Subclasses must at least define the :meth:`load_credentials` method and the
    :attr:`provider_name` attribute. Below is a useless example which
    illustrates how credential providers are defined::
    
        from somewhere import get_isp_from_ip, get_country_from_ip
    
        class NetworkCredentialProvider(BaseCredentialProvider):
            
            provider_name = 'networking'
            
            def load_credentials(self, environ, credentials):
                credentials['ip'] = environ.get('REMOTE_ADDR')
                credentials['isp'] = get_isp_from_ip(credentials['ip'])
                credentials['country'] = get_country_from_ip(credentials['ip'])
    
    The credential provider above will load the IP address, the user's ISP and
    her country name in the ``credentials`` dictionary on every request. If you
    want to load them only when they are requested (on-demand), then you should
    also define the ``credentials_loaded`` class attribute to the list of
    items in the ``credentials`` it would define if it's called, as in::
    
        from somewhere import get_isp_from_ip, get_country_from_ip
    
        class NetworkCredentialProvider(BaseCredentialProvider):
            
            provider_name = 'networking'
            
            credentials_loaded = ['ip', 'isp', 'country']
            
            def load_credentials(self, environ, credentials):
                credentials['ip'] = environ.get('REMOTE_ADDR')
                credentials['isp'] = get_isp_from_ip(credentials['ip'])
                credentials['country'] = get_country_from_ip(credentials['ip'])
    
    """
    
    credentials_loaded = None
    
    @property
    def provider_name(self):
        raise NotImplementedError
    
    def load_credentials(self, environ, credentials):
        """
        Load the relevant credentials in the ``credentials`` dictionary.
        
        The credential provider has to edit the ``credentials`` dictionary to
        load the relevant credential.
        
        ``credentials`` will contain at least the ``repoze.what.userid`` key,
        whose value represents the current user's Id or ``None`` if she's not
        been authenticated.
        
        Any value returned by this method will be ignored.
        
        :param environ: The WSGI environ.
        :type environ: dict
        :param credentials: The :mod:`repoze.what` ``credentials`` dict.
        :type credentials: dict
        
        """
        raise NotImplementedError


class Credentials(dict):
    """
    The class for the :mod:`repoze.what`'s ``credentials`` dictionary.
    
    """
    
    def __repr__(self):
        return '<repoze.what credentials (hidden, dict-like) at %s>' % id(self)
    
    __str__ = __repr__
