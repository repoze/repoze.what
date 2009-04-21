***************************
:mod:`repoze.what` releases
***************************

This document describes the releases of :mod:`repoze.what`.


.. _repoze.what-2.0a1:

:mod:`repoze.what` 2.0a1 (*unreleased*)
=======================================

* Removed :mod:`repoze.who` dependency.
* Reorganized many modules from v1:
  * Created the :mod:`repoze.what.patterns` namespace package for support
    for the different authorization patterns in :mod:`repoze.what` v2, either
    as built-in packages or third-party plugins.
  * Predicates for the groups/permissions-based authorization pattern were
    moved from :mod:`repoze.what.predicates` to 
    :mod:`repoze.what.patterns.groups.predicates`.
  * :mod:`repoze.what.authorize` is gone. Its ``check_authorization`` function
    is defined as a method of the predicate (the way it should've had been)
    and its ``NotAuthorizedError`` exception is now at 
    :class:`repoze.what.predicates.base.NotAuthorizedError` (it replaces
    :class:`repoze.what.predicates.base.PredicateError`).
  * :mod:`repoze.what.adapters.testutil` was been moved to
    :mod:`repoze.what.testutils.adapters`.
* Changed the way predicates are evaluated:
  * Predicate checkers are now evaluated by passing three positional
    arguments: The userid, the WebOb ``Request`` object for the current
    request and the new repoze.what "helpers" dict.
  * :meth:`repoze.what.predicates.Predicate.parse_variables` is gone because
    of the use of WebOb.
* Introduced :meth:`repoze.what.predicates.Predicate.is_met`.
* Now :meth:`repoze.what.predicates.Predicate.unmet` receives an optional
  argument to override the error message.
* The manual was reorganized and updated accordingly and the API documentation
  is now available in a separate section.
