**********************************
Controlling access with predicates
**********************************

:Status: Official

.. module:: repoze.what.predicates
    :synopsis: repoze.what predicates checkers
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>
.. moduleauthor:: Florent Aide <florent.aide@gmail.com>
.. moduleauthor:: Agendaless Consulting and Contributors

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
        A class that checks whether a :term:`predicate` is met.

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
        message = 'The current month must be %(right_month)s and it is ' \
                  '%(this_month)s'
        
        def __init__(self, right_month, **kwargs):
            self.right_month = right_month
            super(is_month, self).__init__(**kwargs)
        
        def evaluate(self, environ, credentials):
            # Let's calculate the current day on every evaluation because
            # the application may be running for many days; hence it's not
            # defined once in the constructor.
            today = date.today()
            if today.month != self.right_month:
                # Raise an exception because the predicate is not met.
                self.unmet(this_month=today.month)

Then you can use your predicate this way::

    # Grant access if the current month is March
    p = is_month(3)

.. note::

    When you create a predicate, don't try to guess/assume the context in
    which the predicate is evaluated when you write the predicate message
    because such a predicate may be used in a different context.
    
    * Bad: "The software can be released if it's %(right_month)s".
    * Good: "The current month must be %(right_month)s".


Built-in predicate checkers
===========================

These are the predicate checkers that are included with
:mod:`repoze.what`:

.. autoclass:: Predicate
    :members: __init__, evaluate, unmet, check_authorization, is_met, _eval_with_environ


Single predicate checkers
-------------------------

.. autoclass:: not_anonymous

.. autoclass:: is_user

.. autoclass:: in_group

.. autoclass:: in_all_groups

.. autoclass:: in_any_group

.. autoclass:: has_permission

.. autoclass:: has_all_permissions

.. autoclass:: has_any_permission

.. autoclass:: Not


Compound predicate checkers
---------------------------

You may create a `compound predicate` by aggregating single (or even compound)
predicate checkers with the functions below:

.. autoclass:: All

.. autoclass:: Any


But you can also nest compound predicates::

    p = All(Any(is_month(4), is_month(10)), has_permission('release'))

Which may be translated as "Anyone granted the 'release' permission may release 
a version of Ubuntu, if and only if it's April or October".


Evaluating your predicates
==========================

Predicates are used to define how to control access and you evaluate them
to verify that the required conditions are met for the subject to access the
requested resource.

There are two ways to check predicates:

Raising an exception if the predicate is not met
------------------------------------------------

If you need to enforce that to access the requested resource the predicate
must be met, you should use :meth:`Predicate.check_authorization` because it
will raise an exception if it's not met.

For example, if you have a sensitive function that should be run by certain
users, you may use it at the start of the function as in the example below::

    # ...
    from repoze.what.predicates import has_permission
    # ...
    environ = give_me_the_wsgi_environ()
    # ...
    
    def add_comment(post_id, comment):
        has_permission('post-comment').check_authorization(environ)
        # If reached this point, then the user *can* leave a comment!
        new_comment = Comment(post=post_id, comment=comment)
        save(new_comment)

The exception raised is :class:`NotAuthorizedError`:

.. autoclass:: NotAuthorizedError

.. autoclass:: PredicateError

Web frameworks may provide utilities to make it easier to check authorization
this way. For example, the TurboGears framework provides the ``@require`` 
decorator for actions, which can be used as in the example below::

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
the WSGI environment to :meth:`Predicate.check_authorization`. The framework 
also catches the exception and replaces it with a 401 HTTP error and a error 
message visible to the user.

Getting a boolean after the predicate evaluation
------------------------------------------------

If you want to control access on a portion of the resource, not in the whole
resource, you may want to avoid the exception 
:meth:`Predicate.check_authorization` would raise if the predicate that 
controls that portion is not met. For example, you may want to display a given
message if the user is not anonymous.

This is where :meth:`Predicate.is_met` would come into play. You can use it as
in the code below::

    # ...
    from repoze.what.predicates import has_permission, in_group
    # ...
    environ = give_me_the_wsgi_environ()
    # ...
    
    def add_comment(post_id, comment):
        has_permission('post-comment').check_authorization(environ)
        # If reached this point, then the user *can* leave a comment!
        new_comment = Comment(post=post_id, comment=comment)
        save(new_comment)
        if in_group('customer').is_met(environ):
            print_message('Dear customer, thank you for your comment!')


:mod:`repoze.what.authorize`
============================

.. module:: repoze.what.authorize
    :synopsis: repoze.what authorization utilities

Before :meth:`Predicate.check_authorization`, predicates were evaluated with
:func:`check_authorization` where you wanted to restrict access. That function 
was run before performing the protected procedure so that it can raise the 
:class:`NotAuthorizedError` exception if the user was not authorized:

.. autofunction:: check_authorization

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
