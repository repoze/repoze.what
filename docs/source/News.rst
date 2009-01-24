***************************
:mod:`repoze.what` releases
***************************

This document describes the releases of :mod:`repoze.what`.


.. _repoze.what-2.0a1:

:mod:`repoze.what` 2.0a1 (*unreleased*)
=======================================

* Reorganized many modules from v1:
  * Created the :mod:`repoze.what.patterns` namespace package for support
    for the different authorization patterns in :mod:`repoze.what` v2, either
    as built-in packages or third-party plugins.
  * Predicates for the groups/permissions-based authorization pattern were
    moved from :mod:`repoze.what.predicates` to 
    :mod:`repoze.what.patterns.groups.predicates`.
