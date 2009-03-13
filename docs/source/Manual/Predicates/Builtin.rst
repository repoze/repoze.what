***************************
Built-in predicate checkers
***************************

.. module:: repoze.what.predicates
    :synopsis: repoze.what predicates checkers

These are the predicate checkers that are included with :mod:`repoze.what`:


The base :class:`Predicate` class
=================================

:class:`Predicate` is the parent class of every predicate checker and its API
is described below:

.. autoclass:: Predicate
    :members: __init__, evaluate, unmet, check_authorization, is_met, parse_variables, _eval_with_environ


Single predicate checkers
=========================

.. autoclass:: is_user

.. autoclass:: not_anonymous

.. autoclass:: is_anonymous

.. autoclass:: in_group

.. autoclass:: in_all_groups

.. autoclass:: in_any_group

.. autoclass:: has_permission

.. autoclass:: has_all_permissions

.. autoclass:: has_any_permission

.. autoclass:: Not


Compound predicate checkers
===========================

You may create a `compound predicate` by aggregating single (or even compound)
predicate checkers with the functions below:

.. autoclass:: All

.. autoclass:: Any


But you can also nest compound predicates::

    p = All(Any(is_month(4), is_month(10)), has_permission('release'))

Which may be translated as "Anyone granted the 'release' permission may release 
a version of Ubuntu, if and only if it's April or October".


Predicate errors
================

.. autoclass:: NotAuthorizedError

.. autoclass:: PredicateError
