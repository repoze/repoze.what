**********************************************************
:mod:`repoze.what` and :mod:`repoze.what.plugins` releases
**********************************************************

This document describes the releases of :mod:`repoze.what` and its official
plugins.


.. _repoze.what-1.0b2:

:mod:`repoze.what` 1.0b2 (*unreleased*)
===================================================

* Added support for read-only sources. See 
  :class:`repoze.what.adapters.BaseSourceAdapter`.
* Added :mod:`generic utilities for testing plugins <repoze.what.testutil>`.
  That module used to be part of the :mod:`repoze.what` test suite.

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


.. _repoze.what-sql-1.0b1:

:mod:`repoze.what.plugins.sql` 1.0a2 (*unreleased*)
===================================================

* Fixed the broken test suite for Elixir, thanks to Helio Pereira.
* Updated :func:`repoze.what.plugins.quickstart.setup_sql_auth` according
  to the backwards incompatible change on 
  :func:`repoze.what.middleware.setup_auth` introduced in 
  :ref:`repoze.what-1.0b2`.

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
