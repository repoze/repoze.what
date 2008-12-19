***************************************
Getting started with :mod:`repoze.what`
***************************************

.. topic:: Overview

    This document describes the basics of :mod:`repoze.what`, including its
    terminology and how to configure authentication and authorization easily.


Terminology
-----------

As explained previously, :mod:`repoze.what`'s base authorization pattern
is based on the groups to which the user belongs and the permissions granted 
to such groups, and such groups and permissions can be stored in different
types of sources -- because of that, :mod:`repoze.what` uses a generic 
terminology when it deals with those sources:

.. glossary::

    source
        Where authorization data (groups and/or permissions) is stored.
        It may be a database or a file (an Htgroups file, an Ini file, etc), for
        example.
    group source
        A :term:`source` that stores groups. For example, an Htgroups
        file or an Ini file.
    permission source
        A :term:`source` that stores permissions. For example, an
        Ini file.
    source adapter
        An object that manages a given type of :term:`source` to add,
        edit and delete entries under an API independent of the source type.
    group adapter
        An :term:`adapter <source adapter>` that deals with one :term:`group 
        source`.
    permission adapter
        An :term:`adapter <source adapter>` that deals with one 
        :term:`permission source`.
    section
        Sections are the `compound elements` that make up a :term:`source` -- 
        this is, in a :term:`permission source`, the sections are the 
        permissions, and in a :term:`group source`, the sections are the 
        groups.
    item
        The elements that are contained in a :term:`section`. In a
        :term:`permission source`, the items are the groups that are granted
        the permission represented in their parent section; likewise, in a
        :term:`group source`, the items are the Ids of the users that belong to
        the group represented in the parent section.


The authentication framework (:mod:`repoze.who`) only deals with the 
:term:`sources <source>` that handle your users' credentials, while the 
authorization framework (:mod:`repoze.what`) deals with both the 
:term:`sources <source>` that handle your groups and those that handle your
permissions.

Sample sources
~~~~~~~~~~~~~~

Below are the contents of a mock ``.htgroups`` file that defines the groups of
an application. In other words, such a file is a :term:`group source` of
type ``htgroups``::

    developers: rms, linus, guido
    admins: rms, linus
    users: gustavo, maribel

It has three sections and five items: "developers" (made up of the items "rms",
"linus" and "guido"), "admins" (made up of the items "rms" and "linus") and
"users (made up of the items "gustavo" and "maribel").

And below are the contents of a mock ``.ini`` file that defines the permissions
of the groups in an application. In other words, such a file is a
:term:`permission source` of type ``Ini``::

    [manage-site]
    admins
    [release-software]
    admins
    developers
    [contact-us]
    users

It has three sections and three items: "manage-site" (made up one item,
"admins"), "release-software" (made up of the items "admins" and "developers")
and "contact-us" (made up of the item "users").

If you use a database to store your users, groups and permissions, then such a
database is both the group and permission source:

  * The tables where you store your groups and users are the sections and the
    section items, respectively, of the ``group source``.
  * The tables where you store your permissions and groups are the sections and
    the section items, respectively, of the ``permission source``.


.. _add-auth-middleware:

Setting up authentication and authorization
-------------------------------------------

.. note::

    If you are using a web framework and it already configures 
    :mod:`repoze.what`, you may want to skip this section.

To enable authorization in your Web application, you need to add some
WSGI middleware to your application, which is automatically done for you if
you are using the :mod:`quickstart <repoze.what.plugins.quickstart>`.

When you enable authorization with :mod:`repoze.what`, authentication
with :mod:`repoze.who` is automatically enabled. 

.. warning::

    Do not try to configure :mod:`repoze.who` directly -- if you want 
    authorization to work, you have to configure it through :mod:`repoze.what`.


Using authentication and authorization without the quickstart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're not using the quickstart, then you have to add the required
middleware in your application. This gives you more flexibility, such as being
able not to use a database to store your users' credentials, your groups
and/or your permissions.

You are highly encouraged to add such a middleware with a function defined in,
say, ``{yourproject}.config.middleware`` and called, say, ``add_auth``. Then
that function may look like this::

    def add_auth(app):
        """
        Add authentication and authorization middleware to the ``app``.
        
        :param app: The WSGI application.
        :return: The same WSGI application, with authentication and
            authorization middleware.
        
        People will login using HTTP Authentication and their credentials are
        kept in an ``Htpasswd`` file. For authorization through repoze.what,
        we load our groups stored in an ``Htgroups`` file and our permissions
        stored in an ``.ini`` file.
        
        """
    
        from repoze.who.plugins.basicauth import BasicAuthPlugin
        from repoze.who.plugins.htpasswd import HTPasswdPlugin, crypt_check
        
        from repoze.what.middleware import setup_auth
        from repoze.what.plugins.ini import INIPermissionsAdapter
        # Please note that the Htgroups plugins has not been created yet; want 
        # to jump in?
        from repoze.what.plugins.htgroups import HtgroupsAdapter

        # Defining the group adapters; you may add as much as you need:
        groups = {'all_groups': HtgroupsAdapter('/path/to/groups.htgroups')}

        # Defining the permission adapters; you may add as much as you need:
        permissions = {'all_perms': INIPermissionsAdapter('/path/to/perms.ini')}
        
        # repoze.who identifiers; you may add as much as you need:
        basicauth = BasicAuthPlugin('Private web site')
        identifiers = [('basicauth', basicauth)]

        # repoze.who authenticators; you may add as much as you need:
        htpasswd_auth = HTPasswdPlugin('/path/to/users.htpasswd', crypt_check)
        authenticators = [('htpasswd', htpasswd_auth)]

        # repoze.who challengers; you may add as much as you need:
        challengers = [('basicauth', basicauth)]

        app_with_auth = setup_auth(
            app,
            groups,
            permissions,
            identifiers=identifiers,
            authenticators=authenticators,
            challengers=challengers)
        return app_with_auth

Of course, there are other things you may customize, such as adding
:mod:`repoze.who` identifiers, more authenticators, challengers and metadata
providers (read :func:`repoze.what.middleware.setup_auth` for more information).


What's next?
------------

Now you are ready to control authorization in your application with 
:mod:`predicates <repoze.what.predicates>`!
