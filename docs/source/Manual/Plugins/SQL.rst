*********************************
The :mod:`repoze.what` SQL plugin
*********************************

:Author: Gustavo Narea.
:Status: Official
:Version: 1.0

.. module:: repoze.what.plugins.sql
    :synopsis: SQL support for repoze.what
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>
.. moduleauthor:: Florent Aide <florent.aide@gmail.com>
.. moduleauthor:: Agendaless Consulting and Contributors

.. topic:: Overview

    The SQL plugin makes :mod:`repoze.what` support :term:`sources <source>` 
    defined in `SQLAlchemy <http://www.sqlalchemy.org/>`_-managed databases by 
    providing one :term:`group adapter`, one :term:`permission adapter` and 
    one utility to configure both in one go (optionally, when the 
    :term:`group source` and the :term:`permission source` have a 
    relationship). They are all defined in the :mod:`repoze.what.plugins.sql` 
    module.
    
    This plugin also defines :mod:`repoze.what.plugins.quickstart`.
    
    To install it, you may run::
    
        easy_install repoze.what.plugins.sql


.. warning::

    This plugin doesn't work with Elixir yet. If you want to make it work with
    Elixir, please contact us.


.. contents:: Table of Contents
    :depth: 3


.. class:: SqlGroupsAdapter(group_class, user_class, session)
    
    Create an SQL groups source adapter.
    
    :param group_class: The class that manages the groups.
    :param user_class: The class that manages the users.
    :param session: The SQLALchemy session to be used.
    
    To use this adapter, you must also define your users in a SQLAlchemy-managed
    table with the relevant one-to-many (or many-to-many) relationship defined 
    with ``group_class``.
    
    On the other hand, unless stated otherwise, it will also assume the 
    following naming conventions in both classes; to replace any of those
    default values, you should use the ``translations`` dictionary of the
    relevant class accordingly:
    
    * In `group_class`, the attribute that contains the group name is 
      ``group_name`` (e.g., ``Group.group_name``).
    * In `group_class`, the attribute that contains the members of such a group
      is ``users`` (e.g., ``Group.users``).
    * In `user_class`, the attribute that contains the user's name is
      ``user_name`` (e.g., ``User.user_name``).
    * In `user_class`, the attribute that contains the groups to which a user
      belongs is ``groups`` (e.g., ``User.groups``).
    
    Example #1, without special naming conventions::
    
        # ...
        from repoze.what.plugins.sql import SqlGroupsAdapter
        from my_model import User, Group, DBSession
        
        groups = SqlGroupsAdapter(Group, User, DBSession)
        
        # ...
    
    Example #2, with special naming conventions::
    
        # ...
        from repoze.what.plugins.sql import SqlGroupsAdapter
        from my_model import Member, Team, DBSession
        
        groups = SqlGroupsAdapter(Team, Member, DBSession)
        
        # Replacing the default attributes, if necessary:
        
        # We have "Team.team_name" instead of "Team.group_name":
        groups.translations['section_name'] = 'team_name'
        # We have "Team.members" instead of "Team.users":
        groups.translations['items'] = 'members'
        # We have "Member.username" instead of "Member.user_name":
        groups.translations['item_name'] = 'username'
        # We have "Member.teams" instead of "Member.groups":
        groups.translations['sections'] = 'teams'
        
        # ...


