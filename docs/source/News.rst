**********************************************************
:mod:`repoze.what` and :mod:`repoze.what.plugins` releases
**********************************************************

This document describes the releases of :mod:`repoze.what` and its official
plugins.


.. _repoze.what-1.0b1:

:mod:`repoze.what` 1.0b1 (*unreleased*)
=======================================

This is the first release of this package as part of the Repoze project. It
started as the :mod:`repoze.who` extension for TurboGears 2 applications
(:mod:`tg.ext.repoze.who`, doing authenticatication and authorization) by 
Florent Aide and Agendaless Consulting, then Gustavo Narea took over the 
project to make it deal with authorization only and add support to store 
`groups` and `permissions` in other types of sources (among other things) 
under the :mod:`tgext.authorization` namespace, but finally it was turned into
a Repoze project in order to make it available in arbitrary WSGI applications.

* Removed dependencies on TurboGears and Pylons.
* Introduced a framework-independent function 
  (:func:`repoze.what.authorize.check_authorization`) to check authorization 
  based on a predicate and the WSGI environment, along with the
  :class:`repoze.what.authorize.NotAuthorizedError` exception.
* Now :mod:`repoze.what` is fully documented.
* Now you can override the error message of the built-in predicates or set your
  own message at instantiation time by passing the ``msg`` keywork argument to
  the predicate. Example::
  
      from repoze.what.authorize import is_user
      
      my_predicate = is_user('carla', msg="You must be Carla to come here!")
      
  As a result, if your custom predicate defines the constructor method
  (``__init__``), then you're highly encouraged to call its parent with the
  ``msg`` keyword argument. Example::
  
      from repoze.what.authorize import Predicate
      
      class MyCoolPredicate(Predicate):
          def __init__(self, **kwargs):
              super(MyCoolPredicate, self).__init__(**kwargs)
  
* Moved the SQL plugin (:mod:`repoze.what.plugins.sql`) into a separate
  package. Also moved :mod:`repoze.what.plugins.quickstart` into that package
  because it's specific to the SQL plugin.


Backwards-incompatible changes
------------------------------

* If you have custom predicates, you should update the ``eval_with_object`` 
  method, which has been renamed to ``eval_with_environ`` and only receives one 
  argument (the WSGI environment). This is, if your method's signature looks 
  like this::

      eval_with_object(obj, errors)

  Now it should look like this::
  
      _eval_with_environ(environ)
  
  Note that ``errors`` are no longer passed.
* The :func:`repoze.what.authorize.require` decorator has been removed because 
  it's specific to TurboGears. TurboGears 2 applications will find it at
  :func:`tg.require`.

Because this is the first beta release, there should not be more backwards
incompatible changes in the coming 1.X releases.
