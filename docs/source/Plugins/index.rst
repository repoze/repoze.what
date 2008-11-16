:mod:`repoze.what.plugins` -- Available plugins for ``repoze.what``
===================================================================================

:Status: Draft

.. module:: repoze.what.plugins
    :synopsis: repoze.what plugins
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

.. topic:: Overview

    Plugins extend the functionality of :mod:`repoze.what` and the most
    common type of plugins are those that add support for more type of group and
    permission sources.


:mod:`repoze.what` itself doesn't ship with support for :term:`adapters`, so 
you should install the relevant plugins to manage your groups and permissions.

A plugin may provide one :term:`group adapter` and/or one :term:`permission
adapter` for a given back-end, but it may also provide additional functionality
specific to such a back-end.

The following plugins are currently available:

.. toctree::
    :maxdepth: 2

    SQL