.. class:: SqlPermissionsAdapter(permission_class, group_class, session)
    
    Create an SQL permissions source adapter.
    
    :param permission_class: The class that manages the permissions.
    :param group_class: The class that manages the groups.
    :param session: The SQLALchemy session to be used.
    
    To use this adapter, you must also define your groups in a 
    SQLAlchemy-managed table with the relevant one-to-many (or many-to-many)
    relationship defined with ``permission_class``.
    
    On the other hand, unless stated otherwise, it will also assume the 
    following naming conventions in both classes; to replace any of those
    default values, you should use the ``translations`` dictionary of the
    relevant class accordingly:
    
    * In `permission_class`, the attribute that contains the permission name is 
      ``permission_name`` (e.g., ``Permission.permission_name``).
    * In `permission_class`, the attribute that contains the groups that are 
      granted such a permission is ``groups`` (e.g., ``Permission.groups``).
    * In `group_class`, the attribute that contains the group name is
      ``group_name`` (e.g., ``Group.group_name``).
    * In `group_class`, the attribute that contains the permissions granted to
      that group is ``permissions`` (e.g., ``Group.permissions``).
    
    Example #1, without special naming conventions::
    
        # ...
        from repoze.what.plugins.sql import SqlPermissionsAdapter
        from my_model import Group, Permission, DBSession
        
        groups = SqlPermissionsAdapter(Permission, Group, DBSession)
        
        # ...
    
    Example #2, with special naming conventions::
    
        # ...
        from repoze.what.plugins.sql import SqlPermissionsAdapter
        from my_model import Team, Permission, DBSession
        
        permissions = SqlPermissionsAdapter(Permission, Team, DBSession)
        
        # Replacing the default attributes, if necessary:
        
        # We have "Permission.perm_name" instead of "Permission.permission_name":
        permissions.translations['section_name'] = 'perm_name'
        # We have "Permission.teams" instead of "Permission.groups":
        permissions.translations['items'] = 'teams'
        # We have "Team.team_name" instead of "Team.group_name":
        permissions.translations['item_name'] = 'team_name'
        # We have "Team.perms" instead of "Team.permissions":
        permissions.translations['sections'] = 'perms'
        
        # ...


.. function:: configure_sql_adapters(user_class, group_class, permission_class, session[, group_translations={}, permission_translations={}])
    
    Configure and return group and permission adapters that share the same model.
    
    :param user_class: The class that manages the users.
    :param group_class: The class that manages the groups.
    :param user_class: The class that manages the permissions.
    :param session: The SQLALchemy session to be used.
    :param group_translations: The dictionary of translations for the group.
    :param permission_translations: The dictionary of translations for the permissions.
    :return: The ``group`` and ``permission`` adapters, configured.
    :rtype: dict 
    
    For this function to work, ``user_class`` and ``group_class`` must have the
    relevant one-to-many (or many-to-many) relationship; likewise, ``group_class`` 
    and ``permission_class`` must have the relevant one-to-many (or many-to-many)
    relationship.
    
    Example::
    
        # ...
        from repoze.what.plugins.sql import configure_sql_adapters
        from my_model import User, Group, Permission, DBSession
        
        adapters = configure_sql_adapters(User, Group, Permission, DBSession)
        groups = adapters['group']
        permissions = adapters['permission']
        
        # ...


:mod:`repoze.what.plugins.quickstart` -- Auth quickstart
========================================================

.. module:: repoze.what.plugins.quickstart
    :synopsis: Ready-to-use authentication and authorization
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>
.. moduleauthor:: Florent Aide <florent.aide@gmail.com>
.. moduleauthor:: Agendaless Consulting and Contributors


Your application may take advantage of a rather simple, and usual, 
authentication and authorization setup, in which the users' data, the groups
and the permissions used in the application are all stored in a SQLAlchemy
managed database.

To get started quickly, you may copy the SQLAlchemy-powered model defined in
`model_sa_example.py <../../_static/model_sa_example.py>`_ and then create
at least a few rows to try it out::

    u = User()
    u.user_name = u'manager'
    u.password = u'managepass'

    DBSession.save(u)

    g = Group()
    g.group_name = u'managers'

    g.users.append(u)

    DBSession.save(g)

    p = Permission()
    p.permission_name = u'manage'
    p.groups.append(g)

    DBSession.save(p)
    DBSession.flush()

Now that you have some rows in your database, you can set up authentication
and authorization as explained in the next section.

