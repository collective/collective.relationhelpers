# -*- coding: UTF-8 -*-
from collections import Counter
from collections import defaultdict
from plone import api
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.app.iterate.dexterity.relation import StagingRelationValue
from plone.app.linkintegrity.handlers import modifiedContent
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemataForType
from Products.Five.browser import BrowserView
from z3c.relationfield import event
from z3c.relationfield import RelationValue
from z3c.relationfield.schema import Relation
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified

import json
import logging

logger = logging.getLogger(__name__)

RELATIONS_KEY = 'ALL_REFERENCES'


class RebuildRelations(BrowserView):

    def __call__(self, rebuild=False):
        self.done = False
        if rebuild:
            rebuild_relations()
            self.done = True
            api.portal.show_message(u'Finished! See log for details.', self.request)

        self.info = get_relations_stats()
        return self.index()


def rebuild_relations(context=None):
    store_relations()
    purge_relations()
    cleanup_intids()
    restore_relations()


def get_relations_stats():
    info = defaultdict(int)
    relation_catalog = getUtility(ICatalog)
    for rel in relation_catalog.findRelations():
        if rel.isBroken():
            info[rel.from_attribute + ' (broken)'] += 1
        else:
            info[rel.from_attribute] += 1
    return info


def get_all_relations():
    """Get all data from zc.relation catalog.
    Logs some useful statistics.
    """
    results = []
    info = defaultdict(int)

    relation_catalog = getUtility(ICatalog)
    for rel in relation_catalog.findRelations():
        if rel.from_object and rel.to_object:
            results.append({
                'from_uuid': rel.from_object.UID(),
                'to_uuid': rel.to_object.UID(),
                'from_attribute': rel.from_attribute,
            })
            info[rel.from_attribute] += 1
        else:
            logger.info(u'Dropping relation {} from {} to {}'.format(rel.from_attribute, rel.from_object, rel.to_object))
    msg = ''
    for k, v in info.items():
        msg += u'{}: {}\n'.format(k, v)
    logger.info(u'\nFound the following relations:\n{}'.format(msg))
    return results


def store_relations(context=None):
    """Store all relations in a annotation on the portal.
    """
    all_relations = get_all_relations()
    portal = api.portal.get()
    IAnnotations(portal)[RELATIONS_KEY] = all_relations
    logger.info('Stored {0} relations on the portal'.format(
        len(all_relations))
    )


def export_relations(context=None):
    """Store all relations in a annotation on the portal.
    """
    all_relations = get_all_relations()
    with open('all_relations.json', 'w') as f:
        json.dump(all_relations, f)
        logger.info('Stored {0} relations as all_relations.json'.format(
            len(all_relations))
        )


def purge_relations(context=None):
    """Removes all entries form zc.relation catalog.
    RelationValues that were set as attribute on content are still there!
    These are removed/overwritten when restoring the relations.
    """
    rel_catalog = getUtility(ICatalog)
    rel_catalog.clear()
    logger.info('Purged zc.relation catalog')


