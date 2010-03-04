***************************
:mod:`repoze.what` releases
***************************

This document describes the releases of :mod:`repoze.what`.

.. _repoze.what-1.0.9:

:mod:`repoze.what` 1.0.9 (2010-03-04)
=====================================

* Pin ``repoze.who`` to versions <= 1.99 (2.0a1 is incompatible).

* Made tests compatible with released :mod:`repoze.who` 1.0.x.

.. _repoze.what-1.0.8:

:mod:`repoze.what` 1.0.8 (2009-03-14)
=====================================

* Fixed problem with `routing_args 
  <http://www.wsgi.org/wsgi/Specifications/routing_args>`_ compliance in
  :meth:`repoze.what.predicates.Predicate.parse_variables`; a wrong structure
  of that variable was assumed.
* Fixed small internal problem with the credentials dictionary.

.. _repoze.what-1.0.7:

:mod:`repoze.what` 1.0.7 (2009-03-13)
=====================================

* Added the :class:`is_anonymous <repoze.what.predicates.is_anonymous>`
  predicate.


.. _repoze.what-1.0.6:

:mod:`repoze.what` 1.0.6 (2009-03-05)
=====================================

* The deprecated :func:`repoze.what.authorize.check_authorization` didn't
  evaluate predicates correctly if predicates were :func:`booleanized
  <repoze.what.plugins.pylonshq.booleanize_predicates>`. Thanks to
  Michael Brickenstein!
  
  .. attention:: **Don't panic!**
      This can hardly affect somebody on the earth: If you're using
      :func:`repoze.what.authorize.check_authorization` directly, then you're 
      not using Pylons, and if you're not using Pylons, then you're not using
      :mod:`repoze.what-pylons <repoze.what.plugins.pylonshq>`.
      
      However, this does affect you if you're not on the earth, use
      :func:`repoze.what.authorize.check_authorization` and "booleanize
      predicates" in your non-Pylons-based framework ;-)


.. _repoze.what-1.0.5:

:mod:`repoze.what` 1.0.5 (2009-03-02)
=====================================

* To ease testing, now :func:`repoze.what.middleware.setup_auth` uses
  :func:`repoze.who.plugins.testutil.make_middleware` instead of calling
  :class:`repoze.who.middleware.PluggableAuthenticationMiddleware` directly.
* Now non-ASCII messages can be logged without problems in Python < 2.6. Thanks
  to Christoph Zwerschke (`TG Issue #2250 
  <http://trac.turbogears.org/ticket/2250>`_).
* Minor updates in the documentation.


.. _repoze.what-1.0.4:

:mod:`repoze.what` 1.0.4 (2009-02-06)
=====================================

* Now request-sensitive predicate checkers are easier to write because of the
  introduction of the :meth:`repoze.what.predicates.Predicate.parse_variables`
  method, which is aware of the `wsgiorg.routing_args specification
  <http://www.wsgi.org/wsgi/Specifications/routing_args>`_.
* Now :meth:`repoze.what.predicates.Predicate.unmet` receives an optional
  argument to override the error message. This feature is backported from v2.
* Backported :meth:`repoze.what.predicates.Predicate.is_met` from
  :mod:`repoze.what` v2.
* Improved the :term:`predicates <predicate checker>` section in the manual.
* For forward compatibility with :mod:`repoze.what` v2, the
  :mod:`repoze.what.authorize` module is deprecated. If you want to use
  :mod:`repoze.what` v2, you should start using 
  :meth:`repoze.what.predicates.Predicate.check_authorization` and
  :class:`repoze.what.predicates.NotAuthorizedError` instead of
  :meth:`repoze.what.authorize.check_authorization` and
  :class:`repoze.what.authorize.NotAuthorizedError`, respectively.


.. _repoze.what-1.0.3:

:mod:`repoze.what` 1.0.3 (2009-01-28)
=====================================

This is a bug fix release, there is no new feature implemented.

* For forward compatibility with v2, the latest version of the Ini, SQL and
  XML :term:`group adapters <group adapter>` rely on the ``repoze.what.userid``
  key in the :mod:`repoze.what` ``credentials`` dictionary. However, 
  :mod:`repoze.what` was passing the :mod:`repoze.who` ``identity`` to them
  instead of its ``credentials`` dict.


