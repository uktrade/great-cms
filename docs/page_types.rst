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

If a Page's template requires some custom context data then use use the a "context data provider":

.. code-block:: python
   :linenos:
    from core.context import AbstractPageContextProvider

    # example/context.py
    class ExampleContextProvider(AbstractPageContextProvider):
        template_name = 'example/example_pae.html'

        @staticmethod
        def get_context_data(request, page):
            return {'foo': 'bar'}

.. code-block:: python
   :linenos:
    # example/apps.py
    from django.apps import AppConfig


    class ExampleConfig(AppConfig):
        name = 'example'

        def ready(self):
            from learn import context  # noqa F401
 

Behind the scenes core.models.CMSGenericPage.get_context  will call example.ExampleContextProvider.get_context_data for any Page that uses example/example_pae.html