def restore_relations(context=None, all_relations=None):
    """Restore relations from a annotation on the portal.
    """

    portal = api.portal.get()
    if all_relations is None:
        all_relations = IAnnotations(portal)[RELATIONS_KEY]
    logger.info('Loaded {0} relations to restore'.format(
        len(all_relations))
    )
    update_linkintegrity = []
    modified_items = []
    modified_relation_lists = defaultdict(list)

    # remove duplicates
    unique_relations = set(tuple(tuple([i['from_uuid'], i['to_uuid'], i['from_attribute']]) for i in all_relations))
    if len(unique_relations) < len(all_relations):
        logger.info('Dropping {0} duplicates'.format(
            len(all_relations) - len(unique_relations)))
        all_relations = [{'from_uuid': i[0], 'to_uuid': i[1], 'from_attribute': i[2]} for i in unique_relations]

    intids = getUtility(IIntIds)
    for item in all_relations:
        source_obj = uuidToObject(item['from_uuid'])
        target_obj = uuidToObject(item['to_uuid'])
        from_attribute = item['from_attribute']
        to_id = intids.getId(target_obj)

        if from_attribute == referencedRelationship:
            # Ignore linkintegrity for now. We'll rebuilt it at the end!
            update_linkintegrity.append(item['from_uuid'])
            continue

        if from_attribute == ITERATE_RELATION_NAME:
            # Iterate relations are not set as values of fields
            relation = StagingRelationValue(to_id)
            event._setRelation(source_obj, ITERATE_RELATION_NAME, relation)
            continue

        fti = getUtility(IDexterityFTI, name=source_obj.portal_type)
        field_and_schema = get_field_and_schema_for_fieldname(from_attribute, fti)
        if field_and_schema is None:
            # the from_attribute is no field
            # we could either create a fresh relation or log the case
            logger.info(u'No field. Setting relation: {}'.format(item))
            event._setRelation(source_obj, from_attribute, RelationValue(to_id))
            continue

        field, schema = field_and_schema
        relation = RelationValue(to_id)

        if isinstance(field, RelationList):
            logger.info('Add relation {} from {} to {}'.format(
                from_attribute, source_obj.absolute_url(), target_obj.absolute_url()))
            if item['from_uuid'] in modified_relation_lists.get(from_attribute, []):
                # Do not purge relations
                existing_relations = getattr(source_obj, from_attribute, [])
            else:
                # First touch. Make sure we purge!
                existing_relations = []
            existing_relations.append(relation)
            setattr(source_obj, from_attribute, existing_relations)
            modified(source_obj)
            modified_items.append(item['from_uuid'])
            modified_relation_lists[from_attribute].append(item['from_uuid'])
            continue

        elif isinstance(field, (Relation, RelationChoice)):
            logger.info('Add relation {} from {} to {}'.format(
                from_attribute, source_obj.absolute_url(), target_obj.absolute_url()))
            setattr(source_obj, from_attribute, relation)
            modified(source_obj)
            modified_items.append(item['from_uuid'])
            continue

        else:
            # we should never end up here!
            logger.info('Warning: Unexpected relation {} from {} to {}'.format(
                from_attribute, source_obj.absolute_url(), target_obj.absolute_url()))

    to_update = [i for i in update_linkintegrity if i not in modified_items]
    if to_update:
        logger.info('Recreating linkintegrity for {} items'.format(len(to_update)))
    for uuid in to_update:
        # fix linkintegrity-relations for items that were not yet modified
        modifiedContent(uuidToObject(uuid), None)

    # purge annotation from portal if they exist
    if RELATIONS_KEY in IAnnotations(portal):
        del IAnnotations(portal)[RELATIONS_KEY]


def link_objects(source, target, relationship):
    """Create a relation from source to target using zc.relation

    For RelationChoice or RelationList it will add the relation as attribute.
    Other relations they will only be added to the relation-catalog.
    """
    relation_catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    to_id = intids.getId(target)
    from_attribute = relationship

    # Check if there is exactly this relation.
    # If so remove it and create a fresh one.
    query = {
        'from_attribute': from_attribute,
        'from_id': source.UID(),
        'to_id': target.UID(),
    }
    for rel in relation_catalog.findRelations(query):
        relation_catalog.unindex(rel)

    if from_attribute == referencedRelationship:
        # Don't mess with linkintegrity-relations!
        # Refresh them by triggering this subscriber.
        modifiedContent(source, None)
        return

    if from_attribute == ITERATE_RELATION_NAME:
        # Iterate relations use a subclass of RelationValue
        relation = StagingRelationValue(to_id)
        event._setRelation(source, ITERATE_RELATION_NAME, relation)
        return

    fti = getUtility(IDexterityFTI, name=source.portal_type)
    field_and_schema = get_field_and_schema_for_fieldname(from_attribute, fti)

    if field_and_schema is None:
        # The relationship is not the name of a field. Only create a relation.
        logger.info(u'No field. Setting relation {} from {} to {}'.format(
            source.absolute_url(), target.absolute_url(), relationship))
        event._setRelation(source, from_attribute, RelationValue(to_id))
        return

    field, schema = field_and_schema

    if isinstance(field, RelationList):
        logger.info('Add relation to relationlist {} from {} to {}'.format(
            from_attribute, source.absolute_url(), target.absolute_url()))
        existing_relations = getattr(source, from_attribute, [])
        existing_relations.append(RelationValue(to_id))
        setattr(source, from_attribute, existing_relations)
        modified(source)
        return

    elif isinstance(field, (Relation, RelationChoice)):
        logger.info('Add relation {} from {} to {}'.format(
            from_attribute, source.absolute_url(), target.absolute_url()))
        setattr(source, from_attribute, RelationValue(to_id))
        modified(source)
        return

    # We should never end up here!
    logger.info('Warning: Unexpected relation {} from {} to {}'.format(
        from_attribute, source.absolute_url(), target.absolute_url()))


