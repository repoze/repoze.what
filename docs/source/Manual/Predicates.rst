**********************************
Controlling access with predicates
**********************************

:Status: Official

.. module:: repoze.what.predicates
    :synopsis: repoze.what predicates.
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>
.. moduleauthor:: Florent Aide <florent.aide@gmail.com>
.. moduleauthor:: Agendaless Consulting and Contributors

.. topic:: Overview

    This document explains how to implement authorization in the action 
    controllers of your WSGI application.


You are ready to use authorization in your controllers once you
have setup the required middleware, either through the quickstart or in a
custom way.

Overview
========

:mod:`repoze.what` allows you to define access rules based on so-called
"predicate checkers":

.. glossary::

    predicate
         A ``predicate`` is the condition that must be met for the user to be 
         able to access the requested source (e.g., "The current user is not 
         anonymous").
    compound predicate
        A :term:`predicate`, or condition, may be made up of more predicates 
        -- those are called `compound predicates` (e.g., "The user is not 
        anonymous `and` her IP address belongs to the company's intranet").
    predicate checker
        A class that checks whether a :term:`predicate` is met.

If a user is not logged in, or does not have the proper permissions, the
application throws a 401 (HTTP Unauthorized) which is caught by the
:mod:`repoze.who` middleware to display the login page allowing
the user to login, and redirecting the user back to the proper page when they
are done.

For example, if you have a predicate which is "grant access to any authenticated
user", then you can use the following built-in predicate checker::

    from repoze.what.predicates import not_anonymous
    
    p = not_anonymous(msg='Please login to access this area')

Or if you have a predicate which is "allow access to root or anyone with the
'manage' permission", then you may use the following built-in predicate
checker::

    from repoze.what.predicates import Any, is_user, has_permission
    
    p = Any(is_user('root'), has_permission('manage'),
            msg='You must be root or have the "manage" permission')

As you may have noticed, predicates receive the ``msg`` keyword argument to
use its value as the error message if the predicate is not met. It's optional
and if you don't define it, the built-in predicates will use the default
English message; you may take advantage of this funtionality to make such
messages translatable.


Creating your own single predicate checkers
===========================================

You may create your own predicate checkers if the built-in ones are not enough 
to achieve a given task.

To do so, you should extend the :class:`repoze.what.predicates.Predicate`
class. For example, if your predicate is "The current month is the 
specified one", your predicate checker may look like this::

    from datetime import date
    from repoze.what.predicates import Predicate
    
    class is_month(Predicate):
        error_message = 'You can only come here if the current month is %(right_month)s'
        
        def __init__(self, right_month, **kwargs):
            self.right_month = right_month
            self.today = date.today()
            super(is_month, self).__init__(**kwargs)
        
        def _eval_with_environ(self, environ):
            return self.today.month == self.right_month

Then you can use your predicate this way::

    # Grant access if the current month is March
    p = is_month(3)


Built-in predicate checkers
===========================

These are the predicate checkers that are included with
:mod:`repoze.what`:

.. class:: Predicate(msg=None)

    :param msg: The error message, if you want to override the default one
        defined by the predicate.
    :type msg: str

    The base predicate class. It won't do anything useful for you, unless you
    subclass it.


Single predicate checkers
-------------------------

.. class:: not_anonymous()

    Check that the current user has been authenticated.
    
    Example::
    
        # The user must have been authenticated!
        p = not_anonymous()

.. class:: is_user(user_name)
    
    Check that the authenticated user's username is the specified one.
    
    :param user_name: The required user name.
    :type user_name: str
    
    Example::
    
        p = is_user('linus')

.. class:: in_group(group_name)

    Check that the user belongs to the specified group.
    
    :param group_name: The name of the group to which the user must belong.
    :type group_name: str
    
    Example::
    
        p = in_group('customers')

.. class:: in_all_groups(group1_name, group2_name[, group3_name ...])

    Check that the user belongs to all of the specified groups.
    
    :param group1_name: The name of the first group the user must belong to.
    :param group2_name: The name of the second group the user must belong to.
    :param group3_name ...: The name of the other groups the user must belong to.
    
    Example::
    
        p = in_all_groups('developers', 'designers')

.. class:: in_any_group(group1_name, [group2_name ...])

    Check that the user belongs to at least one of the specified groups.
    
    :param group1_name: The name of the one of the groups the user may belong to.
    :param group2_name ...: The name of other groups the user may belong to.
    
    Example::
    
        p = in_any_group('directors', 'hr')

.. class:: has_permission(permission_name)

    Check that the current user has the specified permission.
    
    :param permission_name: The name of the permission that must be granted to 
        the user.
    
    Example::
    
        p = has_permission('hire')

.. class:: has_all_permissions(permission1_name, permission2_name[, permission3_name...])

    Check that the current user has been granted all of the specified 
    permissions.
    
    :param permission1_name: The name of the first permission that must be
        granted to the user.
    :param permission2_name: The name of the second permission that must be
        granted to the user.
    :param permission3_name ...: The name of the other permissions that must be
        granted to the user.
    
    Example::
    
        p = has_all_permissions('view-users', 'edit-users')

.. class:: has_any_permission(permission1_name[, permission2_name ...])

    Check that the user has at least one of the specified permissions.
    
    :param permission1_name: The name of one of the permissions that may be
        granted to the user.
    :param permission2_name ...: The name of the other permissions that may be
        granted to the user.
    
    Example::
    
        p = has_any_permission('manage-users', 'edit-users')


Compound predicate checkers
---------------------------

You may create a `compound predicate` by aggregating single (or even compound)
predicate checkers with the functions below:

.. class:: All(predicate1, predicate2[, predicate3 ...])

    Check that all of the specified predicates are met.
    
    :param predicate1: The first predicate that must be met.
    :param predicate2: The second predicate that must be met.
    :param predicate3 ...: The other predicates that must be met.
    
    Example::
    
        # Grant access if the current month is July and the user belongs to
        # the human resources group.
        p = All(is_month(7), in_group('hr'))

.. class:: Any(predicate1[, predicate2 ...])

    Check that at least one of the specified predicates is met.
    
    :param predicate1: One of the predicates that may be met.
    :param predicate2 ...: Other predicates that may be met.
    
    Example::
    
        # Grant access if the currest user is Richard Stallman or Linus
        # Torvalds.
        p = Any(is_user('rms'), is_user('linus'))


But you can also nest compound predicates::

    p = All(Any(is_month(4), is_month(10)), has_permission('release'))

Which translates as "Anyone granted the 'release' permission may release a 
version of Ubuntu, if and only if it's April or October".


Evaluating your predicates
==========================

.. module:: repoze.what.authorize
    :synopsis: repoze.what authorization utilities

Predicates are useless by themselves -- you should use
:func:`check_authorization` where you want to restrict 
access. That function must be run before performing the protected procedure
so that it can raise the :class:`NotAuthorizedError` exception if the user
is not authorized:

.. function:: check_authorization(predicate, environ)

    :param predicate: The predicate to be evaluated.
    :param environ: The WSGI environment.
    :raise NotAuthorizedError: If it the predicate is not met.
    
    Verify if the current user really can access the requested source.

For example, if you have a sensitive function that should be run by certain
users, you may use it at the start of the function as in the example below::

    # ...
    from repoze.what.authorize import check_authorization
    from repoze.what.predicates import has_permission
    # ...
    environ = give_me_the_wsgi_environ()
    # ...
    
    def add_comment(post_id, comment):
        check_authorization(has_permission('post-comment'), environ)
        # If reached this point, then the user *can* leave a comment!
        new_comment = Comment(post=post_id, comment=comment)
        save(new_comment)

Web frameworks may provide utilities to make it easier to check authorization.
For example, the TurboGears framework provides the ``@require`` decorator for 
actions, which is a wrapper for :func:`check_authorization` -- it can be used 
as in the example below::

    # ...
    from tg import require
    # ...
    from repoze.what.predicates import has_permission
    # ...
    
    class BlogController(BaseController):
        # ...
        @expose('coolproject.templates.blog')
        @require(has_permission('post-comment'))
        def add_comment(self, post_id, comment):
            new_comment = Comment(post=post_id, comment=comment)
            save(new_comment)

As you may have noticed, it's a more elegant solution because the predicate is
defined outside of the method itself and the framework automatically passes 
the WSGI environment to :func:`check_authorization`. The framework also catches
the exception and replaces it with a 401 HTTP error and a error message visible
to the user.

.. class:: NotAuthorizedError(errors)

    :param errors: The error messages for the predicates that were not met.
    
    Exception raised by :func:`check_authorization` if the user is not allowed
    to access the request source.
