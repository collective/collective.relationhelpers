.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==========================
collective.relationhelpers
==========================

Helpers to manage, create, export, inspect and rebuild relations in Plone

To learn more about relations read https://training.plone.org/5/mastering-plone/relations.html


Features
========

Dealing with relations on individual objects
--------------------------------------------

**Convenience methods:**

``relations(obj, attribute=None, as_dict=False)``
    Get related objects.

``unrestricted_relations(obj, attribute=None, as_dict=False)``
    Get related objects without permission checks.

``backrelations(obj, attribute=None, as_dict=False)``
    Get objects with a relation to this object.

``unrestricted_backrelations(obj, attribute=None, as_dict=False)``
    Get objects with a relation to this object without permission checks.

``relation(obj, attribute)``
    Get related object. This is only valid if the attribute is the name of a relationChoice field on the object.

``unrestricted_relation(obj, attribute)``
    Get related object without permission checks. See relation

``backrelation(obj, attribute)``
    Get relating object. This only makes sense when one item has a relation of this type to the obj.
    One example is parent -> child where only one parent can exist.

``unrestricted_backrelation(obj, attribute)``
    Get relating object without permission checks. See backrelation

``relapi.link_objects(source, target, relationship)``
    Link objects: Create a relation between two objects using the specified relationship.
    From the parameter ``relationship`` the method will find out what kind of relationship you want to create (RelationChoice, RelationList) by inspecting the schema-field on the source-object.
    The method also works for linkintegrity-relations and relations between working-copies.

    Example: To use the default-behavior ``plone.relateditems`` use the field-name ``relatedItems`` as relationship: ``relapi.link_objects(obj, anotherobj, 'relatedItems')``.


**Main method to get all kinds of relations:**

``relapi.get_relations(obj, attribute=None, backrels=False, restricted=True, as_dict=False)``
    Get a list of incoming or outgoing relation for a specific content object.

    If you pass a attribute you only get relations of that type. This is the same as the fieldname on the source-object and the ``from_attribute`` on a RelationValue. You can also pass a list if attributes to get relations of certain types.

    By default the result is a list of objects. If you set as_dict=True it will return a dict with the names of the relations as keys and lists of objects as values.


Dealing with all relations at once
----------------------------------

Especially during migrations (e.g. between Archetypes and Dexteriy or from Python 2 to 3) you need to deal with all relations at once.
For example the relation-catalog and the intid-catalog could hold references to broken or removes objects.

First import the api: ``from collective.relationhelpers import api as relapi``

``relapi.rebuild_relations()``
    Rebuild all relations using the same code as the form ``@@rebuild-relations``

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


Rebuild all relations
---------------------

There is a form ``http://localhost:8080/Plone/@@rebuild-relations`` that rebuilds all relations.

It exports all valid reations from the relation-catalog, purges the relation-catalog (and the intid-catalog) and restores all valid relations.


Inspect relations
-----------------

There is a controlpanel ``http://localhost:8080/Plone/@@inspect-relations`` that allows you to inspect all relations in your site:

.. image:: https://raw.githubusercontent.com/collective/collective.relationhelpers/master/docs/relationinfo.png


Dealing with Archetypes-Relations
---------------------------------

This package does not support Archetypes but it can be of great help to migrate relations form Archetypes to Dexterity.
Here are two upgrade-steps.

The first stores all relations (AT and DX) as a annotation on the portal). Run that in Plone 4 or 5 if you still have AT content.::

    def store_relations(context=None):
        from plone.app.contenttypes.migration.utils import store_references
        portal = api.portal.get()
        store_references(portal)

The second restores them. Run it after you migrated all your content to Dexterity.::

    # Map References used with of Archetypes (Plone 4) to the ones used in Plone 5 with Dexterity
    RELATIONSHIP_FIELD_MAPPING = {
        'Working Copy Relation': 'iterate-working-copy',
        'relatesTo': 'relatedItems',
    }

    IGNORE = [
        'translationOf',  # LinguaPlone relation
    ]

    def restore_relations(context=None):
        portal = api.portal.get()
        all_stored_relations = IAnnotations(portal)['ALL_REFERENCES']
        log.info('Loaded {0} relations to restore'.format(
            len(all_stored_relations))
        )
        all_fixed_relations = []
        for rel in all_stored_relations:
            if rel['relationship'] in ignore:
                continue
            # plone.app.contenttypes exports references with 'relationship' but relationshelpers
            # expects 'from_attribute' which is what zc.relation uses.
            # Also some relationships have changed their name
            rel['from_attribute'] = RELATIONSHIP_FIELD_MAPPING.get(rel['relationship'], rel['relationship'])
            all_fixed_relations.append(rel)
        all_fixed_relations = sorted(all_fixed_relations, key=itemgetter('from_uuid', 'from_attribute'))
        relapi.restore_relations(all_relations=all_fixed_relations)


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
