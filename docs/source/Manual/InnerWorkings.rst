****************************************
The inner-workings of :mod:`repoze.what`
****************************************

.. module:: repoze.what.middleware
    :synopsis: repoze.what WSGI middleware
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

.. topic:: Overview

    :mod:`repoze.what` doesn't provide WSGI middleware per se. Instead, it 
    configures and re-uses :mod:`repoze.who`'s.

Middleware-related components are defined in the :mod:`repoze.what.middleware`
module. It contains one function to configure :mod:`repoze.who` with support
for :mod:`repoze.what` and the :mod:`repoze.who` metadata provider that loads
authorization-related data in the :mod:`repoze.who` ``identity`` and the
:mod:`repoze.what` ``credentials`` dictionaries.

.. warning::

    In :mod:`repoze.what` v2, the ``userid``, groups and permissions will only 
    be loaded in the :mod:`repoze.what` ``credentials`` dictionary 
    (``environ['repoze.what.credentials']``). So you are encouraged not to 
    access this data from the :mod:`repoze.who` ``identity`` -- if you do so, 
    you will have to update your code when you want to upgrade to v2.

.. autofunction:: setup_auth


WSGI environment variables
==========================

:mod:`repoze.what` defines and uses the following WSGI environment variables:

* ``repoze.what.credentials``: It contains authorization-related data about the
  current user (it's similar to :mod:`repoze.who`'s ``identity``). It is
  a dictionary made up of the following items: ``userid`` (the user name of
  the current user, if not anonymous; copied from
  ``environ['repoze.who.identity']['repoze.who.userid']`` in :mod:`repoze.what`
  v1.X), ``groups`` (tuple of groups to which the currrent user belongs) and 
  ``permissions`` (tuple of permissions granted to such groups).
  
  .. warning::
  
      Do **not** access this dictionary directly, use a :term:`predicate
      checker` instead. **This variable is internal** and the disposal or 
      availability of its items may change at any time.
  
* ``repoze.what.adapters``: It contains the available :term:`source adapters
  <source adapter>`, if any. It's a dictionary made up of the following items:
  ``groups`` (dictionary of :term:`group adapters <group adapter>`) and 
  ``permissions`` (dictionary of :term:`permission adapters 
  <permission adapter>`).

.. warning::

    Because :mod:`repoze.what` 1.X works as a :mod:`repoze.who` metadata
    provider, the variables above are defined if and only if the current user
    is not anonymous. This limitation will not exist in :mod:`repoze.what` v2,
    since it will have its own middleware.
