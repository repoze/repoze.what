**************************
Evaluating your predicates
**************************

Evaluating a predicate is to check whether it is met or not. There are two
ways of evaluating predicates, and which one should you use depends on the
situation:

Raising an exception if the predicate is not met
------------------------------------------------

If you need to enforce that to access the requested resource the predicate
must be met, you should use :meth:`Predicate.check_authorization
<repoze.what.predicates.Predicate.check_authorization>` because it
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

The exception raised is :class:`repoze.what.predicates.NotAuthorizedError`.

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
the WSGI environment to :meth:`Predicate.check_authorization
<repoze.what.predicates.Predicate.check_authorization>`. The framework 
also catches the exception and replaces it with a 401 HTTP error and a error 
message visible to the user.

Finding if it's met or not
--------------------------

If you want to control access on a portion of the resource, not in the whole
resource, you may want to avoid the exception 
:meth:`Predicate.check_authorization
<repoze.what.predicates.Predicate.check_authorization>` would raise if the 
predicate that controls that portion is not met. For example, you may want to 
grant access to a given page if the user has the "post-comment" permission, 
but only display a polite message if she belongs to the "customer" group.

This is where :meth:`Predicate.is_met
<repoze.what.predicates.Predicate.is_met>` would come into play. You can use 
it as in the code below::

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
            print_message('Dear customer, thanks for your comment!')


:mod:`repoze.what.authorize`
============================

.. module:: repoze.what.authorize
    :synopsis: repoze.what authorization utilities

Before :meth:`Predicate.check_authorization
<repoze.what.predicates.Predicate.check_authorization>`, predicates were 
evaluated with :func:`check_authorization` where you wanted to restrict access.
That function was run before performing the protected procedure so that it can 
raise the :class:`NotAuthorizedError
<repoze.what.predicates.NotAuthorizedError>` exception if the user was not 
authorized:

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
