***************************
:mod:`repoze.what` releases
***************************

.. currentmodule:: repoze.what

This document describes the releases of :mod:`repoze.what` 1.1.X. You can also
`check the 1.0.X releases <http://what.repoze.org/docs/1.0/News.html>`_.


.. _version-1-1-0:

Version 1.1.0 (*unreleased*)
============================

New or enhanced stuff
---------------------

* Added support for Access Control Lists.
* Predicate checkers can now be evaluated with a :class:`webob.Request` object
  instead of the WSGI environment dictionary.
* The predicates :class:`is_user <predicates.is_user>`, :class:`not_anonymous
  <predicates.not_anonymous>`, :class:`is_anonymous <predicates.is_anonymous>`,
  :class:`is_anonymous <predicates.in_group>`, :class:`in_all_groups
  <predicates.in_all_groups>`, :class:`in_any_group <predicates.in_any_group>`,
  :class:`has_permission <predicates.has_permission>`,
  :class:`has_all_permissions <predicates.has_all_permissions>` and
  :class:`has_any_permission <predicates.has_any_permission>`
  have all been renamed to their CamelCase versions and aliases for the old
  names have been added to keep backwards compatibility.
* Added aliases for instances of nullary predicates:
  :data:`AUTHENTICATED <predicates.AUTHENTICATED>` and :data:`ANONYMOUS
  <predicates.ANONYMOUS>`.
* Predicates can now be negated with a tilde. The following expressions are now
  equivalent::
  
      predicate = Not(IsUser("foo"))
      predicate = ~IsUser("foo")
  
* Predicates can now be joint pythonically, without using the :class:`Any
  <repoze.what.predicates.Any>` or :class:`All <repoze.what.predicates.All>`
  predicates. For example, the following conjunctive operations are equivalent::
  
      predicate = IsUser("foo") & has_permission("bar")
      predicate = All(IsUser("foo"), has_permission("bar"))
  
  And the following disjunctive operations are equivalent too::
  
      predicate = IsUser("foo") | IsUser("bar")
      predicate = Any(IsUser("foo"), IsUser("bar"))
  
* Now groups and permissions are loaded on demand, as long as you use the new
  :mod:`repoze.who` independent middleware.
* Predicate checkers should preferably return a boolean value from now on::

      class FromLocalhost(Predicate):
          """Predicate to check whether the user comes from the local host."""
          
          def check(self, request, credentials):
              return request.remote_addr == "127.0.0.1"
  
  See :meth:`repoze.what.predicates.Predicate.check`.
  
* Added :mod:`benchmarking utilities for the source adapters
  <repoze.what.adapters.benchmark>`.


Bug fixes
---------

* When a section was renamed, the adapter didn't check if the new name was
  in use. `Bug #68 <http://bugs.repoze.org/issue68>`_.
* Fixed a typo in the documentation. Reported by Jonás Melián.
* Fixed a typo in a test of the :mod:`repoze.what.adapters.testutil` module,
  in which a variable is misspelled. It became visible when that test failed.
  Reported by Jonás Melián.


Deprecations
------------

The following things still work, but don't expect to see them in eventual v1.2
or v2 releases:

* :meth:`~repoze.what.predicates.Predicate.is_met` has been superseded by
  :meth:`repoze.what.predicates.Predicate.__call__`.
* Predicate checkers should not have messages associated anymore. Now they are
  not only used to grant authorization conditionally: Thanks to the ACL support,
  they can also be used to deny authorization conditionally. So such a message
  would only make sense in one of these situations.
  
  This value should have never been coupled with the logic that verifies a
  given condition anyway. It was also useless in many situations, since its value
  got lost when a compound predicate was formed.
  
  From now on, predicates checkers should define
  :meth:`~repoze.what.predicates.Predicate.check` and return a boolean value.
  
  To be precise, the following methods in :class:`repoze.what.predicates.Predicate`
  are deprecated:
  :meth:`~repoze.what.predicates.Predicate.unmet`,
  :meth:`~repoze.what.predicates.Predicate.evaluate`, and
  :meth:`~repoze.what.predicates.Predicate.check_authorization`, as well as the
  predicate related exceptions
  :class:`~repoze.what.predicates.PredicateError` and
  :class:`~repoze.what.predicates.NotAuthorizedError`.


Backwards incompatible changes
------------------------------

Support has been dropped for the following long deprecated things:

* The :meth:`repoze.what.predicates.Predicate._eval_with_environ` method. Make
  sure none of your predicates define this method; if they do, upgrade them to
  :meth:`repoze.what.predicates.Predicate.check`.
* The :meth:`repoze.what.predicates.Predicate.eval_with_environ` method. Make
  sure it didn't use to get called in your application; if it does, replace it
  by calling the predicate checker object -- But keep in mind it returns a value,
  instead of raising an exception.
* The :mod:`repoze.what.authorize` module. If you call
  :func:`repoze.what.authorize.check_authorization` somewhere, again, replace it
  by calling the predicate checker object.

