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

"""Anti-spam predicates."""

from copy import copy

from paste.request import parse_formvars

from repoze.what.predicates import Predicate

__all__ = ['not_spam', 'not_spammer']


class _BaseAntiSpamPredicate(Predicate):
    """
    Base anti-spam predicate.
    
    The ``default_variable_names`` attribute contains the `POST` or `GET`
    variable names of the variables that may be required by the anti-spam
    service. 
    
    """
    
    def __init__(self, *services, **kwargs):
        """
        Create an anti-spam predicate.
        
        If not ``services`` are defined, the default one will be used.
        
        :param *services: The name of the defined anti-spam services that
            should perform the evaluation.
        
        """
        self.services = services
        self.variable_names = copy(self.default_variable_names)
        self._configure(**kwargs)
    
    def __call__(self, **kwargs):
        self._configure(**kwargs)
    
    def _configure(self, **kwargs):
        if 'http_method' not in kwargs:
            kwargs['http_method'] = 'POST'
        self.http_method = kwargs['http_method']
        
        for key in self.variable_names.keys():
            if key in kwargs:
                self.variable_names[key] = kwargs[key]
    
    def _get_variables(self, environ):
        if self.http_method == 'POST':
            form_vars = parse_formvars(environ, False)
        else:
            form_vars = parse_formvars(environ, True)
        needed_vars = {}
        for req_var in self.variable_names.keys():
            needed_vars[req_var] = form_vars.get(req_var)
        return needed_vars
    
    def _eval_with_environ(self, environ):
        antispam_mgr = environ.get('repoze.what.antispam')
        variables = self._get_variables(environ)
        return antispam_mgr.check(check_type, environ, variables,
                                  self.services)


class not_spam(_BaseAntiSpamPredicate):
    message = "The submitted message must not be spam"
    
    checker_type = 'spam'
    
    default_variable_names = {
        'message': 'message',
        'title': 'message_title',
        'author': 'author_name',
        'email': 'author_email',
        'url': 'author_url'
        }


class not_spammer(_BaseAntiSpamPredicate):
    message = "The current user must not be a known spammer"
    
    checker_type = 'spammer'
    
    default_variable_names = {
        'name': 'person_name',
        'email': 'person_email',
        'url': 'person_url'
        }
