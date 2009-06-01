repoze.what plugins performance comparison
==========================================

This directory contains all the files required to compared the performance of
the following repoze.what adapters:

 * SQL/SQLAlchemy (repoze.what.plugins.sql).
 * XML (repoze.what.plugins.xml).
 * Redis (repoze.what.plugins.redis).

repoze.what.plugins.ini plugin could not be included because at present it's
a read-only adapter.

Files
-----

 * runbenchmarks.py: The script which will run and compare the benchmarks.
 * config.py: The configuration file for the benchmarks. Feel free to override
   the default settings.
 * plugins_setup.py: Contains the adapters to be compared. Feel free to add or
   remove adapters, or even modify their individual settings.
 * sa_model.py: Contains the SQLAlchemy model definitions used by the SQL
   adapters.
 * groups.xml and permissions.xml: The mock sources for the XML adapters.