.. _repoze.what-1.0.2:

:mod:`repoze.what` 1.0.2 (2009-01-23)
=====================================

For forward compatibility with :mod:`repoze.what` v2.0, :mod:`predicates
<repoze.what.predicates>` should define the :meth:`evaluate
<repoze.what.predicates.Predicate.evaluate>` method which deprecates
:meth:`_eval_with_environ <repoze.what.predicates.Predicate._eval_with_environ>`
as of this release.

This indirectly fixes a thread-safety bug found by Alberto Valverde on
:class:`Any <repoze.what.predicates.Any>`-based predicates when used along
with :class:`All <repoze.what.predicates.All>`-based ones. Thank you very much
once again, Alberto!


.. _repoze.what-1.0.1:

:mod:`repoze.what` 1.0.1 (2009-01-21)
=====================================

This release fixes an important bug which *may* affect production Web
sites depending on how you use the ``All`` predicate or any of its
derivatives (``has_all_permissions`` and ``in_all_groups``). TurboGears 2 
applications are all affected, at least by default.

The likelihood that this will affect your application is very high, so 
upgrading is highly recommended if it's on production.

* Some :mod:`repoze.what` :mod:`predicates <repoze.what.predicates>` were not 
  thread-safe when they were instantiated in a module and then shared among
  threads (as used in TurboGears 2). This was found by and solved with the
  help of `Alberto Valverde <http://albertovalverde.es/>`_ (¡Gracias, 
  Alberto!).
  
  We fixed this by making 
  :meth:`repoze.what.predicates.Predicate.eval_with_predicate` raise an
  exception if the predicate is not met, instead of returning a boolean and
  setting the ``error`` instance attribute of the predicate to the predicate
  failure message.
  
  So if you are using that method directly, instead of using
  :func:`repoze.what.authorize.check_authorization`, this is a backwards
  incompatible change for you and thus you should update your code. If you
  check predicates like this (which is discouraged; see
  :func:`repoze.what.authorize.check_authorization`)::
  
      from repoze.what.predicates import is_user, in_group, All
      
      p = All(is_user('someone'), in_group('some-group'))
      environ = gimme_the_environ()
      
      if p.eval_with_environ(environ):
          print('Authorization is denied: %s' % p.error)
      else:
          print('Authorization is granted')
  
  Then you should update your code like this::
  
      # This way of checking predicates is DISCOURAGED. Use
      # repoze.what.authorize.check_authorization() instead.
      from repoze.what.predicates import is_user, in_group, All, PredicateError
      
      p = All(is_user('someone'), in_group('some-group'))
      environ = gimme_the_environ()
      
      try:
          p.eval_with_environ(environ)
          print('Authorization is granted')
      except PredicateError, error:
          print('Authorization is denied: %s' % error)
  
  .. note::
  
      Because of this, TurboGears 2 users who want to use this release, should 
      try the latest revision in the TG2 Subversion repository or wait for 
      TurboGears-2.0b4. But again, there's no hurry if your application is not
      in production.
  
* For forward compatibility with :mod:`repoze.what` v2, the user id used in
  the built-in predicates is that found in 
  ``environ['repoze.what.credentials']['repoze.what.userid']`` and the adapters
  loaded are now available at ``environ['repoze.what.adapters']``. This is
  *not* a backwards incompatible change.


.. _repoze.what-1.0:

:mod:`repoze.what` 1.0 (2009-01-19)
===================================

This is the first stable release of :mod:`repoze.what` and it was announced
on the `Repoze blog 
<http://blog.repoze.org/repoze-what-1-dot-oh-20090119.html>`_.

* Fixed a problem with unicode support in
  :func:`repoze.what.authorize.check_authorization`, reported by Chen Houwu on
  TurboGears mailing list.
* Added the current user's groups and permissions to the newly-created
  ``environ['repoze.what.credentials']`` dictionary for forward compatibility 
  with :mod:`repoze.what` v2. Such values are still defined in the 
  :mod:`repoze.who` ``identity`` dictionary, but its use is highly discouraged 
  as of this release. See :mod:`repoze.what.middleware`.
* Applied work-around to fix Python v2.4 and v2.5 support.


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
