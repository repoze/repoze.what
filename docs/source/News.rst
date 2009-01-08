***************************
:mod:`repoze.what` releases
***************************

This document describes the releases of :mod:`repoze.what`.


.. _repoze.what-1.0rc3:

:mod:`repoze.what` 1.0rc3 (*unreleased*)
========================================

* Fixed a problem with unicode support in
  :func:`repoze.what.authorize.check_authorization`, reported by Chen Houwu on
  TurboGears mailing list.
* Added the current user's groups and permissions to the newly-created
  ``environ['repoze.what.identity']`` dictionary for forward compatibility with
  :mod:`repoze.what` v2. Such values are still defined in the :mod:`repoze.who`
  identity dictionary, but its use is highly discouraged as of this release.
  See :mod:`repoze.what.middleware`.


.. _repoze.what-1.0rc2:

:mod:`repoze.what` 1.0rc2 (2008-12-20)
======================================

* Fixed the constructor of the :class:`Not <repoze.what.predicates.Not>`
  predicate, which didn't call its parent and therefore it was not possible
  to specify a custom message.
* From now on, predicates that are not met will have only *one* error message,
  even in compound predicates. It didn't make sense to have a list of errors
  and thus this behavior has been changed in this release. This will affect
  you if you deal with :func:`repoze.what.authorize.check_authorization`
  directly and handled the errors of
  :class:`repoze.what.authorize.NotAuthorizedError` as in::
  
    try:
        check_authorization(predicate, environ)
    except NotAuthorizedError, exc:
        for error in exc.errors:
            print error
  
  The code above may be updated this way::
  
    try:
        check_authorization(predicate, environ)
    except NotAuthorizedError, exc:
        print exc
  
  .. note::
  
    This doesn't affect TurboGears 2 users because TG itself deals with this
    function and it's already updated to work with :mod:`repoze.what` 1.0rc2.
    Keep in mind that for this release to work on TurboGears 2, you need
    TurboGears 2 Beta 1 (not yet released as of this writing) or the latest
    revision in the repository.
* For forward compatibility, it's no longer mandatory to use the
  groups/permissions-based authorization pattern in order to use
  :mod:`repoze.what`. This package should support several authorization 
  patterns and they must all be optional, such as the upcoming support for
  roles-based authorization in :mod:`repoze.what` 1.5. As a result, now you
  can skip the definition of group and permission adapters and use
  :func:`repoze.what.middleware.setup_auth` as a simple proxy for
  :class:`repoze.who.middleware.PluggableAuthenticationMiddleware`::
  
      app_with_auth = setup_auth(
          app,
          identifiers=identifiers,
          challengers=challengers,
          mdproviders=mdproviders,
          classifier=classifier,
          challenge_decider=challenge_decider
          )

.. _repoze.what-1.0rc1:

:mod:`repoze.what` 1.0rc1 (2008-12-10)
======================================

* Added support for read-only adapters in the :mod:`testutil
  <repoze.what.adapters.testutil>` with the :class:`ReadOnlyGroupsAdapterTester
  <repoze.what.adapters.testutil.ReadOnlyGroupsAdapterTester>` and
  :class:`ReadOnlyPermissionsAdapterTester
  <repoze.what.adapters.testutil.ReadOnlyPermissionsAdapterTester>` test cases.
* Fixed Python 3 deprecation warnings.


.. _repoze.what.plugins.ini:

:mod:`repoze.what.plugins.ini` -- Ini adapters available (2008-12-09)
=====================================================================

José Dinuncio has made a *great* work writing :term:`group <group adapter>` 
and :term:`permission <permission adapter>` adapters for Ini files! So, thanks
to him, now it's not only possible to store your groups and permissions in
databases, but also in files!

 * Link: http://github.com/jdinuncio/repoze.what.plugins.ini/


.. _repoze.what-1.0b2:

:mod:`repoze.what` 1.0b2 (2008-12-04)
=====================================

* Added support for read-only sources. See
  :class:`repoze.what.adapters.BaseSourceAdapter`.

Backwards-incompatible changes
------------------------------
* The signature of :func:`repoze.what.middleware.setup_auth` has changed:
  Now it simply receives the WSGI application, the group adapters and the
  permissions adapters -- additional keyword arguments will be sent to
  :class:`repoze.who.middleware.PluggableAuthenticationMiddleware`. Also, it
  no longer defines a default identifier or challenger.

  .. note::

      It's very unlikely that this affects your application, as that function
      is normally used by :func:`repoze.what.plugins.quickstart.setup_sql_auth`.


.. _repoze.what-1.0b1:

:mod:`repoze.what` 1.0b1 (2008-11-26)
=====================================

This is the first release of this package as part of the Repoze project. It
started as the :mod:`repoze.who` extension for TurboGears 2 applications
(:mod:`tg.ext.repoze.who`, doing authenticatication and authorization) by
Chris McDonough, Florent Aide and Christopher Perkins, then Gustavo Narea took
over the project to make it deal with authorization only and add support to
store `groups` and `permissions` in other types of sources (among other things)
under the :mod:`tgext.authorization` namespace, but finally it was turned into
a Repoze project in order to make it available in arbitrary WSGI applications.

* Removed dependencies on TurboGears and Pylons.
* Introduced a framework-independent function
  (:func:`repoze.what.authorize.check_authorization`) to check authorization
  based on a predicate and the WSGI environment, along with the
  :class:`repoze.what.authorize.NotAuthorizedError` exception.
* Now :mod:`repoze.what` is 100% documented.
* Moved the predicates from :mod:`repoze.what.authorize` to
  :mod:`repoze.what.predicates`. Nevertheless, they are imported in the former
  to avoid breaking TurboGears 2 applications created when
  :mod:`tg.ext.repoze.who` or :mod:`tgext.authorization` existed.
* Added the :class:`Not <repoze.what.predicates.Not>` predicate.
* Now you can override the error message of the built-in predicates or set your
  own message at instantiation time by passing the ``msg`` keywork argument to
  the predicate. Example::

      from repoze.what.predicates import is_user

      my_predicate = is_user('carla', msg="Only Carla may come here")

  As a result, if your custom predicate defines the constructor method
  (``__init__``), then you're highly encouraged to call its parent with the
  ``msg`` keyword argument. Example::

      from repoze.what.predicates import Predicate

      class MyCoolPredicate(Predicate):
          def __init__(self, **kwargs):
              super(MyCoolPredicate, self).__init__(**kwargs)

* Moved the SQL plugin (:mod:`repoze.what.plugins.sql`) into a separate
  package. Also moved :mod:`repoze.what.plugins.quickstart` into that package
  because it's specific to the SQL plugin.
* Log messages are no longer sent to standard output if the ``WHO_LOG``
  environment variable is defined, but with ``AUTH_LOG``.
* Now :mod:`repoze.what` uses logging internally to ease debugging.

Backwards-incompatible changes
------------------------------

* If you have custom predicates, you should update the ``eval_with_object``
  method, which has been renamed to ``_eval_with_environ`` and only receives one
  argument (the WSGI environment). This is, if your method's signature looks
  like this::

      eval_with_object(obj, errors)

  Now it should look like this::

      _eval_with_environ(environ)

  Note that ``errors`` are no longer passed.

  On the other hand, the ``error_message`` attribute of predicates has been
  renamed to ``message`` because they are not only used to display errors
  (see :mod:`repoze.what.predicates`).
* The :func:`repoze.what.authorize.require` decorator has been removed because
  it's specific to TurboGears. TurboGears 2 applications will find it at
  :func:`tg.require`.

Because this is the first beta release, there should not be more backwards
incompatible changes in the coming 1.X releases.
