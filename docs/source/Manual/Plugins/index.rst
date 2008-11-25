:mod:`repoze.what.plugins` -- Available plugins for :mod:`repoze.what`
======================================================================

:Status: Official

.. module:: repoze.what.plugins
    :synopsis: repoze.what plugins
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

.. topic:: Overview

    :mod:`repoze.what` itself strives to be a rather minimalist project which
    only depends on :mod:`repoze.who` and built-in Python modules, so that
    it will never get in your way and thus make it rather easy for third parties
    to extend it to suit their needs.
    
    As a consequence, it doesn't ship with support for :term:`adapters
    <source adapter>`, so you should install the relevant plugins to manage your 
    groups and permissions.

There are three types of plugins:

.. glossary::

    adapters plugin
        It's a plugin that provides one :term:`group adapter` and/or one 
        :term:`permission adapter` for a given back-end, but it may also 
        provide additional functionality specific to said back-end. 
        
        For example, the SQL plugin provides group and permission adapters
        that enable you to store your groups and permissions in databases, 
        as well as a module with some utilities to get started with 
        :mod:`repoze.who` and :mod:`repoze.what` very quickly.
    
    predicates plugin
        It's a plugin that provides one or more :term:`predicate checkers
        <predicate checker>`.
        
        For example, the network plugin will provide :term:`predicate checkers
        <predicate checker>` to make sure that only people from the intranet
        can access certain parts of a web site.
    
    extras plugin
        It's a plugin that enables a functionality not available in
        :mod:`repoze.what` out-of-the-box (other than providing :term:`adapters
        <source adapter>` or :term:`predicate checkers <predicate checker>`).
        
        For example, the quickstart (:mod:`repoze.what.plugins.quickstart`).

The classification above is not mutually exclusive: If a plugin provides
:term:`adapters <source adapter>`, :term:`predicate checkers <predicate 
checker>` and extra functionality, then it can be referred to as "a predicates,
adapters and extras plugin". For instance, the SQL plugin is both an adapters
and extras plugin.

The following plugins are currently available:

.. toctree::
    :maxdepth: 2

    SQL