How to set it up
----------------

Although :mod:`repoze.what` is meant to deal with authorization only,
this module defines a :mod:`repoze.who` authenticator (which deals with your
users' login using your users table) and a function that adds auth middleware
to your application easily.

You only have deal with that function (:func:`setup_sql_auth`), not with the
authenticator (:class:`SQLAuthenticatorPlugin`) as the function itself will
configure the authenticator.

.. function:: setup_sql_auth(app, user_class, group_class, permission_class, session[, form_plugin=None, form_identifies=True, identifiers=None, authenticators=[], challengers=[], mdproviders=[], translations={}])
    
    Setup :mod:`repoze.who` and :mod:`repoze.what` with SQL authentication 
    and authorization.
    
    :param app: Your WSGI application.
    :param user_class: The SQLAlchemy class for the users.
    :param group_class: The SQLAlchemy class for the groups.
    :param permission_class: The SQLAlchemy class for the permissions.
    :param session: The SQLAlchemy session.
    :param form_plugin: The main :mod:`repoze.who` challenger plugin; this is 
        usually a login form.
    :param form_identifies: Whether the ``form_plugin`` may and should act as
        an :mod:`repoze.who` identifier.
    :param identifiers: Secondary :mod:`repoze.who` identifier plugins, if any.
    :param authenticators: The :mod:`repoze.who` authenticators to be used.
    :param challengers: Secondary :mod:`repoze.who` challenger plugins, if any.
    :param mdproviders: Secondary :mod:`repoze.who` metadata plugins, if any.
    :param translations: The model translations.
    :return: The WSGI application with authentication and authorization
        middleware.
    
    See `Changing attribute names`_ to learn how to use the `translations`
    argument.

.. class:: SQLAuthenticatorPlugin(user_class, session)

    Only :func:`setup_sql_auth` is expected to deal with this :mod:`repoze.who`
    authenticator.

    :param user_class: The SQLAlchemy class for the users.
    :param session: The SQLAlchemy session.

Customizing the model definition
--------------------------------

Your auth-related model doesn't `have to` be like the default one, where the
class for your users, groups and permissions are, respectively, ``User``,
``Group`` and ``Permission``, and your users' user name is available in
``User.user_name``. What if you prefer ``Member`` and ``Team`` instead of
``User`` and ``Group``, respectively? Or what if you prefer ``Group.members``
instead of ``Group.users``? Read on!

Changing class names
~~~~~~~~~~~~~~~~~~~~

Changing the name of an auth-related class (``User``, ``Group`` or ``Permission``)
is a rather simple task. Just rename it in your model, and then make sure to
update the parameters you pass to :func:`setup_sql_auth` accordingly.

Changing attribute names
~~~~~~~~~~~~~~~~~~~~~~~~

You can also change the name of the attributes assumed by
:mod:`repoze.what` in your auth-related classes, such as renaming
``User.groups`` to ``User.memberships``.

Changing such values is what :mod:`repoze.what` calls "translating".
You may set the translations for the attributes of the models
:mod:`repoze.what` deals with in a dictionary passed to :func:`setup_sql_auth`
as its ``translations`` parameters. For
example, if you want to replace ``Group.users`` by ``Group.members``, you may
use the following translation dictionary::

    translations['users'] = 'members'

These are the translations you may set in ``base_config.sa_auth.translations``:
    * ``user_name``: The translation for the attribute in ``User.user_name``.
    * ``users``: The translation for the attribute in ``Group.users``.
    * ``group_name``: The translation for the attribute in ``Group.group_name``.
    * ``groups``: The translation for the attribute in ``User.groups`` and
      ``Permission.groups``.
    * ``permission_name``: The translation for the attribute in
      ``Permission.permission_name``.
    * ``permissions``: The translation for the attribute in ``User.permissions``
      and ``Group.permissions``.
    * ``validate_password``: The translation for the method in
      ``User.validate_password``.
