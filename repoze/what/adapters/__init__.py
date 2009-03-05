# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
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
Base adapters for the supported source types.

This is, the foundations for the source adapters defined in plugins.

In a ``group source adapter``, ``a section is a group`` in the source and
``its items are the users that belong to that group``. Example: If Bob and Mary
belong to the "developers" group, then you can also say that items Bob and Mary
belong to the "developers" section.

In a ``permission source adapter``, ``a section is a permission`` in the source
and ``its items are the groups that are granted that permission``. Example: If
"developers" and "designers" are granted the right to update the web site
("update-site"), then you can also say that items "developers" and "designers"
belong to the "update-site" section.

@todo: Add support for "universal sections" (those containing item "_").
@todo: Add support for "anonymous sections" (those containing item "-").

"""

from zope.interface import Interface

__all__ = ['BaseSourceAdapter', 'AdapterError', 'SourceError',
           'ExistingSectionError', 'NonExistingSectionError', 
           'ItemPresentError', 'ItemNotPresentError']


class BaseSourceAdapter(object):
    """
    Base class for :term:`source adapters <source adapter>`.
    
    Please note that these abstract methods may only raise one exception:
    :class:`SourceError`, which is raised if there was a problem while dealing 
    with the source. They may not raise other exceptions because they should not
    validate anything but the source (not even the parameters they get).

    .. attribute:: is_writable = True

        :type: bool
        
        Whether the adapter can write to the source.
        
        If the source type handled by your adapter doesn't support write
        access, or if your adapter itself doesn't support writting to the
        source (yet), then you should set this value to ``False`` in the class
        itself; it will get overriden if the ``writable`` parameter in 
        :meth:`the contructor <BaseSourceAdapter.__init__>` is set, unless you 
        explicitly disable that parameter::
        
            # ...
            class MyFakeAdapter(BaseSourceAdapter):
                def __init__():
                    super(MyFakeAdapter, self).__init__(writable=False)
            # ...
        
        .. note::
        
            If it's ``False``, then you don't have to define the methods that
            modify the source because they won't be used:
            
            * :meth:`_include_items`
            * :meth:`_exclude_items`
            * :meth:`_create_section`
            * :meth:`_edit_section`
            * :meth:`_delete_section`

    .. warning::
    
        Do not ever cache the results -- that is :class:`BaseSourceAdapter`'s
        job. It requests a given datum once, not multiple times, thanks to
        its internal cache.
    
    """
    
    def __init__(self, writable=True):
        """
        Run common setup for source adapters.
        
        :param writable: Whether the source is writable.
        :type writable: bool
        
        """
        # The cache for the sections loaded by the source adapter.
        self.loaded_sections = {}
        # Whether all of the existing items have been loaded
        self.all_sections_loaded = False
        # Whether the current source is writable:
        self.is_writable = writable
    
    def get_all_sections(self):
        """
        Return all the sections found in the source.
        
        :return: All the sections found in the source.
        :rtype: dict
        :raise SourceError: If there was a problem with the source.
        
        """
        if not self.all_sections_loaded:
            self.loaded_sections = self._get_all_sections()
            self.all_sections_loaded = True
        return self.loaded_sections
    
    def get_section_items(self, section):
        """
        Return the properties of ``section``.
        
        :param section: The name of the section to be fetched.
        :type section: unicode
        :return: The items of the ``section``.
        :rtype: tuple
        :raise NonExistingSectionError: If the requested section doesn't exist.
        :raise SourceError: If there was a problem with the source.
        
        """
        if section not in self.loaded_sections:
            self._check_section_existence(section)
            # It does exist; let's load it:
            self.loaded_sections[section] = self._get_section_items(section)
        return self.loaded_sections[section]
    
    def set_section_items(self, section, items):
        """
        Set ``items`` as the only items of the ``section``.
        
        :raise NonExistingSectionError: If the section doesn't exist.
        :raise SourceError: If there was a problem with the source.
        
        """
        old_items = self.get_section_items(section)
        items = set(items)
        # Finding what was added and what was removed:
        added = set((i for i in items if i not in old_items))
        removed = set((i for i in old_items if i not in items))
        # Removing/adding as requested. We're removing first to avoid
        # increasing the size of the source more than required.
        self.exclude_items(section, removed)
        self.include_items(section, added)
        # The cache must have been updated by the two methods above.
    
    def find_sections(self, hint):
        """
        Return the sections that meet a given criteria.
        
        :param hint: repoze.what's credentials dictionary or a group name.
        :type hint: dict or unicode
        :return: The sections that meet the criteria.
        :rtype: tuple
        :raise SourceError: If there was a problem with the source.
        
        """
        return self._find_sections(hint)
    
    def include_item(self, section, item):
        """
        Include ``item`` in ``section``.
        
        This is the individual (non-bulk) edition of :meth:`include_items`.
        
        :param section: The ``section`` to contain the ``item``.
        :type section: unicode
        :param item: The new ``item`` of the ``section``.
        :type item: tuple
        :raise NonExistingSectionError: If the ``section`` doesn't exist.
        :raise ItemPresentError: If the ``item`` is already included.
        :raise SourceError: If there was a problem with the source.
        
        """
        self.include_items(section, (item, ))
    
    def include_items(self, section, items):
        """
        Include ``items`` in ``section``.
        
        This is the bulk edition of :meth:`include_item`.
        
        :param section: The ``section`` to contain the ``items``.
        :type section: unicode
        :param items: The new ``items`` of the ``section``.
        :type items: tuple
        :raise NonExistingSectionError: If the ``section`` doesn't exist.
        :raise ItemPresentError: If at least one of the items is already
            present.
        :raise SourceError: If there was a problem with the source.
        
        """
        # Verifying that the section exists and doesn't already contain the
        # items:
        self._check_section_existence(section)
        for i in items:
            self._confirm_item_not_present(section, i)
        # Verifying write permissions:
        self._check_writable()
        # Everything's OK, let's add it:
        items = set(items)
        self._include_items(section, items)
        # Updating the cache, if necessary:
        if section in self.loaded_sections:
            self.loaded_sections[section] |= items
    
    def exclude_item(self, section, item):
        """
        Exclude ``item`` from ``section``.
        
        This is the individual (non-bulk) edition of :meth:`exclude_items`.
        
        :param section: The ``section`` that contains the ``item``.
        :type section: unicode
        :param item: The ``item`` to be removed from ``section``.
        :type item: tuple
        :raise NonExistingSectionError: If the ``section`` doesn't exist.
        :raise ItemNotPresentError: If the item is not included in the section.
        :raise SourceError: If there was a problem with the source.
        
        """
        self.exclude_items(section, (item, ))
    
    def exclude_items(self, section, items):
        """
        Exclude items from section.
        
        This is the bulk edition of :meth:`exclude_item`.
        
        :param section: The ``section`` that contains the ``items``.
        :type section: unicode
        :param items: The ``items`` to be removed from ``section``.
        :type items: tuple
        :raise NonExistingSectionError: If the ``section`` doesn't exist.
        :raise ItemNotPresentError: If at least one of the items is not
            included in the section.
        :raise SourceError: If there was a problem with the source.
        
        """
        # Verifying that the section exists and already contains the items:
        self._check_section_existence(section)
        for i in items:
            self._confirm_item_is_present(section, i)
        # Verifying write permissions:
        self._check_writable()
        # Everything's OK, let's remove them:
        items = set(items)
        self._exclude_items(section, items)
        # Updating the cache, if necessary:
        if section in self.loaded_sections:
            self.loaded_sections[section] -= items
    
    def create_section(self, section):
        """
        Add ``section`` to the source.
        
        :param section: The section name.
        :type section: unicode
        :raise ExistingSectionError: If the section name is already in use.
        :raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_not_existence(section)
        self._check_writable()
        self._create_section(section)
        # Adding to the cache:
        self.loaded_sections[section] = set()
        
    def edit_section(self, section, new_section):
        """
        Edit ``section``'s properties.
        
        :param section: The current name of the section.
        :type section: unicode
        :param new_section: The new name of the section.
        :type new_section: unicode
        :raise NonExistingSectionError: If the section doesn't exist.
        :raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        self._check_writable()
        self._edit_section(section, new_section)
        # Updating the cache too, if loaded:
        if section in self.loaded_sections:
            self.loaded_sections[new_section] = self.loaded_sections[section]
            del self.loaded_sections[section]
        
    def delete_section(self, section):
        """
        Delete ``section``.
        
        It removes the ``section`` from the source.
        
        :param section: The name of the section to be deleted.
        :type section: unicode
        :raise NonExistingSectionError: If the section in question doesn't 
            exist.
        :raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        self._check_writable()
        self._delete_section(section)
        # Removing from the cache too, if loaded:
        if section in self.loaded_sections:
            del self.loaded_sections[section]
    
    def _check_writable(self):
        """
        Raise an exception if the source is not writable.
        
        :raise SourceError: If the source is not writable.
        
        """
        if not self.is_writable:
            raise SourceError('The source is not writable')
    
    def _check_section_existence(self, section):
        """
        Raise an exception if ``section`` is not defined in the source.
        
        :param section: The name of the section to look for.
        :type section: unicode
        :raise NonExistingSectionError: If the section is not defined.
        :raise SourceError: If there was a problem with the source.
        
        """
        if not self._section_exists(section):
            msg = u'Section "%s" is not defined in the source' % section
            raise NonExistingSectionError(msg)
    
    def _check_section_not_existence(self, section):
        """
        Raise an exception if ``section`` is defined in the source.
        
        :param section: The name of the section to look for.
        :type section: unicode
        :raise ExistingSectionError: If the section is defined.
        :raise SourceError: If there was a problem with the source.
        
        """
        if self._section_exists(section):
            msg = u'Section "%s" is already defined in the source' % section
            raise ExistingSectionError(msg)
    
    def _confirm_item_is_present(self, section, item):
        """
        Raise an exception if ``section`` doesn't contain ``item``.
        
        :param section: The name of the section that may contain the item.
        :type section: unicode
        :param item: The name of the item to look for.
        :type item: unicode
        :raise NonExistingSectionError: If the section doesn't exist.
        :raise ItemNotPresentError: If the item is not included.
        :raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        if not self._item_is_included(section, item):
            msg = u'Item "%s" is not defined in section "%s"' % (item, section)
            raise ItemNotPresentError(msg)
    
    def _confirm_item_not_present(self, section, item):
        """
        Raise an exception if ``section`` already contains ``item``.
        
        :param section: The name of the section that may contain the item.
        :type section: unicode
        :param item: The name of the item to look for.
        :type item: unicode
        :raise NonExistingSectionError: If the section doesn't exist.
        :raise ItemPresentError: If the item is already included.
        :raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        if self._item_is_included(section, item):
            msg = u'Item "%s" is already defined in section "%s"' % (item,
                                                                     section)
            raise ItemPresentError(msg)
    
    #{ Abstract methods
    
    def _get_all_sections(self):
        """
        Return all the sections found in the source.
        
        :return: All the sections found in the source.
        :rtype: dict
        :raise SourceError: If there was a problem with the source while
            retrieving the sections.
        
        """
        raise NotImplementedError()
    
    def _get_section_items(self, section):
        """
        Return the items of the section called ``section``.
        
        :param section: The name of the section to be fetched.
        :type section: unicode
        :return: The items of the section.
        :rtype: set
        :raise SourceError: If there was a problem with the source while 
            retrieving the section.
        
        .. attention::
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        
        """
        raise NotImplementedError()
        
    def _find_sections(self, hint):
        """
        Return the sections that meet a given criteria.
        
        :param hint: repoze.what's credentials dictionary or a group name.
        :type hint: dict or unicode
        :return: The sections that meet the criteria.
        :rtype: tuple
        :raise SourceError: If there was a problem with the source while
            retrieving the sections.
        
        This method depends on the type of adapter that is implementing it:
        
        * If it's a ``group`` source adapter, it returns the groups the 
          authenticated user belongs to. In this case, hint represents
          repoze.what's credentials dict. Please note that hint is not an 
          user name because some adapters may need something else to find the 
          groups the authenticated user belongs to. For example, LDAP adapters 
          need the full Distinguished Name (DN) in the credentials dict, or a 
          given adapter may only need the email address, so the user name alone 
          would be useless in both situations.
        * If it's a ``permission`` source adapter, it returns the name of the
          permissions granted to the group in question; here hint represents
          the name of such a group.
        
        """
        raise NotImplementedError()
    
    def _include_items(self, section, items):
        """
        Add ``items`` to the ``section``, in the source.
        
        :param section: The section to contain the items.
        :type section: unicode
        :param items: The new items of the section.
        :type items: tuple
        :raise SourceError: If the items could not be added to the section.

        .. attention:: 
            When implementing this method, don't check whether the
            section really exists or the items are already included; that's 
            already done when this method is called.
        
        """
        raise NotImplementedError()
    
    def _exclude_items(self, section, items):
        """
        Remove ``items`` from the ``section``, in the source.
        
        :param section: The section that contains the items.
        :type section: unicode
        :param items: The items to be removed from section.
        :type items: tuple
        :raise SourceError: If the items could not be removed from the section.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists or the items are already included; that's 
            already done when this method is called.
        
        """
        raise NotImplementedError()
    
    def _item_is_included(self, section, item):
        """
        Check whether ``item`` is included in ``section``.
        
        :param section: The name of the item to look for.
        :type section: unicode
        :param section: The name of the section that may include the item.
        :type section: unicode
        :return: Whether the item is included in section or not.
        :rtype: bool
        :raise SourceError: If there was a problem with the source.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        
        """
        raise NotImplementedError()
        
    def _create_section(self, section):
        """
        Add ``section`` to the source.
        
        :param section: The section name.
        :type section: unicode
        :raise SourceError: If the section could not be added.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section already exists; that's already done when this method is
            called.
        
        """
        raise NotImplementedError()
        
    def _edit_section(self, section, new_section):
        """
        Edit ``section``'s properties.
        
        :param section: The current name of the section.
        :type section: unicode
        :param new_section: The new name of the section.
        :type new_section: unicode
        :raise SourceError: If the section could not be edited.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        
        """
        raise NotImplementedError()
        
    def _delete_section(self, section):
        """
        Delete ``section``.
        
        It removes the ``section`` from the source.
        
        :param section: The name of the section to be deleted.
        :type section: unicode
        :raise SourceError: If the section could not be deleted.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        
        """
        raise NotImplementedError()
    
    def _section_exists(self, section):
        """
        Check whether ``section`` is defined in the source.
        
        :param section: The name of the section to check.
        :type section: unicode
        :return: Whether the section is the defined in the source or not.
        :rtype: bool
        :raise SourceError: If there was a problem with the source.
        
        """
        raise NotImplementedError()
    
    #}


#{ Exceptions


class AdapterError(Exception):
    """
    Base exception for problems in the source adapters.
    
    It's never raised directly.
    
    """
    pass


class SourceError(AdapterError):
    """
    Exception for problems with the source itself.
    
    .. attention::
        If you are creating a :term:`source adapter`, this is the only
        exception you should raise.
    
    """
    pass


class ExistingSectionError(AdapterError):
    """Exception raised when trying to add an existing group."""
    pass


class NonExistingSectionError(AdapterError):
    """Exception raised when trying to use a non-existing group."""
    pass


class ItemPresentError(AdapterError):
    """
    Exception raised when trying to add an item to a group that already
    contains it.
    
    """
    pass


class ItemNotPresentError(AdapterError):
    """
    Exception raised when trying to remove an item from a group that doesn't
    contain it.
    
    """
    pass


#}
