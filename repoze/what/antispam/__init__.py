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

"""Base functionality for anti-spam plugins."""

from zope.interface import implements
from repoze.who.interfaces import IIdentifier

from repoze.what.antispam.services import ServiceError
# They are provided as a short-cut, but they're not used over here:
from repoze.what.antispam.predicates import *


class AntiSpamManager(object):
    """
    The anti-spam manager.
    
    """
    
    implements(IIdentifier)
    
    def __init__(self, antispam_services, default_service=None,
                 spam_queue=None, spammer_queue=None):
        """
        Create the anti-spam manager.
        
        :param antispam_services: The anti-spam services to be used.
        :type antispam_services: list
        :param default_service: The name of the default service.
        :type default_service: unicode
        :param spam_queue: The queue where potential spam is stored.
        :param spammer_queue: The queue where potential spammer are stored.
        
        ``antispam_services`` must be instances of
        :class:`repoze.what.antispam.services.BaseAntiSpamService`.
        
        If ``default_service`` is not set and there's only one anti-spam
        service, then that service is used as the default.
        
        """
        # Turning the services list/tuple into a dictionary:
        services_dict = {}
        for service in antispam_services:
            services_dict[service.service_name] = service
        
        self.antispam_services = services_dict
        self.queues = {'spam': spam_queue,
                       'spammer': spammer_queue}
        
        if default_service and len(antispam_services) > 1:
            self.default_service = self.antispam_services[default_service]
        elif len(antispam_services) is 1:
            self.default_service = antispam_services[0]
        else:
            self.default_service = None
    
    def check(self, check_type, environ, variables, services=None):
        """
        Check whether a message is spam or the current user is a known spammer.
        
        :param check_type: ``spam`` if we are going to check if a message is
            spam or ``spammer`` if we are going to check if the current user
            is a known spammer.
        :type check_type: str
        :param environ: The WSGI environment.
        :param variables: The variables involved in the verification.
        :type variables: dict
        :param services: A filter with the name of the anti-spam services to
            be used.
        :type services: list
        :return: ``True`` if the message is spam or the current user is a known
            spammer; ``False`` otherwise.
        :rtype: bool
        
        """
        logger = environ.get('repoze.who.logger')
        logger and logger.debug('Verification type: %s' %  check_type)
        logger and logger.debug('Verification variables: %s' % str(variables))
        
        # ----- Selecting the anti-spam services to be used:
        service_list = []
        if services:
            # It's been selected a subset of the available services
            for service in services:
                if service not in self.antispam_services:
                    logger and logger.error('Anti-spam service "%s" is unknown'
                                            % service)
                    continue
                service_list.append(self.antispam_services[service])
        elif len(self.antispam_services) > 0:
            # There's no filter, so we have to select all the available
            # services
            service_list = self.antispam_services.values()
            # Logging it...
            name_of_services = ", ".join(self.antispam_services.keys())
            logger and logger.debug('Using the available anti-spam services: %s'
                                    % name_of_services)
        
        if not service_list:
            if self.default_service is None:
                logger and logger.critical('No defined anti-spam service has '
                                           'been selected')
                return False
            logger and logger.debug('Using the default anti-spam service (%s)'
                                    % self.default_service.service_name)
            service_list.append(self.default_service)
        
        # ----- Checking if it's a spam or a spammer:
        is_spam = True
        for service in service_list:
            try:
                if service.check(check_type, environ, **variables):
                    logger and logger.info('Service "%s" says it is %s' % 
                                           (service.service_name, check_type))
                    queue = self.queues[check_type]
                    if queue:
                        queue.add_item(**variables)
                        logger and logger.info('Added %s to the moderation '
                                               'queue' % check_type)
                    return True
                logger and logger.info('Service "%s" says it is not %s' % 
                                       (service.service_name, check_type))
                is_spam = False
            except ServiceError, msg:
                exc_name = msg.__class__.__name__
                logger and logger.critical('%s: %s' % (exc_name, msg))
        return is_spam
    
    # IIdentifier
    def identify(self, environ):
        environ['repoze.what.antispam'] = self
    
    # IIdentifier
    def remember(self, environ, identity):
        pass
    
    # IIdentifier
    def forget(self, environ, identity):
        pass

    def set_auth_settings(self, auth_args):
        if 'identifiers' not in auth_args:
            auth_args['identifiers'] = []
        auth_args['identifiers'].insert(0, ('antispam_mgr', self))
