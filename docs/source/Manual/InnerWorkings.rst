****************************************
The inner-workings of :mod:`repoze.what`
****************************************

.. module:: repoze.what.middleware
    :synopsis: repoze.what WSGI middleware
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

:Status: Official

.. topic:: Overview

    :mod:`repoze.what` doesn't provides WSGI middleware per se. Instead, it 
    configures and re-uses :mod:`repoze.who`'s.

Middleware-related components are defined in the :mod:`repoze.what.middleware`
module. It contains one function to configure :mod:`repoze.who` with support
for :mod:`repoze.what` and the :mod:`repoze.who` metadata provider that loads
authorization-related data in the ``identity`` dict.

.. class:: setup_auth(app, group_adapters, permission_adapters, **who_args)

    Setup :mod:`repoze.who` with :mod:`repoze.what` support.
    
    Additional keyword arguments will be passed to
    :class:`repoze.who.middleware.PluggableAuthenticationMiddleware`.
    
    :param app: The WSGI application object.
    :param group_adapters: The group source adapters to be used.
    :type group_adapters: dict
    :param permission_adapters: The permission source adapters to be used.
    :type permission_adapters: dict
    
    In fact, you can customize all the options for :mod:`repoze.who` from this 
    function. Keep in mind that :mod:`repoze.who` must be configured `through`
    :mod:`repoze.what` for authorization to work.

    For example::
        
        from repoze.who.plugins.htpasswd import HTPasswdPlugin, crypt_check
        from repoze.what.middleware import setup_auth
        # Please note that the plugins below have not been created yet:
        from repoze.what.plugins.htgroups import HtgroupsAdapter
        from repoze.what.plugins.ini import IniPermissionAdapter

        # Defining the group adapters; you may add as much as you need:
        groups = {'all_groups': HtgroupsAdapter('/path/to/groups.htgroups')}

        # Defining the permission adapters; you may add as much as you need:
        permissions = {'all_perms': IniPermissionAdapter('/path/to/perms.ini')}

        # repoze.who authenticators; you may add as much as you need:
        htpasswd_auth = HTPasswdPlugin('/path/to/users.htpasswd', crypt_check)
        authenticators = [('htpasswd', htpasswd_auth)]

        app_with_auth = setup_auth(
            app,
            groups,
            permissions,
            authenticators=authenticators)

.. class:: AuthorizationMetadata(group_adapters, permission_adapters)

    Fetch the groups and permissions of the authenticated user.
    
    :param group_adapters: Set of adapters that retrieve the known groups
        of the application, each identified by a keyword.
    :type group_adapters: dict
    :param permission_adapters: Set of adapters that retrieve the
        permissions for the groups, each identified by a keyword.
    :type permission_adapters: dict
    
    .. method:: add_metadata(environ, identity)
    
        Load the groups and permissions of the authenticated user into the
        repoze.who identity.
        
        :param environ: The WSGI environment.
        :param identity: The repoze.who's identity dictionary.
        
        It also logs the groups and permissions for the user.
        
        .. warning::
        
            This method should only be used by :mod:`repoze.who`.
    
    .. note::
    
        Only :func:`setup_auth` is expected to use this :mod:`repoze.who`
        metadata provider directly. It's documented here to help you understand
        how things work internally, but there's no reason why you may need to
        use it without :func:`setup_auth`.
