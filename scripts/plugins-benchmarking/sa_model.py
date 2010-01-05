# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
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
Utilities to set up bechmarks for source adapters powered by the repoze.what
SQLAlchemy plugin.

"""

from sqlalchemy import Table, ForeignKey, Column, create_engine
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relation, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from repoze.what.adapters.benchmark import AdapterBenchmark
from repoze.what.plugins.sql import configure_sql_adapters


def make_benchmarks(db, **table_args):
    """
    Create and return the benchmarks for group and permission adapters in
    ``db``.
    
    """
    groups_adapter, permissions_adapter, metadata = make_adapters(db, **table_args)
    groups_benchmark = RelationalIntegrityBenchmark(groups_adapter, metadata)
    permissions_benchmark = RelationalIntegrityBenchmark(permissions_adapter, metadata)
    return groups_benchmark, permissions_benchmark


def make_adapters(db, **table_args):
    """Create and return group and permission adapters in ``db``."""
    User, Group, Permission, Session, metadata = create_model(db, **table_args)
    adapters = configure_sql_adapters(User, Group, Permission, Session)
    return adapters['group'], adapters['permission'], metadata


def create_model(db, **table_args):
    """
    Create auth models for ``db`` and return them along with the resulting
    session.
    
    """
    engine = create_engine(db)
    DeclarativeBase = declarative_base()
    metadata = DeclarativeBase.metadata
    metadata.bind = engine
    
    # This is the association table for the many-to-many relationship between
    # groups and permissions.
    group_permission_table = Table('group_permission', metadata,
        Column(
               'group_name',
               Unicode(16),
               ForeignKey('group.group_name', onupdate="CASCADE",
                          ondelete="CASCADE")
        ),
        Column(
               'permission_name',
               Unicode(16),
               ForeignKey('permission.permission_name', onupdate="CASCADE",
                          ondelete="CASCADE")
        ),
	**table_args
    )

    # This is the association table for the many-to-many relationship between
    # groups and members - this is, the memberships.
    user_group_table = Table('user_group', metadata,
        Column(
               'user_name',
               Unicode(16),
               ForeignKey('user.user_name',
                          onupdate="CASCADE", ondelete="CASCADE")
        ),
        Column(
               'group_name',
               Unicode(16),
               ForeignKey('group.group_name',
                          onupdate="CASCADE", ondelete="CASCADE")
        ),
        **table_args
    )


    class User(DeclarativeBase):
        __tablename__ = 'user'
        __table_args__ = table_args
        user_name = Column(Unicode(16), primary_key=True)


    class Group(DeclarativeBase):
        __tablename__ = 'group'
        __table_args__ = table_args
        group_name = Column(Unicode(16), primary_key=True)
        users = relation(User, secondary=user_group_table, backref='groups')


    class Permission(DeclarativeBase):
        __tablename__ = 'permission'
        __table_args__ = table_args
        permission_name = Column(Unicode(16), primary_key=True)
        groups = relation(Group, secondary=group_permission_table,
                          backref='permissions')

    sm = sessionmaker(autoflush=True, autocommit=False, bind=engine)
    Session = scoped_session(sm)
    
    return User, Group, Permission, Session, metadata


#{ Custom benchmarks


class RelationalIntegrityBenchmark(AdapterBenchmark):
    """
    Take into account the referential constraints when the source is reset.
    
    """

    def __init__(self, adapter, metadata):
        self.metadata = metadata
        super(RelationalIntegrityBenchmark, self).__init__(adapter)
    
    def reset_source(self, source):
        self.adapter.dbsession.remove()
        if source:
            self.metadata.drop_all()
            self.metadata.create_all()
            # Adding the required items:
            new_items = set()
            for (section, items) in source.items():
                new_items |= set(items)
            for item_name in new_items:
                item = self.adapter.children_class()
                setattr(item, self.adapter.translations['item_name'], item_name)
                self.adapter.dbsession.add(item)
            self.adapter.dbsession.commit()
        super(RelationalIntegrityBenchmark, self).reset_source(source)
        self.adapter.dbsession.remove()


#}
