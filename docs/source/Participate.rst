*****************************************************
Participate in the development of :mod:`repoze.what`!
*****************************************************

.. topic:: Overview

    Here you will learn how you may contribute to :mod:`repoze.what`, either
    extending it or fixing issues.


Sending patches
===============

Please feel free to send patches to fix bugs or implement features, but keep
in mind that it will take some time to get applied if it doesn't follow our
basic `coding conventions`_. If you can, please include the respective tests
too.

Patches should be sent to `the Repoze mailing list
<http://lists.repoze.org/listinfo/repoze-dev>`_.


Writing plugins
===============

An important way to contribute to :mod:`repoze.what` is by creating
:mod:`plugins <repoze.what.plugins>`.

There are no special guidelines to create unofficial plugins, but you are
highly encouraged to create plugins under the :mod:`repoze.what.plugins`
namespace and contact us once you have at least one usable release (so that
we can mention it in the manual).


Guidelines for official plugins
-------------------------------

Official plugins must meet certain requirements:

* It must use `the Repoze license <http://repoze.org/license.html>`_.
* It should follow the `coding conventions`_ of the project.
* Its documentation should be merged into the official documentation.

If you want to turn your :mod:`repoze.what` unofficial plugin into an official
one and you are willing to make it meet the requirements above, please
propose it after you have at least one usable release (e.g., a beta, a
release candidate; not only pre-alphas) -- The rate of `stillborn` Free
Software projects is very high, so we prefer to turn a unofficial plugin
into an official one if it has ever seen the light.

Coding conventions
==================

The basic coding conventions for :mod:`repoze.what` are not special at all --
they are basically the same you will find in other Python projects:

* The character encoding should be UTF-8.
* Lines should not contain more than 80 characters.
* The new line character should be the one used in Unix systems (``\n``).
* Stick to the `widely` used `Style Guide for Python Code
  <http://www.python.org/dev/peps/pep-0008/>`_ and `Docstring Conventions
  <http://www.python.org/dev/peps/pep-0257/>`_.

However, we have the following additional coding conventions which should be
applied in the first beta release of a package `at the latest` (this is, they
are not strictly necessary in alpha releases):

* The unit test suite for the package should cover 100% of the code. `People
  entrust us with nothing less than the authorization control of their
  application`, so we should take this additional security step to deserve
  their trust. Sure, it won't make the package 100% bug-free (that's
  impossible), but at least we'll avoid regression bugs effectively and
  we'll be sure that a bug found will be an unwritten test. It shouldn't be
  hard for you if you practice the Test-Driven Development methodology.
* `All` the public components of the package should be properly documented
  along with examples, so that people won't have to dive into our code to
  learn how to achieve what they want.