def get_relations(obj, attribute=None, backrefs=False, fullobj=False):
    """Get specific relations or backrelations for a content object
    TODO: Maybe check view permissions and conditionally return stubs
    """
    retval = []
    int_id = get_intid(obj)
    if not int_id:
        return retval

    relation_catalog = getUtility(ICatalog)
    if not relation_catalog:
        return retval

    query = {}
    if attribute:
        query['from_attribute'] = attribute

    if backrefs:
        query['to_id'] = int_id
    else:
        query['from_id'] = int_id

    relations = relation_catalog.findRelations(query)
    for relation in relations:
        if relation.isBroken():
            value = dict(
                href='',
                title=u'Broken relation',
                relation=relation.from_attribute)
            if fullobj:
                value['fullobj'] = None
            retval.append(value)
        else:
            if backrefs:
                obj = relation.from_object
            else:
                obj = relation.to_object
            value = dict(
                id=obj.id,
                href=obj.absolute_url(),
                title=obj.title,
                relation=relation.from_attribute)
            if fullobj:
                value['fullobj'] = obj
            retval.append(value)
    return retval


def get_backrelations(obj, attribute=None, fullobj=False):
    """Get backrelations"""
    return get_relations(
        obj, attribute=attribute, backrefs=True, fullobj=fullobj)


def get_intid(obj):
    """Intid from intid-catalog"""
    intids = queryUtility(IIntIds)
    if intids is None:
        return
    # check that the object has an intid, otherwise there's nothing to be done
    try:
        return intids.getId(obj)
    except KeyError:  # noqa
        # The object has not been added to the ZODB yet
        return


def get_field_and_schema_for_fieldname(field_id, fti):
    """Get field and its schema from a fti.
    """
    # Turn form.widgets.IDublinCore.title into title
    field_id = field_id.split('.')[-1]
    for schema in iterSchemataForType(fti):
        field = schema.get(field_id, None)
        if field is not None:
            return (field, schema)


def cleanup_intids(context=None):
    intids = getUtility(IIntIds)
    all_refs = ['{}.{}'.format(i.object.__class__.__module__, i.object.__class__.__name__)
                for i in intids.refs.values()]
    logger.info(Counter(all_refs))

    count = 0
    refs = [i for i in intids.refs.values() if isinstance(i.object, RelationValue)]
    for ref in refs:
        intids.unregister(ref)
        count += 1
    logger.info('Removed all {} RelationValues from IntId-tool'.format(count))

    count = 0
    for ref in intids.refs.values():
        if 'broken' in repr(ref.object):
            intids.unregister(ref)
    logger.info('Removed {} broken refs from IntId-tool'.format(count))
    all_refs = ['{}.{}'.format(i.object.__class__.__module__, i.object.__class__.__name__)
                for i in intids.refs.values()]
    logger.info(Counter(all_refs))
