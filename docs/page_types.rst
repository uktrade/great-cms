Page Types
==========

Design Philosophy
-----------------

Great use a parent child relationship.
The number of page types has been kept to the lowest possible. More control is given on the page layout with the selection of a custom template from the template tab in the page edit interface.

.. note::
    Generic hierarchy of Great website:

        Home Page -> Listing Page -> Detail Page


===================== =================
Parent Page Type      Child Page Types
===================== =================
Home Page              List Page
List Page              Detail Page
Detail Page            N/A
===================== =================

Page types and templates
------------------------

Usually a developer needs to add a new page type if a new level is added to the hierarchy.
All page types inherit from `CMSGenericPage` class:


.. automodule:: core.models

.. class:: CMSGenericPage

   .. attribute:: template_choices


Custom context for layout type
------------------------------


