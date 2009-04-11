*********************************************************
:mod:`repoze.what` -- Authorization for WSGI applications
*********************************************************

.. module:: repoze.what
    :synopsis: Authorization framework for WSGI applications
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

:Author: Gustavo Narea.
:Latest version: |release|

.. topic:: Overview

    :mod:`repoze.what` is an extensible **authorization** framework for WSGI
    arbitrary applications.
    
    TODO: Continue


Features
========

Unless mentioned otherwise, the following features are available in
:mod:`repoze.what` and its official plugins:

* ``Web framework independent``. You can use it on any WSGI 
  application and any WSGI framework (or no framework at all).
* ``Authorization only``. It doesn't try to be an all-in-one auth
  monster -- it will only do `authorization` and nothing else.
* ``Highly extensible``. It's been created with extensibility in mind, so
  that it won't get in your way and you can control authorization however you
  want or need, either with official components, third party plugins or your
  own plugins.
* ``Fully documented``. If it's not described in the manual, it doesn't exist.
  Everything is documented along with examples.
* ``Reliable``. We are committed to keep the code coverage at 100%.
* It works with Python 2.4, 2.5 and 2.6.
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
  allow access if the user belongs to the "ABC" organization), as well as
  the ability to re-use LDAP `Organizational Units` as groups.
* Enable a highly extensible `CAPTCHA <http://en.wikipedia.org/wiki/CAPTCHA>`_
  driven authorization mechanism to restrict access to a given resource 
  (possibly the hardest to create plugin).
* Store groups in ``Htgroups``.


.. _install:

How to install
==============

To install :mod:`repoze.what` v2, run::

    easy_install repoze.what

The development mainline is available at the following Subversion repository::

    http://svn.repoze.org/repoze.what/trunk/


Framework-specific documentation
================================

The following documents will help you implement :mod:`repoze.what` in your
framework (if any):

* **Nothing yet**.

If you have written documents to implement :mod:`repoze.what` in a web
framework, please `let us know <http://lists.repoze.org/listinfo/repoze-dev>`_
to get a link here.

How to get help?
================

The prefered place to ask questions is the `Repoze mailing list 
<http://lists.repoze.org/listinfo/repoze-dev>`_ or the `#repoze 
<irc://irc.freenode.net/#repoze>`_ IRC channel. Bugs reports and feature 
requests should be sent to `the issue tracker of the Repoze project 
<http://bugs.repoze.org/>`_.


Contents
========

.. toctree::
    :maxdepth: 2

    Manual/index
    API/index
    News
    Participate


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
