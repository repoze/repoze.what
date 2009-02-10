*******************************************
Creating your own single predicate checkers
*******************************************

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


Creating a predicate checker more sensitive to the request
----------------------------------------------------------

Authorization always depends on the context and :mod:`repoze.what` predicates
are no exception. Access is controlled based on who the current user is, what
groups she belongs to, what permissions she is granted, what her IP address is,
what day is today and so on -- and such data are always provided by the
context.

The context is a wide term which doesn't only include information about *who*
makes the request, but also about *what* is requested and *how* the request is
made (represented by the WSGI environment), *when* it is requested and possibly
include external conditions.

With :mod:`repoze.what` predicates, you can control access based on any of the
parts that make up the context (described above). However, this framework 
mostly helps you control access based on *who* the user is (her credentials),
while gives you a hand to control access based on *what* is requested and 
*how* by passing the WSGI environ to the predicate checker
(:meth:`Predicate.parse_variables 
<repoze.what.predicates.Predicate.parse_variables>` exists to help you with the 
*what* too). Writing predicates based on *when* it is requested and external 
conditions (if any) is completely up to you.

For example, if to allow users edit posts in a blog you don't only want 
the predicate "the current user is granted the ``edit-posts`` permission" 
(*who* makes the request) to be met, but also "the current user is the author 
of the post in question" (*what* is requested), you may write the latter as::

    from repoze.what.predicates import Predicate
    # Say you use SQLAlchemy:
    from yourcoolapplication.model import BlogPost, DBSession
    
    class post_is_managed_by_author(Predicate):
        message = 'Only %(author)s can manage post %(post_id)s'
        
        def evaluate(self, environ, credentials):
            # Extracting the post Id from the GET variables
            vars = self.parse_variables(environ)
            post_id = vars['get'].get('post_id')
            # Loading the post object
            post = DBSession.query(BlogPost).get(post_id)
            # Checking if it's the author
            if post.author_userid != credentials.get('repoze.what.userid'):
                self.unmet(post_id=post_id, author=post.author_userid)

If you don't use the :meth:`Predicate.parse_variables 
<repoze.what.predicates.Predicate.parse_variables>` method, you would have
to import and use `Paste <http://pythonpaste.org/>`_'s 
:func:`paste.request.parse_querystring` and/or 
:func:`paste.request.parse_formvars` functions whenever authorization depends 
on *what* is requested.

Finally, you would end up with the following compound predicates::

    from repoze.what.predicates import All, has_permission
    # Can the user edit the post?
    p = All(has_permission('edit-post'), post_is_managed_by_author())
    # Can the user delete the post?
    p2 = All(has_permission('delete-posts'), post_is_managed_by_author())

.. note::
    
    If you're using a dispatcher like `Routes <http://routes.groovie.org/>`_ or
    `Selector <http://lukearno.com/projects/selector/>`_ and the variables you
    need are not passed in the query string nor as POST variables, you will
    find them in the dictionary returned by :meth:`Predicate.parse_variables 
    <repoze.what.predicates.Predicate.parse_variables>`, either in the 
    ``positional_args`` or ``named_args`` items -- check the
    `wsgiorg.routing_args specification
    <http://www.wsgi.org/wsgi/Specifications/routing_args>`_ for more
    information.
