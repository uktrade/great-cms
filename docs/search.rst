Search in Magna
===============

High-level summary
------------------

* `great-cms` has a search page at /search/ - it is very, very similar to the search behaviour in Great V1 (directory-cms + great-domestic-ui), effectively being a merging of the relevant parts of those two codebases.

* What content is searchable?
    * Searchable CMS-driven content is currently:
        * Live ``domestic.ArticlePage``s
        * Live ``domestic.CountryGuidePage``s

    This content is fully re-indexed automatically by the ActivityStream service every 2 minutes and partial updates are ingested twice between full rebuilds.

    * There is also hard-coded configuration for Services pages, plus 'promoted' keywords that we want to associate with particular pages.

* Search results are pulled from ActivityStream and shown to the user - they do not come from the great-cms database.


Diving deeper
-------------

Relevant areas of code in great-cms are the `activitystream` and `search` apps.

There is documentation about how to develop Search against ActivityStreamin Confluence, under the How To Guides - search for 'activity stream local development search'.
