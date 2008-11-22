Restricting access with :mod:`repoze.what.authorize`
====================================================

:Status: Official

.. module:: repoze.what.authorize
    :synopsis: Authorization in application's controllers and action controllers.
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>
.. moduleauthor:: Florent Aide <florent.aide@gmail.com>
.. moduleauthor:: Agendaless Consulting and Contributors

.. topic:: Overview

    This document explains how to implement authorization in the action 
    controllers of your WSGI application. The code snippets shown here have 
    been tested with TurboGears 2, but should also work with Pylons and other 
    frameworks (`write to us <http://lists.repoze.org/listinfo/repoze-dev>`_ 
    if you know of a framework in which they don't work).


You are ready to use authorization in your controllers once you
have setup the required middleware, either through the quickstart or in a
custom way.

All you need to implement it is defined in the 
:mod:`repoze.what.authorize` module.

.. contents:: Table of Contents
    :depth: 3


Action-level authorization
--------------------------

:mod:`repoze.what.authorize` provides you with utilities to control 
authorization on a per-action controller basis, so that you can restrict access
in certain action controllers to certain users.

For example, to restrict access in a private page to the users that belong to
the "manage" group, you may use a code like this::

    # ...
    from repoze.what import authorize
    
    class MyController(BaseController):
        # ...
        @authorize.require(authorize.has_permission('manage'))
        # authorize.has_permission() is a predicate checker function; read on!
        def manage_permission_only(self, **kw):
            return dict()
        # ...

Or to make sure that those who leave comments on a news site are registered
users, you make use something like this::

    # ...
    from repoze.what import authorize
    
    class MyController(BaseController):
        # ...
        @authorize.require(authorize.not_anonymous())
        def leave_comment(self, **kw):
            return dict()
        # ...

Authorization may not only be based on single conditions -- you may use
a `compound predicate` when more conditions must be met (read on to learn about
them!).


Controller-level authorization
------------------------------

The TurboGears 2 framework allows to define controller-wide predicates, although
:mod:`repoze.what` `will eventually ship with a function that will work in any
framework <http://bugs.repoze.org/issue45>`_.

In the mean time, the work-around is to define the same `require`
decorator with the same parameters in every action controller of the controller
in question, as shown in the following code snippet::

    class MySecureController(MyFrameworkBaseController):
        # ...
        
        @authorize.require(authorize.not_anonymous())
        def leave_comment(self, **kw):
            return dict()
        
        @authorize.require(authorize.not_anonymous())
        def send_trackback(self, **kw):
            return dict()
        
        @authorize.require(authorize.not_anonymous())
        def see_staff(self, **kw):
            return dict()
        
        # ...


Predicates
----------

A predicate is the condition that must be met for the user to be able to access
the requested action controller. Such a predicate, or condition, may be made
up of more predicates -- those are called `compound predicates`. Action
controllers, or controllers, may have only one predicate, be it single or
compound.

If a user is not logged in, or does not have the proper permissions, the 
predicate checker throws a 403 (HTTP Not Authorized) which is caught by the 
:mod:`repoze.what` middleware which displays the login page allowing 
the user to login, and redirecting the user back to the proper page when they 
are done.


Built-in single predicate checkers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are the predicate checkers that are included with
:mod:`repoze.what`:

.. class:: not_anonymous()

    Check that the current user has been authenticated.
    
    Example::
    
        # ...
        @authorize.require(authorize.not_anonymous())
        def leave_comment(self, **kw):
            return dict()

.. class:: is_user(user_name)
    
    Check that the authenticated user's user name is the specified one.
    
    :param user_name: The required user name.
    :type user_name: str
    
    Example::
    
        # ...
        @authorize.require(authorize.is_user('linus'))
        def release_kernel_version(self, **kw):
            flash('Hello Linus!')
            return dict()

.. class:: in_group(group_name)

    Check that the user belongs to the specified group.
    
    :param group_name: The name of the group to which the user must belong.
    :type group_name: str
    
    Example::
    
        # ...
        @authorize.require(authorize.in_group('customers'))
        def customers_only(self, **kw):
            flash('Hello dear customer!')
            return dict()

.. class:: in_all_groups(group1_name, group2_name[, group3_name ...])

    Check that the user belongs to all of the specified groups.
    
    :param group1_name: The name of the first group the user must belong to.
    :param group2_name: The name of the second group the user must belong to.
    :param group3_name ...: The name of the other groups the user must belong to.
    
    Example::
    
        # ...
        @authorize.require(authorize.in_all_groups('developers', 'designers'))
        def edit_javascript(self, **kw):
            return dict()

.. class:: in_any_group(group1_name, [group2_name ...])

    Check that the user belongs to at least one of the specified groups.
    
    :param group1_name: The name of the one of the groups the user may belong to.
    :param group2_name ...: The name of other groups the user may belong to.
    
    Example::
    
        # ...
        @authorize.require(authorize.in_any_group('directors', 'hr'))
        def hire_person(self, person_name):
            flash('%s is hired!' % person_name)
            return dict()

.. class:: has_permission(permission_name)

    Check that the current user has the specified permission.
    
    :param permission_name: The name of the permission that must be granted to 
        the user.
    
    Example::
    
        # ...
        @authorize.require(authorize.has_permission('hire'))
        def hire_person(self, person_name):
            flash('%s is hired!' % person_name)
            return dict()

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
    
        # ...
        @authorize.require(authorize.has_all_permissions('view-users', 'edit-users'))
        def edit_user(self, user_name, new_username):
            flash('%s is now %s!' % (user_name, new_username))
            return dict()

.. class:: has_any_permission(permission1_name[, permission2_name ...])

    Check that the user has at least one of the specified permissions.
    
    :param permission1_name: The name of one of the permissions that may be
        granted to the user.
    :param permission2_name ...: The name of the other permissions that may be
        granted to the user.
    
    Example::
    
        # ...
        @authorize.require(authorize.has_any_permission('manage-users', 'edit-users'))
        def edit_user(self, user_name, new_username):
            flash('%s is now %s!' % (user_name, new_username))
            return dict()


Custom single predicate checkers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may create your own predicate checkers if the built-in ones are not enough 
to achieve a given task.

To do so, you should extend the :class:`repoze.what.authorize.Predicate`
class. For example, if your predicate is "Check that the current month is the 
specified one", your predicate checker may look like this::

    from datetime import date
    from repoze.what.authorize import Predicate
    
    class is_month(Predicate):
        error_message = 'You cannot access this page this month'
        
        def __init__(self, month):
            self.month = month
            self.today = date.today()
        
        def _eval_with_environ(self, environ):
            if today.month == self.month:
                return True
            return False

If you defined that class in, say, ``{yourproject}.lib.auth``, you may use it
as in this example::

    # ...
    from spain_travels.lib.auth import is_month
    # ...
    class SummerVacations(BaseController):
        # ...
        @authorize.require(is_month(7))
        def start_vacations():
            flash('Have fun!')
            dict()
        # ...


Built-in compound predicate checkers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may create a `compound predicate` by aggregating single (or even compound)
predicate checkers with the functions below:

.. class:: All(predicate1, predicate2[, predicate3 ...])

    Check that all of the specified predicates are met.
    
    :param predicate1: The first predicate that must be met.
    :param predicate2: The second predicate that must be met.
    :param predicate3 ...: The other predicates that must be met.
    
    Example::
    
        # ...
        from yourproject.lib.auth import is_month
        # ...
        @authorize.require(authorize.All(
                                         is_month(7),
                                         authorize.in_group('hr')))
        def allow_vacations(self, employee_name):
            flash('%s can take vacations!' % employee_name)
            return dict()

.. class:: Any(predicate1[, predicate2 ...])

    Check that at least one of the specified predicates is met.
    
    :param predicate1: One of the predicates that may be met.
    :param predicate2 ...: Other predicates that may be met.
    
    Example::
    
        # ...
        @authorize.require(authorize.Any(
                                         authorize.is_user('rms'),
                                         authorize.is_user('linus')))
        def release_gnu_linux(self, **kwargs):
            return dict()


But you can also nest compound predicates::

    # ...
    from yourproject.lib.auth import is_month
    # ...
    @authorize.require(authorize.All(
                                     Any(is_month(4), is_month(10)),
                                     authorize.has_permission('release')
                                     ))
    def release_ubuntu(self, **kwargs):
        return dict()
    # ...

Which translates as "Anyone granted the 'release' permission may release a 
version of Ubuntu, if and only if it's April or October".
