****************************************
The inner-workings of :mod:`repoze.what`
****************************************

TODO


WSGI environment variables
==========================

:mod:`repoze.what` defines and uses the following WSGI environment variables:

* ``repoze.what.credentials``: It contains authorization-related data about the
  current user (it's similar to :mod:`repoze.who`'s ``identity``). It is
  a dictionary made up of the following items: ``userid`` (the user name of
  the current user, if not anonymous), ``groups`` (tuple of groups to which 
  the currrent user belongs) and ``permissions`` (tuple of permissions granted
  to such groups).
* ``repoze.what.adapters``: It contains the available :term:`source adapters
  <source adapter>`, if any. It's a dictionary made up of the following items:
  ``groups`` (dictionary of :term:`group adapters <group adapter>`) and 
  ``permissions`` (dictionary of :term:`permission adapters 
  <permission adapter>`).
