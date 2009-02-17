**********************************************************************
:mod:`repoze.what.plugins` -- Available plugins for :mod:`repoze.what`
**********************************************************************

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
:term:`adapters <source adapter>`, :term:`predicate checkers 
<predicate checker>` and extra functionality, then it can be referred to as 
"a predicates, adapters and extras plugin". For instance, the :mod:`SQL plugin
<repoze.what.plugins.sql>` is both an adapters and extras plugin because
it provides the :mod:`quickstart <repoze.what.plugins.quickstart>` plugin.

Available :term:`adapters plugins <adapters plugin>`
====================================================

============================== ================ =============== ================ ====================
      Plugin name                 Source type    Write support   Groups adapter   Permissions adapter
============================== ================ =============== ================ ====================
repoze.what.plugins.ini [#f1]_  ``.ini`` files        No               Yes                Yes
:mod:`repoze.what.plugins.sql`       SQL             Yes               Yes                Yes
:mod:`repoze.what.plugins.xml`     XML files         Yes               Yes                Yes
============================== ================ =============== ================ ====================


Available :term:`predicates plugins <predicates plugin>`
========================================================

None, yet.


Available :term:`extras plugins <extras plugin>`
================================================

====================================== ===========================================================================================================
             Plugin name                  Description
====================================== ===========================================================================================================
:mod:`repoze.what.plugins.quickstart`   Pre-configured authentication system to get started with :mod:`repoze.who` and :mod:`repoze.what` quickly
:mod:`repoze.what.plugins.pylonshq`    :mod:`repoze.what` utilities for Pylons/TG2 applications
repoze.what.plugins.config [#f2]_       Configure :mod:`repoze.what` from an ``Ini`` file with Paste Deploy.
====================================== ===========================================================================================================


.. rubric:: Footnotes

.. [#f1] `repoze.what Ini plugin 
    <http://github.com/jdinuncio/repoze.what.plugins.ini/wikis>`_, written by 
    José Dinuncio.

.. [#f2] `repoze.what Config plugin 
    <http://github.com/jdinuncio/repoze.what.plugins.config/tree/master>`_, 
    written by José Dinuncio.
    