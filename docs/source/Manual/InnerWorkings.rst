****************************************
The inner-workings of :mod:`repoze.what`
****************************************

.. module:: repoze.what.middleware
    :synopsis: repoze.what WSGI middleware
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

:Status: Official

.. topic:: Overview

    :mod:`repoze.what` doesn't provides WSGI middleware per se. Instead, it 
    configures and re-uses :mod:`repoze.who`'s.

Middleware-related components are defined in the :mod:`repoze.what.middleware`
module. It contains one function to configure :mod:`repoze.who` with support
for :mod:`repoze.what` and the :mod:`repoze.who` metadata provider that loads
authorization-related data in the :mod:`repoze.who` ``identity`` and the
:mod:`repoze.what` ``credentials`` dictionaries.

.. warning::

    In :mod:`repoze.what` v2, the groups and permissions will only be loaded
    in the :mod:`repoze.what` ``credentials`` dictionary 
    (``environ['repoze.what.credentials']``). So you are encouraged not to 
    access this data from the :mod:`repoze.who` ``identity`` -- if you do, 
    you will have to update your code when you want to upgrade to v2.

.. autofunction:: setup_auth
