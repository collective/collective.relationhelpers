.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==========================
collective.relationhelpers
==========================

Helpers for dealing with relations in Plone.

To learn more about relations read https://training.plone.org/5/mastering-plone/relations.html


Features
========

Rebuild all relations
---------------------

There is a form ``http://localhost:8080/Plone/@@rebuild_relations`` that rebuilds all relations.

It exports all valid reations from the relation-catalog, purges the relation-catalog (and the intid-catalog) and restores all valid relations.


It uses some helper methods that you can use in your own projects or upgrade-steps.

First import the api: ``from collective.relationhelpers import api as relapi``


Dealing with all relations at once
----------------------------------

Especially during migrations (e.g. between Archetypes and Dexteriy or from Python 2 to 3) you need to deal with relations.

These methods can help:

``relapi.rebuild_relations()``
    Rebuild all relations using the same code as the form ``@@rebuild_relations``

``relapi.get_all_relations()``
    Get all relations as a list of dicts.

``relapi.export_relations()``
    Export all relations as a json file ``all_relations.json`` in you buildout directory.

``relapi.store_relations()``
    Export all relations and store them as a annotation on the portal ``IAnnotations(portal)['ALL_REFERENCES']``.

``relapi.cleanup_intids()``
    Purge all RelationValues and all references to broken objects from the IntId catalog.

``relapi.get_relations_stats()``
    Log information on all existing relations

``relapi.restore_relations(all_relations=None)``
    Recreate relations from a annotation on the portal or a list of dicts (e.g. restored from the json-file created by ``export_relations``).
    This works fine for all kinds of relations, RelationList- or RelationChoice-fields (including the default field "Related Items") as well as for linkintegrity-relations and relations between working-copies.


Dealing with relations on individual objects
--------------------------------------------

``relapi.link_objects(source, target, relationship)``
    Link objects: Create a relation between two objects using the specified relationship.
    From the parameter ``relationship`` the method will find out what kind of relationship you want to create (RelationChoice, RelationList) by inspecting the schema-field on the source-object.
    The method also works for linkintegrity-relations and relations between working-copies.

    Example: To use the default-behavior ``plone.relateditems`` use the field-name ``relatedItems`` as relationship: ``relapi.link_objects(obj, anotherobj, 'relatedItems')``.

``relapi.get_relations(obj, attribute=None, backrefs=False, fullobj=False)``
    Get a list of incoming or outgoing relation for a specific content object.

    If you pass a attribute (i.e. the ``from_attribute`` of the relation) you can use it to get only specific relations.

    The result is returned as a dict with the following values:

    ``id``: The id of the related or relating (for backreferences) object

    ``href``: The url of the object

    ``title``: The title

    ``relation``: The name of the relation (i.e. field).

    ``fullobj``: The obj (optional)

``relapi.get_backrelations(obj, attribute=None, fullobj=False)``
    Wrapper for ``get_relations`` that only return backrelations.


Installation
============

Install collective.relationhelpers by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.relationhelpers


and then running ``bin/buildout``.


Contribute
==========

- Issue Tracker: https://github.com/collective/collective.relationhelpers/issues
- Source Code: https://github.com/collective/collective.relationhelpers


Support
=======

If you are having issues, please create a ticket.


License
=======

The project is licensed under the GPLv2.
