# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Ready-to-use adapters.

"""
from redis import Redis

from repoze.what.plugins.redis import RedisGroupAdapter, RedisPermissionAdapter
from repoze.what.plugins.xml import XMLGroupsAdapter, XMLPermissionsAdapter

from sa_model import make_benchmarks

__all__ = ["group_adapters", "permission_adapters"]

group_adapters = {}
permission_adapters = {}

#{ Adapters setup

# XML:
group_adapters['xml'] = XMLGroupsAdapter("groups.xml")
permission_adapters['xml'] = XMLPermissionsAdapter("permissions.xml")

# Redis:
group_adapters['redis'] = RedisGroupAdapter(Redis())
permission_adapters['redis'] = RedisPermissionAdapter(Redis())

# SQLAlchemy + SQLite (memory backend):
sqlite_mem_groups, sqlite_mem_permissions = make_benchmarks("sqlite://")
group_adapters['sqlite_memory'] = sqlite_mem_groups
permission_adapters['sqlite_memory'] = sqlite_mem_permissions

# SQLAlchemy + SQLite (file backend):
sqlite_file_groups, sqlite_file_permissions = make_benchmarks("sqlite:///whatbench.db")
group_adapters['sqlite_file'] = sqlite_file_groups
permission_adapters['sqlite_file'] = sqlite_file_permissions

# SQLAlchemy + MySQL (InnoDB tables)
innodb_tables = "mysql://whatbench@localhost/whatbench"
mysql_innodb_groups, mysql_innodb_permissions = make_benchmarks(innodb_tables,
                                                                mysql_engine="InnoDB")
group_adapters['mysql_innodb'] = mysql_innodb_groups
permission_adapters['mysql_innodb'] = mysql_innodb_permissions

# SQLAlchemy + MySQL (MyISAM tables)
myisam_tables = "mysql://whatbench@localhost/whatbench"
mysql_myisam_groups, mysql_myisam_permissions = make_benchmarks(myisam_tables,
                                                                mysql_engine="MyISAM")
group_adapters['mysql_myisam'] = mysql_myisam_groups
permission_adapters['mysql_myisam'] = mysql_myisam_permissions

#}
