# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com> and
#                     Gustavo Narea <me@gustavonarea.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
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

@todo: Error messages should be translatable.
@todo: Add support for "universal sections" (those containing item "_").
@todo: Add support for "anonymous sections" (those containing item "-").

"""

from zope.interface import Interface

__all__ = ['BaseSourceAdapter', 'AdapterError', 'SourceError', 
           'ExistingSectionError', 'NonExistingSectionError',
           'ItemPresentError', 'ItemNotPresentError']


class BaseSourceAdapter(object):
    """
    Base class for source adapters.
    
    Please note that these abstract methods may only raise one exception:
    L{SourceError}, which is raised if there was a problem while dealing with
    the source. They may not raise other exceptions because they should not
    validate anything but the source (not even the parameters they get).
    
    """
    
    def __init__(self):
        """Run common setup for source adapters."""
        # The cache for the sections loaded by the source adapter.
        self.loaded_sections = {}
        # Whether all of the existing items have been loaded
        self.all_sections_loaded = False
    
    def get_all_sections(self):
        """
        Return all the sections found in the source.
        
        This method is like L{BaseSourceAdapter._get_all_sections}, but it uses 
        the cache to avoid future queries to the source.
        
        @return: All the sections found in the source.
        @rtype: C{dict}
        @raise SourceError: If there was a problem with the source.
        
        """
        if not self.all_sections_loaded:
            self.loaded_sections = self._get_all_sections()
            self.all_sections_loaded = True
        return self.loaded_sections
    
    def get_section_items(self, section):
        """
        Return the properties of C{section}.
        
        This method is similar to L{BaseSourceAdapter._get_section_items}, but 
        it uses the cache to avoid future requests to the source.
        
        @param section: The name of the section to be fetched.
        @type section: C{unicode}
        @return: The C{items} of the section.
        @rtype: C{tuple}
        @raise NonExistingSectionError: If the requested section doesn't exist.
        @raise SourceError: If there was a problem with the source.
        
        """
        if not self.loaded_sections.has_key(section):
            self._check_section_existence(section)
            # It does exist; let's load it:
            self.loaded_sections[section] = self._get_section_items(section)
        return self.loaded_sections[section]
    
    def set_section_items(self, section, items):
        """
        Set C{items} as the only items of the C{section}.
        
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise SourceError: If there was a problem with the source.
        
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
        
        @param hint: repoze.who's C{identity} dictionary or a group name.
        @type hint: C{dict} or C{unicode}
        @return: The sections that meet the criteria.
        @rtype: C{tuple}
        @raise SourceError: If there was a problem with the source.
        
        """
        return self._find_sections(hint)
    
    def include_item(self, section, item):
        """
        Include C{item} in C{section}.
        
        This is the individual (non-bulk) edition of L{BaseSourceAdapter.
        include_items}.
        
        @param section: The section to contain the item.
        @type section: C{unicode}
        @param items: The new item of the C{section}.
        @type items: C{tuple}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise ItemPresentError: If the item is already included.
        @raise SourceError: If there was a problem with the source.
        
        """
        self.include_items(section, (item, ))
    
    def include_items(self, section, items):
        """
        Include C{items} in C{section}.
        
        This is the bulk edition of L{include_item}.
        
        @param section: The section to contain the items.
        @type section: C{unicode}
        @param items: The new items of the C{section}.
        @type items: C{tuple}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise ItemPresentError: If at least one of the items is already
            present.
        @raise SourceError: If there was a problem with the source.
        
        """
        # Verifying that the section exists and doesn't already contain the
        # items:
        self._check_section_existence(section)
        for i in items:
            self._confirm_item_not_present(section, i)
        # Everything's OK, let's add it:
        items = set(items)
        self._include_items(section, items)
        # Updating the cache, if necessary:
        if self.loaded_sections.has_key(section):
            self.loaded_sections[section] |= items
    
    def exclude_item(self, section, item):
        """
        Exclude C{item} from C{section}.
        
        This is the individual (non-bulk) edition of L{BaseSourceAdapter.
        exclude_items}.
        
        @param section: The section that contains the item.
        @type section: C{unicode}
        @param items: The item to be removed from C{section}.
        @type items: C{tuple}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise ItemNotPresentError: If the item is not included in the section.
        @raise SourceError: If there was a problem with the source.
        
        """
        self._exclude_items(section, (item, ))
    
    def exclude_items(self, section, items):
        """
        Exclude C{items} from C{section}.
        
        This is the bulk edition of L{exclude_item}.
        
        @param section: The section that contains the items.
        @type section: C{unicode}
        @param items: The items to be removed from C{section}.
        @type items: C{tuple}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise ItemNotPresentError: If at least one of the items is not
            included in the section.
        @raise SourceError: If there was a problem with the source.
        
        """
        # Verifying that the section exists and already contains the items:
        self._check_section_existence(section)
        for i in items:
            self._confirm_item_is_present(section, i)
        # Everything's OK, let's remove them:
        items = set(items)
        self._exclude_items(section, items)
        # Updating the cache, if necessary:
        if self.loaded_sections.has_key(section):
            self.loaded_sections[section] -= items
    
    def create_section(self, section):
        """
        Add C{section} to the source.
        
        @param section: The section name.
        @type section: C{unicode}
        @raise ExistingSectionError: If the section name is already in use.
        @raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_not_existence(section)
        self._create_section(section)
        # Adding to the cache:
        self.loaded_sections[section] = set()
        
    def edit_section(self, section, new_section):
        """
        Edit C{section}'s properties.
        
        @param section: The current name of the section.
        @type section: C{unicode}
        @param new_section: The new name of the section.
        @type new_section: C{unicode}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        self._edit_section(section, new_section)
        # Updating the cache too, if loaded:
        if self.loaded_sections.has_key(section):
            self.loaded_sections[new_section] = self.loaded_sections[section]
            del self.loaded_sections[section]
        
    def delete_section(self, section):
        """
        Delete C{section}.
        
        It removes the C{section} from the source.
        
        @param section: The name of the section to be deleted.
        @type section: C{unicode}
        @raise NonExistingSectionError: If the section in question doesn't 
            exist.
        @raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        self._delete_section(section)
        # Removing from the cache too, if loaded:
        if self.loaded_sections.has_key(section):
            del self.loaded_sections[section]
    
    def _check_section_existence(self, section):
        """
        Raise an exception if C{section} is not defined in the source.
        
        @param section: The name of the section to look for.
        @type section: C{unicode}
        @raise NonExistingSectionError: If the section is not defined.
        @raise SourceError: If there was a problem with the source.
        
        """
        if not self._section_exists(section):
            msg = u'Section "%s" is not defined in the source' % section
            raise NonExistingSectionError(msg)
    
    def _check_section_not_existence(self, section):
        """
        Raise an exception if C{section} is defined in the source.
        
        @param section: The name of the section to look for.
        @type section: C{unicode}
        @raise ExistingSectionError: If the section is defined.
        @raise SourceError: If there was a problem with the source.
        
        """
        if self._section_exists(section):
            msg = u'Section "%s" is already defined in the source' % section
            raise ExistingSectionError(msg)
    
    def _confirm_item_is_present(self, section, item):
        """
        Raise an exception if C{section} doesn't contain C{item}.
        
        @param section: The name of the section that may contain the item.
        @type section: C{unicode}
        @param item: The name of the item to look for.
        @type item: C{unicode}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise ItemNotPresentError: If the item is not included.
        @raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        if not self._item_is_included(section, item):
            msg = u'Item "%s" is not defined in section "%s"' % (item, section)
            raise ItemNotPresentError(msg)
    
    def _confirm_item_not_present(self, section, item):
        """
        Raise an exception if C{section} already contains C{item}.
        
        @param section: The name of the section that may contain the item.
        @type section: C{unicode}
        @param item: The name of the item to look for.
        @type item: C{unicode}
        @raise NonExistingSectionError: If the section doesn't exist.
        @raise ItemPresentError: If the item is already included.
        @raise SourceError: If there was a problem with the source.
        
        """
        self._check_section_existence(section)
        if self._item_is_included(section, item):
            msg = u'Item "%s" is already defined in section "%s"' % (item,
                                                                     section)
            raise ItemPresentError(msg)
    
    #{ Abstract methods
    
    def _get_all_sections():
        """
        Return all the sections found in the source.
        
        L{BaseSourceAdapter.get_all_sections} is more efficient than this method
        because it uses a cache, so you should avoid this unless you really
        want to query the source directly. It doesn't add the sections found to
        the cache either.
        
        @return: All the sections found in the source.
        @rtype: C{dict}
        @raise SourceError: If there was a problem with the source while
            retrieving the sections.
        
        """
        raise NotImplementedError()
    
    def _get_section_items(section):
        """
        Return the properties of the section called C{section}.
        
        L{BaseSourceAdapter.get_section_items} is more efficient than this 
        method because it uses a cache, so you should avoid this unless you 
        really want to query the source directly. It doesn't add the section 
        found to the cache either.
        
        @attention: When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        @param section: The name of the section to be fetched.
        @type section: C{unicode}
        @return: The C{items} of the section.
        @rtype: C{set}
        @raise SourceError: If there was a problem with the source while
            retrieving the section.
        
        """
        raise NotImplementedError()
        
    def _find_sections(hint):
        """
        Return the sections that meet a given criteria.
        
        This method depends on what kind of adapter is implementing it:
        
        If it's a ``group`` source adapter, it returns the groups the 
        authenticated user belongs to. In this case, C{hint} represents
        repoze.who's C{identity} dict. Please notice that C{hint} is not an 
        user name because some adapters may need something else to find the 
        groups the authenticated user belongs to. For example, LDAP adapters 
        need the full Distinguished Name (DN) in the C{identity} dict, or a 
        given adapter may only need the email address, so the user name alone 
        would be useless in both situations.
        
        If it's a ``permission`` source adapter, it returns the name of the
        permissions granted to the group in question; here C{hint} represents
        the name of such a group.
        
        @param hint: repoze.who's C{identity} dictionary or a group name.
        @type hint: C{dict} or C{unicode}
        @return: The sections that meet the criteria.
        @rtype: C{tuple}
        @raise SourceError: If there was a problem with the source while
            retrieving the sections.
        
        """
        raise NotImplementedError()
    
    def _include_items(section, items):
        """
        Add C{items} to the C{section}, in the source.
        
        @attention: When implementing this method, don't check whether the
            section really exists or the items are already included; that's 
            already done when this method is called.
        @param section: The section to contain the items.
        @type section: C{unicode}
        @param items: The new items of the C{section}.
        @type items: C{tuple}
        @raise SourceError: If the items could not be added to the section.
        
        """
        raise NotImplementedError()
    
    def _exclude_items(section, items):
        """
        Remove C{items} from the C{section}, in the source.
        
        @attention: When implementing this method, don't check whether the
            section really exists or the items are already included; that's 
            already done when this method is called.
        @param section: The section that contains the items.
        @type section: C{unicode}
        @param items: The items to be removed from C{section}.
        @type items: C{tuple}
        @raise SourceError: If the items could not be removed from the section.
        
        """
        raise NotImplementedError()
    
    def _item_is_included(section, item):
        """
        Check whether C{item} is included in C{section}.
        
        @attention: When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        @param section: The name of the item to look for.
        @type section: C{unicode}
        @param section: The name of the section that may include the item.
        @type section: C{unicode}
        @return: Whether the C{item} is included in C{section} or not.
        @rtype: C{bool}
        @raise SourceError: If there was a problem with the source.
        
        """
        raise NotImplementedError()
        
    def _create_section(section):
        """
        Add C{section} to the source.
        
        @attention: When implementing this method, don't check whether the
            section already exists; that's already done when this method is
            called.
        @param section: The section name.
        @type section: C{unicode}
        @raise SourceError: If the section could not be added.
        
        """
        raise NotImplementedError()
        
    def _edit_section(section, new_section):
        """
        Edit C{section}'s properties.
        
        @attention: When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        @param section: The current name of the section.
        @type section: C{unicode}
        @param new_section: The new name of the section.
        @type new_section: C{unicode}
        @raise SourceError: If the section could not be edited.
        
        """
        raise NotImplementedError()
        
    def _delete_section(section):
        """
        Delete C{section}.
        
        It removes the C{section} from the source.
        
        @attention: When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.
        @param section: The name of the section to be deleted.
        @type section: C{unicode}
        @raise SourceError: If the section could not be deleted.
        
        """
        raise NotImplementedError()
    
    def _section_exists(section):
        """
        Check whether C{section} is defined in the source.
        
        @param section: The name of the section to check.
        @type section: C{unicode}
        @return: Whether the C{section} is the defined in the source or not.
        @rtype: C{bool}
        @raise SourceError: If there was a problem with the source.
        
        """
        raise NotImplementedError()
    
    #}


#{ Exceptions


class AdapterError(Exception):
    """Base exception for problems the source adapters."""
    pass


class SourceError(AdapterError):
    """Exception for problems with the source itself."""
    pass


class ExistingSectionError(AdapterError):
    """Exception raised when trying to add an existing group."""
    pass


class NonExistingSectionError(AdapterError):
    """Exception raised when trying to use a non-existing group."""
    pass


class ItemPresentError(AdapterError):
    """Exception raised when trying to add an item to a group that already
    contains it."""
    pass


class ItemNotPresentError(AdapterError):
    """Exception raised when trying to remove an item from a group that doesn't
    contain it."""
    pass


#}
