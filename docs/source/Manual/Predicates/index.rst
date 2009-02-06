**********************************
Controlling access with predicates
**********************************

.. topic:: Overview

    This document explains how to restrict access within your application
    by using :term:`predicates <predicate>`, which you will be
    able to use  once you have setup the required middleware, either through 
    the quickstart or in a custom way.

:mod:`repoze.what` allows you to define access rules based on so-called
"predicate checkers":

.. glossary::

    predicate
         A ``predicate`` is the condition that must be met for the subject to be 
         able to access the requested source (e.g., "The current user is not 
         anonymous").
    compound predicate
        A :term:`predicate`, or condition, may be made up of more predicates 
        -- those are called `compound predicates` (e.g., "The user is not 
        anonymous `and` her IP address belongs to the company's intranet").
    predicate checker
        A class that checks whether a :term:`predicate` is met. It must
        extend :class:`repoze.what.predicates.Predicate`.

If a user is not logged in, or does not have the proper permissions, the
application throws a 401 (HTTP Unauthorized) which is caught by the
:mod:`repoze.who` middleware to display the login page allowing
the user to login, and redirecting the user back to the proper page when they
are done.

For example, if you have a predicate above ("The user is not anonymous"), 
then you can use the following built-in predicate checker::

    from repoze.what.predicates import not_anonymous
    
    p = not_anonymous(msg='Only logged in users can read this post')

Or if you have a predicate which is "The current user is root and/or somebody 
with the 'manage' permission", then you may use the following built-in predicate
checkers::

    from repoze.what.predicates import Any, is_user, has_permission
    
    p = Any(is_user('root'), has_permission('manage'),
            msg='Only administrators can remove blog posts')

As you may have noticed, predicates receive the ``msg`` keyword argument to
use its value as the error message if the predicate is not met. It's optional
and if you don't define it, the built-in predicates will use the default
English message; you may take advantage of this funtionality to make such
messages translatable.

.. note::

    Good predicate messages don't explain `what` went wrong; instead, they 
    describe the predicate in the current context (regardless of whether
    the condition is met or not!). This is because such messages may be used in 
    places other than in a user-visible message (e.g., in the log file).
    
    * Really bad: "Please login to access this area".
    * Bad: "You cannot delete an user account because you are not an 
      administrator".
    * OK: "You have to be an administrator to delete user accounts".
    * Perfect: "Only administrators can delete user accounts".


More on predicates
==================
.. toctree::
    :maxdepth: 2

    Builtin
    Evaluating
    Writing
