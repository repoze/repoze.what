# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008, Gustavo Narea <me@gustavonarea.net>
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

"""Base functionality for anti-spam services."""


class BaseAntiSpamService(object):
    """
    Base class for an anti-spam service.
    
    Anti-spam plugins should extend this class to support the respective
    anti-spam service provider.
    
    .. attribute :: service_name = None
    
        The name of the service. For example, ``akismet`` or ``defensio``.
        
        :type: unicode
    
    """
    
    service_name = None
    
    def check(self, check_type='spam', *args, **kwargs):
        if check_type == 'spam':
            return self.is_spam(*args, **kwargs)
        elif check_type == 'spammer':
            return self.is_spammer(*args, **kwargs)
        raise ValueError('Unknown check_type "%s"' % check_type)
    
    def is_spam(self, environ, message=None, title=None, author=None,
                email=None, url=None):
        """
        Check whether the ``message`` is spam.
        
        :param environ: The WSGI enviroment.
        :param message: The message to be verified.
        :type message: unicode
        :param title: The title of the message (if any).
        :type title: unicode
        :param author: The message's author (if not anonymous).
        :type author: unicode
        :param email: The author's email address (if provided).
        :type email: unicode
        :param url: The URL to the author's website (if provided).
        :type url: unicode
        :rtype: bool
        :raise ServiceError: If there was a problem with the service.
        
        """
        raise NotImplementedError()
    
    def is_spammer(self, environ, name=None, email=None, url=None):
        """
        Check whether the current user is a known spammer.
        
        :param environ: The WSGI enviroment.
        :param name: The user's name (if known).
        :type name: unicode
        :param email: The user's email address (if known).
        :type email: unicode
        :param url: The URL to the user's website (if known).
        :type url: unicode
        :rtype: bool
        :raise ServiceError: If there was a problem with the service.
        
        """
        raise NotImplementedError()
    
    def spam_feedback(self, spam):
        """
        Mark a spam as ham or vice versa.
        
        :param spam: The spam message in question.
        :type spam: repoze.what.antispam.queues.PotentialSpam
        :raise ServiceError: If there was a problem with the service.
        
        """
        raise NotImplementedError()
    
    def spammer_feedback(self, spammer):
        """
        Mark a spammer as ham or vice versa.
        
        :param spammer: The (potential) spammer in question.
        :type spammer: repoze.what.antispam.queues.PotentialSpammer
        :raise ServiceError: If there was a problem with the service.
        
        """
        raise NotImplementedError()


class ServiceError(Exception):
    """Exception raised when there's an error with the anti-spam service."""
    pass
