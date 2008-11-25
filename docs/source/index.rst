:mod:`repoze.what` -- Authorization for WSGI applications
=========================================================

.. module:: repoze.what
    :synopsis: Authorization framework for WSGI applications
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

:Author: Gustavo Narea.
:Latest version: |release|

.. topic:: Overview

    :mod:`repoze.what` is an `authorization framework` for WSGI applications,
    based on :mod:`repoze.who` (which deals with `authentication`).
    
    On the one hand, it enables an authorization system based on the groups to 
    which the `authenticated or anonymous` user belongs and the permissions 
    granted to such groups by loading these groups and permissions into the 
    request on the way in to the downstream WSGI application.
    
    And on the other hand, it enables you to manage your groups and permissions
    from the application itself or another program, under a backend-independent 
    API. For example, it would be easy for you to switch from one back-end to 
    another, and even use this framework to migrate the data.
    
    It's highly extensible, so it's very unlikely that it will get in your way.
    Among other things, you can extend it to check for many other conditions 
    (such as checking that the user comes from a given country, based on her IP 
    address, for example).


Features
========

Unless mentioned otherwise, the following features are available in
:mod:`repoze.what` and its official plugins:

* ``Web framework independent``. You can use it on any WSGI 
  application and any WSGI framework (or no framework at all). Web frameworks
  may provide integration with it (like `TurboGears 2 
  <http://turbogears.org/2.0/docs/>`_, which features a strong integration with 
  :mod:`repoze.what`).
* ``Authorization only``. It doesn't try to be an all-in-one auth
  monster -- it will only do `authorization` and nothing else.
* ``Highly extensible``. It's been created with extensibility in mind, so
  that it won't get in your way and you can control authorization however you
  want or need, either with official components, third party plugins or your
  own plugins.
* ``Fully documented``. If it's not described in the manual, it doesn't exist.
* ``Reliable``. We are committed to keep the code coverage at 100%.
* ``Control access to any resource``. Although it's only recommended to control
  authorization on action controllers, you can also use it to restrict access
  to other things in your package (e.g., only allow access to a database table
  if the current user is the admin).
* Your application's `groups` and `permissions` may be stored in an SQLAlchemy
  managed database, thanks to the SQL plugin (:mod:`repoze.what.plugins.sql`).
* The only requirement is that you use the powerful and extensible `repoze.who
  <http://static.repoze.org/whodocs/>`_ authentication framework.
* `It's not hard to get started!`


And according to `the to-do list
<http://bugs.repoze.org/issue?@columns=title,id,activity,status,assignedto&@sort=activity&@group=priority&@filter=topic,status&topic=13&status=-1,1,2,3,4,5,6,7>`_, 
we *will* have official plugins to:

* Enable `OAuth <http://oauth.net/>`_ support.
* Enable authorization based on certain network conditions 
  (e.g., grant access if the user's IP address belongs to a given IP range,
  deny access if the user's host name is "example.org", grant access based on 
  the user's ISP).
* Enable authorization based on `client-side SSL certificates 
  <http://en.wikipedia.org/wiki/X.509>`_ (e.g., allow access if the
  `Certificate Authority` is XYZ, allow access if the user is called "John
  Smith" or "Foo Bar").
* Enable authorization based on LDAP attributes of the authenticated user's
  entry (e.g., allow access if the user can be reached at a cellular phone,
  allow access if the user belongs to the "ABC" organization).
* Enable a highly extensible `CAPTCHA <http://en.wikipedia.org/wiki/CAPTCHA>`_
  driven authorization mechanism to restrict access to a given resource 
  (possibly the hardest to create plugin).
* Store groups in ``Htgroups`` and ``ini`` files, and re-use LDAP
  `Organizational Units` as groups. 
* Store permissions in ``ini`` files.


.. _install:

How to install
==============

The only requirement of :mod:`repoze.what` is :mod:`repoze.who` and you can
install both by running::

    easy_install repoze.what

The development mainline is available at the following Subversion repository::

    http://svn.repoze.org/repoze.what/trunk/


How to get help?
================

The prefered place to ask questions is the `Repoze mailing list 
<http://lists.repoze.org/listinfo/repoze-dev>`_ or the `#repoze 
<irc://irc.freenode.net/#repoze>`_ IRC channel. Bugs reports and feature 
requests should be sent to `the issue tracker of the Repoze project 
<http://bugs.repoze.org/>`_.

If you have problems, please don't forget to include the output of your 
application with the ``AUTH_LOG`` environment variable set to ``1`` when you
get in touch with us. For example, if your application is based on TurboGears 
or Pylons, you may run it with the following command::

    AUTH_LOG=1 paster serve --reload development.ini


Contents
========

.. toctree::
    :maxdepth: 2

    Manual/index
    News
    Participate


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
